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
import uuid

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
# v1.3, section 2.3), so the board steps down to it at the top left. Right
# of the step the board reaches the top edge for the IR LED and receiver.
MODULE_TOP = 5.0
STEP_X = 19.0
# Raytac's drawing has the module near the left of the board and at least
# 15 mm of ground to its right. 4.5 mm to the left edge leaves a channel
# for the tracks from pads 1 to 13 and the parts on them.
U1_X = 10.75
MODULE_LEFT = U1_X - 4.75
MODULE_RIGHT = U1_X + 4.75
U1_Y = MODULE_TOP + 0.3 + 6.875

# Keys by the net they pull low, centred under their caps in front.svg.
KEYS = {
    "KEY_POWER": (31.0, 11.0),
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
    # Module, antenna end up and 0.3 mm in from the edge so its corner
    # ground pads keep the fab's edge clearance.
    "U1": (U1_X, U1_Y, 0),
    # DC/DC inductor, supply capacitor and crystal in the channel left of
    # the module, beside pads 8 to 13.
    "L1": (3.5, 14.3, 90),
    "C2": (3.5, 16.9, 90),
    "Y1": (3.5, 20.0, 90),
    "C3": (3.0, 23.1, 270),
    "C4": (4.6, 23.1, 270),
    # IR LED laid flat with its lens at the top edge, receiver beside it,
    # lens up, both on the part of the board right of the step. The
    # receiver's supply filter sits right of Power, leaving the gap below
    # the receiver for its tracks.
    "D1": (24.0, 11.5, 180),
    "U2": (30.2, 5.2, 180),
    "R5": (36.3, 9.2, 90),
    "R4": (36.3, 12.4, 90),
    "C5": (36.3, 15.0, 90),
    # IR drive below the LED.
    "Q1": (25.0, 14.8, 0),
    "R1": (21.7, 16.6, 90),
    "R2": (27.9, 15.7, 90),
    "C1": (25.0, 18.7, 0),
    "TP3": (19.6, 17.5, 0),
    # Status light on the top face, centred, under the IR LED.
    "D2": (20.0, 14.0, 0),
    "R3": (17.5, 14.0, 90),
    # Programming pads below Power.
    "J1": (31.5, 19.5, 0),
    # Supply at the battery end.
    "BT1": (20.0, BOTTOM - 2.5, 0),
    "Q2": (20.0, 96.3, 0),
    "TP1": (16.0, 93.8, 0),
    "TP2": (16.0, 96.5, 0),
}

# Raytac's "no ground-pad area" under the antenna: 7.35 by 3.3 mm from the
# module's top edge, starting 1 mm in from its left edge.
ANTENNA_KEEPOUT = (MODULE_LEFT + 1.0, MODULE_TOP, MODULE_LEFT + 1.0 + 7.35, MODULE_TOP + 0.3 + 3.3)
# No tracks or vias across the antenna end: from the left edge to 3.5 mm
# right of the module, down to the no-ground area's lower edge, just above
# pads 1 and 39.
ANTENNA_BAND = (LEFT - 1.0, MODULE_TOP - 1.0, MODULE_RIGHT + 3.5, ANTENNA_KEEPOUT[3])
# Inside the module's pad ring: ground pour and ground vias only, as in
# Raytac's drawing. The inner pads 40 and 41 are not connected.
MODULE_BODY = (U1_X - 3.75, ANTENNA_KEEPOUT[3], U1_X + 3.75, U1_Y + 5.75)


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


def left_step_angle(r, y):
    """Angle in radians where the top left corner's arc of radius r meets
    the horizontal line at y, on the upper left quarter."""
    dy = y - (TOP + CORNER_R)
    return math.atan2(dy, -math.sqrt(r ** 2 - dy ** 2)) + 2 * math.pi


def perimeter(inset):
    """The board outline as points, moved inset mm inwards."""
    r = CORNER_R - inset
    left_c = (LEFT + CORNER_R, TOP + CORNER_R)
    right_c = (RIGHT - CORNER_R, TOP + CORNER_R)
    end = left_step_angle(r, MODULE_TOP + inset)
    pts = []
    for k in range(13):
        a = math.pi + (end - math.pi) * k / 12
        pts.append((left_c[0] + r * math.cos(a), left_c[1] + r * math.sin(a)))
    pts += [(STEP_X + inset, MODULE_TOP + inset), (STEP_X + inset, TOP + inset)]
    for k in range(13):
        a = math.radians(270 + 90 * k / 12)
        pts.append((right_c[0] + r * math.cos(a), right_c[1] + r * math.sin(a)))
    pts += [(RIGHT - inset, BOTTOM - inset), (LEFT + inset, BOTTOM - inset)]
    return pts


def outline(board):
    left_c = (LEFT + CORNER_R, TOP + CORNER_R)
    right_c = (RIGHT - CORNER_R, TOP + CORNER_R)
    step_deg = math.degrees(left_step_angle(CORNER_R, MODULE_TOP))
    _, (sx, sy) = add_arc(board, left_c, 180, step_deg)
    add_line(board, (sx, sy), (STEP_X, MODULE_TOP))
    add_line(board, (STEP_X, MODULE_TOP), (STEP_X, TOP))
    add_line(board, (STEP_X, TOP), (right_c[0], TOP))
    add_arc(board, right_c, 270, 360)
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
        # Solid to the module's fine-pitch pads and the switches, spokes
        # to the through-hole LED; place() sets spokes for small passives.
        zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
        zone.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        zone.SetThermalReliefGap(pcbnew.FromMM(0.25))
        zone.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.3))
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
    rule_area(board, "antenna no-ground area", [(x0, y0 - 0.5), (x1, y0 - 0.5), (x1, y1), (x0, y1)],
              fill=False, tracks=False, vias=False)
    x0, y0, x1, y1 = ANTENNA_BAND
    rule_area(board, "antenna band", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)],
              tracks=False, vias=False)
    # Vias stay allowed here so the ground vias below can go in; the
    # project's .kicad_dru keeps signal vias out, and with no tracks
    # allowed the router has no way in.
    x0, y0, x1, y1 = MODULE_BODY
    rule_area(board, "module body", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], tracks=False)
    # Ground ends level with the antenna end, as in Raytac's drawing: no
    # pour on the part right of the step.
    rule_area(board, "no ground above the antenna end",
              [(STEP_X - 0.5, TOP - 1.0), (RIGHT + 1.0, TOP - 1.0),
               (RIGHT + 1.0, MODULE_TOP), (STEP_X - 0.5, MODULE_TOP)], fill=False)


def rule_area(board, name, corners, fill=True, tracks=True, vias=True):
    rule = pcbnew.ZONE(board)
    rule.SetIsRuleArea(True)
    rule.SetLayerSet(pcbnew.LSET.AllCuMask())
    rule.SetDoNotAllowZoneFills(not fill)
    rule.SetDoNotAllowTracks(not tracks)
    rule.SetDoNotAllowVias(not vias)
    rule.SetDoNotAllowPads(False)
    rule.SetDoNotAllowFootprints(False)
    rule.SetZoneName(name)
    polygon(rule, corners)
    board.Add(rule)


def inside(box, at, margin=0.0):
    x0, y0, x1, y1 = box
    lo, hi = mm(x0 - margin, y0 - margin), mm(x1 + margin, y1 + margin)
    return lo.x <= at.x <= hi.x and lo.y <= at.y <= hi.y


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
        for model in fp.Models():
            if not model.m_Filename.startswith(MODELS):
                sys.exit(f"{ref}: 3D model {model.m_Filename} is not in hardware/pcb/lib/models")
        if ref[0] in "RCL":
            # Small passives meet the pours through thermal spokes, so
            # both ends heat alike in reflow and the part does not stand up.
            for pad in fp.Pads():
                pad.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_THERMAL)
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
    pads = [pad for fp in board.GetFootprints() for pad in fp.Pads()]
    yards = {fp.GetReference(): fp.GetCourtyard(pcbnew.F_CrtYd) for fp in board.GetFootprints()}
    placed = []
    radius = pcbnew.FromMM(0.3)

    def free(start, at, own):
        if not outline.PointInside(at):
            return False
        if inside(ANTENNA_BAND, at, 0.4) or inside(MODULE_BODY, at, 0.4):
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
        # The short track from the pad must clear other nets' pads too.
        path = pcbnew.SHAPE_SEGMENT(start, at, pcbnew.FromMM(0.3))
        for pad in pads:
            if pad.GetNetname() != "/GND" and pad.GetEffectiveShape(pcbnew.F_Cu).Collide(path, pcbnew.FromMM(0.2)):
                return False
        return True

    for pad in pads:
        if pad.GetNetname() != "/GND" or pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
            continue
        own = pad.GetParentFootprint().GetReference()
        centre = pad.GetPosition()
        if inside(ANTENNA_BAND, centre):
            continue  # the module's top corner pads reach ground through the top pour
        spot = None
        for dist in (0.9, 1.2, 1.5, 1.8, 2.2, 2.6):
            for step in range(16):
                a = math.radians(step * 22.5 + 90)
                at = pcbnew.VECTOR2I(centre.x + int(pcbnew.FromMM(dist) * math.cos(a)),
                                     centre.y + int(pcbnew.FromMM(dist) * math.sin(a)))
                if free(centre, at, own):
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
    module_vias(board, pads)


def module_vias(board, pads):
    """Ground vias on a 1.5 mm grid under the module, clear of the
    unconnected inner pads."""
    gnd = board.FindNet("/GND")
    x0, y0, x1, y1 = MODULE_BODY
    radius = pcbnew.FromMM(0.3)
    y = y0 + 0.75
    while y <= y1 - 0.5:
        x = x0 + 0.5
        while x <= x1 - 0.5:
            at = mm(x, y)
            x += 1.5
            circle = pcbnew.SHAPE_CIRCLE(at, radius)
            if any(pad.GetEffectiveShape(pcbnew.F_Cu).Collide(circle, pcbnew.FromMM(0.3)) for pad in pads):
                continue
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(at)
            via.SetWidth(pcbnew.FromMM(0.6))
            via.SetDrill(pcbnew.FromMM(0.3))
            via.SetNet(gnd)
            via.SetLocked(True)
            board.Add(via)
        y += 1.5


def stable_uuids(board):
    """Name every item by what it is and where, not at random, so a rebuild
    of the same inputs writes the same file and the diff shows only what
    changed. KiCad orders items by these ids when it saves."""
    seen = set()
    ns = uuid.UUID("8c5e1c34-55a3-4d52-9a0e-6c2f7e1b4d90")
    named = []

    def put(item, key):
        k, n = key, 0
        while k in seen:
            n += 1
            k = f"{key}#{n}"
        seen.add(k)
        named.append((item, str(uuid.uuid5(ns, k))))

    def where(p):
        return f"{p.x},{p.y}"

    def shape(item):
        box = item.GetBoundingBox()
        return f"{item.GetClass()}/{item.GetLayer()}/{where(box.GetOrigin())}/{where(box.GetEnd())}"

    for fp in board.GetFootprints():
        ref = fp.GetReference()
        put(fp, "fp/" + ref)
        for pad in fp.Pads():
            put(pad, f"fp/{ref}/pad/{pad.GetNumber()}")
        for field in fp.GetFields():
            put(field, f"fp/{ref}/field/{field.GetName()}")
        for item in fp.GraphicalItems():
            put(item, f"fp/{ref}/{shape(item)}")
        for i, zone in enumerate(fp.Zones()):
            put(zone, f"fp/{ref}/zone/{i}")
    for item in board.GetDrawings():
        put(item, "drawing/" + shape(item))
    for track in board.GetTracks():
        if track.GetClass() == "PCB_VIA":
            put(track, f"via/{where(track.GetPosition())}")
        else:
            put(track, f"track/{track.GetLayer()}/{where(track.GetStart())}/{where(track.GetEnd())}")
    for i in range(board.GetAreaCount()):
        zone = board.GetArea(i)
        box = zone.Outline().BBox()
        put(zone, f"zone/{zone.GetZoneName()}/{zone.GetLayerSet().FmtHex()}/{zone.GetNetname()}/"
                  f"{where(box.GetOrigin())}/{where(box.GetEnd())}")
    # Two passes, so no item takes an id another still holds.
    for item, _ in named:
        item.SetUuid(pcbnew.KIID())
    for item, new in named:
        item.SetUuid(pcbnew.KIID(new))


POINT = re.compile(r'(\(point\s+\(at ([-\d.]+) ([-\d.]+)\)\s+\(size [-\d.]+\)\s+'
                   r'\(layer "([^"]+)"\)\s+\(uuid ")[0-9a-f-]+"')


def save(board, path):
    stable_uuids(board)
    pcbnew.SaveBoard(path, board)
    # pcbnew's Python has no wrapper for footprint points (the IR LED's
    # body markers), so their ids are set in the file.
    ns = uuid.UUID("8c5e1c34-55a3-4d52-9a0e-6c2f7e1b4d90")
    text = open(path).read()
    text = POINT.sub(lambda m: f'{m.group(1)}{uuid.uuid5(ns, "point/" + "/".join(m.groups()[1:]))}"', text)
    open(path, "w").write(text)


def main():
    parts, nets = read_netlist()
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    board.GetDesignSettings().SetBoardThickness(pcbnew.FromMM(1.0))
    outline(board)
    place(board, parts, nets)
    ground_and_keepout(board)
    ground_vias(board)
    # The placement export reads from here: shell coordinates, x right, y down.
    board.GetDesignSettings().SetAuxOrigin(mm(0, 0))
    board.GetDesignSettings().SetGridOrigin(mm(0, 0))
    path = PROJECT + ".kicad_pcb"
    save(board, path)
    # Reload with the project so its net classes apply, then fill the pours.
    board = pcbnew.LoadBoard(path)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    save(board, path)
    print(f"wrote {os.path.relpath(path, ROOT)}: {len(parts)} parts")


if __name__ == "__main__":
    main()
