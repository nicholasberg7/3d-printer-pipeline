# Why OrcaSlicer CLI Can't Work Programmatically - Simple Answer

## The Short Answer

**OrcaSlicer CLI fails because of TWO bugs:**

1. **System OrcaSlicer** → Validation error (profile inheritance issue)
2. **Custom Build** → Segfault (GUI initialization issue)

## The Details

### System OrcaSlicer (`/Applications/OrcaSlicer.app`)
```
Error: "Relative extruder addressing requires resetting the extruder position 
at each layer to prevent loss of floating point accuracy. Add 'G92 E0' to layer_gcode."
```

**Why:** The validation check runs BEFORE profile inheritance resolves, so it doesn't find `G92 E0` even though it's in the profile.

**Test:**
```bash
/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer \
  --slice 0 \
  --outputdir ~/AI_PIPELINE/SLICED_OUTPUT \
  "lets try this!.stl"
# Result: Exit code 205 - Validation error
```

### Custom Build (`~/Documents/OrcaSlicer/build/arm64/...`)
```
Segmentation fault: 11
Location: Slic3r::GUI::PartPlate::set_shape
```

**Why:** The CLI tries to initialize GUI components even when running headless, causing a crash.

**Test:**
```bash
~/Documents/OrcaSlicer/build/arm64/src/OrcaSlicer.app/Contents/MacOS/OrcaSlicer \
  --slice 0 \
  --outputdir ~/AI_PIPELINE/SLICED_OUTPUT \
  "lets try this!.stl"
# Result: Exit code 139 - Segfault
```

## What DOES Work

✅ **OrcaSlicer GUI** - Works perfectly!
- Opens files
- Slices correctly
- Exports G-code
- No issues at all

## The Solution

**You CAN use OrcaSlicer programmatically, but you need to automate the GUI instead of using CLI:**

1. **GUI Automation** (AppleScript) - Bypasses CLI entirely
2. **Network Integration** - Use OrcaSlicer's built-in network features
3. **Fix the Build** - Debug the segfault in custom build

## Current Status

- ❌ CLI: Broken (validation error or segfault)
- ✅ GUI: Works perfectly
- ✅ FTP Upload: Works (you can upload G-code manually)
- ⚠️ Programmatic: Needs GUI automation

## Quick Test

Try this:
```bash
open -a OrcaSlicer "lets try this!.stl"
```

It opens in GUI and works! The CLI just has bugs that prevent programmatic use.


