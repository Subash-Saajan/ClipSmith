import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "./downloads")

# Queue names
CLIP_QUEUE = "clip-processing"
