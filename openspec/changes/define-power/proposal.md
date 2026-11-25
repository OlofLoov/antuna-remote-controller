## Why

A household setter-upper wants to put batteries in and forget about the
remote for years, and to get a warning before it stops. The owner chose
two AAA cells on 2026-11-25: they handle the IR LED's pulses, last years,
and are what comparable remotes use (docs/research/apple-tv-connectivity.md).

This change sets what the user can expect from the batteries and how the
board gets power from them, before PCB rev A draws the power section.

## What Changes

- The `power` capability: two AAA cells, two-year life at a stated use,
  a low battery warning, IR reach as the cells drain, keeping the pairing
  across a battery change, and no harm from backwards cells.
- design.md settles the power path: no regulator for the MCU, a
  constant-current IR LED driver, reverse polarity protection and battery
  measurement.
- A first current measurement on the dev board, run as part of the bench
  in `prove-the-apple-tv-link`.

Out of scope:

- Rechargeable lithium cells and USB charging.
- The battery contacts' part numbers and the battery door. Those come in
  the PCB and enclosure rev A changes.

## Capabilities

### New Capabilities

- `power`: what runs the remote, how long it lasts, and how it warns.

### Modified Capabilities

None.

## Impact

- Depends on `prove-the-apple-tv-link` for the measured currents and for
  whether Bluetooth stays connected while idle.
- Depends on `define-keys-and-layout` for the status light.
- PCB rev A implements the power section; this change stays active until
  a rev A board is measured.
