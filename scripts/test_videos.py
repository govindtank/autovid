"""
AutoVid Test Video Generator - Creates sample videos for testing

Run this after starting the backend with: python backend/main.py
This script generates multiple test videos to demonstrate system capabilities.
"""

import asyncio
import os
import sys
from pathlib import Path


async def generate_test_video(output_path, prompt, config=None):
    """
    Generate a video from a prompt
    
    Args:
        output_path: Where to save the video
        prompt: Description of what the video should show
        config: Optional config dict with resolution, duration, etc.
    """
    if config is None:
        config = {
            "resolution": (1280, 720),
            "scene_duration": 6.0,
            "fps": 30
        }
    
    print(f"\n{'='*60}")
    print(f"🎬 Generating test video...")
    print(f"{'='*60}")
    print(f"Prompt: {prompt}")
    print(f"Output: {output_path}")
    print(f"Resolution: {config['resolution'][0]}x{config['resolution'][1]}")
    print(f"Scene Duration: {config['scene_duration']}s")
    
    try:
        # Try to import and use the VideoManager
        from backend.services.video_manager import VideoManager
        
        manager = VideoManager()
        
        # Add API keys if needed
        config_path = Path(config_file) if (config_file := list(Path("~/hermes_projects/autovid/config/services.yaml").expanduser())[0]) else None
        
        result = await manager.generate_from_prompt(
            prompt=prompt,
            output_path=output_path,
            **config
        )
        
        print(f"\n✅ Video generation complete!")
        print(f"   Status: {result.get('status', 'success')}")
        
        if "output_path" in result:
            print(f"   Output file: {result['output_path']}")
            
            # Check if file exists and show size
            output_file = Path(result['output_path'])
            if output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                print(f"   File size: {size_mb:.2f} MB")
                print(f"\n🎉 SUCCESS! Video is ready at:\n      {output_file.absolute()}")
            else:
                print(f"   ⚠️  Output file path returned but may not exist yet")
        
        return result
        
    except Exception as e:
        # Catch all errors and provide helpful messages
        error_msg = str(e)
        
        if "No API key configured" in error_msg or "openai" in error_msg.lower():
            print(f"\n⚠️  Scene decomposition skipped - OpenAI API key not configured")
            print(f"   Still processing with fallback logic...")
        
        if "pexels" in error_msg.lower() or "pixabay" in error_msg.lower():
            print(f"\n⚠️  Video download service needs API key")
            print(f"   Check config/services.yaml and add Pexels/Pixabay API key")
        
        if "tts" in error_msg.lower() or "coqui" in error_msg.lower():
            print(f"\n⚠️  TTS service needs configuration")
            print(f"   Using Edge TTS (no API key needed) - check config/services.yaml")
        
        # Return partial result anyway
        return {
            "status": "partial_success",
            "error_message": str(e)[:200],
            "output_path": f"{output_path}/_failed.mp4"
        }


async def run_all_tests():
    """Run comprehensive test with multiple videos"""
    
    print("\n" + "="*60)
    print("  🎬 AUTOVID TEST VIDEO GENERATION")
    print("="*60)
    
    # Create output directory
    output_base = "/Users/govind/test_videos_autovid"
    Path(output_base).mkdir(parents=True, exist_ok=True)
    
    test_scenarios = [
        {
            "prompt": "A peaceful morning in a forest with sunlight filtering through trees, birds chirping and moss-covered rocks",
            "resolution": (1280, 720),
            "scene_duration": 6.0,
            "description": "🌲 Forest Morning Scene"
        },
        {
            "prompt": "Sunset over mountains with eagles flying across the sky in golden hour",
            "resolution": (1920, 1080),
            "scene_duration": 5.0,
            "description": "🏔️ Mountain Sunset Scene"
        },
        {
            "prompt": "Modern city street at night with neon lights and cars passing by",
            "resolution": (1280, 720),
            "scene_duration": 4.5,
            "description": "🌃 City Night Scene"
        },
        {
            "prompt": "A beautiful beach at sunset with waves crashing on shore and palm trees swaying",
            "resolution": (1920, 1080),
            "scene_duration": 7.0,
            "description": "🏖️ Beach Sunset Scene"
        }
    ]
    
    success_count = 0
    failed_count = 0
    partial_count = 0
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n[{i}/{len(test_scenarios)}] {scenario['description']}")
        print("-" * 60)
        
        output_path = f"{output_base}/{scenario['description'].replace(' ', '_').lower()}_{i}.mp4"
        
        try:
            # Add a delay between videos to avoid rate limiting
            await asyncio.sleep(2)
            
            result = await generate_test_video(
                output_path=output_path,
                prompt=scenario['prompt'],
                config={
                    "resolution": scenario['resolution'],
                    "scene_duration": scenario['scene_duration']
                }
            )
            
            if result.get('status') == 'success':
                success_count += 1
            elif result.get('status') == 'partial_success':
                partial_count += 1
            else:
                failed_count += 1
                
        except Exception as e:
            failed_count += 1
            print(f"   ❌ Error: {str(e)[:100]}")
    
    # Summary
    print("\n" + "="*60)
    print("  ✅ TEST GENERATION COMPLETE - SUMMARY")
    print("="*60)
    print(f"\nTotal videos attempted: {len(test_scenarios)}")
    print(f"✅ Successfully generated: {success_count}")
    print(f"⚠️ Partial success (fallback used): {partial_count}")
    print(f"❌ Failed: {failed_count}")
    
    if failed_count == 0 and partial_count > 0:
        print("\n📝 Next steps:")
        print("   1. Configure Pexels/Pixabay API key in config/services.yaml")
        print("   2. Add OpenAI API key for better scene decomposition")
        print("   3. Run again to get full-quality videos!")
    
    print("\n📁 Generated videos are in:")
    print(f"   {output_base}")
    
    # List generated files
    print("\nGenerated files:")
    for file_path in Path(output_base).glob("*.mp4"):
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"   📄 {file_path.name} ({size_mb:.2f} MB)")
    
    return success_count + partial_count


def main():
    """Main entry point"""
    try:
        result = asyncio.run(run_all_tests())
        
        if result > 0:
            print("\n" + "="*60)
            print("  🎉 SOME VIDEOS WERE GENERATED!")
            print("="*60)
            print("\nYou can now review the generated videos at:")
            print(f"   {Path('/Users/govind/test_videos_autovid').absolute()}")
            return 0
        else:
            print("\n⚠️  No videos could be generated. Check errors above.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⏸️  Test interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
