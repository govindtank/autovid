# AutoVid Usage Guide

## 📖 Complete User Documentation

This guide explains how to use all features of AutoVid for generating AI-powered videos from text prompts.

---

## 🎯 Quick Start (5 minutes)

### 1. Setup Configuration

```bash
cd ~/hermes_projects/autovid

# Copy configuration templates
cp config/database.example.yaml config/database.yaml
cp config/services.example.yaml config/services.yaml
cp config/.env.example .env

# Edit .env and add your API keys:
nano .env
# Fill in OPENAI_API_KEY and PEXELS_API_KEY
```

### 2. Start the Service

```bash
make dev
# OR
docker-compose up -d
```

### 3. Generate Your First Video

**Via Web UI:**
1. Open `http://localhost:8000` (API docs) or your frontend port
2. Enter prompt: `"A peaceful morning in a forest with birds chirping"`
3. Click "🚀 Generate Video"
4. Wait 1-2 minutes for processing
5. Download the final video!

**Via Python:**
```python
from backend.services.video_manager import generate_video_from_prompt
import asyncio

async def main():
    result = await generate_video_from_prompt(
        prompt="A beautiful sunset over mountains with eagles flying",
        output_path="/output/my_first_video"
    )
    print(f"Video saved to: {result['output_path']}")
    
asyncio.run(main())
```

---

## 🎬 Advanced Features

### 1. Custom Resolution & Duration

Edit `config/services.yaml`:

```yaml
service:
  resolution: [1920, 1080]  # Full HD
  default_scene_duration: 5.0  # Seconds per scene
  fps: 30  # Frames per second
```

### 2. Alternative LLM Providers

#### HuggingFace (local/edge GPU)

```yaml
llm:
  provider: huggingface
  huggingface:
    enabled: true
    model_id: microsoft/Phi-3-mini-4k-instruct
    api_token: hf-your-token-here
```

#### Azure OpenAI

```yaml
llm:
  provider: azure
  azure:
    enabled: true
    endpoint: https://your-resource.azure.com
    key: your-key
    model: gpt-4o
```

### 3. Voice Synthesis Options

#### Edge TTS (Recommended - Free, High Quality)

Default configuration uses Edge TTS automatically. Available voices:

| Voice ID | Language | Description |
|----------|----------|-------------|
| `en-US-JennyNeural` | English (US) | Friendly female (default) |
| `en-US-GuyNeural` | English (US) | Friendly male |
| `en-GB-SoniaNeural` | British English | Formal British |
| `es-ES-ElviraNeural` | Spanish | European Spanish |

#### Coqui TTS (Open Source, Local)

```yaml
tts:
  provider: coqui
  coqui:
    enabled: true
    model_name: tts_models/en/ljspeech/tacotron2-DDC
```

---

## 🔧 API Reference

### POST /api/generate-video

Generate a complete video from text prompt.

**Request:**
```json
{
  "prompt": "A beautiful sunset over mountains",
  "output_path": "/output/my-video",
  "resolution": [1920, 1080],
  "scene_duration": 5.0
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt` | string | ✅ Yes | Your text prompt describing desired video content |
| `output_path` | string | ⚠️ Optional | Base directory for output files (default: `/output`) |
| `resolution` | array | ❌ No | [width, height] in pixels (default: 1920×1080) |
| `scene_duration` | float | ❌ No | Seconds per scene (default: 5.0) |

**Response:**
```json
{
  "task_id": "vid-a1b2c3d4e5f6",
  "status": "completed",
  "progress": 100.0,
  "scenes_count": 4,
  "output_path": "/output/my-video/final_output.mp4",
  "duration": 18.5,
  "created_at": "2026-05-03T15:30:00"
}
```

---

## 🎨 Prompt Engineering Tips

### Good Prompts ✅

```
"A peaceful morning in a forest with sunlight filtering through trees"

"Waves crashing on a sandy beach during golden hour sunset"

"A busy street scene in Tokyo at night with neon lights and pedestrians"

"A chef cooking in a modern kitchen, sizzling vegetables in a pan"
```

### Bad Prompts ❌

```
"Make a video about life"  # Too vague
"A happy day"              # No visual description
"Random stuff"             # No specific content
```

### Best Practices:

1. **Be descriptive**: Describe visual elements, lighting, mood
2. **Include action**: "waves crashing", "chef cooking", "birds flying"
3. **Specify setting**: "morning forest", "busy Tokyo street", "modern kitchen"
4. **Set atmosphere**: "sunset golden hour", "peaceful", "energetic"

### Examples by Category:

#### Nature Scenes
```
"Aerial view of green mountains with lakes reflecting the sky, mist rolling over valleys"
"Waves crashing on rocky cliffs during stormy weather, dark clouds overhead"
"Serpentine river winding through forest, sunlight piercing through canopy"
```

#### Urban Life
```
"Busy subway station platform with commuters checking phones, fluorescent lights"
"Construction site with workers lifting steel beams against blue sky"
"Metro train arriving at terminal station, passengers waiting on platform"
```

#### Wildlife
```
"Polar bear walking across ice floes in arctic landscape, breathing fog"
"Lion pride resting on grassland savanna during golden hour sunset"
"Bald eagle soaring over mountain lake with reflection of snowy peaks"
```

---

## 🔍 Understanding the Pipeline

When you submit a prompt, AutoVid performs these steps:

### Step 1: Scene Decomposition (LLM)

```
Input Prompt: "Peaceful morning in forest with birds"
↓
LLM Decompiles into:
[
  {"id": 1, "description": "Sunlight filtering through tree canopy", "duration": 5},
  {"id": 2, "description": "Birds flying overhead in blue sky", "duration": 4},
  {"id": 3, "description": "Forest floor with dappled light and moss", "duration": 6}
]
↓
Extracted keywords: ["forest", "sunlight", "birds", "canopy"]
```

### Step 2: Media Download (Pexels/Pixabay)

```
For each scene:
  Search Pexels with keywords: "forest sunlight birds"
  Download best matching video (1920×1080, landscape)
  Fallback to Pixabay if rate-limited
```

### Step 3: Voice Synthesis (Edge TTS)

```
For each scene description:
  Text extraction: "Sunlight filtering through tree canopy..."
  Select voice: JennyNeural (friendly female, default)
  Generate audio: /tmp/tts_scene_1.mp3 (approx. 5s duration)
```

### Step 4: Video Composition (MoviePy)

```
Combine all scenes in order:
  Scene 1 video + Scene 1 audio → Trim to 5s
  Scene 2 video + Scene 2 audio → Trim to 4s
  Scene 3 video + Scene 3 audio → Trim to 6s
↓
Final output: /output/final_output.mp4 (15 seconds total)
```

---

## 🚀 Production Deployment

### Docker Compose Production Setup

```bash
# Copy config and environment
cp config/services.example.yaml config/services.yaml
cp config/.env.example .env

# Edit config files with production values
nano config/services.yaml
nano .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Environment Variables for Production

Required in `.env`:

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
PEXELS_API_KEY=your-pexels-api-key-here
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## 🐛 Troubleshooting

### Error: "No API key configured for Pexels or Pixabay"

**Solution:** Add Pexels API key to `.env` and restart.

### Error: "Decomposition failed: Connection error"

**Causes:**
- OpenAI/HuggingFace API not accessible
- Network blocking (check proxy settings)
- API quota exceeded

**Solutions:**
1. Verify internet connectivity
2. Check if API key is valid: `curl https://api.openai.com/v1/models`
3. Switch to local model (HuggingFace) or alternative provider

### Error: "Composition failed: Missing FFmpeg"

**Solution:** Install FFmpeg:

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Docker
docker-compose up -d  # Rebuilds with ffmpeg
```

### Low Quality Output Videos

**Causes:**
- Low resolution in config
- Failed downloads (using placeholders)
- Compression artifacts

**Solutions:**
1. Check `service.resolution` in `config/services.yaml`
2. Verify Pexels API key is valid and has quota
3. Increase download retry attempts in code

---

## 📊 Monitoring & Debugging

### View Service Logs

```bash
docker-compose logs -f api     # Backend API logs
docker-compose logs -f redis   # Redis logs
```

### Test API Health

```bash
curl http://localhost:8000/health
# Returns: {"status": "healthy", ...}
```

### Test Generation Pipeline

```bash
curl -X POST http://localhost:8000/api/generate-video \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test video scene"}'
```

---

## 🔐 Security Best Practices

1. **Never commit API keys**: Store in `.env`, add to `.gitignore`
2. **Use environment variables**: Reference with `${VARIABLE_NAME}` in configs
3. **Set proper permissions**: `chmod 600 .env`
4. **Rate limit API calls**: Implement in production
5. **Sanitize file paths**: Use `os.path` and avoid path traversal

---

## 📈 Performance Tips

1. **Batch requests**: Generate multiple videos in parallel (with rate limiting)
2. **Cache results**: Store generated videos for reuse
3. **Use Redis**: For task queue scaling
4. **Optimize downloads**: Only download needed resolutions
5. **GPU acceleration**: Use CUDA-capable GPU for faster processing

---

## 📚 Next Steps

**Ready to build Phase 2 features?**

- Add subtitle generation from voice text
- Implement thumbnail preview service
- Create batch processing API endpoint
- Add cloud storage integration (AWS S3, Azure Blob)

**Want to contribute?**
1. Fork the repository on GitHub
2. Create feature branch: `git checkout -b feat/my-feature`
3. Make changes and commit
4. Push and create pull request

---

**Questions? Issues? Contributing?**  
👉 https://github.com/govindtank/autovid/issues
