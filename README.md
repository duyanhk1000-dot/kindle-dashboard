# 📱 Kindle Touch 4th Gen (D01200) Smart Dashboard v2.0

Hệ thống **E-ink Smart Dashboard** tự động dành riêng cho máy đọc sách **Kindle Touch 4th Generation (Model D01200)** với màn hình dọc **600x800**, hiển thị 16 cấp độ thang xám (16 Grayscale).

> [!NOTE]
> Dự án được xây dựng và tối ưu hóa với mô hình **Gemini-2.5-Flash Engine** kết hợp hệ thống cào dữ liệu tài chính đa nguồn **Multi-Provider MarketCrawler** (`vnstock`, KBSV, TCBS, CafeF, Cophieu68, giavang.org).

---

## 📸 GIAO DIỆN & TÍNH NĂNG NỔI BẬT

### 1. 🖼️ Nửa Trên: Khung Ảnh Phong Cảnh Hàng Ngày (Y: 8 -> 305)
- Tự động quét và chọn ảnh từ thư mục ảnh cá nhân `photos/` hoặc tải ảnh ngẫu nhiên từ Unsplash / Picsum.
- Tự động chuyển đổi sang ảnh 8-bit Grayscale, nâng độ tương phản và tăng độ sắc nét tối ưu cho màn E-ink.
- **Thanh Header trên cùng**: Hiển thị tên cá nhân hóa `KIỀU DUY ANH - KINDLE DASHBOARD` và Thứ, Ngày Dương lịch + Ngày Âm lịch (`ÂL: 11/7`).

### 2. 📈 Cột Trái Nửa Dưới (X: 18 -> 305):
- **THỊ TRƯỜNG (Multi-Provider MarketCrawler)**:
  - **Vàng SJC**: Cào dữ liệu trực tiếp từ `https://giavang.org/` (`144.60 - 147.60 tr (+0.50%)`).
  - **VN-Index**: Chỉ số đóng cửa chính xác `1,768.12 (+39.04 (+2.26%))`.
  - **Cổ phiếu theo dõi**: Cập nhật giá 3 mã cổ phiếu `HPG` (`21.70`), `NVL` (`13.35`), `SSI` (`20.75`).
- **CHỮ HÁN HÔM NAY (Chiết tự & Bộ thủ)**:
  - Ô vuông chữ Hán to sắc nét **`62x62px`** (`48pt`).
  - Pinyin & Hán-Việt (`dé - ĐỨC`).
  - **Cột Bộ thủ**: Mỗi bộ 1 dòng kèm chữ Hán và nghĩa tiếng Việt trong ngoặc đơn (Ví dụ: `• Bộ Xích 彳 (bước đi ngắn)`, `• Bộ Tâm 心 (trái tim)`).
  - **Chiết tự etymology**: Giải nghĩa câu chuyện chiết tự dễ nhớ.
  - **Ví dụ mẫu**: Hiển thị đầy đủ chữ Hán ghép từ (Ví dụ: `Đạo đức (道德), Phẩm đức (品德)`).
- **THỜI TIẾT 3 NGÀY**:
  - Dự báo thời tiết Hà Nội từ Open-Meteo API (Hôm nay, Ngày mai, Ngày kia).
  - Biểu tượng Monochrome đơn giản (`[NẮNG]`, `[MÂY]`, `[MƯA]`).
  - Thêm thông tin **Chất lượng không khí AQI**, **Cảm giác như (°C)** và **Độ ẩm (%)**.

### 3. 📅 Cột Phải Nửa Dưới (X: 318 -> 585):
- **LỊCH THÁNG**: Lưới lịch tháng đầy đủ (T2 - CN).
  - **Khoanh tròn đóng khung đậm** ngày hiện tại.
  - Nổi bật màu nền các ngày **Mùng 1** và **Rằm (15)** Âm lịch.
- **LỊCH NGHỈ LỄ & LÀM BÙ**: Danh sách ngày lễ Quốc Khánh, nghỉ bù, rằm tháng 7 xếp theo thứ tự thời gian.

---

## 📁 CẤU TRÚC THƯ MỤC DỰ ÁN

```
d:\code-cho-kindle\dashboard\
├── render_dashboard.py      # Core script render ảnh dashboard.png (PIL/Pillow)
├── vnstock_crawler.py       # Multi-Provider MarketCrawler (vnstock, giavang.org, TCBS, CafeF, Cophieu68)
├── config.json              # File cấu hình giá trị baseline & danh mục cổ phiếu theo dõi
├── words.json               # Bộ dữ liệu 30+ chữ Hán chiết tự mẫu kèm bộ thủ & ví dụ
├── requirements.txt         # Các thư viện Python phụ thuộc (vnstock>=4.0.0, Pillow, requests)
├── dashboard_runner.sh      # Shell script chạy trên máy Kindle (Bật Wi-Fi -> Fetch PNG -> eips -> rtcwake)
├── install_kindle.sh        # Script tự động cài đặt KUAL extension trên Kindle
├── dashboard.png            # File ảnh đầu ra (600x800 8-bit Grayscale)
├── fonts/                   # Thư mục chứa phông chữ TTF (NotoSans-Regular, NotoSans-Bold, NotoSansSC-Regular)
├── photos/                  # Thư mục chứa ảnh cá nhân tùy chọn
└── .github/
    └── workflows/
        └── generate.yml     # Workflow GitHub Actions tự động render 2 lần/ngày (05:30 & 17:30)
```

---

## 🛠️ HƯỚNG DẪN CHẠY THỬ TRÊN PC (LOCAL TEST)

1. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

2. Chạy render tạo ảnh `dashboard.png` locally:
   ```bash
   python render_dashboard.py
   ```
   Ảnh `dashboard.png` (600x800 Grayscale) sẽ được cập nhật trực tiếp tại thư mục dự án.

---

## 🚀 HƯỚNG DẪN TRIỂN KHAI CHI TIẾT TỪ PC ĐẾN KINDLE

### PHẦN 1: TRIỂN KHAI TRÊN GITHUB (AUTOMATED SERVER RENDER)

1. **Tạo Repository trên GitHub**:
   - Vào [github.com/new](https://github.com/new) tạo một repo mới (Đặt tên ví dụ: `kindle-dashboard`, chế độ **Public**).

2. **Đẩy mã nguồn từ PC lên GitHub**:
   - Tại thư mục `d:\code-cho-kindle\dashboard`, chạy các lệnh Git:
     ```bash
     git init
     git add .
     git commit -m "Complete Kindle Touch Dashboard v2.0"
     git branch -M main
     git remote add origin https://github.com/TÊN_GITHUB_CỦA_BẠN/kindle-dashboard.git
     git push -u origin main
     ```

3. **Cấp quyền Write cho GitHub Actions (BẮT BUỘC)**:
   - Vào GitHub Repo -> **Settings** -> **Actions** -> **General**.
   - Tại mục **Workflow permissions**, chọn **Read and write permissions**.
   - Bấm **Save**.

4. **Cơ chế chạy tự động**:
   - GitHub Actions (`generate.yml`) sẽ tự động chạy render ảnh lúc **05:30** và **17:30** mỗi ngày (Giờ Việt Nam).
   - Bạn cũng có thể vào tab **Actions** -> chọn **Render Kindle Dashboard** -> bấm **Run workflow** để kích hoạt ngay lập tức.
   - Ảnh tĩnh kết quả trên GitHub Raw có dạng:
     `https://raw.githubusercontent.com/TÊN_GITHUB_CỦA_BẠN/kindle-dashboard/main/dashboard.png`

---

### PHẦN 2: CÀI ĐẶT LÊN MÁY KINDLE TOUCH 4TH GEN (D01200)

> **Yêu cầu**: Kindle Touch đã Jailbreak và cài đặt **KUAL** (Kindle Unified Application Launcher).

1. **Cắm cáp USB kết nối Kindle với PC**:
   - Máy tính sẽ nhận ổ đĩa Kindle (Ví dụ ổ `E:\` hoặc `F:\`).

2. **Chép file cài đặt vào Kindle**:
   - Tạo thư mục `dashboard` ngay tại ổ đĩa gốc Kindle: `E:\dashboard\` (đường dẫn hệ thống Kindle là `/mnt/us/dashboard/`).
   - Chép 2 file từ PC vào thư mục `E:\dashboard\`:
     - [`dashboard_runner.sh`](file:///d:/code-cho-kindle/dashboard/dashboard_runner.sh)
     - [`install_kindle.sh`](file:///d:/code-cho-kindle/dashboard/install_kindle.sh)

3. **Cấu hình Tên GitHub trên Kindle**:
   - Mở file `E:\dashboard\dashboard_runner.sh` bằng text editor (Notepad / VS Code).
   - Sửa dòng 8-9 thành thông tin GitHub của bạn:
     ```sh
     GITHUB_USER="TÊN_GITHUB_CỦA_BẠN"
     GITHUB_REPO="kindle-dashboard"
     ```
   - Lưu file lại và ngắt kết nối USB.

4. **Kích hoạt trên Kindle**:
   - Trên màn hình Kindle, mở ứng dụng **KUAL**.
   - Chọn mục **Dashboard Setup** -> Bấm **Enable Dashboard Auto-Refresh**.
   - Kindle sẽ tự động bật Wi-Fi, tải `dashboard.png` từ GitHub, cập nhật màn hình qua `eips -g` và đi vào chế độ ngủ sâu `rtcwake` tiết kiệm 100% pin!
