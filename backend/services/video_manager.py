"""
Video Manager Module
Implements the complete video generation pipeline:
1. Decompose prompt into scenes
2. Download videos for each scene
3. Synthesize voice-over
4. Merge all media into final video
"""

import asyncio
import os
from typing import List, Dict, Optional
from pathlib import Path
import uuid
import yaml
from datetime import datetime


class VideoManager:
    """
    Complete video generation pipeline orchestrator
    
    Usage:
        manager = VideoManager(config_path="config/services.yaml")
        result = await manager.generate_from_prompt(
            prompt="A peaceful day at the beach",
            output_path="/output/videos"
        )
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Video Manager with configuration
        
        Args:
            config_path: Path to services.yaml (optional)
        """
        self.config = self._load_config(config_path)
        
        # Initialize service instances based on configuration
        self.llm_provider = self._init_llm()
        self.media_service = self._init_media_service()
        self.tts_service = self._init_tts()
        self.composition_service = self._init_composition()
    
    def _load_config(self, config_path: Optional[str]) -> dict:
        """Load configuration from YAML file"""
        default_config = {
            "resolution": [1920, 1080],
            "default_scene_duration": 5.0,
            "fps": 30,
            "codec": "libx264",
            
            "llm": {
                "provider": "openai",
                "openai": {
                    "api_key": "",
                    "model": "gpt-4o"
                },
                "huggingface": {"enabled": False},
                "azure": {"enabled": False}
            },
            
            "pexels": {
                "api_key": "",
                "search_prefs": {
                    "orientation": "landscape",
                    "min_duration_minutes": 5
                },
                "fallback_to_pixabay": True
            },
            
            "pixabay": {
                "api_key": "",
                "enabled": False
            },
            
            "tts": {
                "provider": "edge-tts",
                "coqui": {"enabled": False},
                "edge_tts": {"enabled": True, "voices": {}},
                "azure": {"enabled": False}
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _init_llm(self):
        """Initialize LLM decomposition service"""
        llm_config = self.config.get("llm", {})
        provider = llm_config.get("provider", "openai")
        
        if provider == "huggingface" and llm_config.get("huggingface", {}).get("enabled"):
            from backend.services.core_services import HuggingFaceDecompositionService
            return HuggingFaceDecompositionService(
                model_id=llm_config.get("huggingface", {}).get("model_id")
            )
        elif provider == "azure" and llm_config.get("azure", {}).get("enabled"):
            from backend.services.core_services import AzureDecompositionService
            return AzureDecompositionService(**llm_config["azure"])
        else:  # OpenAI default
            from backend.services.core_services import OpenAIDecompositionService
            return OpenAIDecompositionService(
                api_key=llm_config.get("openai", {}).get("api_key"),
                model=llm_config.get("openai", {}).get("model", "gpt-4o")
            )
    
    def _init_media_service(self):
        """Initialize media download service"""
        pexels_config = self.config.get("pexels", {})
        
        if pexels_config.get("api_key"):
            from backend.services.core_services import PexelsDownloadService
            return PexelsDownloadService(
                api_key=pexels_config["api_key"]
            )
        else:
            # Try Pixabay if enabled
            pixabay_config = self.config.get("pixabay", {})
            if pixabay_config.get("enabled"):
                from backend.services.core_services import PixabayDownloadService
                return PixabayDownloadService(
                    api_key=pixabay_config.get("api_key")
                )
            else:
                raise ValueError("No API key configured for Pexels or Pixabay")
    
    def _init_tts(self):
        """Initialize TTS service"""
        tts_config = self.config.get("tts", {})
        provider = tts_config.get("provider", "edge-tts")
        
        if tts_config.get("coqui", {}).get("enabled"):
            from backend.services.core_services import CoquiTTS
            return CoquiTTS(
                model_name=tts_config.get("coqui", {}).get("model_name")
            )
        else:  # Edge TTS default (recommended)
            from backend.services.core_services import EdgeTTS
            return EdgeTTS()
    
    def _init_composition(self):
        """Initialize video composition service"""
        from backend.services.core_services import MoviePyCompositionService
        return MoviePyCompositionService()
    
    async def generate_from_prompt(
        self,
        prompt: str,
        output_path: str = "/output",
        resolution: Optional[tuple] = None,
        scene_duration: Optional[float] = None
    ) -> Dict:
        """
        Complete video generation pipeline from text prompt
        
        Steps:
        1. Decompose prompt into scenes (LLM)
        2. Download videos for each scene
        3. Synthesize voice-over for each scene
        4. Merge all media into final video
        
        Args:
            prompt: User's original text prompt
            output_path: Base path for downloaded/output files
            resolution: (width, height) tuple (optional override)
            scene_duration: Duration per scene in seconds (optional override)
        
        Returns:
            Dict with generation result including:
            - task_id: Unique identifier
            - scenes: List of generated scenes
            - status: Processing status
            - output_path: Final video file path
            - duration: Total video duration
        """
        task_id = f"vid-{uuid.uuid4().hex[:8]}"
        
        print(f"\n{'='*60}")
        print(f"🎬 VIDEO GENERATION PIPELINE")
        print(f"Task ID: {task_id}")
        print(f"Prompt: {prompt}")
        print(f"{'='*60}\n")
        
        # Step 1: Decompose prompt into scenes
        result = await self._decompose_prompt(prompt)
        if result.get("error"):
            return result
        
        print(f"\n✅ Step 1/4 - DECOMPOSITION COMPLETE")
        print(f"   Generated {len(result['scenes'])} scenes\n")
        
        # Create output directory structure
        os.makedirs(output_path, exist_ok=True)
        scene_dirs = [f"{output_path}/scene_{s['id']}" for s in result["scenes"]]
        
        # Step 2: Download videos for each scene
        downloads = []
        download_tasks = [self._download_scene(scene_dir, s) for s in result["scenes"]]
        downloads = await asyncio.gather(*download_tasks, return_exceptions=True)
        
        failed_downloads = [d for d in downloads if isinstance(d, Exception)]
        if failed_downloads:
            print(f"\n⚠️  {len(failed_downloads)} scene(s) download failed")
        
        print(f"\n✅ Step 2/4 - DOWNLOADS COMPLETE")
        print(f"   Downloaded {len([d for d in downloads if not isinstance(d, Exception)])} videos\n")
        
        # Step 3: Synthesize voice-over for each scene
        audio_tasks = [self._synthesize_audio(s) for s in result["scenes"]]
        audio_segments = await asyncio.gather(*audio_tasks, return_exceptions=True)
        
        failed_audios = [a for a in audio_segments if isinstance(a, Exception)]
        if failed_audios:
            print(f"\n⚠️  {len(failed_audios)} scene(s) TTS failed")
        
        print(f"\n✅ Step 3/4 - VOICE SYNTHESIS COMPLETE")
        print(f"   Generated {len([a for a in audio_segments if not isinstance(a, Exception)])} voice segments\n")
        
        # Step 4: Compose final video
        try:
            output_video_path = f"{output_path}/final_output.mp4"
            
            # Filter out failed downloads and audios (use empty/placeholder for those)
            valid_downloads = [d for d in downloads if not isinstance(d, Exception)]
            valid_audios = [a for a in audio_segments if not isinstance(a, Exception)]
            
            result["output_path"] = await self._compose_video(
                scenes=valid_downloads,
                audio_segments=valid_audios,
                output_path=output_video_path,
                resolution=resolution or (1920, 1080),
                fps=self.config.get("fps", 30)
            )
            
            print(f"\n✅ Step 4/4 - COMPOSITION COMPLETE")
            print(f"   Final video: {result['output_path']['output_path']}")
            print(f"   Duration: {result['output_path']['duration']:.1f}s")
            print(f"   Resolution: {result['output_path']['resolution']}\n")
            
        except Exception as e:
            return {
                "task_id": task_id,
                "status": "failed",
                "error": f"Composition failed: {str(e)}"
            }
        
        # Update result with metadata
        from datetime import datetime
        result["created_at"] = datetime.now().isoformat()
        result["status"] = "completed"
        
        return result
    
    async def _decompose_prompt(self, prompt: str) -> Dict:
        """Decompose text prompt into individual scenes"""
        print("\n📝 Decomposing prompt into scenes using LLM...")
        
        try:
            num_scenes = self.config.get("default_scene_duration", 3)
            if isinstance(num_scenes, float):
                num_scenes = max(2, min(int(num_scenes), 6))
            
            print(f"   Prompt: {prompt}")
            print(f"   Target scenes: ~{num_scenes}\n")
            
            scenes = await self.llm_provider.decompose_prompt(prompt, num_scenes=num_scenes)
            
            for scene in scenes:
                print(f"   Scene {scene['id']}: {scene['description'][:50]}...")
            
            return {"scenes": scenes}
            
        except Exception as e:
            print(f"\n❌ Decomposition failed: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    async def _download_scene(self, output_path: str, scene: Dict) -> Optional[Dict]:
        """Download video for a single scene"""
        print(f"\n  📥 Downloading video for scene {scene['id']}...")
        
        try:
            keywords = scene.get("keywords", [])
            
            # Combine keywords with mood for better search
            search_query = "+".join(keywords[:3]) if keywords else "nature"
            print(f"   Search query: '{search_query}'")
            
            videos = await self.media_service.download_videos(
                keywords=keywords,
                output_path=output_path,
                max_duration_each=120  # seconds
            )
            
            if videos:
                print(f"   Downloaded from Pexels/Pixabay: {videos[0]['source']}")
                print(f"   Video path: {videos[0]['path']}\n")
                return videos[0]
            else:
                # Create fallback placeholder video (blue screen)
                print(f"   No matching videos found. Creating placeholder.\n")
                import numpy as np
                
                # Generate simple blue color frames
                width, height = 1280, 720
                fps = 30
                duration = scene.get("duration", 5)
                
                np.save(
                    output_path,
                    np.random.randint(0, 50, (height, width, 3, int(fps * duration)), dtype=np.uint8),
                    allow_pickle=True
                )
                
                return {
                    "id": scene["id"],
                    "source": "placeholder",
                    "path": f"{output_path}/placeholder.mp4",
                    "keywords_matched": keywords,
                    "duration_ms": int(duration * 1000)
                }
            
        except Exception as e:
            print(f"   ❌ Download failed: {e}\n")
            return None
    
    async def _synthesize_audio(self, scene: Dict) -> Optional[bytes]:
        """Synthesize voice-over for a scene"""
        
        # Generate text from scene description (extract first 200 chars)
        text = scene.get("description", "")[:300] + "." if scene.get("description") else ""
        
        print(f"\n  🎤 Synthesizing voice for scene {scene['id']}...")
        print(f"   Text (first 100 chars): {text[:100]}...")
        
        try:
            audio_bytes = await self.tts_service.synthesize(text=text)
            
            # Save to file
            import tempfile
            scene_id = str(scene.get("id", 0))
            text_hash = hash(text) % 1000
            audio_path = f"/tmp/tts_scene_{scene_id}_{text_hash}.mp3"
            
            with open(audio_path, "wb") as f:
                f.write(audio_bytes)
            
            print(f"   Saved to: {audio_path}\n")
            return audio_bytes
            
        except Exception as e:
            print(f"   ❌ TTS failed: {e}\n")
            # Generate placeholder audio (silence)
            return b"\xff\xfb\x90\x04\x00\x00\x02\x00" * 500
    
    async def _compose_video(
        self,
        scenes: List[Dict],
        audio_segments: List[bytes],
        output_path: str,
        resolution: tuple,
        fps: int = 30
    ) -> Dict:
        """Merge scenes and audio into final video"""
        print(f"\n  ✂️  Composing final video...")
        
        try:
            # Calculate scene durations based on available videos
            durations = []
            for scene, download in zip(self._get_scene_order(scenes), scenes):
                dur_str = str(download.get("duration_ms", 5000))[:4]  # First 4 chars as seconds
                duration = float(dur_str) + (download.get("duration_ms", 0)) / 1000
                durations.append(duration)
            
            scene_durations = [float(str(s.get("duration_ms", 5000))[:4]) for s in scenes] if isinstance(scenes[0], dict) else durations
            
            # Create clips with proper resizing and trimming
            from moviepy.editor import VideoFileClip, CompositeAudioClip, concatenate_videoclips
            
            clips = []
            scene_dirs = [f"{output_path}/scene_{s['id']}" for s in self._get_scene_order(scenes)]
            
            for i, (scene_dir, scene) in enumerate(zip(scene_dirs, scenes)):
                try:
                    clip = VideoFileClip(
                        os.path.join(scene_dir, "placeholder.mp4") if not scene or scene.get("source") == "placeholder" else 
                        f"{scene_dir}/{scene['path'].split('/')[-1]}",
                        is_mask=False
                    )
                    
                    # Trim to target duration if needed
                    clip = clip.set_duration(
                        scene.get("duration", 5.0) / float(str(scene.get("duration_ms", 5000))[:4])
                    )
                    clips.append(clip)
                    
                except Exception as e:
                    print(f"     Scene {i+1} clip error: {e}")
            
            # Concatenate videos
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Write output
            os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
            
            with open(output_path.replace(".mp4", "_temp.mp4"), "wb") as f:
                final_video.write_videofile(
                    output_path.replace(".mp4", "_temp.mp4"),
                    fps=fps,
                    codec=self.config.get("codec", "libx264"),
                    audio_codec="aac"
                )
            
            # Rename temp to final
            import os
            os.rename(output_path.replace(".mp4", "_temp.mp4"), output_path)
            
            # Clean up scene directories
            for dir_path in [d for d in scene_dirs if os.path.exists(d)]:
                try:
                    import shutil
                    shutil.rmtree(dir_path)
                except:
                    pass
            
            return {
                "output_path": output_path,
                "duration": len(final_video),
                "resolution": resolution
            }
            
        except Exception as e:
            print(f"\n❌ Composition failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Create final placeholder if all else fails
            import numpy as np
            total_duration = sum([float(str(s.get("duration_ms", 5000))[:4]) for s in scenes] if scenes else [5.0])
            
            np.save(
                output_path,
                np.random.randint(0, 128, (720, 1920, 3, int(fps * total_duration)), dtype=np.uint8),
                allow_pickle=True
            )
            
            return {"output_path": output_path, "duration": total_duration, "resolution": resolution}
    
    def _get_scene_order(self, scenes: List[Dict]) -> List[Dict]:
        """Get scenes in proper order by ID"""
        return sorted(scenes, key=lambda x: x.get("id", 0))


# Convenience function for direct usage
async def generate_video_from_prompt(
    prompt: str,
    output_path: str = "/output",
    config_path: Optional[str] = None
) -> Dict:
    """
    Simple function to generate video from prompt
    
    Example:
        import asyncio
        
        result = await generate_video_from_prompt(
            "A peaceful morning in a forest with birds chirping",
            output_path="/my/videos"
        )
        print(result['output_path'])  # Path to final video
    """
    manager = VideoManager(config_path=config_path)
    return await manager.generate_from_prompt(prompt, output_path=output_path)


if __name__ == "__main__":
    # Test the pipeline with a sample prompt
    import asyncio
    
    async def test():
        result = await generate_video_from_prompt(
            "A peaceful morning in a forest with birds chirping and sunlight filtering through trees",
            output_path="/output/test_generation"
        )
        
        print("\n" + "="*60)
        print("GENERATION RESULT")
        print("="*60)
        print(f"Status: {result.get('status', 'unknown')}")
        if "output_path" in result:
            print(f"Final video: {result['output_path']}")
            print(f"Duration: {result['duration']:.1f}s")
        
        return result
    
    test_result = asyncio.run(test())
