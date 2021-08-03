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
from supervision import embeding

#Permanent variables
testingChannel = 869998032324804618

#Functional code------------------
intents = discord.Intents().all()
client = commands.Bot(command_prefix="n@", intents=intents)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', filename='logs/info.log', level=logging.INFO)


#On_ready - everytime discord bot gets started
@client.event
async def on_ready():
    channel = client.get_channel(testingChannel)
    await channel.send('We are online')
    logging.info('Bot is online')

    gameSettings = pull('gameSettings','storage/gameDB/')
    if gameSettings['game-state']['state'] == 'running':
      now = datetime.datetime.now()
      h = now.hour
      m = now.minute
      h = h + m / 60

      target = gameSettings['player-income']['latest-income']
      th = int(target[0:2]) + int(gameSettings['player-income']['time-unit'])
      tm = int(target[3:5])
      th = th + tm / 60

      if th > h:
        waitingTimeH = th - h
      elif th < h:
        waitingTimeH = (24 - h) + th
      else:
        waitingTimeH = 0

      logging.info(f'Since game should be running, starting token loop again; waiting: {waitingTimeH}')
      await asyncio.sleep(waitingTimeH * 60 * 60)
      token_loop.start()
      
@client.event
async def on_message(message):
  if message.author.id != 869998264987045929:
    if message.channel.id == testingChannel:
      channel = client.get_channel(869942398229295124)
      embed = embeding(message,'public')
      if embed != None:
       await channel.send(embed=embed)
    elif isinstance(message.channel, discord.channel.DMChannel):
      channel = client.get_channel(869942398229295124)
      embed = embeding(message,'private')
      if embed != None:
        await channel.send(embed=embed)
    else:
      ...
  await client.process_commands(message)
  


#Checking if the person in question has the right permissions/role
def permissions(ctx,level):
  guild = client.get_guild(869931454237397103)
  member = guild.get_member(ctx.author.id)
  #Check channel
  if ctx.channel.id != testingChannel and not(isinstance(ctx.channel, discord.channel.DMChannel)):
    logging.info('Wrong channel')
    return True #Isn't in the right channel
  #Check role
  if level == 'Game_master':
    if not (guild.get_role(869989536489414717) in member.roles): 
      logging.info('No game master role')
      return True #Has no Game master role
    else:
      return False
  elif level == 'Game_admin':
    if not (guild.get_role(870021534243250176) in member.roles): 
      logging.info('No game admin role')
      return True #Has no Game admin role
    else:
      return False
  elif level == 'Player':
    if not (guild.get_role(869989618177691658) in member.roles): 
      logging.info('No game player role')
      return True #Has no Game player role
    else:
      return False
  elif level == 'Channel':
    return False
  else:
    logging.warning('Permission function used wrong, no or wrong level given')
    return 'Error'



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
    if permissions(ctx,'Game_admin'):
      logging.info(f'Create_user command registered but has wrong permissions, send by: {ctx.author.name}')
      await ctx.send('You do not have the given permissions or are in the wrong channel')
      return
    if user == None:
        await ctx.send('No user given')
        return
    logging.info(f'Create_user command registered, send by: {ctx.author.name}; creating user for {user.name}')

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



#Reset_user - resets a user's game stats
@client.command() 
async def reset_user(ctx,user=discord.User,*,args=""):
  if permissions(ctx,'Game_admin'):
    logging.info(f'Reset_user command registered but has wrong permissions, send by:{ctx.author.name}')
    await ctx.send('You do not have the given permissions or are in the wrong channel')
    return
  logging.info(f'Reset_user command registered, send by: {ctx.author.name}; attacking {user.name}')



#token_loop - loops every x time to add a token to all players
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
    gameSettings = pull('gameSettings','storage/gameDB/')
    now =  datetime.datetime.now()
    h = str(now.hour)
    m = str(now.minute)
    if len(h) == 1:
      h = f'0{h}'
    if len(m) == 1:
      m = f'0{m}'
    gameSettings['player-income']['latest-income'] = f'{h};{m}'
    push(gameSettings,'gameSettings','storage/gameDB/')



#Start_game - starts game and token loop 
@client.command() 
async def start_game(ctx,*,args=''):
  #Does the person have the right role and is in the right channel
  if permissions(ctx,'Game_master'):
    logging.info(f'Start_game command registered but has wrong permissions, send by: {ctx.author.name}')
    await ctx.send('You do not have the given permissions or are in the wrong channel')
    return 

  #Is the game already running?
  gameSettings = pull('gameSettings', 'storage/gameDB/')
  if gameSettings['game-state']['state'] != 'stopped':
    await ctx.send('Game is already running or paused')
    return
  logging.info(f'Start_game command registered, send by: {ctx.author.name}; and starting game')
  await ctx.send('Starting game')

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
    data['gameinfo']['x-location'] = x
    data['gameinfo']['y-location'] = y
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

  await ctx.send('Game started')
  logging.info('GAME STARTED')
  await asyncio.sleep(waitingTimeH*60*60)
  token_loop.start()
  


@client.command() 
async def stop_game(ctx,*,args=''):
  #Does the person have the right role and is in the right channel
  if permissions(ctx,'Game_master'):
    logging.info(f'Stop_game command registered but has wrong permissions, send by: {ctx.author.name}')
    await ctx.send('You do not have the given permissions or are in the wrong channel')
    return 

  #Is the game already running?
  gameSettings = pull('gameSettings', 'storage/gameDB/')
  if gameSettings['game-state']['state'] == 'stopped':
    await ctx.send('Game is not running')
    return
  logging.info(f'Stop_game command registered, send by: {ctx.author.name}; and stopping game')
  await ctx.send('Stopping game')

  #Stop the token loop if running
  try:
    token_loop.cancel()
  except:
    ...
  #Change game state
  logging.info('changing game state')
  gameSettings['game-state']['state'] = 'stopped'
  push(gameSettings,'gameSettings','storage/gameDB/')

  #@everyone that the game has been finalised and stopped

  logging.info('GAME STOPPED')



@client.command() 
async def pause_game(ctx,*,args=''):
  #Does the person have the right role and is in the right channel
  if permissions(ctx,'Game_master'):
    logging.info(f'Pause_game command registered but has wrong permissions, send by: {ctx.author.name}')
    await ctx.send('You do not have the given permissions or are in the wrong channel')
    return 

  #Is the game already running?
  gameSettings = pull('gameSettings', 'storage/gameDB/')
  if gameSettings['game-state']['state'] != 'running':
    await ctx.send('Game is not running or paused')
    return
  logging.info(f'Pause_game command registered, send by: {ctx.author.name}; and pausing game')
  await ctx.send('Pausing game')

  #Stop the token loop if running
  try:
    token_loop.cancel()
  except:
    ...

  #Change game state
  logging.info('changing game state')
  gameSettings['game-state']['state'] = 'paused'
  push(gameSettings,'gameSettings','storage/gameDB/')

  #@everyone that the game has been paused

  logging.info('GAME PAUSED')



@client.command() 
async def unpause_game(ctx,*,args=''):
  #Does the person have the right role and is in the right channel
  if permissions(ctx,'Game_master'):
    logging.info(f'Unpause_game command registered but has wrong permissions, send by: {ctx.author.name}')
    await ctx.send('You do not have the given permissions or are in the wrong channel')
    return 

  #Is the game already running?
  gameSettings = pull('gameSettings', 'storage/gameDB/')
  if gameSettings['game-state']['state'] != 'paused':
    await ctx.send('Game is not paused')
    return
  logging.info(f'Unpause_game command registered, send by: {ctx.author.name}; and pausing game')
  await ctx.send('Unpausing game')

  #Start the token loop again
  now = datetime.datetime.now()
  h = now.hour
  m = now.minute
  h = h + m / 60

  target = gameSettings['player-income']['latest-income']
  th = int(target[0:2]) + int(gameSettings['player-income']['time-unit'])
  tm = int(target[3:5])
  th = th + tm / 60

  if th > h:
    waitingTimeH = th - h
  elif th < h:
    waitingTimeH = (24 - h) + th
  else:
    waitingTimeH = 0

  #NOT WORKING YET, NEEDS FIXING!!!!!!!!!!!!!!!!!!!!!
  #
  #
  #
  logging.info(f'Since the game is unpaused, starting token loop again; waiting: {waitingTimeH}')
  await asyncio.sleep(waitingTimeH * 60 * 60)
  token_loop.start()

  #Change game state
  logging.info('changing game state')
  gameSettings['game-state']['state'] = 'running'
  push(gameSettings,'gameSettings','storage/gameDB/')

  #@everyone that the game has been unpaused

  logging.info('GAME UNPAUSED')



@client.command()
async def kill(ctx,user: discord.User,*,args=""):
  if permissions(ctx,'Player'):
    logging.info(f'Kill command registered but has wrong permissions, send by: {ctx.author.name}')
    return
  logging.info(f'Kill command registered, send by: {ctx.author.name}; attacking {user.name}')
  
  players = pull('players','storage/playerDB/')
  #Check if game is running
  gameSettings = pull('gameSettings', 'storage/gameDB/')
  if gameSettings['game-state']['state'] != 'running':
    logging.info(f'Game is not running, command cannot be executed')
    await ctx.send("The game needs to be running for you to use this command!")
    return
  #Check if player is trying to shoot themselves
  if ctx.author.id == user.id:
    logging.info(f'Author is trying to shoot themselves')
    await ctx.send("You can't shoot yourself.")
  #Check if author is an ALIVE player
  elif players[ctx.author.id] != 1:
    logging.info(f'Author is not an alive player')
    await ctx.send("You are not an alive player, you can't use this command.")
  #Check if target is an ALIVE player
  elif players[user.id] != 1:
    logging.info(f'Target is not an alive player')
    await ctx.send("You can't kill a player who is dead.")
  else:
    #Check if target is in range
    playerData = pull(ctx.author.id, 'storage/playerDB/players/')
    targetData = pull(user.id, 'storage/playerDB/players/')
    playerCoords = [playerData['gameinfo']['x-location'], playerData['gameinfo']['y-location']]
    targetCoords = [targetData['gameinfo']['x-location'], targetData['gameinfo']['y-location']]

    xDifference = targetCoords[0] - playerCoords[0]
    yDifference = targetCoords[1] - playerCoords[1]
    shooterRange = playerData['stats']['range']
    if (-shooterRange <= xDifference <= shooterRange) and (-shooterRange <= yDifference <= shooterRange):
      if playerData['character']['tokens'] >= gameSettings['prices']['shooting']:
        #Remove life from target
        targetData['character']['lives'] -= 1
        lives = targetData['character']['lives']
        logging.info(f'new no. of lives: {str(lives)}')
        push(targetData, user.id, 'storage/playerDB/players/')
        logging.info(f'Hit carried out')
        await ctx.send("Shot fired against " + user.name)
        await user.send(ctx.author.name + " fired a shot against you! You now have " + str(lives) + " lives remaining.")
        #Check if the target is now dead
        if (targetData['character']['lives'] <= 0):
          players[user.id] = 0
          push(players, 'players','storage/playerDB/')
          logging.info(f'Target dead.')
          channel = client.get_channel(testingChannel)
          await channel.send(f"<@{user.id}> ran out of lives! They are out of the game!")
      
        #Remove token(s)
        playerData['character']['tokens'] -= gameSettings['prices']['shooting']
        push(playerData, ctx.author.id, 'storage/playerDB/players/')
      else:
        logging.info(f'Author does not have enough tokens')
        await ctx.send("You don't have enough tokens!")
    else:
      logging.info(f'Player not in range')
      await ctx.send("That player is not in range!")



@client.command() 
async def game_state(ctx,*,args=""):
  gameSettings = pull('gameSettings', 'storage/gameDB/')
  await ctx.send(gameSettings['game-state']['state'])



@client.command()
async def move(ctx,x=0,y=0,*,args=""):
  if permissions(ctx,'Player'):
    logging.info(f'Move command registered but has wrong permissions, send by: {ctx.author.name}')
    return
  logging.info(f'Move command registered, send by: {ctx.author.name}; moving {x} sideways and {y} vertically')
  ...
  #Check if the game is running
  gameSettings = pull('gameSettings', 'storage/gameDB/')
  if gameSettings['game-state']['state'] != 'running':
    logging.info(f'Game is not running, command cannot be executed')
    await ctx.send("The game needs to be running for you to use this command!")
    return
  #Check if author is an ALIVE player
  players = pull('players','storage/playerDB/')
  if players[ctx.author.id] != 1:
    logging.info(f'Author is not an alive player')
    await ctx.send("You are not an alive player, you can't use this command.")
    return
  #Check if author has enough tokens
  playerData = pull(ctx.author.id, 'storage/playerDB/players/')
  if playerData['character']['tokens'] < gameSettings['prices']['moving']:
    logging.info(f'Author does not have enough tokens')
    await ctx.send("You don't have enough tokens!")
    return
  #Check if x and y arent both 0
  if x == 0 and y == 0:
    logging.info(f'User tried to move zero spaces')
    await ctx.send("You can't move zero spaces!")
    return
  #Check if the movement is a valid movement (not out of boundaries)
  if x < -1 or x > 1:
    logging.info(f'X movement out of boundaries')
    await ctx.send("You can only move one space!")
    return
  elif y < -1 or y > 1:
    logging.info(f'X movement out of boundaries')
    await ctx.send("You can only move one space!")
    return
  #Move player
  playerData['gameinfo']['x-location'] += x
  playerData['gameinfo']['y-location'] += y
  #Remove token(s)
  playerData['character']['tokens'] -= gameSettings['prices']['moving']
  push(playerData, ctx.author.id, 'storage/playerDB/players/')
  logging.info(f'Move carried out successfully.')
  await ctx.send("You moved (" + str(x) + ", " + str(y) + ")! You are now at position (" + str(playerData['gameinfo']['x-location']) + ", " + str(playerData['gameinfo']['y-location']) + ")")


@client.command()
async def range_upgrade(ctx,*,args=""):
  if permissions(ctx,'Player'):
    logging.info(f'Range_upgrade command registered but has wrong permissions, send by: {ctx.author.name}')
    return
  logging.info(f'Range_upgrade command registered, send by: {ctx.author.name}')
  ...
  #Check if the game is running
  gameSettings = pull('gameSettings', 'storage/gameDB/')
  if gameSettings['game-state']['state'] != 'running':
    logging.info(f'Game is not running, command cannot be executed')
    await ctx.send("The game needs to be running for you to use this command!")
    return
  #Check if author is an ALIVE player
  players = pull('players','storage/playerDB/')
  if players[ctx.author.id] != 1:
    logging.info(f'Author is not an alive player')
    await ctx.send("You are not an alive player, you can't use this command.")
    return
  #Check if author has enough tokens
  playerData = pull(ctx.author.id, 'storage/playerDB/players/')
  if playerData['character']['tokens'] < gameSettings['prices']['range-upgrade']:
    logging.info(f'Author does not have enough tokens')
    await ctx.send("You don't have enough tokens!")
    return
  #Check current range
  #Upgrade range
  playerData['stats']['range'] += 1
  #Remove token(s)
  playerData['character']['tokens'] -= gameSettings['prices']['range-upgrade']
  push(playerData, ctx.author.id, 'storage/playerDB/players/')
  logging.info(f'Range upgrade carried out successfully')
  await ctx.send("You upgraded your range! It is now " + str(playerData['stats']['range']) + " spaces.")


@client.command()
async def transfer_tokens(ctx,user:discord.User,amount,*,args=""):
  if permissions(ctx,'Player'):
    logging.info(f'Range_upgrade command registered but has wrong permissions, send by: {ctx.author.name}')
    return
  logging.info(f'Transfer_token command registered, send by: {ctx.author.name} to {user.name}; amount: {amount}')
  #Check if the game is running
  #Check if author is an ALIVE player
  #Check if target is an ALIVE player
  #Check if amount > 0
  #Remove tokens from author
  #Add tokens to target

  ...



#Starting the bot
if repl:
    from keep_alive import keep_alive
    keep_alive()
logging.info('starting bot')
client.run(os.getenv('TOKEN'))
