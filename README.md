# ClipSmith

AI-powered video intelligence platform that automates viral content extraction from long-form YouTube videos.

## Features

- **Smart Clipping**: Extract the best moments from YouTube videos using AI analysis
- **Speech-to-Text**: Automatic transcription with faster-whisper (GPU accelerated)
- **AI Analysis**: LLaMA 3.2 powered content analysis for viral moment detection
- **Real-time Progress**: Live progress tracking with step-by-step status updates
- **Job Queue**: Distributed job processing with Redis + BullMQ

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React, Tailwind CSS, shadcn/ui |
| Backend | NestJS, TypeScript, Prisma ORM |
| Database | PostgreSQL (Supabase) |
| Queue | Redis (Upstash) + BullMQ |
| Workers | Python, faster-whisper, Ollama |
| Video | yt-dlp, FFmpeg |

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│    Redis    │
│  (Next.js)  │     │  (NestJS)   │     │   (Queue)   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  PostgreSQL │     │   Python    │
                    │  (Supabase) │     │   Worker    │
                    └─────────────┘     └─────────────┘
```

## Prerequisites

- Node.js 18+
- Python 3.10+
- FFmpeg
- Ollama with llama3.2 model
- PostgreSQL database (Supabase)
- Redis instance (Upstash)
- NVIDIA GPU (recommended for transcription)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Subash-Saajan/ClipSmith.git
cd ClipSmith
```

### 2. Backend Setup

```bash
cd backend
npm install

# Create .env file
cat > .env << 'ENVEOF'
DATABASE_URL="postgresql://user:pass@host:5432/db"
REDIS_URL="rediss://default:xxx@xxx.upstash.io:6379"
ENVEOF

# Generate Prisma client and push schema
npx prisma generate
npx prisma db push

# Start backend
npm run start:dev
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Worker Setup

```bash
cd workers

# Create .env file
cat > .env << 'ENVEOF'
DATABASE_URL="postgresql://user:pass@host:5432/db"
REDIS_URL="rediss://default:xxx@xxx.upstash.io:6379"
ENVEOF

# Install dependencies
pip install -r requirements.txt

# Start Ollama (in separate terminal)
ollama run llama3.2

# Start worker
python -u worker.py
```

## Usage

1. Open http://localhost:3002 in your browser
2. Paste a YouTube URL
3. Optionally add a prompt (e.g., "Find the funniest moments")
4. Click "Clip" to extract viral moments
5. Watch the progress in real-time

## Pipeline Steps

1. **Download** - Fetch video from YouTube using yt-dlp
2. **Transcribe** - Convert audio to text with faster-whisper
3. **Analyze** - AI identifies viral moments using LLaMA 3.2
4. **Clip** - Extract segments with FFmpeg (lossless)

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string (with SSL) |

## Hardware Requirements

- **Minimum**: 8GB RAM, 4-core CPU
- **Recommended**: 16GB RAM, NVIDIA GPU (6GB+ VRAM)

GPU is used for:
- faster-whisper transcription (CUDA)
- Ollama LLM inference

## License

MIT

## Author

Built by [Subash](https://github.com/Subash-Saajan)
