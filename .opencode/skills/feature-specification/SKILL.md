---
name: feature-specification
description: Guide for creating feature specifications. Use this when asked to create the specs of a feature.
---

Read the files in SPECS/, these are the project's constitution. Then create a feature specification for the most natural next step according to the ROADMAP.md file. Make a branch, ask me about the feature spec.

Create:

- A new directory YYYY-MM-DD-feature-name under SPECS/ for this feature work
- In there:
    * plan.md as a series of numbered task groups (remind yourself to use the project's actual scripts/commands documented in README and `scripts/` when running checks, tests, or pipeline steps)
    * requirements.md for the scope, decisions, context
    * validation.md for how to know that the validation succeeded and can be merged

    
# Requirements

* All features must include comprehensive logging, privileging decorator-type designs to avoid mixing business logic with logging logic.
* Privilege proper schemas as much as possible over relying on regexes
* Do not assume backward compatibility should be kept, as that could cause legacy code to be kept unnecessarily; ask user in each specific instance where a decision must be made about backward compatibility
* Privilege solutions that are simple, elegant and general; complexity and arbitrariness should be minimised. Feel free to propose the user ways to make the specification simpler and more elegant

# Root cause, category & prevention (bug-fixing specs)

When a spec fixes a bug (or a set of related bugs), it must go beyond the reported symptom. **Invoke the `investigate-bug` skill** — it is the canonical protocol for RCA and category sweeps. This section is a summary; the skill is the source of truth.

* **Investigate the root cause** (Horizon 0) — why the failure happens (data shape, type mismatch, missing guard, false assumption), with evidence.
* **Fix the category, not the instance** (Horizons 1 & 2) — sweep narrow blast radius and then the entire codebase for siblings sharing the same root cause; fix every instance found.
* **Prevent recurrence** — include at least one general, mechanism-level guard appropriate to this repo (e.g. typed validation/contract, fail-loud invariant, deterministic derivation, or a check script wired into the project's workflow) so the class cannot silently recur.
* **Lock the category in with tests** — cover instance + siblings, plus a test/check that the prevention actually fires where applicable.
* **Name the category** — stable name (e.g. "silently empty query results", "misaligned verse mapping", "untrusted input used as identity key") matching `investigate-bug`.

The spec's `plan.md` must include the sweeps as explicit tasks; a spec that only patches the reported call site is rejected. When unsure whether two findings are the same class, ask the user.

# Contracts against arbitrary inputs & outputs

* Treat external boundaries (raw CSV/TSV/SQL inputs, OCR results, SQLite rows, file paths, API/model responses, and any user-provided data) as **untrusted and arbitrary**: they can arrive malformed, mis-typed, partial, or surprising.
* Boundary crossings should be validated by clear, explicit contracts (typed structures/schemas where appropriate) — parse/validate at the edge, then work with well-defined values internally. Avoid passing around ambiguous raw data when a structured representation is practical.
* Prefer explicit schemas/structured parsing over brittle defensive string/regex heuristics when structure and types matter.
* Where a field's meaning matters (IDs, references, book/chapter/verse keys, stage markers), model it explicitly and keep value types consistent across reads/writes.
* Specs should define these contracts explicitly: the input/output shapes, validation rules, and failure behaviour (fail loud vs degrade) for malformed or unexpected data.

# YAGNI (You Aren't Gonna Need It)

* Spec only what is needed **now**. Do not include hypothetical future features, speculative abstractions, or flexibility that no current requirement demands.
* If a requirement can be met with a simpler, more general solution, prefer it. Complexity must be earned, not anticipated.
* Cut scope by default: when unsure whether something belongs in the spec, leave it out and ask the user.
* Do not add config toggles, extension points, or extra fields "just in case".

# Planning strategy

This is a Red/Green TDD repo, so tests must be created *before* feature code and tested against it until they pass.

# Validation

The validation step also includes surfacing differences between what was implemented and the specs in SPECS/ and the feature specs, and updating the specs upon user's approval.

# Important

* You *must* ask the user for clarifications before writing to disk. 


