import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration with all required intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guilds = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user.name}')
    try:
        # Sync slash commands
        print("Syncing slash commands...")
        await bot.tree.sync()
        print("Slash commands synced successfully")

        # Load music cog
        await bot.load_extension('cogs.music')
        print("Music cog loaded successfully")
    except Exception as e:
        print(f"Failed to initialize bot: {e}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found! Use /help to see available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    else:
        print(f"Error: {error}")  # Log the error for debugging
        await ctx.send(f"An error occurred: {str(error)}")

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("No Discord token found in .env file")
    bot.run(token)