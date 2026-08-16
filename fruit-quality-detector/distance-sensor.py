# Created by Ciobanu Marius

# connection to counterfit IoT device
from counterfit_connection import CounterFitConnection
CounterFitConnection.init('127.0.0.1', 5000)

# imports
import time
from counterfit_shims_rpi_vl53l0x.vl53l0x import VL53L0X

# initialization of the distance sensor
distance_sensor = VL53L0X()
distance_sensor.begin()

# continuously read the distance and print it to the console
while True:
   distance_sensor.wait_ready()
   print(f'Distance = {distance_sensor.get_distance()} mm')
   time.sleep(1)