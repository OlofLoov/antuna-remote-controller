## Context

Target: no board revision yet. These decisions feed PCB rev A and
enclosure rev A. The board in `boards/front.svg` is the intent; once the
PCB exists, its placement export is the one source for key positions.

## Decisions

### 1. Layout, top to bottom

Drawn in `boards/front.svg`, 40 by 154 mm:

- Top edge: two openings in the top wall, one for the IR LED and one for
  the IR receiver (decision 12). Top face: status light at center, Power
  at upper right, recessed in a ring.
- D-pad, 30 mm across, one ring that tilts onto four switches, with select
  in the middle, 13 mm across with a 0.4 mm gap to the ring, centered
  36 mm from the top.
- Back (round) at left and Home (rounded square) at right, 60 mm from the
  top, 20 mm apart.
- Play/pause, 11 mm across, centered 73 mm from the top.
- Mute (round) at left and a volume rocker, 9 by 20 mm, at right, both
  centered 89 mm from the top. The rocker pivots at its middle, 5.5 mm
  from each of its two switches, so up and down take the same force.
- From 101 mm down: the battery bay, past the end of the PCB, no keys.

Options considered: volume on the side edge (easy to press by accident
when gripping, harder to print), and play/pause inside the d-pad ring
(fewer keys to find but a crowded center). Both rejected.

### 2. Profile: thin over the keys, a head for the IR parts, cells on the back

Three thicknesses, all inside the limits of 11 mm over the keys and at the
top end and 14 mm at the battery end. The owner found 20 mm too chunky on
2026-11-25.

- Over the keys, about 6 mm of body and 7.5 mm with the caps: 1.2 mm back
  wall, 0.5 mm of ribs under the board (the IR LED's clipped leads stick
  out there), 1.0 mm PCB with every part on the top side, 1.7 mm switches,
  0.3 mm clearance, 1.2 mm front wall, caps 1.5 mm proud.
- The head, the top 18 mm, about 10 mm: the IR LED lies flat on the board
  and its 5.8 mm flange, centered 3.0 mm above the board, reaches 5.9 mm
  up; the receiver stands 5.3 mm. With the same back wall and ribs that is
  1.7 + 1.0 + 5.9 + 0.3 + 1.2 = 10.1 mm. The extra 4.2 mm rises on the
  front, since the parts sit on the board's top side. Power sits in the
  head, which is how it ends up below the surface around it.
- The battery end, 13.5 mm: a 10.5 mm cell, two 1.2 mm walls and 0.6 mm of
  clearance. The extra rises on the back, so the key face stays flat down
  to the end and the hand's palm fills the step.

Options considered for the IR parts: a body 10 mm thick all the way with
caps 0.8 mm proud (simplest shell, but thick in the hand and caps too low
to find by touch), and the two IR parts on the board's bottom side so the
head rises on the back (a flat front, but a second assembly side for one
part). Both rejected.

### 3. Batteries past the PCB's end, contacts held by the shell

An AAA cell is 10.5 mm across, so any cell under the PCB sets the
thickness at about 18 mm or more. The cells instead lie side by side past
the end of the PCB, on 11.5 mm centers.

Length, from Keystone's catalog page 42: contacts 5204 and 5226 at one end
and the bridge 5213 at the other need 49.5 mm between their plates for an
AAA cell. With the plates' 0.5 mm each, a 1 mm rib behind the contacts and
a 2.5 mm end wall, the bay takes 53 mm, from 101 mm to the end at 154 mm.
The first draft had 46 mm in a 150 mm shell, shorter than the cells need.
The bottom end's corners are 3 mm in the side view, not the 8 mm first
drawn, so the bridge plate and the cells fit to the end.

The contact plates stand across the cells, at right angles to the PCB, so
they cannot lie on pads. Each plate slides into a slot in the shell, which
takes the springs' push and a drop's knock. A short wire from each plate's
tab goes to a plated hole in the PCB. The bridge sits in a slot in the end
wall. The battery door is a sliding cover on the back and carries no
contact, so a drop on the end does not load it.

Options considered: cells under the PCB (about 18 to 20 mm, the first
draft), cells end to end along the back (a narrower body, about 32 mm, but
10.5 mm of cell under most of the PCB), contact tabs bent onto pads at the
PCB's edge (the solder joints would carry the springs through a 5.5 mm
lever, and the cells would sit too high for 14 mm), and the bridge in the
door (the door would carry both springs). All rejected.

### 4. Key mechanism: SMD tactile switches under printed caps

| Option | Click | Parts | Home-printable | Cost at 10 units |
|--------|-------|-------|----------------|------------------|
| SMD tactile switches on the PCB, printed caps in printed guides | Crisp, set by the switch | Switches placed by the assembler | Yes | Low |
| Silicone rubber keypad over carbon pads | Soft, set by the dome | Custom mold | No | High setup |
| Printed TPU membrane over tactile switches | Muted | Same switches | Yes, with TPU | Low |

Tactile switches under printed caps. The switch sets the force, so the
"every press clicks" range is met by choosing a switch rated in it, for
example a 160 gf (1.6 N) or 250 gf (2.5 N) part. The part number is picked
in the PCB change from the assembler's stock.

The switch picked there travels 0.2 mm (plus or minus 0.1), about one
printed layer, so a loose cap under the front wall would either rattle or
hold its switch down. Each cap therefore gets a 0.8 mm flange under the
front wall, a guide sleeve at least 3 mm long, a 1.8 mm nub on the
switch's stem and a thin foam pad between nub and stem to take up the
print's tolerance. The enclosure change tests that against one navy key
mat with flexure webs, clamped between shell and board, which has no
loose parts. A TPU membrane stays an option if both rattle.

### 5. Key repeat in firmware

The firmware repeats the d-pad and volume keys at 400 ms then 8 per
second, on both links, instead of relying on the Apple TV. Over IR each
repeat is a new frame rather than an NEC repeat frame, unless the bench in
`prove-the-apple-tv-link` shows repeat frames behave better.

### 6. Pairing hold: back and Home for 3 seconds

A two-key hold cannot happen by accident in normal use, and it uses two
keys a user can find by touch. A dedicated pairing button was considered:
one more part and a pinhole in the shell. Rejected.

### 7. Status light: one LED under a printed light pipe

A single small LED under a translucent PETG light pipe, about 5 mm long,
since the status light sits in the head where the front wall is 6 mm
above the board. Orange, not teal: teal and cyan LEDs need about 2.6 V or more and
stay dark on low cells, while a low-current orange LED lights at 2 mA
with about 1.8 V across it (`docs/research/pcb-components/`). Colors and patterns: blinking for pairing mode, a short double
blink on a press when the battery is low (see `define-power`). RGB was
considered and rejected: more parts, more firmware, little gain.

### 8. Not a Siri Remote

The Siri Remote (2021) is about 36 by 136 by 9 mm, aluminum, with a
clickpad. This remote is wider and longer, has a raised head and steps up
to 14 mm at the battery end, is bright teal matte plastic, and has a
d-pad ring that clicks and no touch surface. No Apple
names or glyphs: the Home key shows a generic TV glyph, not Apple's.

### 9. Colors: teal shell, navy keys, off-white select and symbols

The owner asked for a remote that stands out. The shell is printed in a
PETG close to Antuna's brand teal (#4FD1C5), the keys in a deep navy close
to #1A2A44, and select in off-white close to #F2F4F8, so the key used most
is the one that catches the eye. Symbols are raised 0.4 mm on the caps and
printed off-white with a filament change at that layer, which any single
nozzle printer can do. Options considered: a navy shell with teal keys (a
calmer remote, easier to lose on a dark sofa) and an all-black remote with
a teal select (classic, does not stand out). Filament brands and exact
colors are picked in the enclosure change from test prints.

### 10. Grip mock-up in code

`hardware/enclosure/mockup.py` builds the outer shape from decisions 1
to 3 with build123d: the body, the head, the battery bulge, a bump per
key, Power in its recess and the two IR openings. Key positions come
from the board's placement file, which `scripts/build-mockup.sh` exports
first. It is not the enclosure: no board, no switches, no battery door.
The enclosure change replaces it.

It prints as two parts, cut at the back of the 1.2 mm front wall, so each
lies flat on the bed and needs no supports: the back with the bulge, and
the front with the head and the keys. The back has pockets for two real
AAA cells, so the mock-up weighs and balances like the remote; they go in
before the parts are joined. Four pieces of 1.75 mm filament in 2 mm
holes line the parts up, and glue or tape holds them. The outer edges are
rounded 2 mm.

The outputs are STEP and STL. build123d's 3MF writer rejected these
shapes' meshes, and a slicer opens STEP directly.

Options considered: one solid part (the head rises on one face and the
bulge on the other, so either way up needs supports under a face the
hand judges) and printing it on its long edge (no supports, but a 14 mm
footprint for a 40 mm tall print, and layer lines across the grip). Both
rejected.

### 11. Screws through the PCB

Four M2 screws go through the back shell and unplated 2.2 mm holes in the
PCB into bosses in the front shell, at 35/25, 5/52, 35/68 and 5/82 mm
(x/y on the board). They locate the board and clamp it, so the board
needs no notches. The top left corner has no screw, since steel beside
the antenna detunes it: a printed hook holds that corner. The PCB sits
2 mm inside the outline all round, room for a 1.2 mm wall and a 0.8 mm
lap between the two shell halves.

Clips alone were considered: no tools, but nothing clamps the board
against the switches' push, and printed clips wear. Rejected.

The shell opens with a screwdriver, and the programming pads face the
front shell, so a finished remote is updated over Bluetooth, not by
cable. The cable is for bare boards.

### 12. IR openings in the top wall

Printed PETG, dark or not, cannot be trusted to pass 940 nm, so the top
wall has two holes: 6 mm for the IR LED, 23.1 mm from the left, whose lens
sits in the hole, and 4.5 mm for the receiver, 30.2 mm from the left,
chamfered to its 50 degree half angle. Both are centered 3 mm above the
board. A saddle rib behind the LED's flange keeps it from being pushed
in. One window of IR-pass acrylic across both was considered: a bought
part cut to size and glued or clipped, against two printed holes.
Rejected for rev A.

## Risks / Trade-offs

- Nothing here has been held yet: tasks 1.2 and 2.1 to 2.3 are open. The
  viewing keys span 70 mm, and a hand at the battery end covers mute and
  volume with the base of the thumb. The paper cut-out and the printed
  mock-up come before the enclosure change, and can move every key.
- The head rises 4.2 mm above the key face 3 mm above the d-pad ring. If
  it gets in the thumb's way, the fallback is the IR parts on the
  board's bottom side.
- Face down on a cushion, the caps stand 1.5 mm proud and can be pressed
  through the remote's back; only Power is protected, by its recess. On
  a firm surface the head keeps them clear. The mock-up tries the
  buttons spec's face-down scenario.
- No metallic or carbon-filled filament, and no metallic label, near the
  top left corner: the antenna is there.

- Printed caps can wobble in printed guides. The enclosure change sets
  clearances from test prints.

## Open Questions

- Filament brands and how close they get to the brand colors.
