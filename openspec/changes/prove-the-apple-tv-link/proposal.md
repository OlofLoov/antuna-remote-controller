## Why

A living-room viewer wants buttons that click: up and down to hop channels
while live TV plays, select, back and play/pause, without the Siri Remote's
touch surface. Antuna already changes channel when the user swipes up or
down on full-screen Live (antenna:tv-zap-bar-and-number-entry/swipe-up-and-down-to-change-channel),
and that swipe arrives in the app as a plain up or down move. A remote whose
buttons produce the same move gets channel changes with no app change.

Research on 2026-11-25 (`docs/research/apple-tv-connectivity.md`,
summarized in design.md) found two links that can do this without MFi:

- Infrared with Apple's own remote codes. Every Apple TV 4K has an IR
  receiver and accepts these codes with no setup. The parts are a small
  MCU and an IR LED, and no radio certification applies. It needs line of
  sight.
- Bluetooth LE HID. A non-MFi remote's per-button test on tvOS 17.4 shows
  which codes work, and a user reported it still working on tvOS 27 in
  October 2026. It needs a one-time pairing and takes about two seconds to
  reconnect after the remote sleeps.

The owner is happy for the remote to carry both. No source confirms that
either link reaches a third-party app's up, down, back and play/pause
handlers, so this change shows both on a dev board, in the tvOS UI and in
Antuna, before any schematic exists.

Afterwards the owner knows which links the remote carries, the exact code
each button sends on each link, and how the two links share a press.

## What Changes

- A dev board runs firmware that sends Apple's infrared remote codes
  through an IR LED, and pairs as a Bluetooth LE HID device with keyboard
  and consumer control reports.
- A USB serial shell sends any IR code or HID usage on command, so every
  key is tried without building a keypad.
- An IR receiver on the same board captures the Siri Remote's own frames,
  so the codes the firmware sends are checked against the real remote.
- A bench session runs the test list in design.md and logs it in
  `docs/bench/`.
- The `apple-tv-link` capability records what the remote's links must do.

Out of scope:

- Number keys. The remote has none.
- MFi and the game controller profile.
- HDMI-CEC, network control (Companion, MRP), HomeKit, Matter and Thread.
  The research rules them out for a handheld remote.
- The schematic, the PCB, the enclosure and the key layout.
- Battery, charging and power budget beyond the measurements in the bench
  session.
- Any change to Antuna. If the bench shows the app needs one, it is
  proposed in the antenna repo.
- Learning the TV's own IR codes. If the bench shows volume needs it,
  a later change adds it.

## Capabilities

### New Capabilities

- `apple-tv-link`: pairing and setup, which keys each link carries
  (navigation, select, back, play/pause, Home, Power, volume and mute),
  how a press acts once across two links, and how the remote comes back
  after sleep.

### Modified Capabilities

None.

## Impact

- New folder: `firmware/` (the bench firmware). The research report is in
  `docs/research/`.
- Needs an nRF52840 DK, a 940 nm IR LED with a transistor driver, a 38 kHz
  IR receiver module, an Apple TV 4K on tvOS 26 or later with its Siri
  Remote, and Antuna installed with the swipe setting on changing channel.
- Depends on the antenna repo's
  antenna:tv-zap-bar-and-number-entry/swipe-up-and-down-to-change-channel.
- Changes the repo's hard constraint on links: IR and Bluetooth LE HID are
  both allowed, decided here.
- Blocks every PCB change: the links decided here set the radio, the MCU,
  the IR driver and the key codes.
