import json
from django.shortcuts import render
from django.forms.models import modelform_factory
from django.forms import formset_factory
from django.apps import apps
from .models import Post, Content
from django.views.generic.base import TemplateResponseMixin, View
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView
from django.http import QueryDict
from .forms import PostForm, SearchForm
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank,SearchHeadline
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Greatest
# Create your views here.

class ContentOrderView(View):
    def post(self, request):
        d=request.body.decode('utf-8')
        d=json.loads(d)
        for id, order in d.items():
            Content.objects.filter(id=id,
            post__author=request.user).update(order=order)
        return redirect('post_list')

class SearchResultsList(ListView):
        model = Post
        context_object_name = "list"
        template_name = "post/search.html"

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            query = self.request.GET.get("q")
            context.update({'query': query})
            return context
        def get_queryset(self):
            query = self.request.GET.get("q") 
            search_vector = SearchVector('title')
            search_query = SearchQuery(query)
            results= Post.objects.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query)
            ).filter(search=search_query).order_by("-rank")
            return results

class PostList(ListView):
    model = Post
    template_name = 'post/list.html'
    context_object_name = 'list'


class PostDetail(DetailView):
    model = Post
    template_name = 'post/manage/detail.html'
    context_object_name = 'post'


class PostUpdate(UpdateView):
    model = Post
    fields = '__all__'
    template_name = 'post/manage/content/form.html'


class ContentCreateUpdateView(TemplateResponseMixin, View):
    post = None
    model = None
    obj = None
    template_name = 'post/manage/content/form_test.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='post',
                                  model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['post',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, post_id, model_name, id=None,order=None):
        self.post_obj = get_object_or_404(Post,
                                      id=post_id,
                                      author=request.user)
 
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,
                                         id=id,
                                         post=self.post_obj)
        return super().dispatch(request, post_id, model_name, id,order)

    def get(self, request, post_id, model_name, id=None,order=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,
                                        'object': self.obj})

    def post(self, request, post_id, model_name, id=None,order=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.post = self.post_obj
            obj.save()
            if not id:
                if not order:
                    Content.objects.create(post=self.post_obj,
                                        item=obj)
                else:
                    order=str(int(order)+1)
                    Content.objects.create(post=self.post_obj,
                                        order=order,
                                        item=obj)
        return redirect('post_detail_change', self.post_obj.id)


class PostDetailChange(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    contents = None
    template_name = 'post/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='post',
                                  model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['post',
                                                 'order',
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, pk):
        self.module = get_object_or_404(Post,
                                        id=pk,
                                        author=request.user)
        return super().dispatch(request, pk)

    def get(self, request, pk):
        self.contents = Content.objects.filter(post=self.module)
        d={'main':PostForm(instance=self.module)}
        for x in range(len(self.contents)):
            model = self.get_model(self.contents[x].item._meta.model_name)
            self.obj = get_object_or_404(model,
                                         id=self.contents[x].item.id,
                                         post=self.module)
            form = self.get_form(model, instance=self.obj)
            d[self.contents[x]] = form
        return self.render_to_response({'form': d,
                                        'object': self.module})

    def get_main_form(self,model, field, *args, **kwargs):
            Form = modelform_factory(model, fields=[field])
            return Form(*args, **kwargs)
    def post(self, request, pk):
        field=list(request.POST.keys())[0]
        if field!='csrfmiddlewaretoken':
            form=self.get_main_form(Post,field,instance=self.module,data=request.POST,files=request.FILES)
        else:
            field=list(request.FILES.keys())[0]
            print(field)
            form=self.get_main_form(Post,field,instance=self.module,data=request.POST,files=request.FILES)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
        return redirect('post_detail_change', self.module.id)


class ContentDeleteView(View):

    def post(self, request, id):
        content = get_object_or_404(Content,
                                    id=id,
                                    post__author=request.user)

        module = content.post
        content.item.delete()
        content.delete()
        return redirect('post_detail_change', module.id)
