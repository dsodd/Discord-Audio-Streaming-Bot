import discord
from discord import app_commands
from discord.ext import commands
from utils.music_source import MusicSource
from utils.queue_manager import QueueManager
import asyncio
import traceback

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue_managers = {}  # Dict to store queue managers for each guild

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

    async def play(self, interaction: discord.Interaction, query: str):
        """Play music from a given URL or search query"""
        if not interaction.user.voice:
            await interaction.response.send_message("You need to be in a voice channel!")
            return

        queue_manager = self.get_queue_manager(interaction.guild_id)
        await interaction.response.defer()

        try:
            # Connect to voice channel if not already connected
            if not interaction.guild.voice_client:
                try:
                    await interaction.user.voice.channel.connect(timeout=20.0, self_deaf=True)
                    print(f"[DEBUG] Connected to voice channel: {interaction.user.voice.channel.name}")
                except Exception as e:
                    print(f"[ERROR] Failed to connect to voice channel: {str(e)}")
                    await interaction.followup.send("Failed to connect to voice channel. Please try again.")
                    return

            # Process the query and get the source
            print(f"[DEBUG] Processing query: {query}")
            music_source = await MusicSource.create_source(query)
            print(f"[DEBUG] Created music source for: {music_source.title}")

            # Add to queue
            queue_manager.add(music_source)
            await interaction.followup.send(f"Added to queue: {music_source.title}")

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
            return

        queue_list = queue_manager.get_queue()
        queue_text = "\n".join(
            f"{i+1}. {song.title}" for i, song in enumerate(queue_list)
        )
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
            return

        queue_manager = self.get_queue_manager(interaction.guild_id)
        queue_manager.clear()
        interaction.guild.voice_client.stop()
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("Stopped playback and cleared queue")

async def setup(bot):
    await bot.add_cog(Music(bot))