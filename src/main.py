from discord.ext import commands
import discord
import random as rand
from datetime import timedelta
import urllib.request
import json
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix="!",  # Change to desired prefix
    case_insensitive=True, # Commands aren't case-sensitive
    intents = intents # Set up basic permissions
)

bot.author_id = 270197348691476481  # Change to your discord id

@bot.event
async def on_ready():  # When the bot is ready
    print("I'm in")
    print(bot.user)  # Prints the bot's username and identifier

@bot.command()
async def pong(ctx):
    await ctx.send('pong')

### WarmUp ###

@bot.command()
async def name(ctx): #reply with the name of the user
    await ctx.send(ctx.author.name)

@bot.command()
async def d6(ctx): #random number between 1 and 6
    await ctx.send(rand.randint(1, 6))

@bot.event
async def on_message(message):
    if message.author == discord.Client(intents=intents).user: #check that the author isn't the bot
        return
    if message.content == "Salut tout le monde":
        await message.channel.send(f"Salut tout seul {message.author.mention}")
    await bot.process_commands(message)

### Admin ###

@bot.command()
async def admin(ctx, *, member: discord.Member):
    if ctx.message.author.guild_permissions.administrator: # Vérifie si la personne qui a tapé la commande est un administrateur
        admin_role = discord.utils.get(ctx.guild.roles, name="Administrator") # Obtient le rôle d'administrateur
        if not admin_role:
            admin_role = await ctx.guild.create_role(name="Administrator", permissions=discord.Permissions.all())
        # Ajoute le rôle à la personne mentionnée
        await member.add_roles(admin_role)
        await ctx.send(f"{member.mention} est maintenant administrateur")
    else:
        await ctx.send("Vous n'avez pas la permission d'utiliser cette commande")



catchphrases = [
    "Trop nul!",
    "Génant!",
    "Plus drôle que moi!",
    "Tu m'énerves!",
]

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=catchphrases[rand.randint(0, 3)]):
    if (ctx.message.author.guild_permissions.ban_members):
        try:
            await member.ban(reason=reason)
            await ctx.send(f"{member.mention} a été banni pour ces raisons: {reason}")
        except discord.Forbidden:
            await ctx.send(f"{member.mention} ne peut pas être banni")
    else:
        await ctx.send("Vous n'avez pas la permission d'utiliser cette commande")


flood_monitoring = False # Status du flood monitoring
max_messages = 5 # Quantité de messages maximum
time_frame_minutes = 5 # Durée voulue

@bot.command()
async def flood(ctx):
    global flood_monitoring
    if flood_monitoring:
        flood_monitoring = False
        await ctx.send("Le monitoring est désactivé")
    else:
        flood_monitoring = True
        await ctx.send("Le monitoring est activé")

@bot.event
async def on_message(message):
    if flood_monitoring:
        author = message.author
        if not author.bot:
            messages_in_time_frame = sum(1 for m in bot.cached_messages if m.author == author and m.created_at >= (message.created_at - timedelta(minutes=time_frame_minutes)))
            if messages_in_time_frame > max_messages:
                await message.channel.send(f"{author.mention}, arrête de spam le salon!")
    await bot.process_commands(message)

number_img = 1
with urllib.request.urlopen("https://xkcd.com/info.0.json") as response:
    data = json.loads(response.read().decode())
    number_img = data['num']

@bot.command()
async def xkcd(ctx):
    random_comic_number = rand.randint(0, number_img)
    random_comic_url = f"https://xkcd.com/{random_comic_number}/info.0.json"
    try:
        with urllib.request.urlopen(random_comic_url) as response:
            data = json.loads(response.read().decode())
            await ctx.send(data['img'])
    except Exception as e:
        await ctx.send(f"Erreur lors de la récupération d'un comic XKCD aléatoire : {e}")


time_limit = 1

@bot.command()
async def poll(ctx, *, question):
    poll_message = f'@here {question}\n\nReact with :thumbsup: for Yes or :thumbsdown: for No:'
    poll_message = await ctx.send(poll_message)

    await poll_message.add_reaction('👍')
    await poll_message.add_reaction('👎')

    async def close_poll(poll_message):
        poll_message = await ctx.channel.fetch_message(poll_message.id)
        thumbs_up_reaction = discord.utils.get(poll_message.reactions, emoji='👍')
        thumbs_down_reaction = discord.utils.get(poll_message.reactions, emoji='👎')

        thumbs_up_count = thumbs_up_reaction.count - 1  # Subtract the bot's reaction
        thumbs_down_count = thumbs_down_reaction.count - 1  # Subtract the bot's reaction
        total_votes = thumbs_up_count + thumbs_down_count

        result_message = f'Poll results for "{question}":\n\n'
        result_message += f'👍 Yes: {thumbs_up_count} vote(s)\n'
        result_message += f'👎 No: {thumbs_down_count} vote(s)\n'
        result_message += f'Total votes: {total_votes}'

        await ctx.send(result_message)
        await poll_message.delete()

    # Schedule the poll to close after the specified time limit
    await asyncio.sleep(time_limit * 60)  # Convert minutes to seconds
    await close_poll(poll_message)


token = ""
bot.run(token)  # Démarre le bot