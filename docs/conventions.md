# Conventions

## Citations

A requirement's slug is its name lowercased, with each run of other
characters turned into one hyphen. A test or bench log that proves a
requirement names it as `<capability>/<requirement-slug>`. A requirement in
the app repo is cited as `antenna:<capability>/<requirement-slug>`;
`scripts/check-spec-refs.sh` checks only the citations without a prefix.

## Bench logs

One file per session in `docs/bench/`, named `YYYY-MM-DD-<topic>.md`. It
starts with what was tested: the board (dev board name or PCB revision),
the firmware commit, the Apple TV model and tvOS version, and the Antuna
build. Then one section per requirement, headed by its citation, with what
was done, what was seen and pass or fail. A failed result stays in the log.

## Datasheets

Every vendor document a design check reads has a row in
`docs/datasheets/manifest.tsv`, with its revision and sha256 once read.
A value taken from one cites it by part and revision. The PDFs are not
committed; `scripts/fetch-datasheets.sh` gets them. Rules:
`docs/datasheets/README.md`.

## PCB

- Board revisions are letters: rev A, rev B. The revision is printed on
  the silkscreen and named in the change's `design.md`.
- A board revision is tagged `pcb-rev-<letter>` on the commit whose outputs
  were sent to the fab.
- ERC and DRC run clean with `kicad-cli`. A waived violation is excluded in
  the KiCad project with a comment that says why.

## Enclosure

- Parameters come from the PCB placement export and from one parameter file.
  A dimension typed twice is a bug.
- Fit checks are tests: the board fits with its stated clearance, each
  button cap sits over its switch, nothing crosses the radio keep-out.

## Commits

Conventional Commits: `type(scope): subject`, at most 72 characters, no
trailing period. Types: feat, fix, docs, refactor, test, build, ci, chore,
perf, style, revert. Scopes: pcb, enclosure, firmware, spec, ci, build, docs.
