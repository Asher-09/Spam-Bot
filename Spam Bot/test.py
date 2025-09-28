import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True  
bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_ID = 1363708405973385220 

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command()
async def assignrole(ctx, member: discord.Member = None):
    """
    Assign a role to a user by their mention or user ID.
    Usage: !assignrole <@user> or <user_id>
    """

    if member is None:
        await ctx.send("Please mention a user or provide their user ID.")
        return

    try:
        role = discord.utils.get(ctx.guild.roles, id=ROLE_ID)

        if role is None:
            await ctx.send("The role could not be found.")
            return

        await member.add_roles(role)
        await ctx.send(f"Assigned the role `{role.name}` to {member.mention}.")
    
    except discord.DiscordException as e:
        await ctx.send(f"An error occurred: {str(e)}")

bot.run('TOKEN')

