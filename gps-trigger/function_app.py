# Created by Ciobanu Marius
import azure.functions as func
import datetime
import json
import logging
import os
import uuid
from azure.storage.blob import BlobServiceClient, PublicAccess

# create container if it does not exist
def get_or_create_container(name):
    connection_str = os.environ['STORAGE_CONNECTION_STRING']
    blob_service_client = BlobServiceClient.from_connection_string(connection_str)
    
    for container in blob_service_client.list_containers():
        if container.name == name:
            return blob_service_client.get_container_client(container.name)
        
    return blob_service_client.create_container(name, public_access=PublicAccess.Container)
  

app = func.FunctionApp()
@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="",
                               connection="IOT_HUB_CONNECTION_STRING", consumer_group="$Default") 
def iothubtrigger(azeventhub: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event: %s',
                azeventhub.get_body().decode('utf-8'))
    
    device_id=azeventhub.iothub_metadata['connection-device-id']
    blob_name = f'{device_id}/{str(uuid.uuid1())}.json'

    container_client = get_or_create_container('gps-data')
    blob = container_client.get_blob_client(blob_name)

    event_body = json.loads(azeventhub.get_body().decode('utf-8'))
    blob_body = { 
        'device_id' : device_id,
        'timestamp' : azeventhub.iothub_metadata['enqueuedtime'],
        'gps': event_body['gps']
    }

    logging.info(f'Writing blob to {blob_name} - {blob_body}')
    blob.upload_blob(json.dumps(blob_body).encode('utf-8'))

