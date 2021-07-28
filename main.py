repl = True
if False: #True if it shouldn't be running, False if it should
  print('escaping')
  exit()

#---------------------------------
#Imports
from discord.ext import commands
from yml import pull, push
import discord, os
import logging


#Permanent variables
testingChannel = 869998032324804618

#Functional code------------------
intents = discord.Intents().all()
client = commands.Bot(command_prefix="n@",intents=intents)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt = '%m/%d/%Y %H:%M:%S', filename='logs/info.log', level=logging.INFO)

#On_ready - everytime discord bot gets started
@client.event
async def on_ready():
  channel = client.get_channel(testingChannel)
  await channel.send('We are online')
  logging.info('Bot is online')

#Ping - to check for state of bot
@client.command()
async def ping(ctx,arg=""):
  logging.info(f'Ping command registered, send by: {ctx.author.name}')
  await ctx.send("pong")
  if arg == "+":
    await ctx.send(f"measured: {client.latency}")

#Create_user - add a user to the game
@client.command()
async def create_user(ctx,*,user: discord.User):
  if ctx.channel != client.get_channel(testingChannel):
    return
  if not (ctx.author.id == 285793122825404416 or ctx.author.id == 395201615298297858):
    return
  logging.info(f'Create_user command registered, send by: {ctx.author.name}')

  #To be added:
  #-Check if user already is a player
  players = pull('players','storage/playerDB/')
  if players.get(user.id) is not None:
    await ctx.send('Discord user already has a game user')
  else:
    await ctx.send(f'Creating game user for <@{user.id}>')

  #-If not
  #-Create yaml
  #-Add to player list
  #-Add player role


#Starting the bot
if repl:
  from keep_alive import keep_alive
  keep_alive()
logging.info('starting bot')
client.run(os.getenv('TOKEN'))