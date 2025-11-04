import os, trimesh

INPUT_DIR  = os.path.expanduser('~/AI_PIPELINE/INPUT')
OUTPUT_DIR = os.path.expanduser('~/AI_PIPELINE/REPAIRED')
os.makedirs(OUTPUT_DIR, exist_ok=True)

for name in os.listdir(INPUT_DIR):
    if not name.lower().endswith('.stl'):
        continue

    path = os.path.join(INPUT_DIR, name)
    print(f"\nRepairing {name}")
    mesh = trimesh.load_mesh(path)

    # --- Basic cleanup ---
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fill_holes(mesh)

    # --- Boundary check (safe for all trimesh versions) ---
    try:
        if hasattr(mesh, "edges_unique_boundary"):
            open_edges = len(mesh.edges_unique_boundary)
        elif hasattr(mesh, "facets_boundary"):
            open_edges = len(mesh.facets_boundary)
        else:
            open_edges = 0
    except Exception:
        open_edges = 0

    # --- Stitch attempt ---
    if open_edges > 0:
        try:
            trimesh.repair.stitch(mesh)
            print(f"  Stitched {open_edges} open edges.")
        except Exception as e:
            print("  Stitch skipped:", e)
    else:
        print("  No open edges to stitch.")

    # --- Final report ---
    print("  Watertight:", mesh.is_watertight)
    out_path = os.path.join(
        OUTPUT_DIR, f"{os.path.splitext(name)[0]}_repaired_preserve.stl"
    )
    mesh.export(out_path)
    print("  Saved:", out_path)
