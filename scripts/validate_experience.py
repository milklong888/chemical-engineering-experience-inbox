"""Validate a sanitized temporary-inbox submission; never execute, upload or promote.

The observation argument is a caller-owned trust boundary, not a signature.
Never pass contributor-supplied observations to validate_submission as trusted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA = "experience-inbox-submission-v1"
OBSERVATION_SCHEMA = "experience-inbox-observation-v1"
MAX_BYTES = 100_000
TOP_KEYS = {"schema", "item_id", "revision", "channel", "content", "content_sha256",
            "contributor", "publish", "provenance", "source", "claim", "events", "synthetic"}
CONTENT_KEYS = {"title", "trigger", "method", "limits", "evidence_summary", "counterexamples"}
STAGES = {
    "code_behavior": "offline_code_executed",
    "deterministic_calculation": "headless_calculation_executed",
    "aspen_simulation_clean": "aspen_solver_clean_verified",
    "aspen_engineering_accepted": "engineering_acceptance_verified",
    "native_tool_executed": "native_object_executed_verified",
}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
COMMIT = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SENSITIVE = re.compile(
    r"(?:[A-Za-z]:[\\/]|\\\\[^\s]+|/(?:Users|home|etc|mnt)/|"
    r"\b(?:gh[pousr]_[A-Za-z0-9]{12,}|github_pat_[A-Za-z0-9_]{12,}|"
    r"sk-[A-Za-z0-9_-]{16,}|AKIA[A-Z0-9]{16})|"
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|"
    r"\b(?:password|api[_-]?key|access[_-]?token)\s*[:=]\s*\S+)", re.I)


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def _strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path: Path) -> dict:
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("JSON input exceeds 100000 bytes")
    value = json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=_strict_object,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError("Non-finite JSON number")))
    if not isinstance(value, dict):
        raise ValueError("JSON input must be an object")
    return value


def _date(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result.astimezone(timezone.utc) if result.tzinfo else None
    except ValueError:
        return None


def _validate_submission(submission: object, *, observation: dict | None = None,
                        now: datetime | None = None, allow_synthetic: bool = False) -> dict:
    """Inspect declarations against separately acquired observations.

    Only trusted maintainer code may provide observation. A copied local JSON
    file is not cryptographically authenticated. allow_synthetic is for tests
    only, never a public-submission admission mode.
    """
    problems: list[dict] = []

    def issue(level, code):
        if {"level": level, "code": code} not in problems:
            problems.append({"level": level, "code": code})

    def object_fields(value, fields, label):
        if not isinstance(value, dict) or set(value) != fields:
            issue("reject", label + "_FIELDS_INVALID")
            return {}
        return value

    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must have a timezone")
    result = {"schema": "experience-inbox-decision-v1", "status": "rejected",
              "reasons": problems, "inbox_eligible": False, "canonical_eligible": False,
              "default_retrieval_eligible": False, "technical_generalization_verified": False,
              "assurance": "no_external_observation", "scope": "temporary_sanitized_inbox_only"}
    if not isinstance(submission, dict):
        issue("reject", "SUBMISSION_OBJECT_REQUIRED")
        return result
    try:
        raw_size = len(json.dumps(submission, ensure_ascii=False, allow_nan=False).encode("utf-8"))
        result["submission_sha256"] = digest(submission)
    except (TypeError, ValueError, RecursionError):
        issue("reject", "JSON_VALUE_INVALID")
        return result
    if raw_size > MAX_BYTES:
        issue("reject", "SUBMISSION_TOO_LARGE")
    if set(submission) != TOP_KEYS or submission.get("schema") != SCHEMA:
        issue("reject", "SUBMISSION_FIELDS_OR_SCHEMA_INVALID")
    item, revision = submission.get("item_id"), submission.get("revision")
    if not isinstance(item, str) or not IDENTIFIER.fullmatch(item):
        issue("reject", "ITEM_ID_INVALID")
    if type(revision) is not int or revision < 1:
        issue("reject", "REVISION_INVALID")
    channel = submission.get("channel")
    if channel not in {"executed_success", "thought_principle"}:
        issue("reject", "CHANNEL_INVALID")
    if type(submission.get("synthetic")) is not bool:
        issue("reject", "SYNTHETIC_FLAG_REQUIRED")
    if submission.get("synthetic") is True and not allow_synthetic:
        issue("pending", "SYNTHETIC_FIXTURE_NOT_REAL_EXPERIENCE")
    content = object_fields(submission.get("content"), CONTENT_KEYS, "CONTENT")
    for key, value in content.items():
        if not isinstance(value, str) or not value.strip() or len(value) > (200 if key == "title" else 4000):
            issue("reject", "CONTENT_TEXT_INVALID")
        elif SENSITIVE.search(value):
            issue("reject", "POSSIBLE_PRIVATE_DATA_IN_PUBLIC_TEXT")
    content_hash = digest(content)
    if submission.get("content_sha256") != content_hash:
        issue("reject", "CONTENT_HASH_MISMATCH")
    contributor = object_fields(submission.get("contributor"), {"id"}, "CONTRIBUTOR")
    contributor_id = contributor.get("id")
    if not isinstance(contributor_id, str) or not IDENTIFIER.fullmatch(contributor_id):
        issue("reject", "CONTRIBUTOR_ID_INVALID")
    publish = object_fields(submission.get("publish"), {"opt_in", "scope", "license", "event_id",
        "content_sha256", "revoked"}, "PUBLISH")
    if publish.get("opt_in") is not True or publish.get("revoked") is not False:
        issue("reject", "PUBLIC_OPT_IN_MISSING_OR_REVOKED")
    if publish.get("scope") != "sanitized_method_summary" or publish.get("license") != "CC-BY-4.0":
        issue("reject", "PUBLIC_SCOPE_OR_LICENSE_INVALID")
    if publish.get("content_sha256") != content_hash or not isinstance(publish.get("event_id"), str) or not IDENTIFIER.fullmatch(publish.get("event_id", "")):
        issue("reject", "PUBLIC_AUTHORIZATION_CONTENT_BINDING_INVALID")
    lineage = object_fields(submission.get("provenance"), {"state", "ancestry_complete", "ancestor_states"}, "PROVENANCE")
    states = lineage.get("ancestor_states")
    if not isinstance(states, list) or not states or not all(isinstance(s, str) for s in states):
        issue("quarantine", "ANCESTRY_MISSING_OR_INVALID")
        states = []
    if lineage.get("ancestry_complete") is not True or any(s not in {"strict_verified", "source_verified"} for s in states + [lineage.get("state")]):
        issue("quarantine", "RELAXED_UNKNOWN_OR_INCOMPLETE_LINEAGE")
    source = object_fields(submission.get("source"), {"repository", "commit", "skill_version"}, "SOURCE")
    has_git_source = not (channel == "thought_principle" and source and all(value is None for value in source.values()))
    if has_git_source:
        if not isinstance(source.get("repository"), str) or not REPOSITORY.fullmatch(source.get("repository", "")) or ".." in source.get("repository", ""):
            issue("reject", "PUBLIC_REPOSITORY_ID_INVALID")
        if not isinstance(source.get("commit"), str) or not COMMIT.fullmatch(source.get("commit", "")):
            issue("reject", "SOURCE_COMMIT_INVALID")
        if not isinstance(source.get("skill_version"), str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.+_-]{0,59}", source.get("skill_version", "")):
            issue("reject", "SKILL_VERSION_INVALID")
    claim = object_fields(submission.get("claim"), {"kind", "tested_commit", "source_digest",
        "evidence_digest", "check_name", "run_id"}, "CLAIM")
    if claim.get("tested_commit") != source.get("commit"):
        issue("reject", "DECLARED_TESTED_COMMIT_MISMATCH")
    for key in ("source_digest", "evidence_digest"):
        if not isinstance(claim.get(key), str) or not SHA256.fullmatch(claim.get(key, "")):
            issue("reject", "CLAIM_DIGEST_INVALID")
    for key in ("check_name", "run_id"):
        if channel == "thought_principle":
            if claim.get(key) is not None:
                issue("reject", "THOUGHT_CHECK_IDENTIFIERS_MUST_BE_NULL")
        elif not isinstance(claim.get(key), str) or not IDENTIFIER.fullmatch(claim.get(key, "")):
            issue("reject", "CLAIM_CHECK_ID_INVALID")
    if channel == "executed_success" and claim.get("kind") not in STAGES:
        issue("reject", "EXECUTED_CLAIM_KIND_INVALID")
    if channel == "thought_principle" and claim.get("kind") != "behavioral_principle":
        issue("reject", "THOUGHT_CHANNEL_CANNOT_DECLARE_TECHNICAL_SUCCESS")
    events = submission.get("events")
    if not isinstance(events, list) or len(events) > 20:
        issue("reject", "EVENT_LIST_INVALID")
        events = []
    seen_ids, parsed_events = set(), []
    for event in events:
        event = object_fields(event, {"id", "type", "actor_id", "actor_role", "item_id", "revision",
            "content_sha256", "occurred_at", "decision", "source_digest"}, "EVENT")
        if not event:
            continue
        for key in ("id", "actor_id"):
            if not isinstance(event.get(key), str) or not IDENTIFIER.fullmatch(event.get(key, "")):
                issue("reject", "EVENT_ID_INVALID")
        if event.get("id") in seen_ids:
            issue("reject", "DUPLICATE_EVENT_ID")
        seen_ids.add(event.get("id"))
        if event.get("content_sha256") != content_hash or event.get("item_id") != item or event.get("revision") != revision:
            issue("reject", "EVENT_CONTENT_OR_REVISION_MISMATCH")
        if not isinstance(event.get("source_digest"), str) or not SHA256.fullmatch(event.get("source_digest", "")):
            issue("reject", "EVENT_SOURCE_DIGEST_INVALID")
        when = _date(event.get("occurred_at"))
        if when is None or when > now:
            issue("reject", "EVENT_TIME_INVALID")
        parsed_events.append((event, when))
    if channel == "executed_success" and events:
        issue("reject", "EXECUTED_CHANNEL_EVENTS_MUST_BE_EMPTY")
    if channel == "thought_principle":
        if len(parsed_events) != 2:
            issue("pending", "CURRENT_USER_CONFIRMATION_AND_ASSISTANT_REVIEW_REQUIRED")
        else:
            (confirmed, first_time), (reviewed, second_time) = parsed_events
            if (confirmed.get("type"), confirmed.get("actor_role"), confirmed.get("decision")) != ("user_confirmation", "user", "confirm") or confirmed.get("actor_id") != contributor_id:
                issue("reject", "EXPLICIT_CONTRIBUTOR_CONFIRMATION_REQUIRED")
            if (reviewed.get("type"), reviewed.get("actor_role"), reviewed.get("decision")) != ("assistant_review", "assistant", "approve"):
                issue("reject", "ASSISTANT_REVIEW_APPROVAL_REQUIRED")
            if reviewed.get("actor_id") == confirmed.get("actor_id"):
                issue("reject", "REVIEWER_IDENTITY_NOT_DISTINCT")
            if first_time is None or second_time is None or second_time <= first_time:
                issue("reject", "CONFIRMATION_MUST_PRECEDE_REVIEW")
            if claim.get("source_digest") != confirmed.get("source_digest") or claim.get("evidence_digest") != digest(events):
                issue("reject", "THOUGHT_SOURCE_AND_REVIEW_DIGEST_BINDING_INVALID")

    if observation is None:
        issue("pending", "TRUSTED_EXTERNAL_OBSERVATION_REQUIRED")
    elif not isinstance(observation, dict):
        issue("reject", "OBSERVATION_OBJECT_INVALID")
    else:
        result["assurance"] = "caller_supplied_trusted_observation_not_cryptographic_identity"
        if observation.get("schema") != OBSERVATION_SCHEMA or observation.get("submission_sha256") != result.get("submission_sha256"):
            issue("reject", "OBSERVATION_SUBMISSION_BINDING_MISMATCH")
        if observation.get("synthetic") is True and not allow_synthetic:
            issue("pending", "SYNTHETIC_OBSERVATION_NOT_REAL_VERIFICATION")
        if type(observation.get("synthetic")) is not bool:
            issue("pending", "OBSERVATION_FIXTURE_CLASSIFICATION_REQUIRED")
        observed, expires = _date(observation.get("observed_at")), _date(observation.get("expires_at"))
        if observed is None or expires is None or not observed <= now <= expires or not timedelta(0) < expires - observed <= timedelta(hours=24):
            issue("pending", "OBSERVATION_STALE_OR_TIME_INVALID")
        if observed is not None and any(when is not None and when > observed for _, when in parsed_events):
            issue("pending", "OBSERVATION_PREDATES_CONFIRMATION_OR_REVIEW")
        if not isinstance(observation.get("observer_id"), str) or not observation["observer_id"].strip():
            issue("pending", "EXTERNAL_OBSERVER_ID_REQUIRED")
        auth = observation.get("authorization", {})
        if not isinstance(auth, dict):
            auth = {}
        if auth.get("revoked") is True:
            issue("reject", "OBSERVED_PUBLIC_OPT_IN_REVOKED")
        if any(auth.get(key) != expected for key, expected in {
            "contributor_id": contributor_id, "event_id": publish.get("event_id"),
            "content_sha256": content_hash, "explicit_opt_in": True,
            "authorized_to_share": True, "revoked": False}.items()):
            issue("pending", "CONTRIBUTOR_PUBLIC_AUTHORITY_NOT_EXTERNALLY_VERIFIED")
        privacy = observation.get("public_review", {})
        if not isinstance(privacy, dict) or any(privacy.get(key) != expected for key, expected in {
            "content_sha256": content_hash, "decision": "approved", "sanitized_method_only": True,
            "no_private_information": True, "rights_verified": True}.items()) or not privacy.get("reviewer_id"):
            issue("pending", "CONTENT_BOUND_PUBLIC_REVIEW_REQUIRED")
        observed_lineage = observation.get("lineage", {})
        if not isinstance(observed_lineage, dict) or observed_lineage.get("verified") is not True or observed_lineage.get("declaration_sha256") != digest(lineage):
            issue("pending", "COMPLETE_LINEAGE_NOT_EXTERNALLY_VERIFIED")
        elif observed_lineage.get("relaxation_found") is not False or observed_lineage.get("unknown_ancestor_found") is not False:
            issue("quarantine", "OBSERVED_EXCLUDED_OR_UNKNOWN_LINEAGE")
        if has_git_source:
            git = observation.get("git", {})
            if not isinstance(git, dict) or any(git.get(key) != expected for key, expected in {
                "repository": source.get("repository"), "commit": source.get("commit"),
                "commit_exists": True, "repository_public": True, "version_matches_commit": True}.items()):
                issue("pending", "EXACT_PUBLIC_GIT_VERSION_NOT_EXTERNALLY_VERIFIED")
        journal = observation.get("journal", {})
        if not isinstance(journal, dict) or any(journal.get(key) != expected for key, expected in {
            "item_id": item, "revision": revision, "content_sha256": content_hash}.items()):
            issue("pending", "EXTERNAL_REPLAY_JOURNAL_REQUIRED")
            journal = {}
        if journal.get("status") not in {"new", "identical_seen", "revision_conflict"}:
            issue("pending", "EXTERNAL_REPLAY_JOURNAL_REQUIRED")
        if journal.get("status") == "revision_conflict":
            issue("reject", "REVISION_REPLAY_CONTENT_CONFLICT")
        if channel == "executed_success":
            check = observation.get("execution", {})
            if not isinstance(check, dict):
                check = {}
            expected = {"repository": source.get("repository"), "head_sha": claim.get("tested_commit"),
                "source_digest": claim.get("source_digest"), "evidence_digest": claim.get("evidence_digest"),
                "name": claim.get("check_name"), "run_id": claim.get("run_id"), "claim_kind": claim.get("kind"),
                "execution_stage": STAGES.get(claim.get("kind")), "conclusion": "success",
                "scope_verified": True, "oracle_replayed": True, "contradictions": []}
            if any(check.get(key) != value for key, value in expected.items()) or not check.get("oracle_id"):
                issue("pending", "RELEVANT_EXECUTION_EVIDENCE_NOT_VERIFIED")
            if check.get("conclusion") in {"failure", "cancelled", "timed_out"} or check.get("contradictions"):
                issue("reject", "EXECUTION_FAILURE_OR_CONTRADICTORY_EVIDENCE")
            if claim.get("kind") == "native_tool_executed" and check.get("native_object_executed") is not True:
                issue("pending", "NATIVE_OBJECT_EXECUTION_NOT_VERIFIED")
        elif channel == "thought_principle":
            principle = observation.get("principle_review", {})
            reviewer = parsed_events[1][0].get("actor_id") if len(parsed_events) == 2 else None
            if not isinstance(principle, dict) or any(principle.get(key) != expected for key, expected in {
                "content_sha256": content_hash, "behavioral_principle_only": True,
                "technical_claims_present": False, "reviewer_id": reviewer}.items()) or reviewer is None:
                issue("pending", "BEHAVIORAL_SCOPE_REVIEW_REQUIRED")
            event_observations = observation.get("events")
            if not isinstance(event_observations, list) or len(event_observations) != len(events) or not events:
                issue("pending", "CONFIRMATION_REVIEW_EVENTS_NOT_EXTERNALLY_VERIFIED")
            else:
                for event, proof in zip(events, event_observations):
                    if not isinstance(proof, dict) or proof.get("event_sha256") != digest(event) or proof.get("source_authentic") is not True or proof.get("actor_id") != event.get("actor_id"):
                        issue("pending", "CONFIRMATION_REVIEW_EVENTS_NOT_EXTERNALLY_VERIFIED")
    if any(p["level"] == "reject" for p in problems):
        result["status"] = "rejected"
    elif any(p["level"] == "quarantine" for p in problems):
        result["status"] = "quarantined_local_audit_only"
    elif problems:
        result["status"] = "pending_verification"
    elif observation and observation.get("journal", {}).get("status") == "identical_seen":
        result["status"] = "already_in_inbox"
    else:
        result.update(status="ready_for_inbox", inbox_eligible=True)
    return result


def validate_submission(submission: object, *, observation: dict | None = None,
                        now: datetime | None = None, allow_synthetic: bool = False) -> dict:
    """Fail closed on malformed nested JSON, including invalid container types."""
    try:
        return _validate_submission(submission, observation=observation, now=now,
                                    allow_synthetic=allow_synthetic)
    except (TypeError, ValueError, RecursionError):
        return {"schema": "experience-inbox-decision-v1", "status": "rejected",
            "reasons": [{"level": "reject", "code": "MALFORMED_FIELD_TYPE_OR_VALUE"}],
            "inbox_eligible": False, "canonical_eligible": False,
            "default_retrieval_eligible": False, "technical_generalization_verified": False,
            "assurance": "invalid_input", "scope": "temporary_sanitized_inbox_only"}


def public_export(submission: dict, decision: dict) -> dict:
    """Explicit export projection. Private observations and artifacts are excluded."""
    if decision.get("status") != "ready_for_inbox" or decision.get("submission_sha256") != digest(submission):
        raise ValueError("Current submission has no valid inbox admission decision")
    return {"schema": "experience-inbox-public-record-v1", "item_id": submission["item_id"],
        "revision": submission["revision"], "channel": submission["channel"],
        "content": {key: submission["content"][key] for key in sorted(CONTENT_KEYS)},
        "content_sha256": submission["content_sha256"], "contributor": submission["contributor"]["id"],
        "license": submission["publish"]["license"], "source": dict(submission["source"]),
        "claim": dict(submission["claim"]), "submission_sha256": decision["submission_sha256"],
        "status": "temporary_inbox", "canonical_eligible": False, "default_retrieval_eligible": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("submission", type=Path)
    parser.add_argument("--observation", type=Path, help="Maintainer-observed receipt outside submission repository")
    parser.add_argument("--submission-root", type=Path, help="Required with observation: untrusted repository boundary")
    parser.add_argument("--acknowledge-local-observer-trust", action="store_true",
        help="Caller confirms this is independently obtained evidence, not a submitted receipt; not a signature")
    args = parser.parse_args()
    try:
        observation = None
        if args.observation:
            if not args.submission_root or not args.acknowledge_local_observer_trust:
                raise ValueError("Observation needs explicit trust acknowledgement and submission root")
            root, receipt = args.submission_root.resolve(strict=True), args.observation.resolve(strict=True)
            submitted_file = args.submission.resolve(strict=True)
            if not submitted_file.is_relative_to(root):
                raise ValueError("Submission must be within the declared submission root")
            if receipt.is_relative_to(root):
                raise ValueError("Observation must be outside the untrusted submission repository")
            observation = read_json(receipt)
        result = validate_submission(read_json(args.submission), observation=observation)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] in {"ready_for_inbox", "already_in_inbox"} else 2
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(json.dumps({"status": "invalid_input", "error": str(exc), "inbox_eligible": False,
            "canonical_eligible": False, "default_retrieval_eligible": False}, ensure_ascii=False))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
