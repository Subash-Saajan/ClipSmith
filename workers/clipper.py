import os
import subprocess
from config import DOWNLOAD_DIR

FFMPEG_PATH = r"C:\Users\Subash\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
CLIPS_DIR = os.path.join(DOWNLOAD_DIR, "clips")


def create_clip(video_path: str, job_id: str, clip_index: int, start: float, end: float, title: str = None) -> dict:
    """
    Extract a clip from video using FFmpeg.

    Args:
        video_path: Path to source video
        job_id: Job ID for naming
        clip_index: Clip number (1, 2, 3...)
        start: Start time in seconds
        end: End time in seconds
        title: Optional title for the clip

    Returns:
        Dict with clip file path and metadata
    """
    os.makedirs(CLIPS_DIR, exist_ok=True)

    duration = end - start
    output_filename = f"{job_id}_clip_{clip_index}.mp4"
    output_path = os.path.join(CLIPS_DIR, output_filename)

    print(f"[Clipper] Creating clip {clip_index}: {start:.1f}s - {end:.1f}s ({duration:.1f}s)")

    # FFmpeg command for precise cutting with re-encoding
    cmd = [
        FFMPEG_PATH,
        "-y",  # Overwrite output
        "-ss", str(start),  # Start time (before input for fast seek)
        "-i", video_path,  # Input file
        "-t", str(duration),  # Duration
        "-c:v", "libx264",  # Video codec
        "-preset", "fast",  # Encoding speed
        "-crf", "23",  # Quality (lower = better, 18-28 is good)
        "-c:a", "aac",  # Audio codec
        "-b:a", "128k",  # Audio bitrate
        "-movflags", "+faststart",  # Web optimization
        output_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[Clipper] FFmpeg error: {result.stderr}")
        raise Exception(f"FFmpeg failed: {result.stderr}")

    # Get file size
    file_size = os.path.getsize(output_path)

    print(f"[Clipper] Created: {output_filename} ({file_size / 1024 / 1024:.1f} MB)")

    return {
        "file_path": output_path,
        "filename": output_filename,
        "start": float(start),  # Ensure native Python float for DB
        "end": float(end),
        "duration": float(duration),
        "title": title,
        "size_bytes": file_size,
    }


def create_clips(video_path: str, job_id: str, clips_data: list) -> list:
    """
    Create multiple clips from a video.

    Args:
        video_path: Path to source video
        job_id: Job ID
        clips_data: List of clip dicts with start, end, title

    Returns:
        List of created clip info
    """
    created_clips = []

    for i, clip in enumerate(clips_data, 1):
        try:
            result = create_clip(
                video_path=video_path,
                job_id=job_id,
                clip_index=i,
                start=clip["start"],
                end=clip["end"],
                title=clip.get("title")
            )
            created_clips.append(result)
        except Exception as e:
            print(f"[Clipper] Failed to create clip {i}: {e}")

    return created_clips


if __name__ == "__main__":
    # Test clipping
    import sys
    if len(sys.argv) > 1:
        test_video = sys.argv[1]
        clips = create_clips(test_video, "test", [
            {"start": 0, "end": 10, "title": "Test clip 1"},
            {"start": 15, "end": 30, "title": "Test clip 2"},
        ])
        print(f"\nCreated {len(clips)} clips")
        for clip in clips:
            print(f"  - {clip['filename']}: {clip['duration']:.1f}s")
    else:
        print("Usage: python clipper.py <video_path>")
