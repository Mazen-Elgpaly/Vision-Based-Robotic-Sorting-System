import websocket
import time

ws = websocket.WebSocket()
ws.connect("ws://127.0.0.1:5000/RobotArmInput")

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

# تسجيل
ws.send("Record,1")
time.sleep(2)

ws.send("Base,150")
time.sleep(1)

ws.send("Record,0")

# تشغيل
ws.send("Play,1")