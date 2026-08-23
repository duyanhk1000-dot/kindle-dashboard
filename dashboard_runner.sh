#!/bin/sh
# ==============================================================================
# Kindle Touch 4th Gen (D01200) Smart Dashboard Shell Runner Script
# Architecture based on pascalw/kindle-dash & MobileRead E-ink standards
# Location: /mnt/us/dashboard/dashboard_runner.sh
# Target Schedule:
#   - 00:00 ICT (Midnight date & Hanzi change)
#   - 15:30 ICT (Stock market closing session update)
# ==============================================================================

GITHUB_USER="duyanhk1000-dot"
GITHUB_REPO="kindle-dashboard"

# URLs: Direct GitHub Raw HTTPS & HTTP fallback
HTTPS_IMAGE_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/main/dashboard.png"
HTTP_IMAGE_URL="http://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/main/dashboard.png"

TMP_IMAGE="/tmp/dashboard.png"
LOG_FILE="/mnt/us/dashboard/dashboard.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

status_msg() {
    log "$1"
    eips 0 0 "$1                                   " >/dev/null 2>&1
}

# Calculate seconds until next target wakeup time (15:35 or 00:05 ICT)
calc_next_wakeup() {
    CURR_H=$(date +%H | sed 's/^0//')
    CURR_M=$(date +%M | sed 's/^0//')
    [ -z "$CURR_H" ] && CURR_H=0
    [ -z "$CURR_M" ] && CURR_M=0
    
    NOW_MIN=$((CURR_H * 60 + CURR_M))
    
    TARGET_1530=930   # 15:30 in minutes from 00:00
    TARGET_0000=1440  # 00:00 (Midnight) in minutes
    
    if [ $NOW_MIN -lt $TARGET_1530 ]; then
        SLEEP_MIN=$((TARGET_1530 - NOW_MIN))
    else
        SLEEP_MIN=$((TARGET_0000 - NOW_MIN))
    fi
    
    # Add 5 minutes buffer (300 seconds) so GitHub Actions finishes rendering first
    SLEEP_SEC=$((SLEEP_MIN * 60 + 300))
    if [ $SLEEP_SEC -lt 1800 ]; then
        SLEEP_SEC=1800
    fi
    echo $SLEEP_SEC
}

# Step 0: Disable native Kindle screensaver daemon from overwriting dashboard (pascalw technique)
lipc-set-prop com.lab126.powerd preventScreenSaver 1 >/dev/null 2>&1

download_image() {
    rm -f "$TMP_IMAGE"
    
    # Method 1: curl with -k -L (Standard method for Jailbroken Kindles, 100% handles HTTPS & redirects)
    if command -v curl >/dev/null 2>&1 || [ -x /usr/bin/curl ]; then
        log "Attempting download via curl..."
        curl -s -k -L -m 20 -o "$TMP_IMAGE" "$HTTPS_IMAGE_URL"
        SIZE=$(wc -c < "$TMP_IMAGE" 2>/dev/null || echo 0)
        if [ "$SIZE" -gt 20000 ]; then
            log "[✓] Downloaded valid PNG via curl ($SIZE bytes)."
            return 0
        else
            log "[!] curl output invalid size ($SIZE bytes)."
        fi
    fi

    # Method 2: wget fallback
    log "Attempting download via wget..."
    wget -q -U "Mozilla/5.0" -O "$TMP_IMAGE" "$HTTP_IMAGE_URL" 2>&1
    SIZE=$(wc -c < "$TMP_IMAGE" 2>/dev/null || echo 0)
    if [ "$SIZE" -gt 20000 ]; then
        log "[✓] Downloaded valid PNG via wget ($SIZE bytes)."
        return 0
    else
        log "[!] wget output invalid size ($SIZE bytes)."
    fi

    return 1
}

status_msg "Updating Dashboard from GitHub..."

# Step 1: Enable Wi-Fi via Kindle LIPC daemons
lipc-set-prop com.lab126.wifid enable 1 >/dev/null 2>&1
lipc-set-prop com.lab126.cmd wirelessEnable 1 >/dev/null 2>&1
lipc-set-prop com.lab126.cmd wlanEnable 1 >/dev/null 2>&1

# Step 2: Wait for Wi-Fi LIPC cmState to reach CONNECTED
log "Waiting for Wi-Fi connection (LIPC cmState)..."
RETRY=0
CONNECTED=0
while [ $RETRY -lt 25 ]; do
    CM_STATE=$(lipc-get-prop com.lab126.wifid cmState 2>/dev/null)
    if [ "$CM_STATE" = "CONNECTED" ]; then
        CONNECTED=1
        log "[✓] Wi-Fi LIPC cmState: CONNECTED"
        break
    fi
    RETRY=$((RETRY + 1))
    sleep 1
done

# Extra 2-second sleep to ensure DNS resolution ready
sleep 2

# Step 3: Fetch dashboard image
if download_image; then
    status_msg "Rendering Dashboard Image..."
    # Clear screen and status bar
    eips -c >/dev/null 2>&1
    sleep 1
    # Full screen refresh via eips -f -g
    eips -f -g "$TMP_IMAGE" >/dev/null 2>&1
    log "[✓] Framebuffer updated successfully via eips -f -g."
else
    status_msg "Error: Download failed. Check Wi-Fi."
    log "[!] Download failed: Invalid image size."
fi

# Step 4: Turn OFF Wi-Fi to preserve battery
lipc-set-prop com.lab126.wifid enable 0 >/dev/null 2>&1
lipc-set-prop com.lab126.cmd wirelessEnable 0 >/dev/null 2>&1
lipc-set-prop com.lab126.cmd wlanEnable 0 >/dev/null 2>&1

# Step 5: Enter RTC sleep loop only if daemon mode is specified
if [ "$1" = "daemon" ]; then
    SLEEP_SECONDS=$(calc_next_wakeup)
    log "Scheduling Next Smart Wakeup in $SLEEP_SECONDS seconds..."
    if [ -c /dev/rtc1 ]; then
        rtcwake -d /dev/rtc1 -m mem -s "$SLEEP_SECONDS"
    else
        rtcwake -d /dev/rtc0 -m mem -s "$SLEEP_SECONDS"
    fi
fi
