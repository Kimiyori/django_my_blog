
from django.shortcuts import render
from django.forms.models import modelform_factory
from django.forms import formset_factory
from django.apps import apps
from .models import Post, Content
from django.views.generic.base import TemplateResponseMixin, View
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView
from django.http import QueryDict
from .forms import PostForm
# Create your views here.


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
        main= PostForm(instance=self.module)
        d = {}
        #list_of_forms = [PostForm(instance=self.module)]
        for x in range(len(self.contents)):
            model = self.get_model(self.contents[x].item._meta.model_name)
            self.obj = get_object_or_404(model,
                                         id=self.contents[x].item.id,
                                         post=self.module)
            form = self.get_form(model, instance=self.obj)
            #list_of_forms.append(form)
            d[self.contents[x]] = form
        return self.render_to_response({'main':main,
            'form': d,
                                        'object': self.module})


    def post(self, request, pk):
        def query(model_name,model,request,index,obj):
            
            try:
                query_dict = QueryDict('', mutable=True)
                query_dict.update({model_name: dict(request)[model_name][index]})
                if model_name!='image':
                    form = self.get_form(model,
                                            instance=obj,
                                            data=query_dict)
                else:
                    form = self.get_form(model,
                                            instance=obj,
                                            files=query_dict)
                if form.is_valid():
                        obj1 = form.save(commit=False)
                        obj1.post = self.module
                        obj1.save()
            except Exception as e:
                print(e)

        self.contents = Content.objects.filter(post=self.module)
        self.text_i = 0
        self.img_i = 0
        self.video_i = 0
        print(request.POST)
        for x in range(len(self.contents)):
            model_name = self.contents[x].item._meta.model_name
            model = self.get_model(model_name)
            obj = get_object_or_404(model,
                                         id=self.contents[x].item.id,
                                         post=self.module)
            if model_name == 'text':
                query(model_name,model,request.POST,self.text_i,obj)
                self.text_i+=1
            elif model_name == 'image':
                query(model_name,model,request.FILES,self.img_i,obj)
                self.img_i+=1
            elif model_name == 'video':
                query(model_name,model,request.POST,self.video_i,obj)
                self.video_i+=1
        query_dict = QueryDict('', mutable=True)
        query_dict.update({'title': dict(request.POST)[
                          'title'][0], 'related_to': dict(request.POST)['related_to'][0]})
        try:
            img_query_dict = QueryDict('', mutable=True)
            img_query_dict.update(
                {'main_image': dict(request.FILES)['main_image'][0]})
        except Exception as e:
            print(e)
        main = PostForm(query_dict, instance=self.module, files=img_query_dict)
        if main.is_valid():
            main.save()
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
