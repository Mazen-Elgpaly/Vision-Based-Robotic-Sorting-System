import asyncio
import json
from aiohttp import web

# =======================
# Servo Struct
# =======================
class Servo:
    def __init__(self, name, reset=90, min_val=0, max_val=180):
        self.name = name
        self.current = reset
        self.target = reset
        self.min = min_val
        self.max = max_val
        self.reset = reset

servos = {
    "Base": Servo("Base"),
    "Shoulder": Servo("Shoulder"),
    "Elbow": Servo("Elbow"),
    "Gripper": Servo("Gripper"),
}

# =======================
# Timing
# =======================
STEP_DELAY = 0.02
STEP_SIZE = 1

clients = set()

# =======================
# Helpers
# =======================
def build_json():
    return json.dumps({name: s.current for name, s in servos.items()})

def reset_servos():
    print("=== RESET SERVOS ===")
    for s in servos.values():
        s.target = s.reset
        print(f"{s.name} -> Reset to {s.reset}")

def control_car(cmd):
    print(f"Car Command: {cmd}")

# =======================
# HTTP: serve index.html
# =======================
async def index(request):
    return web.FileResponse("./templates/index.html")

# =======================
# WebSocket Handler
# =======================
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print("Client connected")
    clients.add(ws)

    await ws.send_str(build_json())

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            message = msg.data
            print(f"\nReceived: {message}")

            # CAR
            if len(message) == 1:
                control_car(message)
                continue

            # RESET
            if message == "RESET":
                reset_servos()
                continue

            # GET ALL
            if message == "GET":
                await ws.send_str(build_json())
                continue

            # GET ONE
            if message.startswith("GET,"):
                name = message.split(",")[1]
                if name in servos:
                    await ws.send_str(f"{name}:{servos[name].current}")
                continue

            # SET SERVO
            if "," in message:
                name, value = message.split(",")
                if name in servos:
                    value = int(value)
                    s = servos[name]

                    new_target = max(s.min, min(s.max, value))

                    print(f"Servo Move -> {name}: {s.current} -> {new_target}")
                    s.target = new_target

    clients.remove(ws)
    print("Client disconnected")
    return ws

# =======================
# Servo Simulation Loop
# =======================
async def servo_loop():
    while True:
        for s in servos.values():
            if s.current < s.target:
                s.current += STEP_SIZE
            elif s.current > s.target:
                s.current -= STEP_SIZE

        await asyncio.sleep(STEP_DELAY)

# =======================
# Broadcast Loop
# =======================
async def broadcast_loop():
    while True:
        if clients:
            data = build_json()
            await asyncio.gather(*[ws.send_str(data) for ws in clients])
        await asyncio.sleep(0.3)

# =======================
# Main
# =======================
app = web.Application()
app.router.add_get("/", index)
app.router.add_get("/ws", websocket_handler)

app.router.add_static("/templates/", path="./templates", name="templates")

loop = asyncio.get_event_loop()
loop.create_task(servo_loop())
loop.create_task(broadcast_loop())

web.run_app(app, host="0.0.0.0", port=80)