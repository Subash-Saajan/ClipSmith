import os
import json
import requests
from dotenv import load_dotenv
from vision_analyzer import analyze_video_content

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"


def analyze_with_vision(video_path: str, transcript: dict, prompt: str, num_frames: int = 8) -> list:
    """
    Analyze video using BOTH transcript AND visual content for better clip selection.

    Args:
        video_path: Path to the video file
        transcript: Dict with 'segments' and 'full_text' from transcriber
        prompt: User's prompt describing what clips to find
        num_frames: Number of frames to analyze visually

    Returns:
        List of clip suggestions with start/end times
    """
    duration = transcript.get("duration", 300)

    print(f"[Analyzer] Starting combined audio+vision analysis...")
    print(f"[Analyzer] Video duration: {duration:.1f}s")

    # Step 1: Get visual analysis
    print(f"\n[Analyzer] === VISUAL ANALYSIS ===")
    vision_result = analyze_video_content(video_path, num_frames, prompt)

    # Step 2: Prepare transcript with timestamps
    timestamped_text = []
    for seg in transcript["segments"]:
        start_sec = seg["start"]
        end_sec = seg["end"]
        timestamped_text.append(f"[{start_sec:.1f}s - {end_sec:.1f}s] {seg['text']}")

    transcript_with_times = "\n".join(timestamped_text)

    # Step 3: Prepare visual summary
    visual_descriptions = []
    for fa in vision_result.get("frame_analyses", []):
        if fa.get("description"):
            visual_descriptions.append(f"[{fa['timestamp']:.1f}s] {fa['description'][:300]}")

    visual_summary = "\n\n".join(visual_descriptions)
    overall_summary = vision_result.get("summary", "")

    # Step 4: Combined analysis prompt
    print(f"\n[Analyzer] === COMBINED ANALYSIS ===")
    print(f"[Analyzer] Sending to Ollama ({OLLAMA_MODEL})...")

    full_prompt = f"""You are a video clip extraction expert. Analyze BOTH the audio transcript AND visual descriptions to find the best viral moments.

VIDEO DURATION: {duration:.1f} seconds total

USER REQUEST: {prompt}

=== AUDIO TRANSCRIPT ===
{transcript_with_times}

=== VISUAL ANALYSIS (what's happening on screen) ===
{visual_summary}

=== OVERALL VIDEO SUMMARY ===
{overall_summary}

INSTRUCTIONS:
1. Find 3-5 moments that would make great short clips (15-45 seconds each)
2. Consider BOTH what's being said AND what's visually happening
3. Prioritize moments with:
   - Visual action + interesting audio together
   - Emotional peaks (reactions, reveals, surprises)
   - Memorable quotes with visual context
   - Engaging visuals even if audio is quiet
4. The "start" and "end" values must be numbers in SECONDS
5. Make sure clips don't overlap

RESPOND WITH ONLY THIS JSON FORMAT:
{{"clips": [
  {{"title": "Short catchy title", "start": 45.0, "end": 75.0, "reason": "Why this works (visual + audio)"}},
  {{"title": "Another title", "start": 120.0, "end": 150.0, "reason": "Why this moment stands out"}}
]}}"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 1024,
            }
        },
        timeout=180
    )

    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.text}")

    result_text = response.json().get("response", "")
    print(f"[Analyzer] Raw response: {result_text[:300]}...")

    # Parse and validate clips
    clips = parse_and_validate_clips(result_text, duration, transcript)

    print(f"[Analyzer] Found {len(clips)} potential clips:")
    for i, clip in enumerate(clips, 1):
        print(f"  {i}. [{clip['start']:.1f}s - {clip['end']:.1f}s] {clip['title']}")

    return clips


def parse_and_validate_clips(result_text: str, duration: float, transcript: dict) -> list:
    """
    Parse LLM response and validate clip timestamps.
    """
    clips = []
    try:
        json_start = result_text.find("{")
        json_end = result_text.rfind("}") + 1
        if json_start != -1 and json_end > json_start:
            json_str = result_text[json_start:json_end]
            result = json.loads(json_str)
            clips = result.get("clips", [])
        else:
            print("[Analyzer] No JSON found in response")
            clips = []
    except json.JSONDecodeError as e:
        print(f"[Analyzer] JSON parse error: {e}")
        clips = []

    # Validate clips
    validated_clips = []
    for clip in clips:
        try:
            start = float(clip.get("start", 0))
            end = float(clip.get("end", start + 30))

            # Sanity check - if timestamps seem like minutes, convert to seconds
            if start < 10 and end < 10 and duration > 60:
                start = start * 60
                end = end * 60
                print(f"[Analyzer] Converted timestamps from minutes to seconds")

            # Ensure valid times within video duration
            start = max(0, min(start, duration - 15))
            end = max(start + 15, min(end, duration))

            # Ensure reasonable clip length (15-60 seconds)
            clip_duration = end - start
            if clip_duration < 15:
                end = min(start + 30, duration)
            elif clip_duration > 60:
                end = start + 45

            validated_clips.append({
                "title": clip.get("title", "Interesting Moment")[:50],
                "start": round(start, 1),
                "end": round(end, 1),
                "duration": round(end - start, 1),
                "reason": clip.get("reason", "Engaging content")[:100]
            })
        except (ValueError, TypeError) as e:
            print(f"[Analyzer] Skipping invalid clip: {e}")
            continue

    # If no valid clips, create smart defaults
    if not validated_clips:
        print("[Analyzer] No valid clips from LLM, creating defaults")
        validated_clips = create_default_clips(transcript)

    # Sort by start time
    validated_clips.sort(key=lambda x: x["start"])

    return validated_clips


def analyze_transcript(transcript: dict, prompt: str) -> list:
    """
    Use local Ollama LLM to analyze transcript only (no vision).
    This is the fallback/simpler method.

    Args:
        transcript: Dict with 'segments' and 'full_text' from transcriber
        prompt: User's prompt describing what clips to find

    Returns:
        List of clip suggestions with start/end times
    """
    duration = transcript.get("duration", 300)

    # Build transcript with timestamps
    timestamped_text = []
    for seg in transcript["segments"]:
        start_sec = seg["start"]
        end_sec = seg["end"]
        timestamped_text.append(f"[{start_sec:.1f}s - {end_sec:.1f}s] {seg['text']}")

    transcript_with_times = "\n".join(timestamped_text)

    full_prompt = f"""You are a video clip extraction assistant. Find the best moments for short viral clips.

VIDEO DURATION: {duration:.1f} seconds total

USER REQUEST: {prompt}

TRANSCRIPT (with timestamps in seconds):
{transcript_with_times}

INSTRUCTIONS:
1. Find 3-5 engaging moments that would make good short clips
2. Each clip should be 15-45 seconds long
3. Use the EXACT timestamps from the transcript
4. The "start" and "end" values must be numbers in SECONDS
5. Make sure clips don't overlap
6. Pick moments with: humor, drama, key insights, emotional peaks, or memorable quotes

RESPOND WITH ONLY THIS JSON FORMAT:
{{"clips": [
  {{"title": "Short catchy title", "start": 45.0, "end": 75.0, "reason": "Brief reason why this is engaging"}},
  {{"title": "Another title", "start": 120.0, "end": 150.0, "reason": "Why this moment stands out"}}
]}}"""

    print(f"[Analyzer] Sending to Ollama ({OLLAMA_MODEL})...")
    print(f"[Analyzer] Video duration: {duration:.1f}s")

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 1024,
            }
        },
        timeout=180
    )

    if response.status_code != 200:
        raise Exception(f"Ollama error: {response.text}")

    result_text = response.json().get("response", "")
    print(f"[Analyzer] Raw response: {result_text[:300]}...")

    # Use shared parsing function
    clips = parse_and_validate_clips(result_text, duration, transcript)

    print(f"[Analyzer] Found {len(clips)} potential clips:")
    for i, clip in enumerate(clips, 1):
        print(f"  {i}. [{clip['start']:.1f}s - {clip['end']:.1f}s] {clip['title']}")

    return clips


def create_default_clips(transcript: dict) -> list:
    """Create default clips based on transcript segments - spread across video."""
    duration = transcript.get("duration", 300)
    segments = transcript.get("segments", [])

    clips = []

    if segments and len(segments) >= 3:
        # Pick segments from beginning, middle, and end
        indices = [
            len(segments) // 6,           # Early
            len(segments) // 2,           # Middle
            len(segments) * 5 // 6,       # Late
        ]

        for i, idx in enumerate(indices):
            if idx < len(segments):
                seg = segments[idx]
                start = max(0, seg.get("start", 0) - 5)  # Start 5s before segment
                end = min(start + 30, duration)
                clips.append({
                    "title": f"Highlight {i + 1}",
                    "start": round(start, 1),
                    "end": round(end, 1),
                    "duration": round(end - start, 1),
                    "reason": "Key moment from the video"
                })
    else:
        # No segments, create clips at intervals
        interval = duration / 4
        for i in range(3):
            start = round(interval * (i + 0.5), 1)
            end = min(start + 30, duration)
            clips.append({
                "title": f"Highlight {i + 1}",
                "start": start,
                "end": round(end, 1),
                "duration": round(end - start, 1),
                "reason": "Selected moment from the video"
            })

    return clips


if __name__ == "__main__":
    # Test with sample data
    sample_transcript = {
        "duration": 342,
        "segments": [
            {"start": 0, "end": 5, "text": "Welcome to this video about Python."},
            {"start": 5, "end": 15, "text": "Today I'll show you an amazing trick that will blow your mind."},
            {"start": 15, "end": 30, "text": "This one simple trick can save you hours of coding time."},
            {"start": 30, "end": 45, "text": "Let me demonstrate with a real example."},
            {"start": 120, "end": 135, "text": "And here's the crazy part - it actually works!"},
            {"start": 280, "end": 300, "text": "If you enjoyed this, smash that like button!"},
        ],
        "full_text": "Welcome to this video about Python. Today I'll show you an amazing trick..."
    }

    clips = analyze_transcript(sample_transcript, "find the most exciting moments")
    print("\nFinal clips:")
    print(json.dumps(clips, indent=2))
