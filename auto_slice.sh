#!/bin/bash
# Fully Automated Slicing with AppleScript
# This clicks all the buttons automatically!

STL_FILE="$1"
OUTPUT_DIR="$HOME/AI_PIPELINE/SLICED_OUTPUT"
FILENAME=$(basename "$STL_FILE" .stl)
OUTPUT_GCODE="$OUTPUT_DIR/${FILENAME}.gcode"

echo "🤖 Starting FULL automation for: $FILENAME"

# Create AppleScript for full automation
osascript <<EOF
-- Wait for OrcaSlicer to be ready
delay 3

-- Use System Events for UI automation (requires accessibility permissions)
tell application "System Events"
    -- Make sure OrcaSlicer is frontmost
    tell process "OrcaSlicer"
        set frontmost to true
        delay 2
        
        -- Try to click "Slice Plate" button
        try
            click button "Slice Plate" of window 1
            log "✓ Clicked 'Slice Plate'"
            delay 15
        on error errMsg
            log "⚠️  Could not click Slice Plate: " & errMsg
        end try
        
        -- Export G-code (Command+Shift+G)
        try
            keystroke "g" using {command down, shift down}
            log "✓ Triggered export dialog"
            delay 3
        on error errMsg
            log "⚠️  Could not trigger export: " & errMsg
        end try
        
        -- Type the filename
        try
            keystroke "$OUTPUT_GCODE"
            delay 1
            keystroke return
            log "✓ Saved G-code"
            delay 3
        on error errMsg
            log "⚠️  Could not save file: " & errMsg
        end try
        
    end tell
end tell

-- Close OrcaSlicer
tell application "OrcaSlicer"
    try
        close window 1
    end try
end tell

EOF

# Check if G-code was created
if [ -f "$OUTPUT_GCODE" ]; then
    echo "✅ SUCCESS! G-code saved to: $OUTPUT_GCODE"
    exit 0
else
    echo "❌ FAILED! G-code not found"
    exit 1
fi
