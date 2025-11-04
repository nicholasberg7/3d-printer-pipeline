import trimesh, os

INPUT_DIR = os.path.expanduser('~/AI_PIPELINE/INPUT')

for file in os.listdir(INPUT_DIR):
    if file.lower().endswith('.stl'):
        path = os.path.join(INPUT_DIR, file)
        mesh = trimesh.load_mesh(path)
        print(f"\nAnalyzing {file}")
        print("  Triangles:", len(mesh.faces))
        print("  Vertices :", len(mesh.vertices))
        print("  Watertight:", mesh.is_watertight)
        print("  Bounds (mm):", mesh.extents.round(2).tolist())
        print("  Volume (mm³):", round(mesh.volume, 2))
