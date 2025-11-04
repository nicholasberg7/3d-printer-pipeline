# OrcaSlicer AI Pipeline - Status & Solutions

## What We Discovered

### The Problem
OrcaSlicer CLI has a validation bug with the BBL (Bambu Lab) profiles:
- The profiles use `use_relative_e_distances` (relative E positioning)
- This requires `G92 E0` in `layer_gcode` to reset extruder position
- The BBL profiles inherit from parent profiles that don't include this
- The validation happens BEFORE profile inheritance is resolved
- Result: **CLI slicing fails with validation error**

### Why Bambu Studio Works
Bambu Studio likely:
1. Has the validation disabled or fixed
2. Uses different profile inheritance resolution
3. Has the Bambu networking plugin that handles this differently

### Current Status
- ✅ OrcaSlicer installed and working: `/usr/local/bin/orca`
- ✅ P1P printer found on network: `192.168.1.129`
- ✅ FTP upload working with access code: `30551719`
- ✅ GUI slicing works fine
- ❌ CLI slicing fails due to profile validation bug

## Working Solutions

### Solution 1: GUI + FTP Upload (CURRENT WORKING METHOD)
This is what we successfully did:

```bash
# 1. Open STL in OrcaSlicer GUI
open -a OrcaSlicer "/path/to/model.stl"

# 2. In GUI:
#    - Select "Bambu Lab P1P 0.4 nozzle"
#    - Select filament
#    - Click "Slice plate"
#    - Export G-code to Desktop

# 3. Upload via FTP
curl -k --ftp-ssl \
  --user "bblp:30551719" \
  -T ~/Desktop/model.gcode \
  "ftps://192.168.1.129:990/model.gcode" \
  --max-time 300
```

### Solution 2: Use Bambu Studio CLI
Since Bambu Studio works, use its CLI instead:

```bash
# Find Bambu Studio CLI
/Applications/BambuStudio.app/Contents/MacOS/BambuStudio \
  --load-settings "machine.json;process.json" \
  --load-filaments "filament.json" \
  --slice 0 \
  --outputdir ~/AI_PIPELINE/SLICED_OUTPUT \
  model.stl
```

### Solution 3: Fix OrcaSlicer Profiles (ATTEMPTED)
We tried creating standalone profiles without inheritance:
- Created `p1p_standalone.json` with `use_relative_e_distances = 0`
- Created `standalone_process.json` with `layer_gcode = G92 E0`
- Still failed due to compatibility checks

**Files created:**
- `~/AI_PIPELINE/ORCA_CONFIGS/json_profiles/p1p_standalone.json`
- `~/AI_PIPELINE/ORCA_CONFIGS/json_profiles/standalone_process.json`
- `~/AI_PIPELINE/ORCA_CONFIGS/json_profiles/working_process.json`

### Solution 4: Automated Pipeline Script
Created: `~/AI_PIPELINE/slice_pipeline.sh`

**Usage:**
```bash
# Slice only
~/AI_PIPELINE/slice_pipeline.sh

# Slice and upload to printer
~/AI_PIPELINE/slice_pipeline.sh --upload
```

**Note:** Currently fails at slicing step due to profile validation bug.

## Recommended Next Steps

### Option A: Use Bambu Studio for Slicing
1. Install/use Bambu Studio CLI
2. Update `slice_pipeline.sh` to use Bambu Studio instead of OrcaSlicer
3. Keep FTP upload functionality

### Option B: Build Custom OrcaSlicer
1. Clone OrcaSlicer repository (already done)
2. Modify validation code to skip the relative E check
3. Build custom version
4. Use custom build for CLI automation

**File to modify:** `src/libslic3r/GCode.cpp` or `src/libslic3r/PrintConfig.cpp`
**Change:** Comment out or disable the validation error for relative E distances

### Option C: Use GUI Automation
1. Use AppleScript or similar to automate OrcaSlicer GUI
2. Load model, slice, export
3. Upload via FTP

### Option D: Wait for OrcaSlicer Fix
Report the bug to OrcaSlicer developers:
- CLI validation happens before profile inheritance resolution
- BBL profiles fail validation even though they work in GUI

## Your AI Pipeline Architecture

```
Input STL Files
    ↓
~/AI_PIPELINE/LOCKED_SPLIT_STAGE/
    ↓
[SLICING ENGINE]  ← Currently broken in OrcaSlicer CLI
    ↓
~/AI_PIPELINE/SLICED_OUTPUT/
    ↓
[FTP UPLOAD]  ← Working!
    ↓
P1P Printer (192.168.1.129)
```

## Configuration Files

### Profiles Location
- **OrcaSlicer System:** `/Users/nicholasberg/Documents/OrcaSlicer/resources/profiles/BBL/`
- **Custom Profiles:** `~/AI_PIPELINE/ORCA_CONFIGS/json_profiles/`
- **Bambu Studio:** `~/Library/Application Support/BambuStudio/`

### Printer Connection
- **IP:** 192.168.1.129
- **Serial:** 01P09A3A1800831
- **Access Code:** 30551719
- **FTP Port:** 990 (FTPS)
- **Username:** bblp

## Commands Reference

### Test Slicing (will fail currently)
```bash
orca \
  --load-settings "machine.json;process.json" \
  --load-filaments "filament.json" \
  --slice 0 \
  --outputdir ~/AI_PIPELINE/SLICED_OUTPUT \
  model.stl
```

### Upload to Printer
```bash
curl -k --ftp-ssl \
  --user "bblp:30551719" \
  -T model.gcode \
  "ftps://192.168.1.129:990/model.gcode" \
  --max-time 300
```

### Check Printer Files
```bash
curl -k --ftp-ssl \
  --user "bblp:30551719" \
  "ftps://192.168.1.129:990/" \
  --list-only
```

## Next Session TODO

1. **Immediate:** Switch to Bambu Studio CLI for slicing
2. **Short-term:** Update `slice_pipeline.sh` to use working slicer
3. **Long-term:** Either build custom OrcaSlicer or wait for official fix
4. **Test:** End-to-end pipeline with actual print job

## Files Created This Session

- `~/AI_PIPELINE/slice_pipeline.sh` - Automation script
- `~/AI_PIPELINE/ORCA_CONFIGS/json_profiles/*.json` - Custom profiles
- `~/AI_PIPELINE/SLICED_OUTPUT/project.3mf` - Test 3MF file
- `~/AI_PIPELINE/README_PIPELINE.md` - This document

---

**Session Date:** November 2, 2025  
**Status:** FTP upload working, CLI slicing blocked by validation bug  
**Next Action:** Switch to Bambu Studio CLI or build custom OrcaSlicer
