# adr-skills

[中文](README.md)

An architecture decision workflow for software projects: inspect affected code, write an Architecture Decision Record (ADR), obtain an independent review, and implement the accepted decision in verifiable phases. Use the orchestrator for the full workflow or invoke one phase at a time.

## Skills

| Skill | Purpose |
| --- | --- |
| `adr-workflow` | Route the requested stages within the user's authorization. |
| `adr-check` | Inspect affected responsibilities, dependencies, and placement of new behavior. |
| `adr-writing` | Discuss and write the ADR, phase plan, and acceptance contract. |
| `adr-review` | Independently review a proposal and return evidence-based findings. |
| `adr-implementation` | Implement, test, and accept an established ADR in phases. |

The five directories form one suite. **Install all five under the same skills parent directory**: the orchestrator uses the other components, and implementation refers to the review fingerprint rules. Individual phases can be invoked separately, but installing only one directory may leave dependencies missing.

## Installation

### Skills CLI

Run the following from the project where you want to use the suite. Node.js 22.20 or later is required. These commands install to the current project, not globally.

```sh
# List the skills
npx skills add DOIT-Ben/adr-skills --list

# Install the suite for Codex
npx skills add DOIT-Ben/adr-skills --skill '*' --agent codex --copy --yes

# Install the suite for Claude Code
npx skills add DOIT-Ben/adr-skills --skill '*' --agent claude-code --copy --yes
```

To install globally, add `--global` after choosing the target; inspect any existing skills with the same names before updating. Skills CLI is an optional third-party tool; see its [network and telemetry documentation](https://github.com/vercel-labs/skills#telemetry).

### Manual installation

Clone or download this repository and copy all five complete directories from `skills/` into the target agent's skills parent directory, keeping them as siblings. The directory depends on whether installation is personal or project-scoped. Inspect existing directories with the same names before updating. Copy the supporting templates and references as well as each `SKILL.md`.

Start a new session and check that the client discovers the skills. Skill instructions are primarily in Chinese; the model must be able to understand them.

## Usage

```text
Use adr-workflow to inspect the impact of adding text export to this notes app,
write an ADR, and obtain an independent design review. Do not implement code yet.
```

You can also ask `adr-check` to inspect code impact, `adr-writing` to draft a proposal, or `adr-review` to review an existing ADR. To execute an accepted decision, use `adr-implementation` with the ADR, phase plan, and authorized scope.

An independent reviewer can be a person who did not write the proposal or an agent with independent context. If no independent review is available, the proposal remains pending; self-review is not a substitute. Implementation, commits, and publication remain subject to the user's actual authorization.

## Verification and maintenance

With Python 3.9 or later, run this from the repository root:

```sh
python -m unittest discover -s tests -v
python scripts/audit_privacy.py
```

The tests cover skill entry points, references, and the installation layout. The privacy screen checks non-ignored working files and locally reachable Git history and prints categories and locations only. It cannot detect all private information; review the content and history manually before publication. Discovery and behavior still need verification in the target agent.

This repository maintains the distributable version. If you also maintain a personal variant, compare and merge changes deliberately, preserving general behavior and excluding private configuration, machine paths, and personal verification records; rerun the checks after syncing.

## License

[MIT](LICENSE)
