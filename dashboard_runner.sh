#!/bin/sh
# ==============================================================================
# Kindle Touch 4th Gen (D01200) Smart Dashboard Shell Runner Script
# Architecture based on pascalw/kindle-dash & MobileRead E-ink standards
# Location: /mnt/us/dashboard/dashboard_runner.sh
# ==============================================================================

GITHUB_USER="duyanhk1000-dot"
GITHUB_REPO="kindle-dashboard"

# Direct Plain HTTP Image Proxy (Port 80, Status 200, No HTTPS Redirect, 100% BusyBox v1.17.1 Compatible)
HTTP_PROXY_URL="http://images.weserv.nl/?url=raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/main/dashboard.png"
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

# Step 0: Disable native Kindle screensaver daemon from overwriting dashboard (pascalw technique)
lipc-set-prop com.lab126.powerd preventScreenSaver 1 >/dev/null 2>&1

download_image() {
    rm -f "$TMP_IMAGE"
    
    # Method 1: Plain HTTP Proxy via weserv.nl (Uses ONLY standard BusyBox v1.17.1 options: -q -U -O)
    log "Attempting download via Plain HTTP Proxy (weserv.nl)..."
    WGET_OUT=$(wget -q -U "Mozilla/5.0" -O "$TMP_IMAGE" "$HTTP_PROXY_URL" 2>&1)
    WGET_RET=$?
    if [ $WGET_RET -eq 0 ] && [ -s "$TMP_IMAGE" ]; then
        log "[✓] Downloaded successfully via HTTP Proxy ($(wc -c < "$TMP_IMAGE") bytes)."
        return 0
    else
        log "[!] Plain HTTP Proxy failed (exit $WGET_RET): $WGET_OUT"
    fi

    # Method 2: Fallback to wsrv.nl HTTP Proxy
    log "Attempting download via fallback HTTP Proxy (wsrv.nl)..."
    WGET_OUT_ALT=$(wget -q -U "Mozilla/5.0" -O "$TMP_IMAGE" "http://wsrv.nl/?url=raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/main/dashboard.png" 2>&1)
    WGET_RET_ALT=$?
    if [ $WGET_RET_ALT -eq 0 ] && [ -s "$TMP_IMAGE" ]; then
        log "[✓] Downloaded successfully via wsrv.nl Proxy ($(wc -c < "$TMP_IMAGE") bytes)."
        return 0
    fi
    
    # Method 3: curl if available on Kindle
    if command -v curl >/dev/null 2>&1; then
        log "Attempting download via curl..."
        CURL_OUT=$(curl -s -k -L -m 15 -o "$TMP_IMAGE" "$HTTPS_IMAGE_URL" 2>&1)
        CURL_RET=$?
        if [ $CURL_RET -eq 0 ] && [ -s "$TMP_IMAGE" ]; then
            log "[✓] Downloaded successfully via curl ($(wc -c < "$TMP_IMAGE") bytes)."
            return 0
        else
            log "[!] curl failed (exit $CURL_RET): $CURL_OUT"
        fi
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

if [ $CONNECTED -eq 0 ]; then
    log "[!] Wi-Fi cmState did not reach CONNECTED within 25 seconds. Attempting download anyway..."
fi

# Extra 2-second sleep to ensure DNS resolution & DHCP IP routing table ready
sleep 2

# Step 3: Fetch dashboard image
if download_image; then
    status_msg "Rendering Dashboard Image..."
    # Full screen refresh via eips -f -g (pascalw technique to clear ghosting)
    eips -c >/dev/null 2>&1
    sleep 1
    eips -f -g "$TMP_IMAGE" >/dev/null 2>&1
    log "[✓] Framebuffer updated successfully via eips -f -g."
else
    status_msg "Error: Download failed. Check Wi-Fi."
    log "[!] Download failed across all CDN/HTTP/HTTPS endpoints."
fi

# Step 4: Turn OFF Wi-Fi to preserve battery
lipc-set-prop com.lab126.wifid enable 0 >/dev/null 2>&1
lipc-set-prop com.lab126.cmd wirelessEnable 0 >/dev/null 2>&1
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
