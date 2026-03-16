# Contributing to TerraSensus

## Workflow

1. Pick an issue from [GitHub Projects](../../projects) or create one
2. Create a branch: `git checkout -b feat/your-feature` or `fix/your-bug`
3. Write tests first (TDD where possible)
4. Implement the change
5. Run CI locally before pushing:
   ```bash
   # Python services
   ruff check services/your-service && pytest services/your-service/tests

   # TypeScript
   cd mobile && npx tsc --noEmit && npm test -- --watchAll=false
   ```
6. Open a PR using the PR template — fill in all sections

## Logging decisions and mistakes

- **New architectural decision?** → Add an ADR to `docs/ADR/`
- **Found a bug or unexpected behaviour?** → Add an entry to `docs/lessons-learned.md`
- **New engineering insight?** → Add to the relevant file in `docs/engineering-notes/`

## Sensor thresholds

All alert thresholds are defined in `services/alert-engine/rules.py` and mirrored in `CLAUDE.md`. Do not change these values without agronomic justification and updating both files.

## AI prompts

Prompts live in `services/ai-recommendations/prompts/`. Changes require a review pass against known soil profiles before merging.

## Branching

- `main` → staging auto-deploy
- `production` → manual deploy only
- Feature branches: `feat/`, `fix/`, `infra/`, `docs/`

## Claude Code sessions

At the end of each development session, run `/revise-claude-md` to update `CLAUDE.md` with any new learnings.
