## 1. Proposal

- [ ] 1.1 Review the proposal, the delta specs, design.md, tasks.md and `boards/front.svg`
- [ ] 1.2 Print `boards/front.svg` at 100% on paper, cut it out, hold it, and adjust the board

## 2. Grip mock-up and shell prototype

- [x] 2.1 Add `hardware/enclosure/` with a pinned build123d environment and the build command in CLAUDE.md
- [x] 2.2 Write `mockup.py`: the wedge from design.md decision 2 with key bumps at the board's positions, exporting STEP and STL
- [x] 2.3 Print the first mock-up and try it (the owner, 2026-11-28: uncomfortable, and nothing to open; `docs/bench/2026-11-28-grip-mockup-1.md`)
- [x] 2.4 Update design.md with what the mock-up showed: decisions 2, 10 and 11
- [x] 2.5 Rebuild `mockup.py` as a hollow shell in three parts with screws and a battery door, and check the board against it in the build (`fit.py`)
- [ ] 2.6 Print the three parts (PLA or PETG, 0.2 mm layers, no supports), fit six M2 by 5 mm self-tapping screws and two AAA cells, try it with three hand sizes, and log it in `docs/bench/` citing `form-factor/balanced-in-the-hand`, `form-factor/thumb-reaches-the-viewing-keys` and `form-factor/battery-door-without-tools`
- [ ] 2.7 Update the board and design.md with what the prototype showed

## 3. Built in rev A

- [ ] 3.1 PCB rev A change places the keys, the switches, the status light and the battery contacts per this design
- [ ] 3.2 Enclosure rev A change builds the shell, caps, light pipe and battery door per this design

## 4. Verify

- [ ] 4.1 Each requirement has a test or a `docs/bench/` log citing `buttons/<requirement-slug>` or `form-factor/<requirement-slug>`
- [ ] 4.2 `openspec validate --all --strict`, `scripts/check-spec-refs.sh` and `/opsx:verify define-keys-and-layout` pass
