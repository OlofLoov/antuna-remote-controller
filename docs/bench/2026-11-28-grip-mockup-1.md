# Grip mock-up 1, printed

What was tested: the first grip mock-up, `hardware/enclosure/mockup.py`
at commit 1f563c3, printed by the owner on a Bambu Lab P1S. No board, no
firmware, no Apple TV.

## form-factor/balanced-in-the-hand

Done: the owner held the printed mock-up.

Seen: not comfortable, "quite the opposite". The shape was a 6 mm slab
with 2 mm edges, a step up to 13.5 mm at the cells and a step up to the
head. The owner named a Samsung-style TV remote as a grip they like: a
rounded back that grows thicker toward the hand, with no steps.

Result: fail.

## form-factor/prints-at-home

Done: the owner printed both parts.

Seen: two solid parts with no way to join them but glue, and no battery
door. The requirement asks for screws or clips and no glue.

Result: fail. The mock-up was drawn as a shape to hold, not as a shell.

## What changed

`openspec/changes/define-keys-and-layout/design.md`, decisions 2, 10 and
11: a back that swells into the palm with 6 mm edges, and a hollow shell
in three parts with screws and a battery door.
