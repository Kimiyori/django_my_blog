
from django import forms
from .models import Post,Comment
from mptt.forms import TreeNodeChoiceField

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'main_image',]
class SearchForm(forms.Form):
    query = forms.CharField()

class NewCommentForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Comment.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['parent'].widget=forms.HiddenInput()
        self.fields['content'].label = ''
        self.fields['parent'].label = ''
        self.fields['parent'].required = False

    class Meta:
        model = Comment
        fields = ( 'parent', 'content')

        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def save(self, *args, **kwargs): 
        Comment.objects.rebuild()
        return super(NewCommentForm, self).save(*args, **kwargs)