#!/usr/bin/env python3
"""Core primitives for the independent Brief 0018 source audit.

The exact Dirichlet theorem is not inferred from these routines.  This module
implements one deterministic numerical audit of a frozen finite-K source
implementation.  Statistical bounds refer to the ideal iid-uniform model
underlying the fixed pseudorandom construction.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


SCHEMA_VERSION = "cyz-0018-stat-audit-report-v1"
AUDIT_ID = "audit-k1-v1"
BASELINE_COMMIT = "90a8b09bea9fd0881e95a9064179423e51af9dd2"
MASTER_SEED_TEXT = "brief0018-source-audit-v1"
RNG_VERSION = "pcg64dxsm-u52mid-exp-boxmuller-v1"
REGISTRY_CANONICAL_SHA256 = (
    "8532146765b17ea0b23b38e3f47052a68b0d315c7411535cbffcbacdee78f0f8"
)

LEDGER_SIZE = 514
FAMILYWISE_ALPHA = 1.0e-8
BONFERRONI_DELTA = FAMILYWISE_ALPHA / LEDGER_SIZE
BERNSTEIN_LOG = math.log(2.0 / BONFERRONI_DELTA)
FULL_RADIAL_SAMPLES = 2**20
FULL_SOURCE_SAMPLES = 2**18
FULL_MUTATION_SAMPLES = 2**20
CHUNK_SIZE = 8192
FLOW_PREFIX_SAMPLES = 4096
GOLDEN_REPLAY_SAMPLES = 1024

ALPHA = (4, 15, 15)
ALPHA_SUM = sum(ALPHA)
MACHINE_EPSILON = 2.0**-52
ALGEBRA_TOLERANCE_FACTOR = 2.0**-40
FLOW_TOLERANCE_FACTOR = 2.0**-36

SEED_HEX = {
    "gamma_radial": "d797e56bf1073b6a73b1f70d8ec385d7",
    "beta_radial": "f9d684d2cbc683d187447f0001ba16f6",
    "full_source": "beae04640776578fb2ce0e0ebe967c3a",
    "golden_replay": "df0a38bd02cee7f09d0ca0c992427a5c",
    "mut_shape_d": "ca55712204226510e369683fa218a2c2",
    "mut_shape_half_d": "2b718ae0ed2f97bba254c2485d39b96b",
    "mut_shape_d_minus_half": "513bfc79a3676a25986792ac0ba211b6",
}

GOLDEN_RAW_HEX = {
    "gamma_radial": [
        "126d41abbdce1788",
        "a8b54db4e8dd9cfa",
        "f3d0af0f3af85101",
        "557d76b11ea9aabc",
    ],
    "beta_radial": [
        "71848319b7ba7520",
        "943aa0e85160bc7d",
        "38e12b8e069d120e",
        "9c7a923638fc5f2a",
    ],
    "full_source": [
        "5610a215952903d1",
        "4780e61c33c66d5d",
        "ec8060cc51c93700",
        "7c86afd160e28d8d",
    ],
    "golden_replay": [
        "e78fd19850bb9cf6",
        "5db017dd3c94039e",
        "048793b0c61cf9b7",
        "dedd636fd22daf0e",
    ],
    "mut_shape_d": [
        "0bba145404404251",
        "41ad593d69879153",
        "63e6ac674e9781f6",
        "1922dd9a69db8af8",
    ],
    "mut_shape_half_d": [
        "0e6e66ecdcc4612a",
        "f1d2bff7b83723ca",
        "d94743c74ad8f60b",
        "c531ee77d7776bb7",
    ],
    "mut_shape_d_minus_half": [
        "ce55fcfb8cc6032e",
        "1f8c90e88269d774",
        "20c30fdbfa550387",
        "b4b71ea9e88c9d91",
    ],
}


class AuditError(ValueError):
    """A localized registration, serialization, or audit failure."""


def _reject_json_constant(token: str) -> None:
    raise AuditError(f"non-finite JSON token is forbidden: {token}")


def _parse_finite_float(token: str) -> float:
    value = float(token)
    if not math.isfinite(value):
        raise AuditError(f"non-finite JSON number is forbidden: {token}")
    return value


def _reject_duplicate_pairs(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AuditError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def loads_strict_json(text: str) -> Any:
    """Parse JSON while rejecting duplicate keys and non-finite numbers."""

    return json.loads(
        text,
        object_pairs_hook=_reject_duplicate_pairs,
        parse_constant=_reject_json_constant,
        parse_float=_parse_finite_float,
    )


def load_strict_json(path: Path) -> Any:
    return loads_strict_json(path.read_text(encoding="utf-8"))


def canonical_json_bytes(value: Any) -> bytes:
    """Canonical semantic JSON, independent of indentation and line endings."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def type_strict_equal(left: Any, right: Any) -> bool:
    """JSON-semantic equality that does not conflate true with 1."""

    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return set(left) == set(right) and all(
            type_strict_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            type_strict_equal(a, b) for a, b in zip(left, right)
        )
    return bool(left == right)


def attach_semantic_hash(report: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(report))
    result.pop("semantic_sha256", None)
    result["semantic_sha256"] = canonical_sha256(result)
    return result


def verify_semantic_hash(report: Mapping[str, Any]) -> bool:
    if type(report.get("semantic_sha256")) is not str:
        return False
    payload = copy.deepcopy(dict(report))
    observed = payload.pop("semantic_sha256")
    return bool(observed == canonical_sha256(payload))


def write_canonical_report(path: Path, report: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(report) + b"\n")


def normalized_file_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def _require_exact_type(value: Any, expected: type, location: str) -> None:
    if type(value) is not expected:
        raise AuditError(
            f"{location} must have exact type {expected.__name__}, "
            f"not {type(value).__name__}"
        )


def _require_keys(
    value: Mapping[str, Any], expected: set[str], location: str
) -> None:
    actual = set(value)
    if actual != expected:
        raise AuditError(
            f"{location} fields mismatch: "
            f"extra={sorted(actual - expected)} missing={sorted(expected - actual)}"
        )


@dataclass(frozen=True)
class AuditCell:
    tension: float
    winding_length: float
    mass: float
    k1: float
    d: int
    e_perp: float
    e_star: float
    p_total: np.ndarray
    transverse_period: float
    r_in: float
    r_out: float
    ell_s: float
    epsilon_graph: float
    kappa_uv: float


def registry_path() -> Path:
    return Path(__file__).resolve().parent / "stat_audit_registry.json"


def validate_registry(registry: Any) -> AuditCell:
    """Validate the one fixed audit registry, not a general-purpose DSL."""

    _require_exact_type(registry, dict, "registry")
    if canonical_sha256(registry) != REGISTRY_CANONICAL_SHA256:
        raise AuditError("registry canonical SHA-256 differs from audit-k1-v1")

    _require_keys(
        registry,
        {
            "audit_id",
            "claim_class",
            "derived_exact",
            "non_source_registry",
            "profiles",
            "schema_version",
            "source_draw_registry",
            "statistical_contract",
        },
        "registry",
    )
    if registry["audit_id"] != AUDIT_ID:
        raise AuditError("unexpected audit_id")
    if registry["schema_version"] != "cyz-0018-stat-audit-registry-v1":
        raise AuditError("unexpected registry schema_version")

    source = registry["source_draw_registry"]
    non_source = registry["non_source_registry"]
    _require_exact_type(source, dict, "source_draw_registry")
    _require_exact_type(non_source, dict, "non_source_registry")

    forbidden_source_fields = {
        "r_in",
        "r_out",
        "rank_tolerance",
        "response_data",
        "reaction_data",
        "epsilon_graph",
        "kappa_uv",
        "initial_history",
    }
    overlap = forbidden_source_fields.intersection(source)
    if overlap:
        raise AuditError(f"event/validity fields entered source registry: {overlap}")

    for name in ("K", "winding_axis_zero_based"):
        _require_exact_type(source[name], int, f"source_draw_registry.{name}")
    for i, value in enumerate(source["level_matching"]):
        _require_exact_type(value, int, f"source_draw_registry.level_matching[{i}]")
    for i, value in enumerate(source["winding_orientations"]):
        _require_exact_type(
            value, int, f"source_draw_registry.winding_orientations[{i}]"
        )

    tension = float.fromhex(source["T_F_hex"])
    winding_length = float.fromhex(source["L_w_hex"])
    mass = tension * winding_length
    k1 = 2.0 * math.pi / winding_length
    d = 16 * source["K"]
    p_total = np.array(
        [float.fromhex(value) for value in source["P_total_hex"]],
        dtype=np.float64,
    )
    e_perp = float.fromhex(source["E_perp_hex"])
    e_star = e_perp - float(np.dot(p_total, p_total)) / (4.0 * mass)
    transverse_periods = [
        float.fromhex(value) for value in source["torus_circumference_hex"][:8]
    ]
    if len(set(transverse_periods)) != 1:
        raise AuditError("audit cell requires eight equal transverse periods")
    event = non_source["event"]
    validity = non_source["validity"]
    cell = AuditCell(
        tension=tension,
        winding_length=winding_length,
        mass=mass,
        k1=k1,
        d=d,
        e_perp=e_perp,
        e_star=e_star,
        p_total=p_total,
        transverse_period=transverse_periods[0],
        r_in=float.fromhex(event["r_in_hex"]),
        r_out=float.fromhex(event["r_out_hex"]),
        ell_s=float.fromhex(validity["ell_s_hex"]),
        epsilon_graph=float.fromhex(validity["epsilon_graph_hex"]),
        kappa_uv=float.fromhex(validity["kappa_uv_hex"]),
    )
    exact = registry["derived_exact"]
    checks = {
        "M": cell.mass.hex() == exact["M_hex"],
        "k1": cell.k1.hex() == exact["k_1_hex"],
        "d": cell.d == exact["d"],
        "e_star": cell.e_star.hex() == exact["e_star_hex"],
        "alpha": list(ALPHA) == exact["alpha"],
        "alpha_sum": ALPHA_SUM == exact["alpha_sum"],
        "uv": (cell.k1 * cell.ell_s).hex()
        == exact["k_max_ell_s_hex"],
    }
    if not all(checks.values()):
        raise AuditError(f"derived audit-cell identity failed: {checks}")
    if not (0.0 < cell.r_in < cell.r_out < 4.0):
        raise AuditError("registered radii violate injectivity-radius ordering")
    if cell.e_star <= 0.0:
        raise AuditError("registered source requires E_star > 0")
    if source["level_matching"] != [0, 0]:
        raise AuditError("audit-k1-v1 supports only zero level matching")

    registered_seed_hex = registry["statistical_contract"]["seeds_hex"]
    if registered_seed_hex != SEED_HEX:
        raise AuditError("registered seed table differs from implementation")
    if registry["statistical_contract"]["ledger_size"] != LEDGER_SIZE:
        raise AuditError("registered ledger size differs from implementation")
    return cell


def load_registered_cell(path: Path | None = None) -> tuple[dict[str, Any], AuditCell]:
    resolved = path if path is not None else registry_path()
    registry = load_strict_json(resolved)
    return registry, validate_registry(registry)


def seed_from_label(label: str) -> int:
    if label not in SEED_HEX:
        raise AuditError(f"unregistered seed label: {label}")
    digest = hashlib.sha256(
        MASTER_SEED_TEXT.encode("ascii") + b"|" + label.encode("ascii")
    ).digest()
    value = int.from_bytes(digest[:16], "big")
    if f"{value:032x}" != SEED_HEX[label]:
        raise AuditError(f"derived seed mismatch for {label}")
    return value


def make_rng(label: str) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64DXSM(seed_from_label(label)))


def raw_hex_prefix(label: str, count: int = 4) -> list[str]:
    rng = make_rng(label)
    return [f"{int(value):016x}" for value in rng.bit_generator.random_raw(count)]


def verify_golden_raw_streams() -> dict[str, Any]:
    observed = {
        label: raw_hex_prefix(label, len(expected))
        for label, expected in GOLDEN_RAW_HEX.items()
    }
    passed = observed == GOLDEN_RAW_HEX
    if not passed:
        raise AuditError("PCG64DXSM golden raw stream mismatch")
    return {
        "status": "PASS",
        "algorithm": "numpy.random.PCG64DXSM",
        "prefix_words_each": 4,
        "observed": observed,
    }


def uniform_open(
    rng: np.random.Generator, shape: int | tuple[int, ...]
) -> np.ndarray:
    """Map raw words to an open 52-bit midpoint grid in (0,1)."""

    raw = rng.bit_generator.random_raw(shape)
    q = (raw >> np.uint64(12)).astype(np.float64)
    result = (q + 0.5) * 2.0**-52
    if not bool(np.all((result > 0.0) & (result < 1.0))):
        raise AuditError("uniform midpoint map left the open unit interval")
    return result


def validate_gamma_shapes(shapes: Sequence[Any], d: int = 16) -> None:
    expected = (4, d - 1, d - 1)
    if tuple(shapes) != expected or any(type(value) is not int for value in shapes):
        raise AuditError(
            f"Gamma shapes must be exact integers {expected}, got {tuple(shapes)}"
        )


def validate_positive_e_star(value: Any) -> float:
    if type(value) is not float or not math.isfinite(value) or value <= 0.0:
        raise AuditError("E_star must be a finite positive float")
    return value


def gamma_radial_chunk(
    rng: np.random.Generator, count: int, e_star: float = 1.0
) -> np.ndarray:
    """Integer-shape Gamma implementation using sums of exponentials."""

    validate_gamma_shapes(ALPHA)
    uniforms = uniform_open(rng, (count, ALPHA_SUM))
    gamma = np.empty((count, 3), dtype=np.float64)
    gamma[:, 0] = -np.log(uniforms[:, :4]).sum(axis=1)
    gamma[:, 1] = -np.log(uniforms[:, 4:19]).sum(axis=1)
    gamma[:, 2] = -np.log(uniforms[:, 19:34]).sum(axis=1)
    return e_star * gamma / gamma.sum(axis=1)[:, None]


def beta_radial_chunk(
    rng: np.random.Generator, count: int, e_star: float = 1.0
) -> np.ndarray:
    """Independent hierarchical-Beta implementation via order statistics."""

    first = uniform_open(rng, (count, 33))
    second = uniform_open(rng, (count, 29))
    beta_0 = np.partition(first, 3, axis=1)[:, 3]
    beta_1 = np.partition(second, 14, axis=1)[:, 14]
    result = np.empty((count, 3), dtype=np.float64)
    result[:, 0] = beta_0
    result[:, 1] = (1.0 - beta_0) * beta_1
    result[:, 2] = (1.0 - beta_0) * (1.0 - beta_1)
    return e_star * result


def box_muller_sphere(uniforms: np.ndarray, dimension: int) -> np.ndarray:
    if dimension % 2 != 0 or uniforms.shape[1] != dimension:
        raise AuditError("Box-Muller sphere requires one even-sized uniform row")
    pairs = uniforms.reshape(uniforms.shape[0], dimension // 2, 2)
    radius = np.sqrt(-2.0 * np.log(pairs[:, :, 0]))
    phase = 2.0 * math.pi * pairs[:, :, 1]
    normal = np.empty((uniforms.shape[0], dimension), dtype=np.float64)
    normal[:, 0::2] = radius * np.cos(phase)
    normal[:, 1::2] = radius * np.sin(phase)
    norm = np.sqrt((normal * normal).sum(axis=1))
    return normal / norm[:, None]


def full_source_chunk(
    rng: np.random.Generator, count: int, cell: AuditCell
) -> dict[str, Any]:
    """One rejection-free full source chunk with fixed raw-word consumption."""

    if cell.d != 16 or cell.e_star != 1.0:
        raise AuditError("full_source_chunk is frozen to audit-k1-v1")
    uniforms = uniform_open(rng, (count, 114))
    index = 0
    gamma = np.empty((count, 3), dtype=np.float64)
    gamma[:, 0] = -np.log(uniforms[:, index : index + 4]).sum(axis=1)
    index += 4
    gamma[:, 1] = -np.log(uniforms[:, index : index + 15]).sum(axis=1)
    index += 15
    gamma[:, 2] = -np.log(uniforms[:, index : index + 15]).sum(axis=1)
    index += 15
    radial = gamma / gamma.sum(axis=1)[:, None]
    u0 = box_muller_sphere(uniforms[:, index : index + 8], 8)
    index += 8
    chiral: list[np.ndarray] = []
    for _ in range(4):
        chiral.append(
            box_muller_sphere(uniforms[:, index : index + 16], 16)
        )
        index += 16
    q_unit = uniforms[:, index : index + 8]
    index += 8
    if index != 114:
        raise AssertionError("full source raw-word accounting failed")
    return {
        "radial": radial,
        "u0": u0,
        "chiral": chiral,
        "q_unit": q_unit,
        "raw_uniforms_per_sample": index,
    }


def source_chunk_coefficients(
    source: Mapping[str, Any], cell: AuditCell
) -> dict[str, Any]:
    radial = source["radial"]
    u0 = source["u0"]
    chiral = source["chiral"]
    relative_momentum = np.sqrt(radial[:, 0])[:, None] * u0
    z = [
        np.sqrt(radial[:, 1] / 2.0)[:, None] * chiral[0],
        np.sqrt(radial[:, 1] / 2.0)[:, None] * chiral[1],
        np.sqrt(radial[:, 2] / 2.0)[:, None] * chiral[2],
        np.sqrt(radial[:, 2] / 2.0)[:, None] * chiral[3],
    ]
    c_scale = math.sqrt(2.0 * cell.mass) * cell.k1
    c = [value / c_scale for value in z]
    coefficients: list[dict[str, np.ndarray]] = []
    for left, right in ((c[0], c[1]), (c[2], c[3])):
        left_re, left_im = left[:, :8], left[:, 8:]
        right_re, right_im = right[:, :8], right[:, 8:]
        coefficients.append(
            {
                "x": 2.0 * (left_re + right_re),
                "y": -2.0 * (left_im + right_im),
                "p": 2.0 * cell.k1 * (left_im - right_im),
                "q": 2.0 * cell.k1 * (left_re - right_re),
            }
        )
    center_velocity = cell.p_total / (2.0 * cell.mass)
    relative_velocity = relative_momentum / math.sqrt(cell.mass)
    velocity_1 = center_velocity + relative_velocity
    velocity_2 = center_velocity - relative_velocity
    return {
        "relative_momentum": relative_momentum,
        "z": z,
        "c": c,
        "coefficients": coefficients,
        "velocity_1": velocity_1,
        "velocity_2": velocity_2,
        "q_relative": source["q_unit"] * cell.transverse_period,
    }


def moment_multi_indices(max_total_degree: int = 4) -> list[tuple[int, int, int]]:
    result: list[tuple[int, int, int]] = []
    for total in range(1, max_total_degree + 1):
        for r0 in range(total + 1):
            for r1 in range(total - r0 + 1):
                result.append((r0, r1, total - r0 - r1))
    if max_total_degree == 4 and len(result) != 34:
        raise AssertionError("Dirichlet moment index count changed")
    return result


def _rising(value: int, count: int) -> int:
    result = 1
    for offset in range(count):
        result *= value + offset
    return result


def dirichlet_moment(index: tuple[int, int, int]) -> Fraction:
    total = sum(index)
    numerator = math.prod(
        _rising(alpha, exponent) for alpha, exponent in zip(ALPHA, index)
    )
    return Fraction(numerator, _rising(ALPHA_SUM, total))


def dirichlet_variance(index: tuple[int, int, int]) -> Fraction:
    mean = dirichlet_moment(index)
    second = dirichlet_moment(tuple(2 * value for value in index))
    return second - mean * mean


def bernstein_threshold(variance: float | Fraction, count: int) -> float:
    linear = BERNSTEIN_LOG / (3.0 * count)
    return linear + math.sqrt(
        linear * linear + 2.0 * float(variance) * BERNSTEIN_LOG / count
    )


def two_sample_bernstein_threshold(
    variance: float | Fraction, count: int
) -> float:
    linear = BERNSTEIN_LOG / (3.0 * count)
    return linear + math.sqrt(
        linear * linear + 4.0 * float(variance) * BERNSTEIN_LOG / count
    )


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def ledger_entry(
    *,
    test_id: str,
    category: str,
    observed: float,
    expected: float,
    variance: float,
    threshold: float,
    count: int,
) -> dict[str, Any]:
    deviation = abs(observed - expected)
    ratio = deviation / threshold if threshold > 0.0 else math.inf
    return {
        "category": category,
        "count": count,
        "deviation": deviation,
        "expected": expected,
        "normalized_deviation": ratio,
        "observed": observed,
        "passed": bool(deviation <= threshold),
        "test_id": test_id,
        "threshold": threshold,
        "variance_under_null": variance,
    }


def algebra_tolerance(scale: float | np.ndarray) -> float | np.ndarray:
    return ALGEBRA_TOLERANCE_FACTOR * np.maximum(1.0, scale)


def flow_tolerance(scale: float | np.ndarray) -> float | np.ndarray:
    return FLOW_TOLERANCE_FACTOR * np.maximum(1.0, scale)


def source_inventory() -> dict[str, str]:
    directory = Path(__file__).resolve().parent
    names = [
        "stat_audit_core.py",
        "statistical_audit.py",
        "run_stat_audit.py",
        "stat_audit_registry.json",
    ]
    return {
        f"artifacts/0018/{name}": normalized_file_sha256(
            directory / name
        )
        for name in names
    }


def runtime_inventory() -> dict[str, Any]:
    return {
        "numpy_version": np.__version__,
        "python_implementation": sys.implementation.name,
        "python_version": ".".join(str(value) for value in sys.version_info[:3]),
    }


def report_claim_boundary() -> dict[str, Any]:
    return {
        "claim_class": "controlled numerical verification",
        "exact_theorem_supplied_by_this_artifact": False,
        "physical_event_law_computed": False,
        "physical_first_entry_mass_computed": False,
        "prng_is_physical_randomness_claim": False,
        "scope": (
            "one frozen finite-K source implementation audit; statistical "
            "checks supplement but do not prove the analytic Dirichlet law"
        ),
    }


def strict_report_compare(stored: Any, regenerated: Any) -> None:
    if not type_strict_equal(stored, regenerated):
        raise AuditError("stored report differs from regenerated semantic JSON")


def ensure_all_finite(value: Any, location: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            ensure_all_finite(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            ensure_all_finite(child, f"{location}[{index}]")
    elif type(value) is float and not math.isfinite(value):
        raise AuditError(f"non-finite report number at {location}")


def to_json_native(value: Any) -> Any:
    """Convert NumPy scalar containers before type-strict semantic replay."""

    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): to_json_native(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_json_native(child) for child in value]
    return value


def fixed_threshold_manifest() -> dict[str, Any]:
    """Immutable statistical contract shared by full and fast profiles."""

    representative = {}
    for index in [
        (1, 0, 0),
        (0, 1, 0),
        (2, 0, 0),
        (0, 2, 0),
        (1, 1, 0),
        (1, 1, 1),
    ]:
        variance = dirichlet_variance(index)
        representative[",".join(map(str, index))] = {
            "expected": fraction_text(dirichlet_moment(index)),
            "single_sample_threshold": bernstein_threshold(
                variance, FULL_RADIAL_SAMPLES
            ),
            "two_sample_threshold": two_sample_bernstein_threshold(
                variance, FULL_RADIAL_SAMPLES
            ),
        }
    return {
        "bernstein_log": BERNSTEIN_LOG,
        "bonferroni_delta": BONFERRONI_DELTA,
        "familywise_alpha": FAMILYWISE_ALPHA,
        "ledger_size": LEDGER_SIZE,
        "radial_representative": representative,
        "torus_component_threshold": bernstein_threshold(
            0.5, FULL_SOURCE_SAMPLES
        ),
    }


def semantic_manifest_sha256() -> str:
    return canonical_sha256(
        {
            "audit_id": AUDIT_ID,
            "registry_sha256": REGISTRY_CANONICAL_SHA256,
            "rng_version": RNG_VERSION,
            "seed_hex": SEED_HEX,
            "thresholds": fixed_threshold_manifest(),
        }
    )


def source_draw_registry_sha256(registry: Mapping[str, Any]) -> str:
    source = registry.get("source_draw_registry")
    if type(source) is not dict:
        raise AuditError("source_draw_registry must be one JSON object")
    return canonical_sha256(
        {
            "domain": "cyz-0018-source-draw-registry-v1",
            "source_draw_registry": source,
        }
    )
