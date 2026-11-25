## ADDED Requirements

### Requirement: Pairs from the Apple TV settings
The remote SHALL pair with an Apple TV 4K from Settings, Remotes and Devices, Bluetooth, with no app, code or dongle, and SHALL show there under its own name.

#### Scenario: First pairing
- **GIVEN** the remote is in pairing mode and the Apple TV is on its Bluetooth settings
- **WHEN** the user selects the remote in the list of other devices
- **THEN** the Apple TV lists it as connected within 10 seconds, with no code to type

#### Scenario: Two Apple TVs in the house
- **GIVEN** the remote is paired with one Apple TV and a second Apple TV is in range
- **WHEN** the user presses keys
- **THEN** only the paired Apple TV reacts

### Requirement: Arrows move the focus
The remote SHALL move the focus up, down, left and right on the Home screen and in Antuna, one step per press, and keep stepping while a key is held.

#### Scenario: Home screen
- **GIVEN** the Apple TV shows the Home screen
- **WHEN** the user presses an arrow key
- **THEN** the focus moves one app in that direction

#### Scenario: Held key
- **GIVEN** Antuna shows the guide
- **WHEN** the user holds the down key for two seconds
- **THEN** the focus keeps moving down until the key is released and stops within one step of release

### Requirement: Select and back
The remote SHALL open the focused item with its select key and go back one screen with its back key, on the Home screen and in Antuna.

#### Scenario: Open and leave an app
- **GIVEN** Antuna is focused on the Home screen
- **WHEN** the user presses select, then back
- **THEN** Antuna opens, and back leaves it the way the Siri Remote's back button does

### Requirement: Play and pause
The remote SHALL pause and resume playback in Antuna with one key, as the Siri Remote's play/pause button does.

#### Scenario: Pausing a movie
- **GIVEN** a movie is playing in Antuna
- **WHEN** the user presses play/pause, then presses it again
- **THEN** the movie pauses, then resumes

### Requirement: Up and down change channel
The remote's up and down keys SHALL change channel in Antuna's full-screen Live the way a swipe on the Siri Remote does, with Antuna's swipe setting on changing channel.

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

### Requirement: Comes back after sleep
The remote SHALL reconnect without pairing again after the Apple TV sleeps, after the remote's battery is removed and put back, and after the remote has been out of range.

#### Scenario: Apple TV was asleep
- **GIVEN** the remote is paired and the Apple TV has been asleep for an hour
- **WHEN** the user wakes the Apple TV with the Siri Remote and presses an arrow on the remote
- **THEN** the focus moves within 2 seconds of the first press

#### Scenario: Battery swap
- **GIVEN** the remote is paired
- **WHEN** its power is removed for 10 seconds and restored
- **THEN** it reconnects on the first key press and that press is not lost

#### Scenario: Waking the Apple TV
- **GIVEN** the Apple TV is asleep
- **WHEN** the user presses a key on the remote
- **THEN** the bench log records whether the Apple TV wakes, since the Siri Remote stays the way to wake it if it does not
