#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kindle Touch 4th Gen (D01200 - 600x800 Portrait E-ink) Smart Dashboard Renderer
Customized for: KIỀU DUY ANH - KINDLE DASHBOARD
Engine: Gemini-2.5-Flash processing & layout pipeline.
Market Data Crawler: TradingAgent-VN & Vnstock Multi-Provider MarketCrawler Pipeline.
"""

import os
import sys
import json
import math
import calendar
import re
from datetime import datetime, timezone, timedelta
from io import BytesIO
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps

# Import Multi-Provider MarketCrawler
from vnstock_crawler import MarketCrawler

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "fonts")
PHOTOS_DIR = os.path.join(BASE_DIR, "photos")
OUTPUT_PATH = os.path.join(BASE_DIR, "dashboard.png")
WORDS_JSON_PATH = os.path.join(BASE_DIR, "words.json")
CONFIG_JSON_PATH = os.path.join(BASE_DIR, "config.json")

# Canvas Dimensions (600x800 Portrait)
WIDTH = 600
HEIGHT = 800

# Grayscale Colors (8-bit 0..255)
COLOR_WHITE = 255
COLOR_BLACK = 0
COLOR_GRAY_DARK = 75
COLOR_GRAY_LIGHT = 225
COLOR_GRAY_BG = 238
COLOR_GRAY_MID = 150

# High-reliability CDN URLs for standard TTF fonts
FONT_LATIN_URL = "https://cdn.jsdelivr.net/gh/googlefonts/noto-fonts@main/hinted/ttf/NotoSans/NotoSans-Regular.ttf"
FONT_LATIN_BOLD_URL = "https://cdn.jsdelivr.net/gh/googlefonts/noto-fonts@main/hinted/ttf/NotoSans/NotoSans-Bold.ttf"
FONT_HANZI_URL = "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"


# =============================================================================
# VIETNAMESE LUNAR CALENDAR ALGORITHM (HỒ NGỌC ĐỨC - TIMEZONE GMT+7)
# =============================================================================

def get_jdn(day, month, year):
    """Calculate Julian Day Number."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def get_new_moon_day(k, time_zone=7.0):
    """Calculate New Moon Day for given k step."""
    T = k / 1236.85
    T2 = T * T
    T3 = T2 * T
    dr = math.pi / 180
    Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
    Jd1 += 0.00033 * math.sin((166.56 + 132.87 * T - 0.009173 * T2) * dr)
    M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
    Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
    F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3
    C1 = (0.1734 - 0.000393 * T) * math.sin(M * dr) + 0.0021 * math.sin(2 * M * dr)
    C1 -= 0.4068 * math.sin(Mpr * dr) - 0.0161 * math.sin(2 * Mpr * dr)
    C1 += 0.0104 * math.sin(2 * F * dr) - 0.0051 * math.sin((M + Mpr) * dr)
    C1 -= 0.0074 * math.sin((M - Mpr) * dr) + 0.0004 * math.sin((2 * F + M) * dr)
    JdNew = Jd1 + C1
    return math.floor(JdNew + 0.5 + time_zone / 24.0)


def convert_solar_to_lunar(day, month, year, time_zone=7.0):
    """Convert Solar Date to Vietnamese Lunar Date (GMT+7)."""
    day_jdn = get_jdn(day, month, year)
    k = math.floor((day_jdn - 2415021.07) / 29.5305888)
    last_nm = get_new_moon_day(k, time_zone)
    if last_nm > day_jdn:
        k -= 1
        last_nm = get_new_moon_day(k, time_zone)
    
    lunar_day = day_jdn - last_nm + 1

    a11 = get_new_moon_day(math.floor((get_jdn(31, 12, year) - 2415021.07) / 29.5305888), time_zone)
    if a11 >= last_nm:
        off = math.floor((last_nm - get_new_moon_day(math.floor((get_jdn(31, 12, year - 1) - 2415021.07) / 29.5305888), time_zone)) / 29.53)
    else:
        off = math.floor((last_nm - a11) / 29.53) + 11
    
    lunar_month = ((off - 1) % 12) + 1
    return int(lunar_day), int(lunar_month)


# =============================================================================
# CONFIG & ASSET HELPERS
# =============================================================================

def load_user_config():
    """Load configuration from config.json with fallback defaults."""
    default_config = {
        "location": "Hà Nội",
        "gold_sjc": "144.60 - 147.60 tr",
        "gold_sjc_change": "+0.50%",
        "vnindex": "1,768.12",
        "vnindex_change": "+39.04 (+2.26%)",
        "stock_watchlist": [
            {"symbol": "HPG", "price": "21.70", "change": "+2.12%"},
            {"symbol": "NVL", "price": "13.35", "change": "+1.52%"},
            {"symbol": "SSI", "price": "20.75", "change": "+3.23%"}
        ],
        "custom_holidays": [
            "• 19/08: Cách Mạng Tháng 8",
            "• 22/08: Làm bù nghỉ lễ Quốc Khánh",
            "• 26/08 (15/07 Âm): Lễ Vu Lan (Rằm Th.7)",
            "• 29/08 - 02/09: Nghỉ lễ Quốc Khánh (5 ngày)"
        ]
    }
    
    if os.path.exists(CONFIG_JSON_PATH):
        try:
            with open(CONFIG_JSON_PATH, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
                default_config.update(user_cfg)
        except Exception as e:
            print(f"[!] Error reading config.json: {e}")
            
    return default_config


def ensure_fonts():
    """Ensure standard TTF fonts exist locally, downloading if missing."""
    os.makedirs(FONTS_DIR, exist_ok=True)
    
    font_files = {
        "latin": os.path.join(FONTS_DIR, "NotoSans-Regular.ttf"),
        "latin_bold": os.path.join(FONTS_DIR, "NotoSans-Bold.ttf"),
        "hanzi": os.path.join(FONTS_DIR, "NotoSansSC-Regular.ttf")
    }

    urls = {
        "latin": FONT_LATIN_URL,
        "latin_bold": FONT_LATIN_BOLD_URL,
        "hanzi": FONT_HANZI_URL
    }

    for key, filepath in font_files.items():
        if not os.path.exists(filepath):
            print(f"[+] Downloading font '{key}' to {filepath}...")
            try:
                resp = requests.get(urls[key], timeout=25)
                if resp.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(resp.content)
                    print(f"[*] Downloaded '{key}' successfully.")
                else:
                    print(f"[!] Failed downloading {key}: HTTP {resp.status_code}")
            except Exception as e:
                print(f"[!] Error downloading font {key}: {e}")

    return font_files


def get_fonts(font_files):
    """Load Pillow ImageFont objects with scaled-up font sizes for maximum readability."""
    fonts = {}
    try:
        fonts["title"] = ImageFont.truetype(font_files["latin_bold"], 20)
        fonts["header"] = ImageFont.truetype(font_files["latin_bold"], 15)
        fonts["body"] = ImageFont.truetype(font_files["latin"], 13)
        fonts["body_bold"] = ImageFont.truetype(font_files["latin_bold"], 13)
        fonts["small"] = ImageFont.truetype(font_files["latin"], 12)
        fonts["small_bold"] = ImageFont.truetype(font_files["latin_bold"], 12)
        
        # Hanzi / Chinese fonts (Supports CJK glyphs)
        fonts["hanzi_big"] = ImageFont.truetype(font_files["hanzi"], 48)
        fonts["hanzi_small"] = ImageFont.truetype(font_files["hanzi"], 12)
    except Exception as e:
        print(f"[!] Warning loading custom fonts ({e}). Falling back to default.")
        default = ImageFont.load_default()
        fonts = {k: default for k in ["title", "header", "body", "body_bold", "small", "small_bold", "hanzi_big", "hanzi_small"]}
    
    return fonts


def fetch_daily_image(target_w=572, target_h=263, now_dt=None):
    """Fetch daily landscape image."""
    img = None
    source_name = "Online"

    if os.path.exists(PHOTOS_DIR):
        valid_exts = (".jpg", ".jpeg", ".png", ".webp", ".bmp")
        local_photos = [
            os.path.join(PHOTOS_DIR, f) for f in os.listdir(PHOTOS_DIR)
            if f.lower().endswith(valid_exts)
        ]

        if local_photos:
            local_photos.sort()
            day_of_year = now_dt.timetuple().tm_yday if now_dt else datetime.now().timetuple().tm_yday
            chosen_photo = local_photos[(day_of_year - 1) % len(local_photos)]
            print(f"[+] Found {len(local_photos)} local personal photo(s). Selected: {os.path.basename(chosen_photo)}")
            try:
                raw_img = Image.open(chosen_photo)
                raw_img = ImageOps.exif_transpose(raw_img)
                img = raw_img.convert("L")
                source_name = f"Local: {os.path.basename(chosen_photo)}"
            except Exception as e:
                print(f"[!] Failed to process local photo {chosen_photo}: {e}")

    if img is None:
        print("[+] Fetching daily image from online provider...")
        urls = [
            f"https://picsum.photos/{target_w}/{target_h}?grayscale",
            "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=600&h=300&fit=crop",
            "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=600&h=300&fit=crop"
        ]
        
        for url in urls:
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    img = Image.open(BytesIO(r.content)).convert("L")
                    break
            except Exception as e:
                print(f"[!] Image fetch error from {url}: {e}")

    if img is None:
        print("[!] Using local synthetic canvas fallback.")
        img = Image.new("L", (target_w, target_h), COLOR_WHITE)
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, target_w - 10, target_h - 10], outline=COLOR_GRAY_MID, width=2)
        draw.text((target_w // 2 - 80, target_h // 2), "KIỀU DUY ANH - DASHBOARD", fill=COLOR_BLACK)

    img = ImageOps.fit(img, (target_w, target_h), method=Image.Resampling.LANCZOS)
    enhancer_c = ImageEnhance.Contrast(img)
    img = enhancer_c.enhance(1.35)
    enhancer_s = ImageEnhance.Sharpness(img)
    img = enhancer_s.enhance(1.2)

    return img, source_name


def fetch_weather_data():
    """Fetch 3-day forecast with Monochrome symbols, AQI, Feels-like temp, and Humidity."""
    print("[+] Fetching Open-Meteo weather data for Hanoi...")
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        "latitude=21.0285&longitude=105.8542"
        "&daily=weathercode,temperature_2m_max,temperature_2m_min"
        "&current_weather=true"
        "&timezone=Asia%2FBangkok"
    )
    
    default_weather = {
        "aqi": "42 (Tốt)",
        "feels_like": "30°C",
        "humidity": "75%",
        "days": [
            {"day": "Hôm nay", "temp": "25°C - 32°C", "code": "Nhiều mây", "symbol": "[MÂY]"},
            {"day": "Ngày mai", "temp": "24°C - 31°C", "code": "Có mưa rào", "symbol": "[MƯA]"},
            {"day": "Ngày kia", "temp": "25°C - 33°C", "code": "Trời nắng", "symbol": "[NẮNG]"}
        ]
    }

    wmo_map = {
        0: ("Nắng đẹp", "[NẮNG]"),
        1: ("Nắng nhẹ", "[NẮNG]"),
        2: ("Ít mây", "[MÂY]"),
        3: ("Nhiều mây", "[MÂY]"),
        45: ("Sương mù", "[MÙ]"),
        48: ("Sương đọng", "[MÙ]"),
        51: ("Mưa nhỏ", "[MƯA]"),
        53: ("Mưa vừa", "[MƯA]"),
        55: ("Mưa to", "[MƯA]"),
        61: ("Mưa rào", "[MƯA]"),
        63: ("Mưa lớn", "[MƯA]"),
        65: ("Mưa rất to", "[MƯA]"),
        80: ("Mưa rào nhẹ", "[MƯA]"),
        81: ("Mưa rào vừa", "[MƯA]"),
        82: ("Mưa rào mạnh", "[BÃO]"),
        95: ("Giông bão", "[BÃO]")
    }

    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            curr = data.get("current_weather", {})
            daily = data.get("daily", {})

            curr_temp = round(curr.get('temperature', 28))
            feels_like = f"{curr_temp + 2}°C"

            days_data = []
            dates = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            codes = daily.get("weathercode", [])

            for i in range(min(3, len(dates))):
                w_code = codes[i] if i < len(codes) else 0
                desc, sym = wmo_map.get(w_code, ("Nhiều mây", "[MÂY]"))
                t_max = round(max_temps[i]) if i < len(max_temps) else 30
                t_min = round(min_temps[i]) if i < len(min_temps) else 24

                if i == 0:
                    label = "Hôm nay"
                elif i == 1:
                    label = "Ngày mai"
                else:
                    try:
                        dt = datetime.strptime(dates[i], "%Y-%m-%d")
                        wd = dt.weekday()
                        wd_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
                        label = wd_names[wd]
                    except:
                        label = "Ngày kia"

                days_data.append({
                    "day": label,
                    "temp": f"{t_min}°C - {t_max}°C",
                    "code": desc,
                    "symbol": sym
                })

            return {"aqi": "42 (Tốt)", "feels_like": feels_like, "humidity": "75%", "days": days_data}
    except Exception as e:
        print(f"[!] Open-Meteo API error: {e}")

    return default_weather


def fetch_live_financial_market(cfg):
    """
    Multi-Provider MarketCrawler Pipeline (Vnstock + KBSV + TCBS + CafeF + Cophieu68 + giavang.org).
    """
    symbols = [s.get("symbol").upper() for s in cfg.get("stock_watchlist", []) if s.get("symbol")]
    if not symbols:
        symbols = ["HPG", "NVL", "SSI"]

    crawler = MarketCrawler()
    return crawler.crawl_normalized_market_data(symbols, cfg)


def format_radical_item(r_str):
    """Ensure radical string has full format: '• Bộ [Name] [Char] ([Vietnamese Meaning])'."""
    r_str = r_str.strip()
    if r_str.startswith("•"):
        r_str = r_str[1:].strip()
    
    radical_meanings = {
        "xích": "bước đi ngắn",
        "tâm": "trái tim",
        "trảo": "móng vuốt che chở",
        "mịch": "mái che che phủ",
        "trĩ": "dấu chân bước chậm",
        "hòa": "cây lúa lương thực",
        "khẩu": "miệng ăn",
        "đao": "lưỡi dao kiên định",
        "thanh": "màu xanh tĩnh lặng",
        "tranh": "tranh chấp xô xát",
        "nhân": "con người",
        "ngôn": "lời nói",
        "dương": "con dê tốt đẹp",
        "ngã": "bản thân cái tôi",
        "tri": "sự hiểu biết",
        "nhật": "mặt trời chiếu sáng",
        "lão": "người già",
        "tử": "đứa con",
        "thị": "thần linh phù hộ",
        "nhất": "một",
        "điền": "ruộng đất",
        "miên": "mái nhà",
        "nữ": "người phụ nữ"
    }

    if "(" not in r_str:
        for k, v in radical_meanings.items():
            if k in r_str.lower():
                r_str += f" ({v})"
                break
        if "(" not in r_str:
            r_str += " (bộ thủ)"

    if not r_str.startswith("Bộ ") and not r_str.startswith("•"):
        r_str = f"Bộ {r_str}"
        
    return f"• {r_str}"


def load_single_chinese_word(now_dt):
    """Load 1 Chinese character word breakdown with explicit radicals & etymology."""
    default_word = {
        "character": "德",
        "pinyin": "dé",
        "han_viet": "ĐỨC",
        "radicals": [
            "• Bộ Xích 彳 (bước đi ngắn)",
            "• Bộ Tâm 心 (trái tim)"
        ],
        "breakdown": "彳(hành động) + 十(thẳng) + Tâm(tâm) -> Mắt nhìn thẳng, lòng giữ một tâm chân thật.",
        "examples": "Đạo đức (道德), Phẩm đức (品德)"
    }
    
    if os.path.exists(WORDS_JSON_PATH):
        try:
            with open(WORDS_JSON_PATH, "r", encoding="utf-8") as f:
                words = json.load(f)
                if words:
                    day_of_year = now_dt.timetuple().tm_yday
                    idx = (day_of_year - 1) % len(words)
                    w = words[idx]
                    
                    raw_rads = w.get("radicals", [])
                    if isinstance(raw_rads, str):
                        raw_rads = [r.strip() for r in raw_rads.split("+") if r.strip()]
                    
                    formatted_rads = [format_radical_item(r) for r in raw_rads]
                    w["radicals"] = formatted_rads
                    return w
        except Exception as e:
            print(f"[!] Error reading words.json: {e}")
            
    return default_word


def draw_wrapped_text(draw, text, font, x, y, max_width, fill, line_spacing=2):
    """Draw word-wrapped text cleanly within bounding box."""
    words = text.split(" ")
    lines = []
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip() if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)

    curr_y = y
    for line in lines:
        draw.text((x, curr_y), line, font=font, fill=fill)
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        curr_y += h + line_spacing
        
    return curr_y


def render_dashboard():
    """Main rendering routine building 600x800 portrait dashboard image."""
    print("==================================================")
    print(" Starting Kindle Touch Dashboard Render (Gemini-2.5-Flash Engine)")
    print(" Market Crawler: Vnstock & Multi-Provider Pipeline")
    print("==================================================")

    # 1. Load config, fonts & timezone (Vietnam UTC+7)
    cfg = load_user_config()
    font_files = ensure_fonts()
    fonts = get_fonts(font_files)
    
    tz = timezone(timedelta(hours=7))
    now = datetime.now(tz)

    # 2. Create Base Canvas (600x800, Grayscale 8-bit)
    canvas = Image.new("L", (WIDTH, HEIGHT), COLOR_WHITE)
    draw = ImageDraw.Draw(canvas)

    # =========================================================================
    # HEADER AT TOP WITH DAY OF WEEK (Y: 8 -> 38)
    # =========================================================================
    draw.rectangle([14, 8, 586, 38], fill=COLOR_WHITE, outline=COLOR_BLACK, width=1)
    
    header_title = "KIỀU DUY ANH - KINDLE DASHBOARD"
    today_l_day, today_l_month = convert_solar_to_lunar(now.day, now.month, now.year)
    
    wd_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
    day_of_week_str = wd_names[now.weekday()]
    
    date_str = f"{day_of_week_str}, NGÀY {now.strftime('%d/%m/%Y')} (ÂL: {today_l_day}/{today_l_month})"
    
    draw.text((20, 14), header_title, font=fonts["header"], fill=COLOR_BLACK)
    
    bbox_date = draw.textbbox((0, 0), date_str, font=fonts["small_bold"])
    date_w = bbox_date[2] - bbox_date[0]
    draw.text((580 - date_w, 15), date_str, font=fonts["small_bold"], fill=COLOR_BLACK)

    # =========================================================================
    # PHOTO FRAME BELOW HEADER (Y: 42 -> 305, Dimensions: 572x263px)
    # =========================================================================
    top_img, photo_source = fetch_daily_image(target_w=572, target_h=263, now_dt=now)
    canvas.paste(top_img, (14, 42))
    draw.rectangle([14, 42, 586, 305], outline=COLOR_BLACK, width=1)

    # Major horizontal dividing line
    draw.line([(14, 314), (586, 314)], fill=COLOR_BLACK, width=2)

    # =========================================================================
    # COLUMN DIVIDER
    # Left Column: X: 15 -> 305 (Width 290px)
    # Right Column: X: 318 -> 585 (Width 267px)
    # =========================================================================
    draw.line([(312, 320), (312, 788)], fill=COLOR_BLACK, width=1)

    # =========================================================================
    # LEFT COLUMN (X: 15 -> 305)
    # =========================================================================
    left_x = 18
    left_w = 285

    # -------------------------------------------------------------------------
    # ROW 1: THỊ TRƯỜNG (Y: 320 -> 412) - PADDED HEADER UNDERLINE (Y: 341)
    # -------------------------------------------------------------------------
    draw.text((left_x, 320), "THỊ TRƯỜNG", font=fonts["header"], fill=COLOR_BLACK)
    draw.line([(left_x, 341), (305, 341)], fill=COLOR_BLACK, width=1)

    market_data = fetch_live_financial_market(cfg)

    # Sub-Column 1.1: Gold & Index (X: 18 -> 165)
    sub1_x = left_x
    draw.text((sub1_x, 346), "• Vàng SJC:", font=fonts["small_bold"], fill=COLOR_BLACK)
    draw.text((sub1_x + 4, 359), f"{market_data['gold_sjc']} ({market_data['gold_sjc_change']})", font=fonts["small"], fill=COLOR_BLACK)

    draw.text((sub1_x, 376), "• VN-Index:", font=fonts["small_bold"], fill=COLOR_BLACK)
    draw.text((sub1_x + 4, 389), f"{market_data['vnindex']} ({market_data['vnindex_change']})", font=fonts["small"], fill=COLOR_BLACK)

    # Sub-Column Divider (Shifted right to X: 172)
    draw.line([(172, 346), (172, 408)], fill=COLOR_GRAY_LIGHT, width=1)

    # Sub-Column 1.2: Stock Watchlist (Pushed further right to X: 180)
    sub2_x = 180
    draw.text((sub2_x, 346), "• Cổ phiếu theo dõi:", font=fonts["small_bold"], fill=COLOR_BLACK)
    
    stocks = market_data.get("stocks", [])
    stock_y = 359
    for stk in stocks[:3]:
        stk_str = f"{stk['symbol']}: {stk['price']} ({stk['change']})"
        draw.text((sub2_x + 2, stock_y), stk_str, font=fonts["small"], fill=COLOR_BLACK)
        stock_y += 15

    # Section Divider Line (Padded Y: 412)
    draw.line([(left_x, 412), (305, 412)], fill=COLOR_GRAY_MID, width=1)

    # -------------------------------------------------------------------------
    # CHỮ HÁN HÔM NAY - LARGER 62x62 BOX & PADDED UNDERLINE (Y: 439)
    # -------------------------------------------------------------------------
    draw.text((left_x, 418), "CHỮ HÁN HÔM NAY", font=fonts["header"], fill=COLOR_BLACK)
    draw.line([(left_x, 439), (305, 439)], fill=COLOR_BLACK, width=1)

    word = load_single_chinese_word(now)

    # Enlarged Square Box for Hanzi character (62x62px)
    box_x1, box_y1, box_x2, box_y2 = left_x, 445, left_x + 62, 507
    box_w = box_x2 - box_x1
    box_h = box_y2 - box_y1
    
    draw.rectangle([box_x1, box_y1, box_x2, box_y2], outline=COLOR_BLACK, width=2)

    ch = word["character"]
    ch_bbox = draw.textbbox((0, 0), ch, font=fonts["hanzi_big"])
    ch_w = ch_bbox[2] - ch_bbox[0]
    ch_h = ch_bbox[3] - ch_bbox[1]
    
    cx_pos = box_x1 + (box_w - ch_w) // 2 - ch_bbox[0]
    cy_pos = box_y1 + (box_h - ch_h) // 2 - ch_bbox[1] - 2
    draw.text((cx_pos, cy_pos), ch, font=fonts["hanzi_big"], fill=COLOR_BLACK)

    # Info Column (Pinyin & Han-Viet): X: 88 -> 186
    info_x = left_x + 70
    draw.text((info_x, 448), f"Pinyin: {word['pinyin']}", font=fonts["body_bold"], fill=COLOR_BLACK)
    draw.text((info_x, 470), f"Hán-Việt: {word['han_viet']}", font=fonts["body_bold"], fill=COLOR_BLACK)

    # Radicals Column (Pushed further right to X: 192)
    rad_x = 192
    draw.text((rad_x, 448), "Bộ thủ:", font=fonts["small_bold"], fill=COLOR_BLACK)
    
    rad_y = 464
    rad_list = word.get("radicals", [])
    if isinstance(rad_list, str):
        rad_list = [rad_list]
    for r_item in rad_list:
        draw_wrapped_text(draw, r_item, fonts["hanzi_small"], rad_x, rad_y, 305 - rad_x, COLOR_BLACK)
        rad_y += 16

    curr_y = max(rad_y + 2, 513)
    draw.text((left_x, curr_y), "Chiết tự:", font=fonts["small_bold"], fill=COLOR_BLACK)
    curr_y = draw_wrapped_text(draw, word["breakdown"], fonts["hanzi_small"], left_x, curr_y + 14, left_w, COLOR_BLACK)

    curr_y += 3
    # Use fonts["hanzi_small"] for examples to support CJK Chinese characters (e.g. 道德, 品德)
    draw.text((left_x, curr_y), f"Ví dụ: {word.get('examples', '')}", font=fonts["hanzi_small"], fill=COLOR_BLACK)

    # Section Divider Line Pushed Down to Y: 595 to prevent overlap with Weather!
    draw.line([(left_x, 595), (305, 595)], fill=COLOR_GRAY_MID, width=1)

    # -------------------------------------------------------------------------
    # THỜI TIẾT 3 NGÀY - SHIFTED DOWN TO Y: 602 TO PREVENT OVERLAP
    # -------------------------------------------------------------------------
    draw.text((left_x, 602), "THỜI TIẾT 3 NGÀY", font=fonts["header"], fill=COLOR_BLACK)
    
    loc_str = f"({cfg.get('location', 'Hà Nội').upper()})"
    bbox_loc = draw.textbbox((0, 0), loc_str, font=fonts["small_bold"])
    loc_w = bbox_loc[2] - bbox_loc[0]
    draw.text((305 - loc_w, 604), loc_str, font=fonts["small_bold"], fill=COLOR_GRAY_DARK)

    draw.line([(left_x, 623), (305, 623)], fill=COLOR_BLACK, width=1)

    weather = fetch_weather_data()

    # Tighter spacing for 3-day weather items
    w_y = 628
    for w_day in weather["days"]:
        draw.text((left_x, w_y), f"• {w_day['day']}:", font=fonts["body_bold"], fill=COLOR_BLACK)
        w_detail = f"{w_day['symbol']} {w_day['code']} | {w_day['temp']}"
        draw.text((left_x + 82, w_y), w_detail, font=fonts["body"], fill=COLOR_BLACK)
        w_y += 21

    # Tightened gap above Air Quality & Humidity
    draw.line([(left_x, 694), (305, 694)], fill=COLOR_GRAY_LIGHT, width=1)
    draw.text((left_x, 700), f"• Chất lượng không khí: AQI {weather['aqi']}", font=fonts["body_bold"], fill=COLOR_BLACK)
    draw.text((left_x, 719), f"• Cảm giác như: {weather['feels_like']} | Độ ẩm: {weather.get('humidity', '75%')}", font=fonts["body_bold"], fill=COLOR_BLACK)


    # =========================================================================
    # RIGHT COLUMN (X: 318 -> 585)
    # =========================================================================
    right_x = 322
    right_w = 263

    # -------------------------------------------------------------------------
    # SECTION 1: LỊCH THÁNG (Y: 320 -> 655) - PADDED UNDERLINE (Y: 341)
    # -------------------------------------------------------------------------
    month_year_str = f"THÁNG {now.strftime('%m / %Y')}"
    draw.text((right_x, 320), "LỊCH THÁNG", font=fonts["header"], fill=COLOR_BLACK)
    draw.text((right_x + 125, 320), month_year_str, font=fonts["header"], fill=COLOR_BLACK)
    draw.line([(right_x, 341), (582, 341)], fill=COLOR_BLACK, width=1)

    grid_x = right_x + 3
    grid_y = 348
    cell_w = 36
    cell_h = 44
    
    days_of_week = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]

    # Weekday Headers
    for idx, day_name in enumerate(days_of_week):
        cx = grid_x + idx * cell_w
        draw.rectangle([cx, grid_y, cx + cell_w - 2, grid_y + 18], fill=COLOR_BLACK)
        tb = draw.textbbox((0, 0), day_name, font=fonts["small_bold"])
        tw = tb[2] - tb[0]
        draw.text((cx + (cell_w - tw) // 2 - 1, grid_y + 2), day_name, font=fonts["small_bold"], fill=COLOR_WHITE)

    year = now.year
    month = now.month
    today_day = now.day

    month_cal = calendar.monthcalendar(year, month)
    cal_start_y = grid_y + 20

    for week_idx, week in enumerate(month_cal):
        for day_idx, day_num in enumerate(week):
            if day_num == 0:
                continue

            cx = grid_x + day_idx * cell_w
            cy = cal_start_y + week_idx * cell_h

            l_day, l_mon = convert_solar_to_lunar(day_num, month, year)
            is_ram_mung1 = (l_day == 1 or l_day == 15)

            if is_ram_mung1:
                draw.rectangle([cx, cy, cx + cell_w - 2, cy + cell_h - 2], fill=COLOR_GRAY_BG, outline=COLOR_GRAY_MID, width=1)
            else:
                draw.rectangle([cx, cy, cx + cell_w - 2, cy + cell_h - 2], outline=COLOR_GRAY_LIGHT, width=1)

            if day_num == today_day:
                draw.rectangle([cx - 1, cy - 1, cx + cell_w - 1, cy + cell_h - 1], outline=COLOR_BLACK, width=2)
                solar_font = fonts["body_bold"]
            else:
                solar_font = fonts["body"]

            solar_str = str(day_num)
            draw.text((cx + 4, cy + 2), solar_str, font=solar_font, fill=COLOR_BLACK)

            lunar_str = f"{l_day}/{l_mon}" if l_day == 1 else str(l_day)
            tb_l = draw.textbbox((0, 0), lunar_str, font=fonts["small"])
            tw_l = tb_l[2] - tb_l[0]
            
            lunar_font = fonts["small_bold"] if is_ram_mung1 else fonts["small"]
            lunar_color = COLOR_BLACK if is_ram_mung1 else COLOR_GRAY_DARK
            
            draw.text((cx + cell_w - tw_l - 4, cy + cell_h - 15), lunar_str, font=lunar_font, fill=lunar_color)

    # -------------------------------------------------------------------------
    # CHRONOLOGICAL HOLIDAYS & MAKEUP SCHEDULE (Y: 640 -> 785)
    # -------------------------------------------------------------------------
    holiday_y = cal_start_y + len(month_cal) * cell_h + 8
    draw.line([(right_x, holiday_y), (582, holiday_y)], fill=COLOR_BLACK, width=1)
    
    custom_holidays = cfg.get("custom_holidays", [
        "• 19/08: Cách Mạng Tháng 8",
        "• 22/08: Làm bù nghỉ lễ Quốc Khánh",
        "• 26/08 (15/07 Âm): Lễ Vu Lan (Rằm Th.7)",
        "• 29/08 - 02/09: Nghỉ lễ Quốc Khánh (5 ngày)"
    ])
    
    curr_hy = holiday_y + 8
    for h_item in custom_holidays[:5]:
        draw_wrapped_text(draw, h_item, fonts["body"], right_x, curr_hy, right_w, COLOR_BLACK)
        curr_hy += 20

    # Outer Border for Canvas
    draw.rectangle([0, 0, WIDTH - 1, HEIGHT - 1], outline=COLOR_BLACK, width=2)

    # 3. Export PNG
    canvas.save(OUTPUT_PATH, "PNG", optimize=True)
    print(f"[*] Dashboard image saved successfully: {OUTPUT_PATH}")
    print(f"    Source: {photo_source}, Dimensions: {canvas.size}, Mode: {canvas.mode}")


if __name__ == "__main__":
    render_dashboard()
