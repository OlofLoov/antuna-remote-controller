"""Grip mock-up of the Antuna Remote: the outer shape with key bumps, to
print and hold. Not the enclosure: no board, no switches, no battery door.

    scripts/build-mockup.sh            # writes hardware/enclosure/out/

It prints as two parts, each flat on the bed with no supports: the back
(body and battery bulge) and the front (key face, head and keys). Two AAA
cells go in the back's pockets before the parts are joined, so the mock-up
weighs and balances like the remote. Four bits of 1.75 mm filament in the
2 mm holes line the parts up; glue or tape holds them.

Shape and sizes are openspec/changes/define-keys-and-layout/design.md,
decisions 1, 2, 3 and 12. Key positions come from the board's placement
file, in shell coordinates (x from the left, y from the top, in mm).
"""

import csv
import sys
from pathlib import Path

from build123d import (
    Align, Axis, Box, BuildSketch, Circle, Cylinder,
    Plane, Polygon, Pos, RectangleRounded, Rot, export_step,
    export_stl, extrude, fillet,
)

WIDTH, LENGTH = 40.0, 154.0
CORNER = 11.0          # front view, all four corners
END_R = 3.0            # side view, both ends
BODY = 5.9             # thickness over the keys, front face at z = 0
HEAD_RISE = 4.2        # the head stands this far above the key face
HEAD_END, HEAD_SLOPE = 16.0, 3.0     # head is flat to 16 mm, down to the key face at 19
BULGE_START, BULGE_SLOPE = 96.0, 5.0  # the back slopes out from 96 to 101 mm
BATTERY = 13.5         # thickness at the battery end
CAP = 1.5              # caps stand this far above the key face
SPLIT = -1.2           # the front part is the 1.2 mm front wall and what is on it
EDGES = (2.0, 1.5, 1.0)  # rounding of the outer edges, the largest that builds

# Board top above the back face (wall, ribs, board), and the IR parts' axes
# 3 mm above that.
IR_Z = -BODY + 1.2 + 0.5 + 1.0 + 3.0
# The placement file gives D1's pad 1; its lens axis is one lead away.
IR_LED_AXIS = -1.27
IR_HOLES = {"D1": 6.0, "U2": 4.5}

CELL_D, CELL_L = 10.5, 44.5
CELL_PITCH = 11.5
CELL_Y = 104.0         # top of the cells' pockets
PIN_D = 2.0
PINS = [(8.0, 10.0), (16.0, 6.0), (5.0, 143.0), (35.0, 143.0)]


def at(x, y, z=0.0):
    """Shell coordinates to model space: y runs down the remote."""
    return Pos(x, -y, z)


def by_ref(path):
    with open(path, newline="") as f:
        return {row["Ref"]: (float(row["PosX"]), -float(row["PosY"])) for row in csv.DictReader(f)}


def by_value(path):
    with open(path, newline="") as f:
        return {row["Val"]: (float(row["PosX"]), -float(row["PosY"])) for row in csv.DictReader(f)}


def body():
    """Side profile swept across the width, cut to the front outline."""
    profile = [
        (0, HEAD_RISE), (HEAD_END, HEAD_RISE), (HEAD_END + HEAD_SLOPE, 0), (LENGTH, 0),
        (LENGTH, -BATTERY), (BULGE_START + BULGE_SLOPE, -BATTERY), (BULGE_START, -BODY), (0, -BODY),
    ]
    # Drawn with x down the remote and y to the front, then stood on the
    # plane x = 0 and swept across the width.
    face = Polygon(*profile, align=None)

    def corners(points):
        return [v for v in face.vertices()
                if any(abs(v.X - x) < 1e-6 and abs(v.Y - y) < 1e-6 for x, y in points)]

    face = fillet(corners(profile[:1] + profile[3:5] + profile[7:]), END_R)
    face = fillet(corners(profile[1:3] + profile[5:7]), 2.0)
    side = Plane(origin=(0, 0, 0), x_dir=(0, -1, 0), z_dir=(-1, 0, 0))
    slab = side.location * extrude(face, amount=WIDTH)
    slab = Pos(-slab.bounding_box().min.X, 0, 0) * slab
    with BuildSketch() as outline:
        RectangleRounded(WIDTH, LENGTH, CORNER, align=(Align.MIN, Align.MAX))
    column = extrude(outline.sketch, amount=40, both=True)
    solid = slab & column
    for radius in EDGES:
        try:
            return fillet(solid.edges().filter_by(lambda e: e.length > 20), radius)
        except ValueError:
            continue
    print("edges left sharp", file=sys.stderr)
    return solid


def cap(shape):
    """A key cap: the sketch pushed up from just under the key face."""
    solid = extrude(shape, amount=CAP + 0.2)
    solid = fillet(solid.edges().group_by(Axis.Z)[-1], 0.4)
    return Pos(0, 0, -0.2) * solid


def keys(pos):
    parts = []
    ring_xy = [pos[k] for k in ("Up", "Down", "Left", "Right")]
    cx = sum(p[0] for p in ring_xy) / 4
    cy = sum(p[1] for p in ring_xy) / 4
    parts.append(at(cx, cy) * cap(Circle(15.0) - Circle(7.0)))
    parts.append(at(*pos["Select"]) * cap(Circle(6.6)))
    parts.append(at(*pos["Back"]) * cap(Circle(5.0)))
    parts.append(at(*pos["Home"]) * cap(RectangleRounded(10.0, 10.0, 3.0)))
    parts.append(at(*pos["Play"]) * cap(Circle(5.5)))
    parts.append(at(*pos["Mute"]) * cap(Circle(4.5)))
    up, dn = pos["Volup"], pos["Voldn"]
    parts.append(at((up[0] + dn[0]) / 2, (up[1] + dn[1]) / 2) * cap(RectangleRounded(9.0, 20.0, 4.4)))
    parts.append(at(*pos["Power"]) * cap(Circle(3.0)))
    return parts


def build(placement):
    pos, ref = by_value(placement), by_ref(placement)
    shell = body()
    # Power sits in a recess in the head, down to the key face.
    shell -= at(*pos["Power"]) * Cylinder(4.0, HEAD_RISE + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # Status light: a dimple in the head.
    shell -= at(*ref["D2"], HEAD_RISE) * Cylinder(1.0, 0.8)
    # IR openings in the top wall, 2 mm deep.
    for part, dia in IR_HOLES.items():
        x = ref[part][0] + (IR_LED_AXIS if part == "D1" else 0.0)
        shell -= at(x, 0, IR_Z) * Rot(90, 0, 0) * Cylinder(dia / 2, 4.0)
    for key in keys(pos):
        shell += key

    # Cut in two at the back of the front wall.
    half = Box(200, 400, 100, align=(Align.CENTER, Align.CENTER, Align.MIN))
    front = shell & (Pos(0, 0, SPLIT) * half)
    back = shell - (Pos(0, 0, SPLIT) * half)

    # Pockets for two real AAA cells, open to the split face.
    r = CELL_D / 2 + 0.2
    axis_z = SPLIT - 0.3 - CELL_D / 2
    for side in (-1, 1):
        x = WIDTH / 2 + side * CELL_PITCH / 2
        y = CELL_Y + (CELL_L + 1.0) / 2
        back -= at(x, y, axis_z) * Rot(90, 0, 0) * Cylinder(r, CELL_L + 1.0)
        back -= at(x, y, axis_z) * Box(2 * r, CELL_L + 1.0, 2 * (SPLIT - axis_z),
                                       align=(Align.CENTER, Align.CENTER, Align.MIN))
    # Holes for filament pins across the split.
    for x, y in PINS:
        back -= at(x, y, SPLIT) * Cylinder(PIN_D / 2, 8.0)
        front -= at(x, y, SPLIT) * Cylinder(PIN_D / 2, 6.0 if y < HEAD_END else 20.0)
    return front, back


def on_bed(front, back):
    """Both parts as they print: split face down, side by side."""
    front = Pos(0, 0, -SPLIT) * front
    back = Pos(2 * WIDTH + 10, 0, SPLIT) * Rot(0, 180, 0) * back
    return front, back


def main():
    placement, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    front, back = on_bed(*build(placement))
    for name, part in (("front", front), ("back", back)):
        export_stl(part, str(out / f"mockup-{name}.stl"), tolerance=0.02, angular_tolerance=0.1)
        export_step(part, str(out / f"mockup-{name}.step"))
        box = part.bounding_box()
        print(f"{name}: {box.size.X:.1f} x {box.size.Y:.1f} x {box.size.Z:.1f} mm, "
              f"{part.volume / 1000:.1f} cm3, bed face at z = {box.min.Z:.2f}")
    print(f"wrote {out}/mockup-front and mockup-back, as .step and .stl")

if __name__ == "__main__":
    main()
