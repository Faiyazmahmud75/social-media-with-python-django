from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from django.contrib.auth import login, authenticate, logout
from django.db.models import OuterRef, Exists
from django.contrib import messages
from posts.models import Post, Comment
from .forms import ProfileForm
from posts.forms import PostForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid username or password. Please try again.')
            return render(request, 'user_login', {})
        else:
            login(request, user)
            return redirect('home')
    else:
        return render(request, 'user_login', {})

# ------ User Profile --------
@login_required
def profile(request):
    user = request.user
    liked_subquery = Post.likes.through.objects.filter(post_id=OuterRef('pk'), user_id=user.id)
    posts = Post.objects.filter(author=user).order_by('-created_at').annotate( is_liked= Exists(liked_subquery))
    comments = Comment.objects.filter(post__in=posts)
    profile_form = ProfileForm(instance=user.profile)
    edit_forms = {post.id: PostForm(instance=post) for post in posts}
    return render(request, 'accounts/profile.html', {
        'posts': posts,
        'profile_form': profile_form,
        'comments': comments,
        'edit_forms': edit_forms
    })


@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = ProfileForm(user.profile)
    
    return render(request, 'accounts/edit_profile.html', {'profile_form': form})