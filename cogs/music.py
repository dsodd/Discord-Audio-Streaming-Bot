import discord
from discord.ext import commands
from utils.music_source import MusicSource
from utils.queue_manager import QueueManager
import asyncio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue_managers = {}  # Dict to store queue managers for each guild

    def get_queue_manager(self, guild_id):
        if guild_id not in self.queue_managers:
            self.queue_managers[guild_id] = QueueManager()
        return self.queue_managers[guild_id]

    @commands.command()
    async def play(self, ctx, *, query: str):
        """Play music from a given URL or search query"""
        if not ctx.author.voice:
            return await ctx.send("You need to be in a voice channel!")

        queue_manager = self.get_queue_manager(ctx.guild.id)
        
        try:
            # Connect to voice channel if not already connected
            if not ctx.voice_client:
                await ctx.author.voice.channel.connect()
            
            # Process the query and get the source
            music_source = await MusicSource.create_source(query)
            
            # Add to queue
            queue_manager.add(music_source)
            await ctx.send(f"Added to queue: {music_source.title}")

            # Start playing if not already playing
            if not ctx.voice_client.is_playing():
                await self.play_next(ctx)

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

    async def play_next(self, ctx):
        """Play the next song in the queue"""
        queue_manager = self.get_queue_manager(ctx.guild.id)
        
        if queue_manager.is_empty():
            await ctx.send("Queue is empty!")
            return

        source = queue_manager.get_next()
        ctx.voice_client.play(
            await source.get_audio(),
            after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next(ctx), self.bot.loop
            ).result() if e is None else print(f'Player error: {e}')
        )
        await ctx.send(f"Now playing: {source.title}")

    @commands.command()
    async def queue(self, ctx):
        """Display the current queue"""
        queue_manager = self.get_queue_manager(ctx.guild.id)
        if queue_manager.is_empty():
            await ctx.send("Queue is empty!")
            return

        queue_list = queue_manager.get_queue()
        queue_text = "\n".join(
            f"{i+1}. {song.title}" for i, song in enumerate(queue_list)
        )
        await ctx.send(f"Current queue:\n{queue_text}")

    @commands.command()
    async def pause(self, ctx):
        """Pause or resume the current song"""
        if not ctx.voice_client:
            return await ctx.send("Not connected to a voice channel!")

        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Playback paused")
        elif ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Playback resumed")
        else:
            await ctx.send("Nothing is playing!")

    @commands.command()
    async def stop(self, ctx):
        """Stop playback and clear the queue"""
        if not ctx.voice_client:
            return await ctx.send("Not connected to a voice channel!")

        queue_manager = self.get_queue_manager(ctx.guild.id)
        queue_manager.clear()
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped playback and cleared queue")

async def setup(bot):
    await bot.add_cog(Music(bot))
