#Project 4.0 team E3 Smart Vendors 2020-2021
#Smart vending machine code

#   fill in authentication key
#   open http://localhost/indexscanner.html
#   scan QR-code
#   receive hand sanSitizer if code was OK

#   if machine vibration is to much
#   => Warning message is displayed for 10sec

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

#standard messages, these get updated if handgel is requested
welcomeMessage = "welkom op onze smart vending machine"
handGelMessage = "hier is uw handgel"
handGelOutOfStockMessage = "sorry we hebben geen hand gel meer"
authenticationFailedMessage = "u kon niet ingelogd geraken, probeer opnieuw aub"
errorMessage = "er is iets foutgelopen"
limitHandSanitizerReacedMessage = "maximum bereikt"
stock = 10
error = ""

#pubnub is used for the communication between site and program-
pnconfig = PNConfiguration() 
pnconfig.subscribe_key = 'sub-c-4a5481fa-5a4d-11eb-bf6e-f20b4949e6d2' 
pnconfig.publish_key = 'pub-c-f9d086de-b97a-43ce-bff5-e6cb64ecf29d' 
pubnub = PubNub(pnconfig) 
channel = 'scanner' 

buzzer = Buzzer(26)

cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

sensor = 21 #vibration sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor, GPIO.IN)
GPIO.setwarnings(False)

step1 = 20
step2 = 16
step3 = 12
step4 = 1

led = 19

allPins = [step1,step2,step3,step4,led]
# Set all pins as output
for pin in allPins:
        GPIO.setup(pin,GPIO.OUT)

#global variables can be used inside functions
global scanner
scanner = 0

global warning
warning = 0

afnemen = 0

authenticeren = 0

#if debug == 1, debug messages will be printed in terminal
global debug
debug = 1

#subscribe to pubnub channel
def subscriben():
    if debug:
        print('DEBUG: subscribed to channel, waiting for request') 
    pubnub.add_listener(MySubscribeCallback_ITF()) 
    pubnub.subscribe().channels('scanner').execute()

#callback function when pubnub channel receives a message
class MySubscribeCallback_ITF(SubscribeCallback): 
        def message (self, pubnub, message): 
                if message.message == 'scan':
                        global scanner 
                        scanner = 1
                        if debug:
                            print('DEBUG: opening camera module')

#callback function if vibration sensor gets warning                       
def callback(sensor):
    global warning 
    warning = 1

#stepper engine turns 1 round
def stepper(delay):
    for i in range(520): #changing this value will make stepper engine turn more
        GPIO.output(step1 , 1)
        GPIO.output(step2 , 1)

        time.sleep(delay)

        GPIO.output(step1 , 0)
        GPIO.output(step2 , 1)
        GPIO.output(step3 , 1)

        time.sleep(delay)

        GPIO.output(step2, 0)
        GPIO.output(step3, 1)
        GPIO.output(step4, 1)

        time.sleep(delay)
    
        GPIO.output(step3, 0)
        GPIO.output(step4, 1)
        GPIO.output(step1, 1)

        time.sleep(delay)

        GPIO.output(step4, 0) 

#add callback funtion for vibration sensor
GPIO.add_event_detect(sensor, GPIO.BOTH, bouncetime=1000)
GPIO.add_event_callback(sensor, callback)

#if all things are setup this part wil be looped forever
while True:
    #on startup the machine needs to be authenticated with api key
    if authenticeren == 0:
        key = input("Authentication key: ")
        response = requests.get('https://project4-restserver.herokuapp.com/api/vendingMachine/testApiKey',headers = {'api-key':key}) #checks if api-key is in database
        if debug:
            print("SERVER: " + str(response))
        if 'result' in response.json():
            if  response.json()['result'] == True:
                authenticeren = 1
                subscriben() #if api-key is correct, subscribe to pubnub channel
        else:
            print('Authentication key wrong, try again.')

    #if scanner = 1, open camera box and scan QR-code
    elif scanner == 1:
        _, img = cap.read()
        data, bbox, _ = detector.detectAndDecode(img)
        
        if bbox is not None:
            for i in range(len(bbox)):
                cv2.line(img, tuple(bbox[i][0]), tuple(bbox[(i+1) % len(bbox)][0]), color=(255,0, 0), thickness=2)
                
            cv2.putText(img, data, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 255, 0), 2)
            
            if data:
                scanner = 0
                buzzer.beep(0.1, 0.1, 2)
                if debug:
                    print("DEBUG: data found: " + data)
                #send code of QR to restserver
                response = requests.put('https://project4-restserver.herokuapp.com/api/vendingMachine/handgelAfnemen/',data = {'authentication':data},headers = {'api-key':key})
                print(response.json())
                #update all standard messages
                if('result' in response.json()):
                    welcomeMessage  = response.json()['result']['welcomeMessage']
                    handGelMessage = response.json()['result']['handGelMessage']
                    handGelOutOfStockMessage = response.json()['result']['handGelOutOfStockMessage']
                    authenticationFailedMessage = response.json()['result']['authenticationFailedMessage']
                    errorMessage = response.json()['result']['errorMessage']
                    stock = response.json()['result']['stock']

                    pubnub.publish().channel('scanner').message("welcomeMessage"+ welcomeMessage).sync()
                    pubnub.publish().channel('scanner').message("handGelMessage"+ handGelMessage).sync()

                    if debug:
                        print("DEBUG: updated all messages:")
                        print("   welcomeMessage = "+welcomeMessage)
                        print("   handGelMessage = "+handGelMessage)
                        print("   handGelMessage = "+handGelMessage)
                        print("   handGelOutOfStockMessage = " + handGelOutOfStockMessage)
                        print("   authenticationFailedMessage = " + authenticationFailedMessage)
                        print("   errorMessage = " + errorMessage)
                        print("   stock = " + str(stock))
                    afnemen = 1
                else:
                    error = response.json()['message']
                    if("out of stock" in error):
                        errorMessage = handGelOutOfStockMessage
                    
                    elif("user not autherized" in error):
                        errorMessage = "U hebt geen toegang tot deze vending machine!"

                    elif("Not found authentication" in error):
                        errorMessage = authenticationFailedMessage

                    elif("limit reached" in error):
                        errorMessage= limitHandSanitizerReacedMessage
                    
                    elif("vendingmachine not found with api-key!" in error):
                        errorMessage= "Api key is fout, contacteer de admin!"

                    else:
                        errorMessage = errorMessage

                    if debug:
                        print("DEBUG: "+errorMessage)

                    pubnub.publish().channel('scanner').message("errorMessage"+errorMessage).sync()
                data = ""

        cv2.imshow("code detector", img)
    
    else:
        cap.read()
        cv2.destroyAllWindows()
    
    if cv2.waitKey(1) == ord("q"):
        break

    if warning == 1:
        #send warning to website and restserver
        print("WARNING: movement detected")
        pubnub.publish().channel('scanner').message("warning").sync()
        x = requests.post('https://project4-restserver.herokuapp.com/api/alert/machineAbuse', headers = {'api-key': key})
        if debug:
            print("SERVER: " + str(x))
        x=0
        time.sleep(10)
        pubnub.publish().channel('scanner').message("warningDone").sync()
        warning = 0
    
    if afnemen == 1:
        #turn on led and dispence hand sanitizer
        cv2.destroyAllWindows()
        GPIO.output(led,1)
        stepper(0.004)
        afnemen = 0
        GPIO.output(led,0)


cap.release()
cv2.destroyAllWindows()