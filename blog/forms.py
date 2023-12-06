from django import forms
from .models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(label="Your name", max_length=25,
                           help_text="The post would be sent from my email to "
                                     "the recipient(s) given below.")
    # Don't need email field. Default email would be used anyway.
    # email = forms.EmailField(label="Your email")

    # Change field type of 'to' field to allow multiple recipients
    # to = forms.EmailField()
    to = forms.CharField(label="To email(s)",
                         help_text="Use either colon(,), semicolon(;),"
                                   " hyphen(-) or  "
                                   "space(s) in between emails.")
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
