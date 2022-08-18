from django.http import JsonResponse
from django.views.generic.base import TemplateResponseMixin, View
from accounts.forms import ProfileForm
from .models import Profile, CustomUser
# Create your views here.



class ProfileDetail(TemplateResponseMixin, View):
    template_name: str='account/profile.html'
    context_object_name = 'profile'
    def dispatch(self, request,pk):

        self.profile=Profile.objects.filter(user__id=pk).select_related('user',).first()

        return super().dispatch( request,pk)
    def get(self,request,pk,) :
        self.posts=CustomUser.objects.get(id=pk).post.all().values('id','title','main_image')
        return  self.render_to_response({'profile':self.profile,'posts':self.posts})
    
    def post(self,request,pk):
        if self.profile.user!=request.user:
            return JsonResponse({'result':'fail'})
        form=ProfileForm(instance=self.profile,data=request.POST,files=request.FILES)
        if form.is_valid():
            form.save()
        return JsonResponse({'image':self.profile.photo.url})