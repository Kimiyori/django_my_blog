from django.shortcuts import render
from django.views.generic import TemplateView,DetailView
from requests import get
from .models import Profile, CustomUser
from allauth.account.views import SignupView
from django.core.exceptions import PermissionDenied
# Create your views here.



class ProfileDetail(DetailView):
    template_name: str='account/profile.html'
    context_object_name = 'profile'
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user!=self.request.user:
            raise PermissionDenied("You do not have permission to Enter Clients in Other Company, Be Careful")
        return super().dispatch(request, *args, **kwargs)
    def get_object(self,**kwargs) :
        profile=Profile.objects.filter(user__id=self.kwargs['pk']).select_related('user').first()
        return  profile