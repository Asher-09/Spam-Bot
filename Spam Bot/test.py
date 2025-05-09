import discord
from discord.ext import commands

# Create an instance of the bot
intents = discord.Intents.default()
intents.members = True  # Enable the member-related events
bot = commands.Bot(command_prefix="!", intents=intents)

# Replace this with your actual role ID
ROLE_ID = 1363708405973385220  # Example: Role ID to assign

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command()
async def assignrole(ctx, member: discord.Member = None):
    """
    Command to assign a role to a user by their mention or user ID.
    Usage: !assignrole <@user> or !assignrole <user_id>
    """

    # If the member is not mentioned, try to fetch by user ID
    if member is None:
        await ctx.send("Please mention a user or provide their user ID.")
        return

    try:
        # Fetch the role by ID
        role = discord.utils.get(ctx.guild.roles, id=ROLE_ID)

        if role is None:
            await ctx.send("The role could not be found.")
            return

        # Assign the role to the user
        await member.add_roles(role)
        await ctx.send(f"Assigned the role `{role.name}` to {member.mention}.")
    
    except discord.DiscordException as e:
        await ctx.send(f"An error occurred: {str(e)}")

# Run the bot with your token
bot.run('MTM2MzMzMDYzMzY2NDgyMzM4Nw.GYTxss.TAMIzs5TujOGa6oufI2pYoHSPj6uoGUcyn-NpY')
