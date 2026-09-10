# AI Map Generator — Phase 7 Report

Date: 2026-09-10

## RESULT

Phase 7 is complete. A real Eden room passed the full acceptance path:

```text
clean capture r20 -> Critic PASS
intentional solver-valid chair defect r21
-> Critic REPAIR (RELATION_MISMATCH, medium, 0.78)
-> RepairPlanner MOVE_NEAR -> Phase 3 dry-run PASS
-> one setTransform -> read-back + hard validation PASS r22
-> independent after capture -> Critic PASS
-> owned-object cleanup -> original probe fingerprint restored r23
```

No production map was opened or modified. Phase 8 was not started.

## VISION ARCHITECTURE

```text
RoomGenerator -> filesystem capture paths -> CaptureBundle -> CriticService
-> locally validated CriticResult -> RepairPlanner -> PlacementIntent
-> PlacementSolver dry-run -> bounded ScenePatch -> MapAutomation
-> read-back + Phase 3 validation -> independent recapture
```

Planner decides what to build, Solver owns transforms and hard geometry, and Critic reports visual observations plus bounded semantic repair goals. Provider output never directly edits Eden.

## CAPTURE AND OVERLAY

`CaptureBundle` v1 binds generation ID, room ID, exact revision, scene fingerprint, 1–3 camera roles, a small semantic manifest, authoritative validator facts, and image paths. Mixed revisions are rejected. PNG/base64 never enter the SQF queue.

Eden captures paired `entrance`, `opposite_corner`, and `overview` frames without moving the camera inside each pair. The built-in `drawNames_setEnable` state is switched idempotently and restored after capture. Live investigation found that Arma's `screenshot` command did not rasterize those editor UI labels, so Python adds a fallback semantic class overlay to the paired image using only known placement IDs/classes and camera projection. Image text remains untrusted; the manifest remains the identity authority.

Arma's default Screenshots directory limit was encountered during repeated acceptance runs. With user approval, old MapAutomation PNGs were moved—not deleted—to `Tools/MapAutomation/artifacts/screenshots_archive`, with filename, byte count, SHA-256, and timestamp manifests. Current acceptance captures remained in the engine screenshot folder while in use.

## CRITIC CONTRACT

`OpenAICriticProvider` uses the OpenAI Responses API with image inputs and strict JSON Schema. `critic_result.schema.json` is closed and bounded to 12 issues. Local validation independently rejects unknown IDs/views, duplicate identities, forbidden coordinates/transforms/class replacement/code, invalid grounding, and actionable goals without a known subject.

Prompt `room-vision-critic-v1.1` treats all image text as untrusted data. Engine solver facts are authoritative; a passed hard constraint cannot be reopened as a vision repair or recapture request. The critic can assess visual composition and declared semantic relations that the hard validator does not decide.

Implemented issue categories include floating/sunk appearance, visible clipping, relation mismatch, awkward orientation/spacing, visually blocked entrance, composition imbalance, excessive empty/crowded space, occlusion, awkward lighting placement, and unresolved identity.

## REPAIR POLICY

Accepted semantic goals are `REPOSITION`, `REORIENT`, `REGROUP`, `MOVE_AWAY`, `MOVE_NEAR`, `RETRY_PLACEMENT`, `DROP_OPTIONAL`, `REQUEST_RECAPTURE`, and `NO_ACTION`. The repair planner consumes only locally validated fields, reconstructs the scene without the subject, derives a new `PlacementIntent`, and requires a Phase 3 dry-run `VALID` result. It protects required/preferred semantics from deletion.

Review-only is the default. Explicit repair allows 0–3 changes (default 2) and stops on `PASS`, `MAX_ITERATIONS`, `NO_PROGRESS`, `REPAIR_INFEASIBLE`, `REGRESSION`, `LOW_CONFIDENCE`, `CRITIC_FAILED`, or `REVIEW_ONLY`. Every iteration records the critic artifact, issue fingerprint, proposal, apply result, validation result, model usage, latency, and image hashes.

## LIVE ACCEPTANCE EVIDENCE

- Clean baseline: generation `generation_a24abbe5fa934c31`, revision 20, three clean/overlay pairs at 1920×1080; `critic_155b1c7597164195bd37a36d7df371ee` returned `PASS` with zero issues.
- Intentional defect: `seating_001` was solver-valid but moved from the work area to the opposite corner at revision 21; hard spatial/navigation validation still passed.
- Grounding/recapture: the initial ambiguous result safely requested recapture and applied no operation. After the requested views and semantic overlays, the critic grounded the chair/table pair.
- Repair iteration 0: `critic_f7944d568541490ebd841c4f9c53046f` returned `RELATION_MISMATCH`, severity `medium`, confidence `0.78`, targets `seating_001` and `work_surface_001`, goal `MOVE_NEAR`.
- Deterministic correction: RepairPlanner produced one `setTransform` only after Phase 3 dry-run passed. Live apply advanced revision 21→22; read-back, hard constraints, and navigation passed.
- Repair iteration 1: fresh revision-22 captures were reviewed by `critic_6004258f25f24a489909534df61c3b86`, which returned `PASS` with no issues.
- Loop artifact: `Tools/MapAutomation/artifacts/repairs/repair_loop_generation_a24abbe5fa934c31.json` records `stopReason=PASS`, `repairsApplied=1`.
- Cleanup: 30 owned fixture objects were removed at revision 23 and the original probe fingerprint was restored.

The accepted loop used 15,784 reported tokens and 81,846 ms of provider latency across its two reviews. Monetary cost is intentionally not estimated without a pinned price basis.

## EVALUATION

The versioned evaluation manifest contains five clean cases and five intentional, spatially valid defect recipes. The real acceptance run covers the two-worker clean baseline and chair/table relation defect; the remaining recipes stay available for future statistical evaluation rather than blocking the functional milestone.

Offline Phase 7 coverage is 17/17: schema validation, unknown targets, forbidden coordinates/code, unresolved grounding, capture manifest, solver-gated regrouping, required-semantic protection, impossible references, clean no-op, confidence threshold, review-only default, no-progress, regression stop, PNG transport isolation, semantic-overlay rendering, and non-conflicting MOVE_AWAY preferences. Impossible repair is fail-closed and covered without a live mutation.

False-positive policy ignores `low`/`info` by default and requires confidence ≥0.75. The real clean baseline made zero repairs. The bounded loop performed exactly one useful change on the intentional defect and stopped after the independent `PASS`.

## REGRESSION

- Phase 1 static/transport: 18/18 PASS
- Phase 2 catalog: 10/10 PASS
- Phase 3 placement: 16/16 PASS
- Phase 4 patterns: 15/15 PASS
- Phase 5 planner: 9/9 PASS
- Phase 6 generator: 17/17 PASS
- Phase 7 offline: 17/17 PASS
- Python compileall: PASS

## FILES

Created: `critic_result.schema.json`, `vision_critic/*`, `run_phase7.py`, `inject_phase7_defect.py`, `test_vision_critic.py`, the evaluation manifest, artifacts, and this report.

Modified: paired capture/transport SQF, room capture orchestration, medium probe visualization shell, configuration, README, and roadmap.

## LIMITATIONS

- Eden must remain available while its screenshot command executes.
- The current semantic overlay labels generated placement objects; room-shell identity remains in the manifest.
- The 10-case manifest is suitable for repeatable evaluation, but only one clean/defect pair has real provider labels so far; broader false-positive statistics require more runs.
- Screenshot folder capacity must be monitored during large batches; archival is recoverable and hash-manifested.

## PHASE 7 STATUS

`PASS`

## READY FOR PHASE 8

`YES — NOT STARTED`
