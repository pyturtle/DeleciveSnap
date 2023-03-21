from cgitb import html
import os 
from venv import main
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup,SoupStrainer
import colorama
import pickle
from selenium import webdriver
import os
from selenium.webdriver.chrome.options import Options
import time
# VER 1.01


CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument("--headless")
ONLY_A_TAGS = SoupStrainer("a")
DRIVER = webdriver.Chrome("chromedriver.exe",options=CHROME_OPTIONS)
DELAY = 2 # seconds
# driver.get("https://www.gapcanada.ca/browse/category.do?cid=6998")

# html2 = driver.execute_script("return document.documentElement.innerHTML;")

# soup = BeautifulSoup(html2, "html.parser", parse_only = ONLY_A_TAGS)
# print (soup.prettify())




#changing dir
os.chdir(r"oldnavy\pickle_files")

link_set = set()
external_set = set()
link_list = []
total_urls_visited = 0


# if the total_urls_visited is greater than it means that the prograam crashed and ton start where it left off 
with open('total_urls_visited.pkl', 'rb') as f: total_urls_visited = pickle.load(f) 
if total_urls_visited > 0:
    with open('link_set.pkl', 'rb') as f: link_set = pickle.load(f)
    with open('link_list.pkl', 'rb') as f: link_list = pickle.load(f)
with open('external_set.pkl', 'rb') as f: external_set = pickle.load(f)   

#setting the colour text
colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW
RED = colorama.Fore.RED

#max amount of urls to visit
MAX_URLS = 10000
ONLY_A_TAGS = SoupStrainer("a")





def getAllWebsiteLinks(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    

    # domain name of the URL without the protocol
    DRIVER.get(url)
    #loading the whole website
    DRIVER.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(DELAY)
    html2 = DRIVER.page_source
    domain_name = "https"+"://" + urlparse(url).netloc
    soup = BeautifulSoup(html2, "lxml", parse_only = ONLY_A_TAGS)
    # print(soup.prettify())
    #running over each a tag found in the html
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue
        href = urljoin(url, href)
        # print(href)
        parsed_href = urlparse(href)
        href = href.split("&",1)[0]
        href = href.split("#",1)[0]
        # remove URL GET parameters, URL fragments, etc.
        if not isValid(href):
            # not a valid URL
            continue
        if href in external_set :
            continue
        if href in link_set:
            continue
        
        if domain_name not in href:# if the domain nameis not found the it will skip and add it to a set as cheeckinga set is O(1)
            print(f"{RED}[*] External link: {href}{RESET}")
            external_set.add(href)
            with open('external_set.pkl', 'wb') as f:
                pickle.dump(external_set, f)
                
        if "/browse" not in parsed_href.path: #If itss not apart of the browse branch of the website witch contains productss and catalogs
            link_set.add(href)
            continue
        
        if href.endswith('jpg'):#if itss an image link do nnnot save 
            continue

        
            continue
        print(f"{GREEN}[*] Internal link: {href}{RESET}")# Save the link 
        link_list.append(href)
        link_set.add(href)

        #Saves the file progress incase the program stops running as it takes two hours. If it does crash it starts from the saved index 
        with open('link_set.pkl', 'wb') as f:
            pickle.dump(link_set, f)
        with open('link_list.pkl', 'wb') as f:
            pickle.dump(link_list, f)
        



def isValid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)



def crawl(url,max_urls=30):
    
    """
    ALl THE LINKS FOUND ON THE WEBSITE
    """
    
    global total_urls_visited
    total_urls_visited += 1

    



    print(f"{YELLOW}[*] Crawling: {url}{RESET}")
    getAllWebsiteLinks(url)
    with open('total_urls_visited.pkl', 'wb') as f:
            pickle.dump(total_urls_visited, f)
    if total_urls_visited >= max_urls:
        return

    if total_urls_visited > 4:
            total_urls_visited -= 2
    #save total ulrs incase crash to just hop back in 
    for i in range(total_urls_visited,max_urls):
        
        link = link_list[i]
        total_urls_visited += 1
        print(total_urls_visited)
        print(f"{YELLOW}[*] Crawling: {link}{RESET}")
        getAllWebsiteLinks(link)
        with open(r'total_urls_visited.pkl', 'wb') as f:
            pickle.dump(total_urls_visited, f)
        if total_urls_visited >= max_urls:
            break




    


if __name__ == "__main__":
    crawl("https://oldnavy.gapcanada.ca/browse/category.do?cid=26061&mlink=5155,1,m_2",MAX_URLS)
    print("[+] Total Internal links:", len(link_set))
    