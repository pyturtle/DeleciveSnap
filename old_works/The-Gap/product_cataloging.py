import requests
from bs4 import BeautifulSoup
import pickle
from urllib.parse import urlparse, urljoin
import os

# VER 1.01

os.chdir(r"The-Gap\pickle_files")
FILENAME = 'cataloged_images.pkl'
product_list = []
data = {}
MAX_DATA = 2


def productsOnly(filename):
    
    with open(filename, 'rb') as f: link_list = pickle.load(f)
    for link in link_list:
        if "/product" in link:
            product_list.append(link)
            print(link)
    with open('product_list.pkl', 'wb') as f:
                pickle.dump(product_list, f)


def catalogImages(filename):
    with open(filename, 'rb') as f: productlinks = pickle.load(f)
    for i,link in enumerate(productlinks):
        baseurl = "https"+"://" + urlparse(link).netloc
        f = requests.get(link).text
        page = BeautifulSoup(f, 'lxml')


        try:
            name = page.find("h1", class_ = "pdp-mfe-1q3bg7e").text
            if name is "None":
                raise
        except Exception as e:
            print("Name not found")
            print(e)
            print (link)
            continue




        images = page.find_all("a")
        if name in data:
            for tag in images:
                img = tag.attrs.get("href")
                if img is None:
                    continue
                if img.endswith("jpg"):
                    img = baseurl + img
                    data[name]["images"].add(img)
            continue


        try:
            price = page.find("span", class_ =  "pdp-pricing--highlight pdp-pricing__selected pdp-mfe-19nkmoj").text
            if price is None:
                raise
        except Exception as e:
            try:
                price = page.find("span", class_ =  "pdp-pricing__selected pdp-mfe-19nkmoj").text
                if price is None:
                    raise   
            except:
                print("price not found")
                print(e)
                print (link)
                continue


        #images = [a['href'] for a in page.find_all('a', class_='hover-zoom hover-zoom-in pdp-mfe-1scitg2', href=True)]

        imageset = set()
        for tag in images:
            img = tag.attrs.get("href")
            if img == None:
                continue
            if img.endswith("jpg"):
                img = baseurl + img
                imageset.add(img)


        clothing = {"name": name, "price": price, "images": imageset, "link": link}

        data[name] = clothing
        print(i)
    return data

if __name__ == '__main__':
    productsOnly("link_list.pkl")
    data = catalogImages('product_list.pkl')
    with open(FILENAME, 'wb') as f:
                pickle.dump(data, f)
    print(data)
