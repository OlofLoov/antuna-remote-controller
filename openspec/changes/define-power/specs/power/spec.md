## ADDED Requirements

### Requirement: Runs on two AAA cells
The remote SHALL run on two AAA cells, alkaline or NiMH, with no charger, no cable and no power switch.

#### Scenario: Rechargeable cells
- **GIVEN** two charged NiMH AAA cells
- **WHEN** the user puts them in
- **THEN** the remote works over both links

### Requirement: Batteries last two years
With alkaline cells, paired over Bluetooth and used for 200 key presses a day, the remote SHALL run for at least 24 months before the low battery warning, estimated from currents measured on the bench and confirmed by a cell left in a remote.

#### Scenario: Estimate from the bench
- **GIVEN** the measured sleep, connected and per-press charge of a rev A board
- **WHEN** they are combined for 200 presses a day and 20 hours a day idle
- **THEN** the estimate for a 1000 mAh alkaline pair is at least 24 months

### Requirement: Warns before it dies
When the cells have about 20 percent left, the remote SHALL blink its status light twice on each key press, and SHALL report its battery level over Bluetooth, while still working.

#### Scenario: Low cells
- **GIVEN** cells drained to the warning level on a bench supply
- **WHEN** the user presses select
- **THEN** select acts on the Apple TV and the status light blinks twice

#### Scenario: Battery level over Bluetooth
- **GIVEN** the remote is paired
- **WHEN** the battery level drops
- **THEN** the remote reports the new level, and the bench log records whether the Apple TV shows it anywhere

### Requirement: Infrared reach holds as cells drain
The remote SHALL work over infrared from 5 m, within 20 degrees of pointing straight at the Apple TV, from fresh cells down to the warning level.

#### Scenario: Old cells across the room
- **GIVEN** cells at the warning level and the Apple TV 5 m away
- **WHEN** the user points the remote within 20 degrees of the Apple TV and presses right
- **THEN** the focus moves on every one of 20 presses

### Requirement: Nothing lost on a battery change
Changing the cells SHALL keep the Bluetooth pairing and every setting, and the first press after new cells go in SHALL act.

#### Scenario: Fresh cells
- **GIVEN** a paired remote
- **WHEN** the user swaps the cells
- **THEN** the first press acts and no pairing is needed

### Requirement: Cells in backwards do no harm
Cells put in the wrong way round SHALL not damage the remote, and it SHALL work once they are turned round.

#### Scenario: Backwards cells
- **GIVEN** both cells put in backwards for a minute
- **WHEN** they are turned round
- **THEN** the remote works and nothing is warm or damaged
