# Antuna Remote

A Bluetooth remote for Apple TV with number keys and channel keys, built
for the Antuna app (github.com/OlofLoov/antenna). PCB in KiCad, enclosure
as code, firmware on an nRF52840.

Start with `CLAUDE.md` for how the repo works, and
`openspec/changes/` for what is being built now.

## Roadmap

1. `prove-the-apple-tv-link`: which keys Apple TV hands to Antuna, proven
   on a dev board. Everything below waits for it.
2. Key layout and feel: the buttons, their spacing and labels, drawn and
   tried as a printed mock-up.
3. Power: battery type, life at a stated use, charging if any.
4. PCB rev A: module, key matrix, power, programming header.
5. Enclosure rev A: printed shell around rev A, fit checks as tests.
6. Firmware for rev A: key scan, sleep, pairing button, battery report.
