# 🎬 AutoVid - AI-Powered Video Generation Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-active-green.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📋 Project Overview

AutoVid is an AI-powered video generation platform that:
- ✅ Accepts text prompts from users
- ✅ Decomposes prompts into multiple visual scenes using LLM
- ✅ Downloads matching free/open-source videos from Pexels/Pixabay
- ✅ Synthesizes voice-over using TTS models (Coqui/Edge TTS)
- ✅ Merges all media into a single video with synchronized audio
- ✅ Fully customizable pipeline (resolution, timing, file sizes)
- ✅ Cross-platform web interface (runs on any OS/browser)

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   FastAPI Backend │────▶│    Services     │
│   (React/TS)    │     │                  │     │  (Media/TTS)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │
                              ▼
                      ┌──────────────────┐
                      │ PostgreSQL +    │
                      │ Redis Cache      │
                      └──────────────────┘
```

## 🚀 Quick Start (Docker)

### Prerequisites
- Docker & Docker Compose installed

### Installation

```bash
cd ~/hermes_projects/autovid

# Copy configuration templates
cp config/database.example.yaml config/database.yaml
cp config/services.example.yaml config/services.yaml

# Edit services.yaml and add your API keys
nano config/services.yaml  # or use your preferred editor
```

**Required API Keys:**
- OpenAI API key (for LLM): Get at https://platform.openai.com/api-keys
- Pexels API key (free): Get at https://www.pexels.com/api/

### Run with Docker

```bash
docker-compose up -d

# Check logs
docker-compose logs -f api

# Access web interface
open http://localhost:3000  # For Next.js frontend separately
```

**OR run backend only:**

```bash
make setup
make dev
```

Then visit `http://localhost:8000` for API docs and `http://localhost:3000` for web UI.

## 🎯 Features (Roadmap)

### ✅ Phase 1 - MVP (Completed)
- [x] **Scene Decomposition**: Break prompts into detailed scenes using LLM
- [x] **Video Downloader**: Download from Pexels/Pixabay APIs
- [x] **Voice Synthesis**: Coqui TTS or Edge TTS (free, no API key)
- [x] **Video Merging**: MoviePy-based composition engine
- [x] **Web Interface**: Modern React + Tailwind UI
- [x] **Configuration System**: Customizable settings per service
- [x] **Async Pipeline**: Concurrent downloads and TTS processing

### 🔄 Phase 2 - In Progress
- [ ] Thumbnail preview generation
- [ ] Subtitle auto-generation from voice text
- [ ] Multiple export formats (MP4/WebM)
- [ ] Batch processing for multiple prompts

### 🚀 Phase 3 - Future
- [ ] Cloud storage integration (S3-compatible)
- [ ] Real-time streaming output
- [ ] Advanced audio mixing/volume balancing
- [ ] Scene-specific music/background audio

## 🛠️ Configuration

Edit `config/services.yaml`:

```yaml
# Resolution and duration settings
service:
  resolution: [1920, 1080]  # Width × Height
  fps: 30                    # Frames per second
  codec: libx264            # Options: libx264, h264_qsv (NVIDIA)

# LLM for scene decomposition
llm:
  provider: openai
  openai:
    api_key: "your-openai-key"
    model: gpt-4o

# Media download service
pexels:
  api_key: "your-pexels-key"  # Get free key at pexels.com/api
  fallback_to_pixabay: true   # Auto-fallback if rate limited

tts:
  provider: edge-tts           # Recommended: free, no API key needed
  voices:
    en-US-JennyNeural: friendly female (default)
    en-GB-SoniaNeural: British English
```

## 📁 Project Structure

```
autovid/
├── backend/          # FastAPI service
│   ├── api/          # API routes and endpoints
│   ├── core/         # Core logic modules
│   ├── models/       # SQLAlchemy ORM models
│   ├── services/     # External service integrations
│   │   └── video_manager.py  # Main pipeline orchestrator
│   └── main.py       # FastAPI app entry point
├── frontend/app/     # React web interface (Next.js)
├── config/           # YAML configuration files
├── docker/           # Docker & orchestration
├── ci/               # GitHub Actions CI/CD
└── scripts/          # Utility scripts (db init, etc.)
```

## 🧪 Usage Examples

### Python API Usage

```python
import asyncio
from backend.services.video_manager import VideoManager

async def main():
    manager = VideoManager()  # Uses default config
    result = await manager.generate_from_prompt(
        prompt="A peaceful morning in a forest with birds chirping",
        output_path="/output/forest_video"
    )
    
    print(f"Video generated at: {result['output_path']}")
    print(f"Duration: {result['duration']:.1f}s")

asyncio.run(main())
```

### Curl API Call

```bash
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over mountains",
    "output_path": "/output/sunset",
    "resolution": [1920, 1080]
  }'
```

### Web UI Usage

1. Navigate to `http://localhost:3000`
2. Enter your video description prompt
3. Configure optional settings (resolution, output path)
4. Click "🚀 Generate Video"
5. Wait for processing (1-2 minutes)
6. Download the final video

## 📝 API Documentation

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate-video` | POST | Generate video from prompt |
| `/api/health` | GET | Health check endpoint |
| `/` | GET | API info and documentation |

**Generate Video Request:**
```json
{
  "prompt": "A beautiful sunset over mountains with eagles flying",
  "output_path": "/output/sunset",
  "resolution": [1920, 1080],
  "scene_duration": 5.0
}
```

**Response:**
```json
{
  "task_id": "vid-abc123def4",
  "status": "completed",
  "progress": 100.0,
  "scenes_count": 4,
  "output_path": "/output/sunset/final_output.mp4",
  "duration": 18.5,
  "created_at": "2026-05-03T15:30:00"
}
```

## 🐳 Docker Deployment

### Start with Docker Compose

```bash
docker-compose up -d
```

This starts both API and Redis backend services. For the frontend, build separately:

```bash
cd frontend/app
npm install
npm run build
npm run start
```

### Production Docker Build

```bash
make prod
```

## 🔄 Git Workflow (GitHub Integration)

```bash
# Initialize git repository
git init

# Configure credentials (if not already done)
git config user.name "Your Name"
git config user.email "your@email.com"

# Commit and push to GitHub
git add .
git commit -m "feat: initial video generation pipeline"
git push origin main
```

## 🛠️ Development Commands

```bash
make setup        # Install dependencies
make dev          # Start backend in watch mode
make test         # Run tests (TODO)
make lint         # Lint Python code
make clean        # Remove generated files
```

## 📚 Tech Stack

### Backend
- **Python 3.11+**: Main language
- **FastAPI**: Async API framework
- **SQLAlchemy**: ORM for database operations
- **Celery + Redis**: Task queue (for production)
- **MoviePy**: Video composition library

### Services
- **OpenAI/HuggingFace**: LLM for scene decomposition
- **Pexels/Pixabay APIs**: Stock video download
- **Edge TTS/Coqui**: Text-to-speech synthesis
- **MoviePy**: Video editing and merging

### Frontend
- **React 18**: UI framework
- **Next.js 14**: React metapackage
- **Tailwind CSS**: Utility-first styling

## 🔐 Security Considerations

1. **API Key Management**: Store in environment variables, not config files
2. **CORS**: Configure allowed origins in production
3. **Rate Limiting**: Implement for Pexels API calls
4. **Input Validation**: All user inputs sanitized before processing
5. **File Path Safety**: Use `os.path` and avoid path traversal

## 📝 License

MIT License - See LICENSE file for details.

---

**Status: PHASE 1 MVP COMPLETE ✅**
**Builds: 1/4 completed** (Backend + Frontend ready)
**GitHub**: https://github.com/govindtank/autovid
