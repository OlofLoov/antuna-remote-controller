## Why

The owner wants boards that arrive assembled, with as little soldering at
home as possible, and wants the parts chosen from their datasheets before
anything is drawn. The product changes (`define-keys-and-layout`,
`define-power`) and the link change (`prove-the-apple-tv-link`) say what
the remote does. This change picks the parts that can do it from two AAA
cells, checks their datasheet values against those requirements, settles
the pin plan, and captures the schematic in KiCad.

Afterwards the owner has a schematic that passes ERC, a bill of materials
where each line cites its datasheet, and a list of what is still open
before layout.

## What Changes

- The parts for rev A, each with its datasheet values, LCSC number where
  found, and one alternate (design.md, from
  `docs/research/pcb-components/`).
- The pin plan for the nRF54L15 module.
- Power checks: supply range, reset margin under IR bursts, IR LED
  current, status light at low voltage, and a current budget.
- A height check for the 11 mm body.
- A KiCad 10 project in `hardware/pcb/` with a repo-local symbol and
  footprint library, the schematic, and ERC in CI.
- Layout, DRC and ordering, after the bench confirms the link.
- The `pcb-assembly` capability: what the owner can check on a delivered
  board.

Out of scope:

- The enclosure model. The enclosure change reads this board's placement
  export.
- Product firmware. This change only needs test firmware that prints key
  changes and sends IR.
- Certification testing.

## Capabilities

### New Capabilities

- `pcb-assembly`: what a delivered rev A board is, how it is programmed,
  its height, its keys, its Bluetooth reach and its behavior on low cells.

### Modified Capabilities

None.

## Impact

- New: `hardware/pcb/` (KiCad project and library), a KiCad ERC step in CI
  and in `scripts/fast-checks.sh`.
- Implements the board side of `define-keys-and-layout` and `define-power`.
- Layout was to wait for `prove-the-apple-tv-link` to show that the IR
  codes, Bluetooth codes and learning receiver work. The owner waived
  that on 2026-11-26; the board is built by script, so a change from the
  bench rebuilds it. No order before the bench passes.
- LCSC has no stock of the module (2026-11-26). It is ordered through
  JLCPCB Global Sourcing or consigned from Digi-Key, which adds about two
  weeks.
