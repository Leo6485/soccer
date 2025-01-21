from threading import Thread
import jsonbin
import os
from time import sleep

i_set = 0
i_get = 0
ok = 1
def set():
    global i_set, ok
    ok = jsonbin.set_ip(str(i_set))
    print(f"Set: {i_set}")
    i_set += 1

def get():
    global i_get
    print(f"Get: {jsonbin.get_ip()}")
    i_get += 1

for i in range(100):
    Thread(target=set).start()
    Thread(target=get).start()
    
    if not ok:
        os._exit(0)
    
    sleep(1)