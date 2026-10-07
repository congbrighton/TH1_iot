import json
import random
import time
import paho.mqtt.client as mqtt

# Cấu hình MQTT Broker
BROKER = "broker.hivemq.com"
PORT = 1883

# Danh sách các thiết bị cảm biến cần mô phỏng
DEVICES = ["sensor01", "sensor02"]


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[OK] Ket noi toi Broker '{BROKER}' thanh cong!")
    else:
        print(f"[LOI] Ket noi that bai voi ma loi: {rc}")


def main():
    # Xử lý tương thích cho cả paho-mqtt v1 và v2
    try:
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id="MultiSensorPublisher"
        )
    except AttributeError:
        client = mqtt.Client(client_id="MultiSensorPublisher")

    client.on_connect = on_connect

    print("Dang ket noi toi MQTT Broker...")
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_start()

    try:
        print("Bat dau gui du lieu cam bien dinh ky 3s (Nhan Ctrl+C de dung)...\n")
        while True:
            # Tự động gửi dữ liệu cho tất cả sensor trong danh sách ở mỗi chu kỳ
            for dev_id in DEVICES:
                topic = f"iot/lab/{dev_id}/data"
                temperature = round(random.uniform(20.0, 42.0), 1)
                humidity = round(random.uniform(30.0, 85.0), 1)

                payload = {
                    "device_id": dev_id,
                    "temperature": temperature,
                    "humidity": humidity,
                }
                payload_json = json.dumps(payload)

                # Tự động kết nối lại nếu bị ngắt mạng
                if not client.is_connected():
                    print("[!] Mat ket noi Broker. Dang ket noi lai...")
                    client.reconnect()

                result = client.publish(topic, payload_json)

                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"-> Da gui toi [{topic}]: {payload_json}")
                else:
                    print(f"[LOI] Gui du lieu that bai cho {dev_id}: {result.rc}")

            print("-" * 55)
            # Nghỉ 3 giây trước chu kỳ gửi tiếp theo
            time.sleep(3)

    except KeyboardInterrupt:
        print("\n[NGẮT] Dung Multi Sensor Publisher.")
    except Exception as e:
        print(f"\n[LOI] Co loi xay ra: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[OK] Da ngat ket noi an toan.")


if __name__ == "__main__":
    main()