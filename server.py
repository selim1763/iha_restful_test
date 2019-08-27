from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse
import datetime
import json

app = Flask(__name__)
api = Api(app)


users = [
    {
        "kadi" : "astav",
        "sifre" : "astav",
        "takim_no" : 12345
    }
]

active_clients = []

class Client:
    def __init__(self, team_no):
        self.team_no = team_no
        self.telemetry_data = {}

    def update_telemetry_data(self, args):
        self.telemetry_data = args

    def get_enlem(self):
        return self.telemetry_data["IHA_enlem"]
    def get_boylam(self):
        return self.telemetry_data["IHA_boylam"]
    def get_irtifa(self):
        return self.telemetry_data["IHA_irtifa"]
    def get_dikilme(self):
        return self.telemetry_data["IHA_dikilme"]
    def get_yonelme(self):
        return self.telemetry_data["IHA_yonelme"]
    def get_yatis(self):
        return self.telemetry_data["IHA_yatis"]


def is_client_active(team_no):
    for x in range(len(active_clients)):
        if(team_no in active_clients[x]):
            return x
    return -1

def get_active_client(team_no):
    for client in active_clients:
        if(team_no in client):
            return client[team_no]
    return None

def get_location_infos():
    locations = []
    for cl_dict in active_clients:
        for k in cl_dict:
            client = cl_dict[k]
            loc_info = {
                "takim_numarasi": client.team_no,
                "iha_enlem": client.get_enlem(),
                "iha_boylam": client.get_boylam(),
                "iha_irtifa": client.get_irtifa(),
                "iha_dikilme": client.get_dikilme(),
                "iha_yonelme": client.get_yonelme(),
                "iha_yatis": client.get_yatis(),
                "zaman_farki": 0
            }
            locations.append(loc_info)
    return locations


class SunucuSaat(Resource):
    def get(self):
        now = datetime.datetime.now()
        response = {
            "saat" : now.hour,
            "dakika" : now.minute,
            "saniye" : now.second,
            "milisaniye" : now.microsecond
        }
        return response

class Telemetri(Resource):
    def post(self):
        #print(request.environ.get('REMOTE_PORT'))
        args = request.get_json()
        team_no = args["takim_numarasi"]

        if(is_client_active(team_no) is -1):
            return "Unauthorized access", 401

        client = get_active_client(team_no)
        if(client == None):
            return "Unauthorized access", 401
        client.update_telemetry_data(args)
        ##

        now = datetime.datetime.now()
        response = {
            "sistemSaati": {
                "saat": now.hour,
                "dakika": now.minute,
                "saniye": now.second,
                "milisaniye": now.microsecond
            },
            "konumBilgileri": get_location_infos()
        }
        return response

class Kilitlenme(Resource):
    def post(self):
        return "not implemented."

class Giris(Resource):
    def post(self):
        args = request.get_json()
        for user in users:
            if (user["kadi"] == args["kadi"]):
                team_no = user["takim_no"]
                if(is_client_active(team_no) is not -1):
                    return "Account already logged", 400

                client = Client(team_no)
                active_clients.append({team_no:client})
                return team_no, 200

        return "Login attempt was not successful", 400

class Cikis(Resource):
    def post(self):
        team_no = request.get_json()["team_no"]
        index = is_client_active(team_no)
        if(index is not -1):
            active_clients.pop(index)
            return "Successfully exited.", 200
        return "Unauthorized access", 401


api.add_resource(SunucuSaat, "/api/sunucusaati")
api.add_resource(Telemetri, "/api/telemetri_gonder")
api.add_resource(Kilitlenme, "/api/kilitlenme_bilgisi")
api.add_resource(Giris, "/api/giris")
api.add_resource(Cikis, "/api/cikis")

app.run(debug=False)
