#!/bin/bash
# Bambu Studio AI Pipeline Automation Script
# This uses Bambu Studio instead of OrcaSlicer to avoid the CLI validation bug

set -e

# Configuration
INPUT_DIR="$HOME/AI_PIPELINE/LOCKED_SPLIT_STAGE"
OUTPUT_DIR="$HOME/AI_PIPELINE/SLICED_OUTPUT"
BAMBU_APP="/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"

# Printer settings
PRINTER_IP="192.168.1.129"
PRINTER_ACCESS_CODE="30551719"
PRINTER_SERIAL="01P09A3A1800831"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Function to slice a file with Bambu Studio
slice_file() {
    local input_file="$1"
    local filename=$(basename "$input_file" .stl)
    local output_gcode="$OUTPUT_DIR/${filename}.gcode"
    
    echo "Slicing with Bambu Studio: $filename"
    
    # Bambu Studio CLI - adjust profile paths as needed
    "$BAMBU_APP" \
        --slice 0 \
        --outputdir "$OUTPUT_DIR" \
        "$input_file"
    
    # Check if G-code was created
    if [ -f "$OUTPUT_DIR/plate_1.gcode" ]; then
        mv "$OUTPUT_DIR/plate_1.gcode" "$output_gcode"
        echo "✓ Sliced successfully: $output_gcode"
        return 0
    else
        echo "✗ Slicing failed for $filename"
        return 1
    fi
}

# Function to upload to printer via FTP
upload_to_printer() {
    local gcode_file="$1"
    local filename=$(basename "$gcode_file")
    
    echo "Uploading to P1P: $filename"
    
    curl -k --ftp-ssl \
        --user "bblp:$PRINTER_ACCESS_CODE" \
        -T "$gcode_file" \
        "ftps://$PRINTER_IP:990/$filename" \
        --max-time 300 \
        --progress-bar
    
    if [ $? -eq 0 ]; then
        echo "✓ Uploaded successfully to P1P"
        return 0
    else
        echo "✗ Upload failed"
        return 1
    fi
}

# Main pipeline
main() {
    echo "=== Bambu Studio AI Pipeline ==="
    echo "Input: $INPUT_DIR"
    echo "Output: $OUTPUT_DIR"
    echo ""
    
    # Check if Bambu Studio exists
    if [ ! -f "$BAMBU_APP" ]; then
        echo "Error: Bambu Studio not found at $BAMBU_APP"
        echo "Please install Bambu Studio or update the path"
        exit 1
    fi
    
    # Process all STL files
    for stl_file in "$INPUT_DIR"/*.stl; do
        if [ -f "$stl_file" ]; then
            echo "Processing: $(basename "$stl_file")"
            
            # Slice the file
            if slice_file "$stl_file"; then
                # Optionally upload to printer
                if [ "$1" == "--upload" ]; then
                    gcode_file="$OUTPUT_DIR/$(basename "$stl_file" .stl).gcode"
                    upload_to_printer "$gcode_file"
                fi
            fi
            
            echo ""
        fi
    done
    
    echo "=== Pipeline Complete ==="
}

# Run the pipeline
main "$@"
