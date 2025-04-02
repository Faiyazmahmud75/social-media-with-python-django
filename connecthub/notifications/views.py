from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Notification
from django.http import JsonResponse

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-timestamp')

    unread_count = notifications.filter(read=False).count()
    
    for notification in notifications:
        notification.sender_image = (
            notification.sender.profile.image.url 
            if hasattr(notification.sender, 'profile') and notification.sender.profile.image 
            else "/static/default_profile.jpg"
        )

    return render(request, 'notifications/notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })


@login_required
def unread_notifications_count(request):
    unread_count = Notification.objects.filter(user=request.user, read=False).count()
    return JsonResponse({"unread_count": unread_count})

@login_required
def mark_notification_read(request, notification_id):
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@login_required
def mark_all_notifications_read(request):
    notifications = Notification.objects.filter(user=request.user, read=False)
    if notifications.exists():
        if request.method == 'POST':
            notifications.update(read=True)
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'No unread notifications'}, status=400)

@login_required
def clear_all_notifications(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)