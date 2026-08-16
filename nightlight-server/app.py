# Created by Marius CIOBANU
import json
import time
import paho.mqtt.client as mqtt

# broker settings
id = '32a8176b-b3fc-42f7-83fd-9ee8fc7b2c25'
client_telemetry_topic = id + '/telemetry' 

# send command topic
server_command_topic = id + '/commands'
client_name = id + '_nightlight_server'
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()

# function to load the message
def handle_telemetry(client, userdata, message):
   payload = json.loads(message.payload.decode())
   print("Message received:", payload)

   command = { 'led_on' : payload['light'] < 300 }
   print("Sending message:", command)
   client.publish(server_command_topic, json.dumps(command))

# subscribe to the topic
mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.on_message = handle_telemetry

while True:
    time.sleep(2)