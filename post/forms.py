
from django import forms
from .models import Post
from comments.models import CommentPost
from mptt.forms import TreeNodeChoiceField
from django.apps import apps
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'main_image',]
class SearchForm(forms.Form):
    query = forms.CharField()

