#!/bin/sh
# ==============================================================================
# Kindle Touch 4th Gen (D01200) Smart Dashboard Shell Runner Script
# Location: /mnt/us/dashboard/dashboard_runner.sh
# ==============================================================================

GITHUB_USER="duyanhk1000-dot"
GITHUB_REPO="kindle-dashboard"

# URLs: Plain HTTP via jsDelivr CDN (Bypasses TLS 1.2/1.3 handshake issues on old Kindle OS)
HTTP_IMAGE_URL="http://cdn.jsdelivr.net/gh/${GITHUB_USER}/${GITHUB_REPO}@main/dashboard.png"
HTTPS_IMAGE_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/main/dashboard.png"

TMP_IMAGE="/tmp/dashboard.png"
LOG_FILE="/mnt/us/dashboard/dashboard.log"
SLEEP_SECONDS=43200

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Print visual status feedback at top of Kindle E-ink screen
status_msg() {
    log "$1"
    eips 0 0 "$1                                   " >/dev/null 2>&1
}

download_image() {
    rm -f "$TMP_IMAGE"
    
    # Method 1: jsDelivr Plain HTTP (Bypasses old Kindle OpenSSL/TLS 1.3 handshake error)
    log "Attempting download via jsDelivr HTTP CDN..."
    wget -T 15 -t 2 -q -O "$TMP_IMAGE" "$HTTP_IMAGE_URL"
    if [ $? -eq 0 ] && [ -s "$TMP_IMAGE" ]; then
        log "[✓] Downloaded successfully via HTTP CDN."
        return 0
    fi
    
    # Method 2: curl if available
    if command -v curl >/dev/null 2>&1; then
        log "Attempting download via curl..."
        curl -s -k -m 15 -o "$TMP_IMAGE" "$HTTPS_IMAGE_URL"
        if [ $? -eq 0 ] && [ -s "$TMP_IMAGE" ]; then
            log "[✓] Downloaded successfully via curl."
            return 0
        fi
    fi

    # Method 3: Direct wget HTTPS fallback
    log "Attempting download via direct HTTPS wget..."
    wget -T 15 -t 2 --no-check-certificate -q -O "$TMP_IMAGE" "$HTTPS_IMAGE_URL"
    if [ $? -eq 0 ] && [ -s "$TMP_IMAGE" ]; then
        log "[✓] Downloaded successfully via HTTPS wget."
        return 0
    fi

    return 1
}

status_msg "Updating Dashboard from GitHub..."

# Step 1: Enable Wi-Fi
lipc-set-prop com.lab126.cmd wlanEnable 1 >/dev/null 2>&1

# Step 2: Wait for Wi-Fi network connectivity (Up to 15 seconds)
RETRY=0
CONNECTED=0
while [ $RETRY -lt 15 ]; do
    if ping -c 1 8.8.8.8 >/dev/null 2>&1 || ping -c 1 cdn.jsdelivr.net >/dev/null 2>&1; then
        CONNECTED=1
        log "Wi-Fi Connected successfully."
        break
    fi
    RETRY=$((RETRY + 1))
    sleep 1
done

# Step 3: Fetch dashboard image
if download_image; then
    status_msg "Rendering Dashboard Image..."
    eips -c >/dev/null 2>&1
    sleep 1
    eips -g "$TMP_IMAGE" >/dev/null 2>&1
    log "[✓] Framebuffer updated successfully via eips."
else
    status_msg "Error: Download failed. Check Wi-Fi."
    log "[!] Download failed across all CDN/HTTP/HTTPS endpoints."
fi

# Step 4: Turn OFF Wi-Fi to preserve battery
lipc-set-prop com.lab126.cmd wlanEnable 0 >/dev/null 2>&1

# Step 5: Enter RTC sleep loop only if daemon mode is specified
if [ "$1" = "daemon" ]; then
    log "Scheduling RTC Wakeup in $SLEEP_SECONDS seconds..."
    if [ -c /dev/rtc1 ]; then
        rtcwake -d /dev/rtc1 -m mem -s "$SLEEP_SECONDS"
    else
        rtcwake -d /dev/rtc0 -m mem -s "$SLEEP_SECONDS"
    fi
fi
