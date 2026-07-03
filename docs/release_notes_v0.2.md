# Open-MaoField v0.2 Public Draft Notes

Date: 2026-07-03

This update adopts the externally compiled V2.5 final synthesis package as the
current public draft manuscript artifacts.

Included in this update:

- `paper/preprint.tex`;
- `paper/preprint.pdf`;
- `paper/render_contact_sheet.png`;
- `docs/source_map_and_changelog_v2_5_20260703.md`.

V2.5 package hashes verified on node36:

```text
848d6a37bd9310578f8efb4991d60f6892528c029fde976aa08133f2640bef59  MAOFIELD_PREPRINT_V2_5_FINAL_SYNTHESIS_20260703.tex
83b21463351d578e2a22b4785c9fe97e34e9ab4006e77d153895860933ddddde  MAOFIELD_PREPRINT_V2_5_FINAL_SYNTHESIS_20260703.pdf
97759a9e576d7dfb6852acd42a10648dc513751cefb565aee12c2fc5830f46ab  render_contact_sheet.png
```

The V2.5 PDF was reported by its synthesis package as compiled with `pdflatex`
and visually rendered to eight PNG pages. Node36 verified the package hashes and
performed PDF metadata/text scans. Node36 did not have a local LaTeX toolchain
at the time of adoption, so this repository must keep the TeX/PDF pair together
unless a later environment recompiles them.

This update does not create a GitHub Release, Zenodo DOI, arXiv submission,
journal submission, peer-review status, or empirical MaoField positive claim.
The current duplicate-risk level remains `MEDIUM`.
