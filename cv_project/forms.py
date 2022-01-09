from django import forms


class VideoForm(forms.Form):
    videofile = forms.FileField(label='Select a video')
