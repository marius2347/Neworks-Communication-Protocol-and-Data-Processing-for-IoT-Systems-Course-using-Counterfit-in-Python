# Created by Ciobanu Marius

# connection to counterfit IoT device
from counterfit_connection import CounterFitConnection
CounterFitConnection.init('127.0.0.1', 5000)

# initialization of the camera
import io
import requests 
from counterfit_shims_picamera import PiCamera
camera = PiCamera()
camera.resolution = (640, 480)
camera.rotation = 0

# capture the image and save it in a buffer
image = io.BytesIO()
camera.capture(image, 'jpeg')
image.seek(0)

# save the image to a file
with open('image.jpg', 'wb') as image_file:
 image_file.write(image.read())

# send the image to the prediction endpoint
prediction_url = 'http://localhost/image'
headers = {
 'Content-Type' : 'application/octet-stream'
}

# reset the buffer position to the beginning before sending
image.seek(0)
response = requests.post(prediction_url, headers=headers, data=image)
results = response.json()

# print the predictions
for prediction in results['predictions']:
 print(f'{prediction["tagName"]}:\t{prediction["probability"] * 100:.2f}%')