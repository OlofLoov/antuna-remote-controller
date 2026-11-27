"""Build antuna-remote.kicad_pcb from the schematic: parts, positions, outline,
ground pours and the antenna keep-out. Routing is a separate step
(scripts/route-board.sh) because it rewrites tracks only.

Run with KiCad's Python, which has pcbnew:
  scripts/build-board.sh

Coordinates below are in millimetres on the shell's front face, as drawn in
openspec/changes/define-keys-and-layout/boards/front.svg: x from the left
edge, y down from the top edge. The board sits 2 mm inside the shell, room
for the shell's wall and a lap joint.
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

# Board edges in shell coordinates. The bottom edge stops short of the
# battery contacts, which sit in slots in the shell at y = 101.
LEFT, RIGHT, TOP, BOTTOM = 2.0, 38.0, 2.0, 100.0
CORNER_R = 9.0  # the shell's 11 mm corner, 2 mm in
# The module's antenna end must sit on a board edge (Raytac AN54LQ datasheet
# v1.3, section 2.3), so the board steps down to it at the top left. Right
# of the step the board reaches the top edge for the IR LED and receiver.
MODULE_TOP = 5.0
STEP_X = 19.4
# Raytac's drawing has the module near the left of the board and at least
# 15 mm of ground to its right. 5 mm to the left edge leaves a channel
# for the supply parts, the crystal and the tracks from pads 4 to 7.
U1_X = 11.75
MODULE_LEFT = U1_X - 4.75
MODULE_RIGHT = U1_X + 4.75
# The footprint's origin is 6.95 mm below the module's antenna edge and
# 6.75 mm above its other end. The module sits 0.3 mm in from the board
# edge so its corner ground pads keep the fab's edge clearance.
MODULE_EDGE = MODULE_TOP + 0.3
U1_Y = MODULE_EDGE + 6.95
MODULE_BOTTOM = U1_Y + 6.75


def u1_left(n):
    """Centre of module pad n, 1 to 13, on its left edge."""
    return (U1_X - 4.2, U1_Y - 3.2 + 0.7 * (n - 1))


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
    "KEY_MUTE": (11.0, 89.0),
    # The rocker's cap pivots at y = 89, midway between its two switches.
    "KEY_VOLUP": (27.5, 83.5),
    "KEY_VOLDN": (27.5, 94.5),
}

# Everything else by reference: (x, y, rotation in degrees, counter-clockwise).
PARTS = {
    "U1": (U1_X, U1_Y, 0),
    # In the channel left of the module, each beside its pads: the DC/DC
    # inductor at DECD and DCC (8, 9), the supply capacitor at GND and VDD
    # (10, 11), the crystal at XL1 and XL2 (12, 13).
    "L1": (MODULE_LEFT - 2.9, u1_left(9)[1] + 0.1, 180),
    "C2": (MODULE_LEFT - 0.6, u1_left(10)[1] + 0.4, 90),
    "Y1": (MODULE_LEFT - 1.3, u1_left(13)[1] + 1.35, 90),
    # IR LED laid flat with its lens in the shell's top wall, receiver
    # beside it, lens up, both on the part of the board right of the step.
    "D1": (24.4, 10.6, 180),
    "U2": (30.2, 5.2, 180),
    # The receiver's supply filter and pull-up, under its pads as Vishay's
    # application circuit draws them.
    "R5": (27.95, 7.4, 180),
    "C5": (29.9, 7.16, 270),
    "R4": (32.0, 7.4, 180),
    # IR drive below the LED: the pulse runs C1, R1, D1, Q1 and back to
    # C1's ground pad, straight under Q1's source.
    "R2": (23.9, 14.6, 180),
    "Q1": (27.4, 15.7, 0),
    "R1": (21.5, 17.6, 90),
    "C1": (25.0, 18.7, 0),
    "TP3": (19.0, 19.2, 0),
    # Status light on the top face, centred, under the IR LED.
    "D2": (20.0, 14.0, 0),
    "R3": (18.2, 16.3, 0),
    # Programming pads below Power.
    "J1": (31.5, 20.3, 0),
    # Supply at the battery end: the two wire holes on the cells' axes.
    "BT1": (20.0, BOTTOM - 1.5, 0),
    "Q2": (20.0, 95.4, 0),
    "TP1": (16.0, 93.3, 0),
    "TP2": (16.0, 95.7, 0),
}

# M2 screws through the board into the front shell's bosses. None near the
# antenna: the shell holds that corner with a plastic hook.
HOLES = [(35.0, 25.0), (5.0, 52.0), (35.0, 68.0), (5.0, 82.0)]
HOLE_CLEAR = 2.5  # mm from a hole's centre kept free of copper, for the boss

# Raytac's "no ground pad" area under the antenna (datasheet v1.3, section
# 2.2) is a T: 3.3 mm down from the module's antenna edge, 7.35 mm wide
# between the corner ground pads for the first 1.2 mm, then the module's
# full 9.5 mm width.
KEEPOUT_BOTTOM = MODULE_EDGE + 3.3
ANTENNA_KEEPOUT = [
    (MODULE_LEFT + 1.0, MODULE_TOP - 0.5), (MODULE_LEFT + 8.35, MODULE_TOP - 0.5),
    (MODULE_LEFT + 8.35, MODULE_EDGE + 1.2), (MODULE_RIGHT, MODULE_EDGE + 1.2),
    (MODULE_RIGHT, KEEPOUT_BOTTOM), (MODULE_LEFT, KEEPOUT_BOTTOM),
    (MODULE_LEFT, MODULE_EDGE + 1.2), (MODULE_LEFT + 1.0, MODULE_EDGE + 1.2),
]
# No tracks or vias across the antenna end: from the left edge to 3.5 mm
# right of the module, down to the no-ground area's lower edge, just above
# pads 1 and 39.
ANTENNA_BAND = (LEFT - 1.0, MODULE_TOP - 1.0, MODULE_RIGHT + 3.5, KEEPOUT_BOTTOM)
# Ground only from there to the receiver's pads, level with the antenna, so
# the ground Raytac asks for to the module's right is not cut by tracks.
BESIDE_ANTENNA = (ANTENNA_BAND[2], TOP - 1.0, 26.4, KEEPOUT_BOTTOM)
# Inside the module's pad ring: ground pour and ground vias only, as in
# Raytac's drawing. The inner pads 40 and 41 are not connected.
MODULE_BODY = (U1_X - 3.75, KEEPOUT_BOTTOM, U1_X + 3.75, U1_Y + 5.75)
# On the bottom layer nothing but ground under the whole module.
UNDER_MODULE = (MODULE_LEFT - 0.5, KEEPOUT_BOTTOM, MODULE_RIGHT + 0.5, MODULE_BOTTOM + 0.5)
# Solid ground under the crystal and its two tracks.
CRYSTAL = (MODULE_LEFT - 2.5, u1_left(12)[1] - 0.2, MODULE_LEFT - 0.5, u1_left(13)[1] + 3.6)
# Tag-Connect's drawing keeps other copper 0.5 mm from its pads.
J1_PADS = (PARTS["J1"][0] - 2.2, PARTS["J1"][1] - 1.6, PARTS["J1"][0] + 2.2, PARTS["J1"][1] + 1.6)
# Where the router may not go though KiCad's own rules allow it: the top
# layer by the crystal, and between and beside the programming pads.
ROUTER_KEEPOUTS = [CRYSTAL, J1_PADS]


def j1_pad(col, row):
    return (PARTS["J1"][0] + 1.27 * col, PARTS["J1"][1] + 0.635 * row)


# The supply comes up to C2 on the bottom layer, through a via in the one
# free spot between the inductor and the crystal.
SUPPLY_VIA = (PARTS["C2"][0] - 1.1, PARTS["C2"][1] + 0.4)

# Tracks drawn here, not by the router: (net, width, points), top layer.
# The crystal and the DC/DC want them short and direct, and the
# programming pads want them leaving straight out.
PREROUTES = [
    ("/DCC", 0.3, [u1_left(9), (PARTS["L1"][0] + 0.79, u1_left(9)[1])]),
    ("/DECD", 0.25, [u1_left(8), (PARTS["L1"][0] - 0.79, u1_left(8)[1]),
                     (PARTS["L1"][0] - 0.79, PARTS["L1"][1])]),
    ("/GND", 0.3, [u1_left(10), (PARTS["C2"][0], PARTS["C2"][1] - 0.48)]),
    ("/VBAT", 0.3, [u1_left(11), (PARTS["C2"][0], PARTS["C2"][1] + 0.48), SUPPLY_VIA]),
    ("/XL1", 0.15, [u1_left(12), (u1_left(12)[0] - 0.75, u1_left(12)[1]),
                    (PARTS["Y1"][0] + 0.5, PARTS["Y1"][1] - 1.45)]),
    ("/XL2", 0.15, [u1_left(13), (u1_left(13)[0] - 0.6, u1_left(13)[1]),
                    (u1_left(13)[0] - 0.6, PARTS["Y1"][1] + 0.9),
                    (PARTS["Y1"][0] + 0.8, PARTS["Y1"][1] + 1.25)]),
    # Q1's source to C1's ground pad, the IR pulse's way back.
    ("/GND", 0.4, [(PARTS["Q1"][0] - 0.94, PARTS["Q1"][1] + 0.95), (PARTS["C1"][0] + 1.47, PARTS["C1"][1])]),
    ("/SWDIO", 0.2, [j1_pad(-1, -1), (j1_pad(-1, -1)[0], J1_PADS[1] - 0.6)]),
    ("/SWDCLK", 0.2, [j1_pad(0, -1), (j1_pad(0, -1)[0], J1_PADS[1] - 0.6)]),
    ("/VBAT", 0.2, [j1_pad(-1, 1), (j1_pad(-1, 1)[0], J1_PADS[3] + 0.6)]),
    ("/RESET", 0.2, [j1_pad(0, 1), (j1_pad(0, 1)[0], J1_PADS[3] + 0.6)]),
    ("/GND", 0.2, [j1_pad(1, 1), (j1_pad(1, 1)[0], J1_PADS[3] + 1.0)]),
    # C5's ground pad, boxed in by the filter: down to a via under Power.
    ("/GND", 0.3, [(PARTS["C5"][0], PARTS["C5"][1] + 0.48), (PARTS["C5"][0], PARTS["C5"][1] + 1.4)]),
]
# Vias at the ends of the tracks above.
VIAS = [("/VBAT", SUPPLY_VIA)]
GROUND_VIAS = [(j1_pad(1, 1)[0], J1_PADS[3] + 1.0), (PARTS["C5"][0], PARTS["C5"][1] + 1.4)]


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

    rule_area(board, "antenna no-ground area", ANTENNA_KEEPOUT, fill=False, tracks=False, vias=False)
    rule_area(board, "antenna band", corners(ANTENNA_BAND), tracks=False, vias=False)
    # Vias stay allowed in the next three so ground vias can go in; the
    # project's .kicad_dru keeps signal vias out, and with no tracks
    # allowed the router has no way in.
    rule_area(board, "ground beside the antenna", corners(BESIDE_ANTENNA), tracks=False)
    rule_area(board, "module body", corners(MODULE_BODY), tracks=False)
    rule_area(board, "under the module", corners(UNDER_MODULE), tracks=False, layers=[pcbnew.B_Cu])
    rule_area(board, "under the crystal", corners(CRYSTAL), tracks=False, layers=[pcbnew.B_Cu])
    # Ground ends level with the antenna end, as in Raytac's drawing: no
    # pour on the part right of the step.
    rule_area(board, "no ground above the antenna end",
              [(STEP_X - 0.5, TOP - 1.0), (RIGHT + 1.0, TOP - 1.0),
               (RIGHT + 1.0, MODULE_TOP), (STEP_X - 0.5, MODULE_TOP)], fill=False)
    for n, (x, y) in enumerate(HOLES):
        ring = [(x + HOLE_CLEAR * math.cos(math.radians(a)), y + HOLE_CLEAR * math.sin(math.radians(a)))
                for a in range(0, 360, 15)]
        rule_area(board, f"screw boss {n + 1}", ring, fill=False, tracks=False, vias=False)


def corners(box):
    x0, y0, x1, y1 = box
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rule_area(board, name, corners, fill=True, tracks=True, vias=True, layers=None):
    rule = pcbnew.ZONE(board)
    rule.SetIsRuleArea(True)
    if layers:
        lset = pcbnew.LSET()
        for layer in layers:
            lset.AddLayer(layer)
        rule.SetLayerSet(lset)
    else:
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


def no_via(at, margin=0.4):
    """Where no via may go: across the antenna end, by the crystal, between
    the programming pads and where a screw boss lands."""
    if any(inside(box, at, margin) for box in (ANTENNA_BAND, CRYSTAL, J1_PADS)):
        return True
    reach = pcbnew.FromMM(HOLE_CLEAR + margin)
    return any((mm(*hole) - at).EuclideanNorm() < reach for hole in HOLES)


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
        if ref == "BT1":
            fp.SetExcludedFromPosFiles(True)  # wires, soldered at home
        if (ref[0] in "RCL" or ref == "D2") and ref != "C1":
            # Small parts meet the pours through thermal spokes, so both
            # ends heat alike in reflow and the part does not stand up.
            # C1 carries the IR pulses and stays solid.
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
    for n, (x, y) in enumerate(HOLES):
        fp = pcbnew.FootprintLoad(footprint_dir("MountingHole"), "MountingHole_2.2mm_M2")
        fp.SetFPID(pcbnew.LIB_ID("MountingHole", "MountingHole_2.2mm_M2"))
        fp.SetReference(f"H{n + 1}")
        fp.Reference().SetVisible(False)
        fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_BOARD_ONLY
                         | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
        board.Add(fp)
        fp.SetPosition(mm(x, y))


def add_track(board, net, a, b, width):
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(a)
    track.SetEnd(b)
    track.SetWidth(pcbnew.FromMM(width))
    track.SetLayer(pcbnew.F_Cu)
    track.SetNet(net)
    track.SetLocked(True)
    board.Add(track)
    return track


def add_via(board, at, net="/GND"):
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(at)
    via.SetWidth(pcbnew.FromMM(0.6))
    via.SetDrill(pcbnew.FromMM(0.3))
    via.SetNet(board.FindNet(net))
    via.SetLocked(True)
    board.Add(via)
    return via


def preroute(board):
    tracks = []
    for net, width, points in PREROUTES:
        for a, b in zip(points, points[1:]):
            tracks.append(add_track(board, board.FindNet(net), mm(*a), mm(*b), width))
    for at in GROUND_VIAS:
        add_via(board, mm(*at))
    for net, at in VIAS:
        tracks.append(add_via(board, mm(*at), net))
    return tracks


def ground_vias(board, drawn):
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
        if no_via(at) or inside(MODULE_BODY, at, 0.4):
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
        # The via and its short track must clear other nets' pads and the
        # tracks drawn above.
        path = pcbnew.SHAPE_SEGMENT(start, at, pcbnew.FromMM(0.3))
        for pad in pads:
            if pad.GetNetname() != "/GND" and pad.GetEffectiveShape(pcbnew.F_Cu).Collide(path, pcbnew.FromMM(0.2)):
                return False
        for track in drawn:
            if track.GetNetname() == "/GND":
                continue
            shape = track.GetEffectiveShape(pcbnew.F_Cu)
            if shape.Collide(path, pcbnew.FromMM(0.2)) or shape.Collide(circle, pcbnew.FromMM(0.25)):
                return False
        return True

    for pad in pads:
        if pad.GetNetname() != "/GND" or pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
            continue
        own = pad.GetParentFootprint().GetReference()
        centre = pad.GetPosition()
        if own in ("J1", "C5", "C2"):
            continue  # drawn above
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
        add_via(board, spot)
        add_track(board, gnd, centre, spot, 0.3)
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
            add_via(board, at)
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
    ground_vias(board, preroute(board))
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
