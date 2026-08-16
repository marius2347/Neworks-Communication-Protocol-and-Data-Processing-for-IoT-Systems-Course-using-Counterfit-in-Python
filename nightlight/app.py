# Created by Ciobanu Marius

# modules needed
import time 
import json
from counterfit_shims_grove.grove_light_sensor_v1_2 import GroveLightSensor
from counterfit_shims_grove.grove_led import GroveLed
from counterfit_connection import CounterFitConnection
import paho.mqtt.client as mqtt


# connect to the sensor
CounterFitConnection.init('127.0.0.1', 5000)


# instance for the light sensor
light_sensor = GroveLightSensor(0)

# instance for the led actuator
led = GroveLed(5)

# broker settings
id = '32a8176b-b3fc-42f7-83fd-9ee8fc7b2c25'
client_name = id + 'nightlight_client'

# topic
client_telemetry_topic = id + '/telemetry'
server_command_topic = id + '/commands'

# connector to MQTT Broker
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_name)
mqtt_client.connect('test.mosquitto.org')
mqtt_client.loop_start()
print("MQTT connected!")

# command topic function
def handle_command(client, userdata, message):
  payload = json.loads(message.payload.decode())
  print("Message received:", payload)
  if payload['led_on']:
      led.on()
  else:
      led.off()

mqtt_client.subscribe(server_command_topic)
mqtt_client.on_message = handle_command

# loop for printing the light telemetry and publish to the topic
while True:
   light = light_sensor.light
   telemetry = json.dumps({'light' : light})
   print("Sending telemetry ", telemetry)
   mqtt_client.publish(client_telemetry_topic, telemetry)
   time.sleep(5)
