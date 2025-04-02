from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import MediaFile

# Create your views here.

@login_required
def upload(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        media = MediaFile.objects.create(user=request.user, file=uploaded_file)
        return redirect('home')  # Redirect after successful upload
    return render(request, 'upload_media.html')

def view_media(request):
    media_files = MediaFile.objects.all()
    return render(request, 'media_library/view_media.html', {'media_files': media_files})