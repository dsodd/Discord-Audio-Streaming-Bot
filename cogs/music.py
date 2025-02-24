import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import traceback
<<<<<<< HEAD
=======
import random
import os
from collections import deque
import yt_dlp
import re
import urllib.parse
import requests
import subprocess
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.cache_handler import CacheFileHandler

class MusicError(Exception):
    """Base exception class for music-related errors"""
    pass

class VoiceConnectionError(MusicError):
    """Exception for voice connection issues"""
    pass

class AudioSourceError(MusicError):
    """Exception for audio source creation issues"""
    pass

class QueueError(MusicError):
    """Exception for queue-related issues"""
    pass

class SpotifyClient:
    def __init__(self):
        print("[DEBUG] Initializing SpotifyClient...")
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

        if not client_id or not client_secret:
            raise ValueError("Spotify credentials not found in environment variables")

        try:
            cache_dir = os.path.join(os.getcwd(), '.spotify_cache')
            os.makedirs(cache_dir, exist_ok=True)

            cache_path = os.path.join(cache_dir, 'spotify_token.cache')
            print(f"[DEBUG] Using cache path: {cache_path}")

            cache_handler = CacheFileHandler(cache_path=cache_path)

            auth_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret,
                cache_handler=cache_handler
            )
            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            print("[DEBUG] Successfully initialized Spotify client")

        except Exception as e:
            print(f"[ERROR] Failed to initialize Spotify client: {str(e)}")
            raise
    def extract_spotify_id(self, url):
        """Extract Spotify ID from URL"""
        url = url.split('?')[0]  # Remove query parameters
        pattern = r'(?:spotify\.com|open\.spotify\.com)/(?:track|playlist|album)/([a-zA-Z0-9]+)'
        match = re.search(pattern, url)
        if not match:
            raise ValueError("Invalid Spotify URL format")
        return match.group(1)

    def get_content_type(self, url):
        """Determine if URL is for track, playlist, or album"""
        url = url.split('?')[0]  # Remove query parameters
        if 'track' in url:
            return 'track'
        elif 'playlist' in url:
            return 'playlist'
        elif 'album' in url:
            return 'album'
        return None

    async def get_track_info(self, url):
        """Get track information from Spotify URL"""
        try:
            print(f"[DEBUG] Getting track info for URL: {url}")
            track_id = self.extract_spotify_id(url)

            try:
                track = self.sp.track(track_id)
                if not track:
                    raise Exception("Track not found")
                print(f"[DEBUG] Successfully retrieved track data from Spotify API")

                track_info = self._format_track_info(track)
                if not track_info:
                    raise Exception("Failed to format track information")

                return track_info

            except spotipy.exceptions.SpotifyException as e:
                if e.http_status == 404:
                    raise Exception("Track not found or is not available")
                raise Exception(f"Failed to access Spotify track: {str(e)}")

        except Exception as e:
            print(f"[ERROR] Failed to get Spotify track info: {str(e)}")
            raise

    async def get_playlist_tracks(self, url):
        """Get all tracks from a Spotify playlist"""
        try:
            print(f"[DEBUG] Getting playlist tracks for URL: {url}")
            playlist_id = self.extract_spotify_id(url)
            print(f"[DEBUG] Extracted playlist ID: {playlist_id}")

            try:
                playlist = self.sp.playlist(playlist_id)
                if not playlist:
                    raise Exception("Playlist not found")

                print(f"[DEBUG] Found playlist: {playlist['name']}")
                tracks = []

                # Get all tracks using pagination
                results = playlist['tracks']
                track_count = 0
                error_count = 0

                while results:
                    print(f"[DEBUG] Processing playlist page with {len(results['items'])} items")
                    for item in results['items']:
                        try:
                            if not item or not item.get('track'):
                                print("[WARNING] Skipping invalid track item")
                                continue

                            track = item['track']

                            # Skip local files and null tracks
                            if track.get('is_local', False) or not track.get('name'):
                                print("[WARNING] Skipping local or invalid track")
                                continue

                            # Create a more precise YouTube search query
                            artists = [artist['name'] for artist in track['artists']]
                            artist_names = ', '.join(artists)
                            track_name = track['name']

                            track_info = {
                                'title': f"{track_name} - {artist_names}",
                                'search_query': f"{track_name} {artist_names} official audio",
                                'duration_ms': track['duration_ms'],
                                'artists': artists
                            }

                            tracks.append(track_info)
                            track_count += 1
                            print(f"[DEBUG] Added track {track_count}: {track_info['title']}")

                        except Exception as track_error:
                            error_count += 1
                            print(f"[WARNING] Error processing track: {str(track_error)}")
                            continue

                    if results.get('next'):
                        print("[DEBUG] Fetching next page of playlist tracks")
                        results = self.sp.next(results)
                    else:
                        break

                print(f"[DEBUG] Playlist processing complete - Added: {track_count}, Errors: {error_count}")

                if not tracks:
                    raise Exception("No playable tracks found in playlist")

                return tracks

            except spotipy.exceptions.SpotifyException as e:
                print(f"[ERROR] Spotify API error: {str(e)}")
                if e.http_status == 404:
                    raise Exception("Playlist not found or is not accessible")
                raise Exception(f"Failed to access Spotify playlist: {str(e)}")

        except Exception as e:
            print(f"[ERROR] Failed to get playlist tracks: {str(e)}")
            print(traceback.format_exc())
            raise

    async def get_album_tracks(self, url):
        """Get all tracks from a Spotify album"""
        try:
            print(f"[DEBUG] Getting album tracks for URL: {url}")
            album_id = self.extract_spotify_id(url)
            print(f"[DEBUG] Extracted album ID: {album_id}")

            try:
                album = self.sp.album(album_id)
                if not album:
                    raise Exception("Album not found")

                print(f"[DEBUG] Found album: {album['name']}")
                tracks = []
                track_count = 0
                error_count = 0

                # Get all tracks using pagination
                results = album['tracks']
                while results:
                    print(f"[DEBUG] Processing album page with {len(results['items'])} items")
                    for track in results['items']:
                        try:
                            if not track or track.get('is_local', False):
                                print("[WARNING] Skipping invalid or local track")
                                continue

                            # Get full track info for better metadata
                            full_track = self.sp.track(track['id'])

                            # Create a more precise YouTube search query
                            artists = [artist['name'] for artist in full_track['artists']]
                            artist_names = ', '.join(artists)
                            track_name = full_track['name']

                            track_info = {
                                'title': f"{track_name} - {artist_names}",
                                'search_query': f"{track_name} {artist_names} official audio",
                                'duration_ms': full_track['duration_ms'],
                                'artists': artists
                            }

                            tracks.append(track_info)
                            track_count += 1
                            print(f"[DEBUG] Added track {track_count}: {track_info['title']}")

                        except Exception as track_error:
                            error_count += 1
                            print(f"[WARNING] Error processing track: {str(track_error)}")
                            continue

                    if results.get('next'):
                        print("[DEBUG] Fetching next page of album tracks")
                        results = self.sp.next(results)
                    else:
                        break

                print(f"[DEBUG] Album processing complete - Added: {track_count}, Errors: {error_count}")

                if not tracks:
                    raise Exception("No playable tracks found in album")

                return tracks

            except spotipy.exceptions.SpotifyException as e:
                print(f"[ERROR] Spotify API error: {str(e)}")
                if e.http_status == 404:
                    raise Exception("Album not found or is not accessible")
                raise Exception(f"Failed to access Spotify album: {str(e)}")

        except Exception as e:
            print(f"[ERROR] Failed to get album tracks: {str(e)}")
            print(traceback.format_exc())
            raise

    def _format_track_info(self, track):
        """Format track information consistently"""
        try:
            if not track:
                return None

            artists = [artist['name'] for artist in track['artists']]
            artist_names = ', '.join(artists)
            track_name = track['name']

            formatted_info = {
                'title': f"{track_name} - {artist_names}",
                'search_query': f"{track_name} {artist_names} official audio",
                'duration_ms': track['duration_ms'],
                'preview_url': track.get('preview_url'),
                'artists': artists
            }

            print(f"[DEBUG] Formatted track info: {formatted_info['title']}")
            return formatted_info

        except Exception as e:
            print(f"[WARNING] Failed to format track info: {str(e)}")
            return None

class MusicSource:
    def __init__(self, source_url, title):
        self.source_url = source_url
        self.title = title
        self._spotify_client = None
        self.remaining_tracks = None

    @property
    def spotify_client(self):
        """Lazy initialization of Spotify client"""
        if self._spotify_client is None:
            self._spotify_client = SpotifyClient()
        return self._spotify_client

    @staticmethod
    async def create_source(query):
        """Create a music source from a URL or search query"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'ignoreerrors': True,
            'source_address': '0.0.0.0',
            'retries': 10,
            'socket_timeout': 10,
            'default_search': 'ytsearch',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try:
            # Check for FFmpeg before proceeding
            try:
                print("[DEBUG] Checking FFmpeg installation...")
                subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
                print("[DEBUG] FFmpeg is installed and accessible")
            except Exception as e:
                print(f"[ERROR] FFmpeg check failed: {str(e)}")
                raise Exception("FFmpeg is not properly installed or accessible")

            if 'music.youtube.com' in query:
                query = query.replace('music.youtube.com', 'youtube.com')
                print(f"[DEBUG] Converted YouTube Music URL to: {query}")

            spotify_pattern = r'(?:spotify\.com|open\.spotify\.com)/(?:track|playlist|album)/[a-zA-Z0-9]+'
            spotify_match = re.search(spotify_pattern, query)

            if spotify_match:
                print(f"[DEBUG] Processing Spotify URL: {query}")
                try:
                    spotify_client = SpotifyClient()
                    content_type = spotify_client.get_content_type(query)
                    print(f"[DEBUG] Detected Spotify content type: {content_type}")

                    if content_type == 'playlist':
                        print(f"[DEBUG] Starting playlist processing for: {query}")
                        tracks = await spotify_client.get_playlist_tracks(query)
                        print(f"[DEBUG] Retrieved {len(tracks)} tracks from Spotify playlist")

                        if not tracks:
                            raise Exception("No playable tracks found in playlist")

                        first_track = tracks[0]
                        if not first_track or not first_track.get('search_query'):
                            raise Exception("Invalid track data in playlist")

                        print(f"[DEBUG] Processing first track: {first_track['search_query']}")
                        try:
                            source = await MusicSource._create_youtube_source(first_track['search_query'], ydl_opts)
                            if source:
                                source.remaining_tracks = tracks[1:]
                                print(f"[DEBUG] Successfully created source for first track with {len(tracks[1:])} remaining tracks")
                                return source
                            else:
                                raise Exception("Failed to create source for first track")
                        except Exception as yt_error:
                            print(f"[ERROR] YouTube processing error for first track: {str(yt_error)}")
                            raise

                    elif content_type == 'album':
                        print(f"[DEBUG] Processing album: {query}")
                        tracks = await spotify_client.get_album_tracks(query)
                        print(f"[DEBUG] Retrieved {len(tracks)} tracks from Spotify album")

                        if not tracks:
                            raise Exception("No playable tracks found in album")

                        first_track = tracks[0]
                        if not first_track or not first_track.get('search_query'):
                            raise Exception("Invalid track data in album")

                        print(f"[DEBUG] Processing first track: {first_track['search_query']}")
                        source = await MusicSource._create_youtube_source(first_track['search_query'], ydl_opts)
                        source.remaining_tracks = tracks[1:]
                        return source

                    else:  # Single track
                        print(f"[DEBUG] Processing single track: {query}")
                        track_info = await spotify_client.get_track_info(query)
                        if not track_info or not track_info.get('search_query'):
                            raise Exception("Failed to get track information")
                        print(f"[DEBUG] Processing Spotify track: {track_info['search_query']}")
                        return await MusicSource._create_youtube_source(track_info['search_query'], ydl_opts)

                except Exception as e:
                    print(f"[ERROR] Spotify processing error: {str(e)}")
                    print(traceback.format_exc())
                    raise Exception(f"Failed to process Spotify content: {str(e)}")

            if not re.match(r'http[s]?://', query):
                search_query = f"ytsearch:{query}"
                print(f"[DEBUG] Processing as search query: {search_query}")
                return await MusicSource._create_youtube_source(search_query, ydl_opts)
            else:
                print(f"[DEBUG] Processing as direct URL: {query}")
                return await MusicSource._create_youtube_source(query, ydl_opts)

        except Exception as e:
            print(f"[ERROR] Error in create_source: {str(e)}")
            print(traceback.format_exc())
            raise Exception(f"Failed to process source: {str(e)}")

    @staticmethod
    async def _create_youtube_source(query, ydl_opts):
        """Create a YouTube source from a query"""
        max_retries = 3
        current_retry = 0

        while current_retry < max_retries:
            try:
                cookie_opts = {
                    'cookiefile': None,
                    'nocheckcertificate': True,
                    'age_limit': None
                }
                ydl_opts.update(cookie_opts)

                print(f"[DEBUG] Extracting info with yt-dlp for: {query} (Attempt {current_retry + 1}/{max_retries})")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        info = ydl.extract_info(query, download=False)
                        if not info:
                            raise Exception("No results found")

                        if 'entries' in info:
                            if not info['entries']:
                                raise Exception("No matching songs found")

                            valid_entry = None
                            error_messages = []

                            for entry in info['entries']:
                                try:
                                    if entry and entry.get('url'):
                                        test_response = requests.head(entry['url'], timeout=5)
                                        if test_response.status_code == 200:
                                            valid_entry = entry
                                            break
                                except Exception as e:
                                    error_messages.append(f"Entry error: {str(e)}")
                                    continue

                            if valid_entry:
                                info = valid_entry
                            else:
                                raise Exception(f"No playable entries found. Errors: {', '.join(error_messages)}")

                        if not info.get('url'):
                            raise Exception("No valid URL found in the extracted info")

                        title = info.get('title', 'Unknown Title')
                        print(f"[DEBUG] Successfully extracted info for: {title}")

                        return MusicSource(
                            source_url=info['url'],
                            title=title
                        )

                    except yt_dlp.utils.DownloadError as e:
                        error_message = str(e)
                        if 'Sign in to confirm your age' in error_message:
                            ydl_opts['format'] = 'bestaudio'
                            continue
                        elif any(msg in error_message for msg in ['Video unavailable', 'Private video']):
                            raise Exception(f"Video not accessible: {error_message}")
                        elif current_retry < max_retries - 1:
                            print(f"[WARNING] yt-dlp extraction failed, retrying... ({current_retry + 1}/{max_retries})")
                            current_retry += 1
                            continue
                        else:
                            raise Exception(f"Failed to extract video information: {error_message}")

            except Exception as e:
                if current_retry < max_retries - 1:
                    print(f"[WARNING] Attempt {current_retry + 1} failed, retrying...")
                    current_retry += 1
                    continue
                else:
                    print(f"[ERROR] Error in _create_youtube_source after {max_retries} attempts: {str(e)}")
                    print(traceback.format_exc())
                    raise Exception(f"Failed to process video after {max_retries} attempts: {str(e)}")

    async def get_audio(self):
        """Get the audio source for discord.py"""
        try:
            print(f"[DEBUG] Creating FFmpeg audio source for: {self.title}")

            if not self.source_url:
                raise Exception("No valid source URL available")

            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn -b:a 192k -bufsize 3000k'
            }

            try:
                audio_source = discord.FFmpegPCMAudio(
                    self.source_url,
                    **ffmpeg_options
                )
                print("[DEBUG] FFmpeg audio source created successfully")
                return audio_source
            except Exception as e:
                print(f"[ERROR] FFmpeg audio source creation failed: {str(e)}")
                raise Exception(f"Failed to create audio stream: {str(e)}")

        except Exception as e:
            print(f"[ERROR] Failed to create audio source: {str(e)}")
            print(traceback.format_exc())
            raise Exception(f"Failed to create audio source: {str(e)}")

class QueueManager:
    def __init__(self):
        self.queue = deque()
        self.current = None

    def add(self, item):
        """Add an item to the queue"""
        self.queue.append(item)

    def get_next(self):
        """Get the next item from the queue"""
        if not self.is_empty():
            self.current = self.queue.popleft()
            return self.current
        return None

    def clear(self):
        """Clear the queue"""
        self.queue.clear()
        self.current = None

    def is_empty(self):
        """Check if the queue is empty"""
        return len(self.queue) == 0

    def get_queue(self):
        """Get the current queue as a list"""
        return list(self.queue)


<<<<<<< HEAD
>>>>>>> 0dcaccf (Update)

=======
>>>>>>> f43f3bb (Applying some come that is confirmed to b working)
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
<<<<<<< HEAD
        self.queue_managers = {}  # Dict to store queue managers for each guild
=======
        self.queue_managers = {}
        print("[DEBUG] Music cog initialized")
>>>>>>> 0dcaccf (Update)

        # Register slash commands
        self.bot.tree.add_command(app_commands.Command(
            name='play',
            description='Play music from a URL or search query',
            callback=self.play
        ))
        self.bot.tree.add_command(app_commands.Command(
            name='queue',
            description='Display the current queue',
            callback=self.queue
        ))
        self.bot.tree.add_command(app_commands.Command(
            name='pause',
            description='Pause or resume the current song',
            callback=self.pause
        ))
        self.bot.tree.add_command(app_commands.Command(
            name='stop',
            description='Stop playback and clear the queue',
            callback=self.stop
        ))

    def get_queue_manager(self, guild_id):
        if guild_id not in self.queue_managers:
            self.queue_managers[guild_id] = QueueManager()
        return self.queue_managers[guild_id]

<<<<<<< HEAD
    async def play(self, interaction: discord.Interaction, query: str):
        """Play music from a given URL or search query"""
        if not interaction.user.voice:
            await interaction.response.send_message("You need to be in a voice channel!")
=======
    @commands.command(name='play', aliases=['p'])
    async def play_command(self, ctx, *, query: str):
        """Play music from a URL or search query (prefix command version)"""
        await self.play_impl(ctx, query)

    @app_commands.command(
        name='play',
        description='Play music from YouTube URL, Spotify URL (tracks, playlists, albums), or search query'
    )
    async def play_slash(self, interaction: discord.Interaction, query: str):
        """Play music from a URL or search query (slash command version)"""
        await self.play_impl(interaction, query)

    async def play_impl(self, ctx_or_interaction, query: str):
        """Unified implementation for play command with enhanced error handling"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)

<<<<<<< HEAD
        if is_interaction:
            user = ctx_or_interaction.user
            guild = ctx_or_interaction.guild
            await ctx_or_interaction.response.defer()
        else:
            user = ctx_or_interaction.author
            guild = ctx_or_interaction.guild

        if not user.voice:
            embed = self.create_embed("Error", "You need to be in a voice channel!", discord.Color.red())
            if is_interaction:
                await ctx_or_interaction.followup.send(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
>>>>>>> 0dcaccf (Update)
            return

        queue_manager = self.get_queue_manager(guild.id)

        try:
<<<<<<< HEAD
            # Connect to voice channel if not already connected
            if not interaction.guild.voice_client:
=======
=======
        try:
            if is_interaction:
                user = ctx_or_interaction.user
                guild = ctx_or_interaction.guild
                await ctx_or_interaction.response.defer()
            else:
                user = ctx_or_interaction.author
                guild = ctx_or_interaction.guild

            if not user.voice:
                raise VoiceConnectionError("You need to be in a voice channel!")

            queue_manager = self.get_queue_manager(guild.id)

>>>>>>> f43f3bb (Applying some come that is confirmed to b working)
            # Handle voice channel connection
            if not guild.voice_client:
>>>>>>> 0dcaccf (Update)
                try:
                    await user.voice.channel.connect(timeout=20.0, self_deaf=True)
                except Exception as e:
<<<<<<< HEAD
<<<<<<< HEAD
                    print(f"[ERROR] Failed to connect to voice channel: {str(e)}")
                    await interaction.followup.send("Failed to connect to voice channel. Please try again.")
                    return

            # Process the query and get the source
            print(f"[DEBUG] Processing query: {query}")
            music_source = await MusicSource.create_source(query)
            print(f"[DEBUG] Created music source for: {music_source.title}")
=======
                    print(f"[ERROR] Voice connection failed: {str(e)}")
                    embed = self.create_embed("Connection Error", 
                        "Failed to connect to voice channel. Please try again.", 
                        discord.Color.red())
                    if is_interaction:
                        await ctx_or_interaction.followup.send(embed=embed)
                    else:
                        await ctx_or_interaction.send(embed=embed)
=======
                    await self.handle_voice_state_error(ctx_or_interaction, e)
>>>>>>> f43f3bb (Applying some come that is confirmed to b working)
                    return

            # Create music source with error handling
            try:
                music_source = await MusicSource.create_source(query)
            except Exception as e:
                await self.handle_music_source_error(ctx_or_interaction, e)
                return
>>>>>>> 0dcaccf (Update)

            # Add to queue
            queue_manager.add(music_source)
            await interaction.followup.send(f"Added to queue: {music_source.title}")

<<<<<<< HEAD
            # Start playing if not already playing
            if not interaction.guild.voice_client.is_playing():
                print("[DEBUG] Starting playback...")
                await self.play_next(interaction)

        except Exception as e:
            error_msg = f"Error in play command:\n{str(e)}\n{traceback.format_exc()}"
            print(f"[ERROR] {error_msg}")
            await interaction.followup.send(f"An error occurred: {str(e)}")

    async def play_next(self, interaction):
        """Play the next song in the queue"""
        queue_manager = self.get_queue_manager(interaction.guild_id)

        if queue_manager.is_empty():
            await interaction.followup.send("Queue is empty!")
            return

        try:
            print("[DEBUG] Getting next song from queue...")
            source = queue_manager.get_next()
            print(f"[DEBUG] Getting audio source for: {source.title}")
            audio_source = await source.get_audio()
            print("[DEBUG] Audio source created successfully")

            def after_playing(error):
                if error:
                    error_msg = f"Error after playing: {str(error)}\n{traceback.format_exc()}"
                    print(f"[ERROR] {error_msg}")
                    asyncio.run_coroutine_threadsafe(
                        interaction.followup.send(f"An error occurred while playing: {error}"),
                        self.bot.loop
                    )
                else:
                    print("[DEBUG] Song finished playing, moving to next...")
                    asyncio.run_coroutine_threadsafe(
                        self.play_next(interaction), self.bot.loop
                    )

            print("[DEBUG] Starting playback...")
            if interaction.guild.voice_client and interaction.guild.voice_client.is_connected():
                interaction.guild.voice_client.play(audio_source, after=after_playing)
                await interaction.followup.send(f"Now playing: {source.title}")
            else:
                print("[ERROR] Voice client disconnected before playback could start")
                await interaction.followup.send("Lost connection to voice channel. Please try again.")

        except Exception as e:
            error_msg = f"Error in play_next:\n{str(e)}\n{traceback.format_exc()}"
            print(f"[ERROR] {error_msg}")
            await interaction.followup.send(f"An error occurred while playing the next song: {str(e)}")

    async def queue(self, interaction: discord.Interaction):
        """Display the current queue"""
        queue_manager = self.get_queue_manager(interaction.guild_id)
        if queue_manager.is_empty():
            await interaction.response.send_message("Queue is empty!")
=======
            # Handle playlist/album tracks
            remaining_tracks = getattr(music_source, 'remaining_tracks', None)
            if remaining_tracks:
                successful_additions = 0
                failed_additions = 0

                for track_info in remaining_tracks:
                    try:
                        additional_source = await MusicSource.create_source(track_info['search_query'])
                        queue_manager.add(additional_source)
                        successful_additions += 1
                    except Exception as e:
                        print(f"[ERROR] Failed to process track: {str(e)}")
                        failed_additions += 1

                total_tracks = successful_additions + 1  # +1 for the first track
                status_message = f"🎵 Added {total_tracks} tracks to the queue"
                if failed_additions > 0:
                    status_message += f"\n⚠️ {failed_additions} tracks couldn't be processed"

                embed = self.create_embed(
                    "Added to Queue",
                    f"{status_message}\n**Now Playing:** {music_source.title}"
                )
            else:
                embed = self.create_embed("Added to Queue", f"🎵 **{music_source.title}**")

            if is_interaction:
                await ctx_or_interaction.followup.send(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)

            # Start playback if not already playing
            if not guild.voice_client.is_playing():
                await self.play_next(ctx_or_interaction)

        except VoiceConnectionError as e:
            await self.handle_voice_state_error(ctx_or_interaction, e)
        except QueueError as e:
            await self.handle_queue_error(ctx_or_interaction, e)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error in play command: {str(e)}")
            logger.error(traceback.format_exc())
            error_message = f"An unexpected error occurred: {str(e)}"
            embed = self.create_embed("Error", error_message, discord.Color.red())

            if is_interaction:
                if not ctx_or_interaction.response.is_done():
                    await ctx_or_interaction.response.send_message(embed=embed)
                else:
                    await ctx_or_interaction.followup.send(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)


    @commands.command(name='queue', aliases=['q'])
    async def queue_command(self, ctx):
        view = ButtonPause, ButtonSkip
        """Display the current queue (prefix command version)"""
        await self.queue_impl(ctx, view=view)

    @app_commands.command(
        name='queue',
        description='Display the current queue'
    )
    async def queue_slash(self, interaction: discord.Interaction):
        """Display the current queue (slash command version)"""
        await self.queue_impl(interaction)

    async def queue_impl(self, ctx_or_interaction):
        """Unified implementation for queue command"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        guild_id = ctx_or_interaction.guild_id if is_interaction else ctx_or_interaction.guild.id

        queue_manager = self.get_queue_manager(guild_id)
        if queue_manager.is_empty():
            embed = self.create_embed("Queue", "Queue is empty!", discord.Color.blue())
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
>>>>>>> 0dcaccf (Update)
            return

        queue_list = queue_manager.get_queue()
        queue_text = "\n".join(
            f"{i+1}. {song.title}" for i, song in enumerate(queue_list)
        )
<<<<<<< HEAD
        await interaction.response.send_message(f"Current queue:\n{queue_text}")

    async def pause(self, interaction: discord.Interaction):
        """Pause or resume the current song"""
        if not interaction.guild.voice_client:
            await interaction.response.send_message("Not connected to a voice channel!")
            return

        if interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.pause()
            await interaction.response.send_message("Playback paused")
        elif interaction.guild.voice_client.is_paused():
            interaction.guild.voice_client.resume()
            await interaction.response.send_message("Playback resumed")
        else:
            await interaction.response.send_message("Nothing is playing!")

    async def stop(self, interaction: discord.Interaction):
        """Stop playback and clear the queue"""
        if not interaction.guild.voice_client:
            await interaction.response.send_message("Not connected to a voice channel!")
=======
        embed = self.create_embed("Current Queue", queue_text)
        if is_interaction:
            await ctx_or_interaction.response.send_message(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

    @commands.command(name='pause')
    async def pause_command(self, ctx):
        """Pause or resume the current song (prefix command version)"""
        await self.pause_impl(ctx)

    @app_commands.command(
        name='pause',
        description='Pause or resume the current song'
    )
    async def pause_slash(self, interaction: discord.Interaction):
        """Pause or resume the current song (slash command version)"""
        await self.pause_impl(interaction)

    async def pause_impl(self, ctx_or_interaction):
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        guild = ctx_or_interaction.guild if is_interaction else ctx_or_interaction.guild

        if not guild.voice_client:
            embed = self.create_embed("Error", "Not connected to a voice channel!", discord.Color.red())
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            return

        if guild.voice_client.is_playing():
            guild.voice_client.pause()
            embed = self.create_embed("Playback Paused", "⏸️ Music playback has been paused")
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
        elif guild.voice_client.is_paused():
            guild.voice_client.resume()
            embed = self.create_embed("Playback Resumed", "▶️ Music playback has been resumed")
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
        else:
            embed = self.create_embed("Error", "Nothing is playing!", discord.Color.red())
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)

    @commands.command(name='skip', aliases=['s'])
    async def skip_command(self, ctx):
        """Skip the current song (prefix command version)"""
        await self.skip_impl(ctx)

    @app_commands.command(
        name='skip',
        description='Skip the current song and play the next one'
    )
    async def skip_slash(self, interaction: discord.Interaction):
        """Skip the current song (slash command version)"""
        await self.skip_impl(interaction)

    async def skip_impl(self, ctx_or_interaction):
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        guild = ctx_or_interaction.guild if is_interaction else ctx_or_interaction.guild

        if not guild.voice_client:
            embed = self.create_embed("Error", "Not connected to a voice channel!", discord.Color.red())
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            return

        queue_manager = self.get_queue_manager(guild.id)
        if not guild.voice_client.is_playing():
            embed = self.create_embed("Error", "Nothing is currently playing!", discord.Color.red())
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            return

        if queue_manager.is_empty():
            embed = self.create_embed("Queue Empty", "No more songs in the queue!", discord.Color.blue())
            guild.voice_client.stop()
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            return

        guild.voice_client.stop()
        embed = self.create_embed("Skipped", "⏭️ Skipped to the next song!")
        if is_interaction:
            await ctx_or_interaction.response.send_message(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)



    @commands.command(name='stop')
    async def stop_command(self, ctx):
        """Stop playback and clear the queue (prefix command version)"""
        await self.stop_impl(ctx)

    @app_commands.command(
        name='stop',
        description='Stop playback and clear the queue'
    )
    async def stop_slash(self, interaction: discord.Interaction):
        """Stop playback and clear the queue (slash command version)"""
        await self.stop_impl(interaction)

    async def stop_impl(self, ctx_or_interaction):
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        guild = ctx_or_interaction.guild if is_interaction else ctx_or_interaction.guild

        if not guild.voice_client:
            embed = self.create_embed("Error", "Not connected to a voice channel!", discord.Color.red())
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
>>>>>>> 0dcaccf (Update)
            return

        queue_manager = self.get_queue_manager(guild.id)
        queue_manager.clear()
<<<<<<< HEAD
        interaction.guild.voice_client.stop()
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Stopped playback and cleared queue")
=======
        guild.voice_client.stop()
        await guild.voice_client.disconnect()
        embed = self.create_embed("Stopped", "⏹️ Stopped playback and cleared queue")
        if is_interaction:
            await ctx_or_interaction.response.send_message(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

    @commands.command(name='help')
    async def help_command(self, ctx):
        await self.help_impl(ctx)

    @app_commands.command(
        name='help',
        description='Show all available commands and their descriptions'
    )
    async def help_slash(self, interaction: discord.Interaction):
        await self.help_impl(interaction)

    async def help_impl(self, ctx_or_interaction):
        """Unified implementation for help command"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)

        commands_list = [
            "**/play <query>** or **!play <query>** or **!p <query>** - Play music from SoundCloud URL, YouTube URL, Spotify URL, or search query",
            "**/queue** or **!queue** or **!q** - Display the current music queue",
            "**/pause** or **!pause** - Pause/resume the current song",
            "**/skip** or **!skip** or **!s**- Skip to the next song",
            "**/skipqueue [count]** or **!skipqueue [count]** or **!sq [count]** - Skip specified number of songs in queue (default: 1)",
            "**/stop** or **!stop** - Stop playback and clear the queue",
            "**/help** or **!help** - Show all available commands"
        ]

        help_text = "Both prefix commands (! or /) and slash commands (/) are supported:\n\n"
        help_text += "\n".join(f"- {cmd}" for cmd in commands_list)

        embed = self.create_embed(
            "📋 Available Commands",
            help_text
        )
        if is_interaction:
            await ctx_or_interaction.response.send_message(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

    @commands.command(name='skipqueue', aliases=['sq'])
    async def skipqueue_command(self, ctx, count: int = 1):
        """Skip songs in the queue without affecting the current song (prefix command version)"""
        await self.skipqueue_impl(ctx, count)

    @app_commands.command(
        name='skipqueue',
        description='Skip songs in the queue without affecting the current song'
    )
    @app_commands.describe(count='Number of songs to skip (default: 1)')
    async def skipqueue_slash(self, interaction: discord.Interaction, count: int = 1):
        """Skip songs in the queue without affecting the current song (slash command version)"""
        await self.skipqueue_impl(interaction, count)

    async def skipqueue_impl(self, ctx_or_interaction, count: int = 1):
        """Unified implementation for skipqueue command"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        guild = ctx_or_interaction.guild if is_interaction else ctx_or_interaction.guild

        if not guild.voice_client:
            embed = self.create_embed("Error", "Not connected to a voice channel!", discord.Color.red())
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            return

        queue_manager = self.get_queue_manager(guild.id)
        if queue_manager.is_empty():
            embed = self.create_embed("Error", "No songs in queue to skip!", discord.Color.red())
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            return

        # Validate count parameter
        if count <= 0:
            embed = self.create_embed("Error", "Number of songs to skip must be positive!", discord.Color.red())
            if is_interaction:
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            return

        queue_list = queue_manager.get_queue()
        skip_count = min(count, len(queue_list))  # Don't skip more songs than are in queue
        skipped_songs = []

        # Remove songs from queue
        for _ in range(skip_count):
            skipped_songs.append(queue_manager.queue.popleft())

        # Create response message
        if len(skipped_songs) == 1:
            description = f"⏭️ Removed from queue: **{skipped_songs[0].title}**"
        else:
            description = "⏭️ Removed from queue:\n" + "\n".join(
                f"**{i+1}.** {song.title}" for i, song in enumerate(skipped_songs)
            )

        embed = self.create_embed("Skipped from Queue", description)
        if is_interaction:
            await ctx_or_interaction.response.send_message(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

    async def play_next(self, ctx_or_interaction):
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        guild = ctx_or_interaction.guild if is_interaction else ctx_or_interaction.guild

        queue_manager = self.get_queue_manager(guild.id)

        if queue_manager.is_empty():
            embed = self.create_embed("Queue Empty", "Queue is empty!", discord.Color.blue())
            if is_interaction:
                await ctx_or_interaction.followup.send(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)
            return

        try:
            source = queue_manager.get_next()

            try:
                audio_source = await source.get_audio()
            except Exception as e:
                print(f"[ERROR] Failed to create audio source: {str(e)}")
                print(traceback.format_exc())
                embed = self.create_embed("Playback Error", 
                    f"Could not play {source.title}: {str(e)}", 
                    discord.Color.red())
                if is_interaction:
                    await ctx_or_interaction.followup.send(embed=embed)
                else:
                    await ctx_or_interaction.send(embed=embed)
                # Try to play the next song
                await self.play_next(ctx_or_interaction)
                return

            def after_playing(error):
                if error:
                    print(f"[ERROR] Playback error: {str(error)}")
                    print(traceback.format_exc())
                    asyncio.run_coroutine_threadsafe(
                        ctx_or_interaction.followup.send(
                            embed=self.create_embed("Playback Error", 
                                f"Error during playback: {str(error)}", 
                                discord.Color.red())
                        ) if is_interaction else ctx_or_interaction.send(embed=self.create_embed("Playback Error", 
                                f"Error during playback: {str(error)}", 
                                discord.Color.red())),
                        self.bot.loop
                    )

                print("[DEBUG] Song finished, playing next...")
                asyncio.run_coroutine_threadsafe(
                    self.play_next(ctx_or_interaction),
                    self.bot.loop
                )

            if guild.voice_client and guild.voice_client.is_connected():
                guild.voice_client.play(audio_source, after=after_playing)
                embed = self.create_embed("Now Playing", f"🎵 **{source.title}**")
                if is_interaction:
                    await ctx_or_interaction.followup.send(embed=embed)
                else:
                    await ctx_or_interaction.send(embed=embed)
            else:
                print("[ERROR] Voice client disconnected")
                embed = self.create_embed("Connection Error", 
                    "Lost connection to voice channel", 
                    discord.Color.red())
                if is_interaction:
                    await ctx_or_interaction.followup.send(embed=embed)
                else:
                    await ctx_or_interaction.send(embed=embed)

        except Exception as e:
            print(f"[ERROR] Error in play_next: {str(e)}")
            print(traceback.format_exc())
            embed = self.create_embed("Error", 
                f"Failed to play next song: {str(e)}", 
                discord.Color.red())
            if is_interaction:
                await ctx_or_interaction.followup.send(embed=embed)
            else:
                await ctx_or_interaction.send(embed=embed)

    def get_queue_manager(self, guild_id):
        """Get or create a queue manager for a guild"""
        if guild_id not in self.queue_managers:
            self.queue_managers[guild_id] = QueueManager()
        return self.queue_managers[guild_id]
>>>>>>> 0dcaccf (Update)

    async def handle_voice_state_error(self, ctx_or_interaction, error):
        """Handle voice state related errors"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        error_message = None

        if isinstance(error, discord.ClientException):
            if "already connected to a voice channel" in str(error):
                error_message = "I'm already connected to a voice channel!"
            elif "Not connected to voice" in str(error):
                error_message = "I'm not connected to any voice channel!"
        elif isinstance(error, discord.opus.OpusNotLoaded):
            error_message = "Failed to load audio system. Please try again later."
        elif isinstance(error, TimeoutError):
            error_message = "Timed out while trying to connect to voice channel."
        else:
            error_message = f"Voice connection error: {str(error)}"

        embed = self.create_embed("Error", error_message, discord.Color.red())

        if is_interaction:
            if not ctx_or_interaction.response.is_done():
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.followup.send(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

    async def handle_music_source_error(self, ctx_or_interaction, error):
        """Handle music source creation errors"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        error_message = None

        if "age restricted" in str(error).lower():
            error_message = "This video is age-restricted and cannot be played."
        elif "not available in your country" in str(error).lower():
            error_message = "This content is not available in the bot's region."
        elif "private video" in str(error).lower():
            error_message = "This video is private and cannot be accessed."
        elif "sign in" in str(error).lower():
            error_message = "This content requires authentication and cannot be played."
        elif "no playable" in str(error).lower():
            error_message = "No playable sources found for this content."
        else:
            error_message = f"Failed to process audio source: {str(error)}"

        embed = self.create_embed("Error", error_message, discord.Color.red())

        if is_interaction:
            if not ctx_or_interaction.response.is_done():
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.followup.send(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

    async def handle_queue_error(self, ctx_or_interaction, error):
        """Handle queue-related errors"""
        is_interaction = isinstance(ctx_or_interaction, discord.Interaction)
        error_message = None

        if isinstance(error, QueueError):
            if "empty" in str(error).lower():
                error_message = "The queue is empty!"
            elif "invalid position" in str(error).lower():
                error_message = "Invalid queue position specified!"
            else:
                error_message = str(error)
        else:
            error_message = f"Queue error: {str(error)}"

        embed = self.create_embed("Error", error_message, discord.Color.red())

        if is_interaction:
            if not ctx_or_interaction.response.is_done():
                await ctx_or_interaction.response.send_message(embed=embed)
            else:
                await ctx_or_interaction.followup.send(embed=embed)
        else:
            await ctx_or_interaction.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle music-specific command errors"""
        try:
            if isinstance(error, commands.CommandOnCooldown):
                # Add rate limit protection
                await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
            elif isinstance(error, commands.MaxConcurrencyReached):
                await ctx.send("This command is already running! Please wait for it to finish.")
            else:
                # Let the global error handler handle other errors
                await self.bot.on_command_error(ctx, error)
        except Exception as e:
            #print(f"Error in music error handler: {str(e)}")
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in music error handler: {str(e)}")
            logger.error(traceback.format_exc())

    def cog_command_error(self, ctx, error):
        """Handle music-specific slash command errors"""
        try:
            if isinstance(error, commands.CommandOnCooldown):
                return ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
            elif isinstance(error, commands.MaxConcurrencyReached):
                return ctx.send("This command is already running! Please wait for it to finish.")
            # Let the global error handler handle other errors
            return self.bot.tree.on_error(ctx, error)
        except Exception as e:
            #print(f"Error in music slash command error handler: {str(e)}")
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in music slash command error handler: {str(e)}")
            logger.error(traceback.format_exc())

class ButtonSkip(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Skip!", style=discord.ButtonStyle.primary, custom_id="buttonSkip")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You clicked the button!", ephemeral=True)  # Only visible to the user

class ButtonPause(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Pause!", style=discord.ButtonStyle.primary, custom_id="buttonPause")
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You clicked the button!", ephemeral=True)  # Only visible to the user

async def setup(bot):
    await bot.add_cog(Music(bot))