from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='user_logout'),
    path('profile/<str:username>', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('update-cover-photo/', views.update_cover_photo, name='update_cover_photo'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        html_email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'
    ), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    path('change_password/', views.change_password, name='change_password')
]
