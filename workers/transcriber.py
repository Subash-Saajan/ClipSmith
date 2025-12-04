import os
from faster_whisper import WhisperModel
from dotenv import load_dotenv

load_dotenv()

# Model options: tiny, base, small, medium, large-v2, large-v3
# For CPU: "small" is a good balance of speed and accuracy
# For GPU: you can use "medium" or "large-v2"
MODEL_SIZE = "small"

# Try to use CUDA if available, fallback to CPU
# CTranslate2 uses int8 quantization for efficiency
DEVICE = "cuda"  # Will auto-fallback to cpu if cuda unavailable
COMPUTE_TYPE = "int8"  # int8 is fastest, float16 for GPU, float32 for CPU

model = None


def get_model():
    """Lazy load the Whisper model."""
    global model
    if model is None:
        print(f"[Transcriber] Loading faster-whisper {MODEL_SIZE} model...")
        try:
            # Try CUDA first
            model = WhisperModel(MODEL_SIZE, device="cuda", compute_type="float16")
            print(f"[Transcriber] Model loaded on GPU (CUDA)")
        except Exception as e:
            print(f"[Transcriber] CUDA not available ({e}), using CPU")
            model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
            print(f"[Transcriber] Model loaded on CPU (int8 quantization)")
    return model


def transcribe_video(video_path: str) -> dict:
    """
    Transcribe video using faster-whisper (CTranslate2 optimized).
    Returns transcript with word-level timestamps.
    """
    print(f"[Transcriber] Transcribing: {video_path}")

    whisper_model = get_model()

    # Transcribe with word timestamps
    print(f"[Transcriber] Running transcription...")
    segments_gen, info = whisper_model.transcribe(
        video_path,
        word_timestamps=True,
        vad_filter=True,  # Voice activity detection for better accuracy
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    # Convert generator to list and extract segments
    segments = []
    full_text_parts = []

    for seg in segments_gen:
        segments.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip(),
        })
        full_text_parts.append(seg.text.strip())
        print(f"[Transcriber] [{seg.start:.1f}s - {seg.end:.1f}s] {seg.text.strip()[:50]}...")

    # Get duration from last segment
    duration = segments[-1]["end"] if segments else 0

    output = {
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": duration,
        "segments": segments,
        "full_text": " ".join(full_text_parts),
    }

    print(f"[Transcriber] Done - {len(segments)} segments, {duration:.1f}s")
    print(f"[Transcriber] Language: {info.language} ({info.language_probability:.1%} confidence)")

    return output


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) > 1:
        result = transcribe_video(sys.argv[1])
        print(f"\nLanguage: {result['language']} ({result['language_probability']:.1%})")
        print(f"Duration: {result['duration']:.1f}s")
        print(f"Segments: {len(result['segments'])}")
        print(f"\nFirst 5 segments:")
        for seg in result['segments'][:5]:
            print(f"  [{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}")
        print(f"\nFull transcript:\n{result['full_text'][:500]}...")
    else:
        print("Usage: python transcriber.py <video_path>")
