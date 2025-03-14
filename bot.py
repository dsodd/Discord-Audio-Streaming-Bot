import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
<<<<<<< HEAD
=======
import traceback
import asyncio
from logger_config import logger  # Import the shared logger configuration

# Example logging
logger.info("Bot script started.")

>>>>>>> f43f3bb (Applying some come that is confirmed to b working)

# Load environment variables
load_dotenv()

<<<<<<< HEAD
# Bot configuration with all required intents
=======
# Get application ID
APPLICATION_ID = os.getenv('APPLICATION_ID')
if not APPLICATION_ID:
    raise ValueError("No APPLICATION_ID found in .env file")

# Add debug logging for token
token = os.getenv('DISCORD_TOKEN')
if token:
    logger.info("Discord token loaded successfully")
    # Log a masked version of the token for verification (showing only first 10 chars)
    logger.info(f"Token starts with: {token[:10]}...")
else:
    logger.error("No Discord token found in .env file")
    raise ValueError("No Discord token found in .env file")

# Bot configuration with all required intents and permissions
>>>>>>> efedcce (Testing branch merge)
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
        logger.info("Setting up bot hooks...")
        try:
            await self.load_extension('cogs.music')
            logger.info("Bot hooks setup complete")
        except Exception as e:
            logger.error(f"Failed to load music extension: {str(e)}")
            logger.error(traceback.format_exc())
            raise

# Create bot instance with required permissions and multiple prefixes
bot = MusicBot(
    command_prefix=['!'],  # Support ! as the prefix (more can be added ['!', '?'], example)
    intents=intents,
    application_id=APPLICATION_ID,
    help_command=None  # Disable default help command to use our custom one
)
>>>>>>> 0dcaccf (Update)

@bot.event
async def on_ready():
    logger.info(f'Bot is ready! Logged in as {bot.user.name}')
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
        logger.info("Currently registered commands:")
        for command in bot.tree.get_commands():
            logger.info(f"- /{command.name}")

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
                use_application_commands=True
            ),
            scopes=['bot', 'applications.commands']
        )
        logger.info(f"Invite the bot using this link to ensure proper permissions:")
        logger.info(invite_link)

        # Sync slash commands globally with detailed logging
        logger.info("Starting global command sync...")
        try:
            existing_commands = await bot.tree.fetch_commands()
            logger.info(f"Found {len(existing_commands)} existing global commands")

            commands = await bot.tree.sync()
            logger.info(f"Successfully synced {len(commands)} commands globally:")
            for cmd in commands:
                logger.info(f"- /{cmd.name}: {cmd.description}")

            if len(commands) == 0:
                logger.warning("No commands were synced. This might indicate a registration issue.")

        except discord.errors.HTTPException as e:
            if e.code == 429:  # Rate limit error
                logger.warning("Rate limited while syncing commands. Waiting and retrying...")
                await asyncio.sleep(10)
                commands = await bot.tree.sync()
                logger.info(f"Retry successful! Registered {len(commands)} commands")
            else:
                logger.error(f"HTTP Exception during sync: {e.code} - {e.text}")
                raise e
        except Exception as e:
            logger.error(f"Unexpected error during command sync: {str(e)}")
            logger.error(traceback.format_exc())
            raise e

>>>>>>> 0dcaccf (Update)
    except Exception as e:
<<<<<<< HEAD
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
=======
        logger.error(f"Failed to initialize bot:")
        logger.error(traceback.format_exc())
        raise e

@bot.event
async def on_command_error(ctx, error):
    """Handle traditional command errors with detailed error messages"""
    try:
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found! Use /help or !help to see available commands.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command!")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command can't be used in private messages!")
        elif isinstance(error, commands.BotMissingPermissions):
            permissions = '\n'.join(perm for perm, value in error.missing_permissions.items() if value)
            await ctx.send(f"I'm missing the following permissions to execute this command:\n{permissions}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing required argument: {error.param.name}")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"Invalid argument provided. Please check the command usage with !help")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.")
        else:
            logger.error(f"Unhandled command error: {str(error)}")
            logger.error(traceback.format_exc())
            await ctx.send(f"An unexpected error occurred. Please try again later.\nError: {str(error)}")
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}")
        logger.error(traceback.format_exc())
>>>>>>> f43f3bb (Applying some come that is confirmed to b working)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    """Handle slash command errors with detailed error messages"""
    try:
        if isinstance(error, discord.app_commands.CommandNotFound):
            await interaction.response.send_message("Command not found! Use /help to see available commands.")
        elif isinstance(error, discord.app_commands.MissingPermissions):
            await interaction.response.send_message("You don't have permission to use this command!")
        elif isinstance(error, discord.app_commands.BotMissingPermissions):
            permissions = '\n'.join(perm for perm, value in error.missing_permissions.items() if value)
            await interaction.response.send_message(f"I'm missing the following permissions:\n{permissions}")
        elif isinstance(error, discord.app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
            )
        elif isinstance(error, discord.app_commands.TransformerError):
            await interaction.response.send_message(
                f"Invalid argument provided. Please check the command usage with /help"
            )
        else:
            logger.error(f"Unhandled app command error: {str(error)}")
            logger.error(traceback.format_exc())
            await interaction.response.send_message(
                f"An unexpected error occurred. Please try again later.\nError: {str(error)}"
            )
    except Exception as e:
        logger.error(f"Error in app command error handler: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("No Discord token found in .env file")
<<<<<<< HEAD
    bot.run(token)
=======

<<<<<<< HEAD
<<<<<<< HEAD
    print("[DEBUG] Starting bot with enhanced logging...")
<<<<<<< HEAD
    bot.run(token)



## Made by dsod
## Discord: dsodd
>>>>>>> 84b6b34 (Some final fixes)
=======
    bot.run(token)
>>>>>>> 0dcaccf (Update)
=======
    logger.info("Starting bot with enhanced error handling...")
=======
>>>>>>> 523edc9 (yes)
    try:
        bot.run(token)
    except discord.errors.LoginFailure:
        logger.error("Failed to login. Please check your Discord token.")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        logger.error(traceback.format_exc())
>>>>>>> f43f3bb (Applying some come that is confirmed to b working)
