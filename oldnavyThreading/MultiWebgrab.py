from cgitb import html
from concurrent.futures import thread
from operator import index
import os 
from venv import main
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup,SoupStrainer
import colorama
import pickle
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import threading
from selenium.webdriver.chrome.options import Options
import time
# VER 1.01








def getAllWebsiteLinks(url):
    DRIVER = webdriver.Chrome(r"C:\Users\PyPit\OneDrive\Documents\CODE\python things\Cataloging websites\chromedriver.exe",options=CHROME_OPTIONS)
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
        if href in external_set or href in link_set or href in thread_link_set:
            continue
        
        if domain_name not in href:# if the domain name is not found the it will skip and add it to a set as cheecking a set is O(1)
            print(f"{RED}[*] External link: {href}{RESET}", flush=True)
            external_set.add(href)
            with open('external_set.pkl', 'wb') as f:
                pickle.dump(external_set, f)
            continue
                
        
        if href.endswith('jpg'):#if itss an image link do nnnot save 
            continue

        if "/browse" not in parsed_href.path: #If itss not apart of the browse branch of the website witch contains products and catalogs
            link_set.add(href)
            continue


            
        print(f"{GREEN}[*] Internal link: {href}{RESET}", flush=True)# Save the link 
        thread_link_set.add(href)

        
        



def isValid(url):
    """Checks whether `url` is a valid URL.
    Args:
        filename: the pickle file containing the list
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)



def crawl(url,NUM_BATCHES=30):
    global total_batches_done # number of batches done
    global link_set # all wesite links colected into a set this set is seperate from the list containing the website links that should not be checked and ones that are already in the list
    global thread_link_set # shared set each batch connects to that gets added to the main storage set
    """
    ALl THE LINKS FOUND ON THE WEBSITE
        Args: 
        url: starting home url
        NUM_BATCHES: default number of batches to do
    """
    if total_batches_done < 1:
        print(f"{YELLOW}[*] Crawling: {url}{RESET}")
        getAllWebsiteLinks(url)
        print(len(thread_link_set))
        link_set |= thread_link_set
        link_list.extend(list(thread_link_set))
        print(len(link_list))
        thread_link_set = set()
        with open('total_batches_done.pkl', 'wb') as f:
                pickle.dump(total_batches_done, f)
        if total_batches_done >= NUM_BATCHES:
            return
        with open('link_set.pkl', 'wb') as f:
            pickle.dump(link_set, f)
        with open('link_list.pkl', 'wb') as f:
            pickle.dump(link_list, f)

    #save total ulrs incase crash to just hop back in
     
    for i in range(total_batches_done,NUM_BATCHES):
        thread_batch_list = []# Creating list for threading batch
        if len(link_list) - total_batches_done*BATCH_SIZE < BATCH_SIZE: # checks if we are close to the end
            break
        
        for i in range(BATCH_SIZE):#filling batch
            link = link_list[i+total_batches_done*BATCH_SIZE]
            print(f"{YELLOW}[*] Crawling: {link}{RESET}")
            thread = threading.Thread(target=getAllWebsiteLinks,args=(link,)) #creating the thread
            thread_batch_list.append(thread) # adding the thread to list


        for thread in thread_batch_list: #starting the threads
            thread.start()
        for thread in thread_batch_list: #waiting for the threads
            thread.join()
        link_set |= thread_link_set #joining thread sets
        link_list.extend(list(thread_link_set))
        thread_link_set = set()
        total_batches_done += 1
        print(f"{total_batches_done*BATCH_SIZE}/{len(link_list)}")
        if total_batches_done >= NUM_BATCHES:
            break
        with open(r'total_batches_done.pkl', 'wb') as f:
                pickle.dump(total_batches_done, f)
        #Saves the file progress incase the program stops running as it takes two hours. If it does crash it starts from the saved index 
        with open('link_set.pkl', 'wb') as f:
            pickle.dump(link_set, f)
        with open('link_list.pkl', 'wb') as f:
            pickle.dump(link_list, f)


    if len(link_list) - total_batches_done*BATCH_SIZE < BATCH_SIZE:#second one is to clean up the links that didnt fit in batch size
        for i in range(total_batches_done*BATCH_SIZE,len(link_list)):
            link = link_list[i]
            print(f"{YELLOW}[*] Crawling: {link}{RESET}")
            thread = threading.Thread(target=getAllWebsiteLinks,args=(link,)) #creating the thread
            thread_batch_list.append(thread) # adding the thread to list


        for thread in thread_batch_list: #starting the threads
            thread.start()
        for thread in thread_batch_list: #waiting for the threads
            thread.join()
        link_set |= thread_link_set #joining thread sets
        link_list.extend(list(thread_link_set))
        thread_link_set = set()
        total_batches_done += 1
        print(f"{total_batches_done*BATCH_SIZE}/{len(link_list)}")
        with open(r'total_batches_done.pkl', 'wb') as f:
                pickle.dump(total_batches_done, f)
        #Saves the file progress incase the program stops running as it takes two hours. If it does crash it starts from the saved index 
        with open('link_set.pkl', 'wb') as f:
            pickle.dump(link_set, f)
        with open('link_list.pkl', 'wb') as f:
            pickle.dump(link_list, f)



    


if __name__ == "__main__":
    CHROME_OPTIONS = Options()
    CHROME_OPTIONS.add_argument("--headless")
    ONLY_A_TAGS = SoupStrainer("a")
    
    DELAY = 2 # seconds
    # driver.get("https://www.gapcanada.ca/browse/category.do?cid=6998")

    # html2 = driver.execute_script("return document.documentElement.innerHTML;")

    # soup = BeautifulSoup(html2, "html.parser", parse_only = ONLY_A_TAGS)
    # print (soup.prettify())




    #changing dir
    os.chdir(r"oldnavyThreading\pickle_files")

    link_set = set()
    external_set = set()
    link_list = []
    total_batches_done = 0

    thread_link_set = set()



    # if the total_batches_done is greater than it means that the prograam crashed and ton start where it left off 
    with open('total_batches_done.pkl', 'rb') as f: total_batches_done = pickle.load(f) 
    if total_batches_done > 0:
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

    # Size of batch
    BATCH_SIZE = 20
    #max amount of batches to visit each batch has 6 urls
    NUM_BATCHES = 500
    crawl("https://oldnavy.gapcanada.ca/browse/category.do?cid=26061",NUM_BATCHES)
    print("[+] Total Internal links:", len(link_set))
    