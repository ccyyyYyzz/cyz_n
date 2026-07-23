#!/usr/bin/env python3
"""Generate the strict structural JSON Schema for the Brief 0018 v2 record."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import event_contract as contract


def obj(
    properties: dict[str, Any],
    *,
    required: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": properties,
        "required": required if required is not None else list(properties),
    }


def array(items: dict[str, Any], **keywords: Any) -> dict[str, Any]:
    return {"type": "array", "items": items, **keywords}


def nullable(schema: dict[str, Any]) -> dict[str, Any]:
    return {"anyOf": [schema, {"type": "null"}]}


def reference(name: str) -> dict[str, str]:
    return {"$ref": f"#/$defs/{name}"}


def build_schema() -> dict[str, Any]:
    string = {"type": "string", "minLength": 1}
    boolean = {"type": "boolean"}
    number = {"type": "number"}
    integer = {"type": "integer"}
    digest = {
        "type": "string",
        "pattern": "^[0-9a-f]{64}$",
    }
    string_array = array(string)

    defs: dict[str, Any] = {}
    defs["hash"] = digest
    defs["interval"] = obj({"lo": number, "hi": number})
    defs["dyadic"] = obj(
        {
            "numerator": integer,
            "power_of_two": {"type": "integer", "minimum": 0},
        }
    )
    defs["exactInterval"] = obj(
        {"lo": reference("dyadic"), "hi": reference("dyadic")}
    )
    defs["box"] = obj(
        {
            "sigma1": reference("interval"),
            "sigma2": reference("interval"),
            "time": reference("interval"),
        }
    )
    defs["exactBox"] = obj(
        {
            "sigma1": reference("exactInterval"),
            "sigma2": reference("exactInterval"),
            "time": reference("exactInterval"),
        }
    )
    defs["rank"] = obj(
        {
            "status": {"enum": ["certified", "unresolved"]},
            "exact_rank": nullable(
                {"type": "integer", "minimum": 0, "maximum": 3}
            ),
            "possible_ranks": array(
                {"type": "integer", "minimum": 0, "maximum": 3},
                minItems=1,
                uniqueItems=True,
            ),
        }
    )
    defs["rankCertificate"] = obj(
        {
            "certificate_id": string,
            "method": {
                "enum": [
                    "exact_rational_elimination",
                    "interval_singular_enclosure",
                ]
            },
            "J_sha256": digest,
            "G_sha256": digest,
            "H_sha256": digest,
            "singular_intervals_sha256": digest,
            "declared_rank": nullable(
                {"type": "integer", "minimum": 0, "maximum": 3}
            ),
            "possible_ranks": array(
                {"type": "integer", "minimum": 0, "maximum": 3},
                minItems=1,
                uniqueItems=True,
            ),
        }
    )
    vector9 = array(number, minItems=9, maxItems=9)
    integer_vector9 = array(integer, minItems=9, maxItems=9)
    interval_vector3 = array(
        reference("interval"), minItems=3, maxItems=3
    )
    matrix9 = array(
        array(number, minItems=9, maxItems=9),
        minItems=9,
        maxItems=9,
    )
    matrix93 = array(
        array(number, minItems=3, maxItems=3),
        minItems=9,
        maxItems=9,
    )
    matrix3 = array(
        array(number, minItems=3, maxItems=3),
        minItems=3,
        maxItems=3,
    )
    defs["jetNormal"] = obj(
        {
            "coordinate_basis": string,
            "G": matrix9,
            "H": matrix3,
            "J": matrix93,
            "singular_value_intervals": interval_vector3,
            "rank": reference("rank"),
            "rank_certificate": reference("rankCertificate"),
            "normal_dimension": nullable(
                {"type": "integer", "minimum": 0, "maximum": 9}
            ),
            "P_N": nullable(matrix9),
            "normal_frame": nullable(
                array(array(number, minItems=1), minItems=9, maxItems=9)
            ),
            "s": vector9,
            "b": nullable(vector9),
            "ell": nullable(vector9),
        }
    )
    defs["geometryCertificate"] = obj(
        {
            "certificate_id": string,
            "hessian_sha256": digest,
            "flux_sha256": digest,
            "hessian_class": {
                "enum": ["positive_definite", "psd_singular", "unresolved"]
            },
            "leading_minor_range": reference("interval"),
            "determinant_range": reference("interval"),
            "flux_class": {
                "enum": [
                    "strict_inward",
                    "exact_zero_multiplicity",
                    "unresolved",
                ]
            },
            "flux_range": reference("interval"),
            "time_derivative_jet": array(
                reference("interval"), minItems=1
            ),
            "time_derivative_jet_sha256": digest,
            "contact_multiplicity": nullable(
                {"type": "integer", "minimum": 2}
            ),
            "one_sided_behavior": {
                "enum": [
                    "inward_crossing",
                    "touch_or_plateau",
                    "unresolved",
                ]
            },
        }
    )
    defs["representative"] = obj(
        {
            "representative_id": string,
            "candidate_id": string,
            "box": reference("box"),
            "torus_image": integer_vector9,
            "log_unique": boolean,
            "s": vector9,
            "F": reference("interval"),
            "grad_sigma": array(
                reference("interval"), minItems=2, maxItems=2
            ),
            "dF_dt": reference("interval"),
            "H_sigma_sigma": array(
                array(reference("interval"), minItems=2, maxItems=2),
                minItems=2,
                maxItems=2,
            ),
            "geometry_certificate": reference("geometryCertificate"),
            "jet_normal": reference("jetNormal"),
        }
    )
    defs["implicitSet"] = obj(
        {
            "defining_equations": string_array,
            "candidate_ids": array(string, minItems=1, uniqueItems=True),
            "domain_boxes": array(reference("box"), minItems=1),
            "dimension_status": {"enum": ["positive", "unknown"]},
            "set_certificate_ref": string,
            "jet_field_certificate_ref": nullable(string),
            "normal_field_certificate_ref": nullable(string),
        }
    )
    defs["cluster"] = obj(
        {
            "representation": {"enum": ["singleton", "finite", "implicit"]},
            "complete": boolean,
            "unordered": {"const": True},
            "cardinality": {
                "anyOf": [
                    {"type": "integer", "minimum": 1},
                    {"enum": ["continuum", "unknown"]},
                ]
            },
            "members": array(reference("representative")),
            "member_hashes": array(digest),
            "members_sha256": digest,
            "implicit_set": nullable(reference("implicitSet")),
        }
    )
    defs["componentEvent"] = obj(
        {
            "component_id": string,
            "transition": {
                "enum": ["birth", "merge", "split", "disappear"]
            },
            "time": reference("interval"),
        }
    )
    defs["episode"] = obj(
        {
            "episode_id": string,
            "role": {"enum": ["preexisting", "primary", "subsequent"]},
            "left_censored": boolean,
            "right_censored": boolean,
            "complete": boolean,
            "T_in": nullable(reference("interval")),
            "T_out": nullable(reference("interval")),
            "secondary_inner_contacts": {"type": "integer", "minimum": 0},
            "component_events": array(reference("componentEvent")),
        }
    )

    defs["coverageImage"] = obj(
        {
            "image_id": string,
            "lattice_vector": integer_vector9,
            "physical_image_key": string,
            "seam_equivalence_key": string,
        }
    )
    defs["coverageDomain"] = obj(
        {
            "domain_id": string,
            "image_id": string,
            "root_node_id": string,
            "box": reference("exactBox"),
        }
    )
    defs["coverageNode"] = obj(
        {
            "node_id": string,
            "domain_id": string,
            "kind": {"enum": ["split", "leaf"]},
            "box": reference("exactBox"),
            "split_axis": nullable({"enum": ["sigma1", "sigma2", "time"]}),
            "split_value": nullable(reference("dyadic")),
            "children": array(string),
            "leaf_id": nullable(string),
        }
    )
    exact_vector3 = array(
        reference("dyadic"), minItems=3, maxItems=3
    )
    exact_matrix3 = array(
        exact_vector3, minItems=3, maxItems=3
    )
    defs["affineModel"] = obj(
        {
            "variable_order": {
                "const": ["sigma1", "sigma2", "time"]
            },
            "coefficients": exact_vector3,
            "constant": reference("dyadic"),
        }
    )
    defs["affineSystem"] = obj(
        {
            "kind": {"const": "exact_affine"},
            "variable_order": {
                "const": ["sigma1", "sigma2", "time"]
            },
            "matrix": exact_matrix3,
            "constant": exact_vector3,
            "root": exact_vector3,
        }
    )
    defs["separableQuadratic"] = obj(
        {
            "kind": {"const": "separable_quadratic"},
            "variable_order": {
                "const": ["sigma1", "sigma2", "time"]
            },
            "spatial_root": array(
                reference("dyadic"), minItems=2, maxItems=2
            ),
            "time_coefficients": exact_vector3,
            "time_isolating_interval": reference("exactInterval"),
            "endpoint_values": obj(
                {
                    "lo": reference("dyadic"),
                    "hi": reference("dyadic"),
                }
            ),
            "derivative_range": reference("exactInterval"),
        }
    )
    defs["rootModel"] = {
        "oneOf": [
            reference("affineSystem"),
            reference("separableQuadratic"),
        ]
    }
    defs["affineSet"] = obj(
        {
            "variable_order": {
                "const": ["sigma1", "sigma2", "time"]
            },
            "matrix": exact_matrix3,
            "constant": exact_vector3,
            "base_point": exact_vector3,
            "null_direction": exact_vector3,
            "parameter_interval": reference("exactInterval"),
            "declared_rank": {
                "type": "integer",
                "minimum": 0,
                "maximum": 2,
            },
            "declared_dimension": {
                "type": "integer",
                "minimum": 1,
                "maximum": 3,
            },
        }
    )
    exact_matrix9 = array(
        array(reference("dyadic"), minItems=9, maxItems=9),
        minItems=9,
        maxItems=9,
    )
    defs["registeredProblemModelContent"] = {
        "oneOf": [
            reference("rootModel"),
            reference("affineSet"),
            obj(
                {
                    "function_component": string,
                    "affine_model": reference("affineModel"),
                }
            ),
            obj({"equation_status": string}),
            obj(
                {
                    "observable": {"const": "rho=sqrt(2F_min)"},
                    "time_domain": {
                        "enum": [
                            "initial_time",
                            "registered-post-boundary-interval",
                            "all_real",
                        ]
                    },
                    "rho_affine": reference("rhoAffine"),
                }
            ),
        ]
    }
    defs["registeredProblemModel"] = obj(
        {
            "model_id": string,
            "model_kind": {
                "enum": [
                    "exclusion_affine",
                    "root_system",
                    "singular_root_system",
                    "unresolved_problem_partition",
                    "rho_affine",
                ]
            },
            "model": reference("registeredProblemModelContent"),
            "model_sha256": digest,
        }
    )
    defs["eventProofModel"] = obj(
        {
            "model_id": string,
            "model_kind": string,
            "content_sha256": digest,
        }
    )
    defs["eventProofModelRegistry"] = obj(
        {
            "schema_version": {
                "const": (
                    "cyz-brief-0018-event-proof-model-registry-v1"
                )
            },
            "models": array(reference("eventProofModel")),
        }
    )
    defs["problemCommitment"] = obj(
        {
            "schema_version": {
                "const": contract.coverage.PROBLEM_COMMITMENT_SCHEMA_VERSION
            },
            "authority_mode": {"const": "pinned_synthetic_fixture"},
            "fixture_registry_id": string,
            "equation_family": string,
            "equation_version": string,
            "source_state_registry": obj(
                {
                    "schema_version": string,
                    "initial_state": {"const": "armed"},
                    "initial_time": reference("dyadic"),
                    "initial_rho_affine": reference("rhoAffine"),
                }
            ),
            "source_state_sha256": digest,
            "source_registry": obj(
                {
                    "schema_version": string,
                    "registry_role": {
                        "const": "canonical-source-registry"
                    },
                    "preparation_name": string,
                    "source_draw_registry_sha256": digest,
                    "source_state_sha256": digest,
                    "validity_predicate_version": string,
                    "redraw_on_invalid": {"const": False},
                }
            ),
            "source_registry_sha256": digest,
            "source_draw_registry": obj(
                {
                    "schema_version": string,
                    "registry_role": {
                        "const": "source-substream-seed-input-only"
                    },
                    "L_A": reference("dyadic"),
                    "T_F": reference("dyadic"),
                    "L_w": reference("dyadic"),
                    "K": {"type": "integer", "minimum": 1},
                    "E_perp": reference("dyadic"),
                    "P_tot": array(
                        reference("dyadic"),
                        minItems=8,
                        maxItems=8,
                    ),
                    "pi_1": reference("dyadic"),
                    "pi_2": reference("dyadic"),
                    "prng": obj(
                        {
                            "algorithm": string,
                            "version": string,
                            "seed_convention": string,
                        }
                    ),
                }
            ),
            "source_draw_registry_sha256": digest,
            "solver_registry": obj(
                {
                    "schema_version": string,
                    "proof_backend": {
                        "const": "exact-synthetic-fixture"
                    },
                    "budget_semantics": {
                        "const": "deterministic-finite-fixture"
                    },
                    "rank_blind_selection": {"const": True},
                }
            ),
            "solver_registry_sha256": digest,
            "metric_registry": obj(
                {
                    "dimension": {"const": 9},
                    "basis": {
                        "const": "registered-target-coordinate-basis"
                    },
                    "matrix": exact_matrix9,
                }
            ),
            "metric_sha256": digest,
            "lattice_registry": obj(
                {
                    "dimension": {"const": 9},
                    "images": array(
                        reference("coverageImage"), minItems=1
                    ),
                }
            ),
            "lattice_sha256": digest,
            "threshold_registry": obj(
                {
                    "registry_id": string,
                    "r_in": reference("dyadic"),
                    "r_out": reference("dyadic"),
                    "injectivity_radius": reference("dyadic"),
                }
            ),
            "threshold_registry_sha256": digest,
            "observation_window": reference("exactInterval"),
            "observation_window_sha256": digest,
            "function_registry": obj(
                {
                    "schema_version": {
                        "const": (
                            contract.coverage.FUNCTION_REGISTRY_SCHEMA_VERSION
                        )
                    },
                    "models": array(
                        reference("registeredProblemModel"), minItems=1
                    ),
                }
            ),
            "function_registry_sha256": digest,
            "event_model_registry": reference(
                "eventProofModelRegistry"
            ),
            "event_model_registry_sha256": digest,
            "physical_replay_boundary": string,
        }
    )
    problem_reference_fields = {
        "problem_commitment_sha256": digest,
        "model_id": string,
        "model_sha256": digest,
    }
    defs["exclusionWitness"] = obj(
        {
            "type": {"const": "interval_exclusion"},
            "function_component": string,
            "affine_model": reference("affineModel"),
            "range": reference("exactInterval"),
            "backend": string,
            **problem_reference_fields,
        }
    )
    defs["uniqueWitness"] = obj(
        {
            "type": {"const": "interval_newton_inclusion"},
            "candidate_id": string,
            "operator_box": reference("exactBox"),
            "determinant_range": reference("exactInterval"),
            "root_model": reference("rootModel"),
            "backend": string,
            **problem_reference_fields,
        }
    )
    defs["singularWitness"] = obj(
        {
            "type": {"const": "singular_set_certificate"},
            "candidate_ids": array(string, minItems=1, uniqueItems=True),
            "affine_set": reference("affineSet"),
            "set_certificate_sha256": digest,
            "backend": string,
            **problem_reference_fields,
        }
    )
    defs["unresolvedWitness"] = obj(
        {
            "type": {"const": "unresolved"},
            "reason_code": string,
            "event_order_relevant": boolean,
            "backend": string,
            **problem_reference_fields,
        }
    )
    defs["coverageLeaf"] = obj(
        {
            "leaf_id": string,
            "node_id": string,
            "domain_id": string,
            "image_id": string,
            "classification": {
                "enum": [
                    "excluded",
                    "unique_root",
                    "certified_singular_cluster",
                    "unresolved",
                ]
            },
            "witness": {
                "oneOf": [
                    reference("exclusionWitness"),
                    reference("uniqueWitness"),
                    reference("singularWitness"),
                    reference("unresolvedWitness"),
                ]
            },
        }
    )
    defs["coverageCandidate"] = obj(
        {
            "candidate_id": string,
            "leaf_id": string,
            "image_id": string,
            "physical_root_id": string,
            "time_interval": reference("exactInterval"),
        }
    )
    defs["seamBinding"] = obj(
        {
            "candidate_id": string,
            "image_id": string,
            "lattice_delta": integer_vector9,
        }
    )
    defs["seamProof"] = obj(
        {
            "base_candidate_id": string,
            "lattice_delta_bindings": array(
                reference("seamBinding"), minItems=2
            ),
        }
    )
    defs["coverageQuotient"] = obj(
        {
            "physical_root_id": string,
            "candidate_ids": array(string, minItems=1, uniqueItems=True),
            "representative_candidate_id": string,
            "proof_type": {"enum": ["identity", "seam_equivalence"]},
            "seam_equivalence_key": string,
            "seam_proof": nullable(reference("seamProof")),
        }
    )
    defs["coverageManifest"] = obj(
        {
            "schema_version": {
                "const": coverage_schema_version()
            },
            "exact_inputs": obj(
                {
                    "coordinate_order": {
                        "const": ["sigma1", "sigma2", "time"]
                    },
                    "images": array(
                        reference("coverageImage"), minItems=1
                    ),
                    "initial_domains": array(
                        reference("coverageDomain"), minItems=1
                    ),
                    "problem_commitment": reference(
                        "problemCommitment"
                    ),
                    "problem_commitment_sha256": digest,
                }
            ),
            "exact_inputs_sha256": digest,
            "images": array(reference("coverageImage"), minItems=1),
            "initial_domains": array(
                reference("coverageDomain"), minItems=1
            ),
            "nodes": array(reference("coverageNode"), minItems=1),
            "leaves": array(reference("coverageLeaf"), minItems=1),
            "candidates": array(reference("coverageCandidate")),
            "quotient_classes": array(reference("coverageQuotient")),
        }
    )
    defs["coverageCertificate"] = obj(
        {
            "certificate_id": string,
            "manifest": reference("coverageManifest"),
            "manifest_sha256": digest,
            "leaf_counts": obj(
                {
                    "excluded": {"type": "integer", "minimum": 0},
                    "unique_root": {"type": "integer", "minimum": 0},
                    "certified_singular_cluster": {
                        "type": "integer",
                        "minimum": 0,
                    },
                    "unresolved": {"type": "integer", "minimum": 0},
                }
            ),
            "node_count": {"type": "integer", "minimum": 1},
            "image_count": {"type": "integer", "minimum": 1},
            "domain_count": {"type": "integer", "minimum": 1},
            "candidate_count": {"type": "integer", "minimum": 0},
            "physical_root_count": {"type": "integer", "minimum": 0},
        }
    )

    # Cross-field proof replay remains in event_contract.py; these definitions
    # make every serialized field explicit and reject structural substitutions.
    defs["sourceValidity"] = obj(
        {
            "certificate_id": string,
            "status": {"enum": ["valid", "invalid"]},
            "predicate_version": string,
            "reason_codes": string_array,
        }
    )
    defs["globalMinimum"] = obj(
        {
            "certificate_id": string,
            "coverage_manifest_sha256": digest,
            "earliest_time": reference("dyadic"),
            "candidate_ids": array(string, uniqueItems=True),
            "minimizer_candidate_ids": array(string, uniqueItems=True),
            "candidate_time_bindings": array(
                obj(
                    {
                        "candidate_id": string,
                        "time_interval_sha256": digest,
                    }
                )
            ),
            "excluded_leaf_ids": array(string, uniqueItems=True),
        }
    )
    defs["noEarlier"] = obj(
        {
            "certificate_id": string,
            "coverage_manifest_sha256": digest,
            "earliest_time": reference("dyadic"),
            "candidate_ids": array(string, uniqueItems=True),
            "excluded_before_leaf_ids": array(string, uniqueItems=True),
            "history_interval": reference("exactInterval"),
            "initial_rho_lower_bound": reference("dyadic"),
            "r_in": reference("dyadic"),
            "hysteresis_registry_id": string,
            "initial_armed_witness": obj(
                {
                    "observable": {"const": "rho=sqrt(2F_min)"},
                    "time": reference("dyadic"),
                    "rho_affine": reference("rhoAffine"),
                    "rho_range": reference("exactInterval"),
                    "backend": string,
                    **problem_reference_fields,
                }
            ),
        }
    )
    defs["torus"] = obj(
        {
            "certificate_id": string,
            "unique": boolean,
            "image_manifest_hash": digest,
        }
    )
    defs["equalTimeBinding"] = obj(
        {
            "candidate_id": string,
            "representative_id": string,
            "member_time_sha256": digest,
            "candidate_time_sha256": digest,
        }
    )
    defs["equalTimeProof"] = obj(
        {
            "exact_time": reference("dyadic"),
            "bindings": array(
                reference("equalTimeBinding"), minItems=1
            ),
        }
    )
    defs["orderingInterval"] = obj(
        {
            "candidate_id": string,
            "time_interval": reference("exactInterval"),
        }
    )
    defs["orderingProof"] = obj(
        {
            "candidate_intervals": array(
                reference("orderingInterval"), minItems=2
            ),
            "all_candidates_isolated": {"const": True},
            "only_remaining_uncertainty": {
                "const": "earliest_order"
            },
        }
    )
    defs["tie"] = obj(
        {
            "certificate_id": string,
            "status": {
                "enum": ["none", "complete_cluster", "ordering_ambiguous"]
            },
            "candidate_ids": array(string, uniqueItems=True),
            "equal_time_proof": nullable(reference("equalTimeProof")),
            "ordering_proof": nullable(reference("orderingProof")),
        }
    )
    defs["rhoAffine"] = obj(
        {
            "slope": reference("dyadic"),
            "intercept": reference("dyadic"),
        }
    )
    defs["postBoundaryWitness"] = obj(
        {
            "observable": {"const": "rho=sqrt(2F_min)"},
            "exact_time_interval": reference("exactInterval"),
            "time_interval_sha256": digest,
            "rho_affine": reference("rhoAffine"),
            "rho_range": reference("exactInterval"),
            "backend": string,
            **problem_reference_fields,
        }
    )
    defs["outer"] = obj(
        {
            "certificate_id": string,
            "observed": boolean,
            "grazing_touch_count": {
                "type": "integer",
                "minimum": 0,
            },
            "strict_overshoot": boolean,
            "boundary_time": nullable(reference("interval")),
            "post_boundary_interval": nullable(reference("interval")),
            "post_boundary_witness": nullable(
                reference("postBoundaryWitness")
            ),
            "rho_lower_bound": nullable(number),
            "r_out": nullable(number),
            "hysteresis_registry_id": string,
            "global_minimum_certificate_id": nullable(string),
            "coverage_manifest_sha256": nullable(digest),
            "image_manifest_sha256": nullable(digest),
            "rearmed": boolean,
        }
    )
    defs["finiteWindowProof"] = obj(
        {
            "t0": reference("dyadic"),
            "t1": reference("dyadic"),
            "excluded_leaf_ids": array(string, uniqueItems=True),
        }
    )
    exact_vector8 = array(
        reference("dyadic"), minItems=8, maxItems=8
    )
    integer_vector8 = array(integer, minItems=8, maxItems=8)
    defs["timeSeamCover"] = obj(
        {
            "t0": reference("dyadic"),
            "tP": reference("dyadic"),
            "lattice_vector": integer_vector8,
            "state_t0": exact_vector8,
            "state_tP": exact_vector8,
            "wrapped_state_t0": exact_vector8,
            "wrapped_state_tP": exact_vector8,
            "coverage_manifest_sha256": digest,
        }
    )
    defs["recurrenceProof"] = obj(
        {
            "m": {"type": "integer", "minimum": 1},
            "L_w": reference("dyadic"),
            "P": reference("dyadic"),
            "relative_velocity": exact_vector8,
            "transverse_periods": exact_vector8,
            "lattice_vector": integer_vector8,
            "time_seam_cover": reference("timeSeamCover"),
            "backend": string,
            "problem_commitment_sha256": digest,
        }
    )
    defs["globalLowerBoundProof"] = obj(
        {
            "observable": {"const": "rho=sqrt(2F_min)"},
            "time_domain": {"const": "all_real"},
            "rho_affine": reference("rhoAffine"),
            "rho_lower_bound": reference("dyadic"),
            "r_in": reference("dyadic"),
            "witness_range": reference("exactInterval"),
            "backend": string,
            **problem_reference_fields,
        }
    )
    defs["noEntry"] = obj(
        {
            "certificate_id": string,
            "mode": {
                "enum": [
                    "finite_window",
                    "exact_common_period",
                    "global_lower_bound",
                ]
            },
            "coverage_manifest_sha256": digest,
            "finite_window": nullable(reference("finiteWindowProof")),
            "recurrence": nullable(reference("recurrenceProof")),
            "global_lower_bound": nullable(
                reference("globalLowerBoundProof")
            ),
        }
    )
    defs["unresolved"] = obj(
        {
            "certificate_id": string,
            "coverage_manifest_sha256": digest,
            "reason_codes": array(string, minItems=1),
            "unresolved_leaf_ids": array(string, minItems=1, uniqueItems=True),
        }
    )
    defs["closest"] = obj(
        {
            "certificate_id": string,
            "status": {
                "enum": [
                    "none",
                    "episode_complete",
                    "window_only",
                    "unresolved",
                ]
            },
            "time": nullable(reference("interval")),
            "episode_id": nullable(string),
            "coverage_manifest_sha256": nullable(digest),
            "global_minimum_certificate_id": nullable(string),
        }
    )
    defs["proofProvenance"] = obj(
        {
            "proof_id": string,
            "backend": string,
            "problem_commitment_sha256": nullable(digest),
            "proof_content_sha256": digest,
        }
    )

    flag_properties = {name: boolean for name in contract.FLAG_NAMES}
    certificates = obj(
        {
            "source_validity": nullable(reference("sourceValidity")),
            "root_coverage": nullable(reference("coverageCertificate")),
            "global_minimum": nullable(reference("globalMinimum")),
            "no_earlier_entry": nullable(reference("noEarlier")),
            "torus_log": nullable(reference("torus")),
            "tie": nullable(reference("tie")),
            "outer_exit": nullable(reference("outer")),
            "no_entry": nullable(reference("noEntry")),
            "unresolved": nullable(reference("unresolved")),
            "closest": nullable(reference("closest")),
        }
    )
    root_properties = {
        "schema_version": {"const": contract.EVENT_SCHEMA_VERSION},
        "registry_hash": digest,
        "sample_id": string,
        "source": obj(
            {
                "sampling_registry_hash": digest,
                "classification_registry_hash": digest,
                "source_valid": boolean,
                "history_valid": boolean,
                "invalid_reasons": string_array,
                "initial_state": {"enum": ["armed", "active", "unknown"]},
            }
        ),
        "observation": obj(
            {
                "t0": number,
                "t1": number,
                "window_semantics": {"const": "[t0,t1)"},
                "complete_time_domain": boolean,
                "continuation_state": {
                    "enum": [
                        "armed",
                        "active",
                        "terminal",
                        "invalid",
                        "unresolved",
                    ]
                },
            }
        ),
        "primary_outcome": {"enum": list(contract.PRIMARY_PRECEDENCE)},
        "flags": obj(flag_properties),
        "entry_cluster": nullable(reference("cluster")),
        "episodes": array(reference("episode")),
        "certificates": certificates,
        "precedence_trace": array(
            {"enum": list(contract.PRIMARY_PRECEDENCE)}
        ),
        "scope": obj(
            {
                "record_kind": {
                    "enum": ["synthetic_control", "certified_solver_output"]
                },
                "physical_root_solver_run": boolean,
                "proof_backend": string,
                "solver_run_manifest": nullable(
                    obj(
                        {
                            "run_id": string,
                            "backend": string,
                            "executable_sha256": digest,
                            "input_manifest_sha256": digest,
                            "coverage_manifest_sha256": digest,
                            "proof_artifact_sha256": digest,
                            "problem_commitment_sha256": digest,
                            "source_state_sha256": digest,
                            "source_registry_sha256": digest,
                            "source_draw_registry_sha256": digest,
                            "source_validity_sha256": digest,
                            "solver_registry_sha256": digest,
                            "independent_replayer": string,
                        }
                    )
                ),
                "solver_run_manifest_sha256": nullable(digest),
                "problem_commitment_sha256": nullable(digest),
                "source_state_sha256": nullable(digest),
                "source_registry_sha256": nullable(digest),
                "source_draw_registry_sha256": nullable(digest),
                "source_validity": obj(
                    {
                        "certificate_id": string,
                        "predicate_version": string,
                        "status": {"enum": ["valid", "invalid"]},
                        "source_valid": boolean,
                        "history_valid": boolean,
                        "initial_state": {
                            "enum": ["armed", "active", "unknown"]
                        },
                        "invalid_reasons": string_array,
                    }
                ),
                "source_validity_sha256": digest,
                "solver_registry_sha256": nullable(digest),
                "event_model_registry": reference(
                    "eventProofModelRegistry"
                ),
                "event_model_registry_sha256": digest,
                "proof_provenance": array(
                    reference("proofProvenance")
                ),
                "proof_provenance_sha256": digest,
                "replay_authority": {
                    "enum": [
                        "builtin-pinned-synthetic-fixture",
                        "external-0019-independent-replay-required",
                    ]
                },
                "independent_replayer": string,
                "authoritative_physical_certificate": {
                    "const": False
                },
                "physical_outcome_mass_estimated": boolean,
                "rank_used_for_event_selection": boolean,
            }
        ),
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://example.invalid/cyz/brief-0018/event-record-v2.schema.json",
        "title": "Brief 0018 total event record v2",
        "description": (
            "Strict structural schema; event_contract.py replays all exact "
            "proof bindings and outcome semantics."
        ),
        **obj(root_properties),
        "$defs": defs,
    }


def coverage_schema_version() -> str:
    import coverage_proof

    return coverage_proof.COVERAGE_SCHEMA_VERSION


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent
        / "event_record.schema.json",
    )
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    text = json.dumps(
        build_schema(),
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ) + "\n"
    if arguments.check:
        if not arguments.output.exists():
            raise SystemExit(f"missing schema: {arguments.output}")
        existing = arguments.output.read_text(
            encoding="utf-8", errors="strict"
        ).replace("\r\n", "\n")
        if existing != text:
            raise SystemExit("schema regeneration mismatch")
        print(f"PASS: verified {arguments.output}")
    else:
        arguments.output.write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
