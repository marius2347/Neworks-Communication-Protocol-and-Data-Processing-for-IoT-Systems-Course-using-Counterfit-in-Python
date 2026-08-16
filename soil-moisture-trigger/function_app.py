# Created by Marius CIOBANU
import azure.functions as func
import datetime
import json
import logging
import os
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import CloudToDeviceMethod

app = func.FunctionApp()


app = func.FunctionApp()
@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="", connection="IOT_HUB_CONNECTION_STRING")

def iothubtrigger(azeventhub: func.EventHubEvent): 
    logging.info('Python EventHub trigger processed an event: %s',
    azeventhub.get_body().decode('utf-8'))
    body = json.loads(azeventhub.get_body().decode('utf-8'))
    device_id = azeventhub.iothub_metadata['connection-device-id']
    logging.info(f'Received message: {body} from {device_id}')
    soil_moisture = body['soil_moisture']

    if soil_moisture > 450:
        direct_method = CloudToDeviceMethod(method_name='relay_on', payload='{}')
    else:
        direct_method = CloudToDeviceMethod(method_name='relay_off', payload='{}')

    logging.info(f'Sending direct method request for {direct_method.method_name} for device {device_id}')
    registry_manager_connection_string = os.environ['REGISTRY_MANAGER_CONNECTION_STRING']
    registry_manager = IoTHubRegistryManager(registry_manager_connection_string)
    registry_manager.invoke_device_method(device_id, direct_method)
    logging.info('Direct method request sent!')

# This example uses SDK types to directly access the underlying EventData object provided by the Event Hubs trigger.
# To use, uncomment the section below and add azurefunctions-extensions-bindings-eventhub to your requirements.txt file
# Ref: aka.ms/functions-sdk-eventhub-python
#
# import azurefunctions.extensions.bindings.eventhub as eh
# @app.event_hub_message_trigger(
#     arg_name="event", event_hub_name="eventhubname", connection="EventHubConnectionString"
# )
# def iothubtrigger(event: eh.EventData):
#     logging.info(
#         "Python EventHub trigger processed an event %s",
#         event.body_as_str()
#     )
