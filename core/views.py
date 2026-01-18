from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from pathlib import Path
import shutil
import time

from .forms import YouTubeDownloadForm, VideoUploadForm, ProcessVideoForm
from .utils import download_youtube_video, build_command, clean_filename, has_video_stream, FFMPEG_COMMANDS
import subprocess

def get_media_files():
    """Helper to list files in media directories."""
    files = []
    
    # helper to add files
    def add_files(folder_name, source_type):
        path = settings.MEDIA_ROOT / folder_name
        path.mkdir(parents=True, exist_ok=True)
        for f in path.iterdir():
            if f.is_file() and f.name != ".gitignore":
                files.append({
                    'name': f.name,
                    'path': str(f.relative_to(settings.MEDIA_ROOT)).replace('\\', '/'), # relative path for display/selection
                    'full_path': str(f),
                    'source': source_type,
                    'size': f"{f.stat().st_size / (1024*1024):.2f} MB"
                })
    
    add_files("yt_videos", "YouTube")
    add_files("local_videos", "Local")
    add_files("download", "Processed")
    
    return files

def index(request):
    files = get_media_files()
    
    yt_form = YouTubeDownloadForm()
    upload_form = VideoUploadForm()
    process_form = ProcessVideoForm()
    

    # Prepare operations list for UI
    operations_list = []
    for key, val in FFMPEG_COMMANDS.items():
        operations_list.append({
            'key': key,
            'name': key.replace('_', ' ').title(),
            'description': val['description']
        })

    context = {
        'files': files,
        'yt_form': yt_form,
        'upload_form': upload_form,
        'process_form': process_form,
        'ffmpeg_commands': FFMPEG_COMMANDS, # Keep for JS lookup if needed
        'operations_list': operations_list,
    }
    return render(request, 'core/index.html', context)

from django.http import JsonResponse
import threading
import uuid
from .globals import PROGRESS_CACHE

def get_progress(request, task_id):
    """Returns the progress of a task."""
    progress = PROGRESS_CACHE.get(task_id, {'status': 'pending'})
    return JsonResponse(progress)

def run_download_task(url, task_id):
    """Wrapper to run download in thread."""
    try:
        msg = download_youtube_video(url, task_id)
        if msg:
            PROGRESS_CACHE[task_id] = {
                'status': 'complete',
                'percent': 100, 
                'msg': 'Download Complete!'
            }
        else:
             PROGRESS_CACHE[task_id] = {
                'status': 'error',
                'msg': 'Download failed (Check logs)'
            }
    except Exception as e:
        PROGRESS_CACHE[task_id] = {
            'status': 'error',
            'msg': str(e)
        }

def download_video(request):
    if request.method == 'POST':
        form = YouTubeDownloadForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            
            # Generate Task ID
            task_id = str(uuid.uuid4())
            PROGRESS_CACHE[task_id] = {
                'status': 'starting',
                'percent': 0,
                'msg': 'Initializing download...'
            }
            
            # Start Thread
            thread = threading.Thread(target=run_download_task, args=(url, task_id))
            thread.daemon = True
            thread.start()
            
            return JsonResponse({'task_id': task_id})
        else:
             return JsonResponse({'status': 'error', 'msg': 'Invalid URL'}, status=400)
    return redirect('index')

def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['file']
            save_path = settings.MEDIA_ROOT / 'local_videos'
            save_path.mkdir(parents=True, exist_ok=True)
            
            file_path = save_path / f.name
            with open(file_path, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
            
            messages.success(request, f"Uploaded {f.name} successfully.")
        else:
            messages.error(request, "Upload failed.")
    return redirect('index')

def process_video(request):
    if request.method == 'POST':
        file_path_rel = request.POST.get('selected_file')
        if not file_path_rel:
            messages.error(request, "No file selected.")
            return redirect('index')

        input_path = settings.MEDIA_ROOT / file_path_rel
        if not input_path.exists():
             messages.error(request, "File not found.")
             return redirect('index')

        form = ProcessVideoForm(request.POST)
        if form.is_valid():
            cmd_key = form.cleaned_data['command']
            
            # Prepare output path
            output_folder = settings.MEDIA_ROOT / "download"
            output_folder.mkdir(parents=True, exist_ok=True)
            
            # Clean filename (renames file on disk if needed)
            input_path = clean_filename(input_path)
            clean_name = input_path.stem

            # Just use stem + command suffix + proper extension
            # Note: We need to know target extension. 
            # ffmpeg commands in utils rely on {output} having extension.
            # Most output mp4. extract_audio uses wav/aac.
            
            ext = ".mp4"
            if "audio_wav" in cmd_key: ext = ".wav"
            elif "audio_aac" in cmd_key: ext = ".aac"
            
            timestamp = int(time.time())
            output_filename = f"{clean_name}_{cmd_key}_{timestamp}{ext}"
            output_path = output_folder / output_filename
            
            # kwargs
            kwargs = {
                "input": str(input_path),
                "output": str(output_path),
                "start": form.cleaned_data.get('start_time'),
                "end": form.cleaned_data.get('end_time'),
                "duration": form.cleaned_data.get('duration'),
                "width": form.cleaned_data.get('width'),
                "height": form.cleaned_data.get('height'),
            }
            
            # Special case for split_segments output_pattern
            if cmd_key == "split_segments":
                 kwargs["output_pattern"] = str(output_folder / f"{clean_name}_{timestamp}_%03d.mp4")

            try:
                command = build_command(cmd_key, **kwargs)
                # Run command
                subprocess.run(command, check=True)
                messages.success(request, f"Processed successfully! Saved to {output_filename}")
            except Exception as e:
                messages.error(request, f"Processing failed: {str(e)}")
        else:
            messages.error(request, "Invalid form data.")
            
    return redirect('index')

def delete_video(request):
    if request.method == 'POST':
        file_path_rel = request.POST.get('file_path')
        if file_path_rel:
            try:
                path = settings.MEDIA_ROOT / file_path_rel
                if path.exists():
                    path.unlink()
                    messages.success(request, "File deleted.")
            except Exception as e:
                messages.error(request, f"Delete failed: {str(e)}")
    return redirect('index')
