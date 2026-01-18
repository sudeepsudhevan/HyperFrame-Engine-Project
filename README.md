# Video Forge - Premium Video Processor

A powerful, premium-styled web application for downloading YouTube videos and performing professional video operations using FFmpeg. Built with Django and vanilla CSS.

## Features

### 📺 YouTube Actions
- **Download**: Fetch maximum quality videos from YouTube.
- **Library**: Manage your downloaded videos in a dedicated library.

### 🛠 FFmpeg Operations
Perform advanced video processing tasks on both downloaded and uploaded files:
- **Baseline Best**: Convert to high-quality H.264/AAC.
- **Trim**: Cut videos with frame-accurate re-encoding or fast copying.
- **Split**: Automatically split videos into equal-length segments.
- **Compress**: Optimize file size (H.264 High Quality or H.265 Ultra Compression).
- **Extract**: Isolate audio (WAV/AAC) or video streams.
- **Resize**: Scale videos with high-quality Lanczos resampling.
- **Remux**: Change container formats without re-encoding.

### 🎨 Premium UI
- **Glassmorphism Design**: Modern, translucent interface.
- **Responsive**: Works beautifully on all screen sizes.
- **Interactive**: Real-time feedback and dynamic form parameters.

## Prerequisites

1. **Python 3.10+**
2. **FFmpeg**: Must be installed and added to your system's PATH.
   - [FFmpeg Installation Guide](https://ffmpeg.org/download.html)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd video_project
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Run the Server**:
   ```bash
   python manage.py runserver
   ```

5. **Access the App**:
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

## Project Structure

- `core/`: Main Django application containing views, models, and forms.
- `core/utils.py`: Logic for FFmpeg commands and video handling.
- `core/templates/`: HTML templates.
- `static/css/`: Premium CSS styles.
- `media/`:
    - `yt_videos/`: YouTube downloads.
    - `local_videos/`: User uploads.
    - `download/`: Processed output files.
- `legacy/`: Original Python scripts (archived).

## Usage

1. **Download**: Navigate to the "Download" tab, paste a YouTube link, and hit Download.
2. **Upload**: Use the "Upload" tab to add local files to your library.
3. **Process**:
    - Select a file from the "Media Library" list.
    - Go to the "Process" tab.
    - Choose an operation (e.g., "Compress (High Quality)").
    - Fill in any required parameters (e.g., Start/End time).
    - Click "Run Operation".
