import websocket
import time

ws = websocket.WebSocket()
ws.connect("ws://127.0.0.1:80/ws")

print("Connected ✅")

# استقبال (اختياري)
def receive():
    try:
        while True:
            print("Update:", ws.recv())
    except:
        pass

# تحريك السيرفو
ws.send("Base,120")
time.sleep(1)

ws.send("Elbow,60")
time.sleep(1)

ws.send("Base,150")
time.sleep(1)