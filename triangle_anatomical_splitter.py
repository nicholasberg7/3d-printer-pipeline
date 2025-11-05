#!/usr/bin/env python3
"""
Triangle-Based Anatomical Splitter
Splits SINGLE model by analyzing WHERE each triangle is located anatomically
"""

import sys
import os
import json
import trimesh
import numpy as np
from pathlib import Path

def load_color_config(config_path):
    """Load the 8-region color configuration"""
    import configparser
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

def analyze_triangle_anatomy(mesh, color_map):
    """Analyze each triangle and assign to anatomical region based on 3D position"""
    
    print(f"\n{'='*60}")
    print("🧠 TRIANGLE-BASED ANATOMICAL ANALYSIS")
    print(f"{'='*60}\n")
    
    regions = list(color_map.keys())
    print(f"📊 Analyzing {len(mesh.faces):,} triangles for anatomical regions...")
    
    # Calculate triangle centers
    triangle_centers = []
    for i, face in enumerate(mesh.faces):
        vertices = mesh.vertices[face]
        center = vertices.mean(axis=0)
        triangle_centers.append(center)
        
        if (i + 1) % 100000 == 0:
            print(f"   Progress: {i+1:,}/{len(mesh.faces):,}")
    
    triangle_centers = np.array(triangle_centers)
    
    # Get model bounds
    bounds = mesh.bounds
    x_range = bounds[1][0] - bounds[0][0]
    y_range = bounds[1][1] - bounds[0][1]
    z_range = bounds[1][2] - bounds[0][2]
    
    print(f"\n📐 Model bounds:")
    print(f"   X: {bounds[0][0]:.1f} to {bounds[1][0]:.1f} (range: {x_range:.1f})")
    print(f"   Y: {bounds[0][1]:.1f} to {bounds[1][1]:.1f} (range: {y_range:.1f})")
    print(f"   Z: {bounds[0][2]:.1f} to {bounds[1][2]:.1f} (range: {z_range:.1f})")
    
    # Calculate relative positions (0-1)
    rel_x = (triangle_centers[:, 0] - bounds[0][0]) / x_range
    rel_y = (triangle_centers[:, 1] - bounds[0][1]) / y_range
    rel_z = (triangle_centers[:, 2] - bounds[0][2]) / z_range
    
    print(f"\n🎯 Assigning triangles to anatomical regions...")
    
    # Initialize assignments
    triangle_assignments = np.full(len(triangle_centers), -1, dtype=int)
    
    # ANATOMICAL ASSIGNMENT RULES
    for i in range(len(triangle_centers)):
        x_pct, y_pct, z_pct = rel_x[i], rel_y[i], rel_z[i]
        
        # HEAD/HELMET: Top 20% of model
        if z_pct > 0.80:
            if y_pct > 0.6:  # Front face area
                triangle_assignments[i] = regions.index('optics') if 'optics' in regions else 0
            else:  # Helmet/back of head
                triangle_assignments[i] = regions.index('armor_primary') if 'armor_primary' in regions else 0
        
        # UPPER TORSO/CHEST: Upper center (60-80% height)
        elif 0.60 < z_pct <= 0.80 and 0.25 < x_pct < 0.75:
            triangle_assignments[i] = regions.index('armor_primary') if 'armor_primary' in regions else 0
        
        # ARMS/SHOULDERS: Upper sides (50-80% height, outer edges)
        elif 0.50 < z_pct <= 0.80 and (x_pct <= 0.25 or x_pct >= 0.75):
            triangle_assignments[i] = regions.index('armor_highlight') if 'armor_highlight' in regions else 1
        
        # MID TORSO/FRAME: Middle section (40-60% height)
        elif 0.40 < z_pct <= 0.60:
            if 0.2 < x_pct < 0.8:  # Central area
                triangle_assignments[i] = regions.index('frame') if 'frame' in regions else 2
            else:  # Side areas
                triangle_assignments[i] = regions.index('armor_highlight') if 'armor_highlight' in regions else 1
        
        # JOINTS/WAIST: Transition area (25-40% height)
        elif 0.25 < z_pct <= 0.40:
            triangle_assignments[i] = regions.index('joint_shadow') if 'joint_shadow' in regions else 3
        
        # UPPER LEGS: Lower body (15-25% height)
        elif 0.15 < z_pct <= 0.25:
            triangle_assignments[i] = regions.index('armor_highlight') if 'armor_highlight' in regions else 1
        
        # LOWER LEGS/FEET: Bottom section (0-15% height)
        elif z_pct <= 0.15:
            if z_pct < 0.05:  # Very bottom - feet
                triangle_assignments[i] = regions.index('accent') if 'accent' in regions else 7
            else:  # Lower legs
                triangle_assignments[i] = regions.index('armor_primary') if 'armor_primary' in regions else 0
        
        # EDGE DETAILS: Very edges of model
        elif x_pct < 0.05 or x_pct > 0.95 or y_pct < 0.05 or y_pct > 0.95:
            triangle_assignments[i] = regions.index('metal_light') if 'metal_light' in regions else 5
        
        # DEFAULT: Small details
        else:
            triangle_assignments[i] = regions.index('accent') if 'accent' in regions else 7
    
    # Count assignments
    assignment_counts = {}
    for region_idx in triangle_assignments:
        if region_idx >= 0:
            region_name = regions[region_idx]
            assignment_counts[region_name] = assignment_counts.get(region_name, 0) + 1
    
    print(f"\n📊 Anatomical assignment results:")
    total_assigned = sum(assignment_counts.values())
    for region in regions:
        count = assignment_counts.get(region, 0)
        pct = (count / len(triangle_centers)) * 100
        color_info = color_map[region]
        print(f"   • {region:15s}: {count:8,} triangles ({pct:5.1f}%) → {color_info['label']} {color_info['hex']}")
    
    print(f"\nTotal assigned: {total_assigned:,} / {len(triangle_centers):,} triangles")
    
    return triangle_assignments

def save_anatomical_regions(mesh, triangle_assignments, color_map, input_file, output_dir):
    """Save each anatomical region as separate STL"""
    
    os.makedirs(output_dir, exist_ok=True)
    base_name = Path(input_file).stem
    regions = list(color_map.keys())
    
    print(f"\n{'='*60}")
    print("SAVING ANATOMICAL REGIONS:")
    print(f"{'='*60}\n")
    
    output_files = []
    metadata = {
        "original_file": input_file,
        "total_triangles": len(mesh.faces),
        "assignment_method": "triangle_anatomical_analysis",
        "regions": []
    }
    
    # Save each region
    for region_idx, region in enumerate(regions):
        # Find triangles assigned to this region
        region_mask = triangle_assignments == region_idx
        region_triangle_count = np.sum(region_mask)
        
        if region_triangle_count == 0:
            print(f"⚠️  {region:15s}: No triangles assigned, skipping")
            continue
        
        # Extract faces for this region
        region_faces = mesh.faces[region_mask]
        
        # Create new mesh with only these faces
        used_vertices = np.unique(region_faces.flatten())
        vertex_map = {old_idx: new_idx for new_idx, old_idx in enumerate(used_vertices)}
        
        new_vertices = mesh.vertices[used_vertices]
        new_faces = np.array([[vertex_map[v] for v in face] for face in region_faces])
        
        region_mesh = trimesh.Trimesh(vertices=new_vertices, faces=new_faces)
        
        # Save STL
        color_info = color_map[region]
        output_file = os.path.join(output_dir, f"{base_name}_{region}.stl")
        region_mesh.export(output_file)
        
        print(f"✅ {region:15s}: {output_file}")
        print(f"    └─ Color: {color_info['label']} {color_info['hex']} - {color_info['use']}")
        print(f"    └─ Triangles: {region_triangle_count:,}")
        
        output_files.append(output_file)
        metadata["regions"].append({
            "region": region,
            "filename": f"{base_name}_{region}.stl",
            "triangle_count": int(region_triangle_count),
            "hex": color_info['hex'],
            "label": color_info['label'],
            "use": color_info['use']
        })
    
    # Save metadata
    metadata_file = os.path.join(output_dir, f"{base_name}_anatomical_map.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\nMetadata: {metadata_file}")
    
    print(f"\n{'='*60}")
    print(f"✅ ANATOMICAL SPLITTING COMPLETE!")
    print(f"{'='*60}\n")
    
    return output_files, metadata

def main():
    if len(sys.argv) < 2:
        print("Usage: python triangle_anatomical_splitter.py <input.stl> [output_dir] [config_file]")
        print("\nSplits a SINGLE model into anatomical regions by triangle position analysis.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "ANATOMICAL_REGIONS"
    config_file = sys.argv[3] if len(sys.argv) > 3 else "color_map_config.txt"
    
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    if not os.path.exists(config_file):
        print(f"Error: Config file not found: {config_file}")
        sys.exit(1)
    
    try:
        # Load mesh and color config
        print(f"Loading: {input_file}")
        mesh = trimesh.load_mesh(input_file)
        color_map = load_color_config(config_file)
        
        print(f"✅ Loaded SINGLE mesh with {len(mesh.faces):,} triangles")
        print(f"✅ Will split into {len(color_map)} anatomical regions")
        
        # Anatomical triangle analysis
        triangle_assignments = analyze_triangle_anatomy(mesh, color_map)
        
        # Save anatomical regions
        save_anatomical_regions(mesh, triangle_assignments, color_map, input_file, output_dir)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
