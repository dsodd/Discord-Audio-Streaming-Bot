# 🎵 Discord Music Bot

A Discord Audio Streaming Bot designed for seamless cross-platform audio interaction and advanced command management.
Integrated streaming sources: Spotify Links, SoundCloud Links, Youtube/YT Music Links and Youtube Search Query.

## 📥 Installation

1. **Clone Repository & Install Dependencies**
   - git clone <repository-url>
   - cd Discord-Music-Bot
   - pip install -r requirements.txt
   - Recommended python version:
      - Version 3.11

2. **Install FFmpeg**
   - 🟦 Windows:
     1. Download from [FFmpeg website](https://ffmpeg.org/download.html) or [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
     2. Add FFmpeg to your system PATH (Win + R > sysdm.cpl > Advanced > Environment Variables > "PATH" > Edit > New > <FFMPEG_INSTALLATION_FOLDER_PATH>\bin > Save)
     
3. **Set Up Environment Variables**
   Create a `.env` file in the project root:

   - DISCORD_TOKEN=your_discord_bot_token
   - APPLICATION_ID=your_application_id
   - SPOTIFY_CLIENT_ID=your_spotify_client_id
   - SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

## 🔑 Getting API Credentials

1. **Discord Bot Setup**
   1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
   2. Create a new application
   3. Go to the "Bot" section
   4. Create a bot and copy the token
   5. Enable all Privileged Gateway Intents
   6. Go to OAuth2 → URL Generator
   7. Select "bot" and "applications.commands" scopes
   8. Copy the generated URL to invite the bot

2. **Spotify API Setup**
   1. Visit [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   2. Create a new app
   3. Copy the Client ID and Client Secret

## 📋 Available Commands

Both prefix commands (!) and slash commands (/) are supported:

- **/play <query>** or **!play <query>** or **!p <query>** - Play music from YouTube URL, Spotify URL, or search query
- **/queue** or **!queue** or **!q** - Display the current music queue
- **/pause** or **!pause** - Pause/resume the current song
- **/skip** or **!skip** or **!s**- Skip to the next song
- **/skipqueue [count]** or **!skipqueue [count]** or **!sq [count]** - Skip specified number of songs in queue (default: 1)
- **/stop** or **!stop** - Stop playback and clear the queue
- **/help** or **!help** - Show all available commands

## 🎮 Usage Examples

1. **Start playing music**
   /play despacito
   The bot will search YouTube and play the best match

2. **Queue management**
   /play https://open.spotify.com/track/...  (Add to queue)
   /queue  (Check current queue)
   /skip   (Move to next song)

3. **Playback control**
   /pause  (Toggle pause/resume)
   /stop   (Stop and clear queue)

4. **Queue management with skipqueue**
   !sq 3    (Skip next 3 songs in queue)
   /skipqueue 5  (Skip next 5 songs in queue)

## 🔧 Troubleshooting

### Desktop Client Issues

If slash commands aren't working on the desktop client:

1. **Clear Discord Cache**
   - Windows:
     1. Press `Win + R`
     2. Type `%appdata%/discord`
     3. Delete the `Cache` and `Code Cache` folders
     4. Restart Discord

   - macOS:
     1. Go to `~/Library/Application Support/discord`
     2. Delete the `Cache` and `Code Cache` folders
     3. Restart Discord

2. **Reset Discord Client**
   1. Log out of Discord
   2. Close Discord completely
   3. Wait 30 seconds
   4. Reopen Discord and log back in

3. **Alternative Solutions**
   - Use Discord in a web browser temporarily
   - Check if you have the latest Discord client version
   - Try restarting your computer
   - Reinvite the bot using the OAuth2 URL

### Common Issues

1. **No Sound Playing**
   - Verify FFmpeg is installed correctly
   - Check if the bot has proper permissions
   - Ensure you're in a voice channel

2. **Spotify Links Not Working**
   - Verify your Spotify credentials in `.env`
   - Check if the track/playlist is public
   - Try using the search query instead

3. **Bot Not Responding**
   - Check if the bot is online
   - Verify the bot has proper permissions
   - Try reinviting the bot to the server

## 🚀 Running the Bot

- Run the `bot.py` file to run the bot
