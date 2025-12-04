import os
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """Create a database connection."""
    return psycopg2.connect(DATABASE_URL)


def update_job_status(job_id: str, status: str, error_message: str = None):
    """Update job status in the database."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if error_message:
                cur.execute(
                    """UPDATE jobs SET status = %s, "errorMessage" = %s, "updatedAt" = NOW() WHERE id = %s""",
                    (status, error_message, job_id)
                )
            else:
                cur.execute(
                    """UPDATE jobs SET status = %s, "updatedAt" = NOW() WHERE id = %s""",
                    (status, job_id)
                )
        conn.commit()
        print(f"[DB] Updated job {job_id} status to {status}")
    finally:
        conn.close()


def update_job_progress(job_id: str, progress: int):
    """Update job progress percentage (0-100)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE jobs SET progress = %s, "updatedAt" = NOW() WHERE id = %s""",
                (progress, job_id)
            )
        conn.commit()
    finally:
        conn.close()


def save_clip(job_id: str, title: str, start_time: float, end_time: float, duration: float, url: str = None) -> str:
    """Save a clip to the database."""
    clip_id = str(uuid.uuid4())
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO clips (id, "jobId", title, "startTime", "endTime", duration, url, "createdAt")
                   VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())""",
                (clip_id, job_id, title, start_time, end_time, duration, url)
            )
        conn.commit()
        print(f"[DB] Saved clip {clip_id}: {title}")
        return clip_id
    finally:
        conn.close()


def save_clips(job_id: str, clips: list) -> list:
    """Save multiple clips to the database."""
    saved_clips = []
    for clip in clips:
        clip_id = save_clip(
            job_id=job_id,
            title=clip.get("title"),
            start_time=clip.get("start"),
            end_time=clip.get("end"),
            duration=clip.get("duration"),
            url=clip.get("url")
        )
        saved_clips.append({**clip, "id": clip_id})
    return saved_clips


def get_job(job_id: str) -> dict:
    """Get a job by ID."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM jobs WHERE id = %s", (job_id,))
            return cur.fetchone()
    finally:
        conn.close()


if __name__ == "__main__":
    # Test database connection
    conn = get_connection()
    print("[DB] Connection successful!")
    conn.close()
