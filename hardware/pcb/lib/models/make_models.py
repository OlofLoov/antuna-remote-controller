"""Write simple VRML bodies for parts whose vendor model is unusable, from
datasheet dimensions. KiCad reads VRML in units of 0.1 inch, x right,
y up the footprint (footprint y is down) and z up off the board.

  python3 hardware/pcb/lib/models/make_models.py

Vishay_TSMP96000TR.wrl: the TSMP96000 panhead, 7.5 W x 5.3 H x 4.0 D mm
(datasheet rev 1.1, document 82906), lens facing the footprint's +y.
LCSC's STEP for it places its geometry hundreds of mm off the part.

XKB_TS-1187A.wrl: 5.1 mm square, base 0.9 mm, cover to 1.2 mm, a 2.0 mm
stem to 1.7 mm (height code C), terminals on a 3.7 mm pitch (XKB drawing
TS-1187A-X-X-X rev A0).

Raytac_AN54LQ-15.wrl: 9.5 x 13.7 x 1.8 mm (datasheet v1.3), a shield
over all but the antenna end, which is the footprint's -y end.

LCSC's models for the switch and module state no license, and this repo
is public, so these stand in for them.
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
U = 1 / 2.54  # mm to VRML units


def box(cx, cy, cz, sx, sy, sz, color):
    return (f"Transform {{ translation {cx*U:.4f} {cy*U:.4f} {cz*U:.4f} children [ Shape {{ "
            f"appearance Appearance {{ material Material {{ diffuseColor {color} specularColor 0.3 0.3 0.3 shininess 0.4 }} }} "
            f"geometry Box {{ size {sx*U:.4f} {sy*U:.4f} {sz*U:.4f} }} }} ] }}\n")


def prism(centre, axis, r, length, color, sides=16):
    """A cylinder as faces, since KiCad's VRML reader skips Cylinder nodes.
    centre in mm; axis "y" or "z"; length along the axis."""
    import math
    cx, cy, cz = centre
    pts = []
    for end in (-length / 2, length / 2):
        for n in range(sides):
            a = 2 * math.pi * n / sides
            u, v = r * math.cos(a), r * math.sin(a)
            if axis == "z":
                pts.append((cx + u, cy + v, cz + end))
            else:
                pts.append((cx + u, cy + end, cz + v))
    faces = [list(range(sides))[::-1], list(range(sides, 2 * sides))]
    for n in range(sides):
        m = (n + 1) % sides
        faces.append([n, m, sides + m, sides + n])
    coords = ", ".join(f"{x*U:.4f} {y*U:.4f} {z*U:.4f}" for x, y, z in pts)
    index = ", ".join(" ".join(str(i) for i in f) + " -1" for f in faces)
    return (f"Shape {{ appearance Appearance {{ material Material {{ diffuseColor {color} "
            f"specularColor 0.5 0.5 0.5 shininess 0.6 }} }} geometry IndexedFaceSet {{ solid FALSE "
            f"coord Coordinate {{ point [ {coords} ] }} coordIndex [ {index} ] }} }}\n")


def ts1187a():
    base, steel, brass, tin = "0.12 0.12 0.13", "0.62 0.63 0.66", "0.85 0.68 0.3", "0.8 0.8 0.82"
    parts = [box(0, 0, 0.45, 5.1, 5.1, 0.9, base),
             box(0, 0, 1.05, 4.6, 4.6, 0.3, steel),
             prism((0, 0, 1.45), "z", 1.0, 0.5, brass)]
    for x in (-3.0, 3.0):
        for y in (-1.85, 1.85):
            parts.append(box(x, y, 0.15, 1.0, 0.5, 0.3, tin))
    return "#VRML V2.0 utf8\n" + "".join(parts)


def an54lq():
    board, shield, chip = "0.1 0.45 0.2", "0.78 0.79 0.8", "0.15 0.15 0.15"
    # Footprint y -6.97 (antenna end) .. 6.78, so model y -6.78 .. 6.97.
    parts = [box(0, 0.095, 0.4, 9.5, 13.75, 0.8, board),
             box(0, -1.55, 1.3, 9.1, 10.05, 1.0, shield),
             box(0, 5.2, 1.0, 3.2, 1.6, 0.4, chip)]
    return "#VRML V2.0 utf8\n" + "".join(parts)


def tsmp96000():
    black, lens, tin = "0.08 0.08 0.09", "0.15 0.12 0.18", "0.8 0.8 0.82"
    # Footprint y -0.89..2.01 is the body, so model y -2.01..0.89.
    parts = [box(0, -0.56, 2.65, 7.5, 2.9, 5.3, black)]
    parts.append(prism((0, -2.56, 3.0), "y", 1.7, 1.1, lens))
    for x in (-1.9, -0.63, 0.63, 1.9):
        parts.append(box(x, 0.0, 0.1, 0.5, 1.6, 0.2, tin))
    return "#VRML V2.0 utf8\n" + "".join(parts)


MODELS = {
    "Vishay_TSMP96000TR.wrl": tsmp96000,
    "XKB_TS-1187A.wrl": ts1187a,
    "Raytac_AN54LQ-15.wrl": an54lq,
}

if __name__ == "__main__":
    for name, make in MODELS.items():
        path = os.path.join(HERE, name)
        with open(path, "w") as f:
            f.write(make())
        print("wrote", os.path.relpath(path))
