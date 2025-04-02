import datetime

from django.http import JsonResponse
from django.utils.timezone import make_aware, is_naive
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count

from .models import Message
from engagements.models import Friendship

# Get friends and their last messages
def get_friends_with_messages(user):
    friends = Friendship.get_friends(user)
    friends_with_conversations = []
    friends_without_conversations = []

    unread_counts = Message.objects.filter(
        receiver=user, is_read=False
    ).values("sender").annotate(unread_count=Count("id"))

    unread_dict = {item["sender"]: item["unread_count"] for item in unread_counts}

    for friend in friends:
        last_message = Message.objects.filter(
            Q(sender=user, receiver=friend) | Q(sender=friend, receiver=user)
        ).order_by('-timestamp').first()

        unread_count = unread_dict.get(friend.id, 0)

        if last_message:
            friends_with_conversations.append({
                'friend': friend,
                'last_message': last_message,
                'unread_count': unread_count
            })
        else:
            friends_without_conversations.append(friend)

    # Sort by most recent message
    friends_with_conversations.sort(
        key=lambda x: x['last_message'].timestamp, reverse=True
    )

    return friends_with_conversations, friends_without_conversations



@login_required
def chat_list(request):
    friends_with_conversations, friends_without_conversations = get_friends_with_messages(request.user)

    return render(request, 'chats/chats.html', {
        "friends_with_conversations": friends_with_conversations,
        "friends_without_conversations": friends_without_conversations,
    })


@login_required
def chat_room(request, room_name):
    friends_with_conversations, friends_without_conversations = get_friends_with_messages(request.user)
    
    friend = get_object_or_404(User, username=room_name)
    search_query = request.GET.get('search', '')

    # Mark messages as read
    Message.objects.filter(sender=friend, receiver=request.user, is_read=False).update(is_read=True)

    # Fetch chat messages
    chats = Message.objects.filter(
        (Q(sender=request.user, receiver=friend)) | (Q(receiver=request.user, sender=friend))
    ).order_by('timestamp')

    # Apply search filter if needed
    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))

    # Get last messages from all users
    users = User.objects.exclude(id=request.user.id)
    user_last_messages = []
    
    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user, receiver=user)) | (Q(receiver=request.user, sender=user))
        ).order_by('-timestamp').first()

        user_last_messages.append({
            'user': user,
            'last_message': last_message
        })

    # Sort users by last message timestamp
    user_last_messages.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] and not is_naive(x['last_message'].timestamp) 
                     else datetime.datetime.min.replace(tzinfo=datetime.timezone.utc),
        reverse=True
    )

    return render(request, 'chats/chats.html', {
        'room_name': room_name,
        'chats': chats,
        'users': users,
        'user_last_messages': user_last_messages,
        'search_query': search_query,
        'friend': friend,
        "friends_with_conversations": friends_with_conversations,
        "friends_without_conversations": friends_without_conversations,
    })
