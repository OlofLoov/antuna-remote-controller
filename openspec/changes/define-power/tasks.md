## 1. Proposal

- [ ] 1.1 Review the proposal, the delta spec, design.md and tasks.md

## 2. Bench on the dev board

- [ ] 2.1 Measure idle connected, idle disconnected and per-press charge on the DK, as part of `prove-the-apple-tv-link` item 11
- [ ] 2.2 Build design.md decision 2's option A on the breadboard, run it from a bench supply at 3.2 V, 2.4 V and 2.2 V, log the IR reach at each, and pick A or B
- [ ] 2.3 Write the life estimate from the measured numbers into design.md

## 3. Built in rev A

- [ ] 3.1 PCB rev A change draws the power path, the LED driver, the reverse polarity MOSFET and the bulk capacitor per this design
- [ ] 3.2 Firmware for rev A measures the supply, warns at the threshold and reports battery level over Bluetooth

## 4. Verify

- [ ] 4.1 Each requirement has a test or a `docs/bench/` log citing `power/<requirement-slug>`
- [ ] 4.2 `openspec validate --all --strict`, `scripts/check-spec-refs.sh` and `/opsx:verify define-power` pass
