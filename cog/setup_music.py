#!/usr/bin/env python3
"""
Music Streaming Setup Script for Discord Bot
This script helps set up youtube-dl for music streaming functionality.
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies for music streaming"""
    print("🎵 Setting up music streaming functionality...")
    
    # Install required packages
    packages = [
        'yt-dlp',
        'PyNaCl',
        'aiohttp'
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    print("✅ All dependencies installed successfully")
    return True

def main():
    """Main setup function"""
    print("🎵 Setting up music streaming functionality...")
    
    # Install dependencies
    if install_dependencies():
        print("✅ Setup completed successfully")
    else:
        print("❌ Setup failed")

if __name__ == "__main__":
    main()
