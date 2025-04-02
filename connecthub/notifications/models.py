from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('friend_request', 'Friend Request'),
        ('friend_accepted', 'Friend Request Accepted'),
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('mention', 'Mention'),
    )
    
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    content = models.TextField(blank=True, null=True)  
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False) 

    related_object_id = models.IntegerField(null=True, blank=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"Notification from {self.sender.username} to {self.user.username} - {self.notification_type}"

    class Meta:
        ordering = ['-timestamp']
