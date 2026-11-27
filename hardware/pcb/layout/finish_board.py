"""Export the board for Freerouting, then import its session, stitch the two
ground pours together with vias and fill them. Run by scripts/route-board.sh.

  finish_board.py <board.kicad_pcb> --export <board.dsn>
  finish_board.py <board.kicad_pcb> <session.ses>
"""

import os
import sys

import pcbnew

sys.path.insert(0, os.path.dirname(__file__))
from build_board import ROUTER_KEEPOUTS, corners, no_via, rule_area, save  # noqa: E402

GRID = 3.0          # mm between stitching via candidates
VIA_D, VIA_DRILL = 0.6, 0.3
CLEAR = 0.35        # mm from the via's edge to any other copper


def clear_of(copper, at, clear=CLEAR):
    """Clear of other nets by clear mm; ground copper only must not be overlapped."""
    circle = pcbnew.SHAPE_CIRCLE(at, pcbnew.FromMM(VIA_D / 2))
    for item in copper:
        keep = pcbnew.FromMM(0.05 if item.GetNetname() == "/GND" else clear)
        if item.GetClass() == "PAD" and item.GetParentFootprint().GetReference() == "J1":
            keep = pcbnew.FromMM(0.55)  # Tag-Connect's 0.5 mm
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


def join_fragments(board):
    """Give every piece of pour that the grid missed (under the
    module, between small parts) one via of its own, so it reaches the
    bottom pour. Raytac's layout drawing puts vias under the module too."""
    gnd = board.FindNet("/GND")
    outline = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(outline, False)
    copper = [pad for fp in board.GetFootprints() for pad in fp.Pads()] + list(board.GetTracks())
    vias = [t.GetPosition() for t in board.GetTracks()
            if t.GetClass() == "PCB_VIA" and t.GetNetname() == "/GND"]
    step = pcbnew.FromMM(0.25)
    added = 0
    for i in range(board.GetAreaCount()):
        zone = board.GetArea(i)
        if zone.GetIsRuleArea():
            continue
        layer = zone.GetLayerSet().Seq()[0]
        fill = zone.GetFilledPolysList(layer)
        for k in range(fill.OutlineCount()):
            # The piece with its holes, so a via in a hole (another net's,
            # in its clearance) does not count as this piece's.
            piece = pcbnew.SHAPE_POLY_SET()
            piece.AddOutline(fill.Outline(k))
            for h in range(fill.HoleCount(k)):
                piece.AddHole(fill.Hole(k, h))
            if any(piece.Contains(v) for v in vias):
                continue
            box = piece.BBox()
            done = False
            y = box.GetTop()
            while y <= box.GetBottom() and not done:
                x = box.GetLeft()
                while x <= box.GetRight():
                    at = pcbnew.VECTOR2I(x, y)
                    x += step
                    if (piece.Contains(at) and inside(outline, at) and not no_via(at)
                            and clear_of(copper, at, clear=0.2)):
                        copper.append(add_via(board, gnd, at))
                        vias.append(at)
                        added += 1
                        done = True
                        break
                y += step
    return added


def pour_pieces(board):
    """Every filled piece of ground pour, with its holes, and its layer."""
    pieces = []
    for i in range(board.GetAreaCount()):
        zone = board.GetArea(i)
        if zone.GetIsRuleArea():
            continue
        layer = zone.GetLayerSet().Seq()[0]
        fill = zone.GetFilledPolysList(layer)
        for k in range(fill.OutlineCount()):
            piece = pcbnew.SHAPE_POLY_SET()
            piece.AddOutline(fill.Outline(k))
            for h in range(fill.HoleCount(k)):
                piece.AddHole(fill.Hole(k, h))
            pieces.append((layer, piece))
    return pieces


def join_clusters(board):
    """The router takes the pours for solid planes, so its tracks can fence
    a few pieces in on both layers: they reach each other through vias but
    not the rest of the ground. Find such a cluster and put up to three
    vias, 1.5 mm or more apart, where its pieces lie over the main pour on
    the other layer, so its return current has more than one way out."""
    gnd = board.FindNet("/GND")
    outline = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(outline, False)
    copper = [pad for fp in board.GetFootprints() for pad in fp.Pads()] + list(board.GetTracks())
    vias = [t.GetPosition() for t in board.GetTracks()
            if t.GetClass() == "PCB_VIA" and t.GetNetname() == "/GND"]
    pieces = pour_pieces(board)
    group = list(range(len(pieces)))

    def root(i):
        while group[i] != i:
            i = group[i]
        return i

    for v in vias:
        hit = [i for i, (_, piece) in enumerate(pieces) if piece.Contains(v)]
        for i in hit[1:]:
            group[root(i)] = root(hit[0])
    area = {}
    for i, (_, piece) in enumerate(pieces):
        area[root(i)] = area.get(root(i), 0) + piece.Area()
    main = max(area, key=area.get)
    step = pcbnew.FromMM(0.25)
    added = 0
    for cluster in [c for c in area if c != main]:
        mains = [piece for i, (layer, piece) in enumerate(pieces) if root(i) == main]
        new = []
        for i, (layer, piece) in enumerate(pieces):
            if root(i) != cluster:
                continue
            box = piece.BBox()
            y = box.GetTop()
            while y <= box.GetBottom() and len(new) < 3:
                x = box.GetLeft()
                while x <= box.GetRight() and len(new) < 3:
                    at = pcbnew.VECTOR2I(x, y)
                    x += step
                    if (piece.Contains(at) and any(m.Contains(at) for m in mains)
                            and all((at - n).EuclideanNorm() >= pcbnew.FromMM(1.5) for n in new)
                            and inside(outline, at) and not no_via(at) and clear_of(copper, at, clear=0.2)):
                        copper.append(add_via(board, gnd, at))
                        new.append(at)
                y += step
        added += len(new)
        if not new:
            print("a piece of ground pour could not be joined to the rest")
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

    # Freerouting can leave a signal via that only one layer reaches.
    for via in [t for t in board.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetname() != "/GND"]:
        ring = pcbnew.SHAPE_CIRCLE(via.GetPosition(), via.GetWidth(pcbnew.F_Cu) // 2)
        layers = {t.GetLayer() for t in board.GetTracks()
                  if t.GetClass() != "PCB_VIA" and t.GetNetCode() == via.GetNetCode()
                  and t.GetEffectiveShape(t.GetLayer()).Collide(ring, 0)}
        layers |= {layer for fp in board.GetFootprints() for pad in fp.Pads()
                   if pad.GetNetCode() == via.GetNetCode()
                   for layer in (pcbnew.F_Cu, pcbnew.B_Cu)
                   if pad.IsOnLayer(layer) and pad.GetEffectiveShape(layer).Collide(ring, 0)}
        if len(layers) < 2:
            copper.remove(via)
            board.Remove(via)

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
            if no_via(at):
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
        # Keep-outs for the router alone; the tracks build_board.py drew
        # inside them stay.
        for n, box in enumerate(ROUTER_KEEPOUTS):
            rule_area(board, f"router keep-out {n + 1}", corners(box), tracks=False, vias=False)
        # The Specctra export makes every rule area a full keep-out, so a
        # pour-only rule would shut the router out. Locked tracks and vias
        # are build_board.py's; the router keeps them. Everything is
        # picked before anything is removed: a removal leaves pcbnew's
        # Python wrappers unusable.
        drop = [zone for zone in (board.GetArea(i) for i in range(board.GetAreaCount()))
                if zone.GetIsRuleArea() and not zone.GetDoNotAllowTracks() and not zone.GetDoNotAllowVias()]
        drop += [track for track in board.GetTracks() if not track.IsLocked()]
        for item in drop:
            board.Remove(item)
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
        save(board, path)
        # After a session import pcbnew's Python wrappers hand back bare
        # objects, so the stitching runs in a fresh interpreter.
        os.execv(sys.executable, [sys.executable, __file__, path, "--stitch"])
    board = pcbnew.LoadBoard(path)
    added = stitch(board)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    added += join_fragments(board)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    for _ in range(3):
        joined = join_clusters(board)
        if not joined:
            break
        added += joined
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    save(board, path)
    print(f"{added} ground stitching vias")


if __name__ == "__main__":
    main()
