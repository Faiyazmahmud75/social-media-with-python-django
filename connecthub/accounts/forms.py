from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms
from .models import Profile

GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control rounded', 'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control rounded', 'placeholder': 'Email'}))
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=True, widget=forms.Select(attrs={'class': 'form-control rounded'}))
    
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded', 'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control rounded', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'gender', 'password1', 'password2']



class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'input-field form-control bg-transparent', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'input-field form-control bg-transparent', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'input-field form-control', 'placeholder': 'Email', 'readonly': 'readonly'})
    )
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'input-field form-select bg-transparent'})
    )
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'input-field form-control bg-transparent', 'rows': 3, 'placeholder': 'Tell us about yourself'}),
        required=False
    )
    location = forms.CharField(
        max_length=50, required=False,
        widget=forms.TextInput(attrs={'class': 'input-field form-control bg-transparent', 'placeholder': 'Location'})
    )

    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'gender', 'bio', 'image', 'cover_photo', 'location']









# class ProfileForm(forms.ModelForm):
    
#     gender = forms.ChoiceField(
#         choices=GENDER_CHOICES,
#         required=True,
#         widget=forms.Select(attrs={'class': 'form-select'})
#     )
    
#     class Meta:
#         model = Profile
#         fields = ['bio', 'image', 'cover_photo', 'location', 'gender']
#         widgets = {
#             'bio': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 3,
#                 'placeholder': 'Tell us about yourself'
#             }),
            
#         }


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Old Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Old Password'}),
    )
    new_password1 = forms.CharField(  # Corrected field name
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter New Password'}),
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'}),
    )
