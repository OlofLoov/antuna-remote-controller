## Context

Target: no board revision yet. These decisions feed PCB rev A and
enclosure rev A. The board in `boards/front.svg` is the intent; once the
PCB exists, its placement export is the one source for key positions.

## Decisions

### 1. Layout, top to bottom

Drawn in `boards/front.svg`, 40 by 150 mm:

- Top edge: IR window. Top face: status light at center, Power at upper
  right, recessed in a ring.
- D-pad ring, 30 mm across, with select in the middle, 14 mm across,
  centered 36 mm from the top.
- Back (round) at left and Home (rounded square) at right, 60 mm from the
  top, 20 mm apart.
- Play/pause, 11 mm across, centered 73 mm from the top.
- Mute (round) at left and a volume rocker, 9 by 20 mm, at right, around
  90 mm from the top.
- From 104 mm down: the battery bay, past the end of the PCB, no keys.

Options considered: volume on the side edge (easy to press by accident
when gripping, harder to print), and play/pause inside the d-pad ring
(fewer keys to find but a crowded center). Both rejected.

### 2. Profile: thin over the keys, thicker only where the cells are

At most 11 mm over the keys, caps included, rising to at most 14 mm at
the battery end. The owner found 20 mm too chunky on 2026-11-25.

The stack over the keys, bottom to top: 1.2 mm wall, 1.0 mm PCB with every
part on the top side, about 2 to 2.5 mm for the module and the switches,
1.2 mm top wall, and caps standing about 1.5 mm proud. That is about
8.5 to 9.5 mm, which leaves margin under 11 mm. The final numbers come
from the parts picked in the PCB change.

### 3. Batteries beside the PCB, not under it

An AAA cell is 10.5 mm across, so any cell under the PCB sets the
thickness at about 18 mm or more. The cells instead lie side by side in
the bottom 46 mm, past the end of the PCB: 10.5 mm plus two 1.2 mm walls
and clearance gives about 13.5 mm there. The PCB stops at the battery
bay. Spring contacts on the PCB's bottom edge meet one end of the cells,
and a bridge contact in the battery door joins the far ends in series.

Options considered: cells under the PCB (about 18 to 20 mm, the first
draft), and cells end to end along the back (a narrower body, about
32 mm, but 10.5 mm of cell under most of the PCB, so thick for the whole
length). Both rejected.

### 4. Key mechanism: SMD tactile switches under printed caps

| Option | Click | Parts | Home-printable | Cost at 10 units |
|--------|-------|-------|----------------|------------------|
| SMD tactile switches on the PCB, printed caps in printed guides | Crisp, set by the switch | Switches placed by the assembler | Yes | Low |
| Silicone rubber keypad over carbon pads | Soft, set by the dome | Custom mold | No | High setup |
| Printed TPU membrane over tactile switches | Muted | Same switches | Yes, with TPU | Low |

Tactile switches under printed caps. The switch sets the force, so the
"every press clicks" range is met by choosing a switch rated in it, for
example a 160 gf (1.6 N) or 250 gf (2.5 N) part. The part number is picked
in the PCB change from the assembler's stock. A TPU membrane stays an
option if the printed caps rattle.

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

A single small LED behind a thin spot in the shell or a translucent PETG
insert. Colors and patterns: blinking for pairing mode, a short double
blink on a press when the battery is low (see `define-power`). RGB was
considered and rejected: more parts, more firmware, little gain.

### 8. Not a Siri Remote

The Siri Remote (2021) is about 36 by 136 by 9 mm, aluminum, with a
clickpad. This remote is wider and longer, steps up to 14 mm at the
battery end, is bright teal matte plastic, and has a separate-key d-pad
and no touch surface. No Apple
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

A first enclosure file, `hardware/enclosure/mockup.py`, builds the outer
wedge with key bumps at the board's positions, using build123d, to print
and hold. It is not the enclosure: no PCB, no battery door. The real
enclosure change replaces it and reads key positions from the PCB.

## Risks / Trade-offs

- 11 mm over the keys depends on the module and switch heights. The PCB
  change confirms the stack from datasheets before layout.
- Printed caps can wobble in printed guides. The enclosure change sets
  clearances from test prints.

## Open Questions

- Filament brands and how close they get to the brand colors.
