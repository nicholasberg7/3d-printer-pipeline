#!/usr/bin/env python3
"""
Advanced 3MF Export with Color Assignments
Creates 3MF files with embedded color metadata for Bambu Studio/OrcaSlicer
"""

import json
import os
import sys
import zipfile
from pathlib import Path

def create_3mf_with_colors(stl_file, assignment_file, output_file):
    """Create 3MF file with color assignments embedded"""
    
    # Load color assignments
    with open(assignment_file, 'r') as f:
        assignments = json.load(f)
    
    # Read STL file
    with open(stl_file, 'rb') as f:
        stl_data = f.read()
    
    # Create 3MF structure
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as z:
        
        # Content Types
        content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
</Types>'''
        z.writestr('[Content_Types].xml', content_types)
        
        # Main model file
        model_name = Path(stl_file).stem
        model_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
    <metadata name="Title">{model_name}</metadata>
    <metadata name="Designer">AI Pipeline Color Splitter</metadata>
    <metadata name="Description">Advanced anatomical color mapping</metadata>
    <resources>
        <object id="1" type="model" name="{model_name}">
            <mesh>
                <vertices/>
                <triangles/>
            </mesh>
        </object>
    </resources>
    <build>
        <item objectid="1" name="{model_name}"/>
    </build>
</model>'''
        z.writestr('3D/3dmodel.model', model_xml)
        
        # Embed color assignment metadata
        z.writestr('metadata/color_assignment.json', json.dumps(assignments, indent=2))
        
        # Embed original STL for reference
        z.writestr(f'3D/{model_name}.stl', stl_data)
        
        # Create painting instructions
        instructions = {
            "title": "Manual Painting Guide for OrcaSlicer",
            "instructions": [
                "1. Open this 3MF file in OrcaSlicer",
                "2. Right-click the model → 'Paint-on supports' or use Paint tool",
                "3. Select different extruders/colors for each region:",
            ],
            "color_regions": []
        }
        
        for group in assignments["groups"]:
            instructions["color_regions"].append({
                "region": f"Part {group['part']}",
                "color": group["material"],
                "hex": group["hex"],
                "areas": group["use"]
            })
        
        z.writestr('metadata/painting_instructions.json', json.dumps(instructions, indent=2))
    
    print(f"✅ 3MF file created: {output_file}")
    print(f"📦 Contains:")
    print(f"   • Original STL geometry")
    print(f"   • Color assignment metadata")
    print(f"   • Manual painting instructions")
    print(f"   • {len(assignments['groups'])} color regions")
    
    return output_file

def main():
    if len(sys.argv) < 3:
        print("Usage: python export_to_bambu_3mf_advanced.py <input.stl> <assignment.json> [output.3mf]")
        sys.exit(1)
    
    stl_file = sys.argv[1]
    assignment_file = sys.argv[2]
    output_file = sys.argv[3] if len(sys.argv) > 3 else f"{Path(stl_file).stem}_colored.3mf"
    
    if not os.path.exists(stl_file):
        print(f"Error: STL file not found: {stl_file}")
        sys.exit(1)
    
    if not os.path.exists(assignment_file):
        print(f"Error: Assignment file not found: {assignment_file}")
        sys.exit(1)
    
    try:
        create_3mf_with_colors(stl_file, assignment_file, output_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
