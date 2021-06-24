from bs4 import BeautifulSoup
from urllib.parse import unquote as uq
from random import choice
from setting import DATA_PATH, SAVE_PATH
from pyfiglet import Figlet
from termcolor import cprint
from core.helper import check_file_or_path, check_digit_ret, yorn_ret, UserAgent

import concurrent.futures
import os
import requests
from queue import Queue

page_formats = '.php? .asp? .html .cgi .blog? .htm'
page_types ='''page_id cat category id coID include item_id product_id purchase_id login_id id user_id register game_id type type_id gamer_id user_id username_id page sectionid misc mid feed bookid locale panel GUID membership topicid name CatId genre param pageID cPath words path code storeId option search CartId term countryid refresh show medium file sec return team ReturnUrl sortby auth value login_id ref function referer articleID to pageweb prefix play load loader moviecd coID article activation redirect stream categoryid langcode buy showpage aqs cat topic idx partner source strID mobilesite module blogId site language user_id newsID titleno action users num IdStructure view fileId id serials register encoding color pid utm_source do link plugin format geo ID startTime details PID submit extension list channel r flavour clientId next content_type titleid username_id server filepath read client nextpage subscriptions viewAction mod profile doc model comments keyword include page rangeID title product configFile x imageId redirectTo scid purchase_id issue type query hollywood avd default chapter pagetype lang ad style_id pageindex utmsource q viewpage symbol company documentId content contentId langid owner itemName post sourcedir archive profiles cid url item_id'''
search_functions = "intitle: inurl: filetype: ext: intext: site: cache: after: allintext allinurl: allintitle:"
new_sf = "key * site"
domain_extensions = '.com .net .org .co .us .uk .co.uk .co.us .web .it .fr .de .tk .info .edu .gov'\
		        '.ac .id .co.id .ca .mx .nl .my'

class MenuDork:
    def __init__(self):
        self.curr_tool = None
        self.fig = Figlet(font='weird')
        self.display_banner = lambda x: cprint(self.fig.renderText(x), 'green')
        self.clear = "clear" if os.name == "posix" else "cls"
        
    def display_menu(self):
        os.system(self.clear)
        self.display_banner("Dorkers")
        cprint(' '*6 + '='*50, 'green')
        cprint(' '*6 + '{:^50}'.format('Menus Dorkers'), 'green')
        cprint('''
               1. Dork Searching
               2. Dork Maker
               3. Back to main menu
               4. Exit
               ''')
        
    def display(self):
        ask1 = '1'
        while int(ask1) < 3:
            self.display_menu()
            cprint('Enter your choice : ', 'green', end=' ')
            ask1 = input("")
            assert ask1.isdigit(), '[ERROR] Not digit!!'
            if ask1 == '1':
                self.curr_tool = DorkSearcher
            elif ask1 == '2':
                self.curr_tool = DorkMaker
            self.curr_tool = self.curr_tool.Asking()
        
class DorkSearcher(MenuDork):
    def __init__(self, dorklist=None, thread=15, output="", cleaning=False):
        super().__init__()
        self.ua = UserAgent()
        self.yahoo_url = "https://search.yahoo.com/search?p={}" # base url for searching with yaho
        self.bing_url = "https://www.bing.com/{}"
        self.dorklist = Queue()
        self.thread = thread 
        self.output = output
        self.cleaning = cleaning
        self.result = list()
        self.dork_count = 0
        self.count = 0
        self.loaders(dorklist)
        self.main()

    def loaders(self, dorkname):
        if isinstance(dorkname, list):
            for i in dorkname:
                self.dorklist.put(i)
            del dorkname
        else:
            dorkname = dorkname if os.path.isfile(dorkname) else DATA_PATH + dorkname
            try:
                with open(dorkname, 'r') as f:
                    for i in f.readlines():
                        self.dorklist.put(i)
            except Exception as e:
              print("[ERRO] ", e)
              exit()

    def display(self):
        os.system(self.clear)
        self.display_banner("Dork Searching")
        print("DORK USED = {}\nGOT LINK => {}".format(self.dork_count, self.count))
    
    def parsing_bing(self, html=None, first=False):
        if "No results found for " in html:
            return 
        html2 = BeautifulSoup(html, 'html.parser')
        cite = html2.findAll('cite')
        if len(cite) >= 5:
            for x in cite:
                try:
                    print("FROM BING =>", x.text)
                    self.result.append(x.text)
                    self.count += 1
                except:
                    continue
            if first:
                page = html.findAll('a', attrs={'class': 'b_widePag sb_bp'})
                if page:
                    page = [x.attrs['href'] for x in page]
                    return page
        else:
            return 


    def worker(self):
        while not self.dorklist.empty():
            self.dork_count += 1
            query = self.dorklist.get()
            try:
                self.worker_bing(query)
                self.worker_yahoo(query)
            except Exception as e:
                continue

    def worker_bing(self, query):
        bing_url = self.bing_url.format("search?q="+query)
        ua = self.ua.get_random_agent()
        next_page = None
        try:
            r = requests.get(bing_url, headers={"User-agent":ua})
            if r.status_code == 500:
                print("Ups you got blocked DUDE")
                return 
            next_page = self.parsing_bing(r.text, first=True)

        except Exception as e:
            print("BING ERROR1 =>", e)
        if next_page:
            for i in next_page:
                try:
                    r = requests.get(bing_url+i, headers={"User-agent": ua})
                    if r.status_code == 500:
                        print("Ups you got blocked DUDE")
                        return 
                    self.parsing_bing(r.text)
                except: print("BING ERROR 2 => ", e)

    def worker_yahoo(self, query):
        ua = self.ua.get_random_agent()
        try:
            r = requests.get(self.yahoo_url.format(query), headers={"User-Agent":ua})
            if r.status_code == 500:
                print("Ups you got blocked DUDE!!")
                exit(1)
        except:
            pass 
        try:
            pages = self.parsing_yahoo(r.text, first=True)
        except Exception as e:
            print("ERROR FROM PAGES", e)
        if pages:
            for page in pages:
                try:
                    r = requests.get(page, headers={'User-Agent': ua}).text 
                    self.parsing_yahoo(r)
                except:
                    continue 
        return 0

    def parsing_yahoo(self, resp=None, first=False):
        pages = None 
        soup = BeautifulSoup(resp, 'html.parser')
        hrefs = soup.find_all('a', attrs={'class': 'ac-algo'})
        if first:
            try:
                pages = [x.attrs['href'] for x in soup.find('div',attrs={'class': 'pages'}).find_all('a')]
            except:
                pass
        for link in hrefs:
            link = link.attrs['href'].split('RU=')[1].split('/RK')[0]
            link = uq(link)
            print("FROM YAHOO =>", link)
            self.count += 1
            self.result.append(link)
        if pages:
            return pages 
        return None
    
    def main(self):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.thread) as executor:
                exec_dict = dict()  
                for _ in range(self.thread):
                    # exec_dict[executor.submit(self.worker, self.dorklist.pop(0).strip())] = 1
                    exec_dict[executor.submit(self.worker)] = 1
                    
                for future in concurrent.futures.as_completed(exec_dict):
                    continue
                    
        except KeyboardInterrupt:
            self.saving()
        
        if self.cleaning:
            self.cleaner()
        else:
            self.saving()
    
    def cleaner(self):
        print("CLEANING ALL LINK")
        blacklist = ['google','googleusercontent', 'github','yahoo', 'stackoverflow','bing', 'microsoft','amazon','tokopedia','lazada']
        for black in blacklist:
            for link in self.result:
                if black in link:
                    self.result.remove(link)
        with open(self.output, 'w') as f:
            for link in self.result: f.write(link+"\n")

    def saving(self):
        with open(SAVE_PATH + self.output, 'w') as f:
            for link in self.result: f.write(link+"\n")
            
    @classmethod
    def Asking(cls):
        data = {}
        cprint("Enter your dorklist file : ", 'green', end=' ')
        data['dorklist'] = check_file_or_path(input(""))[0]
        cprint('Enter thrad you want (Max 30) : ', 'green', end=' ')
        data['thread'] = check_digit_ret(input(""))
        cprint('Enter your output : ', 'green', end=' ')
        data['output'] = input("")
        cprint("Do you want to clean your result ?? (y/n) :", 'green', end=' ')
        data['cleaning'] = yorn_ret(input(""))
        return cls(**data)

class DorkMaker(MenuDork):
    def __init__(self, max_dork=10000, filein=None, output=None):
        super().__init__()
        self.result = list()
        self.max_dork = max_dork
        self.count = 0
        self.output = output
        self.data_dict = { # Splitting 
            "DE": domain_extensions.split(),
            "PT": page_types.split(),
            "PF": page_formats.split(),
            "SF": search_functions.split()
            }
        if isinstance(filein, list):
            self.data_dict["KW"] = filein
        else:
            self.data_dict["KW"] = [x.strip() for x in open(filein, 'r').readlines()]
            
        self.dorktypes = [
        "{KW}{PF}?{PT}= site:{DE}",
        '{SF} "{DE}" + "{KW}"',
        '{SF}{KW}{PF}?{PT}= site:{DE}',
        '{SF}{PT}={KW}{PF}? site:{DE}',
        '{PT}= "{KW}" + "{DE}"',
        '{SF}{KW}{PF}?{PT}= site:{DE}',
        '{SF}{PT}={KW}{PF}? site:{DE}'
        ]
        self.core()

    def display(self):
        os.system(self.clear)
        self.display_banner('Dork Maker')
        print("Loading... wait")
    
    def worker(self, dork_type):
        temp = list()
        parsing = list()
        for i in range(0, len(dork_type)+1):
            temp_dork = dork_type[i-2:i]
            if temp_dork:
                if temp_dork[0].isupper() and temp_dork[1].isupper():
                    parsing.append(temp_dork)

        dork_type = "".join(x for x in dork_type if not x.isupper())

        for i in self.data_dict[parsing[0]]:
            for n in self.data_dict[parsing[1]]:
                for c in self.data_dict[parsing[2]]:
                    if len(parsing) > 3:
                        x = choice(self.data_dict[parsing[3]])
                        if len(parsing) > 4:
                            w = choice(self.data_dict[parsing[4]])
                            temp.append(dork_type.format(i,n,c,x,w)+"\n")
                            self.count += 1
                        else:
                            temp.append(dork_type.format(i,n,c,x)+"\n")
                            self.count += 1
                    else:
                        temp.append(dork_type.format(i,n,c)+"\n")
                        self.count += 1
        return temp

    def core(self):
        self.display()
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.dorktypes)) as executor:
            fut_dict = dict()
            for z in self.dorktypes:
                fut_dict[executor.submit(self.worker, z)] = 1
                        
            for future in concurrent.futures.as_completed(fut_dict):
                self.result.extend(future.result())
                    
        self.writing()

    def writing(self):
        with open(self.output, 'w') as f:
            for x in self.result:
                f.write(x)

        print("DONE!!")
        input("Enter to continue")
    
    @classmethod
    def Asking(cls):
        data = {}
        cprint("Enter Max Dork :", 'green', end=' ')
        data['max_dork'] = check_digit_ret(input(""))
        cprint('Enter file in keyword list :', 'green', end=' ')
        data['filein'] = check_file_or_path(input(""))[0]
        cprint('Enter your output : ', 'green', end=' ')
        data['output'] = input("")
        return cls(**data)