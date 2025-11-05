# 🎨 Manual Painting Guide for OrcaSlicer

## Overview
This guide shows you how to manually paint your anatomical parts in OrcaSlicer using our advanced 8-region color mapping system.

## 🎯 Color Scheme (8 Regions)

| Region | Color | Hex Code | Use Case |
|--------|-------|----------|----------|
| **armor_primary** | Dark Steel Blue | `#2A4E78` | chest, helmet, shins |
| **armor_highlight** | Medium Blue | `#3E78B1` | arms, thighs, side panels |
| **frame** | Warm Bone Tan | `#C6A376` | ribs, inner limbs, spine |
| **joint_shadow** | Burnt Umber | `#7B4E2D` | elbows, knees, recesses |
| **metal_dark** | Gunmetal Gray | `#5C5C5C` | bolts, hinges, brackets |
| **metal_light** | Light Silver | `#A6A6A6` | edges, wear highlights |
| **optics** | Amber | `#C78B2A` | eyes, sensors, glass |
| **accent** | Faded Black | `#1B1B1B` | soles, gloves, trim |

## 🛠️ Step-by-Step Manual Painting Process

### Method 1: Using Split Parts (Recommended)

1. **Run the Advanced Splitter:**
   ```bash
   cd ~/AI_PIPELINE
   source env/bin/activate
   python advanced_color_splitter.py "lets try this!.stl" ANATOMICAL_PARTS color_map_config.txt
   ```

2. **Load Parts in OrcaSlicer:**
   - Open OrcaSlicer
   - File → Import → Import STL
   - Select all the `*_[region].stl` files from `ANATOMICAL_PARTS/`
   - They'll load as separate objects

3. **Assign Colors:**
   - Right-click each part → "Change Filament"
   - Select the appropriate extruder/color for each region
   - Use the color mapping table above

### Method 2: Paint Tool on Single Model

1. **Load the Full Model:**
   ```bash
   # Open the main STL file in OrcaSlicer
   open -a OrcaSlicer "lets try this!.stl"
   ```

2. **Access Paint Tool:**
   - Select the model
   - Click the **Paint Tool** in the left toolbar (brush icon)
   - Or right-click → "Paint-on supports" → Switch to paint mode

3. **Set Up Extruders:**
   - Go to Printer Settings
   - Set up 5-8 extruders with your colors
   - Match the hex codes from our color scheme

4. **Paint by Region:**
   - Select Extruder 1 (Dark Steel Blue) → Paint chest, helmet, shins
   - Select Extruder 2 (Medium Blue) → Paint arms, thighs, side panels
   - Select Extruder 3 (Warm Bone Tan) → Paint ribs, inner limbs, spine
   - Continue for all 8 regions...

## 🎨 OrcaSlicer Paint Tool Tips

### Brush Settings:
- **Brush Size:** Start with 5-10mm, adjust as needed
- **Brush Strength:** 100% for solid coverage
- **Smart Fill:** Enable for faster painting of enclosed areas

### Navigation:
- **Rotate:** Right-click + drag
- **Zoom:** Scroll wheel
- **Pan:** Middle-click + drag

### Painting Techniques:
- **Large Areas:** Use big brush with Smart Fill
- **Details:** Switch to small brush (1-2mm)
- **Edges:** Use medium brush, paint carefully along boundaries
- **Corrections:** Right-click to erase, or paint over with different color

## 🔧 Advanced Workflow

### Complete Pipeline:
```bash
cd ~/AI_PIPELINE
source env/bin/activate

# 1. Split the model
python advanced_color_splitter.py "lets try this!.stl" ANATOMICAL_PARTS color_map_config.txt

# 2. Create color assignments
python bambu_color_assign.py "lets try this!.stl" bambu_paintgroups.txt color_assignment.json

# 3. Export to 3MF with metadata
python export_to_bambu_3mf_advanced.py "lets try this!.stl" color_assignment.json "lets_try_this_colored.3mf"

# 4. Open in OrcaSlicer
open -a OrcaSlicer "lets_try_this_colored.3mf"
```

## 📋 Quality Control Checklist

Before slicing, verify:
- [ ] All regions are painted with correct colors
- [ ] No unpainted areas (shows as white/default)
- [ ] Color boundaries are clean
- [ ] Small details are properly colored
- [ ] Extruder assignments match your filament setup

## 🎯 Region-Specific Painting Guide

### **Armor Primary (Dark Steel Blue)**
- **Areas:** Main chest plate, helmet dome, shin guards
- **Technique:** Use large brush, fill major surfaces first
- **Details:** Watch for recessed areas that might be missed

### **Armor Highlight (Medium Blue)**
- **Areas:** Arm plates, thigh armor, side panels
- **Technique:** Medium brush, follow natural armor panel lines
- **Details:** Blend edges with primary armor

### **Frame (Warm Bone Tan)**
- **Areas:** Internal structure, ribs, spine details
- **Technique:** Small brush for precision, these are often thin elements
- **Details:** Look for skeletal/structural elements

### **Joint Shadow (Burnt Umber)**
- **Areas:** Elbow joints, knee joints, recessed areas
- **Technique:** Small brush, focus on depth and shadows
- **Details:** These add realism to mechanical joints

### **Metal Dark (Gunmetal Gray)**
- **Areas:** Bolts, hinges, mechanical brackets
- **Technique:** Very small brush, precise application
- **Details:** Small mechanical details that need metallic look

### **Metal Light (Light Silver)**
- **Areas:** Wear points, edges, highlights
- **Technique:** Small brush, light touches for highlights
- **Details:** Adds weathering and realism

### **Optics (Amber)**
- **Areas:** Eyes, sensors, glass elements, lights
- **Technique:** Very small brush, precise application
- **Details:** Should glow/stand out from other elements

### **Accent (Faded Black)**
- **Areas:** Soles, gloves, trim, small details
- **Technique:** Small brush, clean up and define edges
- **Details:** Provides contrast and definition

## 🚀 Pro Tips

1. **Start with Large Areas:** Paint the biggest regions first (armor_primary, armor_highlight)
2. **Work Inside-Out:** Paint recessed areas before raised areas
3. **Use Reference:** Keep the color table open while painting
4. **Save Often:** OrcaSlicer can crash, save your progress
5. **Test Print:** Do a small test print to verify colors before full print

## 🔄 Troubleshooting

### Paint Tool Not Working:
- Make sure model is selected
- Check that you have multiple extruders configured
- Restart OrcaSlicer if tool is unresponsive

### Colors Not Showing:
- Verify extruder setup in printer settings
- Check that filament colors are assigned
- Make sure you're in "Multi-color" mode

### Missing Details:
- Zoom in closer for small features
- Use smaller brush size
- Enable "Show painted areas" to see coverage

---

**Ready to paint!** 🎨 This system gives you professional-quality multi-color prints with anatomically correct color placement.
