"""Draw the grip mock-up as PNGs: scripts/render.sh calls this with the
placement file and the output folder."""

import subprocess
import sys
import tempfile
from pathlib import Path

from build123d import Compound, ExportSVG, LineType, Pos, Rot

import mockup

VIEWS = {
    # name: (camera position, up)
    "front": ((60, -160, 260), (0, 1, 0)),
    "back": ((60, -160, -260), (0, 1, 0)),
    "side": ((400, -77, -4), (0, 0, 1)),
}


def draw(shape, origin, up, path):
    visible, hidden = shape.project_to_viewport(origin, viewport_up=up, look_at=(20, -77, -4))
    svg = ExportSVG(scale=6, margin=10)
    svg.add_layer("visible", line_weight=0.25)
    svg.add_shape(visible, layer="visible")
    svg.write(path)


def main():
    placement, out = Path(sys.argv[1]), Path(sys.argv[2])
    front, back = mockup.build(placement)
    whole = Compound(children=[front, back])
    with tempfile.TemporaryDirectory() as tmp:
        for name, (origin, up) in VIEWS.items():
            svg = f"{tmp}/{name}.svg"
            draw(whole, origin, up, svg)
            subprocess.run(["rsvg-convert", "--width", "1600", "--background-color", "white",
                            "-o", str(out / f"enclosure-mockup-{name}.png"), svg], check=True)


if __name__ == "__main__":
    main()
