from django.db import models
from django.contrib.auth.models import User

class MediaFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="media_files")
    file = models.FileField(upload_to="files")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        if not self.albums.exists() and not self.posts.exists():  # Only delete if not used
            self.file.delete(save=False)  # Delete file from storage
            super().delete(*args, **kwargs)


    def __str__(self):
        return self.file.name

class Album(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="albums")
    media_files = models.ManyToManyField(MediaFile, related_name="albums", blank=True)

    def __str__(self):
        return self.name
