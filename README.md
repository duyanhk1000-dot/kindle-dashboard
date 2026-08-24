# 📱 Kindle Touch E-ink Smart Dashboard

Hệ thống **E-ink Smart Dashboard** tự động hóa dành cho máy đọc sách **Kindle Touch (4th Generation - Model D01200)** và các thiết bị màn hình E-ink dải tần 600x800 Grayscale (Thang xám 16 cấp độ).

Dự án tự động hóa quá trình cào dữ liệu thời tiết, chỉ số tài chính, giá vàng SJC, chứng khoán Việt Nam (HOSE/HNX), từ vựng Hán tự chiết tự mỗi ngày, kết hợp lịch âm dương và bộ quản lý ảnh cá nhân trực tuyến qua Web Configurator.

---

## ✨ TÍNH NĂNG CHÍNH

### 1. 🖼️ Khung Ảnh Phong Cảnh & Ảnh Cá Nhân
- Tự động hiển thị ngẫu nhiên các bức ảnh cá nhân nằm trong thư mục `photos/` hoặc tải ảnh phong cảnh chất lượng cao.
- Thuật toán tự động tối ưu hóa hình ảnh: Chuyển đổi dải tần 8-bit Grayscale, nâng độ tương phản và tăng độ sắc nét tối ưu cho tấm nền E-ink.

### 2. 📈 Thị Trường & Tài Chính Real-time (`MarketCrawler`)
- **Giá vàng SJC**: Cào dữ liệu giá vàng miếng SJC mua vào - bán ra theo thời gian thực từ `giavang.org`.
- **Chỉ số VN-Index**: Cập nhật điểm số đóng cửa phiên và tỷ lệ phần trăm thay đổi.
- **Danh mục Cổ phiếu Theo dõi (Watchlist)**: Tích hợp API Simplize REST API cào giá khớp lệnh và % tăng giảm các mã cổ phiếu chứng khoán Việt Nam (HOSE/HNX).

### 3. 🈲 Học Từ Vựng Hán Tự & Chiết Tự Mỗi Ngày
- Hiển thị chữ Hán to rõ (`56pt`) đúc phông CJK BOLD high-contrast (`NotoSansSC-Bold`).
- Cung cấp Pinyin, Hán-Việt, phân tích bộ thủ, câu chuyện chiết tự dễ nhớ và các ví dụ ghép từ thực tế.

### 4. 🌤️ Dự Báo Thời Tiết 3 Ngày
- Tích hợp API Open-Meteo dự báo thời tiết tự động theo địa điểm tùy chỉnh.
- Hiển thị dự báo nhiệt độ 3 ngày, chỉ số chất lượng không khí (AQI), độ ẩm (%) và cảm giác nhiệt thực tế.

### 5. 📅 Lịch Âm - Dương & Sự Kiện Tùy Chỉnh
- Lưới lịch tháng đầy đủ Âm - Dương lịch, tự động khoanh tròn ngày hiện tại và làm nổi bật các ngày Mùng 1 & Rằm hàng tháng.
- Danh sách quản lý các ngày nghỉ lễ Quốc gia và sự kiện cá nhân tùy chỉnh.

### 6. 🌐 Web Configurator Trực Tuyến
- Giao diện Web đơn giản deployed trực tiếp qua GitHub Pages.
- Cho phép chỉnh sửa Tiêu đề Dashboard, chọn mã cổ phiếu theo dõi, đổi thành phố thời tiết, quản lý danh sách sự kiện và bộ sưu tập ảnh cá nhân (tải lên / xóa ảnh thumbnail trực tiếp via GitHub REST API).

---

## 🛠️ CẤU TRÚC THƯ MỤC DỰ ÁN

```text
kindle-dashboard/
├── render_dashboard.py      # Core script tạo file ảnh dashboard.png (Pillow)
├── vnstock_crawler.py       # Multi-Provider Market Crawler (Simplize, giavang.org, TCBS)
├── config.json              # File cấu hình baseline (Tiêu đề, mã cổ phiếu, thời tiết, sự kiện)
├── words.json               # Cơ sở dữ liệu chữ Hán chiết tự mẫu
├── dashboard_runner.sh      # Shell script chạy trên Kindle (Smart RTC Wakeup & Anti-Ghosting)
├── index.html               # Trang Web Configurator trực tuyến (GitHub Pages)
├── docs/                    # Thư mục deployment cho GitHub Pages
├── fonts/                   # Thư mục chứa phông chữ TTF/OTF (NotoSans, NotoSansSC-Bold)
├── photos/                  # Thư mục lưu trữ ảnh phong cảnh / ảnh cá nhân
└── .github/
    └── workflows/
        └── generate.yml     # Workflow GitHub Actions tự động render (23:55 & 15:25 ICT)
```

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT & SỬ DỤNG

### 1. Chạy Thử Trên Máy Tính (Local Testing)

- **Cài đặt thư viện phụ thuộc**:
  ```bash
  pip install -r requirements.txt
  ```

- **Thực thi render tạo ảnh**:
  ```bash
  python render_dashboard.py
  ```
  File ảnh `dashboard.png` (600x800 Grayscale) sẽ được tạo thành công tại thư mục gốc của dự án.

---

### 2. Triển Khai Tự Động Hóa Trực Tuyến (GitHub Actions & Pages)

1. **Đẩy mã nguồn lên GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - E-ink Kindle Dashboard"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
   git push -u origin main
   ```

2. **Bật quyền Ghi cho Workflow**:
   - Truy cập **Settings** -> **Actions** -> **General** trên GitHub Repository.
   - Tại mục **Workflow permissions**, chọn **Read and write permissions** và bấm **Save**.

3. **Bật Trang Web Configurator (GitHub Pages)**:
   - Truy cập **Settings** -> **Pages**.
   - Tại mục **Source**, chọn **Deploy from a branch**, branch chọn `main` và thư mục chọn `/docs` (hoặc `/root`). Bấm **Save**.
   - Trang Web tùy chỉnh trực tuyến sẽ xuất hiện tại địa chỉ: `https://<YOUR_USERNAME>.github.io/<YOUR_REPO>/`.

---

### 3. Cài Đặt Lên Thiết Bị Kindle Touch (D01200)

> **Yêu cầu**: Kindle Touch đã được Jailbreak và cài đặt ứng dụng **KUAL** (Kindle Unified Application Launcher).

1. Kết nối Kindle với máy tính qua cáp USB.
2. Tạo thư mục `dashboard` trên ổ đĩa gốc của Kindle: `/mnt/us/dashboard/` (Ví dụ trên Windows là `E:\dashboard\`).
3. Chép file [`dashboard_runner.sh`](file:///d:/code-cho-kindle/dashboard/dashboard_runner.sh) vào thư mục `dashboard` trên Kindle.
4. Mở file `dashboard_runner.sh` bằng text editor và thay đổi 2 dòng thông tin repository của bạn:
   ```sh
   GITHUB_USER="<YOUR_USERNAME>"
   GITHUB_REPO="<YOUR_REPO>"
   ```
5. Ngắt kết nối USB, mở ứng dụng **KUAL** trên Kindle và chọn **Dashboard Setup** -> **Enable Dashboard Auto-Refresh**.
6. Kindle sẽ tự động cập nhật Dashboard theo lịch thông minh (**00:00 ICT** cho ngày mới & **15:30 ICT** chốt phiên thị trường).

---

## 📄 GIẤY PHÉP (LICENSE)

Dự án được phát hành theo giấy phép open-source [MIT License](LICENSE). Trân trọng mọi sự đóng góp và phát triển từ cộng đồng!
