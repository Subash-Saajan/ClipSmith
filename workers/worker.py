import json
import redis
import ssl
import os
import sys

# Fix Windows console encoding for Unicode
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Set FFmpeg path for pydub before importing it
from pydub import AudioSegment
FFMPEG_PATH = r"C:\Users\Subash\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
AudioSegment.converter = FFMPEG_PATH
AudioSegment.ffprobe = FFMPEG_PATH.replace("ffmpeg.exe", "ffprobe.exe")

from config import REDIS_URL, CLIP_QUEUE
from downloader import download_video
from transcriber import transcribe_video
from analyzer import analyze_transcript, analyze_with_vision
from clipper import create_clips
from generator import generate_video
from database import update_job_status, save_clips, update_job_progress


def get_redis_client():
    """Create Redis client with SSL support for Upstash."""
    return redis.from_url(
        REDIS_URL,
        ssl_cert_reqs=ssl.CERT_NONE,
        decode_responses=True
    )


def process_clip_job(job_id: str, youtube_url: str, prompt: str):
    """Process a CLIP job - extract clips from long video using audio + vision analysis."""
    try:
        # Step 1: Download video (0-20%)
        update_job_status(job_id, "DOWNLOADING")
        update_job_progress(job_id, 0)
        print("[Step 1/4] Downloading video...")
        download_result = download_video(youtube_url, job_id)
        print(f"[Step 1/4] Downloaded: {download_result['title']}")
        print(f"[Step 1/4] Duration: {download_result['duration']}s")
        update_job_progress(job_id, 20)

        # Step 2: Transcribe video (20-40%)
        update_job_status(job_id, "TRANSCRIBING")
        update_job_progress(job_id, 25)
        print("\n[Step 2/4] Transcribing audio...")
        transcript_result = transcribe_video(download_result["file_path"])
        print(f"[Step 2/4] Language: {transcript_result['language']}")
        print(f"[Step 2/4] Segments: {len(transcript_result['segments'])}")
        update_job_progress(job_id, 40)

        # Step 3: Analyze with Vision + LLM (40-75%)
        update_job_status(job_id, "ANALYZING")
        update_job_progress(job_id, 45)
        print("\n[Step 3/4] Analyzing video (audio + vision)...")
        print("[Step 3/4] This uses LLaVA to 'see' the video frames...")

        # Use vision-enabled analysis (extracts frames and analyzes with LLaVA)
        clip_suggestions = analyze_with_vision(
            video_path=download_result["file_path"],
            transcript=transcript_result,
            prompt=prompt,
            num_frames=8  # Analyze 8 frames spread across video
        )

        print(f"[Step 3/4] Found {len(clip_suggestions)} clips:")
        for i, clip in enumerate(clip_suggestions, 1):
            print(f"  {i}. {clip['title']} ({clip['start']:.1f}s - {clip['end']:.1f}s)")
        update_job_progress(job_id, 75)

        # Step 4: Create clips with FFmpeg (75-100%)
        update_job_status(job_id, "CLIPPING")
        update_job_progress(job_id, 80)
        print("\n[Step 4/4] Creating clips with FFmpeg...")
        created_clips = create_clips(
            video_path=download_result["file_path"],
            job_id=job_id,
            clips_data=clip_suggestions
        )
        print(f"[Step 4/4] Created {len(created_clips)} clips!")
        update_job_progress(job_id, 95)

        # Save clips to database
        print("\n[DB] Saving clips to database...")
        saved_clips = save_clips(job_id, created_clips)

        # Mark job as completed
        update_job_status(job_id, "COMPLETED")
        update_job_progress(job_id, 100)

        print(f"\n{'='*50}")
        print(f"[Worker] Job {job_id} COMPLETED!")
        print(f"[Worker] Created clips:")
        for clip in created_clips:
            print(f"  - {clip['filename']} ({clip['duration']:.1f}s)")
        print(f"{'='*50}\n")

        return {
            "status": "completed",
            "download": download_result,
            "transcript": transcript_result,
            "clip_suggestions": clip_suggestions,
            "created_clips": saved_clips,
        }

    except Exception as e:
        print(f"\n[Worker] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        update_job_status(job_id, "FAILED", str(e))
        return {"status": "failed", "error": str(e)}


def process_generate_job(job_id: str, youtube_url: str, prompt: str):
    """Process a GENERATE job - AI generate new video from reference."""
    try:
        # Step 1: Download reference video (0-30%)
        update_job_status(job_id, "DOWNLOADING")
        update_job_progress(job_id, 0)
        print("[Step 1/2] Downloading reference video...")
        download_result = download_video(youtube_url, job_id)
        print(f"[Step 1/2] Downloaded: {download_result['title']}")
        print(f"[Step 1/2] Duration: {download_result['duration']}s")
        update_job_progress(job_id, 30)

        # Step 2: Generate new video with SVD (30-95%)
        update_job_status(job_id, "GENERATING")
        update_job_progress(job_id, 35)
        print("\n[Step 2/2] Generating new video with AI...")
        print(f"[Step 2/2] Prompt: {prompt}")

        generated_result = generate_video(
            reference_video_path=download_result["file_path"],
            job_id=job_id,
            prompt=prompt,
            num_frames=14,  # ~2 seconds at 7fps
            fps=7.0,
        )
        print(f"[Step 2/2] Generated: {generated_result['filename']}")
        update_job_progress(job_id, 95)

        # Save generated clip to database
        print("\n[DB] Saving generated video to database...")
        saved_clips = save_clips(job_id, [{
            "title": f"Generated: {prompt[:50]}..." if len(prompt) > 50 else f"Generated: {prompt}",
            "start": 0,
            "end": generated_result["duration"],
            "duration": generated_result["duration"],
            "file_path": generated_result["file_path"],
        }])

        # Mark job as completed
        update_job_status(job_id, "COMPLETED")
        update_job_progress(job_id, 100)

        print(f"\n{'='*50}")
        print(f"[Worker] Job {job_id} COMPLETED!")
        print(f"[Worker] Generated: {generated_result['filename']} ({generated_result['duration']:.1f}s)")
        print(f"{'='*50}\n")

        return {
            "status": "completed",
            "download": download_result,
            "generated": generated_result,
        }

    except Exception as e:
        print(f"\n[Worker] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        update_job_status(job_id, "FAILED", str(e))
        return {"status": "failed", "error": str(e)}


def process_job(job_data: dict):
    """Process a job - routes to CLIP or GENERATE pipeline."""
    job_id = job_data.get("id")
    youtube_url = job_data.get("youtubeUrl")
    prompt = job_data.get("prompt", "find the most interesting moments")
    job_type = job_data.get("jobType", "CLIP")

    print(f"\n{'='*50}")
    print(f"[Worker] Processing job: {job_id}")
    print(f"[Worker] Type: {job_type}")
    print(f"[Worker] URL: {youtube_url}")
    print(f"[Worker] Prompt: {prompt}")
    print(f"{'='*50}\n")

    if job_type == "GENERATE":
        return process_generate_job(job_id, youtube_url, prompt)
    else:
        return process_clip_job(job_id, youtube_url, prompt)


def run_worker():
    """Main worker loop - listens for jobs from Redis queue."""
    client = get_redis_client()
    print(f"[Worker] Connected to Redis")
    print(f"[Worker] Listening on queue: bull:{CLIP_QUEUE}:wait")

    while True:
        try:
            # BullMQ uses specific key patterns
            # Pop job from wait list
            result = client.brpop(f"bull:{CLIP_QUEUE}:wait", timeout=5)

            if result:
                _, job_id = result
                # Get job data
                job_key = f"bull:{CLIP_QUEUE}:{job_id}"
                job_raw = client.hget(job_key, "data")

                if job_raw:
                    job_data = json.loads(job_raw)
                    process_job(job_data)

        except KeyboardInterrupt:
            print("\n[Worker] Shutting down...")
            break
        except Exception as e:
            print(f"[Worker] Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    run_worker()
