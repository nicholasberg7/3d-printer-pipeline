# 🖨️ How to Print - SUPER SIMPLE!

## 3 Steps to Print

### 1️⃣ Add your STL file
```bash
cp your_model.stl ~/AI_PIPELINE/LOCKED_SPLIT_STAGE/
```

### 2️⃣ Run the script
```bash
cd ~/AI_PIPELINE
./PRINT.sh
```

### 3️⃣ Click 2 buttons when OrcaSlicer opens
- Click "Slice Plate"
- Export G-code (save to the path shown)
- Press ENTER in terminal

**That's it!** The script handles everything else! 🎉

---

## What It Does

✅ Opens each STL file automatically  
✅ Waits for you to slice (2 clicks)  
✅ Asks if you want to upload to printer  
✅ Uploads via FTP if you say yes  
✅ Marks files as processed  
✅ Handles multiple files in a row  

## Example

```bash
# Add a file
cp robot.stl ~/AI_PIPELINE/LOCKED_SPLIT_STAGE/

# Run
./PRINT.sh

# OrcaSlicer opens → Click "Slice Plate" → Export
# Terminal asks: "Upload to printer? (y/n)"
# Type 'y' and press ENTER
# Done! ✅
```

## Retry Failed Files

```bash
cd ~/AI_PIPELINE/LOCKED_SPLIT_STAGE
mv filename.stl.failed filename.stl
./PRINT.sh
```

## View Output

```bash
ls ~/AI_PIPELINE/SLICED_OUTPUT/
```

---

**Pro Tip**: Keep OrcaSlicer's printer profile set to "Bambu Lab P1P 0.4 nozzle" so you don't have to select it each time!
