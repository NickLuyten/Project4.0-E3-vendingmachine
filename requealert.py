import requests

response = requests.post('https://project4-restserver.herokuapp.com//api/alert/machineAbuse/1')

print(response.json())