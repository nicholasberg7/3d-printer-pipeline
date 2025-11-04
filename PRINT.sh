#!/bin/bash
# 🖨️ SUPER SIMPLE PRINT WORKFLOW
# Just run this and click 2 buttons in OrcaSlicer!

set -e

# Colors for pretty output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

INPUT_DIR="$HOME/AI_PIPELINE/LOCKED_SPLIT_STAGE"
OUTPUT_DIR="$HOME/AI_PIPELINE/SLICED_OUTPUT"
PRINTER_IP="192.168.1.178"  # P1P with AMS
PRINTER_CODE="18835558"      # P1P Access Code

# Create directories
mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}    🖨️  3D PRINTING PIPELINE - EASY MODE 🖨️${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Count STL files
STL_COUNT=$(ls -1 "$INPUT_DIR"/*.stl 2>/dev/null | wc -l | xargs)

if [ "$STL_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No STL files found!${NC}"
    echo ""
    echo "Add STL files to: $INPUT_DIR"
    echo ""
    echo "Example:"
    echo "  cp your_model.stl $INPUT_DIR/"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Found $STL_COUNT file(s) to process${NC}"
echo ""

# Process each file
for STL_FILE in "$INPUT_DIR"/*.stl; do
    [ -f "$STL_FILE" ] || continue
    
    FILENAME=$(basename "$STL_FILE")
    BASE="${FILENAME%.stl}"
    GCODE="$OUTPUT_DIR/${BASE}.gcode"
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}📄 Processing: $FILENAME${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Open OrcaSlicer
    echo -e "${BLUE}🎨 Opening OrcaSlicer...${NC}"
    open -a OrcaSlicer "$STL_FILE"
    sleep 3
    
    echo ""
    echo -e "${YELLOW}┌─────────────────────────────────────────────┐${NC}"
    echo -e "${YELLOW}│  🎯 YOUR TURN - JUST 2 CLICKS!             │${NC}"
    echo -e "${YELLOW}│                                             │${NC}"
    echo -e "${YELLOW}│  1️⃣  Click 'Slice Plate'                   │${NC}"
    echo -e "${YELLOW}│  2️⃣  Export G-code to:                      │${NC}"
    echo -e "${YELLOW}│     $OUTPUT_DIR/${NC}"
    echo -e "${YELLOW}│     Filename: ${BASE}.gcode ${NC}"
    echo -e "${YELLOW}│                                             │${NC}"
    echo -e "${YELLOW}│  Then press ENTER here...                  │${NC}"
    echo -e "${YELLOW}└─────────────────────────────────────────────┘${NC}"
    echo ""
    
    # Wait for user
    read -p "Press ENTER when you've exported the G-code... " 
    
    # Check if G-code exists
    if [ -f "$GCODE" ]; then
        echo ""
        echo -e "${GREEN}✅ G-code found!${NC}"
        
        # Ask about upload
        echo ""
        read -p "Upload to printer at $PRINTER_IP? (y/n): " UPLOAD
        
        if [[ "$UPLOAD" =~ ^[Yy]$ ]]; then
            echo ""
            echo -e "${BLUE}📤 Uploading to printer...${NC}"
            
            if curl -k --ftp-ssl \
                --user "bblp:$PRINTER_CODE" \
                -T "$GCODE" \
                "ftps://$PRINTER_IP:990/$(basename "$GCODE")" \
                --max-time 300 --connect-timeout 30 2>/dev/null; then
                
                echo -e "${GREEN}✅ Uploaded successfully!${NC}"
                echo -e "${GREEN}🎉 Your print should start soon!${NC}"
            else
                echo -e "${RED}❌ Upload failed${NC}"
                echo "G-code saved locally at: $GCODE"
            fi
        else
            echo -e "${BLUE}ℹ️  Skipped upload. G-code saved at:${NC}"
            echo "   $GCODE"
        fi
        
        # Mark as processed
        mv "$STL_FILE" "${STL_FILE}.processed"
        
    else
        echo ""
        echo -e "${RED}❌ G-code not found!${NC}"
        echo "Expected: $GCODE"
        echo ""
        read -p "Try again? (y/n): " RETRY
        
        if [[ ! "$RETRY" =~ ^[Yy]$ ]]; then
            mv "$STL_FILE" "${STL_FILE}.failed"
            echo -e "${RED}Marked as failed. Moving on...${NC}"
        fi
    fi
    
    echo ""
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ ALL DONE!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""
echo "Processed files moved to: *.stl.processed"
echo "Output G-codes in: $OUTPUT_DIR"
echo ""
