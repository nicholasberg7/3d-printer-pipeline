# OrcaSlicer CLI Segfault Fix

## Problem Summary

Both OrcaSlicer and Bambu Studio segfault when running in CLI mode. The crash occurs in GUI initialization code:

```
Segmentation fault: 11
Location: Slic3r::GUI::PartPlate::set_shape
```

The crash happens because the CLI tries to initialize GUI components even when running headless.

## Root Cause

1. **Custom OrcaSlicer Build**: Segfaults in `Slic3r::GUI::PartPlate::set_shape` during GUI initialization
2. **System OrcaSlicer**: Fails validation (G92 E0 check) before it can segfault
3. **Bambu Studio**: Also segfaults in GUI initialization

## Solutions

### Solution 1: Use GUI Programmatically (Recommended)

Use AppleScript or automation to control the GUI:

```bash
# Open OrcaSlicer GUI with STL file
open -a OrcaSlicer ~/AI_PIPELINE/LOCKED_SPLIT_STAGE/lets\ try\ this\!.stl

# Then use AppleScript to:
# 1. Select P1P profile
# 2. Click slice
# 3. Export G-code
# 4. Close app
```

### Solution 2: Patch System OrcaSlicer Binary

The validation check can be disabled in the binary:
- Find the validation error message string
- Patch the binary to skip the validation check
- Requires binary editing tools

### Solution 3: Wait for Upstream Fix

Report the GUI initialization bug to:
- OrcaSlicer: https://github.com/SoftFever/OrcaSlicer
- Bambu Studio: https://github.com/bambulab/BambuStudio

## Current Status

The service is configured to:
1. Try Bambu Studio first (if available)
2. Fall back to OrcaSlicer pipeline
3. Both will likely segfault due to GUI initialization

## Workaround in Service

The service code (`service/utils/print-handler.js`) now:
- Attempts Bambu Studio first
- Falls back to OrcaSlicer if Bambu Studio fails
- Handles segfaults gracefully

## Next Steps

1. **Short-term**: Use GUI programmatically with AppleScript
2. **Medium-term**: Patch system OrcaSlicer binary to disable validation
3. **Long-term**: Wait for upstream fix or rebuild with GUI disabled

## Testing

To test if the segfault is fixed:

```bash
# Test custom build
~/Documents/OrcaSlicer/build/arm64/src/OrcaSlicer.app/Contents/MacOS/OrcaSlicer \
  --slice 0 \
  --outputdir ~/AI_PIPELINE/SLICED_OUTPUT \
  ~/AI_PIPELINE/LOCKED_SPLIT_STAGE/lets\ try\ this\!.stl

# Test system OrcaSlicer
/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer \
  --slice 0 \
  --outputdir ~/AI_PIPELINE/SLICED_OUTPUT \
  ~/AI_PIPELINE/LOCKED_SPLIT_STAGE/lets\ try\ this\!.stl

# Test Bambu Studio
/Applications/BambuStudio.app/Contents/MacOS/BambuStudio \
  --slice 0 \
  --outputdir ~/AI_PIPELINE/SLICED_OUTPUT \
  ~/AI_PIPELINE/LOCKED_SPLIT_STAGE/lets\ try\ this\!.stl
```

All three currently segfault or fail validation.


