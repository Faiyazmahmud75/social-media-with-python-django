from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from .forms import PostForm  
from django.contrib import messages

def home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'posts/home.html', {'posts' : posts})

# ------- Create Post --------
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.author = request.user
            form.save()
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
    return render(request, 'posts/detail_post.html', {'post': post, 'comments': comments, 'is_liked': is_liked})

# ------- Update Post --------
@login_required
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('home')
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/post_form.html', {'edit_form': form})


# ------- Delete Post --------
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('home')
    return render(request, 'posts/detail_post.html', {'post': post})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(post=post, user=request.user, content=content)
            messages.success(request, "Your comment has been added!")
        else:
            messages.error(request, "Comment cannot be empty.")
    return redirect('home')

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment deleted successfully!")
    return redirect('home')

@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.likes.filter(id=request.user.id):
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect('home')