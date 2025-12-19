"""
Vision Analyzer - Uses LLaVA to analyze video frames and understand visual content.
Extracts key frames, describes what's happening, and identifies viral moments.
"""

import os
import sys
import cv2
import base64
import requests
import tempfile
from typing import List, Dict

# Fix Windows console encoding for Unicode
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

OLLAMA_URL = "http://localhost:11434/api/generate"
VISION_MODEL = "llava:7b"


def safe_print(msg: str):
    """Print with Unicode error handling for Windows."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'replace').decode('ascii'))


def extract_frames(video_path: str, num_frames: int = 10) -> List[Dict]:
    """
    Extract evenly spaced frames from a video.

    Args:
        video_path: Path to the video file
        num_frames: Number of frames to extract

    Returns:
        List of dicts with frame data: {timestamp, frame_path, frame_base64}
    """
    safe_safe_print(f"[Vision] Extracting {num_frames} frames from video...")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"Could not open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0

    safe_print(f"[Vision] Video: {total_frames} frames, {fps:.1f} fps, {duration:.1f}s duration")

    # Calculate frame indices to extract (evenly spaced)
    if num_frames >= total_frames:
        frame_indices = list(range(total_frames))
    else:
        step = total_frames / num_frames
        frame_indices = [int(step * i) for i in range(num_frames)]

    frames = []
    temp_dir = tempfile.mkdtemp(prefix="clipsmith_frames_")

    for i, frame_idx in enumerate(frame_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()

        if ret:
            timestamp = frame_idx / fps if fps > 0 else 0

            # Resize frame for faster processing (max 512px width)
            height, width = frame.shape[:2]
            if width > 512:
                scale = 512 / width
                frame = cv2.resize(frame, (512, int(height * scale)))

            # Save frame temporarily
            frame_path = os.path.join(temp_dir, f"frame_{i:04d}.jpg")
            cv2.imwrite(frame_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])

            # Convert to base64 for LLaVA
            with open(frame_path, "rb") as f:
                frame_base64 = base64.b64encode(f.read()).decode("utf-8")

            frames.append({
                "index": i,
                "frame_idx": frame_idx,
                "timestamp": round(timestamp, 2),
                "frame_path": frame_path,
                "frame_base64": frame_base64,
            })

    cap.release()
    safe_print(f"[Vision] Extracted {len(frames)} frames")
    return frames


def analyze_frame(frame_base64: str, timestamp: float, context: str = "") -> Dict:
    """
    Analyze a single frame using LLaVA.

    Args:
        frame_base64: Base64 encoded image
        timestamp: Timestamp in seconds
        context: Optional context about what to look for

    Returns:
        Dict with description and analysis
    """
    prompt = f"""Analyze this video frame at {timestamp:.1f} seconds.

Describe in detail:
1. What is happening in this scene?
2. Who/what is visible (people, objects, text on screen)?
3. What emotion or mood does this convey?
4. Is there anything attention-grabbing or viral-worthy?
5. Rate the visual interest (1-10) and explain why.

{f"Additional context: {context}" if context else ""}

Be specific and detailed. This helps identify the best moments for short clips."""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": VISION_MODEL,
                "prompt": prompt,
                "images": [frame_base64],
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 500,
                }
            },
            timeout=120
        )

        if response.status_code != 200:
            return {"error": f"LLaVA error: {response.text}", "description": ""}

        result = response.json().get("response", "")
        return {
            "timestamp": timestamp,
            "description": result,
            "error": None
        }

    except Exception as e:
        return {
            "timestamp": timestamp,
            "description": "",
            "error": str(e)
        }


def analyze_video_content(video_path: str, num_frames: int = 10, user_prompt: str = "") -> Dict:
    """
    Analyze video content by extracting and analyzing multiple frames.

    Args:
        video_path: Path to the video file
        num_frames: Number of frames to analyze
        user_prompt: User's prompt about what to look for

    Returns:
        Dict with full video analysis including frame descriptions
    """
    safe_print(f"[Vision] Starting video content analysis...")
    safe_print(f"[Vision] User prompt: {user_prompt or 'None'}")

    # Extract frames
    frames = extract_frames(video_path, num_frames)

    # Analyze each frame
    frame_analyses = []
    for i, frame in enumerate(frames):
        safe_print(f"[Vision] Analyzing frame {i+1}/{len(frames)} (t={frame['timestamp']:.1f}s)...")

        analysis = analyze_frame(
            frame["frame_base64"],
            frame["timestamp"],
            user_prompt
        )

        frame_analyses.append({
            "timestamp": frame["timestamp"],
            "description": analysis.get("description", ""),
            "error": analysis.get("error"),
        })

        if analysis.get("description"):
            # Print short preview
            preview = analysis["description"][:150].replace("\n", " ")
            safe_print(f"[Vision]   → {preview}...")

    # Generate overall video summary
    safe_print(f"[Vision] Generating video summary...")
    summary = generate_video_summary(frame_analyses, user_prompt)

    # Clean up temp frames
    for frame in frames:
        try:
            os.remove(frame["frame_path"])
        except:
            pass

    return {
        "num_frames_analyzed": len(frame_analyses),
        "frame_analyses": frame_analyses,
        "summary": summary,
        "viral_moments": identify_viral_moments(frame_analyses),
    }


def generate_video_summary(frame_analyses: List[Dict], user_prompt: str = "") -> str:
    """
    Generate an overall summary of the video based on frame analyses.
    """
    # Combine frame descriptions
    descriptions = []
    for fa in frame_analyses:
        if fa.get("description"):
            descriptions.append(f"[{fa['timestamp']:.1f}s] {fa['description']}")

    combined = "\n\n".join(descriptions)

    prompt = f"""Based on these frame-by-frame analyses of a video, provide a comprehensive summary:

{combined}

{f"The user is looking for: {user_prompt}" if user_prompt else ""}

Please provide:
1. OVERALL SUMMARY: What is this video about? (2-3 sentences)
2. KEY MOMENTS: List the most interesting/engaging timestamps
3. CONTENT TYPE: What type of content is this? (tutorial, entertainment, vlog, etc.)
4. VIRAL POTENTIAL: What makes this video engaging or shareable?
5. BEST CLIP SUGGESTIONS: Which timestamps would make the best short clips and why?

Be specific about timestamps when suggesting clips."""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": VISION_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 1000,
                }
            },
            timeout=180
        )

        if response.status_code == 200:
            return response.json().get("response", "")
        return ""

    except Exception as e:
        safe_print(f"[Vision] Summary error: {e}")
        return ""


def identify_viral_moments(frame_analyses: List[Dict]) -> List[Dict]:
    """
    Identify potentially viral moments based on frame analyses.
    Looks for keywords that indicate high engagement potential.
    """
    viral_keywords = [
        "surprising", "unexpected", "funny", "emotional", "dramatic",
        "shocking", "amazing", "incredible", "reaction", "reveal",
        "transformation", "before and after", "fail", "win", "satisfying",
        "oddly satisfying", "plot twist", "climax", "peak", "intense"
    ]

    moments = []
    for fa in frame_analyses:
        desc_lower = fa.get("description", "").lower()

        # Count viral keywords
        keyword_matches = [kw for kw in viral_keywords if kw in desc_lower]

        # Check for high interest ratings mentioned
        has_high_rating = any(f"{i}/10" in desc_lower or f"{i} out of 10" in desc_lower
                            for i in range(7, 11))

        if keyword_matches or has_high_rating:
            moments.append({
                "timestamp": fa["timestamp"],
                "keywords": keyword_matches,
                "high_rating": has_high_rating,
                "description_preview": fa.get("description", "")[:200]
            })

    return moments


if __name__ == "__main__":
    # Test with a sample video
    import sys

    if len(sys.argv) < 2:
        print("Usage: python vision_analyzer.py <video_path> [num_frames]")
        sys.exit(1)

    video_path = sys.argv[1]
    num_frames = int(sys.argv[2]) if len(sys.argv) > 2 else 8

    print(f"\n{'='*60}")
    print(f"Analyzing: {video_path}")
    print(f"Frames to analyze: {num_frames}")
    print(f"{'='*60}\n")

    result = analyze_video_content(video_path, num_frames, "Find the most engaging moments")

    print(f"\n{'='*60}")
    print("VIDEO ANALYSIS COMPLETE")
    print(f"{'='*60}")

    print(f"\n## Summary:\n{result['summary']}")

    if result['viral_moments']:
        print(f"\n## Potential Viral Moments:")
        for vm in result['viral_moments']:
            print(f"  - {vm['timestamp']:.1f}s: {', '.join(vm['keywords'])}")
