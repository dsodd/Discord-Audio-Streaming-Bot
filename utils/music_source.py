import discord
import yt_dlp
import re

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
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        # Determine if query is a URL or search term
        if not re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', query):
            query = f"ytsearch:{query}"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(query, download=False)
                
                if 'entries' in info:
                    info = info['entries'][0]

                return MusicSource(
                    source_url=info['url'],
                    title=info['title']
                )
        except Exception as e:
            raise Exception(f"Failed to process source: {str(e)}")

    async def get_audio(self):
        """Get the audio source for discord.py"""
        return discord.FFmpegPCMAudio(
            self.source_url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn"
        )
