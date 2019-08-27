import requests
from enum import Enum
import os
import json

endpoint = "http://127.0.0.1:5000"

class Conditions(Enum):
    NotConnected = 0,
    Connected = 1

class Actions(Enum):
    GET_SERVER_TIME = 1,
    POST_SEND_TELEMETRY = 2,
    POST_SEND_LOCK_INFO = 3,
    POST_LOGIN = 4,
    GET_EXIT = 5,

class Client:
    def __init__(self):
        self.team_no = -1
        self.condition = Conditions.NotConnected

        if(os.path.exists("log.txt")):
            os.remove("log.txt")
        self.log_file = open("log.txt","w")

    def log(self, action, status_code, message):
        if(status_code == 200):
            self.log_file.write("[ {0} ] ( Succeded ) : {1}\n".format(Actions(action),message))
        elif(status_code == 204):
            self.log_file.write("[ {0} ] ( Wrong format ) : {1}\n".format(Actions(action),message))
        elif(status_code == 400):
            self.log_file.write("[ {0} ] ( Request is wrong or not valid ) : {1}\n".format(Actions(action),message))
        elif(status_code == 401):
            self.log_file.write("[ {0} ] ( Unauthorized access ) : {1}\n".format(Actions(action),message))
        elif(status_code == 403):
            self.log_file.write("[ {0} ] ( You have no permission to access ) : {1}\n".format(Actions(action),message))
        elif(status_code == 404):
            self.log_file.write("[ {0} ] ( Invalid URL ) : {1}\n".format(Actions(action),message))
        elif(status_code == 500):
            self.log_file.write("[ {0} ] ( Server error ) : {1}\n".format(Actions(action),message))
        else:
            self.log_file.write("[ {0} ] ( Unknown status code ) : {1}\n".format(Actions(action),message))


    def login(self,name,password):
        data = {
            "kadi" : name,
            "sifre" : password
        }
        headers = {'content-type': 'application/json'}
        response = requests.post(url=endpoint+"/api/giris", data=json.dumps(data), headers=headers)
        self.log(Actions.POST_LOGIN,response.status_code,response.json())
        if(response.status_code == 200):
            print("Login succeded.")
            data = response.json()
            self.team_no = data
            self.condition = Conditions.Connected
            print("Team no : {}".format(self.team_no))
        else:
            print("Login was not successful")
            print("Error : {}".format(response.text))

    def get_server_time(self):
        response = requests.get(url=endpoint + "/api/sunucusaati")
        self.log(Actions.GET_SERVER_TIME,response.status_code,response.json())
        return response.json()

    def send_telemetry_data(self, data):
        headers = {'content-type': 'application/json'}
        response = requests.post(url=endpoint + "/api/telemetri_gonder", data=json.dumps(data), headers=headers)
        self.log(Actions.POST_SEND_TELEMETRY, response.status_code, response.json())
        data = response.json()
        #server_time = data["sistemSaati"]
        #location_infos = data["konumBilgileri"]


    def close_connection(self):
        headers = {'content-type': 'application/json'}
        data = {"team_no" : self.team_no}
        response = requests.post(url=endpoint + "/api/cikis", data=json.dumps(data), headers=headers)
        self.log(Actions.GET_EXIT, response.status_code, response.json())

    def clean_up(self):
        self.log_file.close()


client = Client()
client.login("astav","astav")
#
telemetry_data = {
    "takim_numarasi": client.team_no,
    "IHA_enlem": 433.5,
    "IHA_boylam": 222.3,
    "IHA_irtifa": 222.3,
    "IHA_dikilme": 5,
    "IHA_yonelme": 256,
    "IHA_yatis": 0,
    "IHA_hiz": 223,
    "IHA_batarya": 20,
    "IHA_otonom": 0,
    "IHA_kilitlenme": 1,
    "Hedef_merkez_X": 315,
    "Hedef_merkez_Y": 220,
    "Hedef_genislik": 12,
    "Hedef_yukseklik": 46,
    "GPSSaati": {
        "saat": 19,
        "dakika": 1,
        "saniye": 23,
        "milisaniye": 507
    }
}

client.send_telemetry_data(telemetry_data)
client.send_telemetry_data(telemetry_data)
client.send_telemetry_data(telemetry_data)
#
client.close_connection()
client.clean_up()