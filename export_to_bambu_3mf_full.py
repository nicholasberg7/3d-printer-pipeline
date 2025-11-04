import os, json, zipfile

MODEL   = os.path.expanduser('~/AI_PIPELINE/LOCKED_SPLIT_STAGE/lets try this!_repaired_preserve_01_armor_primary.stl')
ASSIGN  = os.path.expanduser('~/AI_PIPELINE/LOCKED_ASSIGN_STAGE/bambu_color_assignment.json')
OUTFILE = os.path.expanduser('~/AI_PIPELINE/LOCKED_ASSIGN_STAGE/lets_try_this_colored_FULL.3mf')

with open(ASSIGN) as f:
    assign = json.load(f)

with open(MODEL, 'rb') as meshfile, zipfile.ZipFile(OUTFILE, 'w') as z:
    # standard 3MF headers
    z.writestr('[Content_Types].xml',
        '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    # include real STL geometry
    z.write(MODEL, '3D/3dmodel.stl')
    # color metadata
    z.writestr('metadata/color_assignment.json', json.dumps(assign, indent=2))

print("Saved:", OUTFILE)
