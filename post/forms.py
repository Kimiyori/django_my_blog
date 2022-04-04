
from django import forms
from .models import Post
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'main_image', 'related_to']
class SearchForm(forms.Form):
    query = forms.CharField()