"""Check that the board fits the shell: no part of it may share space
with the front or the back half.

    scripts/build-mockup.sh            # runs this after building

The board comes from `kicad-cli pcb export step`. That export leaves out
the parts whose models are VRML, so the switches, the radio module and the
IR receiver are added here as boxes, with the sizes
hardware/pcb/lib/models/make_models.py draws them at.
"""

import sys
from pathlib import Path

from build123d import Align, Box, Compound, Pos, import_step

import mockup

# Size in x, y and z, and where the body's centre sits from the part's
# placement point in shell x and y, for the rotation each part has on the board.
BODIES = {
    "SW_Push_1P1T_XKB_TS-1187A": ((5.1, 5.1, 1.7), (0.0, 0.0)),
    "Raytac_AN54LQ-15": ((9.5, 13.75, 1.8), (0.0, -0.095)),
    "Vishay_TSMP96000TR": ((7.5, 2.9, 5.3), (0.0, -0.56)),
}
# Shared volume below this is the board's copper and mask touching the
# faces it rests on.
ALLOWED = 0.5  # mm3


def board(step, placement):
    """The board and its parts, with the board's top at the split."""
    shape = import_step(str(step))
    box = shape.bounding_box()
    # The export's z = 0 is the board's bottom face.
    parts = [Pos(0, 0, mockup.SPLIT - mockup.BOARD) * solid for solid in shape.solids()]
    for row in mockup.rows(placement):
        if row["Package"] in BODIES:
            (sx, sy, sz), (dx, dy) = BODIES[row["Package"]]
            x, y = float(row["PosX"]) + dx, -float(row["PosY"]) + dy
            parts.append(mockup.at(x, y, mockup.SPLIT) * Box(sx, sy, sz, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    return Compound(children=parts), box


def main():
    step, placement = Path(sys.argv[1]), Path(sys.argv[2])
    front, back, _ = mockup.build(placement)
    pcb, box = board(step, placement)
    print(f"board: x {box.min.X:.1f} to {box.max.X:.1f}, y {-box.max.Y:.1f} to {-box.min.Y:.1f} mm")
    bad = False
    for name, half in (("front", front), ("back", back)):
        for item in pcb.children:
            shared = half & item
            volume = shared.volume if shared else 0.0
            if volume > ALLOWED:
                at = shared.bounding_box()
                print(f"{name} half and the board share {volume:.1f} mm3 around "
                      f"x {at.min.X:.1f} to {at.max.X:.1f}, y {-at.max.Y:.1f} to {-at.min.Y:.1f}, "
                      f"z {at.min.Z:.1f} to {at.max.Z:.1f}")
                bad = True
    if bad:
        sys.exit("the board does not fit the shell")
    print("the board fits: no part of it touches the front or the back half")


if __name__ == "__main__":
    main()
