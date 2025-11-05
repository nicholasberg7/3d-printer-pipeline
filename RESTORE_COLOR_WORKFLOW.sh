#!/bin/bash
# Restore Advanced Color Workflow - Recreated from Terminal History
# This script recreates the complete color mapping system we had before

set -e

echo "🎨 RESTORING ADVANCED COLOR WORKFLOW"
echo "======================================"

# Activate virtual environment
if [ ! -d "env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv env
fi

source env/bin/activate

# Install required packages
echo "📦 Installing required packages..."
pip install trimesh shapely numpy scipy networkx

# Create proper config files (bypass gitignore)
echo "📁 Creating CONFIG directory structure..."
mkdir -p CONFIG
mkdir -p LOCKED_REPAIR_STAGE
mkdir -p LOCKED_SPLIT_STAGE  
mkdir -p LOCKED_COLOR_STAGE
mkdir -p LOCKED_ASSIGN_STAGE
mkdir -p ANATOMICAL_PARTS

# Copy config files to proper locations
echo "⚙️  Setting up configuration files..."
cp color_map_config.txt CONFIG/color_map.cfg
cp bambu_paintgroups.txt CONFIG/bambu_paintgroups.json

# Test the color config
echo "🧪 Testing color configuration..."
python3 -c "
import configparser
cfg = configparser.ConfigParser()
cfg.read('CONFIG/color_map.cfg')
print(f'✅ Loaded {len(cfg.sections())} color regions:')
for section in cfg.sections():
    print(f'   • {section}: {cfg[section][\"label\"]} {cfg[section][\"hex\"]}')
"

# Check if we have the STL file
STL_FILE="lets try this!.stl"
if [ -f "$STL_FILE" ]; then
    echo "🎯 Found STL file: $STL_FILE"
    
    # Run the complete workflow
    echo "🚀 Running complete color workflow..."
    
    echo "1️⃣  Splitting model into anatomical parts..."
    python advanced_color_splitter.py "$STL_FILE" ANATOMICAL_PARTS CONFIG/color_map.cfg
    
    echo "2️⃣  Creating color assignments..."
    python bambu_color_assign.py "$STL_FILE" CONFIG/bambu_paintgroups.json LOCKED_ASSIGN_STAGE/color_assignment.json
    
    echo "3️⃣  Exporting to 3MF with color metadata..."
    python export_to_bambu_3mf_advanced.py "$STL_FILE" LOCKED_ASSIGN_STAGE/color_assignment.json LOCKED_ASSIGN_STAGE/lets_try_this_colored.3mf
    
    echo "4️⃣  Copying files to LOCKED stages..."
    cp "$STL_FILE" LOCKED_SPLIT_STAGE/
    cp CONFIG/bambu_paintgroups.json LOCKED_COLOR_STAGE/
    
    echo ""
    echo "✅ WORKFLOW COMPLETE!"
    echo "===================="
    echo ""
    echo "📂 Files created:"
    echo "   • ANATOMICAL_PARTS/ - Split STL files by region"
    echo "   • LOCKED_ASSIGN_STAGE/color_assignment.json - Color mapping"
    echo "   • LOCKED_ASSIGN_STAGE/lets_try_this_colored.3mf - 3MF with colors"
    echo "   • CONFIG/color_map.cfg - 8-region color configuration"
    echo ""
    echo "🎨 Next steps:"
    echo "   1. Read MANUAL_PAINTING_GUIDE.md"
    echo "   2. Open OrcaSlicer"
    echo "   3. Load the 3MF file or individual STL parts"
    echo "   4. Use the Paint Tool to apply colors manually"
    echo ""
    echo "🚀 To open in OrcaSlicer:"
    echo "   open -a OrcaSlicer LOCKED_ASSIGN_STAGE/lets_try_this_colored.3mf"
    
else
    echo "⚠️  STL file not found: $STL_FILE"
    echo "   Place your STL file in the AI_PIPELINE directory and run again"
fi

echo ""
echo "🎉 Advanced color mapping system restored!"
