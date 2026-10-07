# BÁO CÁO THỰC HÀNH: LẬP TRÌNH PYTHON VỚI GIAO THỨC MQTT

Tài liệu hướng dẫn cài đặt, cấu hình và báo cáo kết quả thực hành lập trình MQTT qua Python cho 3 bài toán: Giao tiếp MQTT cơ bản, Giám sát cảm biến nhiệt độ/độ ẩm và Hệ thống điều khiển thiết bị IoT hai chiều.

---

## 1. YÊU CẦU MÔI TRƯỜNG & THƯ VIỆN

- **Ngôn ngữ**: Python 3.x
- **Thư viện phụ thuộc**: `paho-mqtt` (Hỗ trợ tương thích cả phiên bản `v1.x` và `v2.x`)
- **Cài đặt thư viện**:
  ```bash
  pip install paho-mqtt
  BÀI 1 - GIAO TIẾP MQTT CƠ BẢN
1. MQTT Broker sử dụng
Broker: broker.hivemq.com

Port: 1883

Protocol: MQTT

Topic sử dụng: iot/lab/message

2. Các file chương trình
publisher_bai1.py: Kết nối tới Broker, gửi dữ liệu chuỗi (Họ tên, MSV, lời chào) định kỳ mỗi 5 giây, xử lý ngắt bằng Ctrl+C.

subscriber_bai1.py: Lắng nghe liên tục trên topic, giải mã và hiển thị Topic, Payload cùng thời gian nhận dạng HH:MM:SS.

3. Cách chạy chương trình
Bước 1: Mở Terminal 1 chạy Subscriber trước:

Bash
python subscriber_bai1.py
Bước 2: Mở Terminal 2 chạy Publisher:

Bash
python publisher_bai1.py
4. Kết quả đạt được
Khởi tạo client tự động nhận diện và tương thích với cả paho-mqtt v1 và v2 (CallbackAPIVersion.VERSION2).

Publisher gửi thông điệp chu kỳ 5 giây, không làm quá tải băng thông Broker.

Subscriber nhận và hiển thị đầy đủ thông tin:

Topic: iot/lab/message

Payload: Xin chao tu client Python MQTT - B23DCCN102 - Nguyen Duc Cong

Time: Timestamp thời điểm nhận.

Dừng chương trình an toàn bằng Ctrl+C mà không bị gián đoạn hay để lại luồng chạy ngầm.

BÀI 2 - MÔ PHỎNG CẢM BIẾN NHIỆT ĐỘ VÀ ĐỘ ẨM BẰNG MQTT
1. MQTT Broker sử dụng
Broker: broker.hivemq.com

Port: 1883

Protocol: MQTT

Cấu trúc Topic: iot/lab/+/data (Dùng Wildcard + để nhận mọi cảm biến sensor01, sensor02,...)

2. Các file chương trình
sensor_publisher_bai2.py: Mô phỏng gửi dữ liệu cho nhiều cảm biến (sensor01, sensor02), tự sinh ngẫu nhiên nhiệt độ (20-42°C) và độ ẩm (30-85%), gửi JSON định kỳ mỗi 3 giây.

monitor_subscriber_bai2.py: Đăng ký lắng nghe wildcard topic, giải mã JSON, in bảng khung chi tiết và đưa ra cảnh báo tức thì khi vượt ngưỡng.

3. Cách chạy chương trình
Bước 1: Mở Terminal 1 chạy chương trình giám sát:

Bash
python monitor_subscriber_bai2.py
Bước 2: Mở Terminal 2 chạy mô phỏng cảm biến:

Bash
python sensor_publisher_bai2.py
4. Định dạng dữ liệu (Payload JSON)
JSON
{
  "device_id": "sensor01",
  "temperature": 36.5,
  "humidity": 38.2
}
5. Kết quả đạt được
Tự động kiểm tra và khôi phục kết nối (client.reconnect()) nếu mất mạng.

Xử lý ngoại lệ an toàn: json.JSONDecodeError phòng dữ liệu rác trên Broker công cộng.

Đưa ra cảnh báo chính xác theo điều kiện đề bài:

Nhiệt độ > 35.0°C: In [!] CANH BAO: Nhiet do cao

Độ ẩm < 40.0%: In [!] CANH BAO: Do am thap

Nhận diện linh hoạt dữ liệu từ nhiều cảm biến cùng lúc qua Wildcard topic.

BÀI 3 - ĐIỀU KHIỂN THIẾT BỊ IOT HAI CHIỀU BẰNG MQTT
1. MQTT Broker sử dụng
Broker: broker.hivemq.com

Port: 1883

Protocol: MQTT

Cấu trúc Topic:

Topic nhận lệnh: iot/lab/<device_id>/cmd (Lắng nghe tập trung qua iot/lab/+/cmd)

Topic phản hồi trạng thái: iot/lab/<device_id>/status (Lắng nghe tập trung qua iot/lab/+/status)

2. Các file chương trình
device_bai3.py: Mô phỏng quản lý tập trung danh sách nhiều thiết bị (light01, fan01, pump01). Nhận lệnh ON/OFF, cập nhật từ điển trạng thái device_status và phản hồi trạng thái kèm cờ retain=True.

controller_bai3.py: Ứng dụng điều khiển đa năng. Cho phép chọn thiết bị qua Menu phân cấp (1-4) hoặc gõ nhanh lệnh 2 từ (light01 ON), chạy luồng lắng nghe ngầm (loop_start()) để nhận phản hồi mà không làm đè dòng nhắc lệnh.

3. Cách chạy chương trình
Bước 1: Mở Terminal 1 chạy chương trình quản lý thiết bị:

Bash
python device_bai3.py
Bước 2: Mở Terminal 2 chạy ứng dụng điều khiển:

Bash
python controller_bai3.py
4. Luồng giao tiếp hai chiều
Controller gửi lệnh tới Topic: iot/lab/light01/cmd với Payload: ON

Device nhận lệnh, cập nhật trạng thái light01 -> ON, gửi phản hồi tới Topic: iot/lab/light01/status với Payload:

JSON
{
  "device_id": "light01",
  "status": "ON"
}
Cờ retain=True đảm bảo Controller ngay khi vừa bật lên đã nhận ngay trạng thái mới nhất từ Broker.

5. Kết quả đạt được
Hỗ trợ giao tiếp 2 chiều hoàn chỉnh giữa Controller và Device.

Xử lý mở rộng điều khiển đa thiết bị (light01, fan01, pump01).

Bắt lỗi nhập sai cú pháp, bỏ qua lệnh không hợp lệ.

Hỗ trợ lựa chọn EXIT hoặc Ctrl+C để ngắt kết nối an toàn.
