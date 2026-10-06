# Signal

*by Daniel Avissar*

For clear, concise, and easy-to-scan writing.

A style guide for UX writing, technical writing, and knowledge management work. See [SIGNAL.md](./SIGNAL.md) for the full guide.

## Rules pack

The file [`signal.rules.toml`](./signal.rules.toml) is the machine-readable companion to SIGNAL.md. It lists every rule with an ID, a severity, a one-line summary, and the SIGNAL.md section it comes from. It also holds the structural requirements for each document type in section 10.

- **Deterministic rules** – A rule with a `check` names a mechanical test, such as a sentence cap, with its thresholds.
- **Judgment rules** – A rule without a `check` needs a person or a model to apply it.
- **Per-type changes** – A `by_type` table changes a rule for one document type, such as the 12-word cap for UX microcopy.

The PAKT documentation toolkit reads this pack, together with SIGNAL.md, to review and audit docs against Signal. SIGNAL.md stays the source of truth. The pack only points into it.

## Contributing

When you change SIGNAL.md, update `signal.rules.toml` in the same pull request:

1. Add, change, or remove the rules that the edit affects. Cite the section heading or bold lead-in exactly as SIGNAL.md writes it.
2. Set `version` in the `[guide]` table to the new "Last revision" date, in `YYYY-MM-DD` form.
3. Run `python scripts/check_rules_pack.py`. The same check runs in CI on every pull request. It fails on a citation to a missing section, or on a version that differs from the revision date.
