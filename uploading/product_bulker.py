from cgitb import html
import os 
from venv import main
import pickle
import os
from google.protobuf import field_mask_pb2 as field_mask
import pickle
import os
from google.cloud import vision
from google.cloud import storage
import csv
# VER 1.01
#


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\PyPit\OneDrive\Documents\CODE\python things\google_api_file\catalog-search-348918-9e15fab49a67.json"
with open('cataloged_images.pkl', 'rb') as f: cataloged_images = pickle.load(f)
BUCKET_NAME = "gap_bucket"
os.chdir("uploading")
SET_NAME = "product_set"
CSV_NAME = 'csv_products.csv'

# open the file in the write mode
file_cvs = open(CSV_NAME, 'w',encoding="utf-8",newline='')
# create the csv writer
writer = csv.writer(file_cvs)


def uploadBlob(bucket_name, source_file_name, destination_blob_name):
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

    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )



def importProductSets(project_id, location, gcs_uri):
    """Import images of different products in the product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        gcs_uri: Google Cloud Storage URI.
            Target files must be in Product Search CSV format.
    """
    client = vision.ProductSearchClient()

    # A resource that represents Google Cloud Platform location.
    location_path = f"projects/{project_id}/locations/{location}"

    # Set the input configuration along with Google Cloud Storage URI
    gcs_source = vision.ImportProductSetsGcsSource(
        csv_file_uri=gcs_uri)
    input_config = vision.ImportProductSetsInputConfig(
        gcs_source=gcs_source)

    # Import the product sets from the input URI.
    response = client.import_product_sets(
        parent=location_path, input_config=input_config)

    print('Processing operation name: {}'.format(response.operation.name))
    # synchronous check of operation status
    result = response.result()
    print('Processing done.')

    for i, status in enumerate(result.statuses):
        print('Status of processing line {} of the csv: {}'.format(
            i, status))
        # Check the status of reference image
        # `0` is the code for OK in google.rpc.Code.
        if status.code == 0:
            reference_image = result.reference_images[i]
            print(reference_image)
        else:
            print('Status code not OK: {}'.format(status.message))





def split(filehandler, delimiter=',', row_limit=10000,
          output_name_template='output_%s.csv', output_path='.', keep_headers=True):
    import csv
    reader = csv.reader(filehandler, delimiter=delimiter)
    current_piece = 1
    current_out_path = os.path.join(
        output_path,
        output_name_template % current_piece
    )
    current_out_writer = csv.writer(open(current_out_path, 'w',newline=''), delimiter=delimiter)
    current_limit = row_limit
    if keep_headers:
        headers = reader.next()
        current_out_writer.writerow(headers)
    for i, row in enumerate(reader):
        if i + 1 > current_limit:
            current_piece += 1
            current_limit = row_limit * current_piece
            current_out_path = os.path.join(
                output_path,
                output_name_template % current_piece
            )
            current_out_writer = csv.writer(open(current_out_path, 'w',newline=''), delimiter=delimiter)
            if keep_headers:
                current_out_writer.writerow(headers)
        current_out_writer.writerow(row)


def punctuatioRemover(s):
    punc_list = [".",";",":","!","?","/","\\",",","#","@","$",")","(","'s","\"","™","|",""]
    new_s = ''
    for i in s:
        if i not in punc_list:
            new_s += i
        else:
            new_s += ' '
    return new_s



# driver.get("https://www.gapcanada.ca/browse/category.do?cid=6998")

# html2 = driver.execute_script("return document.documentElement.innerHTML;")

# soup = BeautifulSoup(html2, "html.parser", parse_only = ONLY_A_TAGS)
# print (soup.prettify())
# gs://product_search_catalog/unknown.png


for num,i in enumerate(cataloged_images):
    try:
        for n in cataloged_images[i]["images"]:
            #product and image details
            product_name = cataloged_images[i]["name"] 
            product_id = punctuatioRemover(product_name)
            image_id = product_id+n.rsplit('/', 1)[-1] # to get the image name I will take the ending of the given image link and add the name of the product to the start
            gcs_name = f"gs://{BUCKET_NAME}/{image_id}"
            product_catagory = "apparel-v2"
            labels = f"store=TheGap,price=" + cataloged_images[i]["price"]+",link="+ cataloged_images[i]["link"]
            row = [gcs_name,image_id,SET_NAME,product_id,product_catagory,product_name,labels,""]
            print(f"{row}\n{num}")
            # write a row to the csv file
            writer.writerow(row)


            
    except Exception as e:
        print(e)

# close the file
f.close()
uploadBlob("csv_storage_bulk",CSV_NAME,CSV_NAME)
#split file
# split(open(CSV_NAME,"r"))
# Upload file to Google Cloud Storage




    