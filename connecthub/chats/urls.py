from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_list, name='chat_list'),
    path('chat/<str:room_name>/', views.chat_room, name='chat'),
    # path('chats/unread_count/', views.unread_conversations_count, name='unread_count'),
]
