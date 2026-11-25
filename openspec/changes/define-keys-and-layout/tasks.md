## 1. Proposal

- [ ] 1.1 Review the proposal, the delta specs, design.md, tasks.md and `boards/front.svg`
- [ ] 1.2 Print `boards/front.svg` at 100% on paper, cut it out, hold it, and adjust the board

## 2. Grip mock-up

- [ ] 2.1 Add `hardware/enclosure/` with a pinned build123d environment and the build command in CLAUDE.md
- [ ] 2.2 Write `mockup.py`: the wedge from design.md decision 2 with key bumps at the board's positions, exporting STL
- [ ] 2.3 Print it, try it with three hand sizes, and log it in `docs/bench/` citing `form-factor/balanced-in-the-hand` and `form-factor/thumb-reaches-the-viewing-keys`
- [ ] 2.4 Update the board and design.md with what the mock-up showed

## 3. Built in rev A

- [ ] 3.1 PCB rev A change places the keys, the switches, the status light and the battery contacts per this design
- [ ] 3.2 Enclosure rev A change builds the shell, caps, light pipe and battery door per this design

## 4. Verify

- [ ] 4.1 Each requirement has a test or a `docs/bench/` log citing `buttons/<requirement-slug>` or `form-factor/<requirement-slug>`
- [ ] 4.2 `openspec validate --all --strict`, `scripts/check-spec-refs.sh` and `/opsx:verify define-keys-and-layout` pass
