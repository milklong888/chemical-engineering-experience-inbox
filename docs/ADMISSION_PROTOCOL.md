# Temporary experience admission protocol

This repository receives sanitized, bounded experience summaries. Receiving an
item is **not** canonical Skill/KG promotion, default retrieval permission, a
generalization result, or an engineering acceptance certificate. The owner may
later request a separate consolidation review under the existing canonical
learning and task-closure rules. This inbox adds no background telemetry.

## Two channels

| Channel | Required evidence before inbox admission | Meaning of admission |
|---|---|---|
| `executed_success` | Exact public method-code repository and commit, relevant successful run at that commit, actual input/output digests, independently replayed result oracle, known unrelaxed ancestry, authorized sanitized export | The declared bounded behavior ran with the stated evidence. No extra principle confirmation is required. |
| `thought_principle` | User explicitly confirms this exact item/revision/content; assistant then reviews this exact content; independent source observations authenticate both events and the behavioral scope | A reviewed behavioral proposal is stored. No unrelated Git commit, code test or Aspen result is required. |

For a thought with no Git source, set all `source` values and the claim's
`tested_commit`, `check_name`, and `run_id` to JSON `null`. Its `source_digest`
is the private, original user-confirmation source digest, and `evidence_digest`
is the canonical digest of the ordered confirmation/review event list. Do not
invent a check identifier to fill the template. Original messages stay local.

Numerical, convergence, equipment, native-execution and engineering-success
claims cannot use the thought channel as an evidence shortcut. A reviewer must
either constrain the item to a behavioral principle or send its technical
claim to the relevant executed/source-backed review process.

`executed_success` distinguishes these proof scopes:

| Claim kind | Required observed execution stage |
|---|---|
| `code_behavior` | `offline_code_executed` |
| `deterministic_calculation` | `headless_calculation_executed` |
| `aspen_simulation_clean` | `aspen_solver_clean_verified` |
| `aspen_engineering_accepted` | `engineering_acceptance_verified` |
| `native_tool_executed` | `native_object_executed_verified` plus actual native-object execution |

A green lint job is not a calculation. A code test is not Aspen execution. A
solver routing receipt or external point loop is not native Sensitivity. Clean
simulation is not complete equipment/product/delivery acceptance. The relevant
existing evidence owner must replay those results; this inbox validator does
not reimplement Aspen's engineering acceptance parser.

## Public information and consent

Every contributor must separately opt in for the exact content and possess the
rights to share it. One repository owner's request cannot authorize publication
of other users' private projects. Opt-in includes the content license in
CONTRIBUTING.md. Record revocation and re-check it before publishing. Public
copies already obtained by third parties cannot be recalled by this tool.

Only allowlisted short method text and public method-version metadata may be
exported. Raw BKP/APW/INP files, history logs, user messages, local paths, tokens,
client identifiers, licensed manual pages and private project results stay
outside the public repository. A content scanner catches obvious secrets and
paths; a content-bound human/assistant review is still required because a
regex cannot determine all confidentiality or licensing rights. Hashes prove
identity, not anonymity or truth; do not hash low-entropy private facts merely
to publish them. This version accepts executed experiences whose referenced
method source is already public. Keep private sources local rather than
publishing them to satisfy the gate.

Relaxed, unknown or incomplete ancestry is local audit only. Renaming,
summarizing, anonymizing or re-running the same relaxed lineage does not remove
that restriction. Failure records may be investigated locally; a diagnosis is
not admitted as verified success merely because a later run passed.

## Verification boundary

The public submission is **untrusted input**. `validate_submission` accepts a
separate `observation` only from trusted maintainer code. This is a local trust
boundary, not a digital signature or an identity service. Copying a submission's
assertions into that parameter defeats verification and is prohibited.

The CLI requires the observation file to resolve outside the untrusted
submission repository and requires `--acknowledge-local-observer-trust` with
`--submission-root`. These checks prevent accidental use of an in-repository
receipt; they do not make a malicious caller's copied receipt trustworthy.
Maintainer review must acquire the underlying facts independently. The validator
executes no supplied commands, follows no supplied artifact paths, performs no
network requests, uploads nothing and never edits canonical assets.

Observation fields (private; never copied into the public summary):

| Field | Maintainer obligation |
|---|---|
| `schema`, `submission_sha256`, `observer_id`, `observed_at`, `expires_at`, `synthetic` | Use `experience-inbox-observation-v1`; bind the entire submission; identify the actual observer; acquire fresh facts. Validity is at most 24 hours. Synthetic fixtures cannot qualify in normal use. |
| `authorization` | Independently observe matching `contributor_id`, `event_id`, `content_sha256`, `explicit_opt_in: true`, `authorized_to_share: true`, `revoked: false`. |
| `public_review` | Bind `content_sha256`; record `reviewer_id`, `decision: approved`, `sanitized_method_only`, `no_private_information`, `rights_verified` all true. |
| `lineage` | Replay the source chain; record `verified: true`, matching `declaration_sha256`, `relaxation_found: false`, `unknown_ancestor_found: false`. |
| `git` | For Git-backed source, observe exact `repository`, `commit`, `commit_exists`, `repository_public`, `version_matches_commit`; the last three must be true. A tag alone is insufficient. |
| `execution` | For executed claims: exact `repository`, `head_sha`, `source_digest`, `evidence_digest`, `name`, `run_id`, `claim_kind`, required `execution_stage`, `conclusion: success`; `scope_verified`, `oracle_replayed` true; meaningful `oracle_id`; empty `contradictions`. Native claims additionally need `native_object_executed: true`. |
| `events` | For each ordered thought event, independently observe matching `event_sha256`, `actor_id` and `source_authentic: true`. Authentication is an observation, not the event's self-assertion. |
| `principle_review` | For thoughts, bind `content_sha256` and assistant `reviewer_id`; record `behavioral_principle_only: true`, `technical_claims_present: false` after reviewing the actual text. |
| `journal` | Consult the maintained inbox history; bind `item_id`, `revision`, `content_sha256`; report `new`, `identical_seen` or `revision_conflict`. Do not manufacture `new` each time. |

All hashes use SHA256 of UTF-8 JSON with sorted keys, `ensure_ascii=False`,
separators `(',', ':')` and finite numbers only, except raw evidence/source
digests which identify their actual original bytes as documented by the source
owner. Duplicate JSON keys and non-finite values are rejected. No digest proves
that the identified bytes mean success.

## Results and use

| Status | Required handling |
|---|---|
| `ready_for_inbox` | The trusted observation supports this exact temporary admission; export only the allowlisted projection. |
| `pending_verification` | Complete the specifically missing verification. Do not label as success or publish as an admitted experience. |
| `quarantined_local_audit_only` | Preserve locally; exclude from shared learning/default retrieval. |
| `rejected` / CLI `invalid_input` | Fix the invalid, contradictory or unauthorized submission. Preserve audit provenance where appropriate. |
| `already_in_inbox` | No new admission, duplicate success count or repeated learning weight. |

`public_export` consumes the current locally generated decision and projects
only approved fields. It is not a second independent verifier; its caller must
not fabricate a decision. `canonical_eligible` and `default_retrieval_eligible`
are always false. The JSON Schema checks structure only; the Python gate plus
trusted observations enforce these semantic distinctions.

Run the governance regression suite with `python -B -X utf8 -m unittest discover
-s tests -v` using the project's documented Python interpreter. These tests use
explicitly synthetic observations. Passing this suite demonstrates tested code
behavior and does not establish real Aspen performance or a real experience
admission. The example files intentionally remain `synthetic: true` and fail
normal admission.
