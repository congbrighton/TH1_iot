import json
import paho.mqtt.client as mqtt

# Cấu hình MQTT Broker
BROKER = "broker.hivemq.com"
PORT = 1883

# Danh sách các thiết bị thông minh cần mô phỏng
DEVICES = ["light01", "fan01", "pump01"]

# Lưu trữ trạng thái hiện tại của các thiết bị
device_status = {
    "light01": "OFF",
    "fan01": "OFF",
    "pump01": "OFF"
}


def publish_status(client, device_id):
    """Hàm đóng gói JSON và gửi trạng thái hiện tại kèm retain=True"""
    payload_dict = {
        "device_id": device_id,
        "status": device_status[device_id]
    }
    payload_json = json.dumps(payload_dict)
    status_topic = f"iot/lab/{device_id}/status"

    # retain=True giúp lưu trạng thái mới nhất trên Broker
    client.publish(status_topic, payload_json, retain=True)
    print(f" -> [Đã gửi trạng thái] Topic: {status_topic} | Payload: {payload_json}")


def on_connect(client, userdata, flags, rc, properties=None):
    """Callback xử lý khi kết nối thành công tới Broker"""
    if rc == 0:
        print("==================================================")
        print("      HỆ THỐNG THIẾT BỊ THÔNG MINH ĐÃ KHỞI ĐỘNG  ")
        print("==================================================")
        print(f"[OK] Đã kết nối tới Broker '{BROKER}'")

        # Đăng ký nhận lệnh của tất cả thiết bị qua Wildcard '+'
        cmd_topic = "iot/lab/+/cmd"
        client.subscribe(cmd_topic)
        print(f"[OK] Đang lắng nghe lệnh điều khiển tại topic: {cmd_topic}\n")

        print("Gửi trạng thái ban đầu của các thiết bị:")
        for dev_id in DEVICES:
            publish_status(client, dev_id)
        print("-" * 50 + "\n")
    else:
        print(f"[LOI] Kết nối thất bại với mã lỗi: {rc}")


def on_message(client, userdata, msg):
    """Callback xử lý khi nhận lệnh từ ứng dụng điều khiển"""
    global device_status

    try:
        # Lấy device_id từ Topic (Cấu trúc topic: iot/lab/<device_id>/cmd)
        parts = msg.topic.split("/")
        if len(parts) < 4:
            return
        device_id = parts[2]

        # Đọc và chuẩn hóa lệnh nhận được
        command = msg.payload.decode("utf-8").strip().upper()

        print(f"[LỆNH MỚI] Topic: {msg.topic}")
        print(f" -> Device  : {device_id}")
        print(f" -> Command : {command}")

        # Kiểm tra thiết bị có thuộc hệ thống quản lý hay không
        if device_id not in DEVICES:
            print(f" [!] Bỏ qua: Thiết bị '{device_id}' không tồn tại trong hệ thống!\n")
            return

        # Cập nhật trạng thái nếu lệnh hợp lệ
        if command in ["ON", "OFF"]:
            device_status[device_id] = command
            print(f" [OK] Đã thực thi lệnh thành công cho {device_id} -> {command}")
            # Gửi phản hồi trạng thái mới sau khi chuyển mạch
            publish_status(client, device_id)
            print()
        else:
            print(f" [!] Bỏ qua lệnh không hợp lệ: '{command}' (Chỉ chấp nhận ON hoặc OFF)\n")

    except Exception as e:
        print(f"[LOI] Xử lý lệnh thất bại: {e}\n")


def main():
    # Khởi tạo client hỗ trợ cả phiên bản paho-mqtt v1 và v2
    try:
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id="Smart_Device_System_Bai3"
        )
    except AttributeError:
        client = mqtt.Client(client_id="Smart_Device_System_Bai3")

    client.on_connect = on_connect
    client.on_message = on_message

    print("Đang kết nối tới MQTT Broker...")
    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n[NGẮT] Đã tắt hệ thống thiết bị thông minh.")
    except ConnectionRefusedError:
        print("[LOI] Không thể kết nối tới MQTT Broker (Connection Refused).")
    except Exception as e:
        print(f"[LOI] Lỗi kết nối: {e}")
    finally:
        client.disconnect()
        print("[OK] Đã ngắt kết nối an toàn.")


if __name__ == "__main__":
    main()