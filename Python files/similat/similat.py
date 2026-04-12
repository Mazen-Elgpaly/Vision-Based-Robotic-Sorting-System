from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import time

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# ======================
# Servo Simulation
# ======================

class Servo:
    def __init__(self, name, initial=90):
        self.name = name
        self.position = initial

    def write(self, value):
        self.position = value

    def read(self):
        return self.position


servos = [
    Servo("Base"),
    Servo("Shoulder"),
    Servo("Elbow"),
    Servo("Gripper")
]

# ======================
# Recording System
# ======================

recorded_steps = []
record_steps = False
play_steps = False
previous_time = time.time()

# ======================
# HTML (نفس فكرتك)
# ======================

HTML = """
<!DOCTYPE html>
<html>
<body style="text-align:center">

<h2>Robot Arm Simulation</h2>

{% for servo in servos %}
<p>{{servo.name}}</p>
<input type="range" min="0" max="180" value="90"
oninput="send('{{servo.name}}', this.value)">
{% endfor %}

<br><br>
<button onclick="toggle('Record')">Record</button>
<button onclick="toggle('Play')">Play</button>

<script src="https://cdn.socket.io/4.0.1/socket.io.min.js"></script>
<script>
var socket = io();

function send(key, value){
    socket.emit("data", key + "," + value);
}

function toggle(key){
    socket.emit("data", key + ",1");
}

socket.on("update", function(msg){
    console.log(msg);
});
</script>

</body>
</html>
"""

# ======================
# Routes
# ======================

@app.route("/")
def home():
    return render_template_string(HTML, servos=servos)

# ======================
# WebSocket Logic
# ======================

@socketio.on("data")
def handle_data(msg):
    global record_steps, play_steps, previous_time

    key, value = msg.split(",")
    value = int(value)

    print("Received:", key, value)

    if key == "Record":
        record_steps = not record_steps
        if record_steps:
            recorded_steps.clear()
            previous_time = time.time()

    elif key == "Play":
        play_steps = not play_steps
        if play_steps:
            socketio.start_background_task(play_sequence)

    else:
        index = ["Base","Shoulder","Elbow","Gripper"].index(key)
        write_servo(index, value)

# ======================
# Core Logic
# ======================

def write_servo(index, value):
    global previous_time

    if record_steps:
        if len(recorded_steps) == 0:
            # initial state
            for i, s in enumerate(servos):
                recorded_steps.append((i, s.read(), 0))

        current_time = time.time()
        delay = current_time - previous_time
        recorded_steps.append((index, value, delay))
        previous_time = current_time

    servos[index].write(value)
    socketio.emit("update", f"{servos[index].name},{value}")

# ======================
# Play Logic
# ======================

def play_sequence():
    global play_steps

    if not recorded_steps:
        return

    # move to initial slowly
    for i in range(4):
        idx, target, _ = recorded_steps[i]
        while servos[idx].read() != target and play_steps:
            cur = servos[idx].read()
            cur += -1 if cur > target else 1
            servos[idx].write(cur)
            socketio.emit("update", f"{servos[idx].name},{cur}")
            time.sleep(0.05)

    time.sleep(2)

    # play rest
    for step in recorded_steps[4:]:
        if not play_steps:
            break
        idx, val, delay = step
        time.sleep(delay)
        servos[idx].write(val)
        socketio.emit("update", f"{servos[idx].name},{val}")

    play_steps = False

# ======================
# Run
# ======================

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)