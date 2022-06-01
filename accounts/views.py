from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic import TemplateView,DetailView
from requests import get

from accounts.forms import ProfileForm
from .models import Profile, CustomUser
from allauth.account.views import SignupView
from django.core.exceptions import PermissionDenied
# Create your views here.



class ProfileDetail(TemplateResponseMixin, View):
    template_name: str='account/profile.html'
    context_object_name = 'profile'
    def dispatch(self, request,pk):

        self.profile=Profile.objects.filter(user__id=pk).select_related('user').first()

        return super().dispatch( request,pk)
    def get(self,request,pk,) :

        return  self.render_to_response({'profile':self.profile})
    
    def post(self,request,pk):
        if self.profile.user!=request.user:
            return JsonResponse({'result':'fail'})
        form=ProfileForm(instance=self.profile,data=request.POST,files=request.FILES)
        if form.is_valid():
            form.save()
        return JsonResponse({'image':self.profile.photo.url})