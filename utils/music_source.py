import discord
import yt_dlp
import re
import traceback
import subprocess
<<<<<<< HEAD
=======
import urllib.parse
import requests
import os
import json
import tempfile
from .spotify_client import SpotifyClient
>>>>>>> a1187e1 (cil)

class MusicSource:
    def __init__(self, source_url, title):
        self.source_url = source_url
        self.title = title
<<<<<<< HEAD
=======
        self._spotify_client = None
        self.remaining_tracks = None
        self.cookie_file = None

    @property
    def spotify_client(self):
        """Lazy initialization of Spotify client"""
        if self._spotify_client is None:
            self._spotify_client = SpotifyClient()
        return self._spotify_client
>>>>>>> a1187e1 (cil)

    @staticmethod
    def _get_browser_cookies():
        """Get cookies from browser profiles"""
        try:
            # Create a temporary cookie file
            cache_dir = os.path.join(os.getcwd(), '.cache')
            os.makedirs(cache_dir, exist_ok=True)
            cache_path = os.path.join(cache_dir, 'youtube_cookies.txt')
            print(f"[DEBUG] Using cookie cache path: {cache_path}")

            # Try to extract cookies from different browsers
            browsers = ['chrome', 'firefox', 'edge', 'safari', 'opera']
            for browser in browsers:
                try:
                    print(f"[DEBUG] Attempting to extract cookies from {browser}")
                    subprocess.run(
                        ['yt-dlp', '--cookies-from-browser', browser, '-o', cache_path],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
                        print(f"[DEBUG] Successfully extracted cookies from {browser}")
                        return cache_path
                except Exception as e:
                    print(f"[WARNING] Failed to extract cookies from {browser}: {str(e)}")
                    continue

            print("[WARNING] Could not extract cookies from any browser")
            return None

        except Exception as e:
            print(f"[ERROR] Error in cookie extraction: {str(e)}")
            return None

    @classmethod
    async def create_source(cls, query):
        """Create a music source from a URL or search query"""
<<<<<<< HEAD
        # YouTube DL options
=======
        formats = [
            'bestaudio/best',
            'bestaudio[ext=m4a]/bestaudio/best',
            'worstaudio/worst'  # Last resort
        ]

>>>>>>> a1187e1 (cil)
        ydl_opts = {
            'format': formats[0],  # Start with best quality
            'noplaylist': True,
            'quiet': False,  # Enable output for debugging
            'no_warnings': False,  # Show warnings for debugging
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
            }],
            'skip_download': True,
            'no_color': True,
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'extract_audio': True,
            'nocheckcertificate': True,
            'prefer_insecure': True,
            'age_limit': None,
            'format_sort': ['abr', 'asr', 'proto', 'ext'],
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_skip': ['js', 'configs', 'webpage']
                }
            }
        }

<<<<<<< HEAD
        # Determine if query is a URL or search term
        if not re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', query):
            query = f"ytsearch:{query}"

        try:
            # Test FFmpeg installation
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
                print("[DEBUG] FFmpeg is installed and accessible")
            except Exception as e:
                print(f"[ERROR] FFmpeg test failed: {str(e)}")
                raise Exception("FFmpeg is not properly installed")
=======
        # Try to get cookies from browser
        cookie_file = cls._get_browser_cookies()
        if cookie_file:
            ydl_opts['cookiefile'] = cookie_file
            print("[DEBUG] Using browser cookies for authentication")

        try:
            # Convert YouTube Music URLs to regular YouTube URLs
            if 'music.youtube.com' in query:
                query = query.replace('music.youtube.com', 'youtube.com')
                print(f"[DEBUG] Converted YouTube Music URL to: {query}")
>>>>>>> a1187e1 (cil)

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"[DEBUG] Extracting info for: {query}")
                info = ydl.extract_info(query, download=False)

<<<<<<< HEAD
                if 'entries' in info:
                    info = info['entries'][0]

                print(f"[DEBUG] Successfully extracted video info:")
                print(f"[DEBUG] Title: {info.get('title')}")
                print(f"[DEBUG] Format ID: {info.get('format_id')}")
                print(f"[DEBUG] URL: {info.get('url')}")
                print(f"[DEBUG] Ext: {info.get('ext')}")
=======
            if spotify_match:
                return await cls._handle_spotify_url(query, ydl_opts)
            else:
                if not re.match(r'http[s]?://', query):
                    search_query = f"ytsearch:{query}"
                    print(f"[DEBUG] Processing as search query: {search_query}")
                    return await cls._create_youtube_source(search_query, ydl_opts, formats)
                else:
                    print(f"[DEBUG] Processing as direct URL: {query}")
                    return await cls._create_youtube_source(query, ydl_opts, formats)
>>>>>>> a1187e1 (cil)

                return MusicSource(
                    source_url=info.get('url'),
                    title=info.get('title')
                )
        except Exception as e:
            print("[ERROR] Error in create_source:")
            print(traceback.format_exc())
            raise Exception(f"Failed to process source: {str(e)}")

<<<<<<< HEAD
=======
    @classmethod
    async def _handle_spotify_url(cls, query, ydl_opts):
        """Handle Spotify URLs and convert to YouTube sources"""
        try:
            spotify_client = SpotifyClient()
            content_type = spotify_client.get_content_type(query)

            if content_type == 'playlist':
                tracks = await spotify_client.get_playlist_tracks(query)
                if not tracks:
                    raise Exception("No playable tracks found in playlist")

                first_track = tracks[0]
                if not first_track or not first_track.get('search_query'):
                    raise Exception("Invalid track data in playlist")

                source = await cls._create_youtube_source(first_track['search_query'], ydl_opts)
                source.remaining_tracks = tracks[1:]
                return source

            elif content_type == 'album':
                tracks = await spotify_client.get_album_tracks(query)
                if not tracks:
                    raise Exception("No playable tracks found in album")

                first_track = tracks[0]
                if not first_track or not first_track.get('search_query'):
                    raise Exception("Invalid track data in album")

                source = await cls._create_youtube_source(first_track['search_query'], ydl_opts)
                source.remaining_tracks = tracks[1:]
                return source

            else:  # Single track
                track_info = await spotify_client.get_track_info(query)
                if not track_info or not track_info.get('search_query'):
                    raise Exception("Failed to get track information")
                return await cls._create_youtube_source(track_info['search_query'], ydl_opts)

        except Exception as e:
            print(f"[ERROR] Spotify processing error: {str(e)}")
            print(traceback.format_exc())
            raise Exception(f"Failed to process Spotify content: {str(e)}")

    @staticmethod
    async def _create_youtube_source(query, ydl_opts, formats):
        """Create a YouTube source with retries and format fallback"""
        last_error = None
        format_index = 0

        while format_index < len(formats):
            try:
                ydl_opts['format'] = formats[format_index]
                print(f"[DEBUG] Trying format: {formats[format_index]}")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=False)
                    if not info:
                        raise Exception("No results found")

                    if 'entries' in info:
                        if not info['entries']:
                            raise Exception("No matching songs found")
                        info = info['entries'][0]

                    if not info.get('url'):
                        raise Exception("No valid URL found in the extracted info")

                    # Try to verify URL
                    try:
                        response = requests.head(info['url'], timeout=5)
                        if response.status_code != 200:
                            raise Exception(f"URL verification failed with status code: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        print(f"[WARNING] URL verification warning (continuing anyway): {str(e)}")

                    title = info.get('title', 'Unknown Title')
                    print(f"[DEBUG] Successfully extracted info for: {title}")

                    return MusicSource(source_url=info['url'], title=title)

            except Exception as e:
                last_error = str(e)
                print(f"[WARNING] Format {formats[format_index]} failed: {last_error}")
                format_index += 1
                if format_index < len(formats):
                    print(f"[DEBUG] Trying next format option: {formats[format_index]}")
                    continue
                else:
                    print("[ERROR] All format options exhausted")
                    raise Exception(f"Failed to process video with all format options. Last error: {last_error}")

>>>>>>> a1187e1 (cil)
    async def get_audio(self):
        """Get the audio stream for this source"""
        try:
            print(f"[DEBUG] Creating FFmpeg audio source for: {self.title}")
            print(f"[DEBUG] Source URL: {self.source_url}")

            # FFmpeg options for optimal streaming
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn -b:a 128k'  # Set specific audio bitrate
            }

            # Create and test FFmpeg audio source
            audio_source = discord.FFmpegPCMAudio(
                self.source_url,
                **ffmpeg_options
            )
            print("[DEBUG] FFmpeg audio source created successfully")
            return audio_source

        except Exception as e:
            print("[ERROR] Error in get_audio:")
            print(traceback.format_exc())
            raise Exception(f"Failed to create audio source: {str(e)}")