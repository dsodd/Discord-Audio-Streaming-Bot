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

<<<<<<< HEAD
bot = commands.Bot(command_prefix='/', intents=intents)
=======
class MusicBot(commands.Bot):
    async def setup_hook(self):
        print("[DEBUG] Setting up bot hooks...")
        await self.load_extension('cogs.music')
        print("[DEBUG] Bot hooks setup complete")

# Create bot instance with required permissions and multiple prefixes
bot = MusicBot(
    command_prefix=['/', '!'],  # Support both / and ! prefixes
    intents=intents,
    application_id=APPLICATION_ID,
    help_command=None  # Disable default help command to use our custom one
)
>>>>>>> 0dcaccf (Update)

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user.name}')
    try:
<<<<<<< HEAD
        # Sync slash commands
        print("Syncing slash commands...")
        await bot.tree.sync()
        print("Slash commands synced successfully")

        # Load music cog
        await bot.load_extension('cogs.music')
        print("Music cog loaded successfully")
=======
        # Log all registered commands before sync
        print("\n[DEBUG] Currently registered commands:")
        for command in bot.tree.get_commands():
            print(f"- /{command.name}")

        # Generate bot invite link with proper permissions
        invite_link = discord.utils.oauth_url(
            APPLICATION_ID,
            permissions=discord.Permissions(
                send_messages=True,
                connect=True,
                speak=True,
                use_voice_activation=True,
                add_reactions=True,
                attach_files=True,
                read_messages=True,
                read_message_history=True,
                use_application_commands=True  # Important for slash commands
            ),
            scopes=['bot', 'applications.commands']  # Important: both scopes needed
        )
        print(f"\nInvite the bot using this link to ensure proper permissions:")
        print(invite_link)

        # Sync slash commands globally with detailed logging
        print("\n[DEBUG] Starting global command sync...")
        try:
            existing_commands = await bot.tree.fetch_commands()
            print(f"[DEBUG] Found {len(existing_commands)} existing global commands")

            commands = await bot.tree.sync()
            print(f"[DEBUG] Successfully synced {len(commands)} commands globally:")
            for cmd in commands:
                print(f"- /{cmd.name}: {cmd.description}")

            if len(commands) == 0:
                print("[WARNING] No commands were synced. This might indicate a registration issue.")

        except discord.errors.HTTPException as e:
            if e.code == 429:  # Rate limit error
                print("[DEBUG] Rate limited while syncing commands. Waiting and retrying...")
                await asyncio.sleep(10)  # Wait for rate limit to reset
                commands = await bot.tree.sync()
                print(f"[DEBUG] Retry successful! Registered {len(commands)} commands")
            else:
                print(f"[ERROR] HTTP Exception during sync: {e.code} - {e.text}")
                raise e
        except Exception as e:
            print(f"[ERROR] Unexpected error during command sync: {str(e)}")
            print(traceback.format_exc())
            raise e

>>>>>>> 0dcaccf (Update)
    except Exception as e:
        print(f"Failed to initialize bot: {e}")

@bot.event
async def on_command_error(ctx, error):
    """Handle traditional command errors"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found! Use /help or !help to see available commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command!")
    else:
        print(f"Error: {error}")  # Log the error for debugging
        await ctx.send(f"An error occurred: {str(error)}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    """Handle slash command errors"""
    if isinstance(error, discord.app_commands.CommandNotFound):
        await interaction.response.send_message("Command not found! Use /help or !help to see available commands.")
    elif isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have permission to use this command!")
    else:
        print(f"[ERROR] App command error: {str(error)}")  # Log the error for debugging
        print(traceback.format_exc())
        await interaction.response.send_message(f"An error occurred: {str(error)}")

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("No Discord token found in .env file")
<<<<<<< HEAD
    bot.run(token)
=======

    print("[DEBUG] Starting bot with enhanced logging...")
<<<<<<< HEAD
    bot.run(token)



## Made by dsod
## Discord: dsodd
>>>>>>> 84b6b34 (Some final fixes)
=======
    bot.run(token)
>>>>>>> 0dcaccf (Update)
