#!/usr/bin/env python3
"""
Bambu Color Assignment Generator
Creates color assignment JSON for manual painting in OrcaSlicer/Bambu Studio
"""

import json
import os
import sys

def create_color_assignment(stl_file, paintgroups_file, output_file):
    """Create color assignment JSON from paintgroups"""
    
    # Load paint groups
    with open(paintgroups_file, 'r') as f:
        data = json.load(f)
    
    materials = data["materials"]
    
    # Build assignment structure
    assignments = {
        "model": os.path.basename(stl_file),
        "timestamp": "2025-11-04",
        "groups": []
    }
    
    # Create assignment for each material
    for i, material in enumerate(materials, 1):
        assignments["groups"].append({
            "part": i,
            "material": material["name"],
            "hex": material["hex"],
            "use": material["use"]
        })
    
    # Save assignment file
    with open(output_file, 'w') as f:
        json.dump(assignments, f, indent=2)
    
    print(f"✅ Color assignment created: {output_file}")
    print(f"📊 Materials: {len(materials)}")
    for material in materials:
        print(f"   • {material['name']:15s} {material['hex']} - {material['use']}")
    
    return assignments

def main():
    if len(sys.argv) < 2:
        print("Usage: python bambu_color_assign.py <input.stl> [paintgroups.json] [output.json]")
        sys.exit(1)
    
    stl_file = sys.argv[1]
    paintgroups_file = sys.argv[2] if len(sys.argv) > 2 else "bambu_paintgroups.txt"
    output_file = sys.argv[3] if len(sys.argv) > 3 else "bambu_color_assignment.json"
    
    if not os.path.exists(stl_file):
        print(f"Error: STL file not found: {stl_file}")
        sys.exit(1)
    
    if not os.path.exists(paintgroups_file):
        print(f"Error: Paint groups file not found: {paintgroups_file}")
        sys.exit(1)
    
    try:
        create_color_assignment(stl_file, paintgroups_file, output_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
