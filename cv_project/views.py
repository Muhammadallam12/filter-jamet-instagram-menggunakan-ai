from django.shortcuts import render, redirect
from .models import Video
from .forms import VideoForm
from .cv.main import main
import os

def home_view(request):
    message = 'Upload your video!'
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            newvideo = Video(videofile=request.FILES['videofile'])
            newvideo.save()

            main(newvideo.videofile.url, './media/{}'.format(newvideo.videoid))

            os.remove(newvideo.videofile.path)

            return redirect('video/{}'.format(newvideo.videoid))
        else:
            message = 'The form is not valid. Fix the following error:'
    else:
        form = VideoForm() 

    context = {'form': form, 'message': message}
    return render(request, 'home.html', context)

def video_view(request, id=None):
  try:
    video = Video.objects.get(videoid=id)
  except Video.DoesNotExist:
    video = None

  context = {'video': video}
  return render(request, 'video.html', context)