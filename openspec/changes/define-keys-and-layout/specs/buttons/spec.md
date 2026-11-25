## ADDED Requirements

### Requirement: Twelve keys
The remote SHALL have exactly twelve keys: up, down, left, right, select, back, Home, play/pause, volume up, volume down, mute and Power. It SHALL have no number keys and no touch surface.

#### Scenario: Counting keys
- **GIVEN** a finished remote
- **WHEN** the user counts what they can press
- **THEN** there are twelve keys and nothing else to press, swipe or touch

### Requirement: Keys found by touch
The remote SHALL let a user find the d-pad, select, back, play/pause and volume by touch in a dark room, with each of those keys differing from its neighbors in shape or height.

#### Scenario: In the dark
- **GIVEN** a user who has used the remote for a day, in a dark room
- **WHEN** they press back, then play/pause, then volume up without looking
- **THEN** each press lands on the intended key

### Requirement: Every press clicks
Each key SHALL give a tactile click the user can feel, at an operating force between 1.5 N and 3.0 N measured at the center of the key cap.

#### Scenario: Force gauge
- **GIVEN** a remote on the bench and a force gauge
- **WHEN** each key is pressed at the center of its cap
- **THEN** it clicks at between 1.5 N and 3.0 N

### Requirement: Held keys repeat only where it helps
The d-pad arrows and the volume keys SHALL repeat while held, starting 400 ms (plus or minus 50 ms) after the press and repeating 8 times a second (plus or minus 1). Select, back, Home, play/pause, mute and Power SHALL act once per press however long they are held, except for the pairing hold.

#### Scenario: Scrolling the guide
- **GIVEN** Antuna shows the guide
- **WHEN** the user holds down for two seconds
- **THEN** the focus moves one row at once and then about 8 rows a second until release

#### Scenario: Holding play/pause
- **GIVEN** a movie plays
- **WHEN** the user holds play/pause for two seconds
- **THEN** the movie pauses once and stays paused

### Requirement: Power needs a deliberate press
The Power key SHALL sit below the surface around it, so that a hand gripping the remote or the remote lying face down does not press it.

#### Scenario: Face down on the sofa
- **GIVEN** the remote lies face down on a sofa cushion with a hand resting on its back
- **WHEN** the hand presses down
- **THEN** no key acts

### Requirement: Pairing hold
Holding back and Home together for 3 seconds SHALL put the remote in Bluetooth pairing mode for 60 seconds, shown by the status light blinking, and SHALL send nothing else to the Apple TV.

#### Scenario: Entering pairing mode
- **GIVEN** the remote is not in pairing mode
- **WHEN** the user holds back and Home together for 3 seconds
- **THEN** the status light blinks and the remote shows in the Apple TV's Bluetooth list

#### Scenario: Pairing times out
- **GIVEN** the remote is in pairing mode
- **WHEN** 60 seconds pass without a pairing
- **THEN** the light stops blinking and the remote keeps any pairing it had

### Requirement: The status light says little
The remote SHALL have one small status light that is dark in normal use and lights only to show pairing mode and a low battery.

#### Scenario: Normal use
- **GIVEN** the remote is paired and the batteries are good
- **WHEN** the user presses keys
- **THEN** the status light stays dark
