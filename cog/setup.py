#!/usr/bin/env python3
"""
Setup script for the Discord bot
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
        if 'DISCORD_TOKEN=' not in content:
            print("❌ DISCORD_TOKEN not found in .env")
            return False
        if 'CLIENT_ID=' not in content:
            print("❌ CLIENT_ID not found in .env")
            return False
    
    print("✅ .env file configured correctly!")
    return True

def main():
    """Main setup function"""
    print("🤖 Discord Bot Setup")
    print("=" * 30)
    
    # Install dependencies
    install_requirements()
    
    # Check environment
    if check_env_file():
        print("\n✅ Setup complete! You can now run:")
        print("   python bot.py")
        print("\n📋 To invite your bot, use:")
        print("   https://discord.com/oauth2/authorize?client_id=1399824318644621402&permissions=8&scope=bot%20applications.commands")
    else:
        print("\n❌ Please check your .env file configuration")

if __name__ == "__main__":
    main()
