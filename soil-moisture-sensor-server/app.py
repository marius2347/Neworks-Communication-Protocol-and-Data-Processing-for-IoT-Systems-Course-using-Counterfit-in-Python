# Created by Marius CIOBANU
import json
import time
import paho.mqtt.client as mqtt
import threading

# broker settings
id = 'ea1f9c61-27ef-4a2a-92cd-0e9faf11588a'
client_telemetry_topic = id + '/telemetry'
server_command_topic = id + '/commands'
client_name = id + 'soilmoisturesensor_server'
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()

# timing settings
water_time = 5
wait_time = 20

# function to send relay command
def send_relay_command(client, state):
    command = { 'relay_on' : state }
    print("Sending message:", command)
    client.publish(server_command_topic, json.dumps(command))

# function to control relay
def control_relay(client):
    print("Unsubscribing from telemetry")
    mqtt_client.unsubscribe(client_telemetry_topic)
    send_relay_command(client, True)
    time.sleep(water_time)
    send_relay_command(client, False)
    time.sleep(wait_time)
    print("Subscribing to telemetry")
    mqtt_client.subscribe(client_telemetry_topic)

# function to handle telemetry
def handle_telemetry(client, userdata, message):
    payload = json.loads(message.payload.decode())
    print("Message received:", payload)
    if payload['soil_moisture'] > 450:
        threading.Thread(target=control_relay, args=(client,)).start()

mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.on_message = handle_telemetry

# run the program
while True:
    time.sleep(2)