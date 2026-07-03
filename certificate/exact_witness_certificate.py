#!/usr/bin/env python3
"""Exact rational v1.4 witness certificate for the finite order-defect note.

This script is synthetic-only. It uses fractions.Fraction to verify the 2x2
v1.3 order-defect witness without floating point arithmetic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from fractions import Fraction
from pathlib import Path


def matmul(a, b):
    rows = len(a)
    cols = len(b[0])
    inner = len(b)
    return [
        [sum(a[i][k] * b[k][j] for k in range(inner)) for j in range(cols)]
        for i in range(rows)
    ]


def matvec(a, v):
    return [sum(row[j] * v[j] for j in range(len(v))) for row in a]


def transpose(a):
    return [list(row) for row in zip(*a)]


def eye(n):
    return [[Fraction(int(i == j), 1) for j in range(n)] for i in range(n)]


def mat_sub(a, b):
    return [
        [a[i][j] - b[i][j] for j in range(len(a[0]))]
        for i in range(len(a))
    ]


def vec_sub(a, b):
    return [a[i] - b[i] for i in range(len(a))]


def inverse(a):
    n = len(a)
    aug = [list(a[i]) + eye(n)[i] for i in range(n)]
    for col in range(n):
        pivot = None
        for row in range(col, n):
            if aug[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            raise ValueError("singular matrix")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [x / scale for x in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            if factor:
                aug[row] = [
                    aug[row][j] - factor * aug[col][j]
                    for j in range(2 * n)
                ]
    return [row[n:] for row in aug]


def projection_matrix(basis, weights):
    """Weighted orthogonal projection onto span(basis)."""
    n = len(weights)
    k = len(basis)
    gram = [
        [sum(weights[r] * basis[i][r] * basis[j][r] for r in range(n)) for j in range(k)]
        for i in range(k)
    ]
    gram_inv = inverse(gram)
    proj = [[Fraction(0, 1) for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            proj[r][c] = sum(
                basis[i][r] * gram_inv[i][j] * basis[j][c] * weights[c]
                for i in range(k)
                for j in range(k)
            )
    return proj


def norm_sq(v, weights):
    return sum(weights[i] * v[i] * v[i] for i in range(len(v)))


def frac_s(x):
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def vec_s(v):
    return [frac_s(x) for x in v]


def mat_s(a):
    return [vec_s(row) for row in a]


def all_zero(v):
    return all(x == 0 for x in v)


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_certificate():
    weights = [Fraction(1, 11), Fraction(2, 11), Fraction(3, 11), Fraction(5, 11)]
    one = [Fraction(1, 1)] * 4
    a_basis = [Fraction(8, 1), Fraction(8, 1), Fraction(-3, 1), Fraction(-3, 1)]
    b_basis = [Fraction(7, 1), Fraction(-4, 1), Fraction(7, 1), Fraction(-4, 1)]

    p_c = projection_matrix([one], weights)
    p_a = projection_matrix([a_basis], weights)
    p_b0 = projection_matrix([b_basis], weights)
    p_n = projection_matrix([one, a_basis, b_basis], weights)
    ident = eye(4)

    r_q_then_b = matmul(mat_sub(ident, p_b0), matmul(mat_sub(ident, p_a), mat_sub(ident, p_c)))
    r_b_then_q = matmul(mat_sub(ident, p_a), matmul(mat_sub(ident, p_b0), mat_sub(ident, p_c)))
    d_w = mat_sub(r_q_then_b, r_b_then_q)
    commutator = mat_sub(matmul(p_b0, p_a), matmul(p_a, p_b0))

    k_b = [Fraction(7, 11), Fraction(-4, 11), Fraction(7, 11), Fraction(-4, 11)]
    k_a = [Fraction(8, 11), Fraction(8, 11), Fraction(-3, 11), Fraction(-3, 11)]
    expected_b = [Fraction(1, 32), Fraction(5, 168), Fraction(-1, 96), Fraction(-1, 84)]
    expected_a = [Fraction(1, 42), Fraction(-1, 84), Fraction(5, 224), Fraction(-3, 224)]

    true_add_b = matvec(mat_sub(ident, p_n), k_b)
    zero_order_b = matvec(r_b_then_q, k_b)
    artifact_b = matvec(r_q_then_b, k_b)
    true_add_a = matvec(mat_sub(ident, p_n), k_a)
    zero_order_a = matvec(r_q_then_b, k_a)
    artifact_a = matvec(r_b_then_q, k_a)

    checks = {
        "main_b0_true_additive_residual_zero": all_zero(true_add_b),
        "main_b0_zero_order_residual_zero": all_zero(zero_order_b),
        "main_b0_artifact_vector_exact": artifact_b == expected_b,
        "main_b0_artifact_norm_sq_exact": norm_sq(artifact_b, weights) == Fraction(61, 177408),
        "symmetric_a_true_additive_residual_zero": all_zero(true_add_a),
        "symmetric_a_zero_order_residual_zero": all_zero(zero_order_a),
        "symmetric_a_artifact_vector_exact": artifact_a == expected_a,
        "order_defect_equals_commutator_exact": d_w == commutator,
        "order_defect_nonzero": any(x != 0 for row in d_w for x in row),
    }

    return {
        "artifact": "exact_witness_v1_4_20260629",
        "date": "2026-06-29 CST",
        "status": "synthetic_only_exact_fraction_certificate",
        "evidence_boundary": {
            "strongest_allowed_verdict": "definitions_and_harness_viable_only",
            "mode_b_maofield_status": "insufficient_artifact",
            "not_authorized": [
                "full_panel",
                "checkpoint_loading",
                "model_inference",
                "training",
                "new_loss",
                "observed_residual_field",
                "observed_interaction_field",
                "glass_box_broken",
                "completed_formal_system",
            ],
        },
        "weights_row_major": vec_s(weights),
        "basis": {
            "C": vec_s(one),
            "A": vec_s(a_basis),
            "B0": vec_s(b_basis),
        },
        "checks": checks,
        "all_checks_passed": all(checks.values()),
        "main_b0_witness": {
            "K": vec_s(k_b),
            "true_additive_residual": vec_s(true_add_b),
            "zero_order_residual_R_B_then_Q": vec_s(zero_order_b),
            "artifact_R_Q_then_B": vec_s(artifact_b),
            "artifact_weighted_norm_squared": frac_s(norm_sq(artifact_b, weights)),
        },
        "symmetric_a_witness": {
            "K": vec_s(k_a),
            "true_additive_residual": vec_s(true_add_a),
            "zero_order_residual_R_Q_then_B": vec_s(zero_order_a),
            "artifact_R_B_then_Q": vec_s(artifact_a),
        },
        "projection_matrices_row_major": {
            "P_C": mat_s(p_c),
            "P_A": mat_s(p_a),
            "P_B0": mat_s(p_b0),
            "P_N": mat_s(p_n),
            "D_w": mat_s(d_w),
        },
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "arithmetic": "fractions.Fraction",
            "random_draws": 0,
        },
    }


def write_markdown(certificate, path, json_name, json_sha):
    lines = [
        "# Exact Witness Certificate v1.4 -- Order Defect",
        "",
        "Date: 2026-06-29 CST",
        "",
        "Status: synthetic-only exact rational certificate for the v1.3",
        "finite weighted order-defect note. This is not a MaoField empirical",
        "result and is not a complete formalization claim.",
        "",
        "## Artifact",
        "",
        "```text",
        json_name,
        f"sha256={json_sha}",
        "```",
        "",
        "## Boundary",
        "",
        "Allowed ceiling:",
        "",
        "```text",
        "definitions_and_harness_viable_only",
        "```",
        "",
        "Mode B MaoField empirical status:",
        "",
        "```text",
        "insufficient_artifact",
        "```",
        "",
        "## Exact Checks",
        "",
    ]
    for name, passed in certificate["checks"].items():
        lines.append(f"- `{name}`: {'pass' if passed else 'fail'}")
    lines.extend([
        "",
        f"All checks passed: `{str(certificate['all_checks_passed']).lower()}`",
        "",
        "## Main B0 Witness",
        "",
        "```text",
        f"K = {certificate['main_b0_witness']['K']}",
        f"(I-P_N)K = {certificate['main_b0_witness']['true_additive_residual']}",
        f"R_B_then_Q K = {certificate['main_b0_witness']['zero_order_residual_R_B_then_Q']}",
        f"R_Q_then_B K = {certificate['main_b0_witness']['artifact_R_Q_then_B']}",
        f"||R_Q_then_B K||_w^2 = {certificate['main_b0_witness']['artifact_weighted_norm_squared']}",
        "```",
        "",
        "## Symmetric A Witness",
        "",
        "```text",
        f"K' = {certificate['symmetric_a_witness']['K']}",
        f"R_Q_then_B K' = {certificate['symmetric_a_witness']['zero_order_residual_R_Q_then_B']}",
        f"R_B_then_Q K' = {certificate['symmetric_a_witness']['artifact_R_B_then_Q']}",
        "```",
        "",
        "## Interpretation",
        "",
        "This certificate upgrades the displayed 2x2 witness from float-based",
        "regression support to exact rational arithmetic. It does not replace",
        "the analytic proof and does not authorize empirical MaoField claims.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "exact_witness_v1_4_20260629.json"
    md_path = out_dir / "EXACT_WITNESS_V1_4_20260629.md"

    certificate = build_certificate()
    json_path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    json_sha = sha256_file(json_path)
    write_markdown(certificate, md_path, json_path.name, json_sha)

    print(f"json={json_path}")
    print(f"json_sha256={json_sha}")
    print(f"markdown={md_path}")
    print(f"all_checks_passed={certificate['all_checks_passed']}")


if __name__ == "__main__":
    main()
