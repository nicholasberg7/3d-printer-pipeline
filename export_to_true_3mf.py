import os, json, zipfile
import numpy as np
import trimesh

MODEL   = os.path.expanduser('~/AI_PIPELINE/LOCKED_SPLIT_STAGE/lets try this!_repaired_preserve_01_armor_primary.stl')
ASSIGN  = os.path.expanduser('~/AI_PIPELINE/LOCKED_ASSIGN_STAGE/bambu_color_assignment.json')
OUTFILE = os.path.expanduser('~/AI_PIPELINE/LOCKED_ASSIGN_STAGE/lets_try_this_true.3mf')

# load mesh + optional color assignment metadata
mesh   = trimesh.load_mesh(MODEL, force='mesh')
assign = {}
if os.path.exists(ASSIGN):
    try:
        import json
        with open(ASSIGN) as f: assign = json.load(f)
    except Exception:
        assign = {}

# ensure triangles are indexed and vertices are float
mesh.remove_unreferenced_vertices()
V = mesh.vertices.astype(np.float64)
F = mesh.faces.astype(np.int64)

# build 3MF XML (vertices + triangles)
def vx(v): return f'<vertex x="{v[0]:.6f}" y="{v[1]:.6f}" z="{v[2]:.6f}"/>'
def tri(t): return f'<triangle v1="{int(t[0])}" v2="{int(t[1])}" v3="{int(t[2])}"/>'

verts_xml = "\n".join(vx(v) for v in V)
tris_xml  = "\n".join(tri(t) for t in F)

model_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US"
  xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
  <resources>
    <object id="1" type="model">
      <mesh>
        <vertices>
{verts_xml}
        </vertices>
        <triangles>
{tris_xml}
        </triangles>
      </mesh>
    </object>
  </resources>
  <build>
    <item objectid="1" name="{os.path.basename(MODEL)}"/>
  </build>
</model>
'''

content_types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels"  ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
  <Default Extension="json"  ContentType="application/json"/>
</Types>
'''

rels_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rel0"
    Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"
    Target="/3D/3dmodel.model"/>
</Relationships>
'''

with zipfile.ZipFile(OUTFILE, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', content_types)
    z.writestr('_rels/.rels', rels_xml)
    z.writestr('3D/3dmodel.model', model_xml)
    if assign:
        z.writestr('metadata/color_assignment.json', json.dumps(assign, indent=2))

print("Saved:", OUTFILE)
