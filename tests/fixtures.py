"""Synthetic governance fixtures, never evidence of Aspen or engineering success."""
from copy import deepcopy
from datetime import datetime, timezone
from scripts.validate_experience import digest

NOW = datetime(2026, 9, 12, 12, 0, tzinfo=timezone.utc)


def sample(channel="executed_success"):
    content = {"title": "Synthetic bounded method example", "trigger": "A parser input changes.",
        "method": "Compare source-bound outputs with an independent fixture oracle.",
        "limits": "Only the tested code behavior; no simulation or engineering conclusion.",
        "evidence_summary": "Synthetic demonstration of an admission shape, no actual run.",
        "counterexamples": "A green unrelated job and an old tested commit do not qualify."}
    value = {"schema": "experience-inbox-submission-v1", "item_id": "synthetic-example-001",
        "revision": 1, "channel": channel, "content": content, "content_sha256": digest(content),
        "contributor": {"id": "synthetic-contributor"}, "publish": {"opt_in": True,
            "scope": "sanitized_method_summary", "license": "CC-BY-4.0", "event_id": "synthetic-opt-in",
            "content_sha256": digest(content), "revoked": False},
        "provenance": {"state": "strict_verified", "ancestry_complete": True,
            "ancestor_states": ["source_verified", "strict_verified"]},
        "source": {"repository": "example/synthetic-methods", "commit": "a" * 40, "skill_version": "0.4.4"},
        "claim": {"kind": "code_behavior", "tested_commit": "a" * 40,
            "source_digest": "b" * 64, "evidence_digest": "c" * 64,
            "check_name": "synthetic-independent-oracle", "run_id": "synthetic-run-1"},
        "events": [], "synthetic": True}
    if channel == "thought_principle":
        value["claim"]["kind"] = "behavioral_principle"
        value["source"] = {"repository": None, "commit": None, "skill_version": None}
        value["claim"].update(tested_commit=None, check_name=None, run_id=None, source_digest="d" * 64)
        value["content"].update(title="Synthetic principle confirmation example",
            method="Review applicability before treating a preference as a general principle.",
            limits="Behavioral proposal only; no numerical or engineering result is asserted.")
        value["content_sha256"] = digest(value["content"])
        value["publish"]["content_sha256"] = value["content_sha256"]
        for name, role, actor, decision, minute in (
            ("user_confirmation", "user", "synthetic-contributor", "confirm", "10"),
            ("assistant_review", "assistant", "synthetic-reviewer", "approve", "20")):
            value["events"].append({"id": "synthetic-" + name, "type": name, "actor_id": actor,
                "actor_role": role, "item_id": value["item_id"], "revision": 1,
                "content_sha256": value["content_sha256"], "occurred_at": f"2026-09-12T11:{minute}:00Z",
                "decision": decision, "source_digest": "d" * 64})
        value["claim"]["evidence_digest"] = digest(value["events"])
    return value


def observation_for(submission):
    """Test-only stand-in for a separately acquired maintainer observation."""
    source, claim, content_hash = submission["source"], submission["claim"], submission["content_sha256"]
    observation = {"schema": "experience-inbox-observation-v1", "submission_sha256": digest(submission),
        "observer_id": "synthetic-maintainer", "synthetic": True,
        "observed_at": "2026-09-12T11:30:00Z", "expires_at": "2026-09-12T12:30:00Z",
        "authorization": {"contributor_id": submission["contributor"]["id"],
            "event_id": submission["publish"]["event_id"], "content_sha256": content_hash,
            "explicit_opt_in": True, "authorized_to_share": True, "revoked": False},
        "public_review": {"content_sha256": content_hash, "decision": "approved",
            "sanitized_method_only": True, "no_private_information": True,
            "rights_verified": True, "reviewer_id": "synthetic-maintainer"},
        "lineage": {"verified": True, "declaration_sha256": digest(submission["provenance"]),
            "relaxation_found": False, "unknown_ancestor_found": False},
        "git": {"repository": source["repository"], "commit": source["commit"],
            "commit_exists": True, "repository_public": True, "version_matches_commit": True},
        "journal": {"item_id": submission["item_id"], "revision": submission["revision"],
            "content_sha256": content_hash, "status": "new"},
        "execution": {"repository": source["repository"], "head_sha": claim["tested_commit"],
            "source_digest": claim["source_digest"], "evidence_digest": claim["evidence_digest"],
            "name": claim["check_name"], "run_id": claim["run_id"], "claim_kind": claim["kind"],
            "execution_stage": "offline_code_executed", "conclusion": "success",
            "scope_verified": True, "oracle_replayed": True, "contradictions": [],
            "oracle_id": "synthetic-oracle"},
        "events": [{"event_sha256": digest(event), "source_authentic": True,
            "actor_id": event["actor_id"]} for event in submission["events"]]}
    if submission["channel"] == "thought_principle":
        observation["principle_review"] = {"content_sha256": content_hash,
            "behavioral_principle_only": True, "technical_claims_present": False,
            "reviewer_id": submission["events"][1]["actor_id"]}
    return deepcopy(observation)
