## Context

Target: PCB rev A. Sources: `docs/research/pcb-components/ble_module.md`
and `discrete_parts.md`, both from 2026-11-25, with datasheet links and
the values quoted here. Values marked "to confirm" come from a secondary
source or could not be read, and a task confirms them before layout.

The supply is two AAA cells straight to the circuit: about 3.2 V fresh,
2.4 V on NiMH, a warning at 2.2 V under load, and the board must still run
at 2.0 V.

## Decisions

### 1. Block diagram

```
 2 x AAA ──┬── Q2 P-FET (reverse polarity) ──┬── VBAT
           │                                 │
           │      ┌──────────────────────────┼─────────────────────────────┐
           │      │                          │                             │
           │   C1 100 µF              U1 AN54LQ-15 (nRF54L15)         D1 IR LED + R1 10 Ω
           │   (by D1)                 VDD, DCC ── L1 4.7 µH               │
           │                           XL1/XL2 ── Y1 32.768 kHz           Q1 N-FET ── GND
           │                           P1 PWM ───────────────────────── gate (R2 to GND)
           │                           12 keys: P0/P1 ── SW1..SW12 ── GND (internal pull-ups)
           │                           P1 in  ── U2 TSMP96000 out
           │                           P2 out ── U2 VS (powered only while learning)
           │                           P2 out ── R3 ── D2 status LED ── GND
           │                           SWDIO, SWDCLK, RESET, VDD, GND ── J1 Tag-Connect pads
          GND
```

### 2. Parts

| Ref | Part | Datasheet values that decide it | LCSC | Alternate |
|-----|------|---------------------------------|------|-----------|
| U1 | Raytac AN54LQ-15, nRF54L15 module, chip antenna | VDD 1.7 to 3.6 V, reset needs at least 1.75 V; 13.7 x 9.5 x 1.8 mm (Nordic's list says 2.05 mm); 31 GPIO; FCC SH6AN54LQ, IC 8017A-AN54LQ, EU and UKCA declarations; System ON idle with RTC and 64 KB RAM 1.5 µA. Datasheet v1.3, raytac.com | C49419243, extended, Standard PCBA with X-ray | Raytac MDBT42Q-512KV2 (nRF52832), C2828282, 16 x 10 x 2.2 mm, no UKCA declaration |
| L1 | 4.7 µH, 0603, between DCC (pad 9) and DECD (pad 8) | Raytac reference circuit, datasheet v1.3 section 8. Without L1 the chip stays in LDO mode, which Nordic does not support for low power. Current rating at least 120 mA (Nordic, to confirm on the part picked) | to pick | |
| C2 | 4.7 µF, 0402, on VDD_NRF (pad 11) | Raytac reference circuit (their C10). DECD's 2.2 µF is inside the module | basic | |
| Y1 | 32.768 kHz crystal on XL1/XL2 (pads 12, 13), load capacitor footprints not fitted | The SDK expects it. Raytac's reference marks both load capacitors NC; the nRF54L15 sets the load internally, so the firmware's load setting must match the crystal's rated load (to set when the part is picked) | to pick | |
| SW1 to SW12 | XKB TS-1187A-C-C-B tactile switch, 260 gf | 2.6 N, inside the 1.5 to 3.0 N requirement with margin either side; 5.1 x 5.1 mm body, 1.7 mm high (height code C), round 2.0 mm brass stem, travel 0.2 mm (XKB drawing TS-1187A-X-X-X rev A0). Pads A and B are one contact, C and D the other. KiCad's `SW_Push_1P1T_XKB_TS-1187A` matches the drawing: four 1.0 x 0.75 mm pads, 7.0 and 5.0 mm across their outer and inner edges, 4.5 and 3.0 mm the other way. 260 gf and 300,000 cycles (XKB spec SP-A0162-53) | C318889 | XKB TS-1187A-B-A-B, 160 gf (1.57 N, too close to the 1.5 N floor), C318884, basic part |
| D1 | Vishay TSAL6200, 5 mm, 940 nm, laid flat at the top edge | Half angle 17 degrees; 72 mW/sr typical, 40 min at 100 mA; forward voltage 1.35 V typical, 1.6 V max at 100 mA; pulse rating covers 170 mA at 1/3 duty. About 12 m typical, 8.9 m worst case | C55528, extended, through hole | Vishay VSMB2948SL side-looking SMD, C6604342, about 6.3 m typical and 4.5 m worst case, short of 5 m |
| R1 | 10 Ohm, 0603 | About 170 mA at 3.2 V and 65 mA at 2.0 V through D1 | basic | |
| Q1 | AOS AO3416 N-channel MOSFET, SOT-23 | At most 34 mOhm at 1.8 V gate drive, so a GPIO turns it fully on from low cells. Its gate has 1.8 kOhm inside, and turn-off takes about 6 µs at 4.5 V drive (datasheet rev 5.1), against an 8.8 µs carrier pulse; the bench looks at the pulse shape at D1, and Si2312CDS is the swap if it smears | C43307, extended | Vishay Si2312CDS, at most 41.4 mOhm at 1.8 V, C142518. Not AO3400A: only specified from 2.5 V |
| R2 | 100 kOhm, 0603, Q1 gate to ground | Holds Q1 off while the chip resets, so D1 never stays on | basic | |
| Q2 | Diodes DMP2035U-7 P-channel MOSFET, SOT-23 | At most 62 mOhm at -1.8 V gate drive; about 9 mV drop at 150 mA | C110499, extended | AO3401A, C15127, basic, but only specified at -2.5 V |
| C1 | Samsung CL31A107MQHNNNE, 100 µF 6.3 V X5R 1206 | 1.6 mm thick. The initial insulation resistance (at least 50 MOhm x µF) allows up to 6.4 µA at 3.2 V; after Samsung's moisture test the floor is 3.5 MOhm x µF, up to about 91 µA, which would break the current budget. Typical MLCC leakage is far lower, and the idle-current bench check (7.2) measures it. Effective capacitance at 3 V not published in a readable form; assumed 40 to 60 µF, and the low-cells scenario checks the result | C15008, basic | Tantalum CA45A, 1.9 mm, 10 µA, C2976906 |
| U2 | Vishay TSMP96000, IR receiver with raw carrier output, side view SMD, at the top edge next to D1 | Panhead 7.5 W x 5.3 H x 4.0 D mm, standing 5.3 mm on the board with its lens to the side (datasheet rev 1.1, 2024-11-25, document 82906); pads 1 GND, 3 VS, 4 OUT at 1.27 mm pitch. 2.0 to 5.5 V; 0.35 mA typical, 0.45 mA max typical, 0.45 mA max, so powered from a GPIO only while learning; carrier out 30 to 60 kHz, so 36, 38, 40 and 56 kHz TV codes learn with their real frequency | C20346073, stock not shown | Vishay TSOP33338, 2.0 to 5.5 V, decoded 38 kHz only |
| R4, C5 | 100 Ohm 0603 in series to VS, 4.7 µF 0402 from VS to ground | Vishay's recommended supply filter (application circuit, document 82906) | basic | |
| R5 | 4.7 kOhm 0603, OUT pull-up to U2's switched supply | Vishay's recommended pull-up for fast edges and a clean high level; output sinks at most 5 mA | basic | |
| D2 | Kingbright APTD1608LSECK/J4-PF, orange, 0603 | Forward voltage 1.8 V typical, 2.1 V max at 2 mA, bright at low current | C5879215, extended | Kingbright APTD1608LCGCK yellow-green, C5342733, about 50 times dimmer |
| R3 | 330 Ohm, 0603 | About 1.2 mA at 2.2 V and 4 mA at 3.2 V with a typical LED; firmware PWM evens out the brightness | basic | |
| BT1 | Keystone 5204 (negative) and 5226 (positive) AAA contacts, soldered by a tab to the board edge; Keystone 5213 or 5214 bridge contact in the door | Low enough for a 14 mm battery end; PCB-mount AAA spring contacts are 11 to 20 mm tall | not stocked, buy from Digi-Key | Keystone 230-1 board-edge contact, mounting to confirm |
| J1 | Tag-Connect TC2030-NL footprint | No part on the board; the TC2030-CTX-NL cable fits the DK's debug header. KiCad's `Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical` matches drawing TC2030-IDC-NL-FP rev B: six 0.787 mm pads at 1.27 mm, three 0.991 mm unplated holes, no paste. Layout rules from the drawing: no track or via between the pads, other tracks 0.5 mm clear. J1 and the test points are out of the BOM and placement file | none | 2 x 5 1.27 mm header |

### 3. Pin plan

Rules from the nRF54L15: only P0 and P1 can wake the chip (P2 cannot),
the PWM only drives P1, and the 32.768 kHz crystal takes P1.00 and P1.01.
That leaves 18 wake-capable pins for 13 inputs.

| Net | Pin (pad) | Port rule |
|-----|-----------|-----------|
| KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_SELECT | P0.00 (34), P0.01 (35), P0.02 (41), P0.03 (38), P0.04 (40) | Wake on any key; latched detect mode against erratum 114 |
| KEY_BACK, KEY_HOME, KEY_PLAY, KEY_VOLUP, KEY_VOLDN | P1.04 (17) to P1.08 (21) | Same |
| KEY_MUTE, KEY_POWER | P1.09 (2), P1.10 (3) | Same |
| IR_LED (Q1 gate) | P1.11 (4) | PWM20 |
| IR_RX (U2 output) | P1.12 (5) | GPIOTE and timer capture |
| STATUS_LED | P2.00 (22) | Output only |
| IR_RX_PWR (U2 supply) | P2.01 (23) | Output only |
| SWDIO, SWDCLK, RESET | 36, 37, 39 | Dedicated |
| Spare | P1.02, P1.03, P1.13, P1.14, P2.02 to P2.10 | No-connect flags |

Layout may swap pins within the same port rule to ease routing; the
schematic and this table change together.

Module pads, from the AN54LQ datasheet v1.3 pin table and reference
circuit: P1.09 to P1.14 on pads 2 to 7, P1.00 and P1.01 (crystal) on 12
and 13, P1.02 to P1.08 on 15 to 21, P2.00 to P2.03 on 22 to 25, P2.04 to
P2.10 on 27 to 33, P0.00 and P0.01 on 34 and 35, SWDIO 36, SWDCLK 37,
P0.03 on 38, RESET 39, P0.04 on 40, P0.02 on 41. VDD_NRF 11, DCC 9,
DECD 8; GND on 1, 10, 14, 26, 42 and 43.

P0.03 and P0.04 stay keys; their GRTC PWM and CLKOUT32K functions are not
needed. P1.02 and P1.03 default to NFC; they are left for other uses and
set to GPIO in firmware if used, since NFC is not fitted.

### 4. Power checks

- Supply range: 3.2 V fresh is under the 3.6 V maximum. Lithium AAA cells
  (about 1.8 V each fresh) would put 3.6 V on the module, at the limit, so
  the battery door label says alkaline or NiMH.
- Reset margin: at 2.0 V with about 1 Ohm per worn cell (to confirm on the
  bench), a 65 mA IR burst sags the supply by about 0.13 V to 1.87 V, above
  the 1.75 V reset level. C1 smooths the 38 kHz ripple: one 8.8 µs carrier
  pulse at 170 mA moves 1.5 µC, about 30 mV on 50 µF. The
  `pcb-assembly/low-cells-keep-it-running` scenario checks this with a
  scope.
- IR charge per press: an NEC frame has about 27.5 ms of carrier at 1/3
  duty, so about 1.6 mC at 170 mA, or 0.43 µAh per frame.
- Status light: works from 2.2 V with a typical LED; a worst-case LED
  (2.1 V) can stay dark near 2.0 V, so the low-battery warning starts at
  2.2 V and is also reported over Bluetooth.

Current budget, alkaline, 200 presses a day:

| Load | Average |
|------|---------|
| nRF54L15 idle with RTC and RAM | 1.5 µA (datasheet) |
| Bluetooth connected with a long interval and latency | 5 to 15 µA (secondary source, to measure) |
| C1 leakage | up to 6.4 µA at the initial spec, far less typical; measured in 7.2 |
| U2, D2, key pull-ups | 0 when idle |
| IR frames when Bluetooth is down, 1.5 frames a press | about 5 µA if every press went over IR |

Worst case about 28 µA, or about 250 mAh a year, against about 1000 mAh
in an alkaline AAA pair: about four years, against the two-year
requirement.

### 5. Height

All parts on the top side; the bottom is flat against the shell. Tallest
in the key area: the module at 1.8 mm (2.05 mm per Nordic's list), the
switches at 1.7 mm, C1 at 1.6 mm. Stack over the keys: 1.2 mm wall, 1.0 mm
board, about 2 mm of parts, clearance, 1.2 mm top wall and caps 1.5 mm
proud: about 7.5 to 8 mm, under the 11 mm limit.

Two parts at the top edge stand taller and both look out of the top end:
the 5 mm IR LED laid flat and U2 at 5.3 mm. With 1.2 mm walls above and
below and the 1.0 mm board, the top end is about 9 mm, still under 11 mm.
A board cutout under U2 could lower it by the board's thickness if the
enclosure needs it.

### 6. Board

- Two layers, 1.0 mm FR-4, about 37 by 100 mm, the outline following the
  shell's top corners and stopping at the battery bay.
- U1 in the top right corner, antenna end up. Raytac's drawing (datasheet
  v1.3 section 2.3) puts the module's antenna end on a board edge, with
  ground pour under and around the module, a 7.35 by 3.3 mm "no ground-pad
  area" under the antenna end starting 1 mm in from the module's left
  edge, and at least 15 mm of ground beside the antenna. The board steps
  down 3.5 mm at the top right so that edge is straight; the module sits
  0.3 mm in from it so its corner ground pads keep the fab's edge
  clearance. The no-ground area is a rule area with no pour, tracks or
  vias on either layer. To the module's left is about 21 mm of ground.
- The module's supply and crystal pads (1 to 13) are on its left side, so
  the module takes the right corner and they face the board. Power moves
  from the top right in `front.svg` to the top left.
- The IR LED and receiver share the top edge's window, LED at about 15 mm
  and receiver at about 22 mm from the left. The status light sits below
  them, above the d-pad.
- Battery contacts on the bottom edge, solder tabs on pads.
- Test points: VBAT, GND, IR gate.

### 7. Assembler: JLCPCB Standard PCBA

The module needs Standard PCBA with X-ray, which also covers the
through-hole IR LED as an option. Five boards made, two or more
assembled. PCBWay is the alternate if JLCPCB has no stock of the module
or U2 and parts must be sent in. Battery contacts come from Digi-Key and
are soldered at home.

LCSC stock on 2026-11-26, read from LCSC's product API (`wmsc.lcsc.com`,
product detail by C number). A board takes one of each, twelve switches:

| Ref | Part | LCSC | In stock | Enough for 5 boards |
|-----|------|------|----------|---------------------|
| U1 | AN54LQ-15 | C49419243 | 0 | No |
| SW1 to SW12 | TS-1187A-C-C-B | C318889 | 111,060 | Yes |
| D1 | TSAL6200 | C55528 | 8,560 | Yes |
| Q1 | AO3416 | C43307 | 18,565 | Yes |
| Q2 | DMP2035U-7 | C110499 | 218,185 | Yes |
| C1 | CL31A107MQHNNNE | C15008 | 1,476,310 | Yes |
| U2 | TSMP96000TR | C20346073 | 53 | Yes, but thin |
| D2 | APTD1608LSECK/J4-PF | C5879215 | 655 | Yes |

Alternates: MDBT42Q-512KV2 (C2828282) 0, TS-1187A-B-A-B (C318884) 338,960,
VSMB2948SL (C6604342) 197, Si2312CDS (C142518) 9,410, AO3401A (C15127)
531,690, CA45A (C2976906) 26,865, APTD1608LCGCK (C5342733) 1,395.

L1, Y1 and the 0603/0402 passives are picked from JLCPCB basic parts
when the BOM is exported.

The module is the gap, and its alternate is out too. Digi-Key lists the
AN54LQ-15 as 3271-AN54LQ-15-ND, with small stock that varies by regional
site. The route: order it through JLCPCB Global Sourcing, which buys from
Digi-Key or Mouser into JLCPCB's warehouse (9 to 15 days, no refunds once
paid). If Global Sourcing cannot get it, buy from Digi-Key and consign the
modules to JLCPCB. Recheck U2 and the module just before ordering; U2 at 53
can run out.

### 8. Layout as code

`hardware/pcb/layout/build_board.py` builds the board from the schematic
netlist: outline, every part's position, the ground pours and the antenna
rule area. It runs in KiCad's Python with `pcbnew`
(`scripts/build-board.sh`). Positions are in shell coordinates, the ones
`front.svg` uses, so a key moves by editing one line. Freerouting 2.5.0
routes it from a Specctra export (`scripts/route-board.sh`), net classes
give the supply and IR LED nets 0.4 mm tracks, and DRC runs on the
result. Hand-placing in the KiCad editor was considered; it leaves no
record of why a part sits where it does and does not rebuild after a
schematic change.

Layout starts before the bench in `prove-the-apple-tv-link`, at the
owner's call on 2026-11-26, since no DK has been bought yet. If the bench
changes a pin or a part, the script rebuilds the board.

### 9. KiCad 10 with a repo-local library

KiCad 10.0.8. The schematic was first generated from decisions 1 to 3
with one net label per pin, so every connection reads by name, and is now
edited in KiCad. ERC runs in CI and in `scripts/fast-checks.sh`.

Library, `hardware/pcb/lib/`:

- U1 and U2 symbols, footprints and STEP models come from LCSC through
  `easyeda2kicad`, checked against the datasheets: U1's 43 pads match
  Raytac's top view (the import had the corner ground pads 42 and 43
  swapped, now fixed); U2's four 0.9 by 2.2 mm pads at 1.27 mm pitch and
  pinout match Vishay's drawing. Pin types were set by function so ERC
  means something; U1's RESET is passive, since only the debugger drives
  it against the internal pull-up.
- `Keystone_AAAx2_EdgeTabs` is drawn here: two pads on 11.5 mm centers for
  the contact tabs, the spacing of the 5213/5214 bridge's two contacts
  (.453 in on Keystone's catalog page 17), so the cells line up at both ends. Pad sizes are confirmed against Keystone's drawings in
  layout.
- Everything else uses KiCad's own symbols and footprints, including
  `SW_Push_1P1T_XKB_TS-1187A` and the horizontal 5 mm LED with IR body.

Why KiCad: its files are text and review as diffs, and `kicad-cli` runs ERC, DRC
and the fab outputs in CI. Symbols and footprints for LCSC parts come in
through `easyeda2kicad` into `hardware/pcb/lib/`, and each is checked
against its datasheet's drawing before use. EasyEDA was considered for
its one-click ordering and rejected: its projects live in its cloud and do
not diff in git.

## Risks / Trade-offs

- The antenna edge is 3.5 mm below the top edge to its left, so the
  ground there reaches past the antenna's end, which Raytac's drawing does
  not show. Raytac reviews layouts for free (sales@raytac.com); send the
  board before ordering.

- LCSC has no AN54LQ-15 (2026-11-26) and only 53 TSMP96000. The module
  comes through JLCPCB Global Sourcing or consignment (decision 7), which
  adds about two weeks and a markup.
- The 5 mm IR LED laid flat is the only part with margin for 5 m, and it
  sets the top end's thickness.
- Early AN54LQ lots used nRF54L15 revision 1 silicon. The order asks for
  revision 2 (build code C00).

## Open Questions

None.
