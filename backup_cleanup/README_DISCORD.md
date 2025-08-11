# Discord OAuth Login Integration

This backend server now supports login via Discord OAuth2 instead of GitHub.

## Setup

1. Create a Discord OAuth2 application at https://discord.com/developers/applications
2. Set the Redirect URI to `http://localhost:5000/auth/callback`
3. Add the following environment variables to your `.env` file:
   ```
   DISCORD_CLIENT_ID=your_client_id
   DISCORD_CLIENT_SECRET=your_client_secret
   DISCORD_REDIRECT_URI=http://localhost:5000/auth/callback
   DISCORD_TOKEN=your_bot_token
   FLASK_SECRET_KEY=your_flask_secret_key
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run the backend server:
   ```
   python web_server.py
   ```

## Features

- Discord OAuth2 login and logout
- Session management with Flask-Session
- API endpoints protected by authentication
- Live Discord bot command data integration

## Usage

- Visit `/auth/login` to login with Discord
- Access protected API endpoints after login
- Logout via `/auth/logout`

## Notes

- Ensure your bot token and OAuth credentials are correct
- Use HTTPS in production and set `SESSION_COOKIE_SECURE=True`
- Customize scopes and permissions as needed

This setup replaces the previous GitHub OAuth login with Discord OAuth login for seamless integration with your Discord bot.
