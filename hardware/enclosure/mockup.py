"""Shell prototype of the Antuna Remote: three printed parts that screw
together around the board, to judge the grip, the joint and the battery door.

    scripts/build-mockup.sh            # writes hardware/enclosure/out/

- front: the key face, the head and the side walls down to the board's top.
  The keys are bumps on it, not moving caps.
- back: the rest of the body, with a pocket for the board, a bay for two
  AAA cells and six counterbored holes for M2 x 5 self-tapping screws.
- door: the battery door. Two tabs hook in at the bottom end and a sprung
  bar snaps in at the other.

Each part prints flat on the bed with its outside up and no supports. The
bay is 45 mm long so bare cells sit still; the real bay is longer and has
spring contacts.

Shape and sizes are openspec/changes/define-keys-and-layout/design.md,
decisions 1, 2, 3, 10, 11 and 12. Key and screw positions come from the
board, in shell coordinates (x from the left, y from the top, in mm).
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
BODY = 9.0             # thickness over the keys, front face at z = 0
BATTERY = 14.0         # thickness at the battery end
SWELL = (64.0, 96.0)   # the back swells from BODY to BATTERY between these
HEAD_RISE = 4.2        # the head stands this far above the key face
HEAD_END, HEAD_SLOPE = 16.0, 4.5     # head is flat to 16 mm, down to the key face at 20.5
SHOULDER = 6.0         # rounding of the back's edges, the part the palm holds
FRONT_EDGE = 1.5       # rounding of the front's edges
CAP = 1.5              # key bumps stand this far above the key face
WALL = 1.6             # side walls
FACE = 1.2             # front wall, over the switches

# Inside, from the key face down: front wall, 0.3 mm clear, the 1.7 mm
# switches, then the board. The two halves meet at the board's top.
SPLIT = -(FACE + 0.3 + 1.7)
BOARD = 1.0
BOARD_GAP = 0.2        # around the board's edge
BOARD_END = 100.0      # the board's bottom edge
RIB = 0.5              # the board rests this far off the back's floor
LEDGE = 0.8            # width of the step the board's edge rests on
BACK_WALL = 2.0        # back wall under the board
POST = 6.0             # screw posts in the back half
RIBS_Y = (30.0, 42.0, 54.0, 66.0, 78.0, 90.0)

# M2 x 5 self-tapping screws from the back: 1.5 mm under the head, through
# the board, 2.5 mm into a boss in the front half.
SCREW_SEAT = SPLIT - BOARD - 1.5
SCREW_CLEAR, SCREW_HEAD, SCREW_PILOT, BOSS = 2.3, 4.2, 1.7, 4.6
BOARD_SCREWS = [(35.0, 25.0), (5.0, 52.0), (35.0, 68.0), (5.0, 82.0)]   # HOLES in build_board.py
END_SCREWS = [(4.6, 143.0), (35.4, 143.0)]

# The IR parts' axes are 3 mm above the board.
IR_Z = SPLIT + 3.0
# The placement file gives D1's pad 1; its lens axis is one lead away.
IR_LED_AXIS = -1.27
IR_HOLES = {"D1": 6.0, "U2": 4.5}

CELL_D, CELL_L = 10.5, 44.5
CELL_PITCH = 11.5
BAY_Y = (101.5, 146.5)
BAY_W = CELL_PITCH + CELL_D + 0.8
DOOR = 1.6             # door thickness, flush with the back
DOOR_X = (7.6, 32.4)
DOOR_Y = (100.0, 147.5)
FIT = 0.2              # gap around the door
SPRING = 1.1           # the sprung bar at the door's top edge
NOSE = 0.4             # radius of the bar's snap, half of it stands out


def at(x, y, z=0.0):
    """Shell coordinates to model space: y runs down the remote."""
    return Pos(x, -y, z)


def rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def by_ref(path):
    return {row["Ref"]: (float(row["PosX"]), -float(row["PosY"])) for row in rows(path)}


def by_value(path):
    return {row["Val"]: (float(row["PosX"]), -float(row["PosY"])) for row in rows(path)}


def box(x, y, z):
    """A box from (x0, x1), (y0, y1) in shell coordinates and (z0, z1)."""
    return at(x[0], y[0], z[0]) * Box(x[1] - x[0], y[1] - y[0], z[1] - z[0],
                                       align=(Align.MIN, Align.MAX, Align.MIN))


def column(inset=0.0):
    """The front outline, moved inset mm inwards, as a tall prism."""
    with BuildSketch() as outline:
        RectangleRounded(WIDTH - 2 * inset, LENGTH - 2 * inset, CORNER - inset)
    return at(WIDTH / 2, LENGTH / 2) * extrude(outline.sketch, amount=40, both=True)


def slab(front=True, back=True):
    """The side profile swept across the width. With front or back off,
    that face is left far away."""
    far = 30.0
    top = [(-5, HEAD_RISE), (HEAD_END, HEAD_RISE), (HEAD_END + HEAD_SLOPE, 0), (LENGTH + 5, 0)]
    bottom = [(LENGTH + 5, -BATTERY), (SWELL[1], -BATTERY), (SWELL[0], -BODY), (-5, -BODY)]
    if not front:
        top = [(-5, far), (LENGTH + 5, far)]
    if not back:
        bottom = [(LENGTH + 5, -far), (-5, -far)]
    # Drawn with x down the remote and y to the front, then stood on the
    # plane x = 0 and swept across the width.
    face = Polygon(*top, *bottom, align=None)

    def corners(points):
        return [v for v in face.vertices()
                if any(abs(v.X - x) < 1e-6 and abs(v.Y - y) < 1e-6 for x, y in points)]

    if front:
        face = fillet(corners(top[1:3]), 3.0)
    if back:
        face = fillet(corners(bottom[1:3]), 40.0)
    side = Plane(origin=(0, 0, 0), x_dir=(0, -1, 0), z_dir=(-1, 0, 0))
    solid = side.location * extrude(face, amount=WIDTH + 10)
    return Pos(-solid.bounding_box().min.X - 5, 0, 0) * solid


def body():
    """The outside: the outline cut to the side profile, edges rounded."""
    solid = column() & slab()
    back = [e for e in solid.edges() if e.bounding_box().max.Z < -BODY + 0.01]
    solid = fillet(back, SHOULDER)
    front = [e for e in solid.edges() if e.bounding_box().min.Z > -0.01]
    return fillet(front, FRONT_EDGE)


def cap(shape):
    """A key bump: the sketch pushed up from just under the key face."""
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


def rod(x, y, z0, z1, dia):
    return at(x, y, z0) * Cylinder(dia / 2, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def front_part(shell, pos, ref):
    half = Box(200, 400, 100, align=(Align.CENTER, Align.CENTER, Align.MIN))
    front = shell & (Pos(0, 0, SPLIT) * half)
    # Hollow, with the front wall following the head.
    room = column(WALL) & (Pos(0, 0, -FACE) * slab(back=False)) & (Pos(0, 0, SPLIT - 1) * half)
    # Power's recess is a cup that reaches down into the room.
    cup = rod(*pos["Power"], -FACE, HEAD_RISE, 9.4)
    room -= cup
    # The cup's floor runs on to the side wall and to the front wall below
    # the head, so it does not start in mid-air on the printer. The IR LED
    # lies to its left, so it cannot reach that wall.
    px, py = pos["Power"]
    room -= box((px - 4.7, WIDTH), (py - 4.7, HEAD_END + HEAD_SLOPE + 1), (-FACE, 0))
    for x, y in BOARD_SCREWS + END_SCREWS:
        room -= rod(x, y, SPLIT, 0, BOSS)
    front -= room
    front -= rod(*pos["Power"], 0, HEAD_RISE + 1, 7.6)
    # Status light: a dimple in the head.
    front -= at(*ref["D2"], HEAD_RISE) * Cylinder(1.0, 0.8)
    # IR openings through the top wall.
    for part, dia in IR_HOLES.items():
        x = ref[part][0] + (IR_LED_AXIS if part == "D1" else 0.0)
        front -= at(x, 0, IR_Z) * Rot(90, 0, 0) * Cylinder(dia / 2, 6.0)
    for key in keys(pos):
        front += key
    for x, y in BOARD_SCREWS + END_SCREWS:
        front -= rod(x, y, SPLIT - 1, SPLIT + 2.5, SCREW_PILOT)
    return front


def back_part(shell):
    half = Box(200, 400, 100, align=(Align.CENTER, Align.CENTER, Align.MIN))
    back = shell - (Pos(0, 0, SPLIT) * half)
    above_board_end = box((-5, WIDTH + 5), (-5, BOARD_END + BOARD_GAP), (-50, 50))
    # The board's pocket, then a shallower room under it. The step between
    # them and the ribs carry the board.
    back -= column(2.0 - BOARD_GAP) & above_board_end & box((-5, 45), (-5, 160), (SPLIT - BOARD, SPLIT + 1))
    floor = SPLIT - BOARD - RIB
    under = column(2.0 + LEDGE) & above_board_end & box((-5, 45), (-5, 160), (floor, SPLIT))
    # Hollow down to a wall of BACK_WALL. The ribs and the screw posts
    # stand on that wall and reach up to the board.
    under += (column(4.0) & (Pos(0, 0, BACK_WALL) * slab(front=False))
              & box((-5, 45), (-5, BOARD_END - 0.5), (-50, floor + 0.2)))
    for y in RIBS_Y:
        under -= box((0, WIDTH), (y - 0.6, y + 0.6), (-50, SPLIT - BOARD))
    for x, y in BOARD_SCREWS:
        under -= rod(x, y, -50, SPLIT - BOARD, POST)
    # The IR LED's clipped leads stick out under the board at the top end.
    under += column(2.0 + LEDGE) & box((-5, 45), (-5, 22), (floor - 1.2, SPLIT - BOARD))
    back -= under
    for x, y in BOARD_SCREWS + END_SCREWS:
        back -= rod(x, y, SCREW_SEAT, SPLIT + 1, SCREW_CLEAR)
        back -= rod(x, y, -BATTERY - 1, SCREW_SEAT, SCREW_HEAD)

    # Battery bay, open to the front half and to the door.
    ledge = -BATTERY + DOOR
    mid = WIDTH / 2
    back -= box((mid - BAY_W / 2, mid + BAY_W / 2), BAY_Y, (ledge - 1, SPLIT + 1))
    back -= box(DOOR_X, DOOR_Y, (-BATTERY - 1, ledge))
    for x0, x1 in door_tabs():
        back -= box((x0 - FIT, x1 + FIT), (DOOR_Y[1] - 1, DOOR_Y[1] + 1.5), (ledge - 1.0, ledge))
    # The groove the door's snap sits in, and two slots for a fingernail
    # to get under the door's edge beside it.
    back -= at(mid - 4.5, DOOR_Y[0], ledge - NOSE) * Rot(0, 90, 0) * Cylinder(
        NOSE + 0.15, 9.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for x0 in (mid - 10.5, mid + 5.5):
        back -= box((x0, x0 + 5.0), (DOOR_Y[0] - 2.5, DOOR_Y[0] + 0.1), (-BATTERY - 1, ledge + 0.5))
    return back


def door_tabs():
    mid = WIDTH / 2
    return [(mid - 8.0, mid - 3.0), (mid + 3.0, mid + 8.0)]


def door_part():
    ledge = -BATTERY + DOOR
    mid = WIDTH / 2
    top = DOOR_Y[0] + FIT
    door = box((DOOR_X[0] + FIT, DOOR_X[1] - FIT), (top, DOOR_Y[1] - FIT), (-BATTERY, ledge))
    for x0, x1 in door_tabs():
        door += box((x0, x1), (DOOR_Y[1] - FIT - 0.1, DOOR_Y[1] + 1.2), (ledge - 0.8, ledge))
    # A slot leaves a bar along the top edge that bends back as the snap
    # passes the shell's edge.
    door -= box((mid - 11.0, mid + 11.0), (top + SPRING, top + SPRING + 1.0), (-BATTERY - 1, ledge + 1))
    door += at(mid - 4.0, top, ledge - NOSE) * Rot(0, 90, 0) * Cylinder(
        NOSE, 8.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return door


def build(placement):
    pos, ref = by_value(placement), by_ref(placement)
    shell = body()
    return front_part(shell, pos, ref), back_part(shell), door_part()


def on_bed(front, back, door):
    """The parts as they print: outside up, side by side."""
    front = Pos(0, 0, -SPLIT) * front
    back = Pos(2 * WIDTH + 10, 0, SPLIT) * Rot(0, 180, 0) * back
    door = Pos(3 * WIDTH + 20, 0, -BATTERY + DOOR) * Rot(0, 180, 0) * door
    return front, back, door


def main():
    placement, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for name, part in zip(("front", "back", "door"), on_bed(*build(placement))):
        export_stl(part, str(out / f"mockup-{name}.stl"), tolerance=0.02, angular_tolerance=0.1)
        export_step(part, str(out / f"mockup-{name}.step"))
        size = part.bounding_box()
        print(f"{name}: {size.size.X:.1f} x {size.size.Y:.1f} x {size.size.Z:.1f} mm, "
              f"{part.volume / 1000:.1f} cm3, {len(part.solids())} solid, bed face at z = {size.min.Z:.2f}")
    print(f"wrote {out}/mockup-front, -back and -door, as .step and .stl")


if __name__ == "__main__":
    main()
