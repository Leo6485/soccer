import socket
from threading import Thread
import pickle

class Server:
    def __init__(self, ip=None, port=5454):
        print("\033c", end="\r")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = self.get_ip() if not ip else ip
        self.port = port
        self.server.bind((self.ip, port))
        self.routes = {}
        print(f"[ * ] Vinculado como: {self.ip}:{self.port}")

    def parse(self, data):
        data = pickle.loads(data)
        route = data.get("type", None).upper()
        show = ["CONNECT", "ID", "SETSCREEN"]
        if route in show:
            print(f"\033[1;34mDados recebidos: \033[1;32m{data}\n\033[1;34mRota: \033[1;32m{route}\033[0m")

        return data, route

    def listen(self):
        try:
            data, addr = self.server.recvfrom(2048)
            def go_route(data, addr):
                data, route = self.parse(data)

                response = self.routes.get(route, print)(data["data"], addr)

                if response:
                    self.server.sendto(pickle.dumps(response), addr)

            Thread(target=go_route, args=(data, addr)).start()
        except KeyboardInterrupt:
            self.stop()
        except socket.timeout:
            pass
        except Exception as e:
            print(e)

    def route(self, key):
        key = key.upper()
        def wrap0(f):
            self.routes[key] = f
            return None
        return wrap0

    def send(self, data, addr):
        Thread(target=self.server.sendto, args = (pickle.dumps(data), addr)).start()

    def run(self, wait=True):
        self.running = True
        self.server.settimeout(0.1)
        self.threads = {}
        print("[ * ] Aguardando conexões")
        if not wait:
            self.threads["_run"] = Thread(target=self._run)
            self.threads["_run"].start()
        else:
            self._run()

    def _run(self):
        try:
            while self.running:
                self.listen()
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(e)
        finally:
            self.server.close()

    def stop(self):
        print("[ * ] Parando o serviço")
        self.running = False
        for thread in self.threads.values():
            thread.join()
        self.server.close()
        print("[ * ] Serviço parado")

    @staticmethod
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception as e:
            print(f"[ ! ] Erro ao obter o IP: {e}")
            ip = None
        finally:
            s.close()
        return ip

class Client(Server):
    def __init__(self, server_ip="127.0.0.1", port=5454):
        print("\033c", end="\r")
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.settimeout(0.5)
        self.server_ip = server_ip
        self.ip = self.get_ip()
        self.port = port
        self.routes = {}
        print(f"[ * ] Vinculado como: {self.ip}:{self.port}")
        print(f"Conectado com: {self.server_ip}")

    def send(self, data):
        self.server.sendto(pickle.dumps(data), (self.server_ip, self.port))