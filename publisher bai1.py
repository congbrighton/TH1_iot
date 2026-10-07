import time
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "iot/lab/message"
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Ket noi thanh cong toi MQTT Broker!")
    else:
        print(f"Ket noi that bai, ma loi: {rc}")
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
except AttributeError:
    client = mqtt.Client()

client.on_connect = on_connect
client.connect(BROKER, PORT, 60)
client.loop_start()

# Thông tin sinh viên
hoten = "Nguyen Duc Cong"
masv = "B23DCCN102"
loichao = "Xin chao tu client Python MQTT"

try:
    print(f"Bắt đầu gửi thông điệp lên topic '{TOPIC}' (Nhấn Ctrl+C để dừng)...\n")
    while True:
        payload = f"{loichao} - {masv} - {hoten}"
        print(f"Dang gui: {payload}")
        client.publish(TOPIC, payload)


        time.sleep(2)

except KeyboardInterrupt:
    print("\n[NGẮT] Ket thuc chuong trinh Publisher.")
    client.loop_stop()
    client.disconnect()