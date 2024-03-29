import json
from typing import Any, Dict, Optional, Type, Union
import uuid
from django.forms import ModelForm
from django.forms.models import modelform_factory
from django.apps import apps
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    JsonResponse,
    HttpResponseRedirect,
)
from django.urls import reverse
from .models import File, Image, Post, Content, Text, Video
from comments.models import CommentPost
from django.views.generic.base import TemplateResponseMixin, View
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView
from .forms import PostForm
from comments.forms import CommentForm
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, Case, When, Value
from django.db.models.fields import CharField, TextField
from django.db.models.functions import Cast
from titles.filters import Array
import redis
from django.conf import settings
from django.core.cache import cache
from titles.paginator import LargeTablePaginator
import logging
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.core.exceptions import ValidationError


CACHE_TIME = 60 * 5

# logging
file_logger = logging.getLogger("file_logger")
console_logger = logging.getLogger("console_logger")


class ContentOrderView(View):
    """
    View for swapping orders between contents when they dragged
    """

    def post(self, request: HttpRequest) -> JsonResponse:
        console_logger.info("Swaping contents order")
        data_json = request.body.decode("utf-8")
        data: Dict[str, int] = json.loads(data_json)
        for id, order in data.items():
            Content.objects.filter(
                id=id,
            ).update(order=order)
        console_logger.info("Successful swap contents order")
        return JsonResponse({"response": "success"})


class PostList(ListView):
    """
    View for post list
    """

    template_name = "post/list.html"
    context_object_name = "list"
    paginate_by = 10
    paginator = LargeTablePaginator

    def get_queryset(self) -> QuerySet:
        console_logger.info("Get list of posts")
        post: QuerySet = Post.objects.all().values(
            "id", "publish", "title", "main_image", "author"
        )
        return post


def get_views(pk: uuid.UUID) -> int:
    """
    Increment view value for given post

    """
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
        )

        total_views: int = r.get(f"post:{pk}:views")
        if not total_views:
            total_views = 0
        return int(total_views)
    except redis.ConnectionError:
        file_logger.debug("Connect redis error")
        raise redis.exceptions.ConnectionError("Connect redis error")


class PostDetail(TemplateResponseMixin, View):
    """
    View for detail post
    """

    model = Post
    template_name = "post/manage/detail.html"
    context_object_name = "post"

    def get(self, request: HttpRequest, pk: uuid.UUID) -> HttpResponse:
        console_logger.info(f"Trying to get detail post with id - {pk}")

        cache_post_key: str = f"postid:{pk}"
        post = cache.get(cache_post_key)
        if post is None:
            try:
                post = Post.get_instance(pk)
                cache.set(cache_post_key, post)
            except Post.DoesNotExist:
                raise Http404("Cannot find post with given id")

        cache_content_key = f"contentpostid:{pk}"
        content: Optional[QuerySet] = cache.get(cache_content_key)
        if content is None:
            content = Content.get_instance(pk)
            cache.set(cache_content_key, content)

        comments = CommentPost.get_comments_for_post(pk)
        comment_form = CommentForm(CommentPost)
        total_views: int = get_views(pk)

        console_logger.info(f"Successful get detail post with id - {pk}")
        return self.render_to_response(
            {
                "post": post,
                "content": content,
                "total_views": total_views,
                "comments": comments,
                "comment_form": comment_form,
            }
        )


class GetModelAndForm:
    """
    Meta class for common methods
    """

    def get_model(self, model_name: str) -> Union[Text, Video, Image, File, None]:
        # get model based on model_name
        if model_name in ["text", "video", "image", "file"]:
            return apps.get_model(app_label="post", model_name=model_name)
        return None

    def get_form(
        self, model: Union[Text, Video, Image, File, None], *args: Any, **kwargs: Any
    ) -> ModelForm:
        # create form
        Form = modelform_factory(model, exclude=["post", "order", "created", "updated"])
        return Form(*args, **kwargs)


class ContentCreateUpdateView(GetModelAndForm, TemplateResponseMixin, View):
    """
    View for editing or creating Content/Item instances
    """

    obj = None

    def dispatch(self, request, post_id, model_name, id=None, order=None):
        # get post instance
        self.post_obj = get_object_or_404(Post, id=post_id, author=request.user)
        # get model
        self.model = self.get_model(model_name)
        if id:
            # get instance of item based on model_name
            self.obj = get_object_or_404(self.model, id=id, post=self.post_obj)
        return super().dispatch(request, post_id, model_name, id, order)

    def post(
        self,
        request: HttpRequest,
        post_id: uuid.UUID,
        model_name: str,
        id: Optional[int] = None,
        order: Optional[int] = None,
    ) -> JsonResponse:
        data = {}
        data["user_id"] = request.user.id
        # create form for current item model with data from request
        form = self.get_form(
            self.model, instance=self.obj, data=request.POST, files=request.FILES
        )
        if form.is_valid():
            obj = form.save(commit=False)

            if not hasattr(obj, "post"):
                obj.post = self.post_obj
            obj.save()

            # if we have an id attribute, then we just need to update the element,
            #  we don’t need the code below, this is for a new object
            if not id:
                # if we dont have order, then create content withoud order.
                # Its case when we create first or last obj and assign it order 1 or last+1
                if not order:
                    content = Content.objects.create(post=self.post_obj, item=obj)
                # if we have order attr, then that meants that we create new item somewhere
                # in our post and we need to content our content instance based on order that above
                else:
                    # incr order by 1, because we get order from item
                    # and in order for our subject to be lower in post, we need a higher order
                    order = int(order) + 1
                    content = Content.objects.create(
                        post=self.post_obj, order=order, item=obj
                    )
                    data["id"] = content.id
                    data["order"] = order

            if model_name == "video":
                data["url"] = obj.video

        else:
            file_logger.debug(
                f"Get following error for given post id {post_id} and content id {id} {form.errors}"
            )
            raise ValidationError("invalid form")
        return JsonResponse(data)


class PostCreate(GetModelAndForm, TemplateResponseMixin, View):
    """
    View for create post
    """

    template_name = "post/manage/content/form_create.html"

    def get(self, request):
        main_form = PostForm()
        return self.render_to_response({"main_form": main_form})

    def post(self, request):
        form = PostForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.author = get_user_model().objects.get(id=request.user.id)
            inst.save()
            return redirect(reverse("post_detail_change", kwargs={"pk": inst.id}))


class PostDetailChange(GetModelAndForm, TemplateResponseMixin, View):
    """
    View for editing Post
    """

    template_name = "post/manage/content/form.html"

    def dispatch(self, request, pk):
        try:
            self.module = Post.objects.only("id", "title", "author", "main_image").get(
                id=pk
            )
            if request.user != self.module.author:
                file_logger.warning(
                    f"Error for access edit post page. Request user is not the author of that post",
                    extra={
                        "request_user": request.user,
                        "author": getattr(self.module, "author", None),
                    },
                )
                return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
        except Post.DoesNotExist:
            file_logger.warning(f"Post does not exist", extra={"post_id": pk})
            return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))
        return super().dispatch(request, pk)

    def get(self, request: HttpRequest, pk: uuid.UUID) -> HttpResponse:
        console_logger.info(f"Trying to get detail post with id - {pk} for editing")

        self.contents = Content.get_instance_for_edit_page(self.module)
        list_of_values = []
        console_logger.info("Collect content for post in list...")
        for x in self.contents:
            name_model = x["content"][0][2]
            data = x["content"][0][1]
            item_id = x["content"][0][0]
            model = self.get_model(name_model)
            form = self.get_form(model, initial={name_model: data})
            x["model"] = name_model
            x["item_id"] = item_id
            x["form"] = form
            del x["content"]
            list_of_values.append(x)
        main_form = PostForm(instance=self.module)

        file_logger.info(f"Successful get detail post with id - {pk} for editing")
        return self.render_to_response(
            {
                "main_form": main_form,
                "object": self.module,
                "items": list_of_values,
            }
        )

    def get_main_form(
        self, model: Type[Post], field: str, *args: Any, **kwargs: Any
    ) -> ModelForm:
        Form = modelform_factory(model, fields=[field])
        return Form(*args, **kwargs)

    def post(self, request: HttpRequest, pk) -> JsonResponse:
        console_logger.info(f"Trying to update post instance")
        form = self.get_main_form(
            Post,
            request.POST["type"],
            instance=self.module,
            data=request.POST,
            files=request.FILES,
        )
        if form.is_valid():
            form.save()
        else:
            file_logger.warning("Form isn't valid for update post instance")
            raise ValidationError("invalid form")
        file_logger.info(f"Successful  update post instance")
        return JsonResponse({request.POST["type"]: "ok"})


class PostDelete(View):
    def post(self, request, pk: uuid.UUID):
        try:
            post = Post.objects.get(id=pk)
        except Post.DoesNotExist:
            file_logger.debug("failed to delete post", extra={"id": pk})
            raise Http404()
        post.delete()
        return redirect(reverse("post_list"))


class ContentDeleteView(View):
    """
    View for delete content
    """

    def post(self, request: HttpRequest, post_id: uuid.UUID, id: int) -> JsonResponse:
        console_logger.info(
            "Trying to delete content in post...",
            extra={"post_id": post_id, "content_id": id, "request_user": request.user},
        )
        content: Content = get_object_or_404(Content, id=id, post=post_id)
        if content:
            content.item.delete()
            content.delete()
        console_logger.info(
            "Successful delete content in post",
            extra={"post_id": post_id, "content_id": id, "request_user": request.user},
        )
        return JsonResponse({"answer": "success"})


# def delete_comment(request,comment_id):
#     console_logger.info(f'Trying to delete comment with id {comment_id}')
#     if not request.user.is_authenticated:
#         file_logger.info(f'failed to delete comment with id {comment_id} because not auth')
#         return HttpResponseRedirect('accounts/login/')
#     comment=Comment.objects.get(id=comment_id)
#     comment.delete()
#     console_logger.info(f'Successful delete comment with id {comment_id}')
#     return JsonResponse({'answer':'yes'})

# def add_comment(request,post_id):
#     console_logger.info(f'Trying to add comment to post with id {post_id}')
#     if request.method == 'POST':
#         comment_form = NewCommentForm(request.POST)
#         if comment_form.is_valid():
#             if not request.user.is_authenticated:
#                 file_logger.info(f'failed to add comment to post with id {post_id} because not auth')
#                 return HttpResponseRedirect('accounts/login/')
#             post=Post.objects.get(id=post_id)
#             user=get_user_model().objects.get(id=request.user.id)
#             user_comment = comment_form.save(commit=False)
#             user_comment.author=user
#             user_comment.post = post
#             user_comment.save()
#             console_logger.info(f'Successful add comment to post with id {post_id}')
#         return JsonResponse({'id':user_comment.id,
#                             'created':str(user_comment.created.strftime("%b %d %H:%M")),
#                             'author':user.username})
