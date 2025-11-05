#!/usr/bin/env python3
"""
Advanced Anatomical Color Splitter - Recreated from Terminal History
Splits STL by 8 anatomical regions with precise color mapping
"""

import sys
import os
import json
import configparser
import trimesh
import numpy as np
from pathlib import Path

def load_color_config(config_path):
    """Load the 8-region color configuration"""
    config = configparser.ConfigParser()
    config.read(config_path)
    
    color_map = {}
    for section in config.sections():
        color_map[section] = {
            'hex': config[section]['hex'],
            'label': config[section]['label'],
            'use': config[section]['use']
        }
    
    return color_map

def classify_triangle_advanced(vertices, bounds):
    """Classify triangle using the advanced 8-region system"""
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
    
    # Advanced 8-region classification
    
    # Helmet/Head: top 15%
    if z_pct > 0.85:
        return 'armor_primary'  # helmet
    
    # Optics/Eyes: upper front area
    if z_pct > 0.75 and y_pct > 0.6:
        return 'optics'  # eyes, sensors
    
    # Arms/Shoulders: upper sides
    if z_pct > 0.60 and (x_pct < 0.2 or x_pct > 0.8):
        return 'armor_highlight'  # arms, thighs, side panels
    
    # Chest/Torso: upper center
    if 0.45 < z_pct < 0.75 and 0.25 < x_pct < 0.75:
        return 'armor_primary'  # chest
    
    # Frame/Structure: middle sections
    if 0.30 < z_pct < 0.60:
        if 0.15 < x_pct < 0.85:
            return 'frame'  # ribs, inner limbs, spine
    
    # Joints: transition areas
    if 0.25 < z_pct < 0.45:
        return 'joint_shadow'  # elbows, knees, recesses
    
    # Metal details: edges and small features
    edge_threshold = 0.1
    if (x_pct < edge_threshold or x_pct > (1-edge_threshold) or
        z_pct < edge_threshold or z_pct > (1-edge_threshold)):
        return 'metal_light'  # edges, wear highlights
    
    # Lower extremities
    if z_pct < 0.25:
        return 'armor_highlight'  # legs
    
    # Default: accent details
    return 'accent'  # soles, gloves, trim

def split_by_advanced_anatomy(input_file, output_dir, config_path):
    """Main splitting function using advanced 8-region system"""
    print(f"\n{'='*60}")
    print(f"ADVANCED ANATOMICAL COLOR SPLITTER")
    print(f"{'='*60}\n")
    
    # Load color configuration
    color_map = load_color_config(config_path)
    print(f"Loaded {len(color_map)} color regions from config\n")
    
    # Load STL
    print(f"Loading: {input_file}")
    mesh = trimesh.load_mesh(input_file)
    print(f"Loaded mesh with {len(mesh.faces):,} triangles\n")
    
    # Get bounds
    bounds = {
        'x_min': mesh.bounds[0][0], 'x_max': mesh.bounds[1][0],
        'y_min': mesh.bounds[0][1], 'y_max': mesh.bounds[1][1],
        'z_min': mesh.bounds[0][2], 'z_max': mesh.bounds[1][2],
    }
    
    print("Model Bounds:")
    print(f"  X: {bounds['x_min']:.2f} to {bounds['x_max']:.2f}")
    print(f"  Y: {bounds['y_min']:.2f} to {bounds['y_max']:.2f}")
    print(f"  Z: {bounds['z_min']:.2f} to {bounds['z_max']:.2f}\n")
    
    # Classify all triangles
    print("Classifying triangles by advanced anatomy...")
    triangle_regions = []
    
    for i, face in enumerate(mesh.faces):
        vertices = mesh.vertices[face]
        region = classify_triangle_advanced(vertices, bounds)
        triangle_regions.append(region)
        
        if (i+1) % 50000 == 0:
            print(f"  Progress: {i+1:,}/{len(mesh.faces):,}")
    
    # Count triangles per region
    region_counts = {}
    for region in triangle_regions:
        region_counts[region] = region_counts.get(region, 0) + 1
    
    print(f"\n{'='*60}")
    print("ADVANCED PART BREAKDOWN:")
    print(f"{'='*60}")
    
    for region in color_map.keys():
        count = region_counts.get(region, 0)
        pct = (count / len(mesh.faces)) * 100
        color_info = color_map[region]
        print(f"  {region:15s}: {count:8,} triangles ({pct:5.1f}%) → {color_info['label']:15s} {color_info['hex']} - {color_info['use']}")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    base_name = Path(input_file).stem
    
    # Save each region as separate STL
    print(f"\n{'='*60}")
    print("SAVING ANATOMICAL PARTS:")
    print(f"{'='*60}\n")
    
    output_files = []
    metadata = {
        "original_file": input_file,
        "total_triangles": len(mesh.faces),
        "regions": []
    }
    
    for region in color_map.keys():
        if region_counts.get(region, 0) == 0:
            continue
            
        # Create mask for this region
        face_mask = np.array([triangle_regions[i] == region for i in range(len(mesh.faces))])
        
        if not face_mask.any():
            continue
            
        # Extract faces for this region
        region_faces = mesh.faces[face_mask]
        region_mesh = mesh.copy()
        region_mesh.update_faces(face_mask)
        
        # Save STL
        color_info = color_map[region]
        output_file = os.path.join(output_dir, f"{base_name}_{region}.stl")
        region_mesh.export(output_file)
        
        print(f"✅ {region:15s}: {output_file}")
        print(f"    └─ Color: {color_info['label']} {color_info['hex']} - {color_info['use']}")
        
        output_files.append(output_file)
        metadata["regions"].append({
            "region": region,
            "filename": f"{base_name}_{region}.stl",
            "triangle_count": region_counts[region],
            "hex": color_info['hex'],
            "label": color_info['label'],
            "use": color_info['use']
        })
    
    # Save metadata
    metadata_file = os.path.join(output_dir, f"{base_name}_advanced_color_map.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nMetadata: {metadata_file}")
    
    print(f"\n{'='*60}")
    print(f"✅ ADVANCED SPLITTING COMPLETE!")
    print(f"{'='*60}\n")
    
    return output_files, metadata

def main():
    if len(sys.argv) < 2:
        print("Usage: python advanced_color_splitter.py <input.stl> [output_dir] [config_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "ANATOMICAL_PARTS"
    config_file = sys.argv[3] if len(sys.argv) > 3 else "color_map_config.txt"
    
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    if not os.path.exists(config_file):
        print(f"Error: Config file not found: {config_file}")
        sys.exit(1)
    
    try:
        split_by_advanced_anatomy(input_file, output_dir, config_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
