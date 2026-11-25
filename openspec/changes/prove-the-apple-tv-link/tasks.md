## 1. Proposal

- [ ] 1.1 Review the proposal, the delta spec, design.md and tasks.md
- [ ] 1.2 Order the parts in design.md decision 2

## 2. Bench firmware

- [ ] 2.1 Pin the nRF Connect SDK in `firmware/west.yml` and add the build and flash commands to CLAUDE.md
- [ ] 2.2 IR transmit: Apple NEC frames with parity, a settable remote ID and repeat frames, from the PWM peripheral
- [ ] 2.3 IR capture: decode frames from the receiver into address, command and remote ID
- [ ] 2.4 BLE HID: keyboard and 16-bit consumer control reports, bonding stored in flash
- [ ] 2.5 USB serial shell from design.md decision 3, and a script that runs the test list in decision 5
- [ ] 2.6 The rule from decision 4 for when both links are on

## 3. Bench session

- [ ] 3.1 Capture the Siri Remote's frames and correct the IR table in design.md if they differ
- [ ] 3.2 Run the IR tests (decision 5, items 2 to 6) and log them in `docs/bench/`
- [ ] 3.3 Run the Bluetooth tests (items 7 to 9) and log them
- [ ] 3.4 Run both links together (item 10) and measure current (item 11)
- [ ] 3.5 Run Home, Power, volume and mute (item 12), and record whether Bluetooth volume works without learned codes

## 4. Decision

- [ ] 4.1 Write into design.md which links the remote carries, each button's code per link and the rule for a press, with the bench result behind it; move any requirement the bench disproved out of the delta spec
- [ ] 4.2 If Antuna needs a change for something the bench found, propose it in the antenna repo and link it here

## 5. Verify

- [ ] 5.1 Each requirement has a bench log entry citing `apple-tv-link/<requirement-slug>`
- [ ] 5.2 `openspec validate --all --strict`, `scripts/check-spec-refs.sh` and `/opsx:verify prove-the-apple-tv-link` pass
