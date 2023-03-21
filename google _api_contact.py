from google.protobuf import field_mask_pb2 as field_mask
import pickle
import os
from google.cloud import vision


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'catalog-search-348918-9e15fab49a67.json'

# print (os.environ["GOOGLE_APPLICATION_CREDENTIALS"])




    
def listReferenceImages(
        project_id, location, product_id):
    """List all images in a product.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_id: Id of the product.
    """
    client = vision.ProductSearchClient()

    # Get the full path of the product.
    product_path = client.product_path(
        project=project_id, location=location, product=product_id)

    # List all the reference images available in the product.
    reference_images = client.list_reference_images(parent=product_path)

    # Display the reference image information.
    for image in reference_images:
        print('Reference image name: {}'.format(image.name))
        print('Reference image id: {}'.format(image.name.split('/')[-1]))
        print('Reference image uri: {}'.format(image.uri))
        print('Reference image bounding polygons: {}'.format(
            image.bounding_polys))

def listProductsInProduct_set(
        project_id, location, product_set_id,max_products):
    """List all products in a product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
    """
    client = vision.ProductSearchClient()

    # Get the full path of the product set.
    product_set_path = client.product_set_path(
        project=project_id, location=location,
        product_set=product_set_id)

    # List all the products available in the product set.
    products = client.list_products_in_product_set(name=product_set_path)

    # Display the product information.
    for i,product in enumerate(products):
        if i > max_products: break
        print('Product name: {}'.format(product.name))
        print('Product id: {}'.format(product.name.split('/')[-1]))
        print('Product display name: {}'.format(product.display_name))
        print('Product description: {}'.format(product.description))
        print('Product category: {}'.format(product.product_category))
        print('Product labels: {}'.format(product.product_labels))

def updateProductLabels(
        project_id, location, product_id, key_list, value_list):
    """Update the product labels.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_id: Id of the product.
        key: The key of the label.
        value: The value of the label.
    """
    client = vision.ProductSearchClient()

    # Get the name of the product.
    product_path = client.product_path(
        project=project_id, location=location, product=product_id)

    # Set product name, product label and product display name.
    # Multiple labels are also supported.
    key_value = []
    for (key,value) in zip(key_list,value_list):
        key_value.append(vision.Product.KeyValue(key=key, value=value))
    product = vision.Product(
        name=product_path,
        product_labels=key_value)

    # Updating only the product_labels field here.
    update_mask = field_mask.FieldMask(paths=['product_labels'])

    # This overwrites the product_labels.
    updated_product = client.update_product(
        product=product, update_mask=update_mask)

    # Display the updated product information.
    print('Product name: {}'.format(updated_product.name))
    print('Updated product labels: {}'.format(product.product_labels))

def createReferenceImage(
        project_id, location, product_id, reference_image_id, gcs_uri):
    """Create a reference image.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_id: Id of the product.
        reference_image_id: Id of the reference image.
        gcs_uri: Google Cloud Storage path of the input image.
    """
    client = vision.ProductSearchClient()

    # Get the full path of the product.
    product_path = client.product_path(
        project=project_id, location=location, product=product_id)

    # Create a reference image.
    reference_image = vision.ReferenceImage(uri=gcs_uri)

    # The response is the reference image with `name` populated.
    image = client.create_reference_image(
        parent=product_path,
        reference_image=reference_image,
        reference_image_id=reference_image_id)

    # Display the reference image information.
    print('Reference image name: {}'.format(image.name))
    print('Reference image uri: {}'.format(image.uri))


def addProductToProduct_set(
        project_id, location, product_id, product_set_id):
    """Add a product to a product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_id: Id of the product.
        product_set_id: Id of the product set.
    """
    client = vision.ProductSearchClient()

    # Get the full path of the product set.
    product_set_path = client.product_set_path(
        project=project_id, location=location,
        product_set=product_set_id)

    # Get the full path of the product.
    product_path = client.product_path(
        project=project_id, location=location, product=product_id)

    # Add the product to the product set.
    client.add_product_to_product_set(
        name=product_set_path, product=product_path)
    print('Product added to product set.')


def createProduct(
        project_id, location, product_id, product_display_name,
        product_category):
    """Create one product.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_id: Id of the product.
        product_display_name: Display name of the product.
        product_category: Category of the product.
    """
    client = vision.ProductSearchClient()

    # A resource that represents Google Cloud Platform location.
    location_path = f"projects/{project_id}/locations/{location}"

    # Create a product with the product specification in the region.
    # Set product display name and product category.
    product = vision.Product(
        display_name=product_display_name,
        product_category=product_category)

    # The response is the product with the `name` field populated.
    response = client.create_product(
        parent=location_path,
        product=product,
        product_id=product_id)

    # Display the product information.
    print('Product name: {}'.format(response.name))


def createProductSet(
        project_id, location, product_set_id, product_set_display_name):
    """Create a product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
        product_set_display_name: Display name of the product set.
    """
    client = vision.ProductSearchClient()

    # A resource that represents Google Cloud Platform location.
    location_path = f"projects/{project_id}/locations/{location}"

    # Create a product set with the product set specification in the region.
    product_set = vision.ProductSet(
            display_name=product_set_display_name)

    # The response is the product set with `name` populated.
    response = client.create_product_set(
        parent=location_path,
        product_set=product_set,
        product_set_id=product_set_id)

    # Display the product set information.
    print('Product set name: {}'.format(response.name))

def delete_product_set(project_id, location, product_set_id):
    """Delete a product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
    """
    client = vision.ProductSearchClient()

    # Get the full path of the product set.
    product_set_path = client.product_set_path(
        project=project_id, location=location,
        product_set=product_set_id)

    # Delete the product set.
    client.delete_product_set(name=product_set_path)
    print('Product set deleted.')

# list_products_in_product_set("catalog-search-348918","us-east1","PS_CLOTH-SHOE_070318",20)
# listReferenceImages("catalog-search-348918","us-east1","100% Recycled Nylon Relaxed Lightweight Puffer Vest")




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
        try:
            print('Status of processing line {} of the csv: {}'.format(
                i, status))
            # Check the status of reference image
            # `0` is the code for OK in google.rpc.Code.
            if status.code == 0:
                reference_image = result.reference_images[i]
                print(reference_image)
            else:
                print('Status code not OK: {}'.format(status.message))
        except Exception as e:
            print(e)


def getSimilarProductsFile(
        project_id,
        location,
        product_set_id,
        product_category,
        file_path,
        filter,
        max_results
):
    """Search similar products to image.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
        product_category: Category of the product.
        file_path: Local file path of the image to be searched.
        filter: Condition to be applied on the labels.
                Example for filter: (color = red OR color = blue) AND style = kids
                It will search on all products with the following labels:
                color:red AND style:kids
                color:blue AND style:kids
        max_results: The maximum number of results (matches) to return. If omitted, all results are returned.
    """
    # product_search_client is needed only for its helper methods.
    product_search_client = vision.ProductSearchClient()
    image_annotator_client = vision.ImageAnnotatorClient()

    # Read the image as a stream of bytes.
    with open(file_path, 'rb') as image_file:
        content = image_file.read()

    # Create annotate image request along with product search feature.
    image = vision.Image(content=content)

    # product search specific parameters
    product_set_path = product_search_client.product_set_path(
        project=project_id, location=location,
        product_set=product_set_id)
    product_search_params = vision.ProductSearchParams(
        product_set=product_set_path,
        product_categories=[product_category],
        filter=filter)
    image_context = vision.ImageContext(
        product_search_params=product_search_params)

    # Search products similar to the image.
    response = image_annotator_client.product_search(
        image,
        image_context=image_context,
        max_results=max_results
    )

    index_time = response.product_search_results.index_time
    print('Product set index time: ')
    print(index_time)

    results = response.product_search_results.results

    print('Search results:')
    for result in results:
        product = result.product
        print('Score(Confidence): {}'.format(result.score))
        print('Image name: {}'.format(result.image))


        print('Product name: {}'.format(product.name))
        print('Product display name: {}'.format(
            product.display_name))
        print('Product description: {}\n'.format(product.description))
        print('Product labels: {}\n'.format(product.product_labels))

def purgeProductsInProductSet(
        project_id, location, product_set_id, force):
    """Delete all products in a product set.
    Args:
        project_id: Id of the project.
        location: A compute region name.
        product_set_id: Id of the product set.
        force: Perform the purge only when force is set to True.
    """
    client = vision.ProductSearchClient()

    parent = f"projects/{project_id}/locations/{location}"

    product_set_purge_config = vision.ProductSetPurgeConfig(
        product_set_id=product_set_id)

    # The purge operation is async.
    operation = client.purge_products(request={
        "parent": parent,
        "product_set_purge_config": product_set_purge_config,
        # The operation is irreversible and removes multiple products.
        # The user is required to pass in force=True to actually perform the
        # purge.
        # If force is not set to True, the service raises an exception.
        "force": force
    })

    operation.result(timeout=500)

    print('Deleted products in product set.')

PROJECT_ID ="catalog-search-348918"
COMPUTE_REGION= "us-east1"
SET_NAME = "product_set"







# purgeProductsInProductSet(PROJECT_ID,COMPUTE_REGION,SET_NAME,True)



# importProductSets(PROJECT_ID,COMPUTE_REGION,"gs://csv_storage_bulk/csv_products.csv")

# importProductSets(PROJECT_ID,COMPUTE_REGION,"gs://csv_storage_bulk/csv_products2.csv")

# importProductSets(PROJECT_ID,COMPUTE_REGION,"gs://csv_storage_bulk/csv_products3.csv")



# listProductsInProduct_set(PROJECT_ID,COMPUTE_REGION,SET_NAME,30)

# listReferenceImages(PROJECT_ID,COMPUTE_REGION,"100% Organic Cotton Slub T-Shirt")

product = input("file path: ")
getSimilarProductsFile(PROJECT_ID,
    COMPUTE_REGION,
    SET_NAME,
    "apparel-v2",
    product,
    '',2)
