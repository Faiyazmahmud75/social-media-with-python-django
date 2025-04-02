from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Friendship
from django.contrib.auth.models import User
from django.db import models
from django.http import JsonResponse
from notifications.models import Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.urls import reverse

channel_layer = get_channel_layer()

@login_required
def send_request(request, username):
    if request.method == "POST":
        to_user = get_object_or_404(User, username=username)
        if to_user != request.user:
            # Check if a request already exists
            friendship, created = Friendship.objects.get_or_create(
                from_user=request.user, to_user=to_user, defaults={'status': Friendship.REQUESTED}
            )
            if created:
                messages.success(request, "Friend request sent!")
                notification = Notification.objects.create(
                    user = to_user,
                    sender = request.user,
                    notification_type = 'friend_request',
                    content = f"{request.user.username} sent you a connection request",
                    url=reverse('profile', args=[request.user.username])

                    
                    )
                async_to_sync(channel_layer.group_send)(
                    f"notifications_{to_user.id}",
                        {
                            "type": "send_notification",
                            "notification_type": "friend_accepted",
                            "sender": request.user.username,
                            "content": f"{request.user.username} sent you a connection request",
                            "url": notification.url
                        })
            else:
                messages.info(request, "Friend request already exists.")
    
    return redirect("profile", username=to_user.username)


@login_required
def cancel_request(request, request_id):
    friendship = get_object_or_404(Friendship, id=request_id, from_user=request.user)
    friendship.delete()
    messages.info(request, "Friend request cancelled.")
    return redirect(request.META.get('HTTP_REFERER', 'profile'))

@login_required
def accept_request(request, request_id):
    friendship = get_object_or_404(Friendship, id=request_id, to_user=request.user)
    request_sender = friendship.from_user
    friendship.status = Friendship.ACCEPTED
    friendship.save()
    messages.success(request, "Friend request accepted!")

    notification = Notification.objects.create(
        user = request_sender,
        sender = request.user,
        notification_type = 'friend_accepted',
        content = f"{request.user.username} accepted your connection request",
        url=reverse('profile', args=[request.user.username])
    )
    async_to_sync(channel_layer.group_send)(
        f"notifications_{request_sender.id}",
            {
                "type": "send_notification",
                "notification_type": "friend_accepted",
                "sender": request.user.username,
                "content": f"{request.user.username} accepted your connection request",
                "url": notification.url,
            })

    return redirect(request.META.get('HTTP_REFERER', 'profile'))

@login_required
def decline_request(request, request_id):
    friendship = get_object_or_404(Friendship, id=request_id, to_user=request.user)
    friendship.delete()
    messages.info(request, "Friend request declined.")
    return redirect(request.META.get('HTTP_REFERER', 'profile'))


@login_required
def friends_list(request):
    friends = Friendship.get_friends(request.user)
    return render(request, 'engagements/friends_list.html', {'friends': friends})

@login_required
def remove_friend(request, username):
    to_user = get_object_or_404(User, username=username)
    friendship = Friendship.objects.filter(
        (models.Q(from_user=request.user, to_user=to_user) | models.Q(from_user=to_user, to_user=request.user)),
        status=Friendship.ACCEPTED
    ).first()

    if friendship:
        friendship.delete()
        messages.info(request, "Friend removed.")
    else:
        messages.warning(request, "Friend not found.")

    return redirect(request.META.get('HTTP_REFERER', 'friends_list'))

#View for displaying friend suggestions, requests & friend list as well
@login_required
def friends_view(request):
    friend_requests = Friendship.objects.filter(to_user=request.user, status=Friendship.REQUESTED)

    friends = Friendship.get_friends(request.user)
    
    sent_requests = Friendship.objects.filter(
    from_user=request.user,
    status=Friendship.REQUESTED)

    friend_suggestions = User.objects.exclude(
    id__in=[friend.id for friend in friends]  # Exclude current friends
    ).exclude(
    id__in=[request.to_user.id for request in sent_requests]
    ).exclude(
    id__in=[request.from_user.id for request in friend_requests]
    ).exclude(id=request.user.id)

    print("Sent Requests:", list(sent_requests))
    return render(request, 'engagements/friends.html', {
        'friend_requests': friend_requests,
        'friends': friends,
        'friend_suggestions': friend_suggestions,
        'sent_requests': sent_requests,
    })
