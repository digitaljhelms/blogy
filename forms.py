from django import forms
from blogy.models import Post

class PostEditForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'inline_edit'}))
    tags = forms.CharField(widget=forms.TextInput(attrs={'class':'inline_edit'}))
    raw_text = forms.CharField(widget=forms.Textarea(attrs={'class':'inline_edit'}))

    class Meta:
        model = Post
        exclude = ('author','is_draft','slug')
