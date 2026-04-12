import socketio
import time

sio = socketio.Client()

@sio.event
def connect():
    print("Connected ✅")

@sio.on("update")
def on_update(data):
    print("Update:", data)

sio.connect("http://127.0.0.1:5000")

# تحريك السيرفو
sio.emit("data", "Base,120")
time.sleep(1)

sio.emit("data", "Elbow,60")
time.sleep(1)

# تسجيل
sio.emit("data", "Record,1")
time.sleep(2)

sio.emit("data", "Base,150")
time.sleep(1)

sio.emit("data", "Record,0")

# تشغيل
sio.emit("data", "Play,1")