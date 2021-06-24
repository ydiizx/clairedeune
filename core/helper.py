#from pyfiglet import Figlet
from setting import CONFIG_PATH
from random import choice
from termcolor import cprint

import os
import requests
import re

def display_menu_helper():
  cprint('''
    1. Combine Empas path
    ''')
  ask = input('Choice : ')
  if ask == '1':
    return combine_empas_from_path

class RandomUser:
  def __init__(self, max_user=1000, keys="all"):
    cprint("Waiting Getting Random User.....", 'green')
    self._data = [
      {'name': x['name'],
       'login': x['login']
       }
      for x in requests.get(f'https://randomuser.me/api/?results={max_user}').json()['results']
    ]

  @property
  def get_random_name(self):
    temp = choice(self._data)
    return f"{temp['name']['first_name']} {temp['name']['last_name']}"
  
  @property
  def random(self):
    return choice(self._data)
  
  @property
  def get_all(self):
    return self._data


class UserAgent:
  def __init__(self):
    self.user_agent = [x.strip() for x in open(CONFIG_PATH+'user_agents.txt', 'r').readlines()]

  @property
  def random(self):
    return choice(self.user_agent)
  
  def get_random_agent(self):
    return choice(self.user_agent)

  def get_all_agent(self):
    return self.user_agent

def filter_empas(data=None, isfile=False, custom=None, file_out=None, ext=None):
  # custom = custom if custom else ['gmail','yahoo','hotmail','outlook']
  # custom = '|'.join(custom) if custom else 'gmail|yahoo|hotmail|outlook'

  if isinstance(custom, list):
    if ext and isinstance(ext, lit):
      custom.extend(ext)
    custom = '|'.join(custom)
  else:
    custom = 'gmail|yahoo|hotmail|outlook|.ru|.de|.fr|.it|.jp|.cn'

  result = list() if not file_out else open(file_out, 'w')

  if isfile:
    with open(data, 'r') as f:
      data = f.readlines()

  for i in data:
    # if any(x in i for x in custom):
    if re.search(custom, i):
      continue
    if not file_out:
      if len(i.split(":")) == 1:
        result.append(i.strip())
      else:
        result.append(i.strip().split(":"))
      # result.append(i.strip())
    else:
      result.write(i)

  if file_out: result.close()

  return result if not file_out else f"Has been writing to {file_out}"

# def filter_empas_ext(data=None, isfile=False, custom=None, file_out=None):
#   # custom = '|'.join(custom) if custom else 'de|fr|it|ru|jp|cn'

def check_file_or_path(file_or_path):
  assert os.path.isfile(file_or_path) or os.path.isdir(file_or_path)
  return (os.path.join(file_or_path), os.path.isfile(file_or_path))

def check_digit_ret(x):
  assert x.isdigit(), "[ERROR] Not Digit!!"
  return int(x)

def yorn_ret(x):
  assert x.lower() == 'n' or x.lower() == 'y', 'not '
  return True if x.lower() =='y' else False

def combine_empas_from_path():
  data = set()
  path_name, _ = check_file_or_path(input('Enter path empas : '))
  output = 'result/' + input("Enter output file name: ")

  f = open(output, 'w')
  
  for filename in list(os.walk(path_name))[0][2]:
    with open(path_name+'/'+filename, 'r') as c:
      data.add(c.read())

  while data:
    f.write(data.pop())

  f.close()
  print("Saved file to %s" % path_name +'/'+ output)