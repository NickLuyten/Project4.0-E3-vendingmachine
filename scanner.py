from gpiozero import LED, Button, Buzzer
import cv2
import re
import time 
import sys 
from pubnub.pnconfiguration import PNConfiguration 
from pubnub.pubnub import PubNub 
from pubnub.callbacks import SubscribeCallback 
import requests
import RPi.GPIO as GPIO

welcomeMessage = "welkom op onze smart vending machine"
handGelMessage = "hier is uw handgel"
handGelOutOfStockMessage = "sorry we hebben geen hand gel meer"
authenticationFailedMessage = "u kon niet ingelogd geraken, probeer opnieuw aub"
errorMessage = "er is iets foutgelopen"
limitHandSanitizerReacedMessage = "maximum bereikt"
stock = 10
error = ""
 
pnconfig = PNConfiguration() 
pnconfig.subscribe_key = 'sub-c-4a5481fa-5a4d-11eb-bf6e-f20b4949e6d2' 
pnconfig.publish_key = 'pub-c-f9d086de-b97a-43ce-bff5-e6cb64ecf29d' 
pubnub = PubNub(pnconfig) 
channel = 'scanner' 

buzzer = Buzzer(26)

cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

sensor = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor, GPIO.IN)
GPIO.setwarnings(False)

servoPIN = 18

step1in1 = 5
step1in2 = 6
step1in3 = 13
step1in4 = 19

step2in1 = 1
step2in2 = 12
step2in3 = 16
step2in4 = 20

allPins = [step1in1,step1in2,step1in3,step1in4,step2in1,step2in2,step2in3,step2in4,servoPIN]
# Set all pins as output
for pin in allPins:
        GPIO.setup(pin,GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 18 for PWM with 50Hz
#p.start(7.5) # Initialization

global scanner
scanner = 0

global warning
warning = 0

afnemen = 0

print("Reading QR code using Raspberry Pi camera")

class MySubscribeCallback_ITF(SubscribeCallback): 
        def message (self, pubnub, message): 
                if message.message == 'scan':
                        global scanner 
                        scanner = 1
                        print('start scanning')
                if message.message == 'get':
                        print('1 hand gel please')
                        
def callback(sensor):
    print("movement detected")
    pubnub.publish().channel('scanner').message("warning").sync()
    x = requests.post('https://project4-restserver.herokuapp.com/api/alert/machineAbuse/1')
    x=0
    global warning 
    warning = 1
    
def servomotor(status):
    p.start(7.5) # Initialization
    if status == "open":
        p.ChangeDutyCycle(5)
    elif status == "close":
        p.ChangeDutyCycle(7.5)
        time.sleep(0.5)
        p.stop()

def stepper(delay):
    servomotor("open")
    for i in range(520):
        GPIO.output(step2in1 , 1)
        GPIO.output(step2in2 , 1)

        time.sleep(delay)

        GPIO.output(step2in1 , 0)
        GPIO.output(step2in2 , 1)
        GPIO.output(step2in3 , 1)

        time.sleep(delay)

        GPIO.output(step2in2, 0)
        GPIO.output(step2in3, 1)
        GPIO.output(step2in4, 1)

        time.sleep(delay)
    
        GPIO.output(step2in3, 0)
        GPIO.output(step2in4, 1)
        GPIO.output(step2in1, 1)

        time.sleep(delay)

        GPIO.output(step2in4, 0) 
    servomotor("close")

print('Listening...') 
pubnub.add_listener(MySubscribeCallback_ITF()) 
pubnub.subscribe().channels('scanner').execute()


GPIO.add_event_detect(sensor, GPIO.BOTH, bouncetime=300)
GPIO.add_event_callback(sensor, callback)

while True:
    if scanner == 1:

        _, img = cap.read()
        data, bbox, _ = detector.detectAndDecode(img)
        
        if bbox is not None:
            for i in range(len(bbox)):
                cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255,0, 0), thickness=2)
                
            cv2.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 255, 0), 2)
            
            if data:
                scanner = 0
                buzzer.beep(0.1, 0.1, 1)
                print("Data found: " + data)
                response = requests.put('https://project4-restserver.herokuapp.com/api/vendingMachine/handgelAfnemen/1',data = {'authentication':data})
                if('result' in response.json()):
                    welcomeMessage  = response.json()['result']['welcomeMessage']
                    print("welcomeMessage = "+welcomeMessage)

                    handGelMessage = response.json()['result']['handGelMessage']
                    print("handGelMessage = "+handGelMessage)

                    handGelOutOfStockMessage = response.json()['result']['handGelOutOfStockMessage']
                    print("handGelOutOfStockMessage = " + handGelOutOfStockMessage)

                    authenticationFailedMessage = response.json()['result']['authenticationFailedMessage']
                    print("authenticationFailedMessage = " + authenticationFailedMessage)

                    errorMessage = response.json()['result']['errorMessage']
                    print("errorMessage = " + errorMessage)

                    stock = response.json()['result']['stock']
                    print("stock = " + str(stock))

                    pubnub.publish().channel('scanner').message("welcomeMessage"+ welcomeMessage).sync()
                    pubnub.publish().channel('scanner').message("handGelMessage"+ handGelMessage).sync()

                    afnemen = 1

                else:
                    error = response.json()['message']
                    if("out of stock" in error):
                        errorMessage = handGelOutOfStockMessage
                        print(errorMessage)
                    
                    elif("user not autherized" in error):
                        errorMessage = "U hebt geen toegang tot deze vending machine!"
                        print(errorMessage)

                    elif("Not found authentication" in error):
                        errorMessage = authenticationFailedMessage
                        print(errorMessage)

                    elif("limitHandSanitizerReacedMessage" in error):
                        errorMessage= limitHandSanitizerReacedMessage
                        print(errorMessage)

                    else:
                        errorMessage = errorMessage
                        print(errorMessage)
                    pubnub.publish().channel('scanner').message("errorMessage"+errorMessage).sync()
                data = ""

        cv2.imshow("code detector", img)
    
    else:
        cap.read()
        cv2.destroyAllWindows()
    
    if cv2.waitKey(1) == ord("q"):
        break

    if warning == 1:
        time.sleep(10)
        pubnub.publish().channel('scanner').message("warningDone").sync()
        warning = 0
    
    if afnemen == 1:
        cv2.destroyAllWindows()
        stepper(0.004)
        afnemen = 0


cap.release()
cv2.destroyAllWindows()