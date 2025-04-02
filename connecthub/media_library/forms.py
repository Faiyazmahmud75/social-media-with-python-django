from django import forms
from .models import MediaFile

class MediaFileForm(forms.ModelForm):
    class Meta:
        model = MediaFile
        fields = ['file']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*, video/*, audio/*, application/pdf',
                'required': True
            }),
        }