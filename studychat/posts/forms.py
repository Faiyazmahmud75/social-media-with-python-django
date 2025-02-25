from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': "What's on your mind?"
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
