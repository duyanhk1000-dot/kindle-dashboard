#!/bin/sh
# ==============================================================================
# Kindle Touch 4th Gen (D01200) Smart Dashboard Shell Runner Script
# Location: /mnt/us/dashboard/dashboard_runner.sh
# ==============================================================================

# User Configuration: Replace with your actual GitHub Username and Repository name
GITHUB_USER="duyanhk1000-dot"
GITHUB_REPO="kindle-dashboard"
IMAGE_URL="https://raw.githubusercontent.com/${GITHUB_USER}/${GITHUB_REPO}/main/dashboard.png"

# Local temporary output image path
TMP_IMAGE="/tmp/dashboard.png"
LOG_FILE="/mnt/us/dashboard/dashboard.log"

# Refresh interval (seconds) - Default: 12 hours = 43200 seconds
# Morning update: 05:30, Evening update: 17:30
SLEEP_SECONDS=43200

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "=================================================="
log "Starting Kindle Smart Dashboard Runner"
log "=================================================="

# Step 1: Turn ON Wi-Fi
log "Enabling Wi-Fi..."
lipc-set-prop com.lab126.cmd wlanEnable 1

# Step 2: Wait for network connectivity (Up to 30 seconds)
RETRY=0
CONNECTED=0
while [ $RETRY -lt 30 ]; do
    if ping -c 1 raw.githubusercontent.com >/dev/null 2>&1; then
        CONNECTED=1
        log "Wi-Fi Connected successfully."
        break
    fi
    RETRY=$((RETRY + 1))
    sleep 1
done

if [ $CONNECTED -eq 0 ]; then
    log "[!] Warning: Wi-Fi connection timed out. Attempting download anyway..."
fi

# Step 3: Fetch dashboard.png from GitHub static RAW URL
log "Downloading latest dashboard image from GitHub..."
wget --no-check-certificate -q -O "$TMP_IMAGE" "$IMAGE_URL"
DOWNLOAD_STATUS=$?

if [ $DOWNLOAD_STATUS -eq 0 ] && [ -s "$TMP_IMAGE" ]; then
    log "[✓] Image downloaded successfully ($(wc -c < "$TMP_IMAGE") bytes)."
    
    # Step 4: Refresh Kindle E-ink Screen Framebuffer
    # Clear screen first to clear ghosting, then draw grayscale PNG
    eips -c
    sleep 1
    eips -g "$TMP_IMAGE"
    log "[✓] Framebuffer updated via eips."
else
    log "[!] Error: Failed to download dashboard image from GitHub (status: $DOWNLOAD_STATUS)."
fi

# Step 5: Turn OFF Wi-Fi to preserve battery
log "Disabling Wi-Fi to preserve battery..."
lipc-set-prop com.lab126.cmd wlanEnable 0

# Step 6: Enter Deep RTC Sleep (rtcwake)
log "Scheduling RTC Wakeup in $SLEEP_SECONDS seconds..."
log "Going into deep sleep..."

# Execute RTC wake for low-power sleep
# /dev/rtc1 is standard Kindle Real Time Clock interface
if [ -c /dev/rtc1 ]; then
    rtcwake -d /dev/rtc1 -m mem -s "$SLEEP_SECONDS"
else
    log "[!] /dev/rtc1 not found. Using rtc0 fallback."
    rtcwake -d /dev/rtc0 -m mem -s "$SLEEP_SECONDS"
fi

log "Kindle woke up from RTC sleep."
