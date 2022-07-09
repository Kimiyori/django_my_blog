
import json

from django.forms.models import modelform_factory
from django.apps import apps
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import Post, Content, Video,Comment
from django.views.generic.base import TemplateResponseMixin, View
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, UpdateView
from .forms import NewCommentForm, PostForm
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F
from django.db.models.fields import CharField, TextField
from django.db.models.functions import Cast
from django.db.models import Case, When, Value
from embed_video.backends import YoutubeBackend
from titles.filters import Array
import redis
from django.conf import settings
from django.core.cache import cache
from titles.paginator import LargeTablePaginator
import logging
CACHE_TIME = 60*5
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.contrib.auth import get_user_model
# Create your views here.

file_logger = logging.getLogger('file_logger')
console_logger = logging.getLogger('console_logger')


class ContentOrderView(View):
    """View for swap order between content when they dragged"""

    def post(self, request):
        file_logger.info('Swaping contents order')
        d = request.body.decode('utf-8')
        d = json.loads(d)
        for id, order in d.items():
            Content.objects.filter(id=id,
                                   post__author=request.user).update(order=order)
        file_logger.info('Successful swap contents order')
        return JsonResponse({'response': 'yes'})


class PostList(ListView):
    """View for post list"""
    template_name = 'post/list.html'
    context_object_name = 'list'
    paginate_by = 10
    paginator = LargeTablePaginator

    def get_queryset(self):
        console_logger.info('Get list of posts')
        post = Post.objects.all().values('id', 'publish', 'title', 'main_image', 'author')
        return post



class PostDetail(TemplateResponseMixin, View):
    """View for detail post"""
    model = Post
    template_name = 'post/manage/detail.html'
    context_object_name = 'post'

    #@method_decorator(cache_page(CACHE_TIME))
    def get(self, request, pk):
        console_logger.info(f'Trying to get detail post with id - {pk}')
        # connect to redis
        r = redis.Redis(host=settings.REDIS_HOST,
                        port=settings.REDIS_PORT,
                        db=settings.REDIS_DB)
         # search in cache post by key
        cache_post_key = f'postid:{pk}'
        post = cache.get(cache_post_key)
        # if not, then create and cache it
        if post is None:
            post = Post.objects.filter(id=pk).values(
                'id', 'title', 'main_image').first()
            cache.set(cache_post_key, post)

        # search in cache content fo given post by key
        cache_content_key = f'contentpostid:{pk}'
        content = cache.get(cache_content_key)
        # if not, then create and cache  it
        if content is None:
            # get content list with Case function that check type of content if then extract it
            content = Content.objects.filter(post__id=pk).annotate(cont=Case(
                When(text__gte=1, then=ArrayAgg(
                    Array(F('text__text'), Value('text')))),
                When(image__gte=1, then=ArrayAgg(
                    Array(F('image__image'), Value('image')))),
                When(file__gte=1, then=ArrayAgg(
                    Array(F('file__file'), Value('file')))),
                When(video__gte=1, then=ArrayAgg(Array(F('video__video'), Value('video')))), output_field=TextField())).\
                order_by('order').values('cont')
            cache.set(cache_content_key, content)

        comments=Comment.objects.select_related('author__profile').filter(post__id=pk)

        # increate in redis number of views in post
        total_views = r.incr(f'post:{pk}:views')
        file_logger.info(f'Successful get detail post with id - {pk}')
        comment_form = NewCommentForm()
        return self.render_to_response({'post': post, 
                                        'content': content, 
                                        'total_views': total_views,
                                        'comments':comments,
                                        'comment_form': comment_form,})

def delete_comment(request,comment_id):
    console_logger.info(f'Trying to delete comment with id {comment_id}')
    if not request.user.is_authenticated:
        file_logger.info(f'failed to delete comment with id {comment_id} because not auth')
        return HttpResponseRedirect('accounts/login/')
    comment=Comment.objects.get(id=comment_id)
    comment.delete()
    console_logger.info(f'Successful delete comment with id {comment_id}')
    return JsonResponse({'answer':'yes'})

def add_comment(request,post_id):
    console_logger.info(f'Trying to add comment to post with id {post_id}')
    if request.method == 'POST':
        comment_form = NewCommentForm(request.POST)
        if comment_form.is_valid():
            if not request.user.is_authenticated:
                file_logger.info(f'failed to add comment to post with id {post_id} because not auth')
                return HttpResponseRedirect('accounts/login/')
            post=Post.objects.get(id=post_id)
            user=get_user_model().objects.get(id=request.user.id)
            user_comment = comment_form.save(commit=False)
            user_comment.author=user
            user_comment.post = post
            user_comment.save()
            console_logger.info(f'Successful add comment to post with id {post_id}')
        return JsonResponse({'id':user_comment.id,
                            'created':str(user_comment.created.strftime("%b %d %H:%M")),
                            'author':user.username})

class GetModelAndForm:
    """Metaclass"""
    # Meta class foe cummon methods

    def get_model(self, model_name):
        # get model based on model_name
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='post',
                                  model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        # create form
        Form = modelform_factory(model, exclude=['post',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)


class ContentCreateUpdateView(GetModelAndForm, TemplateResponseMixin, View):
    """View for editing or creating Content/Item instances"""
    post = None
    model = None
    obj = None
    template_name = 'post/manage/content/form_add.html'

    def dispatch(self, request, post_id, model_name, id=None, order=None):
        # get post instance
        self.post_obj = get_object_or_404(Post,
                                          id=post_id,
                                          author=request.user)
        # get model
        self.model = self.get_model(model_name)
        if id:
            # get instance of item based on model_name
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         post=self.post_obj)
        return super().dispatch(request, post_id, model_name, id, order)

    def post(self, request, post_id, model_name, id=None, order=None):

        data = {}
        data['user_id'] = request.user.id
        # create form for current item model with data from request
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            # check if item attached to post and if its new item, then attach it
            if not hasattr(obj, 'post'):
                obj.post = self.post_obj
            obj.save()
            # if we have id attribute, then we need just update out item and code below doesnt need for us, its for new obj
            if not id:
                # if we dont have order, then create content withoud order. Its case when we create first obj and issign it order 1
                if not order:
                    content = Content.objects.create(post=self.post_obj,
                                                     item=obj)
                # if we have order attr, then that meants that we create new item somewhere in our post and we need to content our content instance based on order that above
                else:
                    # incr order by 1, because we pass order from item and in order for our subject to be lower in post, we need a higher order
                    order = int(order)+1
                    content = Content.objects.create(post=self.post_obj,
                                                     order=order,
                                                     item=obj)
                    data['id'] = content.id
                    data['order'] = order
        else:
            print(form.errors)
        # this specific case theck if our item is video and if yes, then convert url to embed format
        if isinstance(obj, Video):
            y = YoutubeBackend(url=obj.video)
            data['url'] = y.get_url()

        return JsonResponse(data)


class PostDetailChange(GetModelAndForm, TemplateResponseMixin, View):
    """View for editing Post"""
    module = None
    model = None
    obj = None
    contents = None
    template_name = 'post/manage/content/form_test.html'

    def dispatch(self, request, pk):
        # get post instance
        self.module = Post.objects.filter(id=pk).only(
            'id', 'title', 'author',  'main_image').first()
        # check if request user and author not the same person; only author can edit own posts
        if request.user != self.module.author:
            file_logger.warning(f'Error for access edit post page.Request user is not the author of that post', extra={
                'request_user': request.user,
                'author': self.module.author})
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        return super().dispatch(request, pk)

    def get(self, request, pk):
        console_logger.info(
            f'Trying to get detail post with id - {pk} for editing')
        # get content using case
        self.contents = Content.objects.filter(post=self.module).select_related('text').annotate(content=Case(
            When(text__gte=1, then=ArrayAgg(Array(Cast(F('text__id'), output_field=CharField()), F(
                'text__text'), Value('text'), output_field=TextField()))),
            When(image__gte=1, then=ArrayAgg(Array(Cast(F('image__id'), output_field=CharField()), F(
                'image__image'), Value('image'), output_field=TextField()))),
            When(file__gte=1, then=ArrayAgg(Array(Cast(F('file__id'), output_field=CharField()), F(
                'file__file'), Value('file'), output_field=TextField()))),
            When(video__gte=1, then=ArrayAgg(Array(Cast(F('video__id'), output_field=CharField()), F('video__video'), Value('video'), output_field=TextField()))))).\
            values('id', 'order', 'content').order_by('order')

        list_of_values = []
        file_logger.info('Collect content for post in list...')
        for x in self.contents:
            name_model = x['content'][0][2]
            data = x['content'][0][1]
            item_id = x['content'][0][0]
            model = self.get_model(name_model)
            form = self.get_form(model, initial={name_model: data})
            x['model'] = name_model
            x['item_id'] = item_id
            x['form'] = form
            del x['content']
            list_of_values.append(x)
        main_form = PostForm(instance=self.module)
        file_logger.info(
            f'Successful get detail post with id - {pk} for editing')
        return self.render_to_response({'main_form': main_form,
                                        'object': self.module,
                                        'items': list_of_values,
                                        })

    def get_main_form(self, model, field, *args, **kwargs):
        Form = modelform_factory(model, fields=[field])
        return Form(*args, **kwargs)

    def post(self, request, pk):
        file_logger.info(f'Trying to update post instance')
        form = self.get_main_form(
            Post, request.POST['type'], instance=self.module, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
        else:
            file_logger.warning('Form isn\'t valid for update post instance')
        file_logger.info(f'Successful  update post instance')
        return JsonResponse({request.POST['type']: 'ok'})


class ContentDeleteView(View):
    """View for delete content"""

    def post(self, request, post_id, id):
        file_logger.info('Trying to delete content in post...', extra={
            'post_id': post_id,
            'content_id': id,
            'request_user': request.user
        })
        post = get_object_or_404(Post,
                                 id=post_id,)

        content = get_object_or_404(Content,
                                    id=id,
                                    post=post)

        content.item.delete()
        content.delete()
        file_logger.info('Successful delete content in post', extra={
            'post_id': post_id,
            'content_id': id,
            'request_user': request.user
        })
        return JsonResponse({'answer': 'yes'})
