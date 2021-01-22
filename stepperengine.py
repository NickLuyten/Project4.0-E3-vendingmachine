import RPi.GPIO as GPIO
import time

step1in1 = 5
step1in2 = 6
step1in3 = 13
step1in4 = 19

step2in1 = 1
step2in2 = 12
step2in3 = 16
step2in4 = 20

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

allPins = [5,6,13,19,1,12,16,20]
# Set all pins as output
for pin in allPins:
        GPIO.setup(pin,GPIO.OUT)


def stepper(stepper, delay):
    stepper = stepper
    if(stepper ==1):
        for i in range(510):
            GPIO.output(step1in1 , 1)
            time.sleep(delay)
            GPIO.output(step1in1 , 0)

            GPIO.output(step1in2 , 1)
            time.sleep(delay)
            GPIO.output(step1in2, 0)

            GPIO.output(step1in3, 1)
            time.sleep(delay)
            GPIO.output(step1in3, 0)

            GPIO.output(step1in4, 1)
            time.sleep(delay)
            GPIO.output(step1in4, 0)
    if(stepper ==2):
        for i in range(510):
            GPIO.output(step2in1 , 1)
            time.sleep(delay)
            GPIO.output(step2in1 , 0)

            GPIO.output(step2in2 , 1)
            time.sleep(delay)
            GPIO.output(step2in2, 0)

            GPIO.output(step2in3, 1)
            time.sleep(delay)
            GPIO.output(step2in3, 0)

            GPIO.output(step2in4, 1)
            time.sleep(delay)
            GPIO.output(step2in4, 0)


while True: 
    stepper(1,0.004)
    stepper(2,0.004)


