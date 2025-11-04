import os, json, zipfile

MODEL   = os.path.expanduser('~/AI_PIPELINE/LOCKED_SPLIT_STAGE/lets try this!_repaired_preserve_01_armor_primary.stl')
ASSIGN  = os.path.expanduser('~/AI_PIPELINE/LOCKED_ASSIGN_STAGE/bambu_color_assignment.json')
OUTFILE = os.path.expanduser('~/AI_PIPELINE/LOCKED_ASSIGN_STAGE/lets_try_this_colored.3mf')

with open(ASSIGN) as f:
    assign = json.load(f)

# create minimal 3mf structure
with zipfile.ZipFile(OUTFILE, 'w') as z:
    z.writestr('[Content_Types].xml',
               '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    z.writestr('3D/3dmodel.model',
               f'<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources><object id="1" type="model"><mesh><vertices/><triangles/></mesh></object></resources><build><item objectid="1" name="{os.path.basename(MODEL)}"/></build></model>')
    z.writestr('metadata/color_assignment.json', json.dumps(assign, indent=2))

print("Saved:", OUTFILE)
