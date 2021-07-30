import discord

def commandfinder(content):
  variables = content.split()
  if variables[0].startswith('n@'):
    command = variables[0][2:]
    returnList = []
    returnList.append(command)
    variables.pop(0)
    for i in variables:
      returnList.append(i)
    return returnList
  else:
    return ['error','-']

def colourwheel(command):
  if command == 'ping':
    return 0x32f011
  elif command == 'create_user':
    return 0x1333e8
  elif command == 'reset_user':
    return 0x8000ff
  elif command == 'start_game':
    return 0xff0000
  elif command == 'kill':
    return 0xff6200
  elif command == 'move':
    return 0xfff700
  elif command == 'range_upgrade':
    return 0xfff700
  else:
    return 0x000000

def embeding(message,mode):
  if mode == 'private':
    if message.content.startswith('n@'):
      command = commandfinder(message.content)
      embed=discord.Embed(title="DM",description=f'Command: **{command[0]}**',colour=colourwheel(command[0]))
      embed.set_author(name=message.author.name,icon_url=message.author.avatar_url)
      for k in range(0,len(command)-1):
        embed.add_field(name=f'variable {k+1}',value=command[k+1])
    else:
      embed=discord.Embed(title="DM",description=message.content)
      embed.set_author(name=message.author.name,icon_url=message.author.avatar_url)

    return embed
  elif mode == 'public':
    if message.content.startswith('n@'):
      command = commandfinder(message.content)
      embed=discord.Embed(title=message.channel.name,url=message.jump_url,description=f'Command: **{command[0]}**',colour=colourwheel(command[0]))
      embed.set_author(name=message.author.name,icon_url=message.author.avatar_url)
      for k in range(0,len(command)-1):
        embed.add_field(name=f'variable {k+1}',value=command[k+1])
    else:
      return None

    return embed
  else:
    ...
    #return error embed