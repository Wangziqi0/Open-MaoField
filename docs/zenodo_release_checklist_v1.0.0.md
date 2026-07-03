# Zenodo Release Checklist for Open-MaoField v1.0.0

Date: 2026-07-03

## Local Repository Gate

- [x] Public repository exists: `https://github.com/Wangziqi0/Open-MaoField`.
- [x] Release metadata exists: `.zenodo.json`.
- [x] Citation metadata exists: `CITATION.cff`.
- [x] License exists: `LICENSE` (`Apache-2.0`).
- [x] Manuscript artifacts exist under `paper/`.
- [x] Exact certificate and deterministic harness artifacts exist.
- [x] Claim boundary is explicit in `README.md` and release notes.
- [x] GitHub-Zenodo integration has been enabled by the repository owner.
- [x] GitHub Release `v1.0.0` has been created after Zenodo integration is enabled.
- [x] Zenodo has archived the release and displayed a DOI.
- [x] The DOI has been copied back into the repository in a post-release metadata patch.

## DOI

Repository/software release DOI:

```text
10.5281/zenodo.21157578
```

Concept DOI:

```text
10.5281/zenodo.21157577
```

This is not a separate Zenodo `Publication -> Preprint` DOI.

## Human Zenodo Steps

1. Sign in to Zenodo with the account intended to own the DOI.
2. Open the profile menu and choose GitHub.
3. Click `Sync now`.
4. Find `Wangziqi0/Open-MaoField` and enable it.
5. Only after the repository is enabled, create the GitHub Release `v1.0.0`.
6. Wait for Zenodo to archive the release and show the DOI.
7. Verify the Zenodo record metadata and license.
8. Report the DOI back to node36 for a post-release metadata update.

## Release Text

Suggested GitHub Release title:

```text
Open-MaoField v1.0.0
```

Suggested GitHub Release body:

```text
Open-MaoField v1.0.0 is the first public sanitized release of the finite
projection-order-defect line from the MaoField research programme.

It contains:
- the V2.5 public manuscript artifact (`paper/preprint.pdf` and TeX source);
- an exact rational 2x2 certificate;
- deterministic regression-harness artifacts;
- explicit claim-boundary and duplicate-risk notes.

Claim boundary: this release does not report a MaoField empirical positive
result, full-panel execution, checkpoint inference, model training, a new
optimization loss, deployed-model residual/interaction/transport/holonomy
observations, a completed broad theory, or any claim that JSON floats or the
deterministic harness prove the theorem.

Duplicate risk remains MEDIUM.
```
