import json, os
INPUT  = os.path.expanduser('~/AI_PIPELINE/LOCKED_SPLIT_STAGE/lets try this!_repaired_preserve_01_armor_primary.stl')
PAINTS = os.path.expanduser('~/AI_PIPELINE/LOCKED_COLOR_STAGE/bambu_paintgroups.json')
OUTPUT = os.path.expanduser('~/AI_PIPELINE/CONFIG/bambu_color_assignment.json')

# load colors
data = json.load(open(PAINTS))
materials = data["materials"]

# build assignment skeleton
assignments = {
    "model": os.path.basename(INPUT),
    "groups": [
        {"part": 1, "material": m["name"], "hex": m["hex"]}
        for m in materials
    ]
}

# save
with open(OUTPUT, "w") as f:
    json.dump(assignments, f, indent=2)
print("Saved:", OUTPUT)
