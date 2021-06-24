from socialscan.util import Platforms, sync_execute_queries
from core.helper import check_file_or_path, check_digit_ret, filter_empas, yorn_ret
from termcolor import cprint
from queue import Queue

import concurrent.futures

class Social:
  def __init__(self):
    self.empas = Queue()
    self.platform_list = [
      'Instagram', 'Twitter', 'Github', 'Lastfm', 'Tumblr',
      'Snapchat', 'Gitlab', 'Reddit', 'Yahoo', 'Pinterest',
      'Spotify', 'Firefox'
    ]
    self.valid = Queue()
    self.platform = list()


  def load_file(self, name):
    with open(name, 'r') as f:
        for i in f.readlines():
          if len(i.split(":")) == 1:
            self.empas.put(i.strip())
          else:
            self.empas.put(i.strip().split(":"))

  def question(self):
    cprint('Method for input, manual/file: ', end='')
    ask = input()
    if not isinstance(ask, str) or ask not in ['manual', 'file']:
      cprint('[ERROR] Unknown method!! Exit...', 'green')
      exit()

    elif ask == 'manual':
      cprint('''
        or Enter input manual with : separate
        Example manual input:
        test1:test2:test3@gmail.com:test4
        ''')
      cprint('Enter: ','green', end='')
      ask2 = input()
      self.empas = ask2.split(":")

    elif ask == 'file':
      cprint('Enter file name: ','green', end='')
      ask2 = input()
      ask2, isfile = check_file_or_path(ask2)
      cprint('Want to filter your empas from big domain ? (y/n): ', 'green', end='')
      if yorn_ret(input()):
        temp = filter_empas(data=ask2, isfile=True)
        for x in temp: self.empas.put(x)
        
      elif isfile:
        self.load_file(ask2)

      else:
        cprint("[ERROR] Your input not a file!!!", 'red')
        exit(1)

    cprint('Enter your file out:', 'green', end='')
    self.file_out = input()

    cprint('Enter thread max 8, 20 if you have high cpu, 0 if not want: ', 'green', end='')
    self.threads = check_digit_ret(input())
    
    cprint('Enter max user per thread, max 8 default 5: ', 'green', end='')
    self.max_user_per_thread = check_digit_ret(input())
    if not self.max_user_per_thread: self.max_user_per_thread = 5
    if not self.threads: self.threads = 6

    cprint('''
      Choice platform: 
      instagram, twitter, github, tumblr,
      lastfm, snapchat, gitlab, reddit, yahoo
      pinterest, spotify, firefox
      Enter using separate (:), all for all platform

      Enter : ''', 'green', end='')
    ask_platform = input()

    if ask_platform.lower() == 'all':
      self.platform = list(Platforms)
    else:
      for x in ask_platform:
        if x in self.platform_list:
          self.platform.append(getattr(Platforms, x.title()))

  def sub_core(self, pw, em):
    # print(em)
    # print(pw)
    results = sync_execute_queries(em, self.platform)
    for i, res in enumerate(results):
      text = f'%s on %s: (Valid: %s, Available: %s' % (
        res.query, str(res.platform),
        res.valid, res.available
        )

      if res.valid or res.available:
        yield True, res.query+':'+pw[res.query] if pw else res.query +":"+str(res.platform)
      else:
        yield False, text

  def core(self):
    if not self.threads:
      while not self.empas.empty():
        em = [self.empas.get().split(":") for _ in range(self.max_user_per_thread)]
        pw = {x[0]:x[1] for x in em}
        em = [x[0] for x in em]
        self.sub_core(pw, em)
    else:
      with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as exc:
        while not self.empas.empty():
          fut_dict = dict()
          try:
            for _ in range(self.threads):
              em = [self.empas.get() for _ in range(self.max_user_per_thread)]
              print(em)
              if len(em[0]) == 2:
                pw = {x[0]: x[1] for x in em}
                em = [x[0] for x in em]
                fut_dict[exc.submit(self.sub_core, pw, em)] = 1
              else:
                em = [x[0] for x in em]
                fut_dict[exc.submit(self.sub_core, None, em)] = 1

            for fut in concurrent.futures.as_completed(fut_dict):
              for res in fut.result():
                if res[0]:
                  print(res[1])
                  self.valid.put(res[1])
                else:
                  print(res[1])

            del fut_dict
            
          except KeyboardInterrupt:
            break

    self.write()

  def write(self):
    with open(self.file_out, 'w') as f:
      while not self.valid.empty():
        f.write(self.valid.get() + '\n')
    print("DONE!!!")
    input()