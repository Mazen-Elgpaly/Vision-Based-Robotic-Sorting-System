from flask import Flask, render_template
from flask_sock import Sock
import time

app = Flask(__name__)
sock = Sock(app)

# ======================
# Servo Simulation
# ======================
class Servo:
    def __init__(self, name):
        self.name = name
        self.position = 90

    def write(self, value):
        self.position = value
        print(f"{self.name} -> {self.position}")

    def read(self):
        return self.position


servoPins = [
    Servo("Base"),
    Servo("Shoulder"),
    Servo("Elbow"),
    Servo("Gripper")
]

recordedSteps = []
recordSteps = False
playRecordedSteps = False
previousTime = time.time()

clients = []  # كل الـ clients المتصلة


# ======================
# Routes
# ======================
@app.route("/")
def index():
    return render_template("index.html")


# ======================
# WebSocket (نفس ESP)
# ======================
@sock.route('/RobotArmInput')
def robot_arm(ws):
    global recordSteps, playRecordedSteps, previousTime

    clients.append(ws)
    print("Client connected")

    # send initial state
    sendCurrentState(ws)

    while True:
        data = ws.receive()
        if data is None:
            break

        key, value = data.split(",")
        value = int(value)

        print(f"{key} -> {value}")

        if key == "Record":
            recordSteps = bool(value)
            if recordSteps:
                recordedSteps.clear()
                previousTime = time.time()

            broadcast(f"Record,{ 'ON' if recordSteps else 'OFF' }")

        elif key == "Play":
            playRecordedSteps = bool(value)
            broadcast(f"Play,{ 'ON' if playRecordedSteps else 'OFF' }")

            if playRecordedSteps:
                playRecordedRobotArmSteps()

        elif key in ["Base", "Shoulder", "Elbow", "Gripper"]:
            index = ["Base", "Shoulder", "Elbow", "Gripper"].index(key)
            writeServoValues(index, value)


# ======================
# Core Logic
# ======================
def broadcast(msg):
    for c in clients:
        try:
            c.send(msg)
        except:
            pass


def sendCurrentState(ws):
    for s in servoPins:
        ws.send(f"{s.name},{s.read()}")

    ws.send(f"Record,{ 'ON' if recordSteps else 'OFF' }")
    ws.send(f"Play,{ 'ON' if playRecordedSteps else 'OFF' }")


def writeServoValues(index, value):
    global previousTime

    if recordSteps:
        if len(recordedSteps) == 0:
            for i, s in enumerate(servoPins):
                recordedSteps.append((i, s.read(), 0))

        currentTime = time.time()

        recordedSteps.append((
            index,
            value,
            currentTime - previousTime
        ))

        previousTime = currentTime

    servoPins[index].write(value)
    broadcast(f"{servoPins[index].name},{value}")


def playRecordedRobotArmSteps():
    global playRecordedSteps

    if not recordedSteps:
        return

    print("▶ Playing...")

    # initial
    for i in range(4):
        idx, val, _ = recordedSteps[i]
        servo = servoPins[idx]

        current = servo.read()
        while current != val and playRecordedSteps:
            current += -1 if current > val else 1
            servo.write(current)
            broadcast(f"{servo.name},{current}")
            time.sleep(0.05)

    time.sleep(2)

    # rest
    for idx, val, delay in recordedSteps[4:]:
        if not playRecordedSteps:
            break

        time.sleep(delay)
        servoPins[idx].write(val)
        broadcast(f"{servoPins[idx].name},{val}")

    playRecordedSteps = False
    broadcast("Play,OFF")

    print("✔ Done")


# ======================
# Run
# ======================
if __name__ == "__main__":
    app.run(debug=True)