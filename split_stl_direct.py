#!/usr/bin/env python3
"""
Direct STL Splitter - Copy triangle bytes directly
"""

import sys
import struct

def split_stl_by_indices(input_file, output_file, triangle_indices):
    """Copy specific triangles by index from input to output"""
    
    # Sort indices for efficient reading
    sorted_indices = sorted(triangle_indices)
    
    with open(input_file, 'rb') as inf, open(output_file, 'wb') as outf:
        # Read and skip input header
        inf.read(80)
        total_triangles = struct.unpack('<I', inf.read(4))[0]
        
        # Write output header
        header = b'STL Direct Copy - Anatomical Split' + b' ' * 46
        outf.write(header[:80])
        outf.write(struct.pack('<I', len(sorted_indices)))
        
        # Read and copy selected triangles
        current_idx = 0
        next_target = 0
        
        for idx in range(total_triangles):
            # Each triangle is 50 bytes (12+12+12+12+2)
            triangle_data = inf.read(50)
            
            if next_target < len(sorted_indices) and idx == sorted_indices[next_target]:
                # This triangle should be included
                outf.write(triangle_data)
                next_target += 1
            
            # Progress
            if idx % 100000 == 0:
                print(f"  Progress: {idx:,}/{total_triangles:,}")
        
        print(f"✅ Copied {len(sorted_indices):,} triangles")

# Quick test
if __name__ == "__main__":
    print("Testing direct copy...")
    
    # Copy first 1000 triangles
    test_indices = set(range(1000))
    split_stl_by_indices("/tmp/3D/3dmodel.stl", "test_direct.stl", test_indices)
    
    # Verify
    with open("test_direct.stl", 'rb') as f:
        f.read(80)
        count = struct.unpack('<I', f.read(4))[0]
        print(f"Verification: {count} triangles")
        
        normal = struct.unpack('<fff', f.read(12))
        v1 = struct.unpack('<fff', f.read(12))
        v2 = struct.unpack('<fff', f.read(12))
        v3 = struct.unpack('<fff', f.read(12))
        
        print(f"First vertex: {v1}")
        print(f"Valid: {100 < v1[0] < 150}")
