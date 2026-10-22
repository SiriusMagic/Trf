"""Export a parametric patch-array concept as JSON and ASCII STL.
STL units are millimetres. This is a layout envelope, not fabrication-ready CAD.
"""
import json
from pathlib import Path
from .model import estimate_patch, array_positions


def geometry_spec(frequency_hz, eps_r, substrate_height_m, copper_thickness_m, rows, cols, spacing_m):
    p = estimate_patch(frequency_hz, eps_r, substrate_height_m)
    pos = array_positions(rows, cols, spacing_m, spacing_m)
    return {"status": "PARAMETRIC_CONCEPT_NOT_FABRICATION_VALIDATED", "units": "SI metres",
        "frequency_hz": frequency_hz,
        "substrate": {"relative_permittivity_nominal": eps_r, "thickness_m": substrate_height_m},
        "copper_thickness_m": copper_thickness_m,
        "patch_estimate": {"width_m": p.width_m, "length_m": p.length_m, "effective_permittivity": p.effective_permittivity},
        "array": {"rows": rows, "columns": cols, "elements": rows*cols, "plane": "X-Z", "boresight": "+Y", "spacing_m": spacing_m},
        "element_centres_xz_m": pos.tolist(),
        "limitations": ["No feed network or connector model", "No full-wave EM validation",
            "No verified Starlink compatibility", "Patch dimensions are closed-form estimates"]}


def export_json(spec, path):
    path = Path(path)
    path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return path


def _box_triangles(x0, x1, y0, y1, z0, z1):
    v = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
         (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    faces = [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
             (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    return [(v[a],v[b],v[c]) for a,b,c in faces]


def export_stl(spec, path):
    """Export simple boxes for ground, substrate and patch copper in millimetres."""
    rows, cols = spec["array"]["rows"], spec["array"]["columns"]
    spacing = spec["array"]["spacing_m"] * 1000
    w = spec["patch_estimate"]["width_m"] * 1000
    l = spec["patch_estimate"]["length_m"] * 1000
    h = spec["substrate"]["thickness_m"] * 1000
    cu = spec["copper_thickness_m"] * 1000
    centers = spec["element_centres_xz_m"]
    extent_x, extent_z = (cols-1)*spacing+w, (rows-1)*spacing+l
    margin = max(w, l)*0.25
    faces = _box_triangles(-extent_x/2-margin, extent_x/2+margin, -cu, 0, -extent_z/2-margin, extent_z/2+margin)
    faces += _box_triangles(-extent_x/2-margin, extent_x/2+margin, 0, h, -extent_z/2-margin, extent_z/2+margin)
    for xm, zm in centers:
        x, z = xm*1000, zm*1000
        faces += _box_triangles(x-w/2, x+w/2, h, h+cu, z-l/2, z+l/2)
    path = Path(path)
    with path.open("w", encoding="ascii") as f:
        f.write("solid AtlasRF_parametric_concept\n")
        for a,b,c in faces:
            f.write(" facet normal 0 0 0\n  outer loop\n")
            for x,y,z in (a,b,c):
                f.write(f"   vertex {x:.6f} {y:.6f} {z:.6f}\n")
            f.write("  endloop\n endfacet\n")
        f.write("endsolid AtlasRF_parametric_concept\n")
    return path
