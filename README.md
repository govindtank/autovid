# AutoVid - AI-Powered Video Generation Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen.svg)]()

AutoVid is an AI-powered video generation platform that transforms text prompts into polished videos. It intelligently decomposes prompts into visual scenes, downloads matching stock footage, synthesizes voice-over narration, and composes everything into a final video.

## Features

- **AI Scene Decomposition** - LLM-powered breakdown of prompts into visual scenes
- **Stock Video Download** - Automatic downloads from Pexels/Pixabay APIs (1080p landscape)
- **Voice Synthesis** - Natural narration using Edge TTS (free, no API key) or Coqui
- **Smart Composition** - MoviePy-based merging with audio synchronization
- **Web Interface** - Modern React/Next.js UI with real-time progress tracking
- **Configurable Output** - Adjustable resolution, timing, and export options

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React 18, Tailwind CSS, TypeScript |
| Backend | FastAPI, Python 3.10+, Uvicorn |
| Database | PostgreSQL (SQLite for dev) |
| Media | MoviePy, FFmpeg |
| Voice | Edge TTS, Coqui TTS |

## Quick Start

### Prerequisites

- Python 3.10+
- FFmpeg
- API keys (see [Configuration](#configuration))

### Option 1: Docker (Recommended)

```bash
# Clone and configure
cp config/services.example.yaml config/services.yaml
# Edit config/services.yaml with your API keys

# Start services
docker-compose up -d

# Access at http://localhost:8000
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
python scripts/setup.py

# Configure API keys
cp config/services.example.yaml config/services.yaml

# Start backend
python backend/main.py

# In another terminal, start frontend
cd frontend && npm install && npm run dev
```

### Option 3: Make Commands

```bash
make setup    # Install dependencies
make dev      # Start in development mode
make prod     # Build and start production
make clean    # Remove generated files
```

## Configuration

Create `config/services.yaml` from the example template:

```yaml
service:
  resolution: [1920, 1080]
  default_scene_duration: 5.0
  fps: 30

llm:
  provider: openai
  openai:
    api_key: "your-openai-key"
    model: gpt-4o

pexels:
  api_key: "your-pexels-key"  # Free at https://www.pexels.com/api/
  fallback_to_pixabay: true

tts:
  provider: edge-tts  # Free, no API key needed
  edge_tts:
    enabled: true
    voice: en-US-JennyNeural
```

### API Keys

| Service | Required | Notes |
|---------|----------|-------|
| OpenAI | Yes* | For scene decomposition |
| Pexels | Yes | Free tier available at pexels.com/api |
| Pixabay | No | Fallback option |
| Edge TTS | No | Completely free |

*HuggingFace can be used as an alternative LLM provider

## API Usage

### REST Endpoint

```bash
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A peaceful morning in a forest with sunlight filtering through trees",
    "output_path": "output/forest",
    "resolution": [1920, 1080],
    "scene_duration": 5.0
  }'
```

### Python API

```python
import asyncio
from backend.services.video_manager import generate_video_from_prompt

async def create_video():
    result = await generate_video_from_prompt(
        prompt="A beautiful sunset over mountains with eagles flying",
        output_path="output/sunset"
    )
    print(f"Video generated: {result['output_path']}")

asyncio.run(create_video())
```

## Project Structure

```
autovid/
├── backend/              # FastAPI backend
│   ├── api/             # API routes
│   ├── models/          # Database models
│   ├── services/        # Core services
│   │   ├── core_services.py    # Service interfaces
│   │   └── video_manager.py    # Pipeline orchestrator
│   └── main.py         # Application entry point
├── frontend/           # Next.js web interface
│   ├── app/           # Pages and components
│   └── package.json   # Dependencies
├── config/            # Configuration files
│   ├── services.example.yaml
│   └── database.example.yaml
├── docker/            # Docker deployment
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/           # Utility scripts
│   ├── setup.py
│   ├── test.py
│   └── init_db.py
├── docs/              # Documentation
│   └── USAGE.md
├── requirements.txt   # Python dependencies
└── README.md
```

## Pipeline Flow

```
User Prompt
    ↓
Scene Decomposition (LLM)
    ↓
Video Download (Pexels/Pixabay)
    ↓
Voice Synthesis (Edge TTS/Coqui)
    ↓
Video Composition (MoviePy)
    ↓
Final Output (MP4)
```

## Testing

```bash
# Run test suite
python scripts/test.py

# Quick health check
curl http://localhost:8000/health
```

## Development

```bash
# Backend runs on port 8000
python backend/main.py

# Frontend runs on port 3000
cd frontend && npm run dev
```

## Troubleshooting

**FFmpeg not found:**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

**No API key configured:**
Edit `config/services.yaml` and add your keys, then restart.

## License

MIT License - See [LICENSE](LICENSE) for details.

---

Built with FastAPI, Next.js, and MoviePy.
