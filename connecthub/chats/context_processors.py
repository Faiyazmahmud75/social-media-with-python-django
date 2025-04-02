from django.contrib.auth.models import User
from .models import Message
from django.db.models import Count

def unread_chat_count(request):
    if request.user.is_authenticated:
        unread_conversations = Message.objects.filter(receiver=request.user, is_read=False).values("sender").distinct().count()
        unread_per_chat = Message.objects.filter(receiver=request.user, is_read=False).values('sender').annotate(unread_count=Count('id'))
        user_unread_counts = []
        for item in unread_per_chat:
            user = User.objects.get(id = item['sender'])
            user_unread_counts.append({'username':user.username, 'unread_count':item['unread_count']})
        return {'unread_counts':{'unread_conversations':unread_conversations, 'unread_per_chat':user_unread_counts}}
    return {'unread_counts': {'unread_conversations':0, 'unread_per_chat':[]}}