from django.db import models
from django.contrib.auth.models import User
from media_library.models import MediaFile

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    media_files = models.ManyToManyField(MediaFile, related_name="posts", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def delete(self, *args, **kwargs):
        """Delete associated media files if they are not used in other posts or albums"""
        for media in self.media_files.all():
            if not media.posts.exclude(id=self.id).exists() and not media.albums.exists():
                media.file.delete(save=False)
                media.delete()

        super().delete(*args, **kwargs) 

    def __str__(self):
        return f"Post by {self.author.username} on {self.created_at:%Y-%m-%d}"

    @property
    def like_count(self):
        return self.likes.count()

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on Post {self.post.id}"
