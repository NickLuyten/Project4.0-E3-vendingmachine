import requests
welcomeMessage = "welkom op onze smart vending machine"
handGelMessage = "hier is uw handgel"
handGelOutOfStockMessage = "sorry we hebben geen hand gel meer"
authenticationFailedMessage = "u kon niet ingelogd geraken, probeer opnieuw aub"
errorMessage = "er is iets foutgelopen"
stock = 10
error = ""

response = requests.put('https://project4-restserver.herokuapp.com/api/vendingMachine/handgelAfnemen/1',data = {'authentication':'d2915464-9bb7-4080-a321-fd27dbec8b83'})

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
else:
    error = response.json()['message']
    if("out of stock" in error):
        errorMessage = "Helaas, de handgels zijn op"
        print(errorMessage)
    
    elif("user not autherized" in error):
        errorMessage = "U hebt geen toegang tot deze vending machine!"
        print(errorMessage)

    elif("Not found authentication" in error):
        errorMessage = "geen toegang gevonden tot deze vending machine"
        print(errorMessage)

    else:
        errorMessage = "er is iets misgelopen"
        print(errorMessage)