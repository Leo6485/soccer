import requests

BIN_ID = "676154dead19ca34f8dc8c9e"
API_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

def set_ip(ip):
    headers = {
        "Content-Type": "application/json",
    }
    data = {"server_ip": ip}

    response = requests.put(API_URL, json=data, headers=headers)
    if response.status_code != 200:
        print("[ ! ] Erro ao atualizar IP:", response.text)
        return 0
    
    return 1

def get_ip():
    response = requests.get(API_URL + "/latest").json()
    return response["record"]["server_ip"] or "Erro"