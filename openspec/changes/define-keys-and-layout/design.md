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
  centered 38 mm from the top.
- Back (round) at left and Home (rounded square) at right, 64 mm from the
  top, 20 mm apart.
- Play/pause, 11 mm across, centered 78 mm from the top.
- Mute (round) at left and a volume rocker, 9 by 24 mm, at right, around
  100 mm from the top.
- Bottom 45 mm: the battery end, no keys.

Options considered: volume on the side edge (easy to press by accident
when gripping, harder to print), and play/pause inside the d-pad ring
(fewer keys to find but a crowded center). Both rejected.

### 2. Profile: a wedge

13 mm thick at the top, 20 mm at the battery end, so the weight sits in
the palm. A flat slab at 20 mm was considered: simpler to print, but heavy
at the top and thicker than it needs to be where the thumb works.

### 3. Batteries side by side at the bottom

Two AAA cells side by side need about 23 mm of width and 46 mm of length
inside the bottom end, under the PCB. End to end along the back was
considered: it allows a narrower body, about 32 mm, but spreads the
weight along the whole length and pushes the thickness the full length.
Side by side keeps the top thin and the balance low.

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
clickpad. This remote is wider, longer, a wedge up to 20 mm thick, matte
printed plastic, with a separate-key d-pad and no touch surface. No Apple
names or glyphs: the Home key shows a generic TV glyph, not Apple's.

### 9. Grip mock-up in code

A first enclosure file, `hardware/enclosure/mockup.py`, builds the outer
wedge with key bumps at the board's positions, using build123d, to print
and hold. It is not the enclosure: no PCB, no battery door. The real
enclosure change replaces it and reads key positions from the PCB.

## Risks / Trade-offs

- A wedge at 20 mm may feel chunky next to a Siri Remote. The mock-up
  settles it before the PCB is laid out.
- Printed caps can wobble in printed guides. The enclosure change sets
  clearances from test prints.

## Open Questions

- Whether volume keys stay, depending on the bench in
  `prove-the-apple-tv-link`.
- Colors of the shell and keys.
