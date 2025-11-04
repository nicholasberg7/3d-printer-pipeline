#!/bin/bash
# OrcaSlicer GUI Automation Pipeline - WORKING SOLUTION
# Uses AppleScript to automate the GUI since CLI segfaults

set -euo pipefail
IFS=$'\n\t'

# ========== CONFIGURATION ==========
# Directory paths
INPUT_DIR="$HOME/AI_PIPELINE/LOCKED_SPLIT_STAGE"
OUTPUT_DIR="$HOME/AI_PIPELINE/SLICED_OUTPUT"
LOG_DIR="$HOME/AI_PIPELINE/logs"
LOCK_FILE="/tmp/slice_pipeline.lock"

# Printer settings
PRINTER_IP="192.168.1.129"
PRINTER_ACCESS_CODE="30551719"

# ========== SETUP ==========
mkdir -p "$OUTPUT_DIR" "$LOG_DIR"

# Setup logging
LOG_FILE="$LOG_DIR/pipeline_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$LOG_FILE") 2>&1

# ========== HELPER FUNCTIONS ==========
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

cleanup() {
    log "Cleaning up..."
    rm -f "$LOCK_FILE"
    log "Pipeline stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Function to slice using GUI automation
slice_with_gui() {
    local input_file="$1"
    local filename=$(basename "$input_file" .stl)
    local output_gcode="$OUTPUT_DIR/${filename}.gcode"
    
    log "Starting GUI automation for: $filename"
    
    # Create temporary AppleScript for automation
    local script="/tmp/orcaslicer_auto_$$.scpt"
    
    cat > "$script" <<EOF
-- OrcaSlicer GUI Automation Script
tell application "OrcaSlicer"
    activate
    delay 2
end tell

-- Give OrcaSlicer time to launch
delay 3

-- Open the STL file
tell application "OrcaSlicer"
    open POSIX file "$input_file"
end tell

-- Wait for file to load
delay 5

-- Use System Events for UI automation
tell application "System Events"
    tell process "OrcaSlicer"
        -- Click "Slice Plate" button
        try
            click button "Slice Plate" of window 1
            delay 10
            
            -- Export G-code
            keystroke "g" using {command down, shift down}
            delay 2
            
            -- Set filename in save dialog
            keystroke "$output_gcode"
            delay 1
            
            -- Press Enter to save
            keystroke return
            delay 2
            
            -- Close the file
            keystroke "w" using {command down}
            delay 1
            
        on error errMsg
            log "Error during automation: " & errMsg
        end try
    end tell
end tell

-- Quit OrcaSlicer
tell application "OrcaSlicer"
    quit
end tell
EOF
    
    # Run the AppleScript
    if osascript "$script" 2>&1 | tee "$LOG_DIR/${filename}_gui.log"; then
        rm -f "$script"
        
        # Wait a moment for file to be written
        sleep 2
        
        if [ -f "$output_gcode" ]; then
            log "✓ Sliced successfully: $output_gcode"
            return 0
        else
            log "✗ G-code file not found: $output_gcode"
            log "Note: GUI automation may require manual intervention"
            return 1
        fi
    else
        rm -f "$script"
        log "✗ GUI automation failed for $filename"
        return 1
    fi
}

# Simplified slice function - just open in GUI
slice_file_manual() {
    local input_file="$1"
    local filename=$(basename "$input_file" .stl)
    
    log "Opening $filename in OrcaSlicer GUI for manual slicing..."
    log "Please slice and export to: $OUTPUT_DIR/${filename}.gcode"
    
    open -a OrcaSlicer "$input_file"
    
    log "Waiting for manual slicing..."
    log "Press ENTER when you've exported the G-code..."
    read -r
    
    if [ -f "$OUTPUT_DIR/${filename}.gcode" ]; then
        log "✓ G-code found: ${filename}.gcode"
        return 0
    else
        log "✗ G-code not found"
        return 1
    fi
}

# Function to upload to printer via FTP
upload_to_printer() {
    local gcode_file="$1"
    local filename=$(basename "$gcode_file")
    
    log "Uploading to P1P: $filename"
    
    if curl -k --ftp-ssl \
        --user "bblp:$PRINTER_ACCESS_CODE" \
        -T "$gcode_file" \
        "ftps://$PRINTER_IP:990/$filename" \
        --max-time 300 \
        --connect-timeout 30 2>&1; then
        
        log "✓ Uploaded successfully to P1P"
        return 0
    else
        log "✗ Upload failed"
        return 1
    fi
}

# Function to process a single file
process_file() {
    local file="$1"
    local filename=$(basename "$file")
    
    # Skip if not an STL file
    [[ "$file" != *.stl ]] && return 0
    
    # Skip if already being processed
    [[ -f "${file}.processing" ]] && return 0
    
    # Mark as processing
    touch "${file}.processing"
    
    log "Processing file: $filename"
    
    # Choose automation method
    if [[ "${AUTO_MODE:-manual}" == "auto" ]]; then
        slice_result=$(slice_with_gui "$file")
    else
        slice_result=$(slice_file_manual "$file")
    fi
    
    if [ $? -eq 0 ]; then
        local gcode_file="$OUTPUT_DIR/$(basename "$file" .stl).gcode"
        
        if [ -f "$gcode_file" ]; then
            # Upload if flag is set
            if [ "${UPLOAD:-0}" -eq 1 ]; then
                upload_to_printer "$gcode_file" || log "Upload failed, but file is sliced"
            fi
            
            # Mark as processed
            mv "$file" "${file}.processed"
            log "✓ Completed processing: $filename"
        fi
    else
        # Mark as failed
        mv "$file" "${file}.failed"
        log "✗ Failed to process: $filename"
    fi
    
    rm -f "${file}.processing"
}

# Function to monitor directory for new files
monitor_directory() {
    log "Starting directory monitor for: $INPUT_DIR"
    log "Watching for *.stl files..."
    
    # Initial processing of any existing files
    for file in "$INPUT_DIR"/*.stl; do
        [ -e "$file" ] && process_file "$file" || true
    done
    
    log "Initial processing complete. Monitoring for new files..."
    
    # Watch for new files using fswatch (macOS)
    fswatch -0 -r -e ".*" -i "\\.stl$" "$INPUT_DIR" | while read -d "" file
    do
        log "Detected new file: $(basename "$file")"
        process_file "$file"
    done
}

# Main pipeline
main() {
    log "=== OrcaSlicer GUI Automation Pipeline ==="
    log "Input Directory: $INPUT_DIR"
    log "Output Directory: $OUTPUT_DIR"
    log "Log File: $LOG_FILE"
    log ""
    log "⚠️  NOTE: This pipeline uses GUI automation"
    log "   CLI slicing doesn't work due to segfaults"
    log ""
    
    # Check if another instance is running
    if [ -e "$LOCK_FILE" ]; then
        log "ERROR: Another instance is already running"
        exit 1
    fi
    touch "$LOCK_FILE"
    
    # Set upload flag
    export UPLOAD=0
    [[ "$*" == *"--upload"* ]] && UPLOAD=1 && log "Auto-upload: ENABLED"
    
    # Set automation mode
    export AUTO_MODE="manual"
    [[ "$*" == *"--auto"* ]] && AUTO_MODE="auto" && log "Automation: FULL AUTO (experimental)"
    
    # Check for watch mode
    if [[ "$*" == *"--watch"* ]]; then
        log "Running in WATCH mode..."
        monitor_directory
    else
        log "Running in BATCH mode..."
        
        for stl_file in "$INPUT_DIR"/*.stl; do
            [ -e "$stl_file" ] && process_file "$stl_file" || true
        done
        
        log "=== Pipeline Complete ==="
    fi
}

# Run the pipeline
main "$@"
