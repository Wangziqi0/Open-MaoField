# Open-MaoField

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21157578.svg)](https://doi.org/10.5281/zenodo.21157578)

Open-MaoField is the public, sanitized research surface of the MaoField
programme. Its long-term target is one of the lowest-level mathematical
problems behind black-box LLM evaluation: after scalar metrics, main effects,
decoding artifacts, smoothing trends, judge protocols, aggregation weights and
coordinate choices are stripped away, is there any stable non-scalar structure
left to study?

The current public object is deliberately narrow. It studies finite positive
weighted two-way tables as residual metric audit objects, proves when centered
main-effect subspaces are orthogonal, identifies projection order defects under
non-product weights, and gives an exact rational 2x2 certificate. The point is
not to claim that language-model internals have been solved. The point is to
build a clean finite-dimensional starting point where failures of scalarization,
nuisance removal and sequential residualization can be stated, checked and
reproduced without empirical overreach.

In short:

> A finite-dimensional mathematical starting point for black-box LLM
> evaluation: what survives after scalar metrics, nuisance effects and
> coordinate artifacts are stripped away?

## Current Public Object

The current note is:

```text
Finite Projection Order Defects in Residual Metric Audits:
A Mathematical Starting Point for Black-Box Evaluation
```

Author:

```text
Yifan Chen
```

Current synthesis package:

```text
v1.0.0 release candidate from the V2.5 final synthesis public draft
paper/preprint.tex
paper/preprint.pdf
```

Core finite setup:

- finite non-empty sets `Q` and `B`;
- a positive normalized weight table `w(q,b)` on `Q x B`;
- the weighted Hilbert space `L^2(w)`;
- constant subspace `C`;
- centered row-main-effect subspace `A`;
- centered column-main-effect subspace `B_0`;
- additive nuisance space `N_add = C + A + B_0`;
- ordered stripping maps `R_{Q->B}` and `R_{B->Q}`.

Main bounded claims:

- product weights are equivalent to `A` being orthogonal to `B_0`;
- product weights are equivalent to order-independence of the two ordered
  stripping maps;
- under non-product weights, there is an existential pure-main-effect witness
  whose true additive residual is zero while one wrong-order sequential output
  is nonzero;
- an exact 2x2 rational certificate has squared weighted norm `61/177408`.

## What This Repository Does Not Claim

This repository does not report any positive empirical finding from MaoField.
It does not report model-fitting runs, checkpoint-based inference, a newly
authorized optimization objective, full-panel execution, F3/LOSO success,
deployed-model residual-field measurements, or a completed broad theory of
ANOVA, dependent-input decomposition, projection products, model collapse or
interpretability.

The deterministic floating-point harness is regression support only:

```text
The floating-point harness is deterministic regression support only; the mathematical claims are carried by the analytic proof and exact rational certificate, not by JSON floats.
```

## Repository Layout

```text
paper/
  preprint.tex
  preprint.pdf
  render_contact_sheet.png

certificate/
  exact_witness_certificate.py
  exact_witness_v1_4_20260629.json

harness/
  deterministic_harness.py
  synthetic_harness_v1_3_20260628.json

docs/
  claim_boundary_note.md
  duplicate_risk_note.md
  release_notes_v0.1.md
  release_notes_v0.2.md
  release_notes_v1.0.0.md
  zenodo_release_checklist_v1.0.0.md
  source_map_and_changelog_v2_5_20260703.md
```

## Reproduce The Exact Certificate

The exact witness uses Python standard-library rational arithmetic:

```bash
python3 certificate/exact_witness_certificate.py --out-dir /tmp/open-maofield-exact
```

Expected terminal summary:

```text
all_checks_passed=True
```

The displayed witness uses

```text
w = (1/11) * [[1, 2], [3, 5]]
K = [7/11, -4/11, 7/11, -4/11]
R_{B->Q} K = 0
R_{Q->B} K = [1/32, 5/168, -1/96, -1/84]
||R_{Q->B} K||_w^2 = 61/177408
```

## Run The Deterministic Harness

The harness uses NumPy and is intended only as deterministic regression support:

```bash
python3 harness/deterministic_harness.py \
  --out /tmp/open-maofield-harness/synthetic_harness_v1_3_20260628.json \
  --summary-md /tmp/open-maofield-harness/SYNTHETIC_HARNESS_V1_3_20260628.md
```

Expected result:

```text
all_synthetic_controls_passed = true
```

## Release Status

This repository is a public sanitized release surface. The private MaoField
canonical repository and its historical research state are not mirrored here.
The duplicate-risk level is currently `MEDIUM`: public descriptions must not
claim that no close prior work exists.

The V2.5 PDF is included as the v1.0.0 public manuscript artifact. The GitHub /
Zenodo repository release DOI is:

```text
10.5281/zenodo.21157578
```

The Zenodo concept DOI is:

```text
10.5281/zenodo.21157577
```

This DOI identifies the archived repository/software release. It is not a
separate Zenodo `Publication -> Preprint` DOI. No arXiv submission, journal
submission or peer-review status is claimed by this repository.

## License

The repository currently uses the Apache License 2.0. See `LICENSE`.
