# Discord Bot Web UI - Quick Start Guide

## 🚀 One-Command Start

To start both your Discord bot and web UI simultaneously, run:

```bash
python start_bot_and_web.py
```

This will:
- ✅ Start your Discord bot
- ✅ Start the Flask web server on http://localhost:5000
- ✅ Open the web UI with live bot data
- ✅ Enable GitHub OAuth login

## 📋 Manual Setup Steps

### 1. Environment Setup
Create a `.env` file with:
```bash
DISCORD_TOKEN=your_discord_bot_token
GITHUB_CLIENT_ID=your_github_oauth_app_id
GITHUB_CLIENT_SECRET=your_github_oauth_app_secret
FLASK_SECRET_KEY=your_random_secret_key
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Services
```bash
# Option 1: One command (recommended)
python start_bot_and_web.py

# Option 2: Separate commands
python web_server.py  # Starts web server
# In another terminal:
python enhanced_bot.py  # Starts Discord bot
```

## 🌐 Access Points

- **Web UI**: http://localhost:5000
- **API Endpoints**: http://localhost:5000/api/*
- **GitHub Login**: http://localhost:5000/auth/login

## 📱 Features Available

- **Live Command Display**: All bot commands with real-time data
- **GitHub OAuth Login**: Secure authentication
- **Responsive Design**: Works on mobile and desktop
- **Dark/Light Theme**: User preference saved
- **Search & Filter**: Find commands quickly
- **Copy Commands**: One-click copy to clipboard

## 🔧 Troubleshooting

### Bot Not Starting
- Check your Discord token in `.env`
- Ensure bot has proper permissions

### Web Server Issues
- Check port 5000 is available
- Verify GitHub OAuth credentials

### Dependencies
- All required packages are in `requirements.txt`
- Run `pip install -r requirements.txt` to install

## 🎯 Quick Commands

```bash
# Start everything
python start_bot_and_web.py

# View logs
tail -f bot.log

# Stop services
Ctrl+C in terminal
```

Your Discord bot and web UI are now ready to use with one simple command!
