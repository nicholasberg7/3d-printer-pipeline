#!/usr/bin/env python3
"""
Anatomical Color Splitter V2 - Using Direct Binary Copy
Splits STL by body part regions using direct byte copying (no corruption!)
"""

import sys
import os
import json
import struct
from pathlib import Path

# Color definitions
COLORS = {
    'burnt_umber': {'hex': '#7B4E2D', 'name': 'Brown'},
    'gunmetal_gray': {'hex': '#5C5C5C', 'name': 'Dark Gray'},
    'light_silver': {'hex': '#A6A6A6', 'name': 'Light Gray'},
    'amber': {'hex': '#C78B2A', 'name': 'Gold'},
    'faded_black': {'hex': '#1B1B1B', 'name': 'Black'}
}

# Anatomical mapping
ANATOMICAL_COLORS = {
    'limbs': 'burnt_umber',
    'helmet': 'burnt_umber',
    'chest_body': 'gunmetal_gray',
    'hands_skull': 'light_silver',
    'detail': 'faded_black',
    'accent': 'amber'
}

def classify_triangle_anatomical(vertices, bounds):
    """Classify triangle by anatomical region using vertex coordinates"""
    # Calculate triangle center
    cx = (vertices[0][0] + vertices[1][0] + vertices[2][0]) / 3.0
    cy = (vertices[0][1] + vertices[1][1] + vertices[2][1]) / 3.0
    cz = (vertices[0][2] + vertices[1][2] + vertices[2][2]) / 3.0
    
    # Calculate relative positions
    z_range = bounds['z_max'] - bounds['z_min']
    x_range = bounds['x_max'] - bounds['x_min']
    y_range = bounds['y_max'] - bounds['y_min']
    
    z_pct = (cz - bounds['z_min']) / z_range if z_range > 0 else 0
    x_pct = (cx - bounds['x_min']) / x_range if x_range > 0 else 0
    y_pct = (cy - bounds['y_min']) / y_range if y_range > 0 else 0
    
    # Helmet: top 20%
    if z_pct > 0.80:
        if y_pct > 0.5:
            return 'hands_skull'  # Skull/face
        else:
            return 'helmet'
    
    # Hands: extreme top sides
    if z_pct > 0.75 and (x_pct < 0.15 or x_pct > 0.85):
        return 'hands_skull'
    
    # Chest/Body: middle 30-70% height, center mass
    if 0.30 < z_pct < 0.70 and 0.25 < x_pct < 0.75:
        return 'chest_body'
    
    # Limbs (arms/legs): sides and lower portions
    if x_pct < 0.25 or x_pct > 0.75:
        return 'limbs'
    
    if z_pct < 0.30:
        return 'limbs'
    
    # Detail/trim: edges
    edge_threshold = 0.05
    if (x_pct < edge_threshold or x_pct > (1-edge_threshold) or
        z_pct < edge_threshold or z_pct > (1-edge_threshold)):
        return 'detail'
    
    # Default: accent
    return 'accent'

def analyze_and_split(input_file, output_dir):
    """Analyze STL and split by anatomy using direct byte copying"""
    
    print(f"\n{'='*60}")
    print(f"ANATOMICAL COLOR SPLITTER V2")
    print(f"{'='*60}\n")
    
    print(f"Loading: {input_file}")
    
    # First pass: get bounds and classify triangles
    with open(input_file, 'rb') as f:
        f.read(80)  # Skip header
        total_triangles = struct.unpack('<I', f.read(4))[0]
        print(f"Total triangles: {total_triangles:,}\n")
        
        # Read sample to get bounds
        print("Analyzing bounds...")
        all_x, all_y, all_z = [], [], []
        
        for i in range(min(10000, total_triangles)):
            f.read(12)  # normal
            v1 = struct.unpack('<fff', f.read(12))
            v2 = struct.unpack('<fff', f.read(12))
            v3 = struct.unpack('<fff', f.read(12))
            f.read(2)  # attribute
            
            for v in [v1, v2, v3]:
                all_x.append(v[0])
                all_y.append(v[1])
                all_z.append(v[2])
        
        bounds = {
            'x_min': min(all_x), 'x_max': max(all_x),
            'y_min': min(all_y), 'y_max': max(all_y),
            'z_min': min(all_z), 'z_max': max(all_z),
        }
        
        print(f"  X: {bounds['x_min']:.2f} to {bounds['x_max']:.2f}")
        print(f"  Y: {bounds['y_min']:.2f} to {bounds['y_max']:.2f}")
        print(f"  Z: {bounds['z_min']:.2f} to {bounds['z_max']:.2f}\n")
    
    # Second pass: classify all triangles
    print("Classifying triangles by anatomy...")
    triangle_regions = []
    
    with open(input_file, 'rb') as f:
        f.read(80)
        f.read(4)
        
        for i in range(total_triangles):
            f.read(12)  # normal
            v1 = struct.unpack('<fff', f.read(12))
            v2 = struct.unpack('<fff', f.read(12))
            v3 = struct.unpack('<fff', f.read(12))
            f.read(2)  # attribute
            
            region = classify_triangle_anatomical([v1, v2, v3], bounds)
            triangle_regions.append(region)
            
            if (i+1) % 100000 == 0:
                print(f"  Progress: {i+1:,}/{total_triangles:,}")
    
    print("\nClassification complete!\n")
    
    # Count triangles per region
    region_counts = {}
    for region in triangle_regions:
        region_counts[region] = region_counts.get(region, 0) + 1
    
    print(f"{'='*60}")
    print("PART BREAKDOWN:")
    print(f"{'='*60}")
    
    for region in ANATOMICAL_COLORS.keys():
        count = region_counts.get(region, 0)
        pct = (count / total_triangles) * 100
        color_key = ANATOMICAL_COLORS[region]
        color_info = COLORS[color_key]
        print(f"  {region:15s}: {count:8,} triangles ({pct:5.1f}%) → {color_info['name']:12s} {color_info['hex']}")
    
    # Third pass: copy triangles to separate files
    print(f"\n{'='*60}")
    print("SAVING PARTS:")
    print(f"{'='*60}\n")
    
    os.makedirs(output_dir, exist_ok=True)
    base_name = Path(input_file).stem
    
    # Open output files
    output_files = {}
    for region in ANATOMICAL_COLORS.keys():
        if region_counts.get(region, 0) > 0:
            filepath = os.path.join(output_dir, f"{base_name}_{region}.stl")
            output_files[region] = open(filepath, 'wb')
            
            # Write header
            header = f'Anatomical Part: {region}'.encode('ascii')
            header = header + b' ' * (80 - len(header))
            output_files[region].write(header[:80])
            
            # Write triangle count
            output_files[region].write(struct.pack('<I', region_counts[region]))
    
    # Copy triangles
    with open(input_file, 'rb') as f:
        f.read(80)
        f.read(4)
        
        for i in range(total_triangles):
            # Read triangle (50 bytes)
            triangle_data = f.read(50)
            
            # Write to appropriate file
            region = triangle_regions[i]
            if region in output_files:
                output_files[region].write(triangle_data)
            
            if (i+1) % 100000 == 0:
                print(f"  Progress: {i+1:,}/{total_triangles:,}")
    
    # Close all files
    metadata = {"parts": []}
    for region, fp in output_files.items():
        fp.close()
        filepath = os.path.join(output_dir, f"{base_name}_{region}.stl")
        color_key = ANATOMICAL_COLORS[region]
        color_info = COLORS[color_key]
        
        print(f"✅ {region:15s}: {filepath}")
        print(f"    └─ Color: {color_info['name']} {color_info['hex']}")
        
        metadata["parts"].append({
            "region": region,
            "filename": f"{base_name}_{region}.stl",
            "triangle_count": region_counts[region],
            "color": color_key,
            "hex": color_info['hex'],
            "color_name": color_info['name']
        })
    
    # Save metadata
    metadata_file = os.path.join(output_dir, f"{base_name}_color_map.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nMetadata: {metadata_file}")
    
    print(f"\n{'='*60}")
    print(f"✅ SPLITTING COMPLETE!")
    print(f"{'='*60}\n")
    
    return metadata

def main():
    if len(sys.argv) < 2:
        print("Usage: python anatomical_splitter_v2.py <input.stl> [output_dir]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "anatomical_parts_v2"
    
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    try:
        analyze_and_split(input_file, output_dir)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
