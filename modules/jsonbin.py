import requests
from time import localtime

minutes = localtime().tm_min

BIN_IDS = ["67aa72d0e41b4d34e488e836", "67aa7636ad19ca34f8fea68e"]
API_URLS = [f"https://api.jsonbin.io/v3/b/{bin_id}" for bin_id in BIN_IDS]

HEADERS = {
    "Content-Type": "application/json",
}

def set_ip(ip):
    data = {"server_ip": ip}
    
    for url in API_URLS:

        try:
            response = requests.put(url, json=data, headers=HEADERS)

            if response.status_code == 200:
                return 1
            else:
                print("[ ! ] Erro ao atualizar IP:", response.text)

        except Exception as e:
            print(f"Erro ao atualizar IP: {e}")
    return 0

def get_ip():
    for url in API_URLS:

        try:
            response = requests.get(url + "/latest").json()
            print(response)
            ip = response["record"]["server_ip"]
            dt = abs(int(response["metadata"]["createdAt"][14:16]) - minutes)
            
            print(dt)
            if 10 > dt > 50:
                print(f"Endereço desatualizado: {ip}")
                continue

            return ip

        except Exception as e:
            print(f"Erro ao obter endereço ip: {e}")

    return input("Digite o ip manualmente: ")