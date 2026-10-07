import json
import sys
import time
import paho.mqtt.client as mqtt

# Cấu hình MQTT Broker (Đồng bộ với device_bai3.py)
BROKER = "broker.hivemq.com"
PORT = 1883

# Danh sách thiết bị hỗ trợ điều khiển
DEVICES = ["light01", "fan01", "pump01"]


def on_connect(client, userdata, flags, rc, properties=None):
    """Callback xử lý khi kết nối thành công tới MQTT Broker"""
    if rc == 0:
        # Lắng nghe trạng thái của tất cả thiết bị qua Wildcard '+'
        status_topic = "iot/lab/+/status"
        client.subscribe(status_topic)
    else:
        print(f"[LOI] Kết nối tới Broker thất bại với mã: {rc}")


def on_message(client, userdata, msg):
    """Callback xử lý khi nhận được phản hồi trạng thái từ thiết bị"""
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        device_id = data.get("device_id", "Unknown")
        status = data.get("status", "Unknown")

        print("\n\n----------------------------------------")
        print(" [PHẢN HỒI TỪ THIẾT BỊ]")
        print(f" -> Topic    : {msg.topic}")
        print(f" -> Device   : {device_id}")
        print(f" -> Status   : {status}")
        print(f" -> Payload  : {payload}")
        print("----------------------------------------")
        print("\nChọn thiết bị (1-4) hoặc gõ lệnh trực tiếp: ", end="", flush=True)

    except json.JSONDecodeError:
        print(f"\n[LOI] Payload từ '{msg.topic}' không phải JSON hợp lệ.")
    except Exception as e:
        print(f"\n[LOI] Xảy ra lỗi khi đọc phản hồi: {e}")


def send_command(client, device_id, command):
    """Hàm phụ trợ đóng gói và publish lệnh điều khiển"""
    if not client.is_connected():
        print(" [!] Đã mất kết nối. Đang kết nối lại...")
        client.reconnect()
        time.sleep(1)

    cmd_topic = f"iot/lab/{device_id}/cmd"
    result = client.publish(cmd_topic, command)

    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"\n [->] Đã gửi lệnh '{command}' tới [{device_id}]")
        print(f" -> Topic: {cmd_topic}")
    else:
        print(f" [!] Gửi lệnh thất bại với mã: {result.rc}")

    time.sleep(0.5)


def main():
    # Khởi tạo client hỗ trợ cả phiên bản paho-mqtt v1 và v2
    try:
        client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2, client_id="Controller_App_Complete"
        )
    except AttributeError:
        client = mqtt.Client(client_id="Controller_App_Complete")

    client.on_connect = on_connect
    client.on_message = on_message

    print("==========================================")
    print("      ỨNG DỤNG ĐIỀU KHIỂN CONTROLLER APP  ")
    print("==========================================")
    print("Đang kết nối tới MQTT Broker...")

    try:
        client.connect(BROKER, PORT, keepalive=60)
    except Exception as e:
        print(f"[LOI] Không thể kết nối tới Broker: {e}")
        sys.exit(1)

    # Khởi chạy luồng mạng chạy ngầm
    client.loop_start()
    time.sleep(1)

    try:
        while True:
            print("\nDANH SÁCH THIẾT BỊ:")
            print("1. light01")
            print("2. fan01")
            print("3. pump01")
            print("4. EXIT (Thoát)")

            user_input = input("Chọn thiết bị (1-4) hoặc nhập trực tiếp (VD: light01 ON): ").strip()

            if not user_input:
                continue

            cmd_upper = user_input.upper()

            # 1. Trường hợp thoát
            if cmd_upper in ["4", "EXIT"]:
                print("\nĐang ngắt kết nối và thoát Controller App...")
                break

            # 2. Trường hợp gõ lệnh nhanh 2 từ (VD: light01 ON hoặc fan01 OFF)
            parts = user_input.split()
            if len(parts) == 2:
                dev_id, cmd = parts[0].lower(), parts[1].upper()
                if dev_id in DEVICES and cmd in ["ON", "OFF"]:
                    send_command(client, dev_id, cmd)
                    continue
                else:
                    print(" [!] Lỗi: Tên thiết bị hoặc lệnh không hợp lệ!")
                    continue

            # 3. Trường hợp chọn theo Menu chọn từng bước
            selected_device = None
            if cmd_upper in ["1", "LIGHT01"]:
                selected_device = "light01"
            elif cmd_upper in ["2", "FAN01"]:
                selected_device = "fan01"
            elif cmd_upper in ["3", "PUMP01"]:
                selected_device = "pump01"

            if selected_device:
                print(f"\nThiết bị đã chọn: [{selected_device}]")
                print("1. ON  (Bật)")
                print("2. OFF (Tắt)")
                print("3. HUY (Quay lại)")

                sub_choice = input("Chọn lệnh (1-3 hoặc ON/OFF): ").strip().upper()

                if sub_choice in ["3", "HUY"]:
                    continue
                elif sub_choice in ["1", "ON"]:
                    send_command(client, selected_device, "ON")
                elif sub_choice in ["2", "OFF"]:
                    send_command(client, selected_device, "OFF")
                else:
                    print(" [!] Lỗi: Lệnh không hợp lệ!")
            else:
                print(" [!] Lỗi: Vui lòng chọn số từ 1-4 hoặc nhập cú pháp '<device> <ON/OFF>'")

    except KeyboardInterrupt:
        print("\n[NGẮT] Đã ép buộc dừng chương trình Controller.")
    finally:
        client.loop_stop()
        client.disconnect()
        print("[OK] Đã ngắt kết nối an toàn.")
        sys.exit(0)


if __name__ == "__main__":
    main()