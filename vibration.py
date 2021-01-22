import RPi.GPIO as GPIO
import time

sensor = 16
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor, GPIO.IN)

def callback(sensor):
    print("movement detected")
    time.sleep(10)
    print("klaar")

GPIO.add_event_detect(sensor, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(sensor, callback)

while True:
    time.sleep(1)
    print(".")