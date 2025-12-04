import os
import subprocess
import yt_dlp
from config import DOWNLOAD_DIR
from database import update_job_progress

# Maximum video duration in seconds (10 minutes = 600 seconds)
MAX_DURATION_SECONDS = 600

# FFmpeg paths (installed via winget)
FFMPEG_DIR = r"C:\Users\Subash\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
FFMPEG_PATH = os.path.join(FFMPEG_DIR, "ffmpeg.exe")


# Global variable for job_id in progress hook
_current_job_id = None


def _progress_hook(d):
    """yt-dlp progress hook to report download progress."""
    global _current_job_id
    if d['status'] == 'downloading' and _current_job_id:
        # Calculate progress (download phase is 0-25% of total job)
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            download_pct = (downloaded / total) * 100
            # Download is 0-25% of the total progress
            overall_progress = int(download_pct * 0.25)
            update_job_progress(_current_job_id, overall_progress)
            print(f"[Downloader] Progress: {download_pct:.0f}%", end='\r')
    elif d['status'] == 'finished':
        print(f"\n[Downloader] Download complete, processing...")
        if _current_job_id:
            update_job_progress(_current_job_id, 25)


def download_video(youtube_url: str, job_id: str) -> dict:
    """
    Download video from YouTube using yt-dlp.
    Returns dict with file path and metadata.
    """
    global _current_job_id
    _current_job_id = job_id  # Set for progress hook

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # First, check video duration without downloading
    check_opts = {
        'quiet': True,
        'ffmpeg_location': FFMPEG_DIR,
    }
    with yt_dlp.YoutubeDL(check_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        duration = info.get("duration", 0)

        if duration > MAX_DURATION_SECONDS:
            raise ValueError(
                f"Video too long: {duration}s. Maximum allowed: {MAX_DURATION_SECONDS}s ({MAX_DURATION_SECONDS//60} minutes). "
                "This limit prevents excessive API costs."
            )

    output_template = os.path.join(DOWNLOAD_DIR, f"{job_id}.%(ext)s")
    final_output = os.path.join(DOWNLOAD_DIR, f"{job_id}.mp4")

    ydl_opts = {
        # Most permissive format - no restrictions, just get something
        'format': 'b',  # 'b' = best single file with both video and audio
        'outtmpl': output_template,
        'ffmpeg_location': FFMPEG_DIR,
        'quiet': False,
        'no_warnings': False,
        'retries': 3,
        'fragment_retries': 3,
        # Force merge to mp4 if separate streams
        'merge_output_format': 'mp4',
        # Convert to mp4 after download
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        # Use Android client which has fewer restrictions
        'extractor_args': {'youtube': {'player_client': ['android']}},
        # Progress hook for reporting download progress
        'progress_hooks': [_progress_hook],
    }

    print(f"[Downloader] Starting download: {youtube_url}")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)

        # Find the downloaded file
        file_path = None
        for ext in ['mp4', 'webm', 'mkv']:
            check_path = os.path.join(DOWNLOAD_DIR, f"{job_id}.{ext}")
            if os.path.exists(check_path) and os.path.getsize(check_path) > 0:
                file_path = check_path
                break

        if not file_path:
            raise Exception(f"Downloaded file not found in {DOWNLOAD_DIR}")

        # Convert to mp4 if not already
        if not file_path.endswith('.mp4'):
            print(f"[Downloader] Converting {file_path} to mp4...")
            convert_cmd = [
                FFMPEG_PATH, '-y', '-i', file_path,
                '-c:v', 'copy', '-c:a', 'aac',
                final_output
            ]
            subprocess.run(convert_cmd, capture_output=True)
            if os.path.exists(final_output) and os.path.getsize(final_output) > 0:
                os.remove(file_path)
                file_path = final_output

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise Exception("The downloaded file is empty")

        print(f"[Downloader] File saved: {file_path} ({file_size / 1024 / 1024:.1f} MB)")

        return {
            "file_path": file_path,
            "title": info.get("title"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
        }


if __name__ == "__main__":
    # Test download
    result = download_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "test-job")
    print(result)
