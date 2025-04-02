from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notifications_list, name='notification-list'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/clear-all/', views.clear_all_notifications, name='clear_all_notifications'),
    path('notifications/unread-count/', views.unread_notifications_count, name='unread_notifications_count'),
]
