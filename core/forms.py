from django import forms


class YouTubeDownloadForm(forms.Form):
    url = forms.CharField(label="YouTube URL", widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'https://www.youtube.com/watch?v=...',
        'autocomplete': 'off'
    }))

from django.core.validators import FileExtensionValidator, RegexValidator

class VideoUploadForm(forms.Form):
    file = forms.FileField(
        label="Upload Video", 
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mkv', 'avi', 'webm', 'mov', 'flv', 'wav', 'mp3', 'aac', 'm4a'])],
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control'
        })
    )

class ProcessVideoForm(forms.Form):
    command = forms.ChoiceField(widget=forms.Select(attrs={
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
    factor = forms.FloatField(required=False, label="Speed Factor (PTS Multiplier)", widget=forms.NumberInput(attrs={
        'class': 'form-control command-param',
        'placeholder': '2.0 (Slow Motion)'
    }))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .utils import get_all_commands
        commands = get_all_commands()
        self.fields['command'].choices = [
            (key, config['description']) for key, config in commands.items()
        ]

class AddCommandForm(forms.Form):
    key = forms.CharField(
        label="Command Key (no spaces)", 
        validators=[RegexValidator(r'^[a-zA-Z0-9_]+$', 'Only alphanumeric characters and underscores are allowed.')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'my_custom_command'
        })
    )
    name = forms.CharField(label="Display Name", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'My Custom Command'
    }))
    description = forms.CharField(label="Description", widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Does something cool'
    }))
    command_str = forms.CharField(label="Command String", widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'ffmpeg -i {input} ... {output}',
        'rows': 3
    }))
