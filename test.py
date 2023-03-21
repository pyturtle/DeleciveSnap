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






with open(r'C:\Users\PyPit\OneDrive\Documents\CODE\python things\Cataloging websites\The-Gap\pickle_files\cataloged_images.pkl', 'rb') as f: productcataloging = pickle.load(f)

print (len(productcataloging))