#!/bin/bash
# OrcaSlicer AI Pipeline Automation Script

set -e

# Configuration
INPUT_DIR="$HOME/AI_PIPELINE/LOCKED_SPLIT_STAGE"
OUTPUT_DIR="$HOME/AI_PIPELINE/SLICED_OUTPUT"
PROFILES_DIR="$HOME/Documents/OrcaSlicer/resources/profiles/BBL"
ORCA_CUSTOM="$HOME/Documents/OrcaSlicer/build/arm64/src/OrcaSlicer.app/Contents/MacOS/OrcaSlicer"

# Printer settings
PRINTER_IP="192.168.1.129"
PRINTER_ACCESS_CODE="30551719"
PRINTER_SERIAL="01P09A3A1800831"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Function to slice a file
slice_file() {
    local input_file="$1"
    local filename=$(basename "$input_file" .stl)
    local output_gcode="$OUTPUT_DIR/${filename}.gcode"
    
    echo "Slicing: $filename"
    
    # Use CUSTOM OrcaSlicer CLI with validation fix!
    "$ORCA_CUSTOM" \
        --load-settings "$PROFILES_DIR/machine/Bambu Lab P1P 0.4 nozzle.json;$PROFILES_DIR/process/0.20mm Standard @BBL P1P.json" \
        --load-filaments "$PROFILES_DIR/filament/Bambu PLA Dynamic @BBL P1P.json" \
        --slice 0 \
        --outputdir "$OUTPUT_DIR" \
        "$input_file"
    
    # The G-code will be saved as plate_1.gcode, rename it
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
        --max-time 300
    
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
    echo "=== OrcaSlicer AI Pipeline ==="
    echo "Input: $INPUT_DIR"
    echo "Output: $OUTPUT_DIR"
    echo ""
    
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
