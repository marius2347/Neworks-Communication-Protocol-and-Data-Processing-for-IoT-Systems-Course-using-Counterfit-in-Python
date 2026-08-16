# Created by Marius CIOBANU
import json
import time
import paho.mqtt.client as mqtt
from os import path
import csv
from datetime import datetime

# broker settings
id = '989559b7-9373-4b46-8ceb-cb007195f915'
client_telemetry_topic = id + '/telemetry'
client_name = id + 'temperature_sensor_server'
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()

# save to csv
temperature_file_name = 'temperature.csv'
fieldnames = ['date', 'temperature']

# create csv file
if not path.exists(temperature_file_name):
    with open(temperature_file_name, mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

# function to handle telemetry
def handle_telemetry(client, userdata, message):
    payload = json.loads(message.payload.decode())
    print("Message received:", payload)
    with open(temperature_file_name, mode='a') as temperature_file:
        temperature_writer = csv.DictWriter(temperature_file,
        fieldnames=fieldnames)
        temperature_writer.writerow({'date' :
        datetime.now().astimezone().replace(microsecond=0).isoformat(),
        'temperature' : payload['temperature']})

mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.on_message = handle_telemetry

# run the program
while True:
    time.sleep(2)