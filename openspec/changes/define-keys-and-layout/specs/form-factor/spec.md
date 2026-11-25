## ADDED Requirements

### Requirement: Slim stick size
The remote SHALL be a stick 40 mm wide (plus or minus 2 mm), 145 to 155 mm long and no more than 20 mm thick at its thickest point, and SHALL weigh no more than 90 g with its batteries in.

#### Scenario: Caliper and scale
- **GIVEN** a finished remote with two AAA cells
- **WHEN** it is measured with a caliper and weighed
- **THEN** each measure is inside the stated range

### Requirement: Balanced in the hand
The remote SHALL carry its batteries at the bottom end, so it rests in the palm with the weight low and the thumb over the d-pad.

#### Scenario: Picking it up
- **GIVEN** the remote lies on a table
- **WHEN** a user picks it up and holds it to watch TV
- **THEN** their thumb rests on or next to the d-pad without shifting grip

### Requirement: Thumb reaches the viewing keys
With the remote held at its bottom end, an adult thumb SHALL reach the d-pad, select, back, Home, play/pause, volume and mute without shifting grip. Power may need a shift.

#### Scenario: Three hands
- **GIVEN** three adults with small, medium and large hands
- **WHEN** each holds the remote at its bottom end and presses each viewing key in turn
- **THEN** none of them shifts their grip

### Requirement: Not a Siri Remote
The remote SHALL not look like an Apple Siri Remote: no clickpad or touch surface, no aluminum finish, no Apple logo or wording, and a shape that differs in width, thickness or profile at a glance.

#### Scenario: Side by side
- **GIVEN** the remote and a Siri Remote on a table
- **WHEN** someone who has not seen the remote before is asked which one is Apple's
- **THEN** they pick the Siri Remote without hesitating

### Requirement: Battery door without tools
The user SHALL be able to open the battery door, change both cells and close it again without tools, in under 30 seconds, and the cells SHALL fit only one way round or come to no harm the wrong way round.

#### Scenario: Changing batteries
- **GIVEN** a remote with flat batteries and two new AAA cells
- **WHEN** the user opens the door, swaps the cells and closes it
- **THEN** it takes under 30 seconds and the remote works

### Requirement: Survives the floor
The remote SHALL work after ten drops from 1 m onto a wooden floor, on any face, with the battery door still shut and every key still clicking.

#### Scenario: Drop test
- **GIVEN** a working remote
- **WHEN** it is dropped ten times from 1 m onto a wooden floor, landing on different faces
- **THEN** the door is shut, no part has come off and every key works

### Requirement: Prints at home
The enclosure SHALL print on a common home FDM printer with a 0.4 mm nozzle and a 180 mm by 180 mm bed, in PETG or PLA, with no supports on any outside face, and SHALL assemble with screws or clips and no glue.

#### Scenario: Printing a shell
- **GIVEN** the enclosure's print files and a home FDM printer
- **WHEN** the parts are printed with the stated settings and put together
- **THEN** the outside faces show no support marks and the remote closes without glue
