import paho.mqtt.client as mqtt
from datetime import datetime

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "iot/lab/message"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Ket noi thanh cong! Dang lang nghe topic: {TOPIC}")
        client.subscribe(TOPIC)
    else:
        print(f"Ket noi that bai voi ma loi {rc}")

def on_message(client, userdata, msg):
    now = datetime.now().strftime("%H:%M:%S")
    print("\nNhan duoc message:")
    print(f"Topic: {msg.topic}")
    print(f"Payload: {msg.payload.decode('utf-8')}")
    print(f"Time: {now}")
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
except AttributeError:
    client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)

try:
    print("Nhan Ctrl+C de thoat...")
    client.loop_forever()
except KeyboardInterrupt:
    print("\n[NGẮT] Ket thuc chuong trinh Subscriber")
    client.disconnect()