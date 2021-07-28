repl = True
if False: #True if it shouldn't be running, False if it should
  print('escaping')
  exit()

#---------------------------------
#Imports
from discord.ext import commands
import discord, os

#Permanent variables
testingChannel = 869998032324804618

#Functional code------------------
intents = discord.Intents().all()
client = commands.Bot(command_prefix="n@",intents=intents)

#On_ready - everytime discord bot gets started
async def on_ready():
  channel = client.get_channel(testingChannel)
  await channel.send('We are online')
  print('bot is online')

#Starting the bot
if repl:
  from keep_alive import keep_alive
  keep_alive()
client.run(os.getenv('TOKEN'))