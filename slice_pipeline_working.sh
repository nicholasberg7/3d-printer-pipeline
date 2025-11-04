#!/bin/bash
# Bambu Studio AI Pipeline Automation Script - WORKING VERSION
# Uses Bambu Studio instead of OrcaSlicer to avoid segfaults

set -euo pipefail
IFS=$'\n\t'

# ========== CONFIGURATION ==========
# Directory paths
INPUT_DIR="$HOME/AI_PIPELINE/LOCKED_SPLIT_STAGE"
OUTPUT_DIR="$HOME/AI_PIPELINE/SLICED_OUTPUT"
LOG_DIR="$HOME/AI_PIPELINE/logs"
LOCK_FILE="/tmp/slice_pipeline.lock"

# Bambu Studio binary path (WORKS BETTER THAN ORCASLICER)
SLICER="/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
PROFILES_DIR="/Applications/BambuStudio.app/Contents/Resources/profiles/BBL"

# Printer settings
PRINTER_IP="192.168.1.129"
PRINTER_ACCESS_CODE="30551719"
PRINTER_SERIAL="01P09A3A1800831"

# ========== SETUP ==========
# Create necessary directories
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

# Function to slice a file
slice_file() {
    local input_file="$1"
    local filename=$(basename "$input_file" .stl)
    local output_gcode="$OUTPUT_DIR/${filename}.gcode"
    
    log "Starting slice for: $filename"
    
    # Use Bambu Studio CLI (no segfault issues!)
    if "$SLICER" \
        --slice 0 \
        --outputdir "$OUTPUT_DIR" \
        "$input_file" 2>&1 | tee "$LOG_DIR/${filename}_slice.log"; then
        
        # The G-code will be saved as plate_1.gcode, rename it
        if [ -f "$OUTPUT_DIR/plate_1.gcode" ]; then
            mv "$OUTPUT_DIR/plate_1.gcode" "$output_gcode"
            log "✓ Sliced successfully: $output_gcode"
            return 0
        else
            log "✗ G-code file not found after slicing: plate_1.gcode"
            return 1
        fi
    else
        log "✗ Slicing command failed for $filename"
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
        --connect-timeout 30; then
        
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
    
    if slice_file "$file"; then
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
    log "=== Starting Bambu Studio AI Pipeline ==="
    log "Input Directory: $INPUT_DIR"
    log "Output Directory: $OUTPUT_DIR"
    log "Log File: $LOG_FILE"
    log ""
    
    # Check if another instance is running
    if [ -e "$LOCK_FILE" ]; then
        log "ERROR: Another instance is already running (lock file exists)"
        log "If you're sure no other instance is running, remove: $LOCK_FILE"
        exit 1
    fi
    touch "$LOCK_FILE"
    
    # Set upload flag if specified
    export UPLOAD=0
    if [[ "$*" == *"--upload"* ]]; then
        UPLOAD=1
        log "Auto-upload to printer: ENABLED"
    else
        log "Auto-upload to printer: DISABLED"
    fi
    
    # Check if watch mode is requested
    if [[ "$*" == *"--watch"* ]]; then
        log "Running in WATCH mode - monitoring for new files..."
        monitor_directory
    else
        log "Running in BATCH mode - processing existing files only..."
        
        # Process all existing STL files once
        for stl_file in "$INPUT_DIR"/*.stl; do
            [ -e "$stl_file" ] && process_file "$stl_file" || true
        done
        
        log "=== Pipeline Complete ==="
    fi
}

# Run the pipeline
main "$@"
