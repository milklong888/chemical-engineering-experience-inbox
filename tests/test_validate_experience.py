"""Adversarial admission checks. All success fixtures are explicitly synthetic."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.validate_experience import digest, public_export, read_json, validate_submission
from tests.fixtures import NOW, observation_for, sample


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        self.submission = sample()
        self.observation = observation_for(self.submission)

    def run_gate(self, submission=None, observation=None):
        return validate_submission(submission or self.submission,
            observation=observation or self.observation, now=NOW, allow_synthetic=True)

    def bind(self):
        self.observation["submission_sha256"] = digest(self.submission)

    def denied(self, expected=None):
        result = self.run_gate()
        self.assertFalse(result["inbox_eligible"])
        self.assertFalse(result["canonical_eligible"])
        self.assertFalse(result["default_retrieval_eligible"])
        if expected:
            self.assertEqual(expected, result["status"])
        return result

    def test_executed_fixture_enters_inbox_only_in_test_mode(self):
        result = self.run_gate()
        self.assertEqual("ready_for_inbox", result["status"])
        self.assertTrue(result["inbox_eligible"])
        self.assertFalse(result["canonical_eligible"])
        self.assertFalse(result["default_retrieval_eligible"])
        self.assertFalse(result["technical_generalization_verified"])

    def test_fixture_cannot_enter_real_inbox(self):
        result = validate_submission(self.submission, observation=self.observation, now=NOW)
        self.assertEqual("pending_verification", result["status"])
        self.assertFalse(result["inbox_eligible"])

    def test_self_asserted_success_is_not_external_verification(self):
        result = validate_submission(self.submission, now=NOW, allow_synthetic=True)
        self.assertEqual("pending_verification", result["status"])

    def test_false_user_opt_in_rejects(self):
        self.submission["publish"]["opt_in"] = False
        self.bind()
        self.denied("rejected")

    def test_local_revocation_rejects(self):
        self.submission["publish"]["revoked"] = True
        self.bind()
        self.denied("rejected")

    def test_independently_observed_revocation_overrides_declaration(self):
        self.observation["authorization"]["revoked"] = True
        self.denied("rejected")

    def test_one_user_cannot_opt_in_for_another_contributor(self):
        self.observation["authorization"]["contributor_id"] = "different-user"
        self.denied("pending_verification")

    def test_public_rights_cannot_be_self_asserted(self):
        self.observation["public_review"]["rights_verified"] = False
        self.denied("pending_verification")

    def test_public_export_rejects_arbitrary_attachment_field(self):
        self.submission["attachments"] = ["../../client.bkp"]
        self.bind()
        self.denied("rejected")

    def test_embedded_fake_trusted_observation_is_untrusted_submission_data(self):
        self.submission["trusted_observation"] = deepcopy(self.observation)
        self.bind()
        self.denied("rejected")

    def test_public_export_rejects_raw_file_under_content(self):
        self.submission["content"]["file"] = "client.his"
        self.bind()
        self.denied("rejected")

    def test_private_path_in_allowed_text_is_rejected(self):
        self.submission["content"]["method"] = "Read C:/Users/Client/private/model.bkp"
        self.submission["content_sha256"] = digest(self.submission["content"])
        self.bind()
        self.denied("rejected")

    def test_secret_in_allowed_text_is_rejected(self):
        self.submission["content"]["method"] = "api_key = test-secret-do-not-publish"
        self.bind()
        self.denied("rejected")

    def test_content_mutation_invalidates_stored_hash(self):
        self.submission["content"]["method"] += " Changed."
        self.bind()
        self.denied("rejected")

    def test_rehashed_content_does_not_reuse_old_publish_authority(self):
        self.submission["content"]["method"] += " Changed."
        self.submission["content_sha256"] = digest(self.submission["content"])
        self.bind()
        self.denied("rejected")

    def test_submission_mutation_invalidates_external_observation(self):
        self.submission["source"]["skill_version"] = "0.4.5"
        self.denied("rejected")

    def test_stale_tested_commit_is_not_current_success(self):
        self.observation["execution"]["head_sha"] = "e" * 40
        self.denied("pending_verification")

    def test_declared_run_sha_must_match_source_version(self):
        self.submission["claim"]["tested_commit"] = "e" * 40
        self.bind()
        self.denied("rejected")

    def test_successful_check_in_other_repository_is_not_relevant(self):
        self.observation["execution"]["repository"] = "other/repo"
        self.denied("pending_verification")

    def test_unrelated_green_check_is_not_success_evidence(self):
        self.observation["execution"]["name"] = "formatting-only"
        self.denied("pending_verification")

    def test_changed_evidence_bytes_do_not_reuse_old_digest(self):
        self.observation["execution"]["evidence_digest"] = "f" * 64
        self.denied("pending_verification")

    def test_changed_inputs_do_not_reuse_passing_evidence(self):
        self.observation["execution"]["source_digest"] = "f" * 64
        self.denied("pending_verification")

    def test_green_job_without_independent_result_replay_stays_pending(self):
        self.observation["execution"]["oracle_replayed"] = False
        self.denied("pending_verification")

    def test_failure_wins_over_other_success_fields(self):
        self.observation["execution"]["conclusion"] = "failure"
        self.denied("rejected")

    def test_contradictory_raw_evidence_wins_over_green_badge(self):
        self.observation["execution"]["contradictions"] = ["nonzero_warning"]
        self.denied("rejected")

    def test_code_test_cannot_certify_aspen_simulation(self):
        self.submission["claim"]["kind"] = "aspen_simulation_clean"
        self.bind()
        self.denied("pending_verification")

    def test_native_preparation_is_not_native_execution(self):
        self.submission["claim"]["kind"] = "native_tool_executed"
        self.bind()
        self.observation["execution"].update(claim_kind="native_tool_executed",
            execution_stage="native_object_executed_verified", native_object_executed=False)
        self.denied("pending_verification")

    def test_exact_native_execution_claim_has_separate_positive_path(self):
        self.submission["claim"]["kind"] = "native_tool_executed"
        self.bind()
        self.observation["execution"].update(claim_kind="native_tool_executed",
            execution_stage="native_object_executed_verified", native_object_executed=True)
        self.assertEqual("ready_for_inbox", self.run_gate()["status"])

    def test_unknown_ancestor_is_quarantined(self):
        self.submission["provenance"]["ancestor_states"].append("unknown")
        self.observation = observation_for(self.submission)
        self.denied("quarantined_local_audit_only")

    def test_relaxed_ancestor_cannot_be_cleaned_by_summary(self):
        self.submission["provenance"]["ancestor_states"].append("relaxed_lineage")
        self.observation = observation_for(self.submission)
        self.denied("quarantined_local_audit_only")

    def test_external_relaxation_overrides_self_reported_clean_lineage(self):
        self.observation["lineage"]["relaxation_found"] = True
        self.denied("quarantined_local_audit_only")

    def test_incomplete_ancestry_is_not_admitted(self):
        self.submission["provenance"]["ancestry_complete"] = False
        self.observation = observation_for(self.submission)
        self.denied("quarantined_local_audit_only")

    def test_older_observation_requires_fresh_revocation_check(self):
        self.observation["expires_at"] = "2026-09-12T11:59:59Z"
        self.denied("pending_verification")

    def test_future_observation_is_invalid(self):
        self.observation["observed_at"] = "2026-09-12T12:01:00Z"
        self.denied("pending_verification")

    def test_observation_cannot_grant_indefinite_authority(self):
        self.observation["expires_at"] = "2099-09-12T11:59:59Z"
        self.denied("pending_verification")

    def test_observation_cannot_authenticate_a_later_review(self):
        self.submission = sample("thought_principle")
        self.observation = observation_for(self.submission)
        self.observation["observed_at"] = "2026-09-12T11:15:00Z"
        self.denied("pending_verification")

    def test_private_repository_metadata_is_not_public_exportable(self):
        self.observation["git"]["repository_public"] = False
        self.denied("pending_verification")

    def test_unobserved_git_commit_stays_pending(self):
        self.observation["git"]["commit_exists"] = False
        self.denied("pending_verification")

    def test_duplicate_submission_does_not_count_as_new_admission(self):
        self.observation["journal"]["status"] = "identical_seen"
        self.assertEqual("already_in_inbox", self.run_gate()["status"])
        self.assertFalse(self.run_gate()["inbox_eligible"])

    def test_reusing_revision_for_changed_content_is_rejected(self):
        self.observation["journal"]["status"] = "revision_conflict"
        self.denied("rejected")

    def test_unchecked_replay_history_stays_pending(self):
        self.observation.pop("journal")
        self.denied("pending_verification")

    def test_thought_confirmation_then_assistant_review_is_eligible_only_for_inbox(self):
        self.submission = sample("thought_principle")
        self.observation = observation_for(self.submission)
        self.assertEqual("ready_for_inbox", self.run_gate()["status"])

    def test_thought_self_asserted_event_is_not_authenticated(self):
        self.submission = sample("thought_principle")
        self.observation = observation_for(self.submission)
        self.observation["events"][0]["source_authentic"] = False
        self.denied("pending_verification")

    def test_thought_needs_no_unrelated_git_or_execution_receipt(self):
        self.submission = sample("thought_principle")
        self.observation = observation_for(self.submission)
        self.observation.pop("git")
        self.observation.pop("execution")
        self.assertEqual("ready_for_inbox", self.run_gate()["status"])

    def test_thought_semantic_review_cannot_be_skipped(self):
        self.submission = sample("thought_principle")
        self.observation = observation_for(self.submission)
        self.observation.pop("principle_review")
        self.denied("pending_verification")

    def test_thought_detected_technical_claim_stays_pending(self):
        self.submission = sample("thought_principle")
        self.observation = observation_for(self.submission)
        self.observation["principle_review"]["technical_claims_present"] = True
        self.denied("pending_verification")

    def test_thought_review_before_confirmation_is_rejected(self):
        self.submission = sample("thought_principle")
        self.submission["events"][1]["occurred_at"] = "2026-09-12T11:00:00Z"
        self.observation = observation_for(self.submission)
        self.denied("rejected")

    def test_thought_old_revision_confirmation_is_not_reusable(self):
        self.submission = sample("thought_principle")
        self.submission["revision"] = 2
        self.observation = observation_for(self.submission)
        self.denied("rejected")

    def test_thought_rehashed_mutation_requires_new_confirm_and_review(self):
        self.submission = sample("thought_principle")
        self.submission["content"]["method"] += " New scope."
        self.submission["content_sha256"] = digest(self.submission["content"])
        self.submission["publish"]["content_sha256"] = self.submission["content_sha256"]
        self.observation = observation_for(self.submission)
        self.denied("rejected")

    def test_thought_same_actor_cannot_be_both_confirming_user_and_reviewer(self):
        self.submission = sample("thought_principle")
        self.submission["events"][1]["actor_id"] = self.submission["contributor"]["id"]
        self.observation = observation_for(self.submission)
        self.denied("rejected")

    def test_thought_duplicate_event_cannot_manufacture_second_review(self):
        self.submission = sample("thought_principle")
        self.submission["events"][1]["id"] = self.submission["events"][0]["id"]
        self.observation = observation_for(self.submission)
        self.denied("rejected")

    def test_thought_channel_cannot_bypass_technical_proof(self):
        self.submission = sample("thought_principle")
        self.submission["claim"]["kind"] = "aspen_engineering_accepted"
        self.observation = observation_for(self.submission)
        self.denied("rejected")

    def test_public_projection_does_not_include_private_observation_events(self):
        projected = public_export(self.submission, self.run_gate())
        self.assertNotIn("events", projected)
        self.assertNotIn("authorization", projected)
        self.assertNotIn("execution", projected)
        self.assertNotIn("public_review", projected)
        self.assertEqual("temporary_inbox", projected["status"])

    def test_stale_decision_cannot_export_changed_content(self):
        decision = self.run_gate()
        self.submission["content"]["title"] = "Changed after the gate"
        with self.assertRaises(ValueError):
            public_export(self.submission, decision)

    def test_pending_decision_cannot_export_an_admitted_record(self):
        decision = validate_submission(self.submission, now=NOW, allow_synthetic=True)
        with self.assertRaises(ValueError):
            public_export(self.submission, decision)

    def test_declared_artifact_path_never_becomes_a_local_read(self):
        self.submission["claim"]["path"] = "../../not-to-be-read/private.log"
        self.bind()
        self.denied("rejected")

    def test_malformed_json_types_fail_closed_without_crashing(self):
        for field in ("channel", "item_id", "revision", "claim", "provenance", "events"):
            value = deepcopy(self.submission)
            value[field] = ["unexpected", {"type": "nested"}]
            result = validate_submission(value, now=NOW, allow_synthetic=True)
            self.assertFalse(result["inbox_eligible"], field)

    def test_duplicate_json_keys_rejected_before_hashing(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "duplicate.json"
            path.write_text('{"schema":"first","schema":"second"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                read_json(path)

    def test_nonfinite_json_rejected_before_hashing(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "nonfinite.json"
            path.write_text('{"number":NaN}', encoding="utf-8")
            with self.assertRaises(ValueError):
                read_json(path)

    def test_cli_does_not_trust_observation_in_submission_repository(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            submission, receipt = root / "submission.json", root / "receipt.json"
            submission.write_text(json.dumps(self.submission), encoding="utf-8")
            receipt.write_text(json.dumps(self.observation), encoding="utf-8")
            command = [sys.executable, "-B", "-X", "utf8", str(Path(__file__).parents[1] / "scripts/validate_experience.py"),
                str(submission), "--observation", str(receipt), "--submission-root", str(root),
                "--acknowledge-local-observer-trust"]
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(3, completed.returncode)
            self.assertIn("outside the untrusted submission repository", completed.stdout)


if __name__ == "__main__":
    unittest.main()
