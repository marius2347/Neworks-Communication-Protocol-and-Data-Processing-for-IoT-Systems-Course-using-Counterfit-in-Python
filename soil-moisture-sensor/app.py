# Created by Marius CIOBANU

# IMPORTS
import time
import json
from counterfit_connection import CounterFitConnection
from counterfit_shims_grove.adc import ADC
from counterfit_shims_grove.grove_relay import GroveRelay
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse, X509


# connection to counterfit
CounterFitConnection.init('127.0.0.1', 5000)
host_name = "sms-marius23-99x.azure-devices.net"
x509 = X509("soil-moisture-sensor-x509-cert.pem", "soil-moisture-sensor-x509-key.pem")
device_id = "soil-moisture-sensor-x509"

# create the device client and connect to Azure IoT Hub
device_client = IoTHubDeviceClient.create_from_x509_certificate(x509, host_name, device_id)
print('Connecting')
device_client.connect()
print('Connected')

# create the ADC and relay objects
adc = ADC()
relay = GroveRelay(5)

# function to handle direct method requests
def handle_method_request(request):
   print("Direct method received - ", request.name)
   if request.name == "relay_on":
        relay.on()
   elif request.name == "relay_off":
        relay.off()
   method_response = MethodResponse.create_from_method_request(request, 200)
   device_client.send_method_response(method_response)

device_client.on_method_request_received = handle_method_request

while True:
    soil_moisture = adc.read(0)
    print("Soil moisture:", soil_moisture)
    
    message = Message(json.dumps({ 'soil_moisture': soil_moisture }))
    device_client.send_message(message)
    
    time.sleep(10)