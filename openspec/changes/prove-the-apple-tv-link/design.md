## Context

Target: dev board only, no PCB revision. The question is whether a
standard Bluetooth LE HID remote drives tvOS and Antuna well enough to
build the PCB around it.

What we know:

- Apple's user guide lists wireless keyboards among the Bluetooth devices
  an Apple TV 4K pairs with, under Settings, Remotes and Devices, Bluetooth.
- On full-screen Live, Antuna changes channel on an up or down move
  command, the same event a Siri Remote swipe produces. It goes back on the
  exit command and pauses on the play/pause command. An arrow key that
  tvOS turns into a move command therefore changes channel.
- Developers on Apple's forums report that tvOS gives third-party apps no
  number keys outside a text field. That does not matter here: the remote
  has no number keys.

## Goals / Non-Goals

Goals: a logged pass or fail for each requirement in the delta spec on a
named tvOS version, and the HID code each future button sends.

Non-goals: power, key layout, enclosure, certification.

## Decisions

### 1. Link to Apple TV: Bluetooth LE HID

| Option | Drives tvOS | Changes channel in Antuna | Cost |
|--------|-------------|---------------------------|------|
| A. BLE HID keyboard + consumer control | Expected, Apple lists keyboards | Yes if arrows become move commands | Low power, one radio, no license |
| B. BLE game controller profile | Yes | Yes | tvOS takes only MFi, Xbox and PlayStation controllers; needs MFi. Rejected |
| C. IR, learned in Settings, Learn Remote | Yes, a fixed set of commands | Yes, up and down are in the set | Needs line of sight; setup per Apple TV in a menu |
| D. Wi-Fi to Antuna over the local network | No | Yes | Wi-Fi power on a battery remote, app pairing flow |

A is the plan. C is the fallback if tvOS handles a BLE keyboard's arrows
badly (no key repeat, lost first press after sleep). D is not pursued.

### 2. Bench hardware: Nordic nRF52840 DK

Options: nRF52840 DK, Seeed XIAO nRF52840, ESP32-C3 DevKit. The DK has an
on-board debugger and runs the chip family the PCB would likely use on a
pre-certified module, so firmware carries over. The XIAO is cheaper but
needs an external probe for debugging. The ESP32-C3 draws more current in
BLE, which matters later for a battery remote.

- Part: Nordic nRF52840-DK (PCA10056), datasheet
  https://www.nordicsemi.com/Products/Development-hardware/nRF52840-DK.
  Alternate: Seeed XIAO nRF52840 with a J-Link probe. Source: Mouser or
  Digi-Key.

### 3. Bench firmware: Zephyr through the nRF Connect SDK

Based on the SDK's HID-over-GATT keyboard sample. One HID report map with
two reports: a boot-compatible keyboard report and a consumer control
report. A USB serial shell takes `key <usage>` and `consumer <usage>`,
with an optional hold time, and sends a press and a release, so the whole
matrix runs from the Mac with a script. Bonding on, with keys stored in
flash so a power cycle keeps the pairing. The SDK version is pinned in
`firmware/west.yml`.

### 4. Key matrix

Keyboard page: Up, Down, Left, Right, Return, Escape, Backspace, Space,
Home. Consumer page: Play/Pause, Menu, AC Home, AC Back, Channel
Increment, Channel Decrement, Volume Up, Volume Down, Mute, Power.
Usage codes are written in `firmware/` next to the shell commands.

Each key is tried on the Home screen and in Antuna's full-screen Live,
tapped and held for two seconds. The bench log keeps every result, so a
later change can add a key that works (volume through HDMI-CEC, a Home
key) without repeating the session.

## Risks / Trade-offs

- tvOS behavior can change in a point release. The bench log names the
  tvOS version and the session is repeated on each major tvOS.
- Behavior may differ by Apple TV model. The log names the model.

## Open Questions

- Whether a key press wakes a sleeping Apple TV.
- Whether consumer Volume Up and Down reach the TV through HDMI-CEC.
