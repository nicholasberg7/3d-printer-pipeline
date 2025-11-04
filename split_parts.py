import trimesh, os, itertools, configparser

INPUT  = os.path.expanduser('~/AI_PIPELINE/LOCKED_REPAIR_STAGE/lets try this!_repaired_preserve.stl')
CFG    = os.path.expanduser('~/AI_PIPELINE/CONFIG/color_map.cfg')
OUTPUT = os.path.expanduser('~/AI_PIPELINE/SPLIT_PARTS')
os.makedirs(OUTPUT, exist_ok=True)

# ---- Load color map ----
cfg = configparser.ConfigParser()
cfg.read(CFG)
palette = [s for s in cfg.sections()] or ["part"]

print(f"Loaded {len(palette)} color labels from config.")

# ---- Load the repaired STL ----
mesh = trimesh.load_mesh(INPUT)
print("Loaded mesh:", INPUT)
print("Watertight:", mesh.is_watertight)

# ---- Split by connected components ----
print("Splitting mesh into connected parts...")
parts = mesh.split(only_watertight=False)
print(f"Found {len(parts)} separate parts.")

# ---- Export each part with color-map name ----
for idx, part in enumerate(parts):
    label = palette[idx % len(palette)]
    out_name = f"{os.path.splitext(os.path.basename(INPUT))[0]}_{idx+1:02d}_{label}.stl"
    out_path = os.path.join(OUTPUT, out_name)
    part.export(out_path)
    print("  Saved:", out_name)

print("\nAll parts exported to:", OUTPUT)
