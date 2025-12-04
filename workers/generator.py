"""
Video Generator using Stable Video Diffusion (SVD)
Generates new videos based on style reference + prompt modifications
"""
import os
import gc
import torch
import cv2
import numpy as np
from PIL import Image
from typing import List, Optional
from config import DOWNLOAD_DIR

# Output directory for generated videos
GENERATED_DIR = os.path.join(DOWNLOAD_DIR, "generated")

# Device setup
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32

# Global model (lazy loaded)
_svd_pipeline = None


def clear_gpu_memory():
    """Clear GPU memory cache."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def get_svd_pipeline():
    """Lazy load SVD pipeline with memory optimizations for 6GB VRAM."""
    global _svd_pipeline

    if _svd_pipeline is None:
        print("[Generator] Loading SVD pipeline (this may take a while on first run)...")

        from diffusers import StableVideoDiffusionPipeline

        # Load with memory optimizations
        _svd_pipeline = StableVideoDiffusionPipeline.from_pretrained(
            "stabilityai/stable-video-diffusion-img2vid",
            torch_dtype=DTYPE,
            variant="fp16" if DTYPE == torch.float16 else None,
        )

        # Memory optimizations for 6GB VRAM
        _svd_pipeline.enable_model_cpu_offload()  # Moves models to CPU when not in use

        # Try to enable VAE optimizations if available
        if hasattr(_svd_pipeline, 'enable_vae_slicing'):
            _svd_pipeline.enable_vae_slicing()
        if hasattr(_svd_pipeline, 'enable_vae_tiling'):
            _svd_pipeline.enable_vae_tiling()

        print(f"[Generator] SVD loaded on {DEVICE}")

    return _svd_pipeline


def extract_frames(video_path: str, num_frames: int = 14, target_size: tuple = (576, 320)) -> List[Image.Image]:
    """
    Extract frames from video for analysis/reference.
    Returns list of PIL Images.
    """
    print(f"[Generator] Extracting {num_frames} frames from {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0

    print(f"[Generator] Video: {total_frames} frames, {fps:.1f} fps, {duration:.1f}s")

    # Calculate frame indices to extract (evenly spaced)
    frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)

    frames = []
    for idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert to PIL and resize
            pil_frame = Image.fromarray(frame_rgb)
            pil_frame = pil_frame.resize(target_size, Image.Resampling.LANCZOS)
            frames.append(pil_frame)

    cap.release()
    print(f"[Generator] Extracted {len(frames)} frames")
    return frames


def get_key_frame(video_path: str, frame_idx: int = 0, target_size: tuple = (576, 320)) -> Image.Image:
    """
    Extract a single key frame from video.
    frame_idx: 0 = first frame, -1 = middle frame, -2 = last frame
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if frame_idx == -1:
        # Middle frame
        actual_idx = total_frames // 2
    elif frame_idx == -2:
        # Last frame
        actual_idx = total_frames - 1
    else:
        actual_idx = min(frame_idx, total_frames - 1)

    cap.set(cv2.CAP_PROP_POS_FRAMES, actual_idx)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise ValueError(f"Failed to read frame {actual_idx}")

    # Convert BGR to RGB, then to PIL
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_frame = Image.fromarray(frame_rgb)
    pil_frame = pil_frame.resize(target_size, Image.Resampling.LANCZOS)

    return pil_frame


def frames_to_video(frames: List[np.ndarray], output_path: str, fps: float = 7.0):
    """
    Convert list of frames to video file using OpenCV.
    """
    if not frames:
        raise ValueError("No frames to convert")

    # Get dimensions from first frame
    height, width = frames[0].shape[:2]

    # Use mp4v codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for frame in frames:
        # Convert RGB to BGR for OpenCV
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        else:
            frame_bgr = frame
        out.write(frame_bgr)

    out.release()
    print(f"[Generator] Saved video: {output_path}")


def generate_video(
    reference_video_path: str,
    job_id: str,
    prompt: str = "",
    num_frames: int = 14,  # SVD default
    fps: float = 7.0,
    motion_bucket_id: int = 127,  # Motion amount (0-255, higher = more motion)
    noise_aug_strength: float = 0.02,
    decode_chunk_size: int = 4,  # Lower = less VRAM, slower
    seed: Optional[int] = None,
) -> dict:
    """
    Generate a new video based on reference video style.

    Args:
        reference_video_path: Path to the style reference video
        job_id: Job ID for naming output
        prompt: Text prompt for modifications (used for logging, SVD is image-only)
        num_frames: Number of frames to generate (14 = ~2 seconds at 7fps)
        fps: Output FPS
        motion_bucket_id: Motion intensity (0-255)
        noise_aug_strength: Noise augmentation strength
        decode_chunk_size: VAE decode chunk size (lower = less memory)
        seed: Random seed for reproducibility

    Returns:
        Dict with output path and metadata
    """
    os.makedirs(GENERATED_DIR, exist_ok=True)

    print(f"[Generator] Starting generation for job {job_id}")
    print(f"[Generator] Reference: {reference_video_path}")
    print(f"[Generator] Prompt: {prompt or '(none)'}")

    # Extract key frame from reference video (middle frame)
    key_frame = get_key_frame(reference_video_path, frame_idx=-1)
    print(f"[Generator] Key frame size: {key_frame.size}")

    # Clear memory before loading model
    clear_gpu_memory()

    # Get pipeline
    pipe = get_svd_pipeline()

    # Set seed if provided
    generator = torch.Generator(device=DEVICE)
    if seed is not None:
        generator.manual_seed(seed)
    else:
        generator.manual_seed(torch.randint(0, 2**32, (1,)).item())

    print(f"[Generator] Generating {num_frames} frames...")

    # Generate frames
    # Note: SVD is image-to-video, prompt is not directly used
    # The reference frame defines the style/content
    with torch.inference_mode():
        output = pipe(
            image=key_frame,
            num_frames=num_frames,
            fps=int(fps),
            motion_bucket_id=motion_bucket_id,
            noise_aug_strength=noise_aug_strength,
            decode_chunk_size=decode_chunk_size,
            generator=generator,
        )

    # Convert frames to numpy arrays
    frames = output.frames[0]  # List of PIL Images
    np_frames = [np.array(f) for f in frames]

    # Save to video
    output_filename = f"{job_id}_generated.mp4"
    output_path = os.path.join(GENERATED_DIR, output_filename)
    frames_to_video(np_frames, output_path, fps=fps)

    # Clear memory after generation
    clear_gpu_memory()

    # Get file size
    file_size = os.path.getsize(output_path)
    duration = num_frames / fps

    print(f"[Generator] Generated: {output_filename} ({file_size / 1024 / 1024:.1f} MB, {duration:.1f}s)")

    return {
        "file_path": output_path,
        "filename": output_filename,
        "duration": duration,
        "num_frames": num_frames,
        "fps": fps,
        "size_bytes": file_size,
        "prompt": prompt,
    }


def generate_multiple_clips(
    reference_video_path: str,
    job_id: str,
    prompt: str = "",
    num_clips: int = 3,
    frames_per_clip: int = 14,
    fps: float = 7.0,
) -> List[dict]:
    """
    Generate multiple short clips from a reference video.
    Each clip uses a different key frame from the reference.
    """
    results = []

    # Extract multiple key frames from different points in the video
    cap = cv2.VideoCapture(reference_video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    # Calculate frame positions for each clip
    frame_positions = np.linspace(0, total_frames - 1, num_clips + 2, dtype=int)[1:-1]

    for i, frame_pos in enumerate(frame_positions, 1):
        print(f"\n[Generator] Generating clip {i}/{num_clips}...")

        try:
            # Temporarily modify to use specific frame
            key_frame = get_key_frame(reference_video_path, frame_idx=int(frame_pos))

            # Clear memory
            clear_gpu_memory()

            # Get pipeline
            pipe = get_svd_pipeline()

            generator = torch.Generator(device=DEVICE)
            generator.manual_seed(torch.randint(0, 2**32, (1,)).item())

            with torch.inference_mode():
                output = pipe(
                    image=key_frame,
                    num_frames=frames_per_clip,
                    fps=int(fps),
                    motion_bucket_id=127,
                    noise_aug_strength=0.02,
                    decode_chunk_size=4,
                    generator=generator,
                )

            # Save video
            frames = output.frames[0]
            np_frames = [np.array(f) for f in frames]

            output_filename = f"{job_id}_generated_{i}.mp4"
            output_path = os.path.join(GENERATED_DIR, output_filename)
            frames_to_video(np_frames, output_path, fps=fps)

            file_size = os.path.getsize(output_path)
            duration = frames_per_clip / fps

            results.append({
                "file_path": output_path,
                "filename": output_filename,
                "duration": duration,
                "num_frames": frames_per_clip,
                "fps": fps,
                "size_bytes": file_size,
                "clip_index": i,
            })

            clear_gpu_memory()

        except Exception as e:
            print(f"[Generator] Failed to generate clip {i}: {e}")
            continue

    return results


if __name__ == "__main__":
    # Test generation
    import sys

    if len(sys.argv) > 1:
        test_video = sys.argv[1]
        print(f"Testing with video: {test_video}")

        result = generate_video(
            reference_video_path=test_video,
            job_id="test",
            prompt="test generation",
            num_frames=14,
        )
        print(f"\nResult: {result}")
    else:
        print("Usage: python generator.py <video_path>")
        print("\nChecking GPU availability...")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
