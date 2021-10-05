import os

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__


def upload(local_path, local_file_name, container_name):
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)
    upload_file_path = os.path.join(local_path, local_file_name)
    with open(upload_file_path, "rb") as data:
        blob_client.upload_blob(data)