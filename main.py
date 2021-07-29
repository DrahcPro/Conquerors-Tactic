repl = True
if False:  #True if it shouldn't be running, False if it should
    print('escaping')
    exit()

#---------------------------------
#Imports
from discord.ext import commands, tasks
from yml import pull, push
import discord, asyncio
import logging, os, datetime
import random

#Permanent variables
testingChannel = 869998032324804618

#Functional code------------------
intents = discord.Intents().all()
client = commands.Bot(command_prefix="n@", intents=intents)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    filename='logs/info.log',
                    level=logging.INFO)


#On_ready - everytime discord bot gets started
@client.event
async def on_ready():
    channel = client.get_channel(testingChannel)
    await channel.send('We are online')
    logging.info('Bot is online')


#Ping - to check for state of bot
@client.command()
async def ping(ctx, arg=""):
    logging.info(f'Ping command registered, send by: {ctx.author.name}')
    await ctx.send("pong")
    if arg == "+":
        await ctx.send(f"measured: {client.latency}")


#Create_user - add a user to the game
@client.command()
async def create_user(ctx, *, user: discord.User):
    #Checks if command may be used (Admin and in the right channel)
    if ctx.channel != client.get_channel(testingChannel):
        return
    if not (ctx.author.id == 285793122825404416
            or ctx.author.id == 395201615298297858):
        return
    logging.info(f'Create_user command registered, send by: {ctx.author.name}')

    #-Check if user already is a player
    players = pull('players', 'storage/playerDB/')
    if players.get(user.id) is not None:
        await ctx.send('Discord user already has a game user')
    else:
        await ctx.send(f'Creating game user for <@{user.id}>')
        #takes the template values (e.g. range as 1) to be default values
        #changing the template will change the starting values of all players
        playerStats = pull('playerformat', 'storage/DontEdit/')
        playerStats['info']['id'] = user.id
        playerStats['info']['name'] = user.name
        push(playerStats, user.id, 'storage/playerDB/players/')

        #Adds player to players list
        players[user.id] = 1
        push(players, 'players', 'storage/playerDB/')

        #Adds player role to user 
        newPlayer = ctx.guild.get_member(user.id)
        await newPlayer.add_roles(ctx.guild.get_role(869989618177691658))

#Add token LOOP
@tasks.loop(hours=pull('gameSettings','storage/gameDB/')['player-income']['time-unit'])
async def token_loop():
    logging.info('Adding 1 token to everybody')
    players = pull('players','storage/playerDB/')
    for player in players.keys():
      if player == 0:
        continue
      data = pull(player,'storage/playerDB/players/')
      data['character']['tokens'] += 1
      push(data,player,'storage/playerDB/players/')

#Start game 
@client.command() 
async def start_game(ctx,*,args=''):
  #Is the user using the command a Game master?
  if not (ctx.guild.get_role(869989536489414717) in ctx.author.roles): 
    return #Game master role
  #Is the game already running?
  gameSettings = pull('gameSettings', 'storage/gameDB/')
  if gameSettings['game-state']['state'] != 'stopped':
    await ctx.send('Game is already running')
    return
  logging.info(f'Start_game command registered, send by: {ctx.author.name}; and starting game')
  #Give all players a random position
  players = pull('players','storage/playerDB/')
  usedCoords = []
  logging.info('placing players on map')
  for i in players.keys():
    if i == 0:
      continue
    valid = False
    x = 0
    y = 0
    while valid == False:
      x = random.randint(0, gameSettings['map']['size-x'])
      y = random.randint(0, gameSettings['map']['size-y'])
      coord = [x, y]
      if coord not in usedCoords:
        usedCoords.append(coord)
        valid = True
      else:
        logging.info(f'invalid coordinate: {coord}')
      
    data = pull(i, 'storage/playerDB/players/')
    data['x-location'] = x
    data['y-location'] = y
    push(data, i, 'storage/playerDB/players/')


  #@everyone with link and small text
  #DM's with location and notifying they are an active player


  #Change game state
  logging.info('changing game state')
  gameSettings['game-state']['state'] = 'running'
  push(gameSettings,'gameSettings','storage/gameDB/')
  
  #Start token loops-----------
  #Find time to start loop
  now =  datetime.datetime.now()
  h = now.hour
  m = now.minute
  h = h + m / 60

  target = gameSettings['player-income']['first-income']
  th = int(target[0:2])
  tm = int(target[3:5])
  th = th + tm / 60

  if th > h:
    waitingTimeH = th - h
  elif th < h:
    waitingTimeH = (24 - h) + th
  else:
    waitingTimeH = 0
  #Starting loop
  logging.info(f'starting token loop; waiting time: {waitingTimeH}')
  await asyncio.sleep(waitingTimeH*60*60)
  token_loop.start()
  await ctx.send('Game started')


#Starting the bot
if repl:
    from keep_alive import keep_alive
    keep_alive()
logging.info('starting bot')
client.run(os.getenv('TOKEN'))
