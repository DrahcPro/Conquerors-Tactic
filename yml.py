#NEEDS REWRITING
import yaml

def pull(file="data"):
  with open(f'yaml/{file}.yml') as inputfile:
      data = yaml.full_load_all(inputfile)
      for i in data:
          inp = i
  return inp

def push(data,file="data"):
  with open(f'yaml/{file}.yml', 'w') as outfile:
      yaml.dump(data, outfile, default_flow_style=False)