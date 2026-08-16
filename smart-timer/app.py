# Created by Ciobanu Marius

# importing necessary libraries
import requests
import time
from azure.cognitiveservices.speech import SpeechConfig, SpeechRecognizer

# setting up the speech recognizer with the API key, location, and language
speech_api_key = 'YOUR_SPEECH_API_KEY'
location = 'swedencentral'
language = 'en-GB'

# configuring the speech recognizer with the provided API key, location, and language
recognizer_config = SpeechConfig(
    subscription=speech_api_key,
    region=location,
    speech_recognition_language=language
)
recognizer = SpeechRecognizer(speech_config=recognizer_config)

# defining a function to process the recognized text and print it to the console
def process_text(text):
    print(text)

# defining a function to handle the recognized event and call the process_text function with the recognized text
def recognized(args):
    process_text(args.result.text)

# connecting the recognized event to the recognized function and starting continuous recognition
recognizer.recognized.connect(recognized)
recognizer.start_continuous_recognition()

while True:
    time.sleep(1)