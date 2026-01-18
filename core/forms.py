from django import forms
from .utils import FFMPEG_COMMANDS

class YouTubeDownloadForm(forms.Form):
    url = forms.CharField(label="YouTube URL", widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'https://www.youtube.com/watch?v=...'
    }))

class VideoUploadForm(forms.Form):
    file = forms.FileField(label="Upload Video", widget=forms.ClearableFileInput(attrs={
        'class': 'form-control'
    }))

class ProcessVideoForm(forms.Form):
    COMMAND_CHOICES = [
        (key, config['description']) for key, config in FFMPEG_COMMANDS.items()
    ]
    
    command = forms.ChoiceField(choices=COMMAND_CHOICES, widget=forms.Select(attrs={
        'class': 'form-control',
        'id': 'command-select'
    }))
    
    # Optional fields for various commands
    start_time = forms.CharField(required=False, label="Start Time (HH:MM:SS)", widget=forms.TextInput(attrs={
        'class': 'form-control command-param',
        'placeholder': '00:00:00'
    }))
    end_time = forms.CharField(required=False, label="End Time (HH:MM:SS)", widget=forms.TextInput(attrs={
        'class': 'form-control command-param',
        'placeholder': '00:00:10'
    }))
    duration = forms.IntegerField(required=False, label="Segment Duration (s)", widget=forms.NumberInput(attrs={
        'class': 'form-control command-param',
        'placeholder': '60'
    }))
    width = forms.IntegerField(required=False, label="Width", widget=forms.NumberInput(attrs={
        'class': 'form-control command-param',
        'placeholder': '1920'
    }))
    height = forms.IntegerField(required=False, label="Height", widget=forms.NumberInput(attrs={
        'class': 'form-control command-param',
        'placeholder': '1080'
    }))
