from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from django.db.models import OuterRef, Exists, Q
from posts.models import Post, Comment


from .forms import UserRegistrationForm, ProfileForm, ChangePasswordForm
from posts.forms import PostForm
from engagements.models import Friendship

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome aboard.")
            return redirect('home')
        else:
            messages.error(request, "Invalid Credentials, Please try again.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})



def user_login(request):
    error_message = None  # Initialize error message

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")  # Redirect on success
        else:
            error_message = "Invalid username or password. Please try again."

    return render(request, 'accounts/login.html', {"error_message": error_message})




# ------ User Profile --------
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    liked_subquery = Post.likes.through.objects.filter(post_id=OuterRef('pk'), user_id=profile_user.id)
    
    posts = Post.objects.filter(author=profile_user).order_by('-created_at').annotate(is_liked=Exists(liked_subquery))

    comments = Comment.objects.filter(post__in=posts)

    profile_form = ProfileForm(instance=profile_user.profile) if profile_user == request.user else None
    edit_forms = {post.id: PostForm(instance=post) for post in posts} if profile_user == request.user else {}
    
    # Get friendship request if exists
    friendship = Friendship.objects.filter(
        (Q(from_user=request.user, to_user=profile_user) | Q(from_user=profile_user, to_user=request.user))
    ).first()

    # Friendship status
    sent_request_exists = friendship and friendship.from_user == request.user and friendship.status == Friendship.REQUESTED
    received_request_exists = friendship and friendship.to_user == request.user and friendship.status == Friendship.REQUESTED
    are_friends = friendship and friendship.status == Friendship.ACCEPTED
    request_id = friendship.id if friendship else None


    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'profile_form': profile_form,
        'comments': comments,
        'edit_forms': edit_forms,
        "sent_request_exists": sent_request_exists,
        "received_request_exists": received_request_exists,
        "request_id": request_id,
        "are_friends": are_friends
    })



@login_required
def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=user.profile)

        if profile_form.is_valid():
            # Update user model fields
            user.first_name = profile_form.cleaned_data['first_name']
            user.last_name = profile_form.cleaned_data['last_name']
            user.gender = profile_form.cleaned_data['gender']  # If gender is in User model
            user.save()

            # Save profile fields
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile', username=user.username)

        else:
            print("Form Errors:", profile_form.errors)
            messages.error(request, 'Please correct the errors below.')
    
    else:
        profile_form = ProfileForm(instance=user.profile, initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'gender': user.profile.gender,
        })

    return render(request, 'accounts/edit_profile.html', {'profile_form': profile_form})



@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password has been successfully changed!')
            return redirect('profile', username=request.user.username)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ChangePasswordForm(user=request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})



@login_required
def update_cover_photo(request):
    if request.method == 'POST' and 'cover_photo' in request.FILES:
        profile = request.user.profile
        profile.cover_photo = request.FILES['cover_photo']
        profile.save()
        messages.success(request, "Cover photo updated successfully!")
    return redirect(reverse('profile', kwargs={'username': request.user.username}))
