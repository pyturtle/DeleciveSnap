from cgitb import html
import os
from venv import main
import requests
import pickle
import os
from google.protobuf import field_mask_pb2 as field_mask
import pickle
import os
from google.cloud import vision
from google.cloud import storage
import threading
from time import sleep
from urllib.parse import urlparse, urljoin
import colorama

#
#
# VER 1.01
#
#


with open("cataloged_images.pkl", "rb") as f:
    cataloged_images = pickle.load(f)





os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "catalog-search-348918-9e15fab49a67.json"
os.chdir("imageTemp")
BUCKET_NAME = "gap_bucket"
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW

# TODO change this python file to detect and add straight to cloud rather than pc on


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print("File {} uploaded to {}.".format(source_file_name, destination_blob_name))


def upload_blob_from_memory(bucket_name, contents, destination_blob_name):
    """Uploads a file to the bucket."""

    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The contents to upload to the file
    # contents = "these are my contents"

    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_string(contents)

    print(
        "{} with contents {} uploaded to {}.".format(
            destination_blob_name, contents, bucket_name
        )
    )


def punctuatio_remover(s):
    punc_list = [".",";",":","!","?","/","\\",",","#","@","$",")","(","'s","\"","™","|","","™"]
        # "®",

    new_s = ""
    for i in s:
        if i not in punc_list:
            new_s += i
        else:
            new_s += " "
    return new_s


# driver.get("https://www.gapcanada.ca/browse/category.do?cid=6998")

# html2 = driver.execute_script("return document.documentElement.innerHTML;")

# soup = BeautifulSoup(html2, "html.parser", parse_only = ONLY_A_TAGS)
# print (soup.prettify())
def grab_and_upload(link,name):
    print (link)
    response = requests.get(link)
    file = open(name, "wb")
    file.write(response.content)
    sleep(5)
    file.close()
    upload_blob(BUCKET_NAME, name, name)
    sleep(8)
    os.remove(name)

def isValid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

batch_size = 100
batch_dict = {}

for i in cataloged_images: # iterating over each product
    try:
        for n in cataloged_images[i]["images"]: # each referance image gets their own line so I go over each image in the product
            batch_dict[n] = (
                punctuatio_remover(cataloged_images[i]["name"]) + n.rsplit("/", 1)[-1]# to get the image name I will take the ending of the given image name file and add the name of the product to the start
            )  # product name plus image name
            if len(batch_dict) == batch_size:
                thread_batch_list = []
                for image_link, name in batch_dict.items():
                    thread = threading.Thread(
                        target=grab_and_upload,
                        args=(
                            image_link,
                            name,
                        ),
                    )  # creating the thread
                    thread_batch_list.append(thread)  # adding the thread to list
                for thread in thread_batch_list:  # starting the threads
                    thread.start()
                for thread in thread_batch_list:  # waiting for the threads
                    thread.join()
                batch_dict = {}  # reseting batch
                
    
    except Exception as e:
        print(f"{YELLOW}{e}{RESET}")
try:        
    #second thread to clean up the products which is now less than batch size
    if len(batch_dict) > 0:
        thread_batch_list = []
        for image_link, name in batch_dict.items():
            thread = threading.Thread(
                target=grab_and_upload,
                args=(
                    image_link,
                    name,
                ),
            )  # creating the thread
            thread_batch_list.append(thread)  # adding the thread to list
        for thread in thread_batch_list:  # starting the threads
            thread.start()
        for thread in thread_batch_list:  # waiting for the threads
            thread.join()
except Exception as e:
        print(f"{YELLOW}{e}{RESET}")

# changing dir
