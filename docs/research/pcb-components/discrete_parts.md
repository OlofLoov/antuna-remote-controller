# Discrete parts for the 2xAAA BLE TV remote

Researched 2026-11-25. This goes with `ble_module.md`, which recommends the Raytac AN54LQ-15 (nRF54L15).

**Design limits:**
- Supply: 2xAAA, no regulator. 3.2 V fresh, 2.4 V on NiMH, low-battery warning at 2.2 V under load, must work at 2.0 V.
- Enclosure: 40 x 150 mm, about 11 mm thick over the PCB. 3D-printed key caps.

**Labels used in this file:**
- **[DS]**: value read from the manufacturer's datasheet. I downloaded each PDF and extracted the text with `pdftotext`.
- **[listing]**: value taken only from the LCSC/JLCPCB parameter listing.
- **[UNVERIFIED]**: not checked against a primary source.

**Stock and basic/extended status:** taken from the JLCPCB catalog mirror at jlcsearch.tscircuit.com on 2026-11-25. lcsc.com itself blocked automated queries (HTTP 403), so I could not read LCSC stock directly. "not found" means the part is not in the JLCPCB assembly catalog. It may still be orderable from LCSC or DigiKey.

---

## 1. Tactile switches (12 keys)

### Chosen: XKB Connection TS-1187A-B-A-B
- **LCSC:** C318884. JLCPCB **Basic**. Stock 665,211.
- **Datasheet:** XKB drawing TS-1187A-X-X-X, https://atta.szlcsc.com/upload/public/pdf/source/20211011/CF465E46D2427DB66E133733EF19F823.pdf. XKB product spec SP-A0162-41 (2024-08-19), https://www.ickey.cn/static-pf/datasheet/41/66/b9e0/4166b9e0a0b21fd51f6971764e2d1164.pdf. The LCSC copy is at https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_XKB-Connection-TS-1187A-B-A-B_C318884.pdf (blocked for me).
- **How the part number decodes [DS drawing]:** TS-1187A-*force*-*height*-*stem*.
  - Force: A = 100 gf, **B = 160 gf**, C = 260 gf.
  - Height code: **A = 1.5 mm**, B = 1.6, C = 1.7, D = 2.0, E = 2.5, …
  - Stem ("fixed column"): A = PA46, **B = brass**.
- **Values [DS]:**
  - Body 5.1 x 5.1 mm. Footprint span 6.5 mm.
  - **Actuator: round stem, Ø 2.0 mm**, brass.
  - Travel 0.25 mm (drawing: 0.2 ± 0.1).
  - Contact rating 50 mA, 12 V DC. Contact resistance 100 mΩ max.
  - **Life test: 300,000 cycles** (spec §7). LCSC lists 100k.
  - Metal dome, so it has a tactile snap.
- **Fit to the requirement:**
  - 160 gf = 1.57 N, which sits at the low edge of the 1.5–3.0 N window.
  - Height 1.5 mm is inside the 1.5–2.5 mm window.
- **Plunger:** the Ø 2.0 mm brass stem is small. Give the printed cap a plunger of about Ø 1.6–2.0 mm, centred on the stem. Guide the cap in the top shell, not on the switch: the Alps spec (below) warns that off-centre or side loads degrade the click, and the same applies to this part.

### Heavier, crisper option from the same family: TS-1187A-C-C-B
- **LCSC:** C318889. **Extended**. Stock 121,665.
- **Values:** 260 gf (2.55 N) and 1.7 mm high [DS drawing code]. 100k cycles [listing].
- **When to use it:** if 160 gf feels too light under a printed cap. The cap's own weight and friction cancel part of the switch force.

### Alternate (different maker): Alps Alpine SKQGADE010
- **LCSC:** C116647. Extended. Stock 30,399.
- **Datasheet:** catalog https://tech.alpsalpine.com/cms.media/product_catalog_ta_02_skqg_en_d003713f01.pdf. Spec https://tech.alpsalpine.com/cms.media/SKQGAD_KQG_704_EN_4d96c9216e.pdf.
- **Values [DS]:**
  - Top push, **2.55 N**, travel 0.25 mm, **100,000 cycles**.
  - Initial contact resistance 100 mΩ max.
  - **5.2 x 5.2 x 1.5 mm**. Alps calls this the "sharp feeling" type, with tactile feedback.
  - Rating 50 mA at 12 V DC, minimum 10 µA at 1 V DC. -40 to +90 °C.
- **Stem diameter:** shown only in the drawing, which I could not extract as text **[UNVERIFIED]**.
- **Spec notes C7–C11:** press only the centre of the stem, and apply no side force.
- Other SKQG forces are 0.98 N (AFE), 1.57 N (ABE) and 3.43 N (AKE).

### Rejected
| Part | Why |
|---|---|
| CK PTS526 SM15 | 1.6 N, ok, but extended and more expensive |
| CK PTS810 / PTS815 | 2.5 mm tall, 4 N, or stock of 3 |
| Alps SKRPACE010 | only 50k cycles [listing] |
| C&K KMR2 | 3–4 N |
| Alps SKSGAAE010 | 4.08 N |

---

## 2. IR LED (940 nm, about 100 mA pulses at 38 kHz, 1/3 duty)

### Chosen: Vishay TSAL6200, 5 mm through-hole, laid flat at the top edge
- **LCSC:** C55528. Extended. Stock 9,425. It is a through-hole part: use JLCPCB THT assembly or hand-solder.
- **Datasheet:** https://www.vishay.com/docs/81010/tsal6200.pdf
- **Values [DS]:**
  - λp 940 nm. **Half-intensity angle ±17°**.
  - **Ie 40 min / 72 typ / 200 max mW/sr at IF = 100 mA**, tp = 20 ms.
  - **VF 1.35 typ / 1.6 max at IF = 100 mA**. VF 2.2 typ / 3.0 max at 1 A, 100 µs.
  - Absolute maximums: IF 100 mA DC. **IFM 200 mA at tp/T = 0.5, tp = 100 µs**. IFSM 1.5 A.
  - tr = 15 ns. Ø 5 mm body, Ø 5.8 mm flange.
- **Mounting:** lay the LED flat, with the leads bent 90° and the lens out through the top edge. The centreline then sits about 2.9 mm above the PCB. Alternatively, sink it into a PCB notch so the body straddles the board. Either way it fits in 11 mm.

### Alternate, all-SMD: Vishay VSMB2948SL, side-looking (edge-emitting)
- **LCSC:** C6604342. Extended. Stock 215, which is thin.
- **Datasheet:** https://www.vishay.com/docs/83498/vsmb2948sl.pdf (Rev. 1.1, 24-Mar-2025)
- **Values [DS]:**
  - Side-looking, **2.3 x 2.55 x 2.3 mm**. λp 940 nm. **±25°**.
  - **Ie 10 min / 20 typ / 30 max mW/sr at IF = 100 mA**. 90 mW/sr at 500 mA, 100 µs.
  - **VF 1.15 min / 1.35 typ / 1.6 max at 100 mA**.
  - Absolute maximums: IF 100 mA DC, IFSM 500 mA at tp = 100 µs.

### 3 mm through-hole option: Vishay TSAL4400
- **LCSC:** C94135. Stock 967.
- **Datasheet:** https://www.vishay.com/docs/81006/tsal4400.pdf
- **Values [DS]:** ±25°. Ie 16 / 36 / 80 mW/sr at 100 mA. VF 1.35 typ / 1.6 max at 100 mA. IFM 200 mA at tp/T = 0.5.
- **VSLB3940** (3 mm, ±22°, C139835, stock 2,696) is a possible upgrade, but I did not get its datasheet (the vishay.com URL returned HTML). It is [UNVERIFIED]. The LCSC listing says 32 mW/sr at 100 mA.

### Rejected: Everlight IR26-61C/L302/TR8 (side view, C181893)
- **Datasheet:** DIR-0000579 Rev. 5, https://www.lcsc.com/datasheet/lcsc_datasheet_Everlight-Elec-IR26-61C-L302-TR8_C181893.pdf (I read the endrich.com copy).
- Its 2θ½ = 20°, or ±10°, is attractive. Ie is 40 mW/sr typ at 100 mA, but only for pulses ≤ 100 µs at ≤ 1 % duty.
- Its absolute maximum is **IF 65 mA continuous**, and the datasheet gives no peak-current rating. 100 mA at 33 % duty is therefore outside the datasheet.

### 5 mm flat vs. SMD side-looker
**Reach estimate.** On axis, irradiance is E = Ie / d². I assume a TV receiver needs about 0.5 mW/m², which is conservative. For comparison, Vishay's TSOP93x needs Ee min 0.07 typ / 0.15 max mW/m² [DS].

| LED | Ie at 100 mA (typ / min) | d at 0.5 mW/m² (typ / min) | Height |
|---|---|---|---|
| TSAL6200, 5 mm flat | 72 / 40 mW/sr | **12 m / 8.9 m** | 5.8 mm |
| TSAL4400, 3 mm flat | 36 / 16 mW/sr | 8.5 m / 5.7 m | 3.2 mm |
| VSMB2948SL, SMD side | 20 / 10 mW/sr | 6.3 m / **4.5 m** | 2.3 mm |

**Verdict:**
- The 5 mm TSAL6200 is the only option with comfortable margin for 5 m+ at end of life. Its ±17° beam is also the closest to the target.
- The SMD part keeps the whole board on one reflow pass. However, it misses 5 m with a min-bin part at reduced current.

### Resistor and current at low battery
**Voltage drops in the LED path:**
- P-FET reverse-protection drop at 100 mA: 62 mΩ max × 0.1 A ≈ 6 mV.
- N-FET switch drop at 100 mA: 34 mΩ max × 0.1 A ≈ 3.4 mV.
- Both are negligible.

**Recommended: R = 10 Ω** (0805 or 1206 size), with the TSAL6200:

| Supply | LED current |
|---|---|
| 2.4 V | about 100 mA |
| 3.2 V | about (3.2 − 1.5) / 10 ≈ 170 mA peak. This is within IFM 200 mA: a 38 kHz pulse is 8.8 µs at duty ≤ 0.5 |
| 2.2 V | ≈ 85 mA |
| 2.0 V | ≈ 65 mA |

**If you prefer R = 18 Ω:** 100 mA at 3.2 V, but only about 38 mA at 2.0 V, so range shrinks by about √(100/38) ≈ 1.6x.

**For the VSMB2948SL:** use R ≥ 15 Ω. Its datasheet gives no repetitive-pulse rating above the 100 mA DC limit.

---

## 3. N-channel MOSFET (IR LED low-side switch, gate from GPIO at 1.8–2.0 V)

### Chosen: Alpha & Omega AO3416, SOT-23
- **LCSC:** C43307. Extended. Stock 20,927. There are other AO3416 listings: C5148471, C5248038.
- **Datasheet:** https://www.aosmd.com/res/datasheets/AO3416.pdf
- **Values [DS]:**
  - VDS 20 V. ID 6.5 A at 25 °C. VGS ±8 V.
  - **VGS(th) 0.4 / 0.7 / 1.1 V**.
  - **RDS(on) at VGS = 1.8 V, ID = 5 A: 21 typ / 34 max mΩ**.
  - RDS(on) at 2.5 V: 18 / 26 mΩ. At 4.5 V: < 22 mΩ.
  - The datasheet also has a VGS = 1.5 V curve.
- **Fit:** at 2.0 V GPIO drive and 0.1–0.17 A, the drop is under 6 mV. The 0.5 A requirement is exceeded by more than 10x.

### Alternate: Vishay Si2312CDS-T1-GE3
- **LCSC:** C142518. Extended. Stock 9,613.
- **Datasheet:** https://www.vishay.com/docs/65900/SI2312CD.pdf (Doc 65900)
- **Values [DS]:**
  - VDS 20 V. VGS(th) 0.45–1.0 V.
  - **RDS(on) at VGS = 1.8 V, ID = 4.3 A: 34.5 typ / 41.4 max mΩ**. At 2.5 V: 29.6 / 35.6 mΩ.

### Not chosen: AO3400A (C20917, JLCPCB Basic)
- **Datasheet:** https://www.aosmd.com/res/datasheets/AO3400A.pdf
- Specified only down to VGS = 2.5 V (< 48 mΩ), and its **VGS(th) max is 1.45 V**. It would probably work at 2.0 V, but nothing is guaranteed at 1.8–2.0 V.

### Circuit notes
- Add a 100 kΩ gate pull-down so the LED stays off while the MCU boots.
- An optional 100 Ω series gate resistor is fine. At 38 kHz switching losses are irrelevant.

---

## 4. Reverse-polarity protection: P-channel MOSFET, gate to GND

### Chosen: Diodes Inc. DMP2035U-7, SOT-23
- **LCSC:** C110499. Extended. Stock 219,049.
- **Datasheet:** https://www.diodes.com/assets/Datasheets/DMP2035U.pdf
- **Values [DS]:**
  - BVDSS −20 V. VGSS ±10 V.
  - **VGS(th) −0.4 / −0.7 / −1.0 V**.
  - **RDS(on) at VGS = −1.8 V, ID = −2 A: 41 typ / 62 max mΩ**.
  - RDS(on) at −2.5 V: 30 / 45 mΩ. At −4.5 V: 23 / 35 mΩ.
  - IDSS −1 µA max. Body diode VSD −0.7 / −1.0 V.
- **Drop at 2.0 V battery (VGS ≈ −2.0 V, so the −1.8 V max applies):**
  - 20 mA average: **≈ 1.2 mV**.
  - 150 mA peak: **≈ 9 mV**.
  - 170 mA IR peak: ≈ 11 mV.
- **Compared with a Schottky diode:** a Schottky in series would cost 0.25–0.35 V, about 15 % of a 2.0 V battery.
- **Wiring:** drain to the battery + contact, source to the circuit VBAT, gate to GND. Add an optional 100 kΩ from gate to GND, with 10 kΩ…100 kΩ in series if ESD at the contacts is a concern.
- **Reversed cells:** VGS goes positive, the FET turns off, and the body diode is reverse-biased.
- **Placement:** put the 100 µF bulk capacitor after the FET.

### Alternate: Alpha & Omega AO3401A, JLCPCB Basic
- **LCSC:** C15127. Basic. Stock 1,053,656.
- **Datasheet:** https://www.aosmd.com/res/datasheets/AO3401A.pdf
- **Values [DS]:**
  - VDS −30 V.
  - **VGS(th) −0.5 / −0.9 / −1.3 V**.
  - **RDS(on) at −2.5 V, −2.5 A: 60 typ / 85 max mΩ**. The datasheet has no −1.8 V row.
- **Risk:** at VGS = −2.0 V it is about 0.7 V past the worst-case threshold, so in practice it will be on, but RDS(on) is not guaranteed. Use it only if you want a Basic part. Even at a pessimistic 200 mΩ, the drop at 150 mA would be 30 mV.

### Also viable
- **Vishay Si2333CDS** (C144846, stock 10,149, 12 V): 59 mΩ at −1.8 V [listing; DS not read].
- **AO3415A** (C133233): a −1.8 V figure appears only in the C181094 listing [listing only].

### FET vs. relying on a polarized battery holder
**Do not rely on the holder alone.**
- With ordinary spring/button contacts, a reversed AAA's flat negative end still touches the flat positive button. The circuit sees −3 V. The nRF absolute minimum on VDD is −0.3 V [UNVERIFIED value; check the SoC datasheet].
- Mechanical polarity only works if the + contact sits behind ribs that the flat − end cannot reach. That is possible in a 3D-printed door/cradle, but you would have to design and test it.
- The FET costs about $0.05, takes under 10 mV, and makes the issue go away.
- Keep both protections if you can: the ribs protect usability (a reversed cell simply does nothing), and the FET protects the electronics.

---

## 5. IR receiver for learning codes

### Chosen for learning: Vishay TSMP96000TR (carrier-out sensor, not a demodulator)
- **LCSC:** C20346073 (JLCPCB part page exists, **Extended**). **Stock: not found**: the JLCPCB page shows no stock, and the part is missing from the stock mirror.
- **Datasheet:** https://www.vishay.com/docs/82906/tsmp96000.pdf (Rev. 1.1, 25-Nov-2024)
- **Values [DS]:**
  - **Supply 2.0–5.5 V**. Supply current 0.25 / **0.35** / 0.45 mA at VS = 3.3 V.
  - **AC-coupled response 30–60 kHz, all data formats**.
  - **Output = carrier out** (active low), described as being "for code learning".
  - Output accuracy ±1 carrier cycle on burst length.
  - Minimum irradiance 12 typ / 25 max mW/m². Transmission distance 1.8 m (TSAL6200 at 50 mA). ±50°.
  - **SMD Panhead, side-view tape (TR), 7.5 W x 5.3 H x 4.0 D mm**.
- **Why it fits:**
  - It passes the raw carrier, so firmware can measure it with a TIMER capture or GPIOTE/PPI count. That means 36, 38, 40 and 56 kHz codes are captured **with their real carrier frequency**, and you can replay them exactly.
  - Its low sensitivity is fine for learning, which is done at 5–30 cm.
- **Power:** 0.35 mA is far too much to leave on: the whole remote should sleep at a few µA. Power VS from a GPIO, or through a small P-FET, only while in learn mode.
  - A GPIO can source 0.45 mA with little drop [UNVERIFIED: check the nRF54L15 VOH spec]. A high-drive pin set as output-high is fine.
  - Add 100 nF next to VS.

### Alternate: demodulating receiver rated to 2.0 V, Vishay TSOP33338 (TSOP333xx, Minimold)
- **LCSC/JLCPCB:** not found.
- **Datasheet:** https://www.vishay.com/docs/82742/tsop331.pdf
- **Values [DS]:**
  - **Supply 2.0–5.5 V**. ISD 0.25 / 0.35 / 0.45 mA at 3.3 V.
  - Transmission distance 39 m. Minimold, leaded, 5.4 W x 6.35 H x 4.9 D mm. Bends and cuts are offered, including bent-lead (side-view) options.
  - Variants:

    | Series | AGC level |
    |---|---|
    | TSOP331xx | AGC1 |
    | TSOP333xx | AGC3 |
    | TSOP335xx | AGC5 |

    Each comes in 30/33/36/38/40/56 kHz.
- **Other low-voltage Vishay options:**
  - **TSOP936xx** (https://www.vishay.com/docs/82842/tsop936.pdf): 2.0–3.6 V [DS], 0.37 mA typ, same Minimold package. Vishay recommends an RC filter on VS below 2.2 V. Its AGC6 is the strongest noise suppression, which also gives the lowest code compatibility, so it is a poor choice for learning.
  - **"V" low-voltage option** (https://www.vishay.com/docs/82382/v.pdf, e.g. TSOP36240VTT SMD, TSOP75240VTR Heimdall): 2 V only from +5 to +85 °C, and 2.5 V minimum over the full −25 to +85 °C range. Vishay gives these only as ordering examples [DS]. Availability is [UNVERIFIED].
- **Common SMD receivers that are not suitable:** TSOP75xxx, TSOP36xxx, TSOP57xxx, IRM-H638T, IRM-V838M3. Their listings say 2.5–5.5 V or 2.7–5.5 V.

### Carrier-frequency concern with a demodulating receiver
- A 38 kHz band-pass part still decodes 36 and 40 kHz remotes at learning distance, with somewhat reduced sensitivity.
- 56 kHz codes (some Sharp, Denon/older RC-MM-type devices) are heavily attenuated and may not be learned at all.
- A demodulator throws away the carrier frequency. On replay you would have to guess 38 kHz, and some 36 kHz (RC-5/RC-6) or 40 kHz (Sony) TVs are less tolerant of that.
- Formats outside 30–60 kHz (for example 455 kHz Bang & Olufsen) are unreachable with either part.
- **Conclusion:** use the TSMP96000 for learning. Add a TSOP333xx only if you also want long-range *receiving*, which a remote does not need.

---

## 6. Status LED (about 1–2 mA from a 2.0 V GPIO)

### Physics first: teal is not possible at 2.0 V
- Teal or cyan LEDs (around 490–505 nm) are InGaN, the same chemistry as blue, green and white. Their VF is about 2.6–3.0 V even at 2 mA.
  - Kingbright APTD1608LZGCK (525 nm) lists 2.65 V at 2 mA [listing].
  - ROHM SMLD12E3N1W (496 nm) lists 2.9 V [listing].
- At 2.0–2.6 V such an LED stays dark.
- Only AlGaInP colours (red, orange, amber, yellow, yellow-green at 570 nm) have VF below 2 V at mA currents.
- 570 nm yellow-green is the closest to "teal" that works. It reads lime-green, not teal.

**Options for a teal look:**
- **(a)** Put a yellow-green LED behind a cyan-tinted printed light pipe. The filter only removes light, so the hue shifts slightly toward green-cyan and the LED gets dimmer.
- **(b)** Add an InGaN teal LED that is lit only when VBAT > 2.9 V. This is not useful for a low-battery warning.

### Chosen: Kingbright APTD1608LSECK/J4-PF, orange 605 nm, low-current AlGaInP, 0603 (0.95 mm thick)
- **LCSC:** C5879215. Extended. Stock 657, which is low. Order early.
- **Datasheet:** https://www.kingbrightusa.com/images/catalog/SPEC/APTD1608LSECK-J4-PF.pdf
- **Values [DS]:**
  - **VF 1.5 min / 1.8 typ / 2.1 max at IF = 2 mA**. λdom 605 nm.
  - Iv 250 min / 450 typ mcd at 2 mA. That is very bright, so it is still clearly visible at 0.2–0.5 mA.
  - IF 30 mA DC max. 60° viewing angle.
- **Why orange:**
  - Lowest typical VF among the low-current parts.
  - Highest efficiency, which matters when only about 0.1–0.3 V is left across the resistor.
  - Amber/orange is also the conventional "low battery" colour.

### Alternate (greenest that can work): Kingbright APTD1608LCGCK, yellow-green 570 nm AlGaInP
- **LCSC:** C5342733. Extended. Stock 1,492.
- **Datasheet:** https://www.kingbrightusa.com/images/catalog/SPEC/APTD1608LCGCK.pdf
- **Values [DS]:**
  - **VF 1.5 / 1.9 / 2.1 V at 2 mA**. λdom 570 nm.
  - **Iv only 6 min / 8 typ mcd at 2 mA**, about 50x dimmer than the orange part.
- At 2.0 V a typical part gets well under 1 mA, so it will be dim. Use it only if the colour matters more than end-of-life visibility.

### JLCPCB Basic fallback
- **KT-0603R red**, C2286, Basic, stock 8.6 M.
- Listing values: VF 1.8–2.4 V at 20 mA, 615–630 nm [listing only]. There is no low-current data.

### Resistor (GPIO sourcing, LED to GND, orange part)
**Assumptions:**
- GPIO high-side drop of about 0.05–0.1 V at 1–2 mA [UNVERIFIED for nRF54L15; check VOH vs. IOH].
- VF about 1.75 V at 1–1.5 mA, read from VF ≈ 1.8 V typ at 2 mA (typical-bin part).

| Target | Formula | Result |
|---|---|---|
| 1.5 mA at **2.0 V** | (2.0 − 0.05 − 1.75) / 1.5 mA ≈ 133 Ω | **120 Ω** |
| 1.5 mA at **3.2 V** | (3.2 − 0.1 − 1.85) / 1.5 mA ≈ 833 Ω | **820 Ω** |

**Recommended single value: 330 Ω.**
- About 3.8 mA at 3.2 V (use firmware PWM at about 30 % if that is too bright).
- About 0.6 mA at 2.0 V (typical-bin part), which is still visible at 450 mcd/2 mA efficiency.
- A max-VF (2.1 V) part will be dark at 2.0 V whatever the resistor. This is a datasheet-guaranteed limit, so the low-battery warning should also be signalled over BLE or with a blink pattern triggered at 2.2 V.

---

## 7. Bulk capacitor next to the IR LED (about 100 µF, under 2 mm tall)

### Chosen: Samsung CL31A107MQHNNNE, 100 µF 6.3 V X5R ±20 %, 1206
- **LCSC:** C15008. JLCPCB **Basic**. Stock: **not shown** (the mirror returned null and the JLCPCB page did not show a quantity).
- **Datasheet:** the Samsung reference spec, copy at https://static.chipdip.ru/lib/481/DOC034481301.pdf, and the JLCPCB-hosted C15008 PDF.
- **Values [DS copy]:**
  - **T = 1.6 ± 0.2 mm** (meets < 2 mm).
  - **Insulation resistance ≥ 50 MΩ·µF**, i.e. ≥ 0.5 MΩ at 100 µF. That is a **worst-case leakage of ≤ 6.4 µA at 3.2 V**. Another copy of the sheet says "10,000 MΩ or 50 MΩ·µF, whichever is smaller", so check the current Samsung sheet.
- **Real leakage:** typically orders of magnitude below that IR limit (nA range) [UNVERIFIED, general MLCC behaviour; measure one].
- **DC bias:** X5R 1206 100 µF loses a large share of its capacitance at 3 V. Plan on about 40–60 µF effective [UNVERIFIED; check Samsung's DC-bias curve]. Even 40 µF droops only about 22 mV per 8.8 µs pulse at 100 mA (0.88 µC). Place 2x if you want margin.

### Alternate: tantalum, CA45A-B-10V-100UF-K (manganese tantalum, case B 3528, 1.9 mm)
- **LCSC:** C2976906. Extended. Stock 27,166.
- **Datasheet:** not read. The listing gives a **leakage of 10 µA** (the classic DCL = 0.01·C·V at rated 10 V) [listing only].
- At 3.2 V (32 % of rated voltage) real leakage is much lower, but the guaranteed figure is 1.5x worse than the MLCC's IR limit.
- Case-B tantalums are 1.9 mm (CA45A) to 2.1 mm (KEMET T491B, T520B) tall, which is borderline for the 2 mm limit.

### Leakage comparison (100 µF, guaranteed limits)
| Type | Example | Spec limit | At 3.2 V |
|---|---|---|---|
| Ceramic X5R | CL31A107MQHNNNE | IR ≥ 50 MΩ·µF [DS] | ≤ 6.4 µA worst case; typically nA |
| MnO2 tantalum | CA45A-B / T491B | DCL ≤ 0.01CV (10 µA at 10 V) [listing / general] | ≤ 10 µA at rated V, lower at 3.2 V |
| Polymer tantalum | KEMET T520B107M006 (C2158125, 2.1 mm, stock 40) | DCL typically 0.1CV = 63 µA [UNVERIFIED for this PN] | worst of the three |

**Why this matters:** the nRF sleep current is about 1–3 µA. A polymer cap could multiply standby drain.

**Verdict:** ceramic X5R. It is the lowest leakage, the thinnest, Basic, and cheap.

---

## 8. AAA battery contacts (cells beside the PCB's bottom edge, series bridge in the door)

All Keystone parts below are from Keystone catalog M75. They are mechanical parts, **not in the JLCPCB catalog ("not found")**. Buy them from DigiKey or Mouser and fit them by hand.

### PCB-edge end (chosen): Keystone 5204 (−, spring with tab) + Keystone 5226 (+, button with tab)
- **Datasheet:** https://www.keyelco.com/userAssets/file/K75p17.pdf ("Battery contacts for molded cases").
- **Values [DS]:**
  - For "AAA, AAAA, N, A23, A27".
  - Plate 0.020" (0.51 mm) nickel-plated steel. Spring of nickel-plated spring steel.
  - **"Solder Tab" design for either wire lead or PC mounting**. The plates are 9.2–10.4 mm wide.
- **Mounting:** the plates slide into ribs printed in the case. The tabs bend onto, or pass through, slots at the PCB's bottom edge.
- Keystone 5203 / 5225 are the same contacts without tabs.
- **Stock:** DigiKey listed 5204 and 5226 as stocked parts in search results. I did not read quantities.

### Bridge (series) contact in the battery door (chosen): Keystone 5213 (dual, right) or 5214 (dual, left)
- **Datasheet:** same page, [DS].
- **Values [DS]:** a dual contact for AAA molded cases, **0.827" (21.0 mm) wide**, which is 2 x 10.5 mm cell pitch.
- It joins cell 1's + to cell 2's − at the far end.
- Pick right or left according to which cell has its + at the door end.
- 5254 / 5259 are the dual-spring versions.

### Alternate for the PCB edge: Keystone 230-1 "Off-Board" edge contact
- **Datasheet:** https://www.keyelco.com/userAssets/file/K75p15.pdf [DS].
- **Values:** "AAA, AAAA, N, 12V". "Off-Board edge mounting design". 0.008" (0.20 mm) nickel-plated spring steel.
- Distributors describe it as symmetric (it works as + or −). One listing gives about 5.1 x 13.4 mm [listing].
- Because it straddles the board edge, the cell centreline can sit near the PCB plane. That suits an 11 mm enclosure.
- **[UNVERIFIED]:** exact mounting (through-hole vs. edge-clip) varies between listings. Check the drawing before layout.

### Not suitable for 11 mm
These stand up from the PCB and are too tall:

| Part | Type | Height |
|---|---|---|
| Keystone 179 (−) / 180 (+) / 181 (dual) | AAA "slide-in PC mount" coil contacts | 20 mm plate (.787") [DS p16] |
| Keystone 1020-1 / 1076-1 / 1076-2 | AAA SMT slide-in | H = 11.1 mm [DS p15] |

**MPD and Linx:** not researched in depth. Keystone covers all three roles.

---

## 9. Programming / debug connector

| Option | PCB cost | Tool cost | Notes |
|---|---|---|---|
| **Tag-Connect TC2030-NL footprint** (cable **TC2030-CTX-NL** to a 10-pin 1.27 mm Cortex header on the J-Link or nRF DK) | 0. Six pads plus three holes, no part to place | about $43 cable (tag-connect.com). Optional TC2030-CLIP | No-legs version: hold it by hand or use the clip. Footprint per the TC2030-IDC-NL datasheet. Uses about 66 % less area than an FTSH-105 header |
| 2x5 1.27 mm SMD header (Samtec FTSH-105 style) | about $0.5–1.5 part plus placement. About 3 mm tall, so it may hit the shell | 0 (standard Cortex cable) | Robust, but needs space and height. Could be left unpopulated |
| Pogo pads (5 test pads: VDD, GND, SWDIO, SWCLK, nRESET) | 0 | a few dollars of pogo pins plus a printed jig | Cheapest, but a jig must be built and aligned |

**Recommendation for a few units: TC2030-NL footprint.** It costs nothing on the board and is the smallest footprint. One cable works for every future board. Hold it by hand for the occasional flash.

---

## Chosen parts summary

| # | Function | MPN (maker) | LCSC | JLC | Stock (2026-11-25) | Key datasheet values | Alternate |
|---|---|---|---|---|---|---|---|
| 1 | Key switch x12 | TS-1187A-B-A-B (XKB) | C318884 | Basic | 665,211 | 160 gf (1.57 N), 5.1x5.1x1.5 mm, Ø 2.0 mm brass stem, 0.25 mm travel, 300k-cycle life test | TS-1187A-C-C-B 260 gf/1.7 mm (C318889); Alps SKQGADE010 2.55 N, 5.2x5.2x1.5 (C116647) |
| 2 | IR LED | TSAL6200 (Vishay), 5 mm laid flat | C55528 | Ext (THT) | 9,425 | ±17°, Ie 72 typ/40 min mW/sr at 100 mA, **VF 1.35/1.6 V at 100 mA**, IFM 200 mA | VSMB2948SL side-looking SMD, ±25°, 20 mW/sr, VF 1.35/1.6 V (C6604342, 215 pcs) |
| 3 | IR LED switch N-FET | AO3416 (AOS) | C43307 | Ext | 20,927 | RDS(on) ≤ 34 mΩ at VGS = 1.8 V, Vth 0.4–1.1 V, 20 V, 6.5 A | Si2312CDS-T1-GE3 ≤ 41.4 mΩ at 1.8 V (C142518) |
| 4 | Reverse-polarity P-FET | DMP2035U-7 (Diodes) | C110499 | Ext | 219,049 | RDS(on) ≤ 62 mΩ at VGS = −1.8 V, Vth −0.4…−1.0 V; drop ≈ 9 mV at 150 mA | AO3401A (C15127, Basic), ≤ 85 mΩ at −2.5 V only |
| 5 | IR learning receiver | TSMP96000TR (Vishay) | C20346073 | Ext | not found | 2.0–5.5 V, 0.35 mA typ, carrier out 30–60 kHz, SMD side-view 7.5x5.3x4.0 mm | TSOP33338 demodulator, 2.0–5.5 V, Minimold (LCSC not found) |
| 6 | Status LED | APTD1608LSECK/J4-PF (Kingbright), orange | C5879215 | Ext | 657 | VF 1.8 typ/2.1 max at 2 mA, 450 mcd at 2 mA; 330 Ω (120 Ω for 2.0 V, 820 Ω for 3.2 V) | APTD1608LCGCK yellow-green 570 nm, VF 1.9 V at 2 mA, 8 mcd (C5342733) |
| 7 | Bulk cap | CL31A107MQHNNNE (Samsung) 100 µF 6.3 V X5R 1206 | C15008 | Basic | not shown | 1.6 mm thick, IR ≥ 50 MΩ·µF (≤ 6.4 µA at 3.2 V) | CA45A-B-10V-100UF-K tantalum 1.9 mm, 10 µA (C2976906) |
| 8 | Battery contacts | Keystone 5204 (−) + 5226 (+) at PCB edge; 5213/5214 dual bridge in door | not found | – | DigiKey | AAA, 0.51 mm Ni-plated steel, solder tab for PC mount; bridge 21.0 mm | Keystone 230-1 off-board edge contact (x2) |
| 9 | Debug | Tag-Connect TC2030-NL footprint + TC2030-CTX-NL cable | – | – | – | 6-pad SWD, no PCB part | 2x5 1.27 mm FTSH-105-style header |
