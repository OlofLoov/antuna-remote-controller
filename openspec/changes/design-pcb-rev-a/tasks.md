## 1. Proposal

- [ ] 1.1 Review the proposal, the delta spec, design.md and tasks.md

## 2. Confirm from datasheets

- [x] 2.1 Read Raytac's AN54LQ reference schematic and set L1 and the crystal with its load capacitors in design.md
- [x] 2.2 Check every pin in the pin plan against the module's pad drawing
- [x] 2.3 Confirm the TSMP96000's height and footprint, the TS-1187A's stem size, and C1's capacitance at 3 V from their datasheets (C1's value at 3 V left to the low-cells bench check)
- [ ] 2.4 Check live LCSC stock for every part by hand and record the date in design.md

## 3. KiCad project

- [x] 3.1 Install KiCad 10, create `hardware/pcb/antuna-remote/` and `hardware/pcb/lib/`, and add the setup line to `scripts/setup.sh`
- [x] 3.2 Import each part's symbol and footprint and check it against its datasheet drawing
- [x] 3.3 Add `kicad-cli` ERC to CI and `scripts/fast-checks.sh`, and its command to CLAUDE.md

## 4. Schematic

- [x] 4.1 Capture the schematic from design.md decisions 1 to 3, with each part's LCSC number and alternate in its fields
- [x] 4.2 ERC clean, and a review of every net against design.md
- [ ] 4.3 Check KiCad's TS-1187A footprint against XKB's drawing (`xkb-ts-1187a-drawing.pdf` in `docs/datasheets/manifest.tsv`) and pin its hash
- [ ] 4.4 Owner review of the schematic in KiCad

## 5. Layout

- [ ] 5.1 Wait for `prove-the-apple-tv-link` to pass its IR, Bluetooth and learning tests
- [ ] 5.2 Place parts to the board in `define-keys-and-layout`, keep the module's keep-out, route, DRC clean
- [ ] 5.3 Export the placement file and a STEP model for the enclosure change

## 6. Order

- [ ] 6.1 Generate Gerbers, drill, BOM and placement with `kicad-cli`, quote at JLCPCB, and tag `pcb-rev-a`
- [ ] 6.2 Order five boards with two or more assembled, and the battery contacts from Digi-Key

## 7. Bring-up

- [ ] 7.1 Program over the Tag-Connect cable, check each key alone and in pairs, and log it in `docs/bench/`
- [ ] 7.2 Measure idle current, IR reach and the low-cell burst on a scope, and log them

## 8. Verify

- [ ] 8.1 Each requirement has a test or a `docs/bench/` log citing `pcb-assembly/<requirement-slug>`
- [ ] 8.2 `openspec validate --all --strict`, `scripts/check-spec-refs.sh` and `/opsx:verify design-pcb-rev-a` pass
