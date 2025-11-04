#!/bin/bash
# 🖨️ SAFE 3D PRINTING WORKFLOW
# This version includes validation to prevent printer damage

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

INPUT_DIR="$HOME/AI_PIPELINE/LOCKED_SPLIT_STAGE"
OUTPUT_DIR="$HOME/AI_PIPELINE/SLICED_OUTPUT"
PRINTER_IP="192.168.1.178"  # P1P with AMS
PRINTER_CODE="18835558"      # P1P Access Code

mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"

echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}    🖨️  SAFE 3D PRINTING PIPELINE 🖨️${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo ""

# Count STL files
STL_COUNT=$(ls -1 "$INPUT_DIR"/*.stl 2>/dev/null | wc -l | xargs)

if [ "$STL_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No STL files found!${NC}"
    echo "Add STL files to: $INPUT_DIR"
    exit 1
fi

echo -e "${GREEN}✅ Found $STL_COUNT file(s) to process${NC}"
echo ""

# Safety warning
echo -e "${YELLOW}════════════════════ SAFETY CHECK ════════════════════${NC}"
echo -e "${YELLOW}Before we start, you MUST verify OrcaSlicer settings!${NC}"
echo ""
echo -e "${RED}⚠️  CRITICAL: Wrong settings can damage your printer!${NC}"
echo ""
echo -e "${YELLOW}Please confirm in OrcaSlicer:${NC}"
echo ""
echo -e "  ${BLUE}1.${NC} Printer: ${GREEN}Bambu Lab P1P 0.4 nozzle${NC}"
echo -e "  ${BLUE}2.${NC} Bed Size: ${GREEN}256mm x 256mm${NC}"
echo -e "  ${BLUE}3.${NC} Process: ${GREEN}Something with '@BBL P1P' in the name${NC}"
echo ""
echo -e "${YELLOW}══════════════════════════════════════════════════════${NC}"
echo ""
read -p "Have you verified these settings in OrcaSlicer? (yes/no): " VERIFIED

if [[ ! "$VERIFIED" =~ ^[Yy](es)?$ ]]; then
    echo ""
    echo -e "${RED}❌ Setup not verified. Stopping for safety.${NC}"
    echo ""
    echo -e "${YELLOW}To verify settings:${NC}"
    echo "  1. Open OrcaSlicer"
    echo "  2. Click 'Device' or 'Printer' tab"
    echo "  3. Make sure 'Bambu Lab P1P 0.4 nozzle' is selected"
    echo "  4. Run this script again"
    echo ""
    exit 1
fi

# Process each file
for STL_FILE in "$INPUT_DIR"/*.stl; do
    [ -f "$STL_FILE" ] || continue
    
    FILENAME=$(basename "$STL_FILE")
    BASE="${FILENAME%.stl}"
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}📄 Processing: $FILENAME${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    # Open OrcaSlicer
    echo -e "${BLUE}🎨 Opening OrcaSlicer...${NC}"
    open -a OrcaSlicer "$STL_FILE"
    sleep 5
    
    echo ""
    echo -e "${YELLOW}┌─────────────────────────────────────────────┐${NC}"
    echo -e "${YELLOW}│  ⚠️  VERIFY SETTINGS BEFORE SLICING!       │${NC}"
    echo -e "${YELLOW}│                                             │${NC}"
    echo -e "${YELLOW}│  1️⃣  CHECK: Printer is 'P1P 0.4 nozzle'    │${NC}"
    echo -e "${YELLOW}│  2️⃣  CHECK: Process says '@BBL P1P'        │${NC}"
    echo -e "${YELLOW}│  3️⃣  Click 'Slice Plate'                   │${NC}"
    echo -e "${YELLOW}│  4️⃣  Export G-code as: ${BASE}.gcode${NC}"
    echo -e "${YELLOW}│  5️⃣  Save to: $OUTPUT_DIR/${NC}"
    echo -e "${YELLOW}│                                             │${NC}"
    echo -e "${YELLOW}│  Then press ENTER here...                  │${NC}"
    echo -e "${YELLOW}└─────────────────────────────────────────────┘${NC}"
    echo ""
    
    # Wait for user
    read -p "Press ENTER when you've exported the G-code... " 
    
    # Find the most recently created gcode file
    GCODE=$(find ~ -name "*.gcode" -type f -mmin -5 2>/dev/null | head -1)
    
    if [ -z "$GCODE" ] || [ ! -f "$GCODE" ]; then
        echo ""
        echo -e "${RED}❌ No G-code file found!${NC}"
        echo "Expected a .gcode file created in the last 5 minutes"
        echo ""
        read -p "Try again? (y/n): " RETRY
        
        if [[ ! "$RETRY" =~ ^[Yy]$ ]]; then
            mv "$STL_FILE" "${STL_FILE}.failed"
            echo -e "${RED}Marked as failed. Moving on...${NC}"
            continue
        else
            continue
        fi
    fi
    
    echo ""
    echo -e "${GREEN}✅ Found G-code: $(basename "$GCODE")${NC}"
    
    # Validate G-code before uploading
    echo -e "${BLUE}🔍 Validating G-code...${NC}"
    
    # Check for dangerous movements
    if grep -q "X[3-9][0-9][0-9]" "$GCODE" || grep -q "Y[3-9][0-9][0-9]" "$GCODE"; then
        echo -e "${RED}❌ DANGER: G-code contains movements beyond 256mm!${NC}"
        echo -e "${RED}This will damage your printer!${NC}"
        echo ""
        echo "The G-code was sliced with WRONG settings."
        echo "Please close OrcaSlicer and verify:"
        echo "  - Printer model is P1P (not X1 Carbon)"
        echo "  - Bed size is 256x256 (not 320x320)"
        echo ""
        mv "$STL_FILE" "${STL_FILE}.failed"
        read -p "Press ENTER to continue..."
        continue
    fi
    
    echo -e "${GREEN}✅ G-code looks safe!${NC}"
    
    # Ask about upload
    echo ""
    read -p "Upload to P1P at $PRINTER_IP? (y/n): " UPLOAD
    
    if [[ "$UPLOAD" =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}📤 Uploading to printer...${NC}"
        
        if curl -k --ftp-ssl \
            --user "bblp:$PRINTER_CODE" \
            -T "$GCODE" \
            "ftps://$PRINTER_IP:990/$(basename "$GCODE")" \
            --max-time 600 --connect-timeout 30 --progress-bar 2>&1; then
            
            echo ""
            echo -e "${GREEN}✅ Uploaded successfully!${NC}"
            echo -e "${GREEN}🎉 Ready to print!${NC}"
        else
            echo ""
            echo -e "${RED}❌ Upload failed${NC}"
            echo "G-code saved locally at: $GCODE"
        fi
    else
        echo -e "${BLUE}ℹ️  Skipped upload. G-code saved at:${NC}"
        echo "   $GCODE"
    fi
    
    # Mark as processed
    mv "$STL_FILE" "${STL_FILE}.processed"
    
    echo ""
done

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ ALL DONE!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
