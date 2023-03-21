import requests
from bs4 import BeautifulSoup
import pickle
from urllib.parse import urlparse, urljoin
import os

# VER 1.01

os.chdir(r"oldnavy\pickle_files")
FILENAME = 'cataloged_images.pkl'
product_list = []
data = {}
MAX_DATA = 2


def productsOnly(filename):
    #Opens file with all related links in the website and takes out the websites with products
    with open(filename, 'rb') as f: link_list = pickle.load(f)
    for link in link_list:
        if "/product" in link:
            product_list.append(link)
            print(link)
    with open('product_list.pkl', 'wb') as f:
                pickle.dump(product_list, f)



def catalogImages(filename):
    with open(filename, 'rb') as f: productlinks = pickle.load(f)

    #Goes through productlinks grabing the needed info 
    for i,link in enumerate(productlinks):
        baseurl = "https"+"://" + urlparse(link).netloc
        f = requests.get(link).text
        urmom = BeautifulSoup(f, 'lxml')

        #Grabs the product name from the HTML
        try:
            name = urmom.find("h1", class_ = "pdp-mfe-1t0oy2p").text #Gets the HTLM line that gets the product name
            if name is "None":
                raise
        except Exception as e:
            print("Name not found")
            print(e)
            print (link)
            continue



        #CHeck if the product name is already in it and if it is it only adds the image links for varriation
        images = urmom.find_all("a")
        if name in data:
            for tag in images:
                img = tag.attrs.get("href")
                if img is None:
                    continue
                if img.endswith("jpg"):
                    img = baseurl + img
                    data[name]["images"].add(img)
            continue

        
        #Grabs the product price
        try:
            price = urmom.find("span", class_ =  "pdp-pricing--highlight pdp-pricing__selected pdp-mfe-oan334").text #HTML Price 
            if price is None:
                raise
        except Exception as e:
            try:
                price = urmom.find("span", class_ =  "pdp-pricing__selected pdp-mfe-oan334").text
                if price is None:
                    raise   
            except:
                print("price not found")
                print(e)
                print (link)
                continue


        #images = [a['href'] for a in urmom.find_all('a', class_='hover-zoom hover-zoom-in pdp-mfe-1scitg2', href=True)]
        # Grabs the image links and adds it into a set so no dupelacates
        imageset = set()
        for tag in images:
            img = tag.attrs.get("href")
            if img == None:
                continue
            if img.endswith("jpg"):
                img = baseurl + img
                imageset.add(img)

        #inserts product into dictionary of  products 
        clothing = {"name": name, "price": price, "images": imageset, "link": link}
        print (clothing)
        data[name] = clothing
        print(i)
    return data

if __name__ == '__main__':
    productsOnly("link_list.pkl")
    data = catalogImages('product_list.pkl')# Saves and writes the catalog to a pkl file
    with open(FILENAME, 'wb') as f:
                pickle.dump(data, f)
    print(data)
