from django.urls import path
from . import views

app_name = 'media_library'

urlpatterns = [
    path('upload/', views.upload, name='upload'),
    path('media/', views.view_media, name='view_media'),
    # path('delete/<int:pk>/', views.delete, name='delete'),
    # path('album/create/', views.create_album, name='create_album'),
    # path('album/<int:pk>/', views.album_detail, name='album_detail'),
    # path('album/<int:pk>/delete/', views.delete_album, name='delete_album'),
    # path('album/<int:pk>/add/', views.add_to_album, name='add_to_album'),
    # path('album/<int:album_pk>/remove/<int:media_pk>/', views.remove_from_album, name='remove_from_album'),
    # path('album/<int:pk>/edit/', views.edit_album, name='edit_album'),
]