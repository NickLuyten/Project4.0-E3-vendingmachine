import RPi.GPIO as GPIO
import time

servoPIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 18 for PWM with 50Hz
p.start(7.5) # Initialization

def servomotor(status):
    if status == "open":
        p.ChangeDutyCycle(5)
    elif status == "close":
        p.ChangeDutyCycle(7.5)


try:
  while True:
    servomotor("open")
    print("5")
    time.sleep(2)
    
    servomotor("close")
    print("2.5")
    time.sleep(2)
except KeyboardInterrupt:
  p.stop()
  GPIO.cleanup()