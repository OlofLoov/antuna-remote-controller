# Antuna Remote

A physical remote for Apple TV, built around the Antuna app: clicky
buttons for up, down, left, right, select, back and play/pause, where up
and down change channel while live TV plays. No number pad. This repo holds
the PCB, the enclosure and the firmware. The app lives in a separate,
private repo named antenna.

Antuna Remote is the name people see. The repo is
github.com/OlofLoov/antuna-remote-controller and is public: nothing from the
private app repo beyond its specs' requirement names goes in here.

## Commands

```sh
openspec validate --all --strict           # specs and changes; npm install -g @fission-ai/openspec@1.16.0
scripts/check-spec-refs.sh                 # every cited requirement exists in openspec/specs or an active change
scripts/fast-checks.sh                     # what the pre-push hook runs
shellcheck scripts/*.sh scripts/githooks/* .claude/hooks/*.sh
actionlint
kicad-cli sch erc --severity-error --exit-code-violations hardware/pcb/antuna-remote/antuna-remote.kicad_sch   # KiCad 10.0.8
kicad-cli sch export netlist -o /tmp/antuna.net hardware/pcb/antuna-remote/antuna-remote.kicad_sch            # nets to review against design.md
scripts/fetch-3d-models.sh                 # STEP models for the library parts, kept out of git
scripts/fetch-datasheets.sh                # vendor PDFs from docs/datasheets/manifest.tsv, kept out of git
```

On macOS `kicad-cli` is `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`.
The enclosure and firmware commands land with the changes that create
those folders. Each such change adds its commands here.

Run `scripts/setup.sh` once per clone. It points git at `scripts/githooks`
(commit lint, no commits on main, fast checks before each push).

## Layout

- `openspec/` specs and changes, as in the app repo.
- `hardware/pcb/` the KiCad project (`antuna-remote/`) and the repo-local
  library (`lib/`) of parts checked against their datasheets. KiCad files
  are text and are reviewed as diffs. Fabrication outputs (Gerbers, drill, BOM, placement) are built
  by `kicad-cli`, never committed by hand.
- `hardware/enclosure/` the enclosure as code. STEP, STL and 3MF are build
  outputs.
- `firmware/` the remote's firmware.
- `tools/` bench helpers that never ship.
- `docs/research/` research reports behind decisions, with their sources.
- `docs/datasheets/` the manifest of every vendor document the design
  relies on (source, revision, sha256). The PDFs stay local in `files/`.
- `docs/bench/` bench test logs: what was measured on real hardware, with
  the board revision, date, tvOS version and the requirements it covers.

## How we work

- **Specs and changes are OpenSpec.** `openspec/specs/<capability>/spec.md`
  says what the remote does today, with WHEN/THEN scenarios a person holding
  the remote, or a bench test, can observe. New work is a change in
  `openspec/changes/<name>/` with `proposal.md`, delta specs, `design.md`
  and `tasks.md`. Start with `/opsx:propose` (or `/opsx:explore`), build
  with `/opsx:apply`, check with `/opsx:verify`, fold in with
  `/opsx:archive` in the last PR. No schematic, layout, enclosure or
  firmware work without a change.
- **Decisions live in design.md.** Parts, the radio module, the battery,
  the fab and its rules, the link to Apple TV: each is decided in a
  change's `design.md` with the options considered. Parts carry the
  manufacturer part number, a datasheet link and one alternate. Each
  datasheet the design reads gets a row in `docs/datasheets/manifest.tsv`.
- **One placement source.** Button, LED and connector positions come from
  the PCB. The enclosure reads them from the `kicad-cli` placement export
  and never copies coordinates by hand.
- **Prove before you route.** Anything about Apple TV behavior is proven on
  a dev board and logged in `docs/bench/` before a PCB depends on it.
- **The app side is the app repo's.** When a key needs new behavior in
  Antuna, that is a change in the antenna repo. A change here names it in
  its proposal's Impact and cites app requirements as
  `antenna:<capability>/<requirement-slug>`.
- **Tests and bench logs cite requirements** as
  `<capability>/<requirement-slug>`. `scripts/check-spec-refs.sh` fails CI
  when a cited requirement does not exist.
- **Everything ends in a PR.** Never commit on main or push to main. Hooks
  refuse both.
- **Conventional Commits**, enforced by the commit-msg hook and in CI.
  Scopes: pcb, enclosure, firmware, spec, ci, build, docs.
- **No AI slop.** Every doc, spec, change, commit message and PR body goes
  through the `no-ai-slop` skill.
- Conventions: `docs/conventions.md`.

## Hard constraints

- Works with an unmodified Apple TV 4K on tvOS 26 or later. No dongle, no
  receiver box, no app on the TV other than Antuna.
- Standard links only: infrared with Apple's remote codes, and Bluetooth
  LE HID over GATT. No MFi claims, no Apple trademarks, no Siri Remote
  look-alike.
- A button press acts once on the Apple TV, whichever link carries it.
- The radio is a pre-certified module with the vendor's reference antenna
  layout and keep-out. No custom RF design.
- Every key sends a code that tvOS handles or that an Antuna spec names.
  A key with no defined behavior does not ship.
- Apple-style key set: no number pad. Channels change with up and down,
  the way Antuna already does on a Siri Remote swipe.
- The remote holds no secrets and stores no viewing data.
