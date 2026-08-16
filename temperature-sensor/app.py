# Created by Marius CIOBANU
import time
import json
import paho.mqtt.client as mqtt
from counterfit_connection import CounterFitConnection
from counterfit_shims_seeed_python_dht import DHT

# connection
CounterFitConnection.init('127.0.0.1', 5000)

# instance sensor of temperature
sensor = DHT("11", 5)

# broker settings

id = '989559b7-9373-4b46-8ceb-cb007195f915'
client_name = id + 'temperature_sensor_client'
client_telemetry_topic = id + '/telemetry'
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()
print("MQTT connected!")

while True:
    temp = sensor.read()
    telemetry = json.dumps({'temperature' : temp})
    print("Sending telemetry ", telemetry)
    mqtt_client.publish(client_telemetry_topic, telemetry)
    time.sleep(10*60)