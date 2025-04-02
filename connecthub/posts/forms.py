from django import forms
from .models import Post
from media_library.models import MediaFile

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': "What's on your mind?"
            }),
        }
