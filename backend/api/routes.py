"""
API Routes for AutoVid Backend
FastAPI endpoints for video generation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
from backend.models.database_models import Project, Scene, VoiceSegment, OutputVideo, TaskLog
from sqlalchemy.orm import Session
from backend.services.video_manager import VideoManager


router = APIRouter(prefix="/api", tags=["video-generation"])


class VideoGenerationRequest(BaseModel):
    """Request model for video generation"""
    prompt: str
    output_path: str = "/output"
    resolution: Optional[tuple[int, int]] = None
    scene_duration: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "A peaceful morning in a forest with birds",
                "output_path": "/my/videos/forest",
                "resolution": [1280, 720]
            }
        }


class GenerationResponse(BaseModel):
    """Response model for generation result"""
    task_id: str
    status: str
    progress: float
    scenes_count: int
    output_path: Optional[str] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "vid-a1b2c3d4",
                "status": "completed",
                "progress": 100.0,
                "scenes_count": 5,
                "output_path": "/output/final_output.mp4",
                "duration": 18.5
            }
        }


@router.post("/generate-video", response_model=GenerationResponse)
async def generate_video_endpoint(request: VideoGenerationRequest):
    """
    Generate video from text prompt
    
    Pipeline:
    1. Decompose prompt into scenes using LLM
    2. Download videos from Pexels/Pixabay for each scene
    3. Synthesize voice-over using TTS (Coqui/Edge TTS)
    4. Merge all media into final video
    
    Args:
        prompt: User's text prompt describing desired video content
        output_path: Base path for downloaded/output files
        resolution: Output video resolution (default: 1920x1080)
        scene_duration: Duration per scene in seconds (optional)
    
    Returns:
        Generation result with task_id, status, and output path
    
    Example:
        curl -X POST "http://localhost:8000/api/generate-video" \
            -H "Content-Type: application/json" \
            -d '{"prompt": "A peaceful morning in a forest"}'
    
    Note: This runs synchronously. For production, use async with Celery worker.
    """
    
    try:
        # Initialize video manager with config
        config_path = "/config/services.yaml" if __name__ == "__main__" else "/hermes_projects/autovid/config/services.yaml"
        
        if not request.resolution and __name__ != "__main__":
            resolution = None
        else:
            resolution = request.resolution
        
        # Generate video using VideoManager
        result = await generate_video_from_prompt(
            prompt=request.prompt,
            output_path=request.output_path,
            resolution=resolution,
            scene_duration=request.scene_duration
        )
        
        # Create task record in database (optional)
        # project = Project(...)  # TODO: Implement full DB integration
        
        return GenerationResponse(
            task_id=result.get("task_id", f"vid-{uuid.uuid4().hex[:8]}"),
            status=result.get("status", "completed"),
            progress=100.0 if result.get("status") == "completed" else 50.0,
            scenes_count=len(result.get("scenes", [])),
            output_path=result.get("output_path"),
            duration=result.get("duration"),
            error=result.get("error")
        )
        
    except Exception as e:
        print(f"Error generating video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Helper Functions (moved from main.py for modularity)
# =============================================================================

async def generate_video_from_prompt(
    prompt: str,
    output_path: str = "/output",
    config_path: Optional[str] = None,
    resolution: Optional[tuple] = None,
    scene_duration: Optional[float] = None
) -> dict:
    """
    Complete video generation pipeline from text prompt
    
    Steps:
    1. Decompose prompt into scenes (LLM-based)
    2. Download videos for each scene (Pexels/Pixabay)
    3. Synthesize voice-over (Coqui/Edge TTS)
    4. Merge all media into final video
    
    Args:
        prompt: User's original text prompt
        output_path: Base path for downloaded/output files
        config_path: Path to services.yaml (optional)
        resolution: (width, height) tuple (optional override)
        scene_duration: Duration per scene in seconds (optional override)
    
    Returns:
        Dict with generation result including task_id, scenes, output_path, duration
    """
    
    # Import VideoManager from services module
    from backend.services.video_manager import VideoManager
    
    manager = VideoManager(config_path=config_path)
    
    print(f"\n{'='*60}")
    print(f"🎬 VIDEO GENERATION PIPELINE")
    print(f"Task ID: vid-{uuid.uuid4().hex[:8]}")
    print(f"Prompt: {prompt}")
    print(f"{'='*60}\n")
    
    # Step 1: Decompose prompt into scenes
    result = await manager._decompose_prompt(prompt)
    if result.get("error"):
        return result
    
    print(f"\n✅ Step 1/4 - DECOMPOSITION COMPLETE")
    print(f"   Generated {len(result['scenes'])} scenes\n")
    
    # Create output directory structure
    os.makedirs(output_path, exist_ok=True)
    scene_dirs = [f"{output_path}/scene_{s['id']}" for s in result["scenes"]]
    
    # Step 2: Download videos for each scene
    download_tasks = [manager._download_scene(scene_dir, s) for s in result["scenes"]]
    downloads = await asyncio.gather(*download_tasks, return_exceptions=True)
    
    failed_downloads = [d for d in downloads if isinstance(d, Exception)]
    if failed_downloads:
        print(f"\n⚠️  {len(failed_downloads)} scene(s) download failed")
    
    print(f"\n✅ Step 2/4 - DOWNLOADS COMPLETE")
    print(f"   Downloaded {len([d for d in downloads if not isinstance(d, Exception)])} videos\n")
    
    # Step 3: Synthesize voice-over for each scene
    audio_tasks = [manager._synthesize_audio(s) for s in result["scenes"]]
    audio_segments = await asyncio.gather(*audio_tasks, return_exceptions=True)
    
    failed_audios = [a for a in audio_segments if isinstance(a, Exception)]
    if failed_audios:
        print(f"\n⚠️  {len(failed_audios)} scene(s) TTS failed")
    
    print(f"\n✅ Step 3/4 - VOICE SYNTHESIS COMPLETE")
    print(f"   Generated {len([a for a in audio_segments if not isinstance(a, Exception)])} voice segments\n")
    
    # Step 4: Compose final video
    try:
        output_video_path = f"{output_path}/final_output.mp4"
        
        valid_downloads = [d for d in downloads if not isinstance(d, Exception)]
        valid_audios = [a for a in audio_segments if not isinstance(a, Exception)]
        
        result["output_path"] = await manager._compose_video(
            scenes=valid_downloads,
            audio_segments=valid_audios,
            output_path=output_video_path,
            resolution=resolution or (1920, 1080),
            fps=30  # default
        )
        
        print(f"\n✅ Step 4/4 - COMPOSITION COMPLETE")
        print(f"   Final video: {result['output_path']['output_path']}")
        print(f"   Duration: {result['output_path']['duration']:.1f}s")
        print(f"   Resolution: {result['output_path']['resolution']}\n")
        
    except Exception as e:
        return {
            "task_id": f"vid-{uuid.uuid4().hex[:8]}",
            "status": "failed",
            "error": f"Composition failed: {str(e)}"
        }
    
    # Update result with metadata
    result["created_at"] = datetime.now().isoformat()
    result["status"] = "completed"
    
    return result


# =============================================================================
# Health Check & Info Endpoints
# =============================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AutoVid API", "version": "1.0.0"}


@router.get("/")
async def root_endpoint():
    """API information endpoint"""
    return {
        "service": "AutoVid API",
        "version": "1.0.0",
        "description": "AI-Powered Video Generation Platform",
        "endpoints": [
            "/api/generate-video - Generate video from prompt (POST)",
            "/api/health - Health check (GET)"
        ]
    }
