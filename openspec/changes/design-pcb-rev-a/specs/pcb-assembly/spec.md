## ADDED Requirements

### Requirement: Arrives assembled
A rev A board SHALL arrive from the assembler with every part fitted, so that at most the two wires to the battery contacts and, if the assembler cannot fit it, the IR LED's two leads are soldered by hand.

#### Scenario: Unboxing boards
- **GIVEN** a delivery of assembled rev A boards
- **WHEN** the owner counts what is left to fit
- **THEN** it is the two battery wires, plus the IR LED only if the order said so

### Requirement: Programs without a connector
A board SHALL be programmed and debugged through pads that a spring-pin cable presses onto, with no connector soldered on.

#### Scenario: First flash
- **GIVEN** a bare assembled board powered from a bench supply at 3.0 V
- **WHEN** the owner presses the programming cable onto its pads and flashes the firmware
- **THEN** the firmware runs and the board advertises over Bluetooth

### Requirement: Fits under 11 mm
Every part on the board SHALL sit on its top side and stand no more than 2.1 mm above the board, except the IR LED and the IR receiver at the top edge, so the remote stays within 11 mm over the keys and at its top end.

#### Scenario: Caliper on a board
- **GIVEN** an assembled board
- **WHEN** the tallest part on the top side is measured, the IR LED and IR receiver aside
- **THEN** it stands no more than 2.1 mm above the board, and the bottom side has no parts

### Requirement: Each key reads alone and together
Each of the twelve keys SHALL read on its own pin, so any key or any two keys held together register exactly as pressed.

#### Scenario: Pairing hold
- **GIVEN** a board running test firmware that prints key changes
- **WHEN** back and Home are held together, then each key is pressed alone
- **THEN** the log shows both keys down together, then each key on its own, and nothing else

### Requirement: Bluetooth across the room
A board in its enclosure SHALL keep its Bluetooth link to an Apple TV 10 m away with a clear line of sight, held in a hand at its battery end.

#### Scenario: Far end of the room
- **GIVEN** a paired remote held at its battery end 10 m from the Apple TV
- **WHEN** the user presses right 20 times, pointing the remote away from the Apple TV so infrared cannot reach it
- **THEN** the focus moves 20 times

### Requirement: Low cells keep it running
The board SHALL keep running, without resetting, through infrared bursts from cells at 2.0 V.

#### Scenario: A burst on tired cells
- **GIVEN** a board powered from a 2.0 V supply with 2 Ohm in series, standing in for two worn AAA cells
- **WHEN** it sends 50 infrared frames back to back
- **THEN** it does not reset, and its supply never drops below 1.8 V on a scope
