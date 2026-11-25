## Why

A living-room viewer wants buttons that click: up and down to hop channels
while live TV plays, select, back and play/pause, without the Siri Remote's
touch surface. Antuna already changes channel when the user swipes up or
down on full-screen Live (antenna:tv-zap-bar-and-number-entry/swipe-up-and-down-to-change-channel),
and that swipe arrives in the app as a plain up or down move. A remote whose
arrows produce the same move gets channel changes with no app change.

Apple's user guide lists wireless keyboards among the Bluetooth devices an
Apple TV 4K pairs with. What nobody has shown us yet is a Bluetooth LE
remote built as a keyboard doing all of this on a current Apple TV: the
Home screen, Antuna's Live, play/pause, back, held keys, and coming back
after sleep. This change shows it on a dev board before any schematic
exists.

Afterwards the owner knows the remote can be a standard Bluetooth LE HID
device, with no MFi and no app change, and which HID codes each button
sends.

## What Changes

- A dev board runs firmware that pairs with Apple TV as a Bluetooth LE HID
  keyboard with consumer control, and sends any key on command from a USB
  serial shell, so every key is tried without building a keypad.
- A bench session tries the candidate keys on the Home screen and in
  Antuna, and logs the result.
- The `apple-tv-link` capability records what the remote's link must do.

Out of scope:

- Number keys. The remote has none.
- MFi and the game controller profile.
- The schematic, the PCB, the enclosure and the key layout.
- Battery, charging and power budget.
- Any change to Antuna. If the bench shows the app needs one, it is
  proposed in the antenna repo.
- IR learning of the TV's volume and power.

## Capabilities

### New Capabilities

- `apple-tv-link`: pairing with Apple TV, which keys it carries, and how it
  comes back after sleep.

### Modified Capabilities

None.

## Impact

- New folder: `firmware/` (the bench firmware).
- Needs an nRF52840 dev board, an Apple TV 4K on tvOS 26 or later, and
  Antuna installed on it with the swipe setting on changing channel.
- Depends on the antenna repo's
  antenna:tv-zap-bar-and-number-entry/swipe-up-and-down-to-change-channel.
- Blocks every PCB change: the link decided here sets the radio, the MCU
  family and the key codes.
