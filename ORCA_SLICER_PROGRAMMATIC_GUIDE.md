# OrcaSlicer Programmatic Print Job Guide

## Best Solutions for Your Setup

Based on research, here are the most effective ways to kick off print jobs programmatically with OrcaSlicer, given your Bambu Lab P1P printer and network configuration.

## 🎯 Recommended Solutions (Ranked)

### 1. **OrcaSlicer Network Integration** ⭐ BEST OPTION
OrcaSlicer has built-in network printer support that can send files directly to your printer, **bypassing the CLI entirely**.

**Setup:**
```bash
# In OrcaSlicer GUI:
# 1. Edit Printer Profile → Advanced Settings
# 2. Enable "Use 3rd-party print host"
# 3. Configure printer IP: 192.168.1.129
# 4. Select protocol (FTP/FTPS for Bambu Lab)
```

**Programmatic Usage:**
- Save printer profile configuration
- OrcaSlicer can send sliced files directly via network
- No CLI needed - uses GUI networking features

**Advantages:**
- ✅ No CLI segfault issues
- ✅ Direct integration with Bambu Lab P1P
- ✅ Works with your existing network setup
- ✅ Can be automated via GUI scripting

### 2. **SimplyPrint Integration** ⭐ RECOMMENDED
SimplyPrint acts as an intermediary that OrcaSlicer can send files to, which then forwards to your printer.

**Setup:**
```bash
# Requirements: OrcaSlicer 2.0.0+
# In OrcaSlicer:
# 1. Click Wi-Fi icon next to printer profile
# 2. Select "SimplyPrint" as Host Type
# 3. Login/Test with SimplyPrint account
# 4. Configure for Bambu Lab P1P
```

**Advantages:**
- ✅ Bypasses CLI completely
- ✅ Remote monitoring and control
- ✅ Print queue management
- ✅ Works with network printers

**API Access:**
SimplyPrint provides an API for programmatic control:
- Send files programmatically
- Start/stop prints
- Monitor status
- Queue management

### 3. **AppleScript GUI Automation** ⭐ MACOS-SPECIFIC
Since you're on macOS, you can automate the OrcaSlicer GUI using AppleScript.

**Example Script:**
```applescript
tell application "OrcaSlicer"
    activate
    open file "~/AI_PIPELINE/LOCKED_SPLIT_STAGE/lets try this!.stl"
    
    -- Wait for file to load
    delay 2
    
    -- Select printer profile (requires GUI element access)
    -- This part requires UI scripting
    
    -- Trigger slice
    -- Send to printer via network
    
    quit
end tell
```

**Advantages:**
- ✅ Works around CLI segfault
- ✅ Uses existing GUI
- ✅ Can be called from Node.js service
- ✅ Native macOS integration

**Implementation:**
```javascript
const { exec } = require('child_process');
exec('osascript slice-automation.scpt', (error, stdout, stderr) => {
    // Handle result
});
```

### 4. **PrusaSlicer CLI Alternative**
PrusaSlicer has a stable CLI that can be used as a drop-in replacement.

**Installation:**
```bash
brew install prusa-slicer
```

**Usage:**
```bash
prusa-slicer --slice \
  --load-config "~/Documents/PrusaSlicer/config/printer/Bambu Lab P1P.ini" \
  --output "~/AI_PIPELINE/SLICED_OUTPUT/model.gcode" \
  "~/AI_PIPELINE/LOCKED_SPLIT_STAGE/model.stl"
```

**Advantages:**
- ✅ Stable CLI (no segfaults)
- ✅ Similar profile system
- ✅ Compatible with Bambu Lab printers
- ✅ Can use OrcaSlicer profiles (with conversion)

### 5. **Docker Container with Web Interface**
LinuxServer.io provides a Docker image with web-accessible OrcaSlicer.

**Setup:**
```bash
docker run -d \
  --name=orcaslicer \
  -p 8080:8080 \
  -v ~/AI_PIPELINE:/config \
  lscr.io/linuxserver/orcaslicer:latest
```

**Advantages:**
- ✅ Web interface (bypasses CLI)
- ✅ Can be accessed programmatically via HTTP
- ✅ Isolated environment
- ✅ May avoid segfault issues

## 🔧 Implementation for Your Service

### Option A: Use OrcaSlicer Network Integration

Modify your service to:
1. Use OrcaSlicer GUI to send files directly
2. Automate via AppleScript or GUI automation
3. Bypass CLI entirely

### Option B: Integrate SimplyPrint

```javascript
// service/utils/simplyprint.js
const axios = require('axios');

async function sendPrintJob(filePath, printerId) {
  const formData = new FormData();
  formData.append('file', fs.createReadStream(filePath));
  
  const response = await axios.post(
    `https://api.simplyprint.io/print/${printerId}`,
    formData,
    { headers: { 'Authorization': `Bearer ${API_KEY}` } }
  );
  
  return response.data;
}
```

### Option C: Use PrusaSlicer CLI

```javascript
// service/utils/prusa-slicer.js
const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

async function sliceWithPrusaSlicer(stlPath, outputPath, configPath) {
  const command = `prusa-slicer --slice --export-gcode \
    --load-config "${configPath}" \
    --output "${outputPath}" \
    "${stlPath}"`;
  
  const { stdout, stderr } = await execAsync(command);
  return { success: !stderr, output: stdout };
}
```

## 📋 Recommended Implementation Plan

### Phase 1: Quick Win (AppleScript)
1. Create AppleScript to automate OrcaSlicer GUI
2. Integrate into your service
3. Test with your STL files

### Phase 2: Network Integration
1. Configure OrcaSlicer network printer profile
2. Test direct file sending
3. Automate via GUI scripting

### Phase 3: Alternative Slicer (If Needed)
1. Install PrusaSlicer
2. Convert OrcaSlicer profiles
3. Replace OrcaSlicer CLI with PrusaSlicer CLI

## 🎯 Best Solution for Your Use Case

Given your setup:
- **Mac Mini server**
- **Bambu Lab P1P at 192.168.1.129**
- **Existing FTP upload working**
- **Node.js service**

**Recommended:** Use **OrcaSlicer Network Integration** + **AppleScript automation**

This approach:
- ✅ Bypasses CLI segfault
- ✅ Uses your existing network setup
- ✅ Integrates with your service
- ✅ Minimal changes needed

## 📚 Resources

- [OrcaSlicer Network Printing](https://orcaslicer.com/)
- [SimplyPrint Integration](https://help.simplyprint.io/en/article/the-orcaslicer-simplyprint-integration)
- [Obico Integration](https://www.obico.io/docs/user-guides/orca-slicer-integration/)
- [PrusaSlicer CLI Documentation](https://github.com/prusa3d/PrusaSlicer/wiki/Command-Line-Options)
- [OrcaSlicer GitHub CLI Discussion](https://github.com/SoftFever/OrcaSlicer/discussions/1603)

## 🔍 Next Steps

1. **Test OrcaSlicer Network Integration:**
   - Configure printer profile in GUI
   - Test sending a file directly
   - Document the process

2. **Create AppleScript Automation:**
   - Script to open OrcaSlicer
   - Load STL file
   - Select profile
   - Slice and send

3. **Integrate with Service:**
   - Add AppleScript execution to print-handler.js
   - Handle success/failure
   - Update webhook status


