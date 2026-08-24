# 📱 Kindle Touch E-ink Smart Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Kindle Touch](https://img.shields.io/badge/Platform-Kindle_Touch_4th_Gen-orange.svg)](https://amazon.com)

[**Tiếng Việt**](#-tiếng-việt) | [**English**](#-english)

---

## 🇻🇳 Tiếng Việt

Hệ thống **E-ink Smart Dashboard** tự động hóa dành cho máy đọc sách **Kindle Touch (4th Generation - Model D01200)** và các thiết bị màn hình E-ink dải tần 600x800 Grayscale (Thang xám 16 cấp độ).

Dự án tự động hóa quá trình cào dữ liệu thời tiết, chỉ số tài chính, giá vàng SJC, chứng khoán Việt Nam (HOSE/HNX), từ vựng Hán tự chiết tự mỗi ngày, kết hợp lịch âm dương và bộ quản lý ảnh cá nhân trực tuyến qua Web Configurator.

### ✨ TÍNH NĂNG CHÍNH

1. **🖼️ Khung Ảnh Phong Cảnh & Ảnh Cá Nhân**:
   - Tự động hiển thị ngẫu nhiên các bức ảnh cá nhân nằm trong thư mục `photos/` hoặc tải ảnh phong cảnh chất lượng cao.
   - Thuật toán tự động tối ưu hóa hình ảnh: Chuyển đổi dải tần 8-bit Grayscale, nâng độ tương phản và tăng độ sắc nét tối ưu cho tấm nền E-ink.

2. **📈 Thị Trường & Tài Chính Real-time (`MarketCrawler`)**:
   - **Giá vàng SJC**: Cào dữ liệu giá vàng miếng SJC mua vào - bán ra theo thời gian thực từ `giavang.org`.
   - **Chỉ số VN-Index**: Cập nhật điểm số đóng cửa phiên và tỷ lệ phần trăm thay đổi.
   - **Danh mục Cổ phiếu Theo dõi (Watchlist)**: Tích hợp Simplize REST API cào giá khớp lệnh và % tăng giảm các mã cổ phiếu chứng khoán Việt Nam (HOSE/HNX).

3. **🈲 Học Từ Vựng Hán Tự & Chiết Tự Mỗi Ngày**:
   - Hiển thị chữ Hán to rõ (`56pt`) đúc phông CJK BOLD high-contrast (`NotoSansSC-Bold`).
   - Cung cấp Pinyin, Hán-Việt, phân tích bộ thủ, câu chuyện chiết tự dễ nhớ và các ví dụ ghép từ thực tế.

4. **🌤️ Dự Báo Thời Tiết 3 Ngày**:
   - Tích hợp API Open-Meteo dự báo thời tiết tự động theo địa điểm tùy chỉnh.
   - Hiển thị dự báo nhiệt độ 3 ngày, chỉ số chất lượng không khí (AQI), độ ẩm (%) và cảm giác nhiệt thực tế.

5. **📅 Lịch Âm - Dương & Sự Kiện Tùy Chỉnh**:
   - Lưới lịch tháng đầy đủ Âm - Dương lịch, tự động khoanh tròn ngày hiện tại và làm nổi bật các ngày Mùng 1 & Rằm hàng tháng.
   - Danh sách quản lý các ngày nghỉ lễ Quốc gia và sự kiện cá nhân tùy chỉnh.

6. **🌐 Web Configurator Trực Tuyến**:
   - Giao diện Web đơn giản deployed trực tiếp qua GitHub Pages.
   - Cho phép chỉnh sửa Tiêu đề Dashboard, chọn mã cổ phiếu theo dõi, đổi thành phố thời tiết, quản lý danh sách sự kiện và bộ sưu tập ảnh cá nhân (tải lên / xóa ảnh thumbnail trực tiếp via GitHub REST API).

---

## 🇬🇧 English

An automated **E-ink Smart Dashboard** built for the **Kindle Touch (4th Generation - Model D01200)** and compatible 600x800 16-level grayscale E-ink displays.

This project automates daily rendering of weather forecasts, financial market indices (VN-Index, SJC Gold, stock watchlists), Chinese character etymology breakdown, lunar-solar calendar grid, and an interactive Web Configurator for online management.

### ✨ KEY FEATURES

1. **🖼️ Dynamic Landscape & Personal Photo Frame**:
   - Automatically selects and renders random photos from the `photos/` directory or fetches high-resolution landscapes.
   - Built-in E-ink image optimization: Converts to 8-bit Grayscale, enhances contrast, and applies sharpening algorithms tailored for E-ink panels.

2. **📈 Real-Time Financial Market Crawler (`MarketCrawler`)**:
   - **SJC Gold Prices**: Live buy/sell prices scraped directly from `giavang.org`.
   - **VN-Index**: Real-time closing index points and percentage changes.
   - **Stock Watchlist**: Powered by Simplize REST API for live HOSE/HNX stock market quotes and daily percentage shifts.

3. **🈲 Daily Chinese Character & Etymology Breakdown**:
   - High-contrast large character display (`56pt`) rendered with Google's `NotoSansSC-Bold` CJK font.
   - Complete with Pinyin, Sino-Vietnamese readings, radical breakdowns, mnemonic stories, and real-world word examples.

4. **🌤️ 3-Day Weather Forecast**:
   - Integrated Open-Meteo API providing location-based forecasts.
   - Displays 3-day weather conditions, Air Quality Index (AQI), relative humidity (%), and apparent temperature ("feels like").

5. **📅 Solar-Lunar Calendar & Personal Events**:
   - Full monthly calendar grid supporting both Gregorian and Lunar dates.
   - Highlights the current day and marks the 1st & 15th (Full Moon) of every lunar month.
   - Dynamic schedule block for national holidays and custom events.

6. **🌐 Web Configurator App**:
   - Single-page web interface deployed seamlessly via GitHub Pages.
   - Customize Dashboard Title, stock tickers, weather location, holiday schedule, and manage photo gallery thumbnails (Upload / Delete via GitHub REST API).

---

## 🛠️ PROJECT STRUCTURE

```text
kindle-dashboard/
├── render_dashboard.py      # Core Python renderer using PIL/Pillow
├── vnstock_crawler.py       # Multi-provider market data crawler (Simplize, giavang.org)
├── config.json              # Baseline configuration (Title, stock tickers, location, events)
├── words.json               # Daily Chinese character & etymology database
├── dashboard_runner.sh      # Kindle shell runner script (Smart RTC Wakeup & Anti-Ghosting)
├── index.html               # Web Configurator application (GitHub Pages)
├── docs/                    # GitHub Pages deployment directory
├── fonts/                   # TTF/OTF font assets (NotoSans, NotoSansSC-Bold)
├── photos/                  # Personal photo gallery directory
└── .github/
    └── workflows/
        └── generate.yml     # Automated GitHub Actions workflow (23:55 & 15:25 ICT)
```

---

## 🚀 INSTALLATION & SETUP GUIDE

### 1. Local Testing (PC)

- **Install dependencies**:
  ```bash
  pip install -r requirements.txt
  ```

- **Run local render**:
  ```bash
  python render_dashboard.py
  ```
  The generated `dashboard.png` (600x800 Grayscale) will be saved in the root directory.

---

### 2. Automated Cloud Setup (GitHub Actions & Pages)

1. **Push repository to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - E-ink Kindle Dashboard"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
   git push -u origin main
   ```

2. **Enable Workflow Write Permissions**:
   - Navigate to **Settings** -> **Actions** -> **General** on your repository.
   - Under **Workflow permissions**, select **Read and write permissions** and click **Save**.

3. **Enable Web Configurator (GitHub Pages)**:
   - Navigate to **Settings** -> **Pages**.
   - Under **Source**, select **Deploy from a branch**, set branch to `main` and folder to `/docs` (or `/root`). Click **Save**.
   - Your Web Configurator app will be live at: `https://<YOUR_USERNAME>.github.io/<YOUR_REPO>/`.

---

### 3. Deployment on Kindle Touch (D01200)

> **Requirement**: Your Kindle Touch must be jailbroken with **KUAL** (Kindle Unified Application Launcher) installed.

1. Connect your Kindle to your PC via USB.
2. Create a `dashboard` directory on your Kindle's root drive: `/mnt/us/dashboard/` (e.g. `E:\dashboard\` on Windows).
3. Copy [`dashboard_runner.sh`](file:///d:/code-cho-kindle/dashboard/dashboard_runner.sh) into `E:\dashboard\`.
4. Edit lines 11-12 of `dashboard_runner.sh` with your GitHub details:
   ```sh
   GITHUB_USER="<YOUR_USERNAME>"
   GITHUB_REPO="<YOUR_REPO>"
   ```
5. Eject USB, launch **KUAL** on your Kindle, and select **Dashboard Setup** -> **Enable Dashboard Auto-Refresh**.
6. The Kindle will automatically wake up and update at **00:00 ICT** (Midnight date & Hanzi change) and **15:30 ICT** (Stock market closing).

---

## 📄 LICENSE

This project is open-source under the [MIT License](LICENSE). Contributions, issues, and feature requests are welcome!
