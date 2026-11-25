## ADDED Requirements

### Requirement: Works over infrared with no setup
The remote SHALL control an Apple TV 4K over infrared out of the box, with no pairing and no learning step, on an Apple TV that has not been paired with another infrared remote.

#### Scenario: First use
- **GIVEN** a new remote and an Apple TV 4K showing the Home screen
- **WHEN** the user points the remote at the Apple TV and presses an arrow
- **THEN** the focus moves, with nothing set up on the Apple TV first

#### Scenario: Apple TV learned another remote
- **GIVEN** the Apple TV ignores the remote's infrared because it was paired with or taught another remote
- **WHEN** the user runs Settings, Remotes and Devices, Learn Remote, and presses the remote's buttons when asked
- **THEN** the remote controls the Apple TV from then on

### Requirement: Pairs over Bluetooth from the Apple TV settings
The remote SHALL pair with an Apple TV 4K from Settings, Remotes and Devices, Bluetooth, with no app, code or dongle, and SHALL show there under its own name.

#### Scenario: First pairing
- **GIVEN** the remote is in pairing mode and the Apple TV is on its Bluetooth settings
- **WHEN** the user selects the remote in the list of other devices
- **THEN** the Apple TV lists it as connected within 10 seconds, with no code to type

#### Scenario: Two Apple TVs in the house
- **GIVEN** the remote is paired over Bluetooth with one Apple TV and a second Apple TV is in range
- **WHEN** the user presses keys out of the second Apple TV's line of sight
- **THEN** only the paired Apple TV reacts

### Requirement: A press acts once
The remote SHALL make each button press act once on the Apple TV, whichever link carries it, including while Bluetooth is reconnecting.

#### Scenario: Both links reach the Apple TV
- **GIVEN** the remote is paired over Bluetooth and pointed at the Apple TV
- **WHEN** the user presses down once in Antuna's guide
- **THEN** the focus moves one row, not two

#### Scenario: First press after the remote slept
- **GIVEN** the remote has been idle long enough to drop its Bluetooth link
- **WHEN** the user presses up once while a channel plays full screen in Antuna
- **THEN** Antuna moves exactly one channel, and the bench log records how long the press took to act

### Requirement: Arrows move the focus
The remote SHALL move the focus up, down, left and right on the Home screen and in Antuna, one step per press, and keep stepping while a key is held, over either link.

#### Scenario: Home screen
- **GIVEN** the Apple TV shows the Home screen
- **WHEN** the user presses an arrow key
- **THEN** the focus moves one app in that direction

#### Scenario: Held key
- **GIVEN** Antuna shows the guide
- **WHEN** the user holds the down key for two seconds
- **THEN** the focus keeps moving down until the key is released and stops within one step of release

#### Scenario: Search field focused
- **GIVEN** Antuna's search field has the focus
- **WHEN** the user presses down
- **THEN** the focus leaves the field for the results, as it does with the Siri Remote

### Requirement: Select and back
The remote SHALL open the focused item with its select key and go back one screen with its back key, on the Home screen and in Antuna, over either link.

#### Scenario: Open and leave an app
- **GIVEN** Antuna is focused on the Home screen
- **WHEN** the user presses select, then back
- **THEN** Antuna opens, and back leaves it the way the Siri Remote's back button does

### Requirement: Play and pause
The remote SHALL pause and resume playback in Antuna with one key, as the Siri Remote's play/pause button does, over either link.

#### Scenario: Pausing a movie
- **GIVEN** a movie is playing in Antuna
- **WHEN** the user presses play/pause, then presses it again
- **THEN** the movie pauses, then resumes

### Requirement: Up and down change channel
The remote's up and down keys SHALL change channel in Antuna's full-screen Live the way a swipe on the Siri Remote does, with Antuna's swipe setting on changing channel, over either link.

#### Scenario: Next channel
- **GIVEN** the fourth of 42 channels in the current group plays full screen in Antuna
- **WHEN** the user presses up on the remote
- **THEN** the fifth channel plays and the bar reads "5 of 42"

#### Scenario: Past the end
- **GIVEN** the last channel in the group plays
- **WHEN** the user presses up
- **THEN** the first channel in the group plays

#### Scenario: Pressing again while a channel loads
- **GIVEN** a channel is still loading after a press
- **WHEN** the user presses down
- **THEN** Antuna skips the loading channel and moves on, as it does for a swipe

### Requirement: Home goes to the Home screen
The remote's Home key SHALL take the Apple TV to its Home screen from anywhere, including Antuna's full-screen Live, as the Siri Remote's TV button does, over either link.

#### Scenario: Leaving Live
- **GIVEN** a channel plays full screen in Antuna
- **WHEN** the user presses Home
- **THEN** the Apple TV shows its Home screen

### Requirement: Power puts the Apple TV to sleep
The remote's Power key SHALL put the Apple TV to sleep, and turn the TV off too when the Apple TV's HDMI-CEC setting does so for the Siri Remote, over either link.

#### Scenario: Going to bed
- **GIVEN** the Apple TV is awake
- **WHEN** the user presses Power
- **THEN** the Apple TV sleeps, or shows its sleep menu with sleep focused, and the bench log records which

### Requirement: Volume and mute control the TV
The remote's volume up, volume down and mute keys SHALL change the sound of the TV or receiver the Apple TV is set to control, as the Siri Remote's volume buttons do.

#### Scenario: Turning it up
- **GIVEN** the Apple TV controls the TV's volume over HDMI-CEC
- **WHEN** the user presses volume up three times
- **THEN** the TV's volume goes up three steps

#### Scenario: Held volume key
- **GIVEN** the TV's volume is at 10
- **WHEN** the user holds volume down for two seconds
- **THEN** the volume keeps going down until the key is released

#### Scenario: Mute
- **GIVEN** sound is playing
- **WHEN** the user presses mute, then mute again
- **THEN** the sound goes off, then comes back at the same level

### Requirement: Comes back after sleep
The remote SHALL work again without pairing after the Apple TV sleeps, after the remote's batteries are removed and put back, and after the remote has been out of range.

#### Scenario: Apple TV was asleep
- **GIVEN** the remote is paired and the Apple TV has been asleep for an hour
- **WHEN** the user presses a key on the remote
- **THEN** the bench log records whether the Apple TV wakes, over each link, and how long the press took

#### Scenario: Battery swap
- **GIVEN** the remote is paired over Bluetooth
- **WHEN** its power is removed for 10 seconds and restored
- **THEN** it works on the first key press with no new pairing, and that press is not lost
