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

### 2. Profile: a back that swells into the palm, a head for the IR parts

Inside the limits of 11 mm over the keys and 14 mm at the battery end.
The owner found 20 mm too chunky on 2026-11-25, and the first printed
mock-up, a 6 mm slab with a step up to the cells, uncomfortable on
2026-11-28 (`docs/bench/2026-11-28-grip-mockup-1.md`). They named a
Samsung-style TV remote as the grip to aim for: a rounded back that grows
thicker toward the hand, with no steps.

- Over the keys, 9 mm of body and 10.5 mm with the caps. From the front:
  1.2 mm front wall, 0.3 mm clearance, 1.7 mm switches, 1.0 mm PCB with
  every part on the top side, 0.5 mm of ribs under it, then the back.
  The back is thicker than the 1.3 mm it needs, so its edges can be
  rounded 6 mm.
- The back swells from 9 mm at 64 mm from the top to 14 mm at 96 mm, in
  one curve under the lower keys, and stays 14 mm to the end: a 10.5 mm
  cell, the 1.2 mm front wall, a 1.6 mm door and 0.7 mm of clearance.
  The key face stays flat to the end.
- The back's edges are rounded 6 mm all the way round, the front's
  1.5 mm.
- The head, the top 16 mm, rises 4.2 mm on the front and comes down to
  the key face by 20.5 mm: the IR LED lies flat on the board and its
  5.8 mm flange, centered 3.0 mm above the board, reaches 5.9 mm up; the
  receiver stands 5.3 mm. Power sits in the head, which is how it ends up
  below the surface around it. The head is 13.2 mm through.

Options considered for the back: a back curved across its whole width,
like the remote the owner named (the CAD kernel could not round its ends,
and the door would be curved, which prints badly), and keeping the slab
with larger corner radii (still a step under the palm). Both rejected.
The flat back with 6 mm edges is the first to print; a fuller curve is
the next thing to try if it is still not comfortable.

Options considered for the IR parts: a body thick enough all the way with
caps 0.8 mm proud (simplest shell, but caps too low to find by touch),
and the two IR parts on the board's bottom side so the head rises on the
back (a flat front, but a second assembly side for one part). Both
rejected.

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

### 10. Shell prototype in code

`hardware/enclosure/mockup.py` builds the shell with build123d as three
parts, and `scripts/build-mockup.sh` writes them as STEP and STL:

- The front half: the key face, the head and the side walls down to the
  board's top face, hollow, with a boss per screw. The keys are bumps on
  it. Moving caps come with the enclosure change, once there is a board
  to press on.
- The back half: the rest of the body, with a pocket the board drops
  into, ribs under it, a deeper room under the IR LED's leads, the
  battery bay and the screw holes.
- The battery door: a flat plate, flush with the back. Two tabs hook
  under the shell at the bottom end. At the other end a slot leaves a bar
  1.1 mm thick that bends back as its snap passes the shell's edge. Two
  slots beside the snap let a fingernail under the door's edge.

Key and part positions come from the board's placement file. The same
script exports the board as STEP and `fit.py` fails the build when any
part of the board shares space with either half. The export leaves out
the parts whose models are VRML, so the switches, the radio module and
the IR receiver are checked as boxes of their datasheet sizes.

Each part prints with its outside up and its inside on the bed, so the
faces the hand touches need no supports. The price is a butt joint: a
lip from one half into the other would have to hang below the bed. The
screws line the halves up. The bay is 45 mm long so bare cells do not
slide; the real bay is 50 mm, runs under the end wall and has spring
contacts (decision 3).

The first mock-up was a solid shape in two parts, pinned with filament
and glued. Printed, it could not be opened or closed, and said nothing
about the joint or the door.

Options considered: a lip joint with one half printed outside down (a
supported, rough back), a door that slides on rails (a curved or thick
door, and rails that need supports) and a door with a sprung hook
standing up from it (the hook would point into the bed). All rejected.

### 11. Screws through the PCB

Six M2 by 5 mm self-tapping screws go in from the back, each in a
counterbore. Four pass through unplated 2.2 mm holes in the PCB, at
35/25, 5/52, 35/68 and 5/82 mm (x/y on the board), into bosses in the
front half; two more beside the battery bay, at 4.6/143 and 35.4/143 mm,
hold the bottom end shut. Each has 1.5 mm of back under its head and
2.5 mm of thread in its boss. The board lies in its pocket, clamped
between the bosses and the ribs, so it needs no notches. The top left
corner has no screw, since steel beside the antenna detunes it. The
prototype shows whether that corner gapes; a printed hook there is the
fix if it does. The PCB sits 2 mm inside the outline all round.

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
  prototype come before the enclosure change, and can move every key.
- The head rises 4.2 mm above the key face 3 mm above the d-pad ring. If
  it gets in the thumb's way, the fallback is the IR parts on the
  board's bottom side.
- Face down on a cushion, the caps stand 1.5 mm proud and can be pressed
  through the remote's back; only Power is protected, by its recess. On
  a firm surface the head keeps them clear. The prototype tries the
  buttons spec's face-down scenario.
- No metallic or carbon-filled filament, and no metallic label, near the
  top left corner: the antenna is there.

- Printed caps can wobble in printed guides. The enclosure change sets
  clearances from test prints.

## Open Questions

- Filament brands and how close they get to the brand colors.
