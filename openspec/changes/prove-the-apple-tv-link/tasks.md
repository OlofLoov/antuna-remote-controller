## 1. Proposal

- [ ] 1.1 Review the proposal, the delta spec, design.md and tasks.md

## 2. Bench firmware

- [ ] 2.1 Pin the nRF Connect SDK in `firmware/west.yml` and add the build and flash commands to CLAUDE.md
- [ ] 2.2 HID-over-GATT keyboard and consumer control reports with bonding stored in flash
- [ ] 2.3 USB serial shell with `key <usage>` and `consumer <usage>` and a hold time, plus a script that runs the key matrix from design.md decision 4

## 3. Bench session

- [ ] 3.1 Pair, run the key matrix on the Home screen and in Antuna's full-screen Live, and log it in `docs/bench/`
- [ ] 3.2 Sleep, power-cycle and out-of-range checks for `apple-tv-link/comes-back-after-sleep`
- [ ] 3.3 If the arrows fail or lose the first press after sleep, try option C from design.md decision 1 and log it

## 4. Decision

- [ ] 4.1 Write the chosen link and each button's HID code into design.md with the bench result behind it, and move any requirement the bench disproved out of the delta spec
- [ ] 4.2 If Antuna needs a change for a key the bench found useful, propose it in the antenna repo and link it here

## 5. Verify

- [ ] 5.1 Each requirement has a bench log entry citing `apple-tv-link/<requirement-slug>`
- [ ] 5.2 `openspec validate --all --strict`, `scripts/check-spec-refs.sh` and `/opsx:verify prove-the-apple-tv-link` pass
