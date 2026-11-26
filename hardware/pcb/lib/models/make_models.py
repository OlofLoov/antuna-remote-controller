"""Write simple VRML bodies for parts whose vendor model is unusable, from
datasheet dimensions. KiCad reads VRML in units of 0.1 inch, x right,
y up the footprint (footprint y is down) and z up off the board.

  python3 hardware/pcb/lib/models/make_models.py

Vishay_TSMP96000TR.wrl: the TSMP96000 panhead, 7.5 W x 5.3 H x 4.0 D mm
(datasheet rev 1.1, document 82906), lens facing the footprint's +y.
LCSC's STEP for it places its geometry hundreds of mm off the part.
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
U = 1 / 2.54  # mm to VRML units


def box(cx, cy, cz, sx, sy, sz, color):
    return (f"Transform {{ translation {cx*U:.4f} {cy*U:.4f} {cz*U:.4f} children [ Shape {{ "
            f"appearance Appearance {{ material Material {{ diffuseColor {color} specularColor 0.3 0.3 0.3 shininess 0.4 }} }} "
            f"geometry Box {{ size {sx*U:.4f} {sy*U:.4f} {sz*U:.4f} }} }} ] }}\n")


def cylinder_y(cx, cy, cz, r, length, color):
    # VRML cylinders run along y already.
    return (f"Transform {{ translation {cx*U:.4f} {cy*U:.4f} {cz*U:.4f} children [ Shape {{ "
            f"appearance Appearance {{ material Material {{ diffuseColor {color} specularColor 0.5 0.5 0.5 shininess 0.7 }} }} "
            f"geometry Cylinder {{ radius {r*U:.4f} height {length*U:.4f} }} }} ] }}\n")


def tsmp96000():
    black, lens, tin = "0.08 0.08 0.09", "0.15 0.12 0.18", "0.8 0.8 0.82"
    # Footprint y -0.89..2.01 is the body, so model y -2.01..0.89.
    parts = [box(0, -0.56, 2.65, 7.5, 2.9, 5.3, black)]
    parts.append(cylinder_y(0, -2.56, 3.0, 1.7, 1.1, lens))
    for x in (-1.9, -0.63, 0.63, 1.9):
        parts.append(box(x, 0.0, 0.1, 0.5, 1.6, 0.2, tin))
    return "#VRML V2.0 utf8\n" + "".join(parts)


if __name__ == "__main__":
    path = os.path.join(HERE, "Vishay_TSMP96000TR.wrl")
    with open(path, "w") as f:
        f.write(tsmp96000())
    print("wrote", os.path.relpath(path))
