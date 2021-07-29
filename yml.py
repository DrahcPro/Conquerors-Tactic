import yaml, logging

def pull(file,directory=""):
  with open(f'{directory}{file}.yml') as inputfile:
      data = yaml.full_load_all(inputfile)
      for i in data:
          inp = i
  return inp

def push(data,file,directory=""):
  with open(f'{directory}{file}.yml', 'w') as outfile:
      yaml.dump(data, outfile, default_flow_style=False)