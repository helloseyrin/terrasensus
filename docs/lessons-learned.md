# TerraSensus — Lessons Learned

A running log of mistakes, unexpected behaviour, and what was done to fix them. Updated during development sessions.

---

## Format

```
### [YYYY-MM-DD] Brief title
**Service/Component:** which service was affected
**What happened:** description of the problem
**Root cause:** why it happened
**Fix:** what was done
**Takeaway:** what to remember for next time
```

---

<!-- Claude: append new entries below this line during development sessions -->

---

### [2026-03-16] GitHub Actions workflow injection blocked by pre-write hook
**Service/Component:** `.github/workflows/deploy-staging.yml`
**What happened:** Write tool was blocked by a `PreToolUse:Write` security hook when the workflow file contained `${{ github.sha }}` inline in a `run:` command.
**Root cause:** Interpolating GitHub context expressions (`${{ }}`) directly into shell commands is a known injection vector — an attacker controlling a branch name or PR title could inject arbitrary shell. The hook correctly flagged it.
**Fix:** Moved all `${{ github.sha }}` references into an `env:` block at the job level, then referenced `$IMAGE_TAG` (the env var) inside `run:` commands. The shell never sees a raw GitHub expression.
**Takeaway:** Never put `${{ github.* }}` or `${{ env.* }}` directly inside `run:` blocks. Always intermediate through an `env:` key. This applies to all GitHub Actions workflows, not just deploy pipelines.

---

### [2026-03-16] Sensor ranges in README were wrong for 5 of 7 sensors
**Service/Component:** `README.md`, `simulator/config.yaml`
**What happened:** README sensor table listed ranges that didn't match the actual simulator config — e.g. pH listed as 4.5–8.5 (config: 3.5–9.5), N listed as 0–200 (config: 0–250), EC listed as 0–4 (config: 0–6).
**Root cause:** The README was written before `config.yaml` was finalised. The two diverged silently — there's no automated check that keeps them in sync.
**Fix:** Cross-referenced every sensor row in the README against `config.yaml` min/max values and corrected all five.
**Takeaway:** When a document and a config file describe the same values, the config is the source of truth. If you update config.yaml, update README. Consider adding a CI test that parses config.yaml and checks against a schema — at minimum, a comment in the README directing readers to config.yaml as authoritative.

---

### [2026-03-16] Missing Terraform files referenced in README
**Service/Component:** `infra/`, `README.md`
**What happened:** README project structure listed `infra/bigquery.tf` and `infra/cloud_run.tf` but neither file existed in the repo.
**Root cause:** Repo skeleton was outlined in docs before all files were created. These two were noted as "to do" but slipped through without being created.
**Fix:** Created both files during a sanity-check pass.
**Takeaway:** When doing a repo skeleton pass, diff the listed structure in README against actual `find infra/ -name "*.tf"` output. Empty directories and missing files are silent — they don't cause CI failures, so they survive indefinitely unless explicitly checked.

---

### [2026-03-16] alert-engine tests couldn't import rules module
**Service/Component:** `services/alert-engine/tests/test_rules.py`
**What happened:** `pytest tests/` from the alert-engine directory failed with `ModuleNotFoundError: No module named 'rules'`.
**Root cause:** Python's module resolution looks from the working directory. Running pytest from inside `services/alert-engine/` doesn't add the parent to `sys.path`, so `from rules import evaluate` fails.
**Fix:** Added `sys.path.insert(0, str(Path(__file__).parent.parent))` at the top of the test file.
**Takeaway:** FastAPI services use implicit relative imports in development but tests run from a different working directory. Always add an explicit `sys.path` insert in test files for services, or use `pytest.ini` / `pyproject.toml` with `pythonpath = .` to set it project-wide.

---

### [2026-03-16] logged_at vs created_at — ROI cross-referencing failure mode identified
**Service/Component:** `shared/types/activity_log.ts`, Cloud SQL schema (planned)
**What happened:** During data model design, discovered that storing only a single timestamp on activity logs would silently corrupt ROI calculations. If a farmer logs Monday's fertiliser application on Wednesday, and the system cross-references Wednesday's soil readings (created_at), the pre-fertiliser baseline is lost — the ROI calculation uses post-application readings as the "before" state.
**Root cause:** Standard created_at timestamp pattern assumes event-time ≈ record-time, which is false in agriculture. Farmers log events after the fact, especially for manual applications.
**Fix:** Added both `logged_at` (when the event occurred) and `created_at` (when the record was entered) to all activity log types. ROI queries must always use `logged_at` to find the corresponding soil readings.
**Takeaway:** Any domain where humans record physical events after the fact (agriculture, construction, medical) requires this distinction. It's a design decision that must be made at schema design time — retrofitting it onto a live database with existing records is painful. Learned this from farmOS's design, which has maintained this separation for 15 years.

---

### [2026-03-16] Multi-model fallback rationale — "most data centres" is wrong metric
**Service/Component:** `services/ai-recommendations/client.py`, ADR 006
**What happened:** During AI model selection, initial reasoning pointed to number of data centres as the primary availability metric. This is the wrong metric.
**Root cause:** Data centre count is a marketing number, not an SLA. What matters for a food-security application is: (a) whether the fallback runs on genuinely separate infrastructure from the primary, (b) whether a single regional GCP incident can affect both primary and fallback, and (c) whether the fallback can handle correctness failures (wrong values), not just availability failures.
**Fix:** Decision reframed around two failure modes — availability failure (API down) and correctness failure (API returns bad values). Architecture: Gemini primary (GCP IAM, native), Claude fallback (Anthropic/AWS — separate infrastructure), rule-based local (no network). Bounds checker (`check_bounds()`) handles correctness failures by triggering fallback when numeric values exceed agronomic limits. See ADR 006.
**Takeaway:** For resilience design, ask "what happens when each failure mode occurs?" not "who has more data centres?" Two-provider strategy is only meaningful if the providers run on separate cloud infrastructure.

### [2026-03-17] Terraform role and when to use it
**Service/Component:** `infra/` (Terraform files)
**What happened:** Terraform was listed in the stack but its purpose and timing were unclear — it had never been explicitly discussed and wasn't mentioned in the README workflow.
**Root cause:** Terraform was written alongside the app code (good practice) but never explained in the docs. The `infra/` directory exists with `.tf` files for Cloud SQL, Cloud Run, BigQuery, Pub/Sub, and GCS, but no doc explained when or why to run it.
**Fix/Decision:** Terraform is Phase 4 tooling — run `terraform apply` once when deploying to GCP for real. Until then everything runs locally via `docker-compose`. The MVP0 checklist (`docs/mvp0-checklist.md`) now lists Terraform as the first infrastructure step.
**Takeaway:** Any tool in the stack that isn't part of the local dev loop needs a sentence in the README or docs explaining when it enters the picture.
