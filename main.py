from pyfiglet import Figlet
from os import path
from termcolor import cprint
from core.checkers import Checkers
from core.dorker import MenuDork
from core.helper import display_menu_helper
from core.social import Social

import argparse
import sys
import re
import os

class Menu:
  def __init__(self):
    self.clear = 'clear' if os.name == 'posix' else 'cls'
    self.clrscr = lambda x: os.system(x)
    self.space = 6
    self.curr_tool = None

  def display_banner(self):
    fig = Figlet(font='weird')
    cprint(fig.renderText('CLAIR DE UNE'), 'green')

  def display_menu(self):
    
    ask = "0"
    while int(ask) < 5:
      self.display_banner()
      cprint(' ' * self.space + '='*50, 'green')
      cprint(' ' * self.space + '{:^50}'.format('Menus Tool'), 'green')

      cprint('''
        1. Dorking
        2. Checkers
        3. Social
        4. Helper Tool
        5. Exit
        ''', 'green')
      cprint(' ' * self.space + 'Choice your tools : ', end=' ')
      ask = input("")
      if ask == '1':
        self.curr_tool = MenuDork()
        self.curr_tool.display()
      elif ask == '2':
        self.curr_tool = Checkers()
      elif ask == '3':
        self.curr_tool = Social()
        self.curr_tool.question()
        self.curr_tool.core()
      elif ask == '4':
        self.curr_tool = display_menu_helper()
        self.curr_tool()
    cprint('Thank you see you....')

if __name__ == '__main__':
  c = Menu()
  c.display_menu()