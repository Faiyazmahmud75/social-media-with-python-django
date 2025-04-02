import os

from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import PostForm  
from django.contrib import messages
from django.db.models import Q
from media_library.models import MediaFile
from notifications.models import Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.urls import reverse

channel_layer = get_channel_layer()

def home(request):
    posts = Post.objects.all()
# Filter parameters    
    order = request.GET.get('order', 'latest')
    media_type = request.GET.get('media', 'all')
    owner = request.GET.get('owner', '')
# Filter by date
    if order == 'latest':
        posts = posts.order_by('-created_at')
    elif order == 'oldest':
        posts = posts.order_by('created_at')
# Filter by media
    if media_type == 'text-only':
        posts = posts.filter(Q(image__isnull=True) | Q(image=''))
    elif media_type == 'images':
        posts = posts.filter(image__isnull=False).exclude(image='')
# Filter by owner
    if owner:
        posts = posts.filter(author__username__icontains=owner)

    form = PostForm()
    return render(request, 'posts/home.html', {'posts': posts, 'create_form': form})

# ------- Create Post --------
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            # Handle new uploads
            for uploaded_file in request.FILES.getlist("media_files"):
                media = MediaFile.objects.create(user=request.user, file=uploaded_file)
                post.media_files.add(media)
            messages.success(request, 'Post created successfully!')
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'posts/home.html', {'create_form': form})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = Comment.objects.filter(post=post)
    is_liked = False
    if post.likes.filter(id=request.user.id):
        is_liked = True
    form = PostForm(instance=post)
    return render(request, 'posts/detail_post.html', {'post': post, 'comments': comments, 'is_liked': is_liked, 'edit_form': form})

# ------- Update Post --------
@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            # Save post content update
            post = form.save(commit=False)
            post.save()

            # Get the list of media files to keep (IDs sent from the form)
            keep_media_ids = request.POST.getlist("keep_media")
            keep_media = MediaFile.objects.filter(id__in=keep_media_ids)

            # Find media that is being removed
            removed_media = post.media_files.exclude(id__in=keep_media_ids)

            # Remove and delete media if it's not used in another post or album
            for media in removed_media:
                post.media_files.remove(media)  # Remove from post
                if not media.posts.exists() and not media.albums.exists():
                    media.file.delete(save=False)  # Delete file from storage
                    media.delete()  # Delete from database

            # Handle new media uploads
            for uploaded_file in request.FILES.getlist("media_files"):
                media = MediaFile.objects.create(user=request.user, file=uploaded_file)
                post.media_files.add(media)  # Add new media files to post

            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', pk=post.pk)

    else:
        form = PostForm(instance=post)

    return render(request, 'posts/detail_post.html', {'post': post, 'edit_form': form})



# ------- Delete Post --------

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        
        referrer = request.META.get('HTTP_REFERER', reverse('home'))
        if referrer and f"/post/{pk}/" in referrer:
            return redirect(reverse('home'))

        return redirect(referrer)
    
    return render(request, 'posts/detail_post.html', {'post': post})



@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, user=request.user, content=content)
            messages.success(request, "Your comment has been added!")
            # Create a notification for the post owner
            notification= Notification.objects.create(
                user=post.author,
                sender=request.user,
                notification_type="comment",
                content=f"{request.user.username} commented on your post.",
                related_object_id=post.id,
                url=reverse('post_detail', args=[post.id])
            )
            async_to_sync(channel_layer.group_send)(
                f"notifications_{post.author.id}",
                {
                    "type": "send_notification",
                    "notification_type": "comment",
                    "sender": request.user.username,
                    "content": f"{request.user.username} commented on your post.",
                    "url": notification.url,
                }
            )
        else:
            messages.error(request, "Comment cannot be empty.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment deleted successfully!")
    return redirect('home')


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            comment.content = content
            comment.save()
            messages.success(request, "Comment updated successfully!")
        else:
            messages.error(request, "Comment cannot be empty.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def like_post(request, post_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to like a post.")
        return redirect('login')
    
    post = get_object_or_404(Post, id=post_id)
    is_liked = post.likes.filter(id=request.user.id).exists()

    if is_liked:
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

        notification = Notification.objects.create(
            user = post.author,
            sender = request.user,
            notification_type = 'like',
            content = f"{request.user.username} liked your post",
            related_object_id=post.id,
            url=reverse('post_detail', args=[post.id])
        )
        async_to_sync(channel_layer.group_send)(
                f"notifications_{post.author.id}",
                    {
                        "type": "send_notification",
                        "notification_type": "like",
                        "sender": request.user.username,
                        "content": f"{request.user.username} liked your post.",
                        "url": notification.url,
                        "notification_id": notification.id
                    }
            )
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def post_search(request):
    query = request.GET.get('q', '')
    results = Post.objects.filter(content__icontains=query) | Post.objects.filter(author__username__icontains=query)
    
    return render(request, 'posts/search_results.html', {'query': query, 'results': results})
