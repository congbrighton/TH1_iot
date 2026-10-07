import json
from datetime import datetime
import paho.mqtt.client as mqtt

# Cấu hình MQTT Broker
BROKER = "test.mosquitto.org"
PORT = 1883

# Ký tự '+' đại diện cho bất kỳ cảm biến nào (sensor01, sensor02,...)
TOPIC_PATTERN = "iot/lab/+/data"


def on_connect(client, userdata, flags, reason_code, properties=None):
    """Callback xử lý khi kết nối tới MQTT Broker thành công hoặc thất bại"""
    if reason_code == 0:
        print(f"[OK] Da ket noi toi Broker: {BROKER}")
        client.subscribe(TOPIC_PATTERN)
        print(f"[OK] Dang giam sat tat ca thiet bi qua topic: {TOPIC_PATTERN}\n")
    else:
        print(f"[LOI] Ket noi thất bại, ma loi: {reason_code}")


def on_message(client, userdata, msg):
    """Callback xử lý khi nhận được dữ liệu từ cảm biến gửi về"""
    try:
        # Giải mã dữ liệu nhận được từ bytes -> string -> dict JSON
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        # Trích xuất dữ liệu cảm biến
        device_id = data.get("device_id", "Unknown")
        temperature = data.get("temperature", 0.0)
        humidity = data.get("humidity", 0.0)

        # Lấy thời gian nhận dữ liệu hiện tại
        receive_time = datetime.now().strftime("%H:%M:%S")

        # In thông tin giao diện giám sát
        print("=" * 40)
        print(f" Time        : {receive_time}")
        print(f" Topic       : {msg.topic}")
        print(f" Device ID   : {device_id}")
        print(f" Temperature : {temperature} °C")
        print(f" Humidity    : {humidity} %")

        # Kiểm tra điều kiện cảnh báo
        if temperature > 35.0:
            print(" [!] CANH BAO: Nhiet do cao (> 35°C)")
        if humidity < 40.0:
            print(" [!] CANH BAO: Do am thap (< 40%)")

        print("=" * 40 + "\n")

    except json.JSONDecodeError:
        print(f"[LOI] Dữ liệu từ topic {msg.topic} không đúng định dạng JSON!")
    except Exception as e:
        print(f"[LOI] Xảy ra lỗi khi xử lý dữ liệu: {e}")


def main():
    # Khởi tạo client hỗ trợ cả phiên bản paho-mqtt v1 và v2
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Monitor_Subscriber_Bai2")
    except AttributeError:
        client = mqtt.Client(client_id="Monitor_Subscriber_Bai2")

    client.on_connect = on_connect
    client.on_message = on_message

    print("Dang ket noi toi MQTT Broker...")
    try:
        client.connect(BROKER, PORT, keepalive=60)
        print("Nhan Ctrl+C de dung chuong trinh giam sat.\n")
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n[NGẮT] Ngung giam sat theo yeu cau nguoi dung.")
    except ConnectionRefusedError:
        print("[LOI] Khong the ket noi toi Broker (Connection Refused).")
    except Exception as e:
        print(f"[LOI] Lỗi kết nối: {e}")
    finally:
        client.disconnect()
        print("[OK] Da ngat ket noi an toan.")


if __name__ == "__main__":
    main()