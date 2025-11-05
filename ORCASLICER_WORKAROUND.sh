#!/bin/bash
# OrcaSlicer GUI Automation Workaround
# This bypasses the CLI issues by using the GUI programmatically

STL_FILE="$1"
OUTPUT_DIR="$HOME/AI_PIPELINE/SLICED_OUTPUT"
mkdir -p "$OUTPUT_DIR"

if [ -z "$STL_FILE" ]; then
    echo "Usage: $0 <stl_file>"
    exit 1
fi

echo "🎨 Using OrcaSlicer GUI automation..."
echo "File: $STL_FILE"
echo "Output: $OUTPUT_DIR"

# Create AppleScript to automate OrcaSlicer
cat > /tmp/orcaslicer_automation.scpt <<EOF
tell application "OrcaSlicer"
    activate
    delay 2
    
    -- Open the STL file
    open POSIX file "$STL_FILE"
    delay 3
    
    -- Note: Full automation requires UI scripting which needs accessibility permissions
    -- For now, this opens OrcaSlicer with the file loaded
    -- User needs to manually:
    -- 1. Select P1P profile
    -- 2. Click "Slice Plate"
    -- 3. Export G-code
    
    -- For full automation, we'd need to use UI scripting:
    -- tell application "System Events"
    --     tell process "OrcaSlicer"
    --         click button "Slice Plate"
    --     end tell
    -- end tell
end tell
EOF

# Execute AppleScript
osascript /tmp/orcaslicer_automation.scpt

echo ""
echo "✅ OrcaSlicer opened with your file"
echo "⚠️  Manual steps required (until full automation is implemented):"
echo "   1. Select 'Bambu Lab P1P 0.4 nozzle' profile"
echo "   2. Click 'Slice Plate'"
echo "   3. Export G-code to: $OUTPUT_DIR"


