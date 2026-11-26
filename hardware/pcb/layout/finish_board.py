"""Export the board for Freerouting, then import its session, stitch the two
ground pours together with vias and fill them. Run by scripts/route-board.sh.

  finish_board.py <board.kicad_pcb> --export <board.dsn>
  finish_board.py <board.kicad_pcb> <session.ses>
"""

import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(__file__))
from build_board import ANTENNA_KEEPOUT, mm  # noqa: E402

GRID = 3.0          # mm between stitching via candidates
VIA_D, VIA_DRILL = 0.6, 0.3
CLEAR = 0.35        # mm from the via's edge to any other copper


def clear_of(copper, at, clear=CLEAR):
    """Clear of other nets by clear mm; ground copper only must not be overlapped."""
    circle = pcbnew.SHAPE_CIRCLE(at, pcbnew.FromMM(VIA_D / 2))
    for item in copper:
        keep = pcbnew.FromMM(0.05 if item.GetNetname() == "/GND" else clear)
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            if item.IsOnLayer(layer) and item.GetEffectiveShape(layer).Collide(circle, keep):
                return False
    return True


def add_via(board, net, at):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(at)
    via.SetWidth(pcbnew.FromMM(VIA_D))
    via.SetDrill(pcbnew.FromMM(VIA_DRILL))
    via.SetNet(net)
    board.Add(via)
    return via


def inside(outline, at, margin_mm=0.9):
    """At least margin_mm from the board edge in each direction."""
    m = pcbnew.FromMM(margin_mm)
    return all(outline.Contains(pcbnew.VECTOR2I(at.x + dx, at.y + dy))
               for dx, dy in ((0, 0), (m, 0), (-m, 0), (0, m), (0, -m), (m, m), (-m, m), (m, -m), (-m, -m)))


def in_keepout(at):
    x0, y0, x1, y1 = ANTENNA_KEEPOUT
    lo, hi = mm(x0 - 1, y0 - 1), mm(x1 + 1, y1 + 1)
    return lo.x <= at.x <= hi.x and lo.y <= at.y <= hi.y


def join_fragments(board):
    """Give every piece of pour that the grid missed (under the
    module, between small parts) one via of its own, so it reaches the
    bottom pour. Raytac's layout drawing puts vias under the module too."""
    gnd = board.FindNet("/GND")
    outline = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(outline, False)
    copper = [pad for fp in board.GetFootprints() for pad in fp.Pads()] + list(board.GetTracks())
    vias = [t.GetPosition() for t in board.GetTracks() if t.GetClass() == "PCB_VIA"]
    step = pcbnew.FromMM(0.25)
    added = 0
    for i in range(board.GetAreaCount()):
        zone = board.GetArea(i)
        if zone.GetIsRuleArea():
            continue
        layer = zone.GetLayerSet().Seq()[0]
        fill = zone.GetFilledPolysList(layer)
        for k in range(fill.OutlineCount()):
            piece = fill.Outline(k)
            if any(piece.PointInside(v) for v in vias):
                continue
            box = piece.BBox()
            done = False
            y = box.GetTop()
            while y <= box.GetBottom() and not done:
                x = box.GetLeft()
                while x <= box.GetRight():
                    at = pcbnew.VECTOR2I(x, y)
                    x += step
                    if (piece.PointInside(at) and inside(outline, at) and not in_keepout(at)
                            and clear_of(copper, at, clear=0.2)):
                        copper.append(add_via(board, gnd, at))
                        added += 1
                        done = True
                        break
                y += step
    return added


def stitch(board):
    gnd = board.FindNet("/GND")
    outline = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(outline, False)
    courtyards = []
    for fp in board.GetFootprints():
        yard = fp.GetCourtyard(pcbnew.F_CrtYd)
        if yard.OutlineCount():
            courtyards.append(yard)
    copper = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            copper.append(pad)
    copper.extend(board.GetTracks())

    # Freerouting can leave a via outside the outline; it connects nothing.
    for track in list(board.GetTracks()):
        if track.GetClass() == "PCB_VIA" and not outline.Contains(track.GetPosition()):
            copper.remove(track)
            board.Remove(track)

    box = board.GetBoardEdgesBoundingBox()
    step = pcbnew.FromMM(GRID)
    added = 0
    y = box.GetTop() + step
    while y < box.GetBottom():
        x = box.GetLeft() + step
        while x < box.GetRight():
            at = pcbnew.VECTOR2I(x, y)
            x += step
            if not inside(outline, at):
                continue
            if in_keepout(at):
                continue
            if any(c.Contains(at) for c in courtyards):
                continue
            if clear_of(copper, at):
                copper.append(add_via(board, gnd, at))
                added += 1
        y += step
    return added


def main():
    path = sys.argv[1]
    if sys.argv[2] == "--export":
        board = pcbnew.LoadBoard(path)
        # Locked tracks and vias are build_board.py's; the router keeps them.
        for track in list(board.GetTracks()):
            if not track.IsLocked():
                board.Remove(track)
        if not pcbnew.ExportSpecctraDSN(board, sys.argv[3]):
            sys.exit("could not export " + sys.argv[3])
        return
    if sys.argv[2] != "--stitch":
        board = pcbnew.LoadBoard(path)
        for track in list(board.GetTracks()):
            if not track.IsLocked():
                board.Remove(track)
        if not pcbnew.ImportSpecctraSES(board, sys.argv[2]):
            sys.exit("could not import " + sys.argv[2])
        pcbnew.SaveBoard(path, board)
        # After a session import pcbnew's Python wrappers hand back bare
        # objects, so the stitching runs in a fresh interpreter.
        os.execv(sys.executable, [sys.executable, __file__, path, "--stitch"])
    board = pcbnew.LoadBoard(path)
    added = stitch(board)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    added += join_fragments(board)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(path, board)
    print(f"{added} ground stitching vias")


if __name__ == "__main__":
    main()
