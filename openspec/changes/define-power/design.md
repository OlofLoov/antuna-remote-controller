## Context

Target: PCB rev A. Two AAA cells in series give about 3.2 V fresh,
2.4 V for NiMH, and about 2.0 V when alkaline cells are near the end. An
nRF52 runs from 1.7 V to 3.6 V. The IR LED needs about 100 mA pulses and
drops about 1.3 V to 1.5 V at that current, so at the end of the cells there is
less than 1 V left for anything that sets its current.

## Decisions

### 1. The MCU runs straight from the cells

No regulator. The nRF52 runs across the whole cell range and its internal
DC/DC converter keeps the radio efficient. A buck or LDO was considered:
it adds quiescent current and parts and buys nothing in this range.

### 2. IR LED: a switched resistor first, a burst boost if reach falls short

| Option | LED current, fresh (3.2 V) to warning (2.2 V) | Parts | Idle current |
|--------|-----------------------------------------------|-------|--------------|
| A. LED and series resistor, switched by an N-channel MOSFET from the cells | About 170 mA falling to about 65 mA at 2.0 V (10 Ohm) | 2 | None |
| B. Small boost converter for an LED rail, enabled only during a burst, with a resistor or sink after it | Constant | Inductor, IC, 2 to 3 passives | None when disabled |
| C. Two-transistor current limiter (sense resistor and a second transistor) from the cells | Constant while the cells stay above about 2.3 V, then falls | 3 to 4 | None |

A single transistor with an emitter resistor, driven from a GPIO, is not
on the list: the GPIO's high level falls with the cells, so its current
falls too.

Start with A, the simplest. IR reach scales with roughly the square root of
LED intensity, and the PCB change's datasheet check puts a TSAL6200 at about 12 m typical
from fresh cells and still over 5 m at the warning level. If the
bench shows reach at 2.2 V below 5 m, use B. C is not chosen: its sense
drop (about 0.6 V) uses the headroom that matters at the end of the cells.

A bulk capacitor (about 100 µF) next to the LED smooths the 38 kHz carrier
ripple. The cells' internal resistance sets the sag over a whole burst;
the PCB change checks it stays above the nRF54L15's 1.75 V reset level
near the end of the cells.

### 3. Reverse polarity: P-channel MOSFET in the supply

A series Schottky diode was considered: simplest, but it drops about
0.3 V, which near 2.2 V costs the IR LED a third of its current. A P-channel
MOSFET with its gate to ground conducts with a few millivolts of drop and
blocks backwards cells.

### 4. Battery measurement: the MCU measures its own supply

The nRF52's ADC reads its supply internally, so no divider and no idle
divider current. Warning level: 2.2 V under load for alkaline. For NiMH,
which sits near 2.4 V for most of its life and then falls fast, the same
threshold gives a late warning, which is accepted.

### 5. Idle behavior

Bluetooth stays connected with a long connection interval and peripheral
latency, so a press acts at once. The bench in `prove-the-apple-tv-link`
measures this against disconnecting when idle; if staying connected costs
more than the two-year life allows, the remote disconnects after an idle
period and the first press goes over IR (that change's decision 4).

### 6. Pairing and settings in flash

Bond keys and settings live in the MCU's flash, so a battery change loses
nothing. No coin cell or supercapacitor backup.

## Risks / Trade-offs

- The 24-month figure rests on a secondary-source current estimate until
  the bench measures it.
- IR reach also depends on the LED, the window and the angle, which the
  enclosure change sets.

## Open Questions

- Whether the Apple TV shows a Bluetooth remote's battery level anywhere.
