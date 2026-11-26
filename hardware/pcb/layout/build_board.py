"""Build antuna-remote.kicad_pcb from the schematic: parts, positions, outline,
ground pours and the antenna keep-out. Routing is a separate step
(scripts/route-board.sh) because it rewrites tracks only.

Run with KiCad's Python, which has pcbnew:
  scripts/build-board.sh

Coordinates below are in millimetres on the shell's front face, as drawn in
openspec/changes/define-keys-and-layout/boards/front.svg: x from the left
edge, y down from the top edge. The board sits 1.5 mm inside the shell.
Every position lives in this file; the enclosure reads them back from the
placement export, never from here.
"""

import math
import os
import re
import subprocess
import sys
import tempfile

import pcbnew

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PROJECT = os.path.join(ROOT, "hardware/pcb/antuna-remote/antuna-remote")
LOCAL_LIB = os.path.join(ROOT, "hardware/pcb/lib/antuna.pretty")

KICAD_MODELS = "${KICAD10_3DMODEL_DIR}/"
MODELS = "${KIPRJMOD}/../lib/models/"

# Where the sheet sits on the KiCad page, so the board is not at the corner.
ORIGIN = (100.0, 50.0)

# Board edges in shell coordinates.
LEFT, RIGHT, TOP, BOTTOM = 1.5, 38.5, 1.5, 103.0
CORNER_R = 9.5  # the shell's 11 mm corner, 1.5 mm in
# The module's antenna end must sit on a board edge (Raytac AN54LQ datasheet
# v1.3, section 2.3), so the board steps down to it at the top right.
MODULE_TOP = 5.0
STEP_X = 26.0

# Keys by the net they pull low, centred under their caps in front.svg.
KEYS = {
    "KEY_POWER": (7.3, 12.5),  # front.svg has it top right; the module needs that corner
    "KEY_UP": (20.0, 25.0),
    "KEY_DOWN": (20.0, 47.0),
    "KEY_LEFT": (9.0, 36.0),
    "KEY_RIGHT": (31.0, 36.0),
    "KEY_SELECT": (20.0, 36.0),
    "KEY_BACK": (10.0, 60.0),
    "KEY_HOME": (30.0, 60.0),
    "KEY_PLAY": (20.0, 73.0),
    "KEY_MUTE": (11.0, 90.0),
    "KEY_VOLUP": (27.5, 84.0),
    "KEY_VOLDN": (27.5, 94.5),
}

# Everything else by reference: (x, y, rotation in degrees, counter-clockwise).
PARTS = {
    # Module, antenna end up and flush with the stepped edge, supply and
    # crystal pads (1 to 13) facing the board.
    # 0.3 mm in from the edge so the corner ground pads keep clear of it.
    "U1": (31.25, MODULE_TOP + 0.3 + 6.97, 0),
    "L1": (25.2, 14.0, 90),
    "C2": (25.3, 16.6, 90),
    "Y1": (24.0, 19.0, 0),
    "C3": (22.4, 21.0, 0),
    "C4": (25.6, 21.0, 0),
    # IR LED laid flat, lens at the top edge; receiver beside it, lens up.
    "D1": (15.8, 11.5, 180),
    "U2": (21.9, 5.2, 180),
    "R4": (23.4, 8.0, 0),
    "C5": (23.4, 9.4, 0),
    "R5": (20.2, 8.0, 0),
    # IR drive next to the LED.
    "C1": (15.6, 18.4, 0),
    "Q1": (14.2, 14.6, 0),
    "R1": (17.4, 14.4, 90),
    "R2": (12.0, 18.6, 90),
    "TP3": (9.5, 18.0, 0),
    # Status light under the top face, between the IR parts and the d-pad.
    "D2": (20.6, 14.2, 0),
    "R3": (20.6, 16.2, 0),
    # Programming pads beside the module.
    "J1": (32.0, 27.0, 0),
    # Supply at the battery end.
    "BT1": (20.0, BOTTOM - 2.5, 0),
    "Q2": (20.0, 98.4, 0),
    "TP1": (17.4, 94.5, 0),
    "TP2": (22.6, 94.5, 0),
}

# Raytac's "no ground-pad area" under the antenna: 7.35 by 3.3 mm, starting
# 1 mm in from the module's left edge.
MODULE_LEFT = 31.25 - 4.75
ANTENNA_KEEPOUT = (MODULE_LEFT + 1.0, MODULE_TOP, MODULE_LEFT + 1.0 + 7.35, MODULE_TOP + 3.3)


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(ORIGIN[0] + x), pcbnew.FromMM(ORIGIN[1] + y))


def kicad_cli():
    mac = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
    return mac if os.path.exists(mac) else "kicad-cli"


def footprint_dir(lib):
    if lib == "antuna":
        return LOCAL_LIB
    for env in ("KICAD10_FOOTPRINT_DIR", "KICAD9_FOOTPRINT_DIR"):
        if os.environ.get(env):
            return os.path.join(os.environ[env], lib + ".pretty")
    for base in ("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints",
                 "/usr/share/kicad/footprints"):
        if os.path.isdir(base):
            return os.path.join(base, lib + ".pretty")
    sys.exit("KiCad footprint libraries not found")


def parse_sexpr(text):
    tokens = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    pos = 0

    def item():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        if tok == "(":
            out = []
            while tokens[pos] != ")":
                out.append(item())
            pos += 1
            return out
        return tok[1:-1].replace('\\"', '"') if tok.startswith('"') else tok

    return item()


def children(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def value_of(node, key):
    found = children(node, key)
    return found[0][1] if found and len(found[0]) > 1 else ""


def read_netlist():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "antuna.net")
        subprocess.run([kicad_cli(), "sch", "export", "netlist", "-o", path, PROJECT + ".kicad_sch"],
                       check=True, capture_output=True)
        tree = parse_sexpr(open(path).read())
    parts = []
    for comp in children(children(tree, "components")[0], "comp"):
        props = {value_of(p, "name"): value_of(p, "value") for p in children(comp, "property")}
        fields = {}
        for f in children(children(comp, "fields")[0], "field") if children(comp, "fields") else []:
            name = value_of(f, "name")
            fields[name] = f[2] if len(f) > 2 and not isinstance(f[2], list) else ""
        parts.append({
            "ref": value_of(comp, "ref"),
            "value": value_of(comp, "value"),
            "footprint": value_of(comp, "footprint"),
            "uuid": value_of(comp, "tstamps"),
            "fields": fields,
            "props": props,
        })
    nets = {}
    for net in children(children(tree, "nets")[0], "net"):
        name = value_of(net, "name")
        for node in children(net, "node"):
            nets[(value_of(node, "ref"), value_of(node, "pin"))] = name
    return parts, nets


def add_line(board, a, b):
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetStart(mm(*a))
    seg.SetEnd(mm(*b))
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetWidth(pcbnew.FromMM(0.1))
    board.Add(seg)


def add_arc(board, centre, start_deg, end_deg):
    # Angles on screen, y down, so 270 points up.
    def at(deg):
        return (centre[0] + CORNER_R * math.cos(math.radians(deg)),
                centre[1] + CORNER_R * math.sin(math.radians(deg)))
    arc = pcbnew.PCB_SHAPE(board)
    arc.SetShape(pcbnew.SHAPE_T_ARC)
    arc.SetArcGeometry(mm(*at(start_deg)), mm(*at((start_deg + end_deg) / 2)), mm(*at(end_deg)))
    arc.SetLayer(pcbnew.Edge_Cuts)
    arc.SetWidth(pcbnew.FromMM(0.1))
    board.Add(arc)
    return at(start_deg), at(end_deg)


def perimeter(inset):
    """The board outline as points, moved inset mm inwards."""
    r = CORNER_R - inset
    left_c = (LEFT + CORNER_R, TOP + CORNER_R)
    right_c = (RIGHT - CORNER_R, TOP + CORNER_R)
    pts = []
    for k in range(13):
        a = math.radians(180 + 90 * k / 12)
        pts.append((left_c[0] + r * math.cos(a), left_c[1] + r * math.sin(a)))
    pts += [(STEP_X - inset, TOP + inset), (STEP_X - inset, MODULE_TOP + inset)]
    dy = MODULE_TOP + inset - right_c[1]
    start = math.atan2(dy, math.sqrt(r ** 2 - dy ** 2))
    for k in range(13):
        a = start + (0 - start) * k / 12
        pts.append((right_c[0] + r * math.cos(a), right_c[1] + r * math.sin(a)))
    pts += [(RIGHT - inset, BOTTOM - inset), (LEFT + inset, BOTTOM - inset)]
    return pts


def outline(board):
    left_c = (LEFT + CORNER_R, TOP + CORNER_R)
    right_c = (RIGHT - CORNER_R, TOP + CORNER_R)
    # Where the right corner's arc crosses the stepped top edge.
    dy = MODULE_TOP - right_c[1]
    step_deg = math.degrees(math.atan2(dy, math.sqrt(CORNER_R ** 2 - dy ** 2)))
    add_arc(board, left_c, 180, 270)
    add_line(board, (left_c[0], TOP), (STEP_X, TOP))
    add_line(board, (STEP_X, TOP), (STEP_X, MODULE_TOP))
    (sx, sy), _ = add_arc(board, right_c, step_deg, 0)
    add_line(board, (STEP_X, MODULE_TOP), (sx, sy))
    add_line(board, (RIGHT, right_c[1]), (RIGHT, BOTTOM))
    add_line(board, (RIGHT, BOTTOM), (LEFT, BOTTOM))
    add_line(board, (LEFT, BOTTOM), (LEFT, left_c[1]))


def polygon(zone, corners):
    outline_poly = zone.Outline()
    outline_poly.NewOutline()
    for c in corners:
        outline_poly.Append(mm(*c))


def ground_and_keepout(board):
    gnd = board.FindNet("/GND")
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        zone.SetNet(gnd)
        zone.SetLocalClearance(pcbnew.FromMM(0.25))
        zone.SetMinThickness(pcbnew.FromMM(0.2))
        # Solid to SMD pads (no starved spokes at the module's fine pitch),
        # thermal reliefs only for the through-hole LED.
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
        zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        polygon(zone, [(0, 0), (40, 0), (40, 105), (0, 105)])
        board.Add(zone)
    # A 0.4 mm ring inside the outline with no tracks or vias, so the
    # autorouter keeps the fab's copper-to-edge clearance; it reads rule
    # areas but not KiCad's edge clearance.
    ring = pcbnew.ZONE(board)
    ring.SetIsRuleArea(True)
    ring.SetLayerSet(pcbnew.LSET.AllCuMask())
    ring.SetDoNotAllowTracks(True)
    ring.SetDoNotAllowVias(True)
    ring.SetDoNotAllowZoneFills(False)
    ring.SetDoNotAllowPads(False)
    ring.SetDoNotAllowFootprints(False)
    ring.SetZoneName("edge clearance for the router")
    poly = ring.Outline()
    poly.NewOutline()
    for p in perimeter(-0.05):
        poly.Append(mm(*p))
    poly.NewHole()
    for p in perimeter(0.4):
        poly.Append(mm(*p), 0, 0)
    board.Add(ring)

    x0, y0, x1, y1 = ANTENNA_KEEPOUT
    rule = pcbnew.ZONE(board)
    rule.SetIsRuleArea(True)
    rule.SetLayerSet(pcbnew.LSET.AllCuMask())
    rule.SetDoNotAllowZoneFills(True)
    rule.SetDoNotAllowTracks(True)
    rule.SetDoNotAllowVias(True)
    rule.SetDoNotAllowPads(False)
    rule.SetDoNotAllowFootprints(False)
    rule.SetZoneName("antenna no-ground area")
    polygon(rule, [(x0, y0 - 0.5), (x1, y0 - 0.5), (x1, y1), (x0, y1)])
    board.Add(rule)


def place(board, parts, nets):
    netinfo = {}
    for name in sorted(set(nets.values())):
        item = pcbnew.NETINFO_ITEM(board, name)
        board.Add(item)
        netinfo[name] = item
    key_of = {}
    for (ref, _pin), name in nets.items():
        if name.lstrip("/") in KEYS and ref.startswith("SW"):
            key_of[ref] = name.lstrip("/")
    missing = []
    for part in parts:
        ref = part["ref"]
        lib, name = part["footprint"].split(":", 1)
        fp = pcbnew.FootprintLoad(footprint_dir(lib), name)
        if fp is None:
            sys.exit(f"{ref}: footprint {part['footprint']} not found")
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetReference(ref)
        fp.SetValue(part["value"])
        for field, text in part["fields"].items():
            if field not in ("Reference", "Value", "Footprint") and text:
                fp.SetField(field, text)
                fp.GetField(field).SetVisible(False)
        # The board is too dense for reference text on the silkscreen; the
        # assembly drawing (F.Fab) and the placement file carry them.
        fp.Reference().SetVisible(False)
        fp.SetPath(pcbnew.KIID_PATH("/" + part["uuid"]))
        if "dnp" in part["props"]:
            fp.SetDNP(True)
        if "exclude_from_bom" in part["props"]:
            fp.SetExcludedFromBOM(True)
            fp.SetExcludedFromPosFiles(True)
        # 3D bodies come from hardware/pcb/lib/models, committed, so a
        # render needs no KiCad 3D library and no download.
        # Models() yields copies when iterated; index it to change the path.
        for k in range(len(fp.Models())):
            model = fp.Models()[k]
            if model.m_Filename.startswith(KICAD_MODELS):
                model.m_Filename = MODELS + "kicad/" + model.m_Filename[len(KICAD_MODELS):]
        if name == "SW_Push_1P1T_XKB_TS-1187A":
            # KiCad ships no body for this switch; make_models.py draws one.
            fp.Models()[0].m_Filename = MODELS + "XKB_TS-1187A.wrl"
        if ref in key_of:
            x, y = KEYS[key_of[ref]]
            rot = 0
        elif ref in PARTS:
            x, y, rot = PARTS[ref]
        else:
            missing.append(ref)
            continue
        board.Add(fp)
        fp.SetPosition(mm(x, y))
        fp.SetOrientationDegrees(rot)
        for pad in fp.Pads():
            net = nets.get((ref, pad.GetNumber()))
            if net:
                pad.SetNet(netinfo[net])
    if missing:
        sys.exit("no position for " + ", ".join(missing))


def ground_vias(board):
    """Give every ground pad a via of its own, on a short track, before
    routing. The router then routes around them, so no ground pad can end
    up boxed in on a sliver of pour, and each pad has a short path to the
    bottom pour. Raytac's layout drawing puts ground vias beside the
    module's pads the same way."""
    gnd = board.FindNet("/GND")
    edge = []
    for p in perimeter(1.0):
        edge.append(p)
    outline = pcbnew.SHAPE_LINE_CHAIN()
    for p in edge:
        outline.Append(mm(*p))
    outline.SetClosed(True)
    x0, y0, x1, y1 = ANTENNA_KEEPOUT
    keep_lo, keep_hi = mm(x0 - 0.8, y0 - 0.8), mm(x1 + 0.8, y1 + 0.8)
    pads = [pad for fp in board.GetFootprints() for pad in fp.Pads()]
    yards = {fp.GetReference(): fp.GetCourtyard(pcbnew.F_CrtYd) for fp in board.GetFootprints()}
    placed = []
    radius = pcbnew.FromMM(0.3)

    def free(at, own):
        if not outline.PointInside(at):
            return False
        if keep_lo.x <= at.x <= keep_hi.x and keep_lo.y <= at.y <= keep_hi.y:
            return False
        for ref, yard in yards.items():
            if ref != own and yard.OutlineCount() and yard.Contains(at):
                return False
        circle = pcbnew.SHAPE_CIRCLE(at, radius)
        for pad in pads:
            if pad.GetNetname() == "/GND" and pad.GetParentFootprint().GetReference() == own:
                gap = 0.15
            else:
                gap = 0.35
            if pad.GetEffectiveShape(pcbnew.F_Cu).Collide(circle, pcbnew.FromMM(gap)):
                return False
        for other in placed:
            if (other - at).EuclideanNorm() < pcbnew.FromMM(1.1):
                return False
        return True

    for pad in pads:
        if pad.GetNetname() != "/GND" or pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
            continue
        own = pad.GetParentFootprint().GetReference()
        centre = pad.GetPosition()
        spot = None
        for dist in (0.9, 1.2, 1.5, 1.8, 2.2, 2.6):
            for step in range(16):
                a = math.radians(step * 22.5 + 90)
                at = pcbnew.VECTOR2I(centre.x + int(pcbnew.FromMM(dist) * math.cos(a)),
                                     centre.y + int(pcbnew.FromMM(dist) * math.sin(a)))
                if free(at, own):
                    spot = at
                    break
            if spot:
                break
        if spot is None:
            print(f"no room for a ground via at {own} pad {pad.GetNumber()}")
            continue
        placed.append(spot)
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(spot)
        via.SetWidth(pcbnew.FromMM(0.6))
        via.SetDrill(pcbnew.FromMM(0.3))
        via.SetNet(gnd)
        via.SetLocked(True)
        board.Add(via)
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(centre)
        track.SetEnd(spot)
        track.SetWidth(pcbnew.FromMM(0.3))
        track.SetLayer(pcbnew.F_Cu)
        track.SetNet(gnd)
        track.SetLocked(True)
        board.Add(track)


def main():
    parts, nets = read_netlist()
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    board.GetDesignSettings().SetBoardThickness(pcbnew.FromMM(1.0))
    outline(board)
    place(board, parts, nets)
    ground_and_keepout(board)
    ground_vias(board)
    path = PROJECT + ".kicad_pcb"
    pcbnew.SaveBoard(path, board)
    # Reload with the project so its net classes apply, then fill the pours.
    board = pcbnew.LoadBoard(path)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(path, board)
    print(f"wrote {os.path.relpath(path, ROOT)}: {len(parts)} parts")


if __name__ == "__main__":
    main()
