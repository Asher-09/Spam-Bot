import discord
from discord.ext import commands
import asyncio
import os
import re
import platform
import psutil
from datetime import datetime, timezone
import sys

intents = discord.Intents.all()
owner_ids = [707111534689648760, 875659025210040380]
ALLOWED_USER_IDS = [1169071612960710666, 707111534689648760]

react_mode = {'enabled': False, 'emoji': None}
timers = {}

start_time = datetime.now(timezone.utc)

def load_tokens(file_path="tokens.txt"):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} does not exist. Add one bot token per line.")
        exit(1)

    with open(file_path, "r") as file:
        tokens = [line.strip() for line in file if line.strip()]
    
    if not tokens:
        print(f"Error: No tokens found in {file_path}.")
        exit(1)
    
    return tokens

def generate_invite_link(bot_user_id, permissions):
    """Generates a Discord invite link for the bot with specified permissions."""
    base_url = "https://discord.com/oauth2/authorize"
    params = f"?client_id={bot_user_id}&permissions={permissions}&scope=bot"
    return base_url + params

async def spam_event(channel, message, amount):
    for _ in range(amount):
        await channel.send(message)
        await asyncio.sleep(0.22)

async def send_about_embed(bot, msg):
    try:
        python_version = platform.python_version()
        uptime = datetime.now(timezone.utc) - start_time
        hours, rem = divmod(int(uptime.total_seconds()), 3600)
        mins, secs = divmod(rem, 60)
        latency = round(bot.latency * 1000, 2)
        memory = round(psutil.virtual_memory().used / 1024 / 1024, 2)
        cpu = round(psutil.cpu_percent(interval=1), 2)

        embed = discord.Embed(
            title="🤖 About Nix Bot",
            description="Advanced multi-token utility selfbot built with `discord.py`. ",
            color=discord.Color.blue()
        )
        embed.add_field(name="📌 Python Version", value=python_version, inline=True)
        embed.add_field(name="📶 Latency", value=f"{latency} ms", inline=True)
        embed.add_field(name="🧠 Uptime", value=f"{hours}h {mins}m {secs}s", inline=True)
        embed.add_field(name="🖥️ RAM Usage", value=f"{memory} MB", inline=True)
        embed.add_field(name="⚙️ CPU Usage", value=f"{cpu}%", inline=True)
        embed.add_field(name="🔧 Features", value="Spamming, Embeds, Auto-Reacts, Timers, Crash/Restart, and more.", inline=False)
        embed.set_footer(text="Bot created by Nix • Stay tuned for updates.")

        await msg.channel.send(embed=embed)
    except Exception as e:
        print(f"Error sending about embed: {e}")
        try:
            await msg.channel.send(f"❌ An error occurred: {e}")
        except Exception as error:
            print(f"Failed to send error message: {error}")


async def dm_event(ctx, user, message, amount):
    """Sends a specified number of DM messages to a user."""
    try:
        # Split the amount into manageable batches (e.g., 50 messages per batch)
        batch_size = 50
        total_batches = amount // batch_size
        remaining_messages = amount % batch_size

        # Send in batches
        for batch in range(total_batches):
            for _ in range(batch_size):
                await user.send(message)
            await asyncio.sleep(2)  # Sleep after sending each batch to avoid rate limit

        # Handle remaining messages if any
        for _ in range(remaining_messages):
            await user.send(message)

        await ctx.channel.send(f"✅ Successfully sent {amount} DMs to {user.display_name}.", delete_after=10)
        print(f"DM Event Complete: Sent {amount} messages to {user.display_name} (ID: {user.id}).")

    except Exception as e:
        await ctx.channel.send(f"❌ Failed to send DM to {user.display_name}. Error: {e}", delete_after=10)
        print(f"DM Event Error: Could not send DMs to {user.display_name} (ID: {user.id}). Error: {e}")
async def timer_event(ctx, duration, reason):
    await asyncio.sleep(duration)
    embed = discord.Embed(
        title="⏰ Time's Up!",
        description=f"Hey {ctx.author.mention}, your timer for `{reason}` has finished!",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, delete_after=10)
    timers.pop(ctx.guild.id, None)

async def crash_function(msg):
    """Stops all timers and disables react mode."""
    try:
        if msg.guild and msg.guild.id in timers:
            timers[msg.guild.id].cancel()
            timers.pop(msg.guild.id, None)

        react_mode['enabled'] = False
        react_mode['emoji'] = None

        await msg.channel.send("💥 All functions stopped. Reacts and timers cleared.")
        print(f"[CRASH] Crash executed by {msg.author} ({msg.author.id})")

    except Exception as e:
        await msg.channel.send(f"❌ Crash failed: {e}")
        print(f"[ERROR] Crash failure: {e}")



async def espam_event(ctx, amount, message_text, author_name):
    """Sends a spam embed message with a title, image, and footer."""
    embed = discord.Embed(
        title="Nix",
        description=message_text,
        color=discord.Color.blue()
    )
    embed.set_image(url="https://media.discordapp.net/attachments/1250724106014298234/1337408476338458754/BlueN.gif?ex=681d5474&is=681c02f4&hm=2ad101e5f42016b557d7c187c4f00f904c322e671a4561d863856ee6a5126482&=&width=518&height=560")
    embed.set_footer(text=f"Requested by {author_name}")

    for _ in range(amount):
        await ctx.channel.send(embed=embed)
        await asyncio.sleep(0.22)
        
async def restart_bot(ctx,bot , bot_script_name="main.py"):
    """Restarts the bot (owner only)."""
    try:
        if ctx.author.id not in owner_ids:
            await ctx.send("🚫 You do not have permission to restart the bot.", delete_after=5)
            return

        await ctx.send("♻️ Restarting the bot...")
        print(f"[RESTART] Bot restart initiated by {ctx.author} ({ctx.author.id}).")

        await bot.close()  # Graceful shutdown

        # Optional restart logic (only works if launched from CLI)
        os.execl(sys.executable, sys.executable, bot_script_name)

    except Exception as e:
        await ctx.send(f"❌ Restart failed: {e}", delete_after=5)
        print(f"[ERROR] Restart failure: {e}")

async def is_owner_or_admin(user_id):
    """Check if the user is a bot owner or admin."""
    return user_id in ALLOWED_USER_IDS


async def handle_commands(bot, msg):
    content = msg.content.strip()

    try:
        if content.startswith('*spam '):
            parts = content[len('*spam '):].split(maxsplit=1)
            if len(parts) != 2:
                await msg.channel.send("Usage: *spam <amount> <message>", delete_after=5)
                return

            amount, message_text = parts
            try:
                amount = int(amount)
                if msg.author.id not in ALLOWED_USER_IDS:
                    await msg.channel.send("You do not have permission to use this command.", delete_after=5)
                    return
                await spam_event(msg.channel, message_text, amount)
            except ValueError:
                await msg.channel.send("Invalid amount. It must be a number.", delete_after=5)

        elif content.startswith("*eflood"):
            await msg.delete(delay=5)

            if msg.author.id not in owner_ids and msg.author.id not in ALLOWED_USER_IDS:
                return await msg.channel.send("❌ You don't have permission to use this command.", delete_after=5)

            parts = content.split()
            if len(parts) < 3:
                return await msg.channel.send("Usage: `*eflood <user> <amount> [message]`", delete_after=5)

            user_arg = parts[1]
            try:
                amount = int(parts[2])
            except ValueError:
                return await msg.channel.send("❌ Amount must be a number.", delete_after=5)

            text_to_flood = " ".join(parts[3:]) if len(parts) > 3 else "Flooded By Nix"

            target_user = None

            # Try mention first
            if msg.mentions:
                target_user = msg.mentions[0]
            else:
                try:
                    # Try user ID
                    target_user = await msg.client.fetch_user(int(user_arg))
                except:
                    for guild in msg.client.guilds:
                        member = discord.utils.find(lambda m: m.name.lower() == user_arg.lower(), guild.members)
                        if member:
                            target_user = member
                            break

            if not target_user:
                return await msg.channel.send("❌ Couldn't find the user.", delete_after=5)

            embed = discord.Embed(
                title="𝓝𝓲𝔁",
                description=text_to_flood,
                color=discord.Color.blue()
            )
            embed.set_image(url="https://media.discordapp.net/attachments/1250724106014298234/1337408476338458754/BlueN.gif?ex=681d5474&is=681c02f4&hm=2ad101e5f42016b557d7c187c4f00f904c322e671a4561d863856ee6a5126482&=&width=518&height=560")
            embed.set_footer(text=f"Flooded by {msg.author}", icon_url=msg.author.display_avatar.url)

            tasks = [target_user.send(embed=embed) for _ in range(amount)]

            try:
                await asyncio.gather(*[target_user.send(embed=embed) for _ in range(amount)])
                await msg.channel.send(f"✅ Successfully flooded **{target_user}**'s DMs `{amount}` times.", delete_after=5)
            except Exception as e:
                await msg.channel.send(f"❌ Failed to flood: {e}", delete_after=5)


        

        elif content.startswith('*flood '):
           parts = content[len('*flood '):].split(maxsplit=2)
            
           if len(parts) != 3:
               await msg.channel.send("Usage: *flood <user> <amount> <message>", delete_after=5)
               return

           user_id_or_mention, amount, message_text = parts
           try:
               amount = int(amount)
               user_id_or_mention = re.sub(r"[<@!>]", "", user_id_or_mention)
               user_id = int(user_id_or_mention)

               if msg.author.id not in ALLOWED_USER_IDS:
                   await msg.channel.send("You do not have permission to use this command.", delete_after=5)
                   return

               # Get the user by ID or mention, ensure to check both member and user object
               user = msg.guild.get_member(user_id) or bot.get_user(user_id)
               if user:
                   await dm_event(msg, user, message_text, amount)
               else:
                   await msg.channel.send("User not found. Ensure the user is in the server or you have the correct ID.", delete_after=5)
           
           except ValueError:
               await msg.channel.send("Invalid user ID or amount. Both must be numbers.", delete_after=5)
           except Exception as e:
               await msg.channel.send(f"An unexpected error occurred: {e}", delete_after=5)

        elif content.startswith('*invite'):
            try:
                permissions = 2048 
                invite_link = generate_invite_link(msg.guild.me.id, permissions)
                await msg.channel.send(f"Invite Link: {invite_link}")
            except Exception as e:
                await msg.channel.send(f"An error occurred while generating the invite link: {e}")

        elif content.startswith('*react '):
            try:
                parts = content[len('*react '):].split(maxsplit=1)
                if len(parts) < 1:
                    await msg.channel.send("Usage: *react <on/off> <emoji>", delete_after=5)
                    return

                option = parts[0].lower()
                emoji = parts[1] if len(parts) > 1 else None
                if option == "on" and emoji:
                    react_mode['enabled'] = True
                    react_mode['emoji'] = emoji
                    await msg.channel.send(f"Reaction mode enabled with emoji {emoji}.")
                elif option == "off":
                    react_mode['enabled'] = False
                    react_mode['emoji'] = None
                    await msg.channel.send("Reaction mode disabled.")
                else:
                    await msg.channel.send("Invalid option. Use 'on' or 'off'.", delete_after=5)
            except Exception as e:
                await msg.channel.send(f"An error occurred in reaction mode: {e}", delete_after=5)

        elif content.startswith('*time '):
            try:
                parts = content[len('*time '):].split(maxsplit=1)
                if len(parts) < 1:
                    await msg.channel.send("Usage: *time <time> [reason]", delete_after=5)
                    return

                time, reason = parts[0], parts[1] if len(parts) > 1 else "No reason provided"
                match = re.match(r'(\d+)([smhd])', time)
                if match:
                    amount, unit = match.groups()
                    seconds = int(amount) * {"s": 1, "m": 60, "h": 3600, "d": 86400}[unit]
                    if msg.guild.id in timers:
                        await msg.channel.send("A timer is already active.", delete_after=5)
                        return

                    timers[msg.guild.id] = asyncio.create_task(timer_event(msg, seconds, reason))
                else:
                    await msg.channel.send("Invalid time format. Use <number><s/m/h/d>.", delete_after=5)

            except Exception as e:
                await msg.channel.send(f"An error occurred while setting the timer: {e}", delete_after=5)

        elif content.startswith('*stoptimer'):
            try:
                if msg.guild.id in timers:
                    timers[msg.guild.id].cancel()
                    timers.pop(msg.guild.id, None)
                    await msg.channel.send("Timer has been stopped.", delete_after=5)
                else:
                    await msg.channel.send("No active timer to stop.", delete_after=5)
            except Exception as e:
                await msg.channel.send(f"An error occurred while stopping the timer: {e}", delete_after=5)

        elif content.startswith('*crash'):
            try:
                if msg.author.id in owner_ids:
                    await crash_function(msg)
                else:
                    await msg.channel.send("You do not have permission to stop the functions.", delete_after=5)
            except Exception as e:
                await msg.channel.send(f"An error occurred while stopping the functions: {e}", delete_after=5)

        elif content.startswith('*espam'):
            try:
                parts = content.split(maxsplit=2)
                if len(parts) < 2:
                    await msg.channel.send("Usage: *espam <amount> [message]", delete_after=5)
                    return

                amount = int(parts[1])
                text = parts[2] if len(parts) > 2 else "Spammed by Nix"

                if msg.author.id not in ALLOWED_USER_IDS and msg.author.id not in owner_ids:
                    await msg.channel.send("You do not have permission to use this command.", delete_after=5)
                    return

                await espam_event(msg, amount, text, msg.author.name)

            except ValueError:
                await msg.channel.send("Invalid amount. It must be a number.", delete_after=5)
            except Exception as e:
                await msg.channel.send(f"An error occurred while executing espam: {e}", delete_after=5)

        elif content.startswith('*restart'):
            try:
                if not is_owner_or_admin(msg.author.id):
                    return await msg.channel.send("❌ Only bot owners or admins can use this command.")
                await msg.channel.send("🔁 Restarting bot...")
                os.execv(sys.executable, ['python'] + sys.argv)
            except Exception as e:
                await msg.channel.send(f"An error occurred while restarting: {e}", delete_after=5)

        elif content.startswith('*uptime'):
            try:
                now = datetime.now(timezone.utc)
                delta = now - start_time
                hours, remainder = divmod(int(delta.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                await msg.channel.send(f"⏱️ Uptime: `{hours}h {minutes}m {seconds}s`")
            except Exception as e:
                await msg.channel.send(f"An error occurred while calculating uptime: {e}", delete_after=5)

        elif content.startswith('*help'):
            try:
                embed = discord.Embed(
                    title="🧠 Nix Bot Help",
                    description="Available Commands:",
                    color=discord.Color.purple()
                )
                embed.add_field(name="*espam <amount> [text]", value="Embed spam with image/banner (Admins/Owners only).", inline=False)
                embed.add_field(name="*spam <amount> <message>", value="Sends message multiple times.", inline=False)
                embed.add_field(name="*flood <user> <amount> <message>", value="Floods a user's ID.", inline=False)
                embed.add_field(name="*invite", value="Generates a bot invite link.", inline=False)
                embed.add_field(name="*react on/off <emoji>", value="Enables or disables auto-reacting with an emoji.", inline=False)
                embed.add_field(name="*time <10s/10m/1h> [reason]", value="Starts a timer.", inline=False)
                embed.add_field(name="*stoptimer", value="Stops the current timer.", inline=False)
                embed.add_field(name="*crash", value="Stops all timers and reaction mode (Admins only).", inline=False)
                embed.add_field(name="*restart", value="Restarts the bot (Admins only).", inline=False)
                embed.add_field(name="*ping", value="Shows bot latency.", inline=False)
                embed.add_field(name="*uptime", value="Shows how long the bot has been online.", inline=False)
                embed.add_field(name="*about", value="Shows info about this bot.", inline=False)
                embed.add_field(name="*eflood", value="Floods a user by embed.", inline=False)
                embed.set_footer(text="Bot developed by Nix • More coming soon!")
                await msg.channel.send(embed=embed)

            except Exception as e:
                await msg.channel.send(f"An error occurred while generating help: {e}", delete_after=5)

        elif content.startswith('*about'):
            try:
                await send_about_embed(bot, msg)
            except Exception as e:
                await msg.channel.send(f"An error occurred while showing bot info: {e}", delete_after=5)
    except Exception as e:
            await msg.channel.send(f"An unexpected error occurred while processing your command: {e}", delete_after=5)


async def start_bot(token):
    global start_time
    start_time = datetime.now(timezone.utc)   # Initialize start_time when the bot starts
    bot = commands.Bot(command_prefix='*', intents=intents, help_command=None)

    @bot.event
    async def on_ready():
        print(f'{bot.user} has came to life sucessfully!! ✅ ')

    @bot.event
    async def on_message(msg):
        if msg.author.bot:
            return
        try:
            await handle_commands(bot, msg)  # Pass the bot to handle_commands
        except Exception as e:
            print(f"[ERROR] in handle_commands: {e}")
        await bot.process_commands(msg)

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Usage error. The command is missing required arguments.", delete_after=5)
        else:
            await ctx.send(f"An error occurred: {str(error)}", delete_after=5)

    await bot.start(token)

if __name__ == "__main__":
    tokens = load_tokens()
    loop = asyncio.get_event_loop()

    try:
        for token in tokens:
            loop.create_task(start_bot(token))  # Ensure each token is used
        loop.run_forever()
    except KeyboardInterrupt:
        print("Shutting down bots...")
        loop.run_until_complete(asyncio.gather(*asyncio.all_tasks()))


