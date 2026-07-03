# Open-MaoField v0.1 Public Draft Notes

Date: 2026-07-03

This public draft seed contains:

- a sanitized `paper/preprint.tex` source;
- the exact rational 2x2 witness script and JSON certificate;
- the deterministic floating-point harness and JSON output;
- claim-boundary and duplicate-risk notes;
- a minimal public README, citation metadata and hash manifest.

It intentionally excludes:

- private MaoField git history;
- canonical `STATE.md`;
- RAG indexes;
- personal or operational handoff files;
- model checkpoints or weights;
- raw experiment datasets;
- old empirical pilot logs;
- any public claim of a positive empirical finding from MaoField.

Known limitations:

- a compiled V2.4 PDF is not included in this seed because the node36
  environment used for the sanitized export did not have a LaTeX toolchain.
- rerunning the deterministic harness may produce a different JSON hash because
  runtime metadata such as UTC timestamp, Python version, NumPy version and
  platform are recorded. The mathematical claims are not carried by JSON hashes
  or floating-point values.
