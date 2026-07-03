#!/usr/bin/env python3
"""v1.3 zero-GPU harness for weighted ANOVA order-defect controls.

This is a synthetic-only theorem-control harness for the debranded mathematics
direction. It does not read MaoField aggregates, load checkpoints, run
inference, train, or authorize a new loss. The floating-point harness is deterministic regression support only; the mathematical claims are carried by the analytic proof and exact rational certificate, not by JSON floats.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


EPS = 1e-12
CANONICAL_HARNESS_BOUNDARY_SENTENCE = "The floating-point harness is deterministic regression support only; the mathematical claims are carried by the analytic proof and exact rational certificate, not by JSON floats."
BLOCKED_CLAIMS = [
    "full_panel_has_run",
    "sixteen_cell_full_panel_aggregate_exists",
    "residual_field_observed",
    "interaction_field_observed",
    "quotient_residual_field_observed",
    "transport_field_observed",
    "holonomy_field_observed",
    "glass_box_broken",
    "LOSO_passed",
    "F3_positive",
    "training_authorized",
    "new_loss_authorized",
    "completed_formal_system",
    "formal_v1_3_completed",
]


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def environment_metadata() -> dict[str, str]:
    return {
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.platform(),
    }


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def normalize(weights: np.ndarray) -> np.ndarray:
    weights = np.asarray(weights, dtype=float).reshape(-1)
    if np.any(weights <= 0):
        raise ValueError("weights must be positive")
    return weights / float(np.sum(weights))


def weighted_norm(v: np.ndarray, weights: np.ndarray) -> float:
    v = np.asarray(v, dtype=float).reshape(-1)
    return math.sqrt(float(np.sum(weights * v * v)))


def fro_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(np.asarray(matrix, dtype=float), ord="fro"))


def product_from_marginals(weights: np.ndarray, nq: int, nb: int) -> np.ndarray:
    table = np.asarray(weights, dtype=float).reshape(nq, nb)
    q = table.sum(axis=1)
    b = table.sum(axis=0)
    return np.outer(q, b).reshape(-1) / float(np.sum(table))


def weighted_project(v: np.ndarray, basis: np.ndarray, weights: np.ndarray) -> np.ndarray:
    basis = np.asarray(basis, dtype=float)
    v = np.asarray(v, dtype=float).reshape(-1)
    if basis.shape[1] == 0:
        return np.zeros_like(v)
    sqrt_w = np.sqrt(weights)
    coef = np.linalg.lstsq(basis * sqrt_w[:, None], v * sqrt_w, rcond=None)[0]
    return basis @ coef


def projection_matrix(basis: np.ndarray, weights: np.ndarray) -> np.ndarray:
    basis = np.asarray(basis, dtype=float)
    weights = np.asarray(weights, dtype=float).reshape(-1)
    if basis.shape[1] == 0:
        return np.zeros((len(weights), len(weights)), dtype=float)
    gram = basis.T @ np.diag(weights) @ basis
    return basis @ np.linalg.pinv(gram) @ basis.T @ np.diag(weights)


def q_zero_mean_basis(nq: int, nb: int, weights: np.ndarray) -> np.ndarray:
    table = np.asarray(weights, dtype=float).reshape(nq, nb)
    q_marginal = table.sum(axis=1)
    columns = []
    for q_id in range(max(0, nq - 1)):
        vals = np.zeros(nq, dtype=float)
        vals[q_id] = 1.0
        vals[-1] = -q_marginal[q_id] / q_marginal[-1]
        columns.append(np.repeat(vals, nb))
    if not columns:
        return np.zeros((nq * nb, 0), dtype=float)
    return np.asarray(columns, dtype=float).T


def b_zero_mean_basis(nq: int, nb: int, weights: np.ndarray) -> np.ndarray:
    table = np.asarray(weights, dtype=float).reshape(nq, nb)
    b_marginal = table.sum(axis=0)
    columns = []
    for b_id in range(max(0, nb - 1)):
        vals = np.zeros(nb, dtype=float)
        vals[b_id] = 1.0
        vals[-1] = -b_marginal[b_id] / b_marginal[-1]
        columns.append(np.tile(vals, nq))
    if not columns:
        return np.zeros((nq * nb, 0), dtype=float)
    return np.asarray(columns, dtype=float).T


def order_defect_operators(
    nq: int,
    nb: int,
    weights: np.ndarray,
) -> dict[str, np.ndarray]:
    n = nq * nb
    constants = np.ones((n, 1), dtype=float)
    a_basis = q_zero_mean_basis(nq, nb, weights)
    b0_basis = b_zero_mean_basis(nq, nb, weights)
    n_add = np.column_stack([constants, a_basis, b0_basis])
    p_c = projection_matrix(constants, weights)
    p_a = projection_matrix(a_basis, weights)
    p_b0 = projection_matrix(b0_basis, weights)
    p_n = projection_matrix(n_add, weights)
    eye = np.eye(n, dtype=float)
    r_q_then_b = (eye - p_b0) @ (eye - p_a) @ (eye - p_c)
    r_b_then_q = (eye - p_a) @ (eye - p_b0) @ (eye - p_c)
    return {
        "P_C": p_c,
        "P_A": p_a,
        "P_B0": p_b0,
        "P_N": p_n,
        "R_Q_then_B": r_q_then_b,
        "R_B_then_Q": r_b_then_q,
        "D_w": r_q_then_b - r_b_then_q,
        "commutator": p_b0 @ p_a - p_a @ p_b0,
        "N_add_basis": n_add,
    }


def centered_indicator_identity(weights: np.ndarray, nq: int, nb: int) -> dict[str, Any]:
    table = np.asarray(weights, dtype=float).reshape(nq, nb)
    q_marginal = table.sum(axis=1)
    b_marginal = table.sum(axis=0)
    errors = []
    values = []
    for q0 in range(nq):
        a = np.zeros((nq, nb), dtype=float)
        a[q0, :] = 1.0
        a -= q_marginal[q0]
        for b0 in range(nb):
            b = np.zeros((nq, nb), dtype=float)
            b[:, b0] = 1.0
            b -= b_marginal[b0]
            inner = float(np.sum(table * a * b))
            product_gap = float(table[q0, b0] - q_marginal[q0] * b_marginal[b0])
            errors.append(inner - product_gap)
            values.append(product_gap)
    return {
        "identity_max_abs_error": float(np.max(np.abs(errors))),
        "product_gap_values": values,
        "product_gap_max_abs": float(np.max(np.abs(values))),
    }


def build_threshold_contract() -> dict[str, dict[str, Any]]:
    return {
        "product_weight_order_independence_control": {
            "max_product_weight_error": 1e-12,
            "max_order_defect_fro_norm": 1e-12,
            "max_basis_order_difference_weighted_norm": 1e-12,
            "max_q_order_vs_true_residual_basis_norm": 1e-12,
            "max_b_order_vs_true_residual_basis_norm": 1e-12,
        },
        "centered_indicator_product_iff_control": {
            "max_identity_error": 1e-12,
            "max_product_case_gap": 1e-12,
            "max_nonproduct_gap_matrix_error": 1e-12,
            "min_nonproduct_gap_max_abs": 1e-6,
        },
        "nonproduct_pure_main_effect_no_go_control": {
            "max_true_additive_residual_norm": 1e-12,
            "max_zero_order_residual_norm": 1e-12,
            "max_artifact_vector_inf_error": 1e-12,
            "min_artifact_weighted_norm": 1e-6,
            "max_symmetric_witness_vector_inf_error": 1e-12,
        },
        "threshold_contract_single_source_control": {
            "require_contract_hash_match": True,
            "require_per_test_threshold_match": True,
            "require_central_evaluator": True,
        },
    }


def basis_weighted_norm_max(matrix: np.ndarray, weights: np.ndarray) -> float:
    eye = np.eye(matrix.shape[1], dtype=float)
    return max(weighted_norm(matrix @ eye[:, i], weights) for i in range(matrix.shape[1]))


def block_product_weight_order_independence_control() -> dict[str, Any]:
    nq, nb = 2, 3
    q = normalize(np.array([2.0, 5.0]))
    b = normalize(np.array([3.0, 4.0, 7.0]))
    weights = np.outer(q, b).reshape(-1)
    product = product_from_marginals(weights, nq, nb)
    ops = order_defect_operators(nq, nb, weights)
    eye = np.eye(nq * nb, dtype=float)
    true_residual = eye - ops["P_N"]
    q_order = ops["R_Q_then_B"]
    b_order = ops["R_B_then_Q"]
    return {
        "test_id": "product_weight_order_independence_control",
        "kind": "theorem_control",
        "product_weight_max_abs_error": float(np.max(np.abs(weights - product))),
        "order_defect_fro_norm": fro_norm(ops["D_w"]),
        "basis_order_difference_weighted_norm_max": basis_weighted_norm_max(q_order - b_order, weights),
        "q_order_vs_true_residual_basis_norm_max": basis_weighted_norm_max(q_order - true_residual, weights),
        "b_order_vs_true_residual_basis_norm_max": basis_weighted_norm_max(b_order - true_residual, weights),
        "interpretation": "under product weights, the two ordered stripping maps equal the true additive residual projection",
    }


def block_centered_indicator_product_iff_control() -> dict[str, Any]:
    product_weights = np.outer(normalize(np.array([2.0, 5.0])), normalize(np.array([3.0, 4.0, 7.0]))).reshape(-1)
    nonproduct_weights = normalize(np.array([1.0, 2.0, 3.0, 5.0]))
    product_identity = centered_indicator_identity(product_weights, 2, 3)
    nonproduct_identity = centered_indicator_identity(nonproduct_weights, 2, 2)
    expected_gap = np.array([-1.0, 1.0, 1.0, -1.0], dtype=float) / 121.0
    actual_gap = np.asarray(nonproduct_identity["product_gap_values"], dtype=float)
    return {
        "test_id": "centered_indicator_product_iff_control",
        "kind": "theorem_control",
        "product_identity_max_abs_error": product_identity["identity_max_abs_error"],
        "product_gap_max_abs": product_identity["product_gap_max_abs"],
        "nonproduct_identity_max_abs_error": nonproduct_identity["identity_max_abs_error"],
        "expected_nonproduct_gap_matrix": expected_gap.reshape(2, 2).tolist(),
        "observed_nonproduct_gap_matrix": actual_gap.reshape(2, 2).tolist(),
        "nonproduct_gap_matrix_max_abs_error": float(np.max(np.abs(actual_gap - expected_gap))),
        "nonproduct_gap_max_abs": nonproduct_identity["product_gap_max_abs"],
        "interpretation": "centered indicators recover exactly the product-weight gap cell by cell",
    }


def block_nonproduct_pure_main_effect_no_go_control() -> dict[str, Any]:
    nq, nb = 2, 2
    weights = normalize(np.array([1.0, 2.0, 3.0, 5.0]))
    ops = order_defect_operators(nq, nb, weights)
    eye = np.eye(nq * nb, dtype=float)
    witness_b0 = np.array([7.0 / 11.0, -4.0 / 11.0, 7.0 / 11.0, -4.0 / 11.0], dtype=float)
    expected_artifact = np.array([1.0 / 32.0, 5.0 / 168.0, -1.0 / 96.0, -1.0 / 84.0], dtype=float)
    true_residual = (eye - ops["P_N"]) @ witness_b0
    zero_order = ops["R_B_then_Q"] @ witness_b0
    artifact_order = ops["R_Q_then_B"] @ witness_b0

    witness_a = np.array([8.0 / 11.0, 8.0 / 11.0, -3.0 / 11.0, -3.0 / 11.0], dtype=float)
    expected_symmetric_artifact = np.array([1.0 / 42.0, -1.0 / 84.0, 5.0 / 224.0, -3.0 / 224.0], dtype=float)
    symmetric_artifact = ops["R_B_then_Q"] @ witness_a
    return {
        "test_id": "nonproduct_pure_main_effect_no_go_control",
        "kind": "no_go_witness_control",
        "nonproduct_weight_matrix": weights.reshape(2, 2).tolist(),
        "b0_witness": witness_b0.tolist(),
        "true_additive_residual_weighted_norm": weighted_norm(true_residual, weights),
        "zero_order_residual_weighted_norm": weighted_norm(zero_order, weights),
        "artifact_order_vector": artifact_order.tolist(),
        "expected_artifact_order_vector": expected_artifact.tolist(),
        "artifact_vector_inf_error": float(np.max(np.abs(artifact_order - expected_artifact))),
        "artifact_weighted_norm": weighted_norm(artifact_order, weights),
        "artifact_weighted_norm_squared": weighted_norm(artifact_order, weights) ** 2,
        "expected_artifact_weighted_norm_squared": 61.0 / 177408.0,
        "symmetric_a_witness": witness_a.tolist(),
        "symmetric_artifact_vector": symmetric_artifact.tolist(),
        "expected_symmetric_artifact_vector": expected_symmetric_artifact.tolist(),
        "symmetric_witness_vector_inf_error": float(np.max(np.abs(symmetric_artifact - expected_symmetric_artifact))),
        "interpretation": "non-product weights can turn a pure main effect into a wrong-order sequential stripping artifact",
    }


def make_metric_blocks() -> list[dict[str, Any]]:
    return [
        block_product_weight_order_independence_control(),
        block_centered_indicator_product_iff_control(),
        block_nonproduct_pure_main_effect_no_go_control(),
    ]


def evaluate_test(metrics: dict[str, Any], contract: dict[str, dict[str, Any]]) -> dict[str, Any]:
    test_id = metrics["test_id"]
    thresholds = contract[test_id]
    if test_id == "product_weight_order_independence_control":
        passed = (
            metrics["product_weight_max_abs_error"] <= thresholds["max_product_weight_error"]
            and metrics["order_defect_fro_norm"] <= thresholds["max_order_defect_fro_norm"]
            and metrics["basis_order_difference_weighted_norm_max"] <= thresholds["max_basis_order_difference_weighted_norm"]
            and metrics["q_order_vs_true_residual_basis_norm_max"] <= thresholds["max_q_order_vs_true_residual_basis_norm"]
            and metrics["b_order_vs_true_residual_basis_norm_max"] <= thresholds["max_b_order_vs_true_residual_basis_norm"]
        )
    elif test_id == "centered_indicator_product_iff_control":
        passed = (
            metrics["product_identity_max_abs_error"] <= thresholds["max_identity_error"]
            and metrics["nonproduct_identity_max_abs_error"] <= thresholds["max_identity_error"]
            and metrics["product_gap_max_abs"] <= thresholds["max_product_case_gap"]
            and metrics["nonproduct_gap_matrix_max_abs_error"] <= thresholds["max_nonproduct_gap_matrix_error"]
            and metrics["nonproduct_gap_max_abs"] >= thresholds["min_nonproduct_gap_max_abs"]
        )
    elif test_id == "nonproduct_pure_main_effect_no_go_control":
        passed = (
            metrics["true_additive_residual_weighted_norm"] <= thresholds["max_true_additive_residual_norm"]
            and metrics["zero_order_residual_weighted_norm"] <= thresholds["max_zero_order_residual_norm"]
            and metrics["artifact_vector_inf_error"] <= thresholds["max_artifact_vector_inf_error"]
            and metrics["artifact_weighted_norm"] >= thresholds["min_artifact_weighted_norm"]
            and metrics["symmetric_witness_vector_inf_error"] <= thresholds["max_symmetric_witness_vector_inf_error"]
        )
    elif test_id == "threshold_contract_single_source_control":
        passed = (
            (
                not thresholds["require_contract_hash_match"]
                or metrics["runtime_threshold_contract_sha256"] == metrics["json_threshold_contract_sha256"]
            )
            and (not thresholds["require_per_test_threshold_match"] or len(metrics["per_test_threshold_mismatches"]) == 0)
            and (not thresholds["require_central_evaluator"] or metrics["central_evaluator_used"])
        )
    else:
        raise KeyError(f"no evaluator for {test_id}")
    out = dict(metrics)
    out["thresholds"] = thresholds
    out["threshold_contract_hash"] = sha256_json(contract)
    out["evaluated_by"] = "evaluate_test"
    out["pass"] = bool(passed)
    return out


def block_threshold_contract_single_source_control(
    evaluated_blocks: list[dict[str, Any]],
    contract: dict[str, dict[str, Any]],
    json_threshold_contract_sha256: str,
    json_threshold_contract_source: str,
) -> dict[str, Any]:
    contract_hash = sha256_json(contract)
    per_test_mismatches = []
    for block in evaluated_blocks:
        test_id = block["test_id"]
        if block.get("thresholds") != contract[test_id]:
            per_test_mismatches.append(test_id)
        if block.get("threshold_contract_hash") != contract_hash:
            per_test_mismatches.append(f"{test_id}:hash")
    return {
        "test_id": "threshold_contract_single_source_control",
        "kind": "meta_contract_control",
        "runtime_threshold_contract_sha256": contract_hash,
        "json_threshold_contract_sha256": json_threshold_contract_sha256,
        "json_threshold_contract_source": json_threshold_contract_source,
        "per_test_threshold_mismatches": per_test_mismatches,
        "central_evaluator_function": "evaluate_test",
        "central_evaluator_used": all(block.get("evaluated_by") == "evaluate_test" for block in evaluated_blocks),
        "interpretation": "all pass/fail logic is assigned by evaluate_test against the serialized top-level threshold contract",
    }


def build_result(json_threshold_contract_sha256: str, json_threshold_contract_source: str) -> dict[str, Any]:
    contract = build_threshold_contract()
    evaluated = [evaluate_test(block, contract) for block in make_metric_blocks()]
    meta_metrics = block_threshold_contract_single_source_control(
        evaluated_blocks=evaluated,
        contract=contract,
        json_threshold_contract_sha256=json_threshold_contract_sha256,
        json_threshold_contract_source=json_threshold_contract_source,
    )
    evaluated.append(evaluate_test(meta_metrics, contract))
    return {
        "schema": "debranded_residual_transport_synthetic_harness_v1_3",
        "created_utc": utc_now(),
        "environment": environment_metadata(),
        "evidence_boundary": {
            "mode": "Mode A finite-dimensional synthetic theorem controls only",
            "strongest_allowed_verdict": "definitions_and_harness_viable_only",
            "mode_b_maofield_empirical_status": "insufficient_artifact",
            "harness_boundary": CANONICAL_HARNESS_BOUNDARY_SENTENCE,
            "proof_responsibility": CANONICAL_HARNESS_BOUNDARY_SENTENCE,
            "blocked_claims": BLOCKED_CLAIMS,
        },
        "threshold_contract": contract,
        "threshold_contract_sha256": sha256_json(contract),
        "all_synthetic_controls_passed": all(block["pass"] for block in evaluated),
        "blocks": evaluated,
        "allowed_interpretation": "v1.3 order-defect theorem controls are internally checkable on finite synthetic examples only as deterministic regression support",
        "canonical_harness_boundary_sentence": CANONICAL_HARNESS_BOUNDARY_SENTENCE,
        "proof_responsibility": CANONICAL_HARNESS_BOUNDARY_SENTENCE,
        "forbidden_interpretation": "passing this harness is not a proof artifact, not MaoField empirical evidence, and does not authorize training or a new loss",
    }


def readback_threshold_contract_sha256(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    return sha256_json(data["threshold_contract"])


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


def write_summary(path: Path, result: dict[str, Any], json_rel: str) -> None:
    by_id = {block["test_id"]: block for block in result["blocks"]}
    no_go = by_id["nonproduct_pure_main_effect_no_go_control"]
    meta = by_id["threshold_contract_single_source_control"]
    lines = [
        "# Debranded Residual Transport Synthetic Harness v1.3",
        "",
        "Date: 2026-06-28 CST",
        "",
        "## Boundary",
        "",
        "This is a zero-GPU synthetic theorem-control harness for the debranded",
        "finite-dimensional mathematics direction. It is not a MaoField empirical",
        "result and does not authorize training, checkpoint loading, full-panel",
        "generation, model inference, or a new loss.",
        "",
        CANONICAL_HARNESS_BOUNDARY_SENTENCE,
        "",
        "Strongest allowed verdict:",
        "",
        "```text",
        "definitions_and_harness_viable_only",
        "```",
        "",
        "Mode B MaoField status remains:",
        "",
        "```text",
        "insufficient_artifact",
        "```",
        "",
        "## Artifact",
        "",
        "```text",
        json_rel,
        "```",
        "",
        "## v1.3 Structure",
        "",
        "- metrics are generated by theorem-control block functions;",
        "- pass/fail is assigned only by `evaluate_test`;",
        "- all thresholds come from `build_threshold_contract`;",
        "- top-level JSON serializes the same threshold contract;",
        "- JSON-side threshold hash is read back from a written JSON artifact;",
        "- there are no random draws and no MaoField data reads.",
        "",
        "## Blocks",
        "",
    ]
    for block in result["blocks"]:
        lines.append(f"- `{block['test_id']}`: {'pass' if block['pass'] else 'fail'}")
    lines.extend(
        [
            "",
            "All synthetic controls passed:",
            "",
            "```text",
            str(result["all_synthetic_controls_passed"]).lower(),
            "```",
            "",
            "## Selected Metrics",
            "",
            "```text",
        ]
    )
    selected = [
        (
            "product_weight_order_independence_control",
            [
                "product_weight_max_abs_error",
                "order_defect_fro_norm",
                "basis_order_difference_weighted_norm_max",
                "q_order_vs_true_residual_basis_norm_max",
                "b_order_vs_true_residual_basis_norm_max",
            ],
        ),
        (
            "centered_indicator_product_iff_control",
            [
                "product_identity_max_abs_error",
                "product_gap_max_abs",
                "nonproduct_identity_max_abs_error",
                "nonproduct_gap_matrix_max_abs_error",
                "nonproduct_gap_max_abs",
            ],
        ),
        (
            "nonproduct_pure_main_effect_no_go_control",
            [
                "true_additive_residual_weighted_norm",
                "zero_order_residual_weighted_norm",
                "artifact_vector_inf_error",
                "artifact_weighted_norm",
                "artifact_weighted_norm_squared",
                "symmetric_witness_vector_inf_error",
            ],
        ),
        (
            "threshold_contract_single_source_control",
            [
                "runtime_threshold_contract_sha256",
                "json_threshold_contract_sha256",
                "json_threshold_contract_source",
                "central_evaluator_used",
            ],
        ),
    ]
    for test_id, keys in selected:
        block = by_id[test_id]
        for key in keys:
            lines.append(f"{test_id}.{key} = {fmt(block[key])}")
    lines.extend(
        [
            "```",
            "",
            "## Exact Witness Coordinates",
            "",
            "Main B0 witness artifact:",
            "",
            "```text",
            str(no_go["expected_artifact_order_vector"]),
            "```",
            "",
            "Symmetric A witness artifact uses the corrected coordinates:",
            "",
            "```text",
            str(no_go["expected_symmetric_artifact_vector"]),
            "```",
            "",
            "The symmetric coordinates correct the 11x arithmetic slip in report",
            "(32). The main B0 witness was already sufficient for T3.",
            "",
            "## Interpretation",
            "",
            "The v1.3 harness implements the three deterministic zero-GPU theorem",
            "controls recommended by report (32): product-weight order",
            "independence, centered-indicator product iff, and the non-product",
            "pure-main-effect no-go witness. Passing these controls supports",
            "formal design/proof review only.",
            "",
            "The mathematical order-defect claim is carried by the analytic proof",
            "in `FORMAL_NOTE_V1_3_ORDER_DEFECT_20260628.md` and the exact rational",
            "certificate in `EXACT_WITNESS_V1_4_20260629.md`; this harness only",
            "guards regressions in finite synthetic examples.",
            "",
            "Blocked interpretations:",
            "",
            "```text",
        ]
    )
    lines.extend(BLOCKED_CLAIMS)
    lines.extend(["```", ""])
    write_text(path, "\n".join(lines))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--summary-md", type=Path, required=True)
    parser.add_argument(
        "--json-rel",
        default="docs/infra/debranded_residual_transport/synthetic_harness_v1_3_20260628.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    contract_hash = sha256_json(build_threshold_contract())
    draft = build_result(
        json_threshold_contract_sha256=contract_hash,
        json_threshold_contract_source="prewrite_contract_hash_for_readback_bootstrap",
    )
    write_json(args.out, draft)
    readback_hash = readback_threshold_contract_sha256(args.out)
    result = build_result(
        json_threshold_contract_sha256=readback_hash,
        json_threshold_contract_source="readback_from_written_json_threshold_contract",
    )
    write_json(args.out, result)
    final_readback_hash = readback_threshold_contract_sha256(args.out)
    write_summary(args.summary_md, result, args.json_rel)
    if final_readback_hash != result["threshold_contract_sha256"]:
        return 1
    if not result["all_synthetic_controls_passed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
