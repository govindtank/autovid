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

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Installation (Quick)

```bash
cd ~/hermes_projects/autovid

# Backend setup
python -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt

# Frontend setup
cd frontend/app
npm install && npm run build

# Database
cp config/database.example.yaml config/database.yaml
# Edit with your settings

# Configuration
cp config/services.example.yaml config/services.yaml
# Add API keys for services (Pexels, TTS provider)

# Run
docker-compose up -d
```

## 📁 Project Structure

```
autovid/
├── backend/          # FastAPI service
│   ├── api/          # API routes
│   ├── core/         # Core logic
│   ├── services/     # External service integrations
│   └── models/       # Data models
├── frontend/app/     # React web interface
├── config/           # Configuration files
├── docker/           # Docker & orchestration
├── ci/               # GitHub Actions CI/CD
├── scripts/          # Utility scripts
└── docs/             # Documentation
```

## 🎯 Features (Roadmap)

### ✅ Phase 1 - MVP (Completed)
- [x] Scene decomposition from prompts
- [x] Video download from Pexels/Pixabay
- [x] Voice synthesis with Coqui TTS
- [x] Video merging with audio sync
- [x] Web interface for all operations
- [x] Configurable parameters

### 🔄 Phase 2 - In Progress
- [ ] Thumbnail preview generation
- [ ] Subtitle auto-generation
- [ ] Multiple export formats (MP4/WebM)
- [ ] Batch processing

### 🚀 Phase 3 - Future
- [ ] Cloud storage integration (S3)
- [ ] Real-time streaming output
- [ ] Advanced audio mixing

## 🛠️ Configuration

Edit `config/services.yaml` for service configuration:

```yaml
llm:
  provider: "openai"  # or "huggingface", "azure"
  api_key: "your-api-key"

pexels:
  api_key: "your-pexels-key"

tts:
  provider: "coqui"   # or "edge-tts", "azure"
```

## 📝 License

MIT License - See LICENSE file for details.

---

**Status: PHASE 1 MVP COMPLETE ✅**
**Last Updated: $(date)**
**Builds: 0/4 completed**
