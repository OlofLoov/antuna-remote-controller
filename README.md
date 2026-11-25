# Antuna Remote

A remote for Apple TV with buttons that click, over infrared and
Bluetooth, built for the Antuna IPTV app. Up and down change channel while live TV plays. PCB in KiCad, enclosure
as code, firmware on an nRF52840.

Start with `CLAUDE.md` for how the repo works, and
`openspec/changes/` for what is being built now.

## Roadmap

1. `prove-the-apple-tv-link`: a dev board sends Apple's IR codes and
   pairs over Bluetooth, drives the Home screen and changes channel in
   Antuna. Everything below waits for it.
2. Key layout and feel: the buttons, their spacing and labels, drawn and
   tried as a printed mock-up.
3. Power: battery type, life at a stated use, charging if any.
4. PCB rev A: module, IR LED, key matrix, power, programming header,
   assembled by a PCB assembly service so only the battery holder and
   buttons might need soldering at home.
5. Enclosure rev A: printed shell around rev A, fit checks as tests.
6. Firmware for rev A: key scan, sleep, pairing button, battery report.
