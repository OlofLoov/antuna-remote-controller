## Context

Target: dev board only, no PCB revision. The question is which links a
simple remote uses to drive tvOS and Antuna, and what each button sends.

What we know, from the research of 2026-11-25:

- Apple's spec pages list an IR receiver on every Apple TV 4K, including
  the 2022 Wi-Fi model (support.apple.com/en-us/111839).
- Apple TV decodes Apple's NEC variant: 38 kHz carrier, NEC timing,
  address bytes 0xEE 0x87, then a command byte and a remote ID byte. The
  command's lowest bit is a parity bit over the command and the ID. A
  Flipper capture of the Siri Remote on an Apple TV 4K (2021), remote ID
  0x8C, gives Up 0x0A, Down 0x0C, Left 0x09, Right 0x06, Select 0x5C,
  Back 0x03, Play/Pause 0x5F (Flipper-IRDB,
  Streaming_Devices/Apple/Apple_TV_4K_Gen2.ir). Owners report old IR
  Apple Remotes working on 2021 and 2022 models with no setup (MacRumors,
  January 2023). Nothing newer is first-hand.
- Unfolded Circle tested a non-MFi composite BLE HID remote on an Apple TV
  4K with tvOS 17.4: consumer Menu Up, Down, Left, Right (0x42 to 0x45)
  navigate, Menu Pick (0x41) selects, Menu Escape (0x46) goes back, Play/Pause
  (0xCD) works, AC Back (0x224) does nothing, AC Home (0x223) acts as back.
  Keyboard arrows also navigate but were dropped from their profile because
  they "work better in YouTube & search" as consumer codes
  (github.com/unfoldedcircle/core-api, doc/bt/devices/AppleTV.md). Any
  consumer key wakes the Apple TV; reconnect from remote wake took about two
  seconds.
- Apple's WWDC 2016 session 210 says presses come from the Siri Remote,
  programmable IR remotes and Bluetooth keyboards alike. SwiftUI's
  onMoveCommand responds to arrow keys. No source tests a third-party app's
  handlers with either link, so Antuna's own behavior is the test.
- HDMI-CEC needs an always-on box on the HDMI cable. Companion and MRP are
  private, encrypted protocols with no microcontroller client that break
  across tvOS releases. HomeKit, Matter and Thread cannot navigate. None of
  them fits a handheld remote.

## Goals / Non-Goals

Goals: a logged pass or fail for each requirement over each link on a named
tvOS version; the code each button sends on each link; a rule for which
link carries a press.

Non-goals: key layout, enclosure, certification, a full power budget.

## Decisions

### 1. Links: infrared and Bluetooth LE HID, both on the bench

| Option | Setup | Line of sight | Parts | Certification if sold | Verdict |
|--------|-------|---------------|-------|-----------------------|---------|
| IR, Apple codes | None | Yes | MCU, IR LED, transistor | EMC self-declaration, no radio rules | Bench |
| IR, Learn Remote | One pass in Settings | Yes | Same | Same | Fallback for IR |
| BLE HID | Pair once in Settings | No | Pre-certified module | Radio declaration, Bluetooth SIG listing | Bench |
| HDMI-CEC | Enable CEC | No | Always-on HDMI box plus a second link | Depends on the box | Rejected |
| Companion or MRP | PIN pairing | No | Wi-Fi MCU and a private crypto stack | Radio declaration | Rejected |
| HomeKit, Matter, Thread | Home app | No | Thread module | Radio declaration | Rejected, no navigation |
| BLE game controller | Pair | No | Module plus MFi | MFi | Rejected |

The PCB carries IR only, BLE only, or both, depending on the bench result.
If both, decision 4 applies.

### 2. Bench hardware: Nordic nRF52840 DK with an IR transmitter and receiver

The DK runs the chip family a pre-certified module on the PCB would use,
has an on-board debugger, and its PWM peripheral makes the 38 kHz carrier
in hardware. The IR parts sit on a breadboard on the DK's header.

- Board: Nordic nRF52840-DK (PCA10056),
  https://www.nordicsemi.com/Products/Development-hardware/nRF52840-DK.
  Alternate: Seeed XIAO nRF52840 with a J-Link probe. Source: Mouser or
  Digi-Key.
- IR LED: Vishay TSAL6200, 940 nm,
  https://www.vishay.com/docs/81010/tsal6200.pdf. Alternate: ams OSRAM
  SFH 4546. Source: Mouser.
- LED driver: onsemi 2N3904 NPN with a base resistor and a series
  resistor sized for about 100 mA pulses from the DK's 5 V rail,
  https://www.onsemi.com/pdf/datasheet/2n3903-d.pdf. Alternate: BC337.
  Source: Mouser.
- IR receiver: Vishay TSOP38238, 38 kHz,
  https://www.vishay.com/docs/82491/tsop382.pdf. Alternate: Vishay
  TSOP4838. Source: Mouser. Used to capture the Siri Remote's frames and
  to check our own.

### 3. Bench firmware: Zephyr through the nRF Connect SDK

- BLE: one HID report map with a boot keyboard report and a consumer
  control report with a 16-bit usage field, so usages above 0xFF are not
  cropped. LE Secure Connections with Just Works bonding, bond keys in
  flash, a short ASCII device name.
- IR: Apple NEC frames from the PWM peripheral, address 0xEE 0x87, remote
  ID set from the shell (default 0x8C, the Siri Remote's), parity bit
  computed, NEC repeat frames every 108 ms while a key is held.
- IR capture: the receiver's output on a GPIO, timed and decoded into
  address, command and remote ID, printed on the shell.
- Shell: `ir <command> [hold-ms]`, `ir-id <id>`, `hid key <usage> [hold-ms]`,
  `hid consumer <usage> [hold-ms]`, `capture`, plus a script that runs the
  test list from the Mac.
- The SDK version is pinned in `firmware/west.yml`.

Starting codes per button:

| Button | IR command (ID 0x8C) | BLE consumer | BLE keyboard alternative |
|--------|----------------------|--------------|--------------------------|
| Up | 0x0A | Menu Up 0x42 | Up Arrow |
| Down | 0x0C | Menu Down 0x43 | Down Arrow |
| Left | 0x09 | Menu Left 0x44 | Left Arrow |
| Right | 0x06 | Menu Right 0x45 | Right Arrow |
| Select | 0x5C | Menu Pick 0x41 | Return |
| Back | 0x03 | Menu Escape 0x46 | Escape |
| Play/Pause | 0x5F | Play/Pause 0xCD | none |
| Home | 0x40 on address 0xE5 0x87 | Menu 0x40 | none |
| Power | 0x2A on address 0xE5 0x87 (off) | System Sleep 0x82, then Sleep 0x32, then Power 0x30 | none |
| Volume up | none known | Volume Increment 0xE9 | Volume Up |
| Volume down | none known | Volume Decrement 0xEA | Volume Down |
| Mute | none known | Mute 0xE2 | Mute |

The Siri Remote sends no IR code of its own for volume. It drives the TV
either over HDMI-CEC through the Apple TV or with the TV's own IR codes,
which the Apple TV sets up. Volume over Bluetooth relies on the Apple TV
passing consumer volume codes on the same way; nothing confirms it yet.
Options if it does not:

- A. An IR receiver on the remote's PCB, so the remote learns the TV's
  volume and mute codes once, like a universal remote. One more part and a
  learning mode in firmware.
- B. Leave volume to the TV's own remote. Drops three keys.

The bench decides between Bluetooth volume, A and B.

### 4. A press acts once

If the remote carries both links, a press must not reach the Apple TV
twice. Options:

- A. Bluetooth when connected, IR otherwise. The first press after the
  remote slept goes over IR while Bluetooth reconnects. Fast first press,
  works out of line of sight once connected. Risk: a press sent over IR is
  also queued and sent over Bluetooth when the link comes up.
- B. IR always, Bluetooth only for buttons IR cannot send. Simple, but
  loses the reason for having Bluetooth.
- C. A switch on the remote. Moves the choice to the user.

A is the starting rule. The firmware never queues a press for Bluetooth
that it already sent over IR. The bench checks it with the "a press acts
once" scenarios, and the rule is final only after that.

### 5. Test list

Run on the Home screen and in Antuna (full-screen Live, the guide, search,
a movie), tapped and held, over each link:

1. Capture the Siri Remote's IR frames for the seven buttons and compare
   them with decision 3's table.
2. The seven IR codes with ID 0x8C, then with another ID, on an Apple TV
   that never learned a remote.
3. Learn Remote with plain NEC codes from the same board.
4. Held up and down in Live over IR (repeat frames) and over Bluetooth:
   does Antuna zap once per step, and how fast.
5. IR wake from sleep, and whether Menu first is needed.
6. IR range and angle with the Apple TV where it normally sits.
7. Bluetooth pairing, the seven consumer codes, then the keyboard
   alternatives, with search focused.
8. Bluetooth first-press delay after the remote's idle disconnect, and
   after the Apple TV slept.
9. Bond survives a power cycle.
10. Both links on at once with decision 4's rule.
11. DK current in idle connected and idle disconnected states, as a first
    number for the power change.
12. Home, Power and the volume and mute keys over each link, with the
    Apple TV's volume control set to HDMI-CEC and then to IR.

## Risks / Trade-offs

- tvOS behavior can change in a point release. The bench log names the
  tvOS version and the session is repeated on each major tvOS.
- An Apple TV that learned another IR remote may ignore ours. The Learn
  Remote fallback covers it.
- Behavior may differ by Apple TV model. The log names the model.

## Open Questions

- Whether IR repeat frames give Antuna a smooth held zap or one step.
- Whether consumer Volume Up and Down reach the TV through HDMI-CEC.
