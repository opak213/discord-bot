#!/usr/bin/env python3
"""
One-command script to start both Discord bot (enhanced_bot.py) and web server
"""

import os
import sys
import subprocess
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = {
        'DISCORD_TOKEN': DISCORD_TOKEN,
        'DISCORD_CLIENT_ID': DISCORD_CLIENT_ID,
        'DISCORD_CLIENT_SECRET': DISCORD_CLIENT_SECRET
    }
    
    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file")
        print("\nRequired Discord OAuth variables:")
        print("  DISCORD_CLIENT_ID: Your Discord application's client ID")
        print("  DISCORD_CLIENT_SECRET: Your Discord application's client secret")
        print("  DISCORD_TOKEN: Your Discord bot token")
        return False
    return True

def start_discord_bot():
    """Start the Discord bot using enhanced_bot.py"""
    print("🤖 Starting Discord bot...")
    try:
        # Run the enhanced bot directly
        import subprocess
        subprocess.run([sys.executable, 'enhanced_bot.py'])
    except Exception as e:
        print(f"❌ Error starting Discord bot: {e}")

def start_web_server():
    """Start the Flask web server"""
    print("🌐 Starting web server...")
    try:
        # Import and run the web server
        from web_server import app
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except Exception as e:
        print(f"❌ Error starting web server: {e}")

def main():
    """Main function to start both services"""
    print("🚀 Starting Enhanced Discord Bot + Web UI...")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs('./flask_session', exist_ok=True)
    
    # Start services
    print("\n📋 Starting services:")
    print("1. Discord Bot - Running enhanced_bot.py")
    print("2. Web Server - http://localhost:5000")
    print("3. Web UI - http://localhost:5000")
    
    # Start Discord bot in background thread
    bot_thread = threading.Thread(target=start_discord_bot, daemon=True)
    bot_thread.start()
    
    # Wait a moment for bot to initialize
    time.sleep(3)
    
    # Start web server
    start_web_server()

if __name__ == "__main__":
    main()
