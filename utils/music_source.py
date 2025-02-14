import discord
import yt_dlp
import re
import traceback
import subprocess

class MusicSource:
    def __init__(self, source_url, title):
        self.source_url = source_url
        self.title = title

    @staticmethod
    async def create_source(query):
        """Create a music source from a URL or search query"""
        # YouTube DL options
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': False,  # Enable output for debugging
            'no_warnings': False,  # Show warnings for debugging
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
            }],
        }

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

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"[DEBUG] Extracting info for: {query}")
                info = ydl.extract_info(query, download=False)

                if 'entries' in info:
                    info = info['entries'][0]

                print(f"[DEBUG] Successfully extracted video info:")
                print(f"[DEBUG] Title: {info.get('title')}")
                print(f"[DEBUG] Format ID: {info.get('format_id')}")
                print(f"[DEBUG] URL: {info.get('url')}")
                print(f"[DEBUG] Ext: {info.get('ext')}")

                return MusicSource(
                    source_url=info.get('url'),
                    title=info.get('title')
                )
        except Exception as e:
            print("[ERROR] Error in create_source:")
            print(traceback.format_exc())
            raise Exception(f"Failed to process source: {str(e)}")

    async def get_audio(self):
        """Get the audio source for discord.py"""
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