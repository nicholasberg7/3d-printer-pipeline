#!/usr/bin/env python3
"""
Anatomical Color Splitter
Splits STL by body part regions and assigns colors
"""

import sys
import os
import json
import numpy as np
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
    'limbs': 'burnt_umber',      # Arms and legs (brown instead of blue)
    'helmet': 'burnt_umber',     # Helmet (brown instead of blue)
    'chest_body': 'gunmetal_gray',  # Chest and torso
    'hands_skull': 'light_silver',  # Hands and skull (white-ish)
    'detail': 'faded_black',     # Trim and details
    'accent': 'amber'            # Gold accents
}

def load_stl_binary(filepath):
    """Load binary STL file"""
    with open(filepath, 'rb') as f:
        f.read(80)  # Skip header
        num_triangles = np.frombuffer(f.read(4), dtype=np.uint32)[0]
        
        triangles = []
        for _ in range(num_triangles):
            normal = np.frombuffer(f.read(12), dtype=np.float32).copy()
            v1 = np.frombuffer(f.read(12), dtype=np.float32).copy()
            v2 = np.frombuffer(f.read(12), dtype=np.float32).copy()
            v3 = np.frombuffer(f.read(12), dtype=np.float32).copy()
            f.read(2)  # attribute
            
            triangles.append({
                'normal': normal,
                'vertices': (v1, v2, v3),  # Store as tuple
                'center': (v1 + v2 + v3) / 3.0
            })
    
    return triangles

def get_bounds(triangles):
    """Calculate model bounds"""
    all_verts = []
    for tri in triangles[:10000]:  # Sample for speed
        all_verts.extend(tri['vertices'])
    
    verts = np.array(all_verts)
    return {
        'x_min': verts[:,0].min(), 'x_max': verts[:,0].max(),
        'y_min': verts[:,1].min(), 'y_max': verts[:,1].max(),
        'z_min': verts[:,2].min(), 'z_max': verts[:,2].max(),
        'x_mid': (verts[:,0].min() + verts[:,0].max()) / 2,
        'y_mid': (verts[:,1].min() + verts[:,1].max()) / 2,
        'z_mid': (verts[:,2].min() + verts[:,2].max()) / 2,
    }

def classify_triangle_anatomical(tri, bounds):
    """Classify triangle by anatomical region"""
    center = tri['center']
    x, y, z = center[0], center[1], center[2]
    
    # Calculate relative positions
    z_range = bounds['z_max'] - bounds['z_min']
    x_range = bounds['x_max'] - bounds['x_min']
    y_range = bounds['y_max'] - bounds['y_min']
    
    z_pct = (z - bounds['z_min']) / z_range if z_range > 0 else 0
    x_pct = (x - bounds['x_min']) / x_range if x_range > 0 else 0
    y_pct = (y - bounds['y_min']) / y_range if y_range > 0 else 0
    
    # Helmet: top 20%
    if z_pct > 0.80:
        # Top front = skull/face detail
        if y_pct > 0.5:
            return 'hands_skull'  # Skull/face
        else:
            return 'helmet'  # Helmet
    
    # Hands: extreme top sides
    if z_pct > 0.75 and (x_pct < 0.15 or x_pct > 0.85):
        return 'hands_skull'
    
    # Chest/Body: middle 30-70% height, center mass
    if 0.30 < z_pct < 0.70 and 0.25 < x_pct < 0.75:
        return 'chest_body'
    
    # Limbs (arms/legs): sides and lower portions
    if x_pct < 0.25 or x_pct > 0.75:  # Sides = arms
        return 'limbs'
    
    if z_pct < 0.30:  # Lower = legs
        return 'limbs'
    
    # Detail/trim: edges and transitions
    # Check if near boundaries
    edge_threshold = 0.05
    if (x_pct < edge_threshold or x_pct > (1-edge_threshold) or
        z_pct < edge_threshold or z_pct > (1-edge_threshold)):
        return 'detail'
    
    # Default: accent/gold for anything else
    return 'accent'

def save_stl_binary(filepath, triangles):
    """Save triangles to binary STL file"""
    with open(filepath, 'wb') as f:
        # Header (80 bytes)
        header = b'Anatomical Part - Color Split' + b' ' * 50
        f.write(header[:80])
        
        # Number of triangles (4 bytes)
        f.write(np.uint32(len(triangles)).tobytes())
        
        # Write each triangle
        for tri in triangles:
            # Normal vector (12 bytes = 3 floats) - already float32
            f.write(tri['normal'].tobytes())
            
            # Three vertices (36 bytes = 9 floats) - already float32
            for vertex in tri['vertices']:
                f.write(vertex.tobytes())
            
            # Attribute byte count (2 bytes)
            f.write(np.uint16(0).tobytes())

def split_by_anatomy(input_file, output_dir):
    """Main splitting function"""
    print(f"\n{'='*60}")
    print(f"ANATOMICAL COLOR SPLITTER")
    print(f"{'='*60}\n")
    
    # Load STL
    print(f"Loading: {input_file}")
    triangles = load_stl_binary(input_file)
    print(f"Loaded {len(triangles):,} triangles\n")
    
    # Get bounds
    bounds = get_bounds(triangles)
    print("Model Bounds:")
    print(f"  X: {bounds['x_min']:.2f} to {bounds['x_max']:.2f}")
    print(f"  Y: {bounds['y_min']:.2f} to {bounds['y_max']:.2f}")
    print(f"  Z: {bounds['z_min']:.2f} to {bounds['z_max']:.2f}\n")
    
    # Classify all triangles
    print("Classifying triangles by anatomy...")
    parts = {key: [] for key in ANATOMICAL_COLORS.keys()}
    
    for i, tri in enumerate(triangles):
        region = classify_triangle_anatomical(tri, bounds)
        parts[region].append(tri)
        
        if (i+1) % 100000 == 0:
            print(f"  Progress: {i+1:,}/{len(triangles):,} triangles")
    
    print(f"\nClassification complete!")
    print(f"\n{'='*60}")
    print("PART BREAKDOWN:")
    print(f"{'='*60}")
    
    for region, tris in parts.items():
        color_key = ANATOMICAL_COLORS[region]
        color_info = COLORS[color_key]
        pct = (len(tris) / len(triangles)) * 100
        print(f"  {region:15s}: {len(tris):8,} triangles ({pct:5.1f}%) → {color_info['name']:12s} {color_info['hex']}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    base_name = Path(input_file).stem
    
    # Save each part
    print(f"\n{'='*60}")
    print("SAVING PARTS:")
    print(f"{'='*60}\n")
    
    output_files = []
    metadata = {
        "original_file": input_file,
        "total_triangles": len(triangles),
        "anatomical_mapping": ANATOMICAL_COLORS,
        "parts": []
    }
    
    for region, tris in parts.items():
        if not tris:
            print(f"⚠️  {region}: Skipping (no triangles)")
            continue
        
        color_key = ANATOMICAL_COLORS[region]
        color_info = COLORS[color_key]
        
        output_file = os.path.join(output_dir, f"{base_name}_{region}.stl")
        save_stl_binary(output_file, tris)
        
        print(f"✅ {region:15s}: {output_file}")
        print(f"    └─ Color: {color_info['name']} {color_info['hex']}")
        
        output_files.append(output_file)
        metadata["parts"].append({
            "region": region,
            "filename": os.path.basename(output_file),
            "triangle_count": len(tris),
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
    print(f"Parts saved to: {output_dir}/")
    print(f"Total files: {len(output_files)}")
    
    return output_files, metadata

def main():
    if len(sys.argv) < 2:
        print("Usage: python color_split_anatomical.py <input.stl> [output_dir]")
        print("\nAnatomical Color Mapping:")
        for region, color_key in ANATOMICAL_COLORS.items():
            color_info = COLORS[color_key]
            print(f"  {region:15s} → {color_info['name']:12s} {color_info['hex']}")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "anatomical_parts"
    
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    try:
        split_by_anatomy(input_file, output_dir)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
