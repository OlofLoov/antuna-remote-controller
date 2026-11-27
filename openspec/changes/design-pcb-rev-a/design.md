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
           │                           P1 in  ── U2 TSMP96000 out (R5 pull-up to the P2 pin)
           │                           P2 out ── R4 ── U2 VS, C5 (powered only while learning)
           │                           P2 out ── R3 ── D2 status LED ── GND
           │                           SWDIO, SWDCLK, RESET, VDD, GND ── J1 Tag-Connect pads
          GND
```

### 2. Parts

| Ref | Part | Datasheet values that decide it | LCSC | Alternate |
|-----|------|---------------------------------|------|-----------|
| U1 | Raytac AN54LQ-15, nRF54L15 module, chip antenna | VDD 1.7 to 3.6 V, reset needs at least 1.75 V; 13.7 x 9.5 x 1.8 mm (Nordic's list says 2.05 mm); 31 GPIO; FCC SH6AN54LQ, IC 8017A-AN54LQ, EU and UKCA declarations; System ON idle with RTC and 64 KB RAM 1.5 µA. Datasheet v1.3, raytac.com | C49419243, extended, Standard PCBA with X-ray | Raytac MDBT42Q-512KV2 (nRF52832), C2828282, 16 x 10 x 2.2 mm, no UKCA declaration |
| L1 | Murata LQM18PN4R7MFRL, 4.7 µH 20 %, 0603, between DCC (pad 9) and DECD (pad 8) | Raytac reference circuit, datasheet v1.3 section 8. Without L1 the chip stays in LDO mode, which Nordic does not support for low power. 620 mA and 550 mOhm, against the 120 mA and at most 650 mOhm of the inductor in Nordic's reference design. Multilayer and shielded, beside the crystal | C114862, extended | |
| C2 | Samsung CL05A475MP5NRNC, 4.7 µF 10 V X5R, 0402, on VDD_NRF (pad 11) | Raytac reference circuit (their C10). DECD's 2.2 µF is inside the module | C23733, basic | |
| Y1 | ECS ECS-.327-7-34B-C-TR, 32.768 kHz, 3.2 x 1.5 mm, on XL1/XL2 (pads 12, 13), no load capacitors | The SDK expects it. 7 pF load and 70 kOhm series resistance, 1.05 pF shunt and up to 1.0 µW drive, inside what the nRF54L15's oscillator takes: 6 to 9 pF load, at most 100 kOhm, at most 2.0 pF shunt, and it drives at most 0.5 µW (Nordic's datasheet, table "32.768 kHz crystal oscillator (LFXO)", read 2026-11-27). The chip sets the load with its internal capacitors, which is why Raytac's reference marks both load capacitors NC; the board has no footprints for them, so the crystal's tracks have no stubs. The internal capacitors go from 3 to 18 pF in 0.65 pF steps; firmware asks for 7 pF less about 1 pF of pad and track. The cheapest 3215 crystal at LCSC, Epson's C32346, is 12.5 pF and out of range | C2450085, extended | HCI FC31M2-32.768-N07LLDTL, 7 pF, C5120558 |
| SW1 to SW12 | XKB TS-1187A-C-C-B tactile switch, 260 gf | 2.6 N, inside the 1.5 to 3.0 N requirement with margin either side; 5.1 x 5.1 mm body, 1.7 mm high (height code C), round 2.0 mm brass stem, travel 0.2 mm (XKB drawing TS-1187A-X-X-X rev A0). Pads A and B are one contact, C and D the other. KiCad's `SW_Push_1P1T_XKB_TS-1187A` matches the drawing: four 1.0 x 0.75 mm pads, 7.0 and 5.0 mm across their outer and inner edges, 4.5 and 3.0 mm the other way. 260 gf and 300,000 cycles (XKB spec SP-A0162-53) | C318889 | XKB TS-1187A-B-A-B, 160 gf (1.57 N, too close to the 1.5 N floor), C318884, basic part |
| D1 | Vishay TSAL6200, 5 mm, 940 nm, laid flat at the top edge | Half angle 17 degrees; 72 mW/sr typical, 40 min at 100 mA; forward voltage 1.35 V typical, 1.6 V max at 100 mA; pulse rating covers 170 mA at 1/3 duty. About 12 m typical, 8.9 m worst case | C55528, extended, through hole | Vishay VSMB2948SL side-looking SMD, C6604342, about 6.3 m typical and 4.5 m worst case, short of 5 m |
| R1 | 10 Ohm, 0805, 125 mW | About 170 mA at 3.2 V and 65 mA at 2.0 V through D1. 0.3 W during a carrier pulse and about 0.1 W averaged over a burst at 1/3 duty, so 0805, not 0603. A gate stuck high would put about 180 mA through D1 for good, over its 100 mA continuous rating: firmware drives the pin only from the PWM and R2 holds it low otherwise | C17415, basic | |
| Q1 | AOS AO3416 N-channel MOSFET, SOT-23 | At most 34 mOhm at 1.8 V gate drive, so a GPIO turns it fully on from low cells. Its gate has 1.8 kOhm inside, and turn-off takes about 6 µs at 4.5 V drive (datasheet rev 5.1), against an 8.8 µs carrier pulse; the bench looks at the pulse shape at D1, and Si2312CDS is the swap if it smears. A slow turn-off stretches each pulse toward half the period, which raises the LED's and R1's power by up to about 60 %; firmware shortens the PWM on-time by what the bench measures | C43307, extended | Vishay Si2312CDS, at most 41.4 mOhm at 1.8 V, C142518. Not AO3400A: only specified from 2.5 V |
| R2 | 100 kOhm, 0603, Q1 gate to ground | Holds Q1 off while the chip resets, so D1 never stays on | C25803, basic | |
| Q2 | Diodes DMP2035U-7 P-channel MOSFET, SOT-23 | At most 62 mOhm at -1.8 V gate drive; about 9 mV drop at 150 mA | C110499, extended | AO3401A, C15127, basic, but only specified from -2.5 V, so not a swap for cells below that |
| C1 | Samsung CL31A107MQHNNNE, 100 µF 6.3 V X5R 1206 | 1.6 mm thick. The initial insulation resistance (at least 50 MOhm x µF) allows up to 6.4 µA at 3.2 V; after Samsung's moisture test the floor is 3.5 MOhm x µF, up to about 91 µA, which would break the current budget. Typical MLCC leakage is far lower, and the idle-current bench check (7.2) measures it. Effective capacitance at 3 V not published in a readable form; assumed 40 to 60 µF, and the low-cells scenario checks the result | C15008, basic | Tantalum CA45A, 1.9 mm, 10 µA, C2976906 |
| U2 | Vishay TSMP96000, IR receiver with raw carrier output, side view SMD, at the top edge next to D1 | Panhead 7.5 W x 5.3 H x 4.0 D mm, standing 5.3 mm on the board with its lens to the side (datasheet rev 1.1, 2024-11-25, document 82906); pads 1 GND, 3 VS, 4 OUT at 1.27 mm pitch. 2.0 to 5.5 V; 0.35 mA typical, 0.45 mA max, so powered from a GPIO only while learning; carrier out 30 to 60 kHz, so 36, 38, 40 and 56 kHz TV codes learn with their real frequency | C20346073, stock not shown | Vishay TSOP33338, 2.0 to 5.5 V, decoded 38 kHz only |
| R4, C5 | 100 Ohm 0603 in series to VS, 4.7 µF 0402 (as C2) from VS to ground | Vishay's recommended supply filter (application circuit, document 82906), under U2's pads | C22775 and C23733, basic | |
| R5 | 4.7 kOhm 0603, OUT pull-up to the pin that powers U2 | Vishay's recommended pull-up for fast edges and a clean high level; output sinks at most 5 mA. It returns to the pin side of R4, so its 0.4 mA while OUT is low does not drop VS across R4 | C23162, basic | |
| D2 | Kingbright APTD1608LSECK/J4-PF, orange, 0603 | Forward voltage 1.8 V typical, 2.1 V max at 2 mA, bright at low current | C5879215, extended | Kingbright APTD1608LCGCK yellow-green, C5342733, about 50 times dimmer |
| R3 | 330 Ohm, 0603 | About 1.2 mA at 2.2 V and 4 mA at 3.2 V with a typical LED. The pin is on P2, which has no PWM, so firmware evens out the brightness by switching the pin from a timer | C23138, basic (LCSC's own stock was 0 on 2026-11-27) | Yageo RC0603FR-07330RL, C105881, 7.1 million in stock on 2026-11-27 |
| BT1 | Two plated 1.0 mm holes on 11.5 mm centers for wires from the battery contacts. The contacts sit in the shell: Keystone 5204 (negative) and 5226 (positive) by the board, a 5213 or 5214 bridge at the far end | The contact plates stand at right angles to the board, so the shell holds them and takes the springs' push (`define-keys-and-layout` decision 3). 49.5 mm between the plates for AAA (Keystone catalog page 42). PCB-mount AAA spring contacts are 11 to 20 mm tall, too tall for a 14 mm battery end | contacts not stocked, buy from Digi-Key | Keystone 230-1 board-edge contact, mounting to confirm |
| J1 | Tag-Connect TC2030-NL footprint | No part on the board; the TC2030-CTX-NL cable fits the DK's debug header. KiCad's `Tag-Connect_TC2030-IDC-NL_2x03_P1.27mm_Vertical` matches drawing TC2030-IDC-NL-FP rev B: six 0.787 mm pads at 1.27 mm, three 0.991 mm unplated holes, no paste. Layout rules from the drawing: no track or via between the pads, other copper 0.5 mm clear, which `antuna-remote.kicad_dru` checks. J1 and the test points are out of the BOM and placement file | none | 2 x 5 1.27 mm header |

### 3. Pin plan

Rules from the nRF54L15: only P0 and P1 can wake the chip or raise a pin
event (P2 cannot), the PWM only drives P1, and the 32.768 kHz crystal
takes P1.00 and P1.01. The module brings 16 such pins to its edge, for 12
keys, the IR output and the IR input.

| Net | Pin (pad) | Port rule |
|-----|-----------|-----------|
| KEY_HOME, KEY_RIGHT, KEY_POWER | P0.00 (34), P0.01 (35), P0.03 (38) | Wake on any key; latched detect mode against erratum 114 |
| KEY_LEFT, KEY_DOWN, KEY_SELECT, KEY_UP | P1.11 (4) to P1.14 (7) | Same |
| KEY_MUTE, KEY_BACK | P1.02 (15), P1.03 (16) | Same; the NFC pads, set to GPIO in firmware |
| KEY_PLAY, KEY_VOLUP, KEY_VOLDN | P1.04 (17) to P1.06 (19) | Same |
| IR_RX (U2 output) | P1.07 (20) | GPIOTE and timer capture |
| IR_LED (Q1 gate) | P1.08 (21) | PWM20 |
| STATUS_LED | P2.09 (32) | Output only, high drive |
| IR_RX_PWR (U2 supply) | P2.10 (33) | Output only, high drive |
| SWDIO, SWDCLK, RESET | 36, 37, 39 | Dedicated |
| Spare | P0.02, P0.04, P1.09, P1.10, P2.00 to P2.08 | No-connect flags |

Layout may swap pins within the same port rule to ease routing; the
schematic and this table change together. The plan follows where each
pad sits on the module, so that no track has to pass under it:

- P0.02 and P0.04 are on pads 41 and 40, inside the module's pad ring,
  where only a track under the module could reach them. Raytac's drawing
  keeps that area for ground, so they stay spare.
- Pads 2 to 13 face the channel left of the module, which also holds the
  inductor, the supply capacitor and the crystal. Only four key lines use
  it. They are quiet, which matters beside the crystal; the 38 kHz IR
  output is on the bottom row, away from it.
- Pads 15 to 21 on the bottom row carry the keys further down the board
  and the two IR signals.
- Pads 27 to 39 face right, toward Power, the programming pads, the
  status light and the IR receiver, so the three P0 keys and the two P2
  outputs are there.
- The two NFC pads both carry keys, which idle high together. Nordic's
  datasheet (NFCT, "Pin configuration", read 2026-11-27) says to expect
  "some increased leakage current between the two pins" when they sit at
  different levels, as a key and the unpowered receiver's output would,
  and that both must be at the same level before a power-saving mode. It
  gives no figure. The pads have 5 pF each against 1 pF for other pins,
  which a key does not notice.

Module pads, from the AN54LQ datasheet v1.3 pin table and reference
circuit: P1.09 to P1.14 on pads 2 to 7, P1.00 and P1.01 (crystal) on 12
and 13, P1.02 to P1.08 on 15 to 21, P2.00 to P2.03 on 22 to 25, P2.04 to
P2.10 on 27 to 33, P0.00 and P0.01 on 34 and 35, SWDIO 36, SWDCLK 37,
P0.03 on 38, RESET 39, P0.04 on 40, P0.02 on 41. VDD_NRF 11, DCC 9,
DECD 8; GND on 1, 10, 14, 26, 42 and 43.

What the firmware must do because of this board:

- Set the NFC pads to GPIO (`nfct-pins-as-gpios` on the devicetree's
  `nfct` node). They are NFC pads after reset. Pull both key lines the
  same way, so they sleep at the same level.
- Use high drive on P2.09 and P2.10. A standard-drive pin only promises
  0.5 mA at 0.4 V below the supply, and U2 with its filter needs more
  (decision 4).
- Never pull IR_RX up while U2 is off: its output may sit at most 0.3 V
  above its supply.
- Wait 20 ms after switching U2 on before reading it; C5 charges through
  R4 within a few milliseconds.
- Drop a key's pull-up after it has been held for a minute: a stuck key
  draws about 0.23 mA through the 14 kOhm pull-up.
- Leave RESET alone during power-up (errata 100 and 103).

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
- IR receiver: U2 needs 2.0 V and draws up to 0.45 mA through R4 and the
  pin that powers it. With high drive that costs about 0.1 V, so learning
  works down to about 2.2 V of battery, and firmware refuses to learn
  below that. Sending does not use U2.
- Brown-out: the chip resets at 1.57 to 1.64 V (Nordic) and needs 1.75 V
  to start, so worn cells that sag below 1.75 V with no load will not
  start it.
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
| Q2 gate leakage | about 0.03 µA typical at 3 V (DMP2035U figure 11) |
| IR frames when Bluetooth is down, 1.5 frames a press | about 5 µA if every press went over IR |

Worst case about 28 µA, or about 250 mAh a year, against about 1000 mAh
in an alkaline AAA pair: about four years, against the two-year
requirement.

### 5. Height

All parts on the top side. Tallest in the key area: the module at 1.8 mm
(2.05 mm per Nordic's list), the switches at 1.7 mm, C1 at 1.6 mm. Stack
over the keys: 1.2 mm back wall, 0.5 mm of ribs, 1.0 mm board, 1.7 mm
switch, 0.3 mm clearance, 1.2 mm front wall and caps 1.5 mm proud: about
6 mm of body and 7.5 mm with the caps.

Two parts at the top edge stand taller and both look out of the top end.
The IR LED lies flat with its axis 3.0 mm above the board, and its
5.8 mm flange reaches 5.9 mm; U2 stands 5.3 mm. Over the same back wall
and ribs that is 1.7 + 1.0 + 5.9 + 0.3 + 1.2 = 10.1 mm, under the 11 mm
limit, and it sets the head in `define-keys-and-layout` decision 2. The
LED is through hole, so its two leads stick out under the board; they
are clipped to 0.5 mm, which is what the ribs are for.

### 6. Board

- Two layers, 1.0 mm FR-4, 36 by 98 mm, 2 mm inside the shell all round,
  the outline following the shell's top corners and stopping 1 mm short
  of the battery contacts.
- U1 in the top left corner, antenna end up. Raytac's drawings (datasheet
  v1.3 sections 2.2 and 2.3) put the module's antenna end on a board
  edge, ground pour under and around the module with only ground vias
  under it, no ground under the antenna end, and at least 15 mm of ground
  to the module's right. The no-ground area is a T, 3.3 mm deep: 7.35 mm
  wide between the corner ground pads for the first 1.2 mm, then the
  module's full 9.5 mm.
- The board steps down 3 mm left of x = 19.4 mm so the antenna end sits
  on that edge; the module sits 0.3 mm in from it so its corner ground
  pads keep the fab's edge clearance. Right of the step, 2.9 mm from the
  module, the board reaches the top edge for the IR parts. That part has
  no pour, so the ground ends level with the antenna end, as in the
  drawing.
- Rule areas: the T (no pour, tracks or vias); a band across the antenna
  end from the left edge to 3.5 mm right of the module (no tracks or
  vias); from there to the IR receiver's pads, level with the antenna
  (no tracks); on to 15.5 mm from the module, under the receiver, on the
  bottom layer (no tracks); the inside of the pad ring (no tracks); the
  whole module outline plus 0.5 mm on the bottom layer (no tracks); and
  under the crystal on the bottom layer (no tracks). `antuna-remote.kicad_dru`
  lets DRC pass only ground vias under the module, beside the antenna
  and under the receiver. Measured on the routed board: no pour in the
  T, no track under the module or in the band, and from the module's
  right edge 15 mm of unbroken ground on the bottom layer level with
  the antenna. The top layer is unbroken for the first 10 mm; in the
  last 5 mm it carries the receiver's pads, its filter and the short
  tracks between them, with pour around them.
- The module's supply and crystal pads (8 to 13) face the left edge, 5 mm
  away. L1, C2 and Y1 sit beside their own pads there, and
  `build_board.py` draws their tracks: the crystal's are 1.6 and 3.4 mm
  long with ground under them, and the DC/DC's two are 2.8 and 5.0 mm at
  0.3 and 0.25 mm wide. The four key lines from pads 4 to 7 pass under L1
  on the bottom layer, left of the crystal.
- Power at the top right, as in `front.svg`.
- The IR LED and receiver look out of the top wall right of the step, LED
  23 mm and receiver 30 mm from the left. The LED's lens reaches 1.3 mm
  past the board's edge, into its hole in the wall. The status light sits
  under the LED, centred, 14 mm from the top.
- The IR pulse's loop is drawn tight: C1's ground pad sits under Q1's
  source with a track between them, and R1 beside C1's other pad.
- Four unplated 2.2 mm holes for M2 screws, each with 2.5 mm around its
  centre free of copper for the shell's boss
  (`define-keys-and-layout` decision 11).
- Two plated holes at the bottom edge for the battery wires.
- Programming pads: `build_board.py` draws each pad's track straight out
  of the pad field and keeps the router out of it.
- Test points: VBAT, GND, IR gate.
- No fiducials or tooling holes: the board is narrower than JLCPCB's
  70 mm minimum for assembly, so they add rails with their own.

### 7. Assembler: JLCPCB Standard PCBA

The module needs Standard PCBA with X-ray, which also covers the
through-hole IR LED as an option. Five boards made, two or more
assembled. PCBWay is the alternate if JLCPCB has no stock of the module
or U2 and parts must be sent in. Battery contacts come from Digi-Key;
their two wires are soldered at home.

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

L1, Y1 and the passives carry their LCSC numbers in the schematic, read
from the same API on 2026-11-27: L1 159,490, Y1 3,628 (alternate 1,270),
the 4.7 µF 2,558,550, and the resistors in the millions except the
330 Ohm at 0 in LCSC's own stock, a JLCPCB basic part to recheck in the
quote.

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
give the supply and IR LED nets 0.4 mm tracks, and the board rules keep
every track at 0.127 mm or more. The thinnest on the board are 0.15 mm.
The router runs on one thread, so the machine's core count cannot change
its result.
`build_board.py` names every item by what it is and where it sits
instead of KiCad's random ids, so the same inputs write the same file and
a rebuild's diff shows only what moved. Freerouting gives the same routes
for the same board, so routing repeats too. The tracks that matter most
are not left to it: `build_board.py` draws the crystal's, the DC/DC's,
the supply capacitor's, the IR pulse's ground return and the programming
pads' first millimetre, and locks them. After routing,
`finish_board.py` stitches the two ground pours with vias on a 3 mm grid
and gives every leftover piece of pour its own via. The router takes the
pours for solid planes and can fence a few pieces in with tracks on both
layers, so it also checks that every piece reaches the rest and adds up
to three vias where one does not. Before routing, `build_board.py` gives every SMD ground pad its
own via on a short track, locked, so the router cannot box a ground pad
in and each pad has a short path to the bottom pour; Raytac's layout
drawing does the same beside the module's pads. A 0.4 mm rule area inside the
outline keeps tracks off the edge, since the router does not read
KiCad's edge clearance. Small passives and the status LED meet the pours through thermal
spokes, so both ends heat alike in reflow; C1 stays solid, since it
carries the IR pulses. The auxiliary origin is the
shell's top left corner, so the placement export for the enclosure is in
shell coordinates. DRC with schematic parity runs in CI and before each
push.

3D bodies are committed in `hardware/pcb/lib/models/`, so renders need
no download and look the same everywhere. KiCad's own models for the
passives, transistors, crystal and IR LED are copied there under their
CC-BY-SA licence (`scripts/fetch-kicad-models.sh`). LCSC's models for
the module, the switch and U2 state no license, and the TSMP96000's puts
its geometry hundreds of millimetres off the part, so
`hardware/pcb/lib/models/make_models.py` draws those three from their
datasheet dimensions instead.

Hand-placing in the KiCad editor was considered; it leaves no
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

- U1 and U2 symbols and footprints come from LCSC through
  `easyeda2kicad`, checked against the datasheets: U1's 43 pads match
  Raytac's top view (the import had the corner ground pads 42 and 43
  swapped, now fixed, and the side pads 0.05 mm too far out, moved to
  0.55 mm from the edge as on page 8); U2's four 0.9 by 2.2 mm pads at 1.27 mm pitch and
  pinout match Vishay's drawing. Pin types were set by function so ERC
  means something; U1's RESET is passive, since only the debugger drives
  it against the internal pull-up.
- `Battery_Wire_Pads_P11.5mm` is drawn here: two plated 1.0 mm holes on
  11.5 mm centers, the spacing of the 5213/5214 bridge's two contacts
  (.453 in on Keystone's catalog page 17), so each wire is under its cell.
- Everything else uses KiCad's own symbols and footprints, including
  `SW_Push_1P1T_XKB_TS-1187A` and the horizontal 5 mm LED with IR body.

Why KiCad: its files are text and review as diffs, and `kicad-cli` runs ERC, DRC
and the fab outputs in CI. Symbols and footprints for LCSC parts come in
through `easyeda2kicad` into `hardware/pcb/lib/`, and each is checked
against its datasheet's drawing before use. EasyEDA was considered for
its one-click ordering and rejected: its projects live in its cloud and do
not diff in git.

## Risks / Trade-offs

- Right of the step the board reaches 3 mm past the antenna end, from
  2.9 mm right of the module, with the IR LED's body over it but no
  copper for the first 10 mm. The IR LED's leads are 5 mm right of the
  module. Raytac's drawing shows nothing there. Raytac reviews layouts
  for free (sales@raytac.com); the board goes to them before any order
  (task 5.2c), with that question.
- The IR receiver and its filter sit on the top layer in the last 5 mm of
  the 15 mm of ground Raytac asks for right of the module. The bottom
  layer is unbroken ground under them. Moving the receiver out would put
  it behind the shell's rounded corner. The same review gets that
  question.
- The crystal sits 2 mm from the DC/DC inductor. The inductor is
  shielded and the converter runs far above 32 kHz; the bench checks
  that the crystal starts and holds its frequency with the radio on.
- Nothing protects the key lines or the battery wires from static
  beyond the chip's own 3 kV. The keys sit under plastic caps.
- XKB's specification gives 260 gf with no tolerance, so the margin to
  the 3.0 N limit is unknown until the bench measures it.

- LCSC has no AN54LQ-15 (2026-11-26) and only 53 TSMP96000. The module
  comes through JLCPCB Global Sourcing or consignment (decision 7), which
  adds about two weeks and a markup.
- The 5 mm IR LED laid flat is the only part with margin for 5 m, and it
  sets the top end's thickness.
- Early AN54LQ lots used nRF54L15 revision 1 silicon. The order asks for
  revision 2 (build code C00).

## Open Questions

None.
