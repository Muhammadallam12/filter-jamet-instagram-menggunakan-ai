from django.urls import path, re_path
from .views import home_view, video_view

urlpatterns = [
  path('', home_view, name='home-view'),
  path('video/<int:id>/', video_view, name='video-view'),
]
