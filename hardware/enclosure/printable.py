"""Check that each part prints without supports: no layer may hold a
region with nothing under it.

    scripts/build-mockup.sh            # runs this after building

A region that touches the layer below anywhere passes, so bridges and
overhangs that grow out of a wall are allowed. What fails is plastic that
would start in mid-air.
"""

import sys
from pathlib import Path

from build123d import Box, Pos, import_step

LAYER = 0.2  # mm
THIN = 0.02  # thickness of the slice taken from each layer


def solids(shape):
    return list(shape.solids()) if shape else []


def floating(part):
    """Regions with nothing under them, as (height, bounding box, area)."""
    found, below = [], None
    z = LAYER / 2
    while z < part.bounding_box().max.Z:
        layer = solids(part & (Pos(0, 0, z) * Box(500, 500, THIN)))
        if below is not None:
            for region in layer:
                dropped = Pos(0, 0, -LAYER) * region
                held = sum(s.volume for under in below for s in solids(dropped & under))
                if held < 1e-6:
                    found.append((z, region.bounding_box(), region.volume / THIN))
        below = layer
        z += LAYER
    return found


def main():
    out = Path(sys.argv[1])
    bad = False
    for name in ("front", "back", "door"):
        for z, at, area in floating(import_step(str(out / f"mockup-{name}.step"))):
            print(f"{name}: {area:.0f} mm2 starts in mid-air {z:.1f} mm above the bed, "
                  f"x {at.min.X:.1f} to {at.max.X:.1f}, y {at.min.Y:.1f} to {at.max.Y:.1f}")
            bad = True
    if bad:
        sys.exit("a part needs supports")
    print("every part prints without supports: nothing starts in mid-air")


if __name__ == "__main__":
    main()
