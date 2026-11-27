## Why

A living-room viewer wants a remote they can use without looking: a d-pad
they feel, keys that click, volume under the thumb, and nothing to swipe.
On 2026-11-25 the owner chose the key set (the seven navigation and
playback keys plus Home, volume up and down, mute and Power), the shape (a
slim stick, then no more than 11 mm thick over the keys), the power (two
AAA cells), the colors (teal shell, navy keys) and the enclosure process
(printed at home on an FDM printer).

This change writes those choices down as requirements a person can check
with their hands, a caliper and a force gauge, and draws the front so it
can be printed on paper and held before any PCB or enclosure exists.

## What Changes

- The `buttons` capability: the twelve keys, finding them by touch, the
  click, key repeat, the recessed Power key, the pairing hold and the
  status light.
- The `form-factor` capability: size and weight, balance, thumb reach,
  colors, not looking like a Siri Remote, the battery door, drops, and printing
  at home.
- A front and side drawing at 1:1 in `boards/front.svg`.
- A grip mock-up, then a shell prototype with screws and a battery door, printed from code, to hold and adjust
  before the PCB change places the keys.

Out of scope:

- What each key does on the Apple TV. That is `apple-tv-link`, in
  `prove-the-apple-tv-link`.
- Battery life and low battery. That is `define-power`.
- The PCB, the switch part numbers and the final enclosure model. Those
  come in the PCB rev A and enclosure rev A changes, which implement these
  requirements.
- Backlit keys.

## Capabilities

### New Capabilities

- `buttons`: which keys exist and how they feel and behave under the
  thumb.
- `form-factor`: the shape, size, weight and build of the remote.

### Modified Capabilities

None.

## Impact

- New: `openspec/changes/define-keys-and-layout/boards/front.svg` and,
  for the grip mock-up, the first file in `hardware/enclosure/`.
- Depends on `prove-the-apple-tv-link` for the codes each key sends. The
  volume keys stay whatever the bench finds.
- The PCB rev A and enclosure rev A changes implement and verify these
  requirements; this change stays active until they do.
