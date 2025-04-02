from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from media_library.models import MediaFile

class Profile(models.Model):

    GENDER_CHOICES =[
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')
    image = models.ImageField(default='default/default.png', upload_to='profile_pics')
    current_uploads = models.ForeignKey(
        'media_library.MediaFile', on_delete=models.SET_NULL, null=True, blank=True
    )
    bio = models.TextField(blank=True)
    cover_photo = models.ImageField(upload_to='cover_photos/', blank=True, default='default/cover_default.jpg')
    location = models.CharField(max_length=100, blank=True)    


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Resize the image if it's too large
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def __str__(self):
        return f'{self.user.username} Profile'
    
# Signals to automatically create/update Profile when a User is created/updated
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()