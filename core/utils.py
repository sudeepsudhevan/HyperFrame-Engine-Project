import subprocess
import re
from pathlib import Path
from django.conf import settings

import json
import os

# =========================
# FFmpeg Commands
# =========================

BASE_FFMPEG_COMMANDS = {
    "base_best_quality": {
        "command": [
            "ffmpeg", "-y", "-i", "{input}", "-map", "0:v:0", "-map", "0:a:0?",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-level", "4.1", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", "{output}"
        ],
        "description": "Visually lossless video + high quality AAC audio"
    },
    "trim_reencode": {
        "command": [
            "ffmpeg", "-y", "-ss", "{start}", "-to", "{end}", "-i", "{input}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac",
            "-b:a", "128k", "-movflags", "+faststart", "{output}"
        ],
        "description": "Frame-accurate trimming with re-encoding"
    },
    "trim_copy": {
        "command": [
            "ffmpeg", "-y", "-ss", "{start}", "-to", "{end}", "-i", "{input}",
            "-c", "copy", "{output}"
        ],
        "description": "Fast trim without quality loss (keyframe based)"
    },
    "split_segments": {
        "command": [
            "ffmpeg", "-y", "-i", "{input}", "-map", "0", "-c", "copy",
            "-f", "segment", "-segment_time", "{duration}", "-reset_timestamps", "1",
            "{output_pattern}"
        ],
        "description": "Split video into equal-length segments"
    },
    "compress_high_quality": {
        "command": [
            "ffmpeg", "-y", "-i", "{input}", "-c:v", "libx264", "-preset", "fast",
            "-crf", "26", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "{output}"
        ],
        "description": "Balanced compression (YouTube-grade quality)"
    },
    "compress_ultra": {
        "command": [
            "ffmpeg", "-y", "-i", "{input}", "-c:v", "libx265", "-preset", "fast",
            "-crf", "28", "-c:a", "aac", "-b:a", "96k", "{output}"
        ],
        "description": "Maximum compression using H.265"
    },
    "extract_audio_wav": {
        "command": [
            "ffmpeg", "-y", "-i", "{input}", "-vn", "-c:a", "pcm_s16le", "{output}"
        ],
        "description": "Extract lossless WAV audio"
    },
    "extract_audio_aac": {
        "command": [
            "ffmpeg", "-y", "-i", "{input}", "-vn", "-c:a", "aac", "-b:a", "192k", "{output}"
        ],
        "description": "Extract high-quality AAC audio"
    },
    "extract_video_only": {
        "command": [
            "ffmpeg", "-y", "-i", "{input}", "-an", "-c:v", "libx264",
            "-preset", "fast", "-crf", "23", "{output}"
        ],
        "description": "Extract video stream only"
    },
    "resize_video": {
        "command": [
            "ffmpeg", "-y", "-i", "{input}", "-vf", "scale={width}:{height}:flags=lanczos",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a", "aac",
            "-b:a", "128k", "{output}"
        ],
        "description": "Resize video using high-quality Lanczos scaling"
    },
    "remux_copy": {
        "command": [
            "ffmpeg", "-y", "-i", "{input}", "-c", "copy", "{output}"
        ],
        "description": "Change container format without re-encoding"
    }
}

def load_custom_commands():
    """Load custom commands from the JSON file."""
    custom_file_path = Path("custom_commands.json")
    if not custom_file_path.exists():
        return {}
    try:
        with open(custom_file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def get_all_commands():
    """Merge base and custom commands."""
    commands = BASE_FFMPEG_COMMANDS.copy()
    commands.update(load_custom_commands())
    return commands

def save_custom_command(key, command_list, description):
    """Save a new custom command to the JSON file."""
    custom_commands = load_custom_commands()
    custom_commands[key] = {
        "command": command_list,
        "description": description
    }
    with open("custom_commands.json", 'w') as f:
        json.dump(custom_commands, f, indent=4)

def build_command(profile: str, **kwargs) -> list:
    """Build an FFmpeg command from a profile."""
    all_commands = get_all_commands()
    if profile not in all_commands:
        raise ValueError(f"Unknown profile: {profile}")
    template = all_commands[profile]["command"]
    return [arg.format(**kwargs) for arg in template]


# =========================
# Video Checks
# =========================

def has_video_stream(file_path: Path) -> bool:
    """Checks if a file has a video stream using ffprobe."""
    command = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(file_path)
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip() == "video"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


# =========================
# Download & Cleanup
# =========================

import yt_dlp
from .globals import PROGRESS_CACHE

def download_youtube_video(youtube_url: str, task_id: str = None) -> str | None:
    """Downloads a YouTube video to MEDIA_ROOT/yt_videos using yt_dlp library."""
    yt_video_folder = settings.MEDIA_ROOT / "yt_videos"
    yt_video_folder.mkdir(parents=True, exist_ok=True)

    def progress_hook(d):
        if not task_id:
            return
            
        if d['status'] == 'downloading':
            try:
                p = d.get('_percent_str', '0%').replace('%','')
                PROGRESS_CACHE[task_id] = {
                    'status': 'processing',
                    'percent': float(p) if p != 'N/A' else 0,
                    'eta': d.get('_eta_str', '...'),
                    'msg': f"Downloading: {d.get('_percent_str')} (ETA: {d.get('_eta_str')})"
                }
            except:
                pass
        elif d['status'] == 'finished':
            PROGRESS_CACHE[task_id] = {
                'status': 'complete',
                'percent': 100,
                'eta': '0s',
                'msg': 'Download Complete! Processing...'
            }

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f"{yt_video_folder}/%(title)s.%(ext)s",
        'restrictfilenames': True,
        'progress_hooks': [progress_hook],
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        
        # Determine filename (simplistic approach compatible with previous logic)
        files = list(yt_video_folder.glob("*"))
        if not files:
            return None
        return "Success" # Return string to indicate success
        
    except Exception as e:
        print(f"Error: {e}")
        if task_id:
             PROGRESS_CACHE[task_id] = {
                'status': 'error',
                'msg': str(e)
            }
        return None

def clean_filename(file_path: Path) -> Path:
    """Cleans a filename and renames the file."""
    file_stem = file_path.stem
    file_ext = file_path.suffix
    
    clean_name = re.sub(r"[_\[\]\(\)]", "", file_stem).replace(" ", "_")
    new_path = file_path.parent / f"{clean_name}{file_ext}"
    
    if new_path != file_path:
        file_path.rename(new_path)
        
    return new_path
