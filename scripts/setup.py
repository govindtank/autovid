# AutoVid Setup Script
# Run this script to set up the development environment

#!/usr/bin/env python3
"""
Complete setup script for AutoVid development environment.
Run: python scripts/setup.py
"""

import os
import sys
import shutil

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def check_dependencies():
    """Check if required dependencies are installed"""
    print_section("Step 1: Checking Dependencies")
    
    required = ['requests', 'pyyaml', 'openai', 'sqlalchemy']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✅ {pkg} is installed")
        except ImportError:
            missing.append(pkg)
            print(f"⚠️  {pkg} is NOT installed")
    
    if missing:
        print(f"\nInstalling missing dependencies: {', '.join(missing)}")
        os.system(f"pip install {' '.join(missing)}")

def setup_config():
    """Setup configuration files"""
    print_section("Step 2: Setting Up Configuration Files")
    
    config_dir = "config"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        print(f"✅ Created config directory")
    
    # Create database config if doesn't exist
    db_example = "config/database.example.yaml"
    db_config = "config/database.yaml"
    
    if not os.path.exists(db_config):
        shutil.copy(db_example, db_config)
        print(f"✅ Copied database example to {db_config}")
    else:
        print(f"ℹ️  Database config already exists")
    
    # Create services config if doesn't exist
    services_example = "config/services.example.yaml"
    services_config = "config/services.yaml"
    
    if not os.path.exists(services_config):
        shutil.copy(services_example, services_config)
        print(f"✅ Copied services example to {services_config}")
    else:
        print(f"ℹ️  Services config already exists")

def create_env_example():
    """Create .env.example file"""
    print_section("Step 3: Creating Environment Example")
    
    env_example = "config/.env.example"
    
    if os.path.exists(env_example):
        print(f"✅ {env_example} already exists")
    else:
        # Create placeholder (users need to fill it themselves)
        with open(env_example, 'w') as f:
            f.write("# AutoVid Environment Variables\n")
            f.write("# Copy this file to .env and fill in your values\n\n")
            f.write("# ===========================================\n")
            f.write("# REQUIRED - Get from these sources:\n")
            f.write("# ===========================================\n\n")
            f.write("# OpenAI API for LLM scene decomposition\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n\n")
            f.write("# Pexels API for stock video download (FREE)\n")
            f.write("PEXELS_API_KEY=your_pexels_api_key_here\n\n")
        
        print(f"✅ Created {env_example}")
        print(f"\n⚠️  IMPORTANT: Edit this file with your actual API keys:\n")
        print(f"   1. Get OpenAI API key at: https://platform.openai.com/api-keys\n")
        print(f"   2. Get Pexels API key (FREE) at: https://www.pexels.com/api/\n")
        print(f"   3. Replace the placeholders with your actual keys")

def install_backend_deps():
    """Install backend dependencies"""
    print_section("Step 4: Installing Backend Dependencies")
    
    req_file = "backend/requirements.txt"
    
    if os.path.exists(req_file):
        print(f"Installing from {req_file}...")
        os.system(f"cd backend && pip install -r requirements.txt")
        print(f"✅ Backend dependencies installed")
    else:
        print("⚠️  Requirements file not found, skipping...")

def setup_git():
    """Setup git repository"""
    print_section("Step 5: Setting Up Git")
    
    if os.system("git init") == 0:
        print(f"✅ Initialized git repository")
        
        # Configure git user (optional)
        name = input("\nEnter your GitHub username (optional, press Enter to skip): ").strip()
        if name:
            os.system(f"git config user.name \"{name}\"")
            print(f"✅ Configured git name")
        
        email = input("Enter your email (optional, press Enter to skip): ").strip()
        if email:
            os.system(f"git config user.email \"{email}\"")
            print(f"✅ Configured git email")

def show_next_steps():
    """Show what to do next"""
    print_section("Next Steps")
    
    print("""
🚀 Your AutoVid setup is complete! Here's what to do next:

1. Edit config/services.yaml and add your API keys:
   - OPENAI_API_KEY (for LLM scene decomposition)
   - PEXELS_API_KEY (for video downloads, FREE)

2. Start the backend service:
   python backend/main.py
   
   OR use Docker:
   docker-compose up -d

3. Access the web interface:
   http://localhost:8000 (API docs)
   
4. Generate your first video via:
   - Web UI (if you deployed frontend)
   - Python API calls
   - curl commands (see USAGE.md for examples)

📚 Documentation:
   - Full usage guide: docs/USAGE.md
   - Quick start: README.md
   
🐳 Docker Commands:
   docker-compose up -d      # Start all services
   docker-compose logs -f api # View logs
   docker-compose down       # Stop services

Happy video generating! 🎬
    """)

def main():
    """Main setup function"""
    print_section("🎬 AutoVid Development Environment Setup")
    print("This script will set up your development environment.")
    
    input("\nPress Enter to continue...")
    
    check_dependencies()
    setup_config()
    create_env_example()
    install_backend_deps()
    setup_git()
    show_next_steps()

if __name__ == "__main__":
    main()
