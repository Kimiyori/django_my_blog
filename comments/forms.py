from django import forms

from mptt.forms import TreeNodeChoiceField


def CommentForm(dynamic_model):
    class NewCommentForm(forms.ModelForm):
        parent = TreeNodeChoiceField(queryset=dynamic_model.objects.all())

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['parent'].widget=forms.HiddenInput()
            self.fields['content'].label = ''
            self.fields['parent'].label = ''
            self.fields['parent'].required = False

        class Meta:
            model = dynamic_model
            fields = ( 'parent', 'content')

            widgets = {
                'content': forms.Textarea(attrs={'class': 'form-control'}),
            }

        def save(self, *args, **kwargs): 
            dynamic_model.objects.rebuild()
            return super(NewCommentForm, self).save(*args, **kwargs)
    return NewCommentForm