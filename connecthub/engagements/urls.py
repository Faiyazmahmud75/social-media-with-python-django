from django.urls import path
from . import views

urlpatterns = [
    path('send-request/<str:username>/', views.send_request, name='send_request'),
    path('cancel-request/<int:request_id>/', views.cancel_request, name='cancel_request'),
    path('accept-request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('decline-request/<int:request_id>/', views.decline_request, name='decline_request'),
    path('friends/', views.friends_list, name='friends_list'),
    path('remove-friend/<str:username>/', views.remove_friend, name='remove_friend'),
    path('make-connections/', views.friends_view, name='make_connections'),
]
