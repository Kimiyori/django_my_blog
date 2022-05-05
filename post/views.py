import json
from django.shortcuts import render
from django.forms.models import modelform_factory,modelformset_factory
from django.forms import formset_factory
from django.apps import apps
from .models import Post, Content,Related,Text,File,Image,Video
from django.views.generic.base import TemplateResponseMixin, View
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView
from django.http import QueryDict
from .forms import PostForm, SearchForm
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank,SearchHeadline
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Greatest
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.forms import  generic_inlineformset_factory
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models.expressions import Func
from django.db.models.fields import CharField,UUIDField,TextField,IntegerField
from django.db.models.functions import Cast
from django.db.models import F
from django.db.models import Exists, OuterRef,Count,Case,When,Value
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

class Array(Func):
    template = '%(function)s[%(expressions)s]'
    function = 'ARRAY'
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
                                                 'created',
                                                 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, pk):
        self.module = Post.objects.filter(id=pk,author=request.user).only('id','title','author','related_to','main_image').first()
        return super().dispatch(request, pk)

    def get(self, request, pk):
        self.contents = Content.objects.filter(post=self.module)
        a=modelform_factory(Text, exclude=['post',
                                                 'created',
                                                 'updated'])
        e=['text__text','text__id','image__image','image__id','file__file','file__id','video__video','video__id']
        #n=Content.objects.filter(post=self.module).annotate(item1=ArrayAgg(Array(Cast(F('text__id'),output_field=CharField()),F('text__text'),output_field=TextField()),distinct=True)).values('id','item1','order',)
        n=Content.objects.filter(post=self.module).annotate(content=Case(
        When(text__gte=1,then=ArrayAgg(Array(Cast(F('text__id'),output_field=CharField()),F('text__text'),Value('text'),output_field=TextField()),distinct=True)),
        When(image__gte=1,then=ArrayAgg(Array(Cast(F('image__id'),output_field=CharField()),F('image__image'),Value('image'),output_field=TextField()),distinct=True)),
         When(file__gte=1,then=ArrayAgg(Array(Cast(F('file__id'),output_field=CharField()),F('file__file'),Value('file'),output_field=TextField()),distinct=True)),
          When(video__gte=1,then=ArrayAgg(Array(Cast(F('video__id'),output_field=CharField()),F('video__video'),Value('video'),output_field=TextField()),distinct=True)))).\
            values('id','order','content')

        q={'main':PostForm(instance=self.module)}

        for x in n:
            model = self.get_model(x['content'][0][2])
            form = self.get_form(model, initial={x['content'][0][2]:x['content'][0][1]})
            x['form']=form
            x['model']=x['content'][0][2]
            q[x['id']]=x
        #print(q)
        d={'main':PostForm(instance=self.module)}
        for x in self.contents.iterator():
            a=x.item
            model = self.get_model(a._meta.model_name)
            form = self.get_form(model, instance=a)
            d[x] = form  
        return self.render_to_response({'form': d,
                                        'object': self.module,
                                        })

    def get_main_form(self,model, field, *args, **kwargs):
            Form = modelform_factory(model, fields=[field])
            return Form(*args, **kwargs)
    def post(self, request, pk):
        field=list(request.POST.keys())[0]
        if field!='csrfmiddlewaretoken':
            form=self.get_main_form(Post,field,instance=self.module,data=request.POST,files=request.FILES)
        else:
            field=list(request.FILES.keys())[0]
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
