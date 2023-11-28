from django import forms
from .models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(label="Your name", max_length=25)
    email = forms.EmailField(label="Your email")
    # to = forms.EmailField()
    to = forms.CharField(label="To email(s)",
                         help_text="Misplaced help_text position due to CSS")
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
