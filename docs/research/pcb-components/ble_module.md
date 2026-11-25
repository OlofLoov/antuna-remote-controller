# BLE module choice for the 2xAAA TV remote

Researched 2026-11-25. Status labels used below:
- **[DS]**: read in the vendor datasheet (revision given).
- **[Nordic]**: read in Nordic docs or on the Nordic product page.
- **[listing]**: from a distributor or JLCPCB page.
- **[snippet]**: only seen in a search-result snippet. The crawl date is unknown, so re-check it.
- **[UNVERIFIED]**: from memory or inferred. Check before relying on it.

## TL;DR

- **Recommended: Raytac AN54LQ-15** (nRF54L15, chip antenna). LCSC/JLCPCB part **C49419243** (JLCPCB "Extended" part, "Standard" PCBA only).
  - 13.7 x 9.5 x 1.8 mm. Supply 1.7–3.6 V.
  - 31 GPIOs, 20 of them able to wake the chip from System OFF.
  - Certifications: FCC (SH6AN54LQ), IC (8017A-AN54LQ), plus EU **and UKCA** Declarations of Conformity.
  - Same footprint as the AN54LQ-10 and AN54LQ-05, so the SoC can be swapped later without a re-layout.
- **Alternate: Raytac MDBT42Q-512KV2** (nRF52832, chip antenna). LCSC/JLCPCB part **C2828282** (Extended part, Economic and Standard PCBA).
  - 16 x 10 x 2.2 mm. Supply 1.7–3.6 V. 32 GPIOs, and any pin can wake the chip.
  - Certifications: FCC (SH6MDBT42Q), IC (8017A-MDBT42Q), CE test report. **No UKCA declaration is listed.**
  - Mature, but older silicon.
- **Dev kit: order the nRF54L15 DK, not the nRF52840 DK.** Optionally add the Raytac AN54LQ-DB-15 module board (about $17) to test the real module and antenna.
- **Stock: not verified live.** LCSC and JLCPCB pages load stock and price in the browser after the page loads, and my direct API query was blocked in this session. Check stock by hand before committing, or pre-order the part through JLCPCB.

## 1. What the design needs from the module

- **Supply:** 2xAAA with no regulator. That is 3.2 V fresh, about 2.0 V at end of life, 2.4 V on NiMH. The module's minimum supply must be 2.0 V or lower.
- **Pins:**
  - 12 keys, one GPIO each, to ground, with internal pull-up. Any key must wake the chip.
  - IR LED driven from a PWM peripheral at 38 kHz.
  - IR receiver input. It needs an interrupt, and ideally a capture timer to learn codes.
  - Status LED.
  - SWD for programming.
  - Total: 15 GPIOs plus SWD.
- **Firmware:** Zephyr via nRF Connect SDK, running HID over GATT (keyboard + consumer control) to an Apple TV.
- **Assembly and certification:** JLCPCB or PCBWay assembly. The module must be pre-certified (CE/RED and FCC, ideally IC and UKCA) and used with the vendor's reference antenna layout.

## 2. Candidate comparison

| Module (SoC) | Size L x W x H mm | VDD range | Module GPIO | Antenna | Certs in datasheet | 32 MHz XTAL | DC/DC inductor | 32.768 kHz XTAL | LCSC / JLC | Price (approx) |
|---|---|---|---|---|---|---|---|---|---|---|
| **Raytac AN54LQ-15** (nRF54L15 QFN48) | 13.7 x 9.5 x **1.8** [DS v1.3]. Nordic's module list says 2.05 | **1.7–3.6 V**; POR needs ≥ 1.75 V [DS] | 31 (P0: 5, P1: 15, P2: 11) [DS] | Chip. The -P15 has a PCB antenna, the -U15 a u.FL connector | FCC SH6AN54LQ, IC 8017A-AN54LQ, TELEC, NCC, CE/RCM, SRRC, KC, WPC, **EU + UKCA DoC (RED 2014/53/EU, EN 300 328 V2.2.2)** [DS] | on module [DS] | **external** L1 on the DCC pin [DS] | external (optional) [DS] | **C49419243**, JLCPCB Extended, Standard PCBA, X-ray [listing]. Stock not verified | about €3.5–3.7 (DigiKey marketplace), $4.9–7.3 (TME) [snippet] |
| Raytac AN54LV-15 (nRF54L15) | 6.4 x 8.4 x 1.5 [Nordic list] | 1.7–3.6 V (SoC) | 32 [Nordic list] | Chip | not checked | – | – | – | not found | – |
| **Raytac MDBT42Q-512KV2** (nRF52832 QFN48) | 16 x 10 x 2.2 [DS Ver. P] | 1.7–3.6 V [DS] | 32. P0.22–P0.30 are low-frequency/low-drive only, because they sit near the radio [DS] | Chip (P512KV2: PCB antenna) | FCC SH6MDBT42Q, IC 8017A-MDBT42Q, CE test report, TELEC, NCC, SRRC, KC [DS]. **No UKCA declaration listed** | on module [DS] | **external** L2/L3/C14 [DS] | external (optional) [DS] | **C2828282**, JLCPCB Extended, Economic + Standard PCBA [listing]. LCSC stock 0 per [snippet] | about $5–6 (LCSC reference $5.96 [snippet], DigiKey $4.95 [snippet]) |
| Raytac MDBT50Q-512K (nRF52833) | 15.5 x 10.5 x about 2.05 [UNVERIFIED; this is the MDBT50Q family size] | 1.7–5.5 V [listing] | up to 42 (SoC) | Chip | family: FCC SH6MDBT50Q, IC 8017A-MDBT50Q, CE/RCM, TELEC, NCC, SRRC, KC (from the MDBT50Q-1MV2 datasheet) | on module | REG1 inductor **on module** (MDBT50Q family) | external | **C6904155**, JLCPCB Extended, Economic + Standard PCBA, X-ray [listing] | not found |
| Raytac MDBT50Q-1MV2 (nRF52840) | 15.5 x 10.5 x 2.05 [DS Ver. K, 2022-07-01] | 1.7–5.5 V [DS] | 48 (SoC) [DS] | Chip | FCC SH6MDBT50Q, IC 8017A-MDBT50Q, TELEC, NCC, CE/RCM, SRRC, KC, WPC [DS] | on module | REG1 inductor **on module**; REG0 inductor (10 µH) external, needed only when supplying VDDH > 3.6 V [DS] | external | **C5118826** (LCSC). JLCPCB C2688382 is the U1MV2 (u.FL) variant and C5119772 the P1MV2 (PCB antenna) variant [snippet]. LCSC stock 0 per [snippet] | LCSC reference $6.65, TME $8.40, SparkFun $8.95 [snippet] |
| Ebyte E73-2G4M08S1C (nRF52840) | 18 x 13 x about 3.0 (height inferred from a 3D-model file name) | – | – | Ceramic | **No FCC grant or CE/RED certificate found** | – | – | – | C356849, JLCPCB Extended [listing] | LCSC reference $7.25 [snippet] |
| u-blox NINA-B31x (nRF52840) | about 10 x 15 x 2.2 [UNVERIFIED] | – | – | PCB/pin | – | – | – | – | LCSC C6712551 / C5827219 / C6243482 [snippet] | – |
| u-blox ANNA-B5 (nRF54L15 SiP) | 6.5 x 6.5 x 1.2 [Nordic list] | 1.7–3.6 V (SoC) | 32 | Chip or pin | not checked | – | – | – | not found | – |
| Holyiot HOLYIOT-24005-NRF54L15 | 24.04 x 15.63 x 2.3 [Nordic list] | – | 29 | PCB | not checked | – | – | – | not found | – |
| MinewSemi ME54BS01 / ME54BS11 (nRF54L15) | 23.2 x 17.4 x 2.0 / 15.8 x 12.0 x 2.0 [Nordic list] | – | 19 / 12 | PCB | not checked | – | – | – | not found | – |
| Fanstel BM15C (nRF54L15) | 10.0 x 15.8 x 2.0 [Nordic list] | – | 32 | Chip | not checked | – | – | – | not found | – |
| Silicon Labs BGM220P | 12.9 x 15 [snippet] | 1.8–3.8 V [snippet] | – | – | – | – | – | – | JLCPCB C1512691 (BGM220PC22HNA2R) [snippet] | – |

Notes on the rows above:
- **u-blox NINA-B31x:** u-blox's datasheet marks NINA-B311-00B and NINA-B311-01B as end-of-life. The u-blox page calls the series an older generation and points new designs to NINA-B41x. Do not use it.
- **Silicon Labs BGM220P:** it would mean Simplicity SDK rather than nRF Connect SDK, so it is out of scope.

Candidates ruled out:
- **Ebyte E73 / E104:** no evidence of a modular FCC grant or a RED certificate, so they fail the pre-certification requirement. Their datasheets were not fully read [UNVERIFIED].
- **nRF52805:** the WLCSP package has only 10 GPIOs, which is not enough. RAM is also too small for a Zephyr BLE HID stack.
- **nRF52810 / nRF52811 modules:** 24 KB RAM is very tight for a Zephyr/NCS BLE HID build [UNVERIFIED for current NCS]. Not worth the risk to save under $1.
- **nRF52840:** works, but nothing in this design needs its USB or 256 KB RAM. The module also costs more.

## 3. Sleep current (SoC datasheet values, 3 V, DC/DC on)

| SoC | System OFF, wake on pin, no RAM retained | System OFF, full RAM retained | System ON idle with RAM retained, wake on pin | System ON idle + RTC/GRTC timer + RAM retained |
|---|---|---|---|---|
| **nRF54L15** | 0.7 µA (IOFF0) | +0.96 / +1.9 / +2.2 µA for 96 / 192 / 256 KB (Nordic's estimate, from the Academy table) | 1.3 µA at 64 KB, 1.8 µA at 128 KB, 2.7 µA at 256 KB | 1.5 µA at 64 KB, 1.9 µA at 128 KB, 2.9 µA at 256 KB (LFXO); 3.5 µA at 256 KB (LFRC) |
| nRF52832 | 0.3 µA (IOFF_RAMOFF_GPIO) | 0.7 µA (64 KB) | 1.5 µA (full 64 KB, wake on any event) | 1.9 µA (ION_RAMOFF_RTC, no RAM retained) |
| nRF52833 | 0.6 µA | 1.3 µA (128 KB) | 1.8 µA (128 KB) | 2.6 µA (128 KB, RTC on LFRC) |
| nRF52840 | 0.40 µA | 1.86 µA (256 KB) | 2.35 µA (256 KB) | 3.16 µA (256 KB, RTC on LFRC) |

Sources:
- nRF54L15: [current consumption table](https://docs.nordicsemi.com/r/bundle/ps_nrf54l15/page/chapters/current_consumption/doc/current_consumption.html-unique_1307930676) (nRF54L15/L10/L05 Datasheet v1.0 per [DevZone](https://devzone.nordicsemi.com/f/nordic-q-a/128462/manual-nrf54l-or-nrf54l-series/567955)) and the [Nordic Academy System OFF table](https://academy.nordicsemi.com/courses/designing-low-power-bluetooth-le-products/lessons/lesson-5-soc-specific-power-optimization-i/topic/memory-retention-and-sleep-modes/).
- nRF52832: [PS pmu page](https://docs.nordicsemi.com/r/bundle/ps_nrf52832/page/pmu.html).
- nRF52833: [i_sleep table](https://docs.nordicsemi.com/r/bundle/ps_nrf52833/page/_tmp/nrf52833/autodita/current/parameters.i_sleep.html).
- nRF52840: [i_sleep table](https://docs.nordicsemi.com/r/bundle/ps_nrf52840/page/_tmp/nrf52840/autodita/current/parameters.i_sleep.html).

Radio current:
- nRF54L15: **4.8 mA TX and 3.4 mA RX at 0 dBm, 3 V** ([product page](https://www.nordicsemi.com/Products/nRF54L15)).
- nRF52832: about 5.3 mA TX and 5.4 mA RX at 0 dBm with DC/DC [UNVERIFIED, from memory of the nRF52832 PS].

**What this means for a remote:** with 2xAAA (about 1000 mAh), 1 µA of extra sleep current costs about 9 mAh per year. Average consumption is set by the connection interval and peripheral latency while connected to the Apple TV, plus how often keys are pressed, not by these sub-µA differences.
- nRF54L15 gains roughly 30 % on radio current and has a lower System ON idle with partial RAM retention.
- This helps, but either chip will run for years. The nRF54L choice is mostly about being current silicon with lower cost and better radio current, not about battery life.

**GPIO wake gotcha, both families:** use PORT/SENSE (DETECT) interrupts for the 12 keys, not GPIOTE IN channels.
- On the nRF52840, "wake on GPIOTE IN" costs 17.37 µA, against 2.36 µA for "wake on GPIOTE PORT" (same table).
- There are also not enough GPIOTE channels for 12 keys: the nRF52 has 8, and the nRF54L has 8 on GPIOTE20 and 4 on GPIOTE30.
- In Zephyr, set the GPIO node's `sense-edge-mask` so that edge interrupts on key pins use SENSE [UNVERIFIED property name for current NCS; check the `nordic,nrf-gpio` binding].

## 4. Is nRF54L15 the better choice in late 2026?

**Yes, for a new design.** The evidence:
- **Current:** as section 3 shows, radio current is clearly lower and sleep current is comparable or better.
- **Supply range:** 1.7–3.6 V ([product page](https://www.nordicsemi.com/Products/nRF54L15); key features in the [datasheet](https://docs.nordicsemi.com/r/bundle/ps_nrf54l15/page/keyfeatures_html5.html)). It does *not* start at 1.8 V or higher.
- **Power-on reset needs VDD ≥ 1.75 V** (AN54LQ datasheet v1.3, VDDPOR). That is fine for 2xAAA down to 2.0 V.
- **HID support in nRF Connect SDK:**
  - nRF Desktop, Nordic's HID reference application, has keyboard builds for `nrf54l15dk/nrf54l15/cpuapp`, `nrf54l15dk/nrf54l10/cpuapp` and `nrf54l15dk/nrf54l05/cpuapp` ([NCS latest board configuration](https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrf/applications/nrf_desktop/board_configuration.html); also in the new [HID add-on docs](https://nrfconnectdocs.nordicsemi.com/addons/addon-hid/latest/applications/nrf_desktop/board_configuration.html), v1.0.99, which reference NCS v3.4.2-rc1 / Zephyr 4.4.2).
  - The nRF54L keyboard configuration supports keyboard, consumer control and system control HID reports, which is exactly what this remote needs.
  - The nRF54L05 being a supported keyboard target shows that even the smallest part fits a HID keyboard.
- **SDK maturity:** NCS v3.4.0 LTS was released 2026-07-31 ([release notes](https://nrfconnectdocs.nordicsemi.com/ncs/latest/nrf/releases_and_maturity/releases/release-notes-3.4.0.html)). The nRF54L series has been in mass production since 2025.
- **Price:** the AN54LQ-15 module costs about the same as or less than an nRF52832 module (see the table).

**Costs and risks of the nRF54L (all can be worked around):**
1. **Port P2 cannot wake the chip and has no SENSE or GPIOTE.** Only P0 (5 pins) and P1 (15 pins) can wake it ([port capabilities](https://docs.nordicsemi.com/r/bundle/ps_nrf54l15/page/gpio.html-concept_port_capabilities); [Nordic pin-planning blog, 2025-06-13](https://devzone.nordicsemi.com/nordic/nordic-blog/b/blog/posts/essential-pin-planning-guidelines-for-the-nrf54l-series)).
   - All 12 keys and the IR receiver must be on P0 or P1.
   - With a 32.768 kHz crystal on P1.00/P1.01, **18 wake-capable pins** remain. 13 are needed for keys plus IR receive, so this fits with 5 spare.
2. **PWM20, PWM21 and PWM22 can only drive P1 pins** (same blog: "PWM peripherals are only available on P1 pins"). Put the IR LED on P1.
3. **Erratum [114]:** current rises by about 300 µA in System ON idle if a SENSE pin toggles low-high-low-high within 0.5 µs. Workaround: `GPIO.DETECTMODE = LDETECT` (latched detect), or filter key bounce and IR glitches ([nRF54L15 Rev 2 errata [114]](https://docs.nordicsemi.com/r/Gb3uRMnxMErLI7S1G0Uc~Q/_O74fg3eeng9jbw03xh0wA)). It applies to build codes QFAA-C00 and others.
4. **Silicon revision:** early modules shipped Rev 1 silicon. In one DevZone thread a Fanstel BC15M lot "B0V3" was Rev 1, although its high System OFF current turned out to be a board issue, not silicon ([thread](https://devzone.nordicsemi.com/f/nordic-q-a/129310/nrf54l15-system-off-36-a-on-rev-1-bc15m-v3-modules-vs-0-9-a-on-a-rev-2-dk-same-system_off-sample-and-ncs/571741)).
   - Ask Raytac or JLCPCB for Rev 2 silicon (FICR 0x344 = 0x02, build code -C00).
   - Nordic also says in that thread that **DC/DC is required for the lowest current; LDO-only is not a supported low-power configuration.**
5. **Erratum [37]:** System OFF current is too high if System OFF is entered right after reset. Recent NCS releases are said to include the workaround [UNVERIFIED].
6. **No nRF5 SDK.** Zephyr/NCS is the only option, which is already the plan.

**Dev kit decision:** buy the **nRF54L15 DK** (LCSC lists it as C42857865, about $46.29 with 22 in stock [snippet]).
- It can emulate the nRF54L10 and nRF54L05, and it matches the recommended module.
- The nRF52840 DK would make sense only if the alternate (nRF52832) were chosen. In that case the right board is the nRF52 DK (PCA10040), which carries the nRF52832.
- Optional extras:
  - Raytac **AN54LQ-DB-15** demo board: about $16.84 at DigiKey [snippet]. It is a Zephyr board target, `raytac/an54lq_db_15` ([Zephyr docs](https://docs.zephyrproject.org/latest/boards/raytac/an54lq_db_15/doc/index.html)). Use it to try the exact module, antenna and current draw.
  - A Power Profiler Kit II to measure µA-level current.

## 5. Running straight from 2xAAA: gotchas and parts the schematic needs

### Recommended: AN54LQ-15

Source: [Raytac AN54LQ datasheet v1.3, issued 2026-11-20](https://www.raytac.com/download/index.php?index_id=81).

**Power**
- Connect VDD_NRF (pin 11) directly to the battery. The range is 1.7–3.6 V, so a fresh 3.2 V pair is inside it.
  - No high-voltage (VDDH/REG0) mode exists on the nRF54L, so there is nothing to bypass.
  - Do not use 3xAAA: 4.5–4.8 V is above the 3.6 V maximum.
- **DC/DC inductor L1 goes on the board, from DCC (pin 9).**
  - Datasheet: "When enabling the DC/DC regulator, the device checks if an inductor (L1) is connected to the DCC pin. If L1 is not detected, the device remains in LDO mode."
  - Nordic's QFN48 reference (config 1) uses **4.7 µH, at least 120 mA, ±20 %, about 650 mΩ, 0603** ([Nordic reference circuitry, QFN48 config 1](https://docs.nordicsemi.com/r/bundle/ps_nrf54l15/page/chapters/ref_circuitry.html-concept_refcircuit_config_1); value taken via a search summary, so confirm it in the schematic).
  - Raytac's own reference circuit is an image I could not read as text. Copy L1, and any series parts, from datasheet section 8.
  - In Zephyr: `&vregmain { regulator-initial-mode = <NRF5X_REG_MODE_DCDC>; };` [UNVERIFIED exact syntax for the board file].
- **DECD (pin 8):** the 2.2 µF decoupling capacitor is already inside the module (datasheet). Leave the pin unconnected externally unless the reference schematic says otherwise.
- **VDD decoupling and bulk capacitor:** use the reference values for VDD decoupling. Also add a bulk capacitor (tens to hundreds of µF, low leakage) [UNVERIFIED sizing].
  - The IR LED pulses (typically 100 mA or more at 38 kHz) pull the AAA voltage down, worst on nearly flat cells.
  - Without the bulk capacitor, VDD could dip toward the 1.7 V brown-out level or the 1.75 V POR level.

**Clocks**
- The 32 MHz crystal and its load capacitance are already on the module (datasheet section 3).
- **The 32.768 kHz crystal is NOT on the module.** Raytac says NCS firmware expects an external one by default, so add X2/C12/C13 on XL1/XL2 = P1.00/P1.01 (pins 12 and 13).
  - Recommended: it gives 2.9 µA instead of 3.5 µA for 256 KB retained with GRTC, and tighter BLE timing.
  - If you leave it out, configure the LFRC in Kconfig/devicetree. That frees 2 pins.

**NFC pins**
- P1.02/P1.03 (pins 15 and 16) default to NFC. Configure them as GPIO in UICR (in Zephyr, `nfct-pins-as-gpios` [UNVERIFIED property name for nRF54L]), or leave them unused.

**Debug**
- SWDIO is pin 36, SWDCLK pin 37, RESET pin 39. SWD pins are dedicated and not GPIO.

**Ground and antenna**
- GND is on pins 1, 10, 14, 26, 42 and 43.
- Keep-out: no ground pad or copper under the "No Ground-Pad Area" on **every layer**. Put the module at the PCB edge (datasheet section 2.3; the drawing was updated in v1.2).
- Raytac offers a free layout review at sales@raytac.com.

**Suggested pin plan** (pin numbers read from the datasheet text; re-check them against the drawing)
- **12 keys:** P0.00–P0.04 (5 pins) plus 7 of P1.04–P1.14. Use internal pull-ups (12–16 kΩ, from the datasheet's GPIO specification) and SENSE-low wake.
  - Avoid P0.03 and P0.04 if the GRTC PWM or CLKOUT32K functions are wanted. They are not needed here.
- **IR LED:** a P1 pin, for example P1.05 or P1.06, through an NMOS/NPN driver, since high-drive GPIO is only 3–5 mA. PWM20 generates the 38 kHz carrier.
- **IR receiver:** a P1 pin with GPIOTE20 and a TIMER2x capture through DPPI, to measure edges when learning codes.
- **Status LED:** a P2 pin is fine. It needs no wake function, and its current is low.
- **Max total GPIO current: 15 mA** (datasheet), so the IR LED must be driven by a transistor.

### Alternate: MDBT42Q-512KV2

Source: [Raytac MDBT42Q approval sheet, Ver. P, 2025-07-14](https://www.raytac.com/upload/download_files/38a8a4a0aff945d8484507d60058109b.pdf).

- **Power:** supply 1.7–3.6 V, battery straight to VDD. The nRF52832 has no high-voltage mode.
- **DC/DC:** "When using DC-DC mode, please add L2 / L3 / C14" on DCC (pin 10). Nordic's nRF52832 reference uses 10 µH + 15 nH + 1 µF [UNVERIFIED; copy them from the datasheet section 8 schematic].
  - The module ships with Raytac test firmware set to LDO mode.
- **Decoupling:** DEC4 (1 µF) is on the module.
- **Clocks:** 32 MHz crystal on the module. 32.768 kHz crystal external, on XL1/XL2 (P0.00/P0.01).
- **NFC:** remove NFC1/C19/C21 when NFC is not used.
- **Pin limits:** P0.22–P0.30 are for low-frequency, low-drive use only (up to 10 kHz). Keys are fine there; **do not put the 38 kHz IR PWM on them.**
- **Wake:** the nRF52832 can wake from System OFF on any GPIO, and its PWM can be routed to any pin.

## 6. Certification notes (EU/US/UK)

- **AN54LQ (datasheet section 9):**
  - FCC modular grant: the host product is labelled "Contains FCC ID: SH6AN54LQ".
  - IC: "Contains IC ID: 8017A-AN54LQ".
  - EU and UKCA Declarations of Conformity: RED 2014/53/EU, EN 300 328 V2.2.2, EN 301 489-1/-17, and EN 55032 among others. Tests by SGS Taiwan.
  - FCC RF exposure was evaluated for portable use with no separation distance, which suits a handheld remote.
- **MDBT42Q:**
  - FCC SH6MDBT42Q; IC 8017A-MDBT42Q.
  - CE: a test report only. **No UKCA declaration is listed.**
- **What the module certificate does not cover:** the finished product still needs its own:
  - FCC Part 15B unintentional-radiator verification and SDoC;
  - EU DoC covering EMC and safety (EN 62368-1);
  - Assessment against the RED delegated act (EN 18031, applying since 2025-08-01). A BLE-only remote may fall outside the "internet-connected" scope [UNVERIFIED; check this].
- Keep the antenna keep-out and trace layout exactly as the datasheet shows. The grants assume the reference layout.

## 7. Open items / not verified

- **Live LCSC stock and price for C49419243, C2828282, C6904155 and C5118826.**
  - The pages load stock in the browser after loading, and my API query was denied.
  - Snippets showed LCSC stock 0 for C2828282, C5118826 and C356849 at an unknown date.
  - If LCSC shows 0, use JLCPCB pre-order or Global Sourcing, or consign parts bought from TME or DigiKey.
- **AN54LQ-15 height:** the datasheet says 1.8 mm; Nordic's module list says 2.05 mm. Either fits an 11 mm enclosure.
- **Reference values:** the exact L1 and VDD capacitor values in Raytac's own reference schematic for the AN54LQ (an image), and the MDBT42Q DC/DC part values.
- **Modules not checked against datasheets:** AN54LV, u-blox ANNA-B5, Ezurio BL54L15, Fanstel BM15, and the Minew modules. None of them was found on LCSC.
- **Apple TV:** support for HID consumer-control usages (play/pause, volume) is outside the scope of this note [UNVERIFIED].
