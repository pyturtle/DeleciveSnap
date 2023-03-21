from shlex import join
import requests
from bs4 import BeautifulSoup
import pickle
from urllib.parse import urlparse, urljoin
import os
import threading
import colorama


"""
Name: Nathan Nguyen
Date: 6/7/2022
Program Name : Delecive
Purpose: Catalog the products from an online store
"""

# VER 1.01
#TODO Have each product have their colour identifier in the name and a seperate dictionary to check and diffrienciate their referance images from other colours.
#TODO Colour will go at back of name eg: Prom dress BLUE

#Changing directory
os.chdir(r"TheGapThreading\pickle_files")
FILENAME = 'cataloged_images.pkl'
product_list = []
data = {}


#setting the colour text
colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW
RED = colorama.Fore.RED


def productsOnly(filename):
    """Filters out the links in a list that is not a product
    Args:
        filename: the pickle file containing the list
    """
    #Opens file with all related links in the website and takes out the websites with products
    with open(filename, 'rb') as f: link_list = pickle.load(f)
    for link in link_list:
        if "/product" in link:
            product_list.append(link)
            print(link)
    with open('product_list.pkl', 'wb') as f:
                pickle.dump(product_list, f)




def lightWebScraper(link):
    """Grabs the price Name and images from a given product page
    Args:
        Link: The link you want to scrap
    """

    baseurl = "https"+"://" + urlparse(link).netloc
    f = requests.get(link).text # temp holder for the html
    html_content = BeautifulSoup(f, 'lxml') # formated html

    #Grabs the product name from the HTML
    try:
        name = html_content.find("h1", class_ = "pdp-mfe-th2qfw").text #Gets the HTLM line that gets the product name
        if name == None:
            raise
    except Exception as e: 
        print(f"{RED}Name not found {link}{RESET}")
        print(e)
        return



    #Check if the product name is already in it and if it is it only adds the image links for varriation
    images = html_content.find_all("a")
    if name in data:
        for tag in images:
            img = tag.attrs.get("href")
            if img is None:
                return
            if img.rsplit("/", 1)[-1] in existing_images:
                return
            if img.endswith("jpg"):
                img = baseurl + img
                data[name]["images"].add(img)
                existing_images.add(img)
        return

    
    #Grabs the product price
    try:
        price = html_content.find("span", class_ =  "pdp-pricing--highlight pdp-pricing__selected pdp-mfe-19nkmoj").text #Checks first tag
        if price is None:
            raise
    except Exception as e:
        try:
            price = html_content.find("span", class_ =  "pdp-pricing__selected pdp-mfe-19nkmoj").text#Checks alternate
            if price is None:
                raise   
        except:
            print(f"{RED}price not found{link}{RESET}")
            print(e)
            return


    #images = [a['href'] for a in html_content.find_all('a', class_='hover-zoom hover-zoom-in pdp-mfe-1scitg2', href=True)]
    # Grabs the image links and adds it into a set so no dupelacates
    imageset = set()
    for tag in images:
        img = tag.attrs.get("href")
        if img == None:
            continue
        if img.endswith("jpg"):
            img = baseurl + img
            imageset.add(img)
            existing_images.add(img)

    #inserts product into dictionary of  products 
    clothing = {"name": name, "price": price, "images": imageset, "link": link}
    print (clothing)
    data[name] = clothing


def processThreads(function,batch):
    """Creates threads for multithreading and runs them
    Args:
        function: The function you are threading
        batch: the batch you are iterating over
    """
    threads = []
    for j in batch:# creating new threads
        thread = threading.Thread(target=function, args=(j,))
        threads.append(thread)
    for thread in threads: #starting the threads
        thread.start()
    for thread in threads: #waiting for the threads
        thread.join()

def catalogImages(filename):
    """Multithreading fucntion made to thread catalog images
    Args:
        filename: the path to the list of products
    """
    with open(filename, 'rb') as f: productlinks = pickle.load(f)
    #Goes through productlinks grabing the needed info 
    current_batch = []
    for i,link in enumerate(productlinks):
        current_batch.append(link)
        if len(current_batch) == batch_size:#waiting for batch to fill
            processThreads(lightWebScraper,current_batch) #using batch
            current_batch = []
    if len(current_batch) > 0: # Cleans up the remaining links that could not fit into BatchSize
        threads = []
        processThreads(lightWebScraper,current_batch) # using batch
    return data



if __name__ == '__main__':
    batch_size = 100
    existing_images = set()
    productsOnly("link_list.pkl")
    data = catalogImages('product_list.pkl')# Saves and writes the catalog to a pkl file
    with open(FILENAME, 'wb') as f:
                pickle.dump(data, f)
    print(data)
