from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Friendship(models.Model):
    REQUESTED = 'requested'
    ACCEPTED = 'accepted'
    SENT = 'sent'

    STATUS_CHOICES = [
        (REQUESTED, 'Requested'),
        (ACCEPTED, 'Accepted'),
        (SENT, 'sent'),
    ]

    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['from_user', 'to_user'], 
                name='unique_friend_request',
                violation_error_message="A friend request already exists between these users."
            )
        ]


    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"

    @staticmethod
    def get_friends(user):
        # Get all friends of a user
        friends = Friendship.objects.filter(
            (models.Q(from_user=user) | models.Q(to_user=user)) & models.Q(status=Friendship.ACCEPTED)
        )
        return sorted([f.to_user if f.from_user == user else f.from_user for f in friends], key=lambda u: u.username)
    
    @staticmethod
    def get_requests(user):
        # Get all friend requests of a user
        requests = Friendship.objects.filter(to_user=user, status=Friendship.REQUESTED)
        return {f.from_user for f in requests}
    
    @staticmethod
    def get_sent_requests(user):
        requests = Friendship.objects.filter(from_user=user, status=Friendship.SENT)
        return {f.to_user for f in requests}