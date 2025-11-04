# 🚀 Quick Start Guide

## TL;DR - Get Printing Now!

```bash
# 1. Add your STL file
cp your_model.stl ~/AI_PIPELINE/LOCKED_SPLIT_STAGE/

# 2. Run the pipeline
cd ~/AI_PIPELINE
./slice_pipeline_gui.sh

# 3. When OrcaSlicer opens:
#    - Select "Bambu Lab P1P 0.4 nozzle"
#    - Click "Slice Plate"
#    - Export G-code
#    - Press ENTER in terminal

# 4. Your G-code is ready!
ls ~/AI_PIPELINE/SLICED_OUTPUT/
```

## 📋 All Commands

### Basic Usage
```bash
# Process files once (manual mode)
./slice_pipeline_gui.sh

# Process and auto-upload to printer
./slice_pipeline_gui.sh --upload

# Watch for new files continuously
./slice_pipeline_gui.sh --watch

# Watch and upload automatically
./slice_pipeline_gui.sh --watch --upload
```

### Check Status
```bash
# View logs
tail -f ~/AI_PIPELINE/logs/pipeline_*.log

# See output files
ls -lh ~/AI_PIPELINE/SLICED_OUTPUT/

# Check processed files
ls ~/AI_PIPELINE/LOCKED_SPLIT_STAGE/*.processed
```

### Troubleshooting
```bash
# Remove lock file if stuck
rm /tmp/slice_pipeline.lock

# Retry failed file
cd ~/AI_PIPELINE/LOCKED_SPLIT_STAGE
mv filename.stl.failed filename.stl

# Test printer connection
ping 192.168.1.129
```

## ✅ What's Working

1. ✅ **Automated File Monitoring** - Watches for new STL files
2. ✅ **GUI Automation** - Opens OrcaSlicer automatically
3. ✅ **FTP Upload** - Sends G-code to your P1P printer
4. ✅ **Comprehensive Logging** - Track everything
5. ✅ **Error Handling** - Marks files as processed/failed
6. ✅ **Git Backup** - All code pushed to GitHub

## 🔧 Your Configuration

- **Printer IP**: 192.168.1.129
- **Input Folder**: ~/AI_PIPELINE/LOCKED_SPLIT_STAGE/
- **Output Folder**: ~/AI_PIPELINE/SLICED_OUTPUT/
- **Logs**: ~/AI_PIPELINE/logs/

## 📚 More Info

- **Full Guide**: `SETUP_COMPLETE_GUIDE.md`
- **Project Vision**: `PROJECT_VISION.md`
- **Technical Details**: `SOLUTION.md`

## 💡 Pro Tips

1. **Start with one file** to test the workflow
2. **Check logs** if something goes wrong
3. **Use --watch mode** for continuous automation
4. **Keep OrcaSlicer settings** as you like them - the pipeline uses your profiles

## 🎉 You're Ready!

Just run `./slice_pipeline_gui.sh` and start printing!
