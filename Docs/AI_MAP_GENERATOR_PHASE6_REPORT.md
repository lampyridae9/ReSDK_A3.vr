# AI Map Generator — Phase 6 Report

## ROOM GENERATOR ARCHITECTURE

`RoomGenerator` coordinates the existing Planner, `PatternPipeline`, `AssetResolver`, Phase 3
`PlacementSolver`, validators and a narrow `MapAutomationRoomGateway`. It contains no OBB/support
math, no LLM parsing and no Eden calls. `GenerationResult` is a strict dataclass with status,
lifecycle, every intermediate artifact, revisions/fingerprints, ownership, screenshots, timings,
token usage, search metrics and reproducibility data.

## GENERATION LIFECYCLE

`CREATED → INSPECTING → PLANNING → PLANNED → RESOLVING → PLACING → VALIDATING → APPLYING →
READBACK → CAPTURING → COMPLETE`. Every transition is timestamped. Failure records both last
working stage and terminal `FAILED`.

## TRANSACTION / FAILURE HANDLING

All semantic and spatial work is preflight. Live mode then records revision, full owned scene
snapshot/fingerprint and semantic state, and submits shell fixture plus furnishing as one typed
`applyPatch`. A failed patch stays under Phase 1 safe-stop and is never auto-reconciled. Failures
after a confirmed commit attempt ownership-scoped cleanup; divergence becomes `PARTIAL_FAILURE`.
The intentionally too-small test exits before the gateway and leaves the scene untouched.

## ROOM SHELL

`ExistingRoomShell` owns the Phase 3 `SceneState` reference and optional probe-only materialization
operations. Inspection requires a floor, four-vertex orthogonal region, entrance, at least two
walls, ceiling when lighting requires it, horizontal floor/ceiling and upright walls. Unsupported
input returns `UNSUPPORTED_ROOM_GEOMETRY`.

## LLM → ROOMPLAN

One Planner result is validated once and used to create exactly one `RoomPlan`. Spatial retries do
not call the LLM. Saved brief replay and `regenerate_room(..., new_seed)` skip Planner entirely.

## PLACEMENT ORCHESTRATION

Virtual entrance/circulation are supplied by the inspected shell. Furnishing follows semantic
dependency order: core sleeping, storage, lighting, then work surface and dependent seating.
Explicit slot relations are topologically sorted. Door clearance is an existing obstacle and every
tentative required placement rechecks Phase 3 accessibility to all required interaction targets.

## BACKTRACKING

Phase 3 gained a backward-compatible `resolve_candidates(limit=N)` API returning ranked candidates
that already passed hard validators. `resolve()` remains the best-candidate API. DFS is deterministic
and bounded by top-N, node, backtrack and wall-clock budgets. Metrics expose generated candidates,
attempts, nodes, backtracks and budget exhaustion. No combinatorial unbounded search exists.

## OPTIONAL DEGRADATION

Required exhaustion returns controlled `INFEASIBLE`. Preferred/optional failures record
`DROPPED_PREFERRED` / `DROPPED_OPTIONAL` and `OPTIONAL_DROPPED`; they never invalidate a complete
required solution or trigger LLM repair.

## STABLE IDS / OWNERSHIP

RoomPlan slot IDs (`sleeping_001`, etc.) are unchanged through intent, patch and Eden read-back.
External ownership records `generationId`, `roomId`, `patternId`, slot mapping and seed; Eden's
existing `parentId` stores room membership without expanding `__ai` into a graph database.

## VARIATION / SEEDS

The existing `parallel_beds`, `opposite_beds`, `adjacent_beds` strategies and seeded candidate
tie-breaking produce deterministic variation. Same brief/shell/seed reproduces identical RoomPlan
and transforms. Seeds 100/200/300/400/500 produced five layout fingerprints for every successful
capacity/size group.

## GENERATION MATRIX

60 dry-runs: capacities 1–4 × small/medium/large × seeds 100–500. Result: 45 SUCCESS, 15 controlled
INFEASIBLE (all small rooms with capacity 2–4), no other status. This is intentional graceful
behavior, not silent capacity reduction.

## METRICS

Success 75%; infeasible 25%; optional-drop rate 3.509%; 345 candidate attempts; 60 backtracks;
275 placed objects; latency 40–6228 ms, mean 2654.88 ms. All 45 successful navigation results pass.
Planner latency and token usage are preserved separately in each real generation result.

## SCREENSHOTS

The live adapter requests three views and associates generation/room/revision/camera pose with every
returned artifact. Screenshots are saved only; no image is sent to a model and no Vision Critic or
repair exists. The final acceptance returned three confirmed 1920×1080 artifacts: entrance,
opposite corner and overview. Captures are deliberately separate requests so each diagnostic report
stays below the legacy FileManager read buffer and one failed view cannot hide successful peers.

## HUMAN VISUAL REVIEW

Fresh post-fix Phase 6 entrance/opposite-corner/overview screenshots were reviewed manually.
Grounding, parallel bed orientation, cabinet door clearance and ceiling light height look physically
sensible. The entrance view is inside the threshold and unobstructed. The table and chair form a
coherent work pair at 1.0 m center distance with usable space; there are no obvious absurd placements.

## LIVE EDEN TEST

PASS on `AI_AutomationProbe`, generation `generation_3978944b5300458e`: real uncached OpenAI Planner
succeeded in one call (402 input / 74 output / 476 total tokens, 3333 ms); preflight placed six
furnishings; one patch committed at revision 3→4; all 11 owned IDs were read back and actual Phase 3
geometry/accessibility validation passed. Three independent capture requests returned successfully.
Interactive inspection remained available until Enter, then cleanup advanced revision 4→5.
Final snapshot contains no generation-owned IDs, matches the pre-generation fingerprint, and no
production map was opened or modified. Evidence: `artifacts/phase6_live_latest.json` plus the three
`artifacts/phase6_screenshots/*_postfix.png` files.

The preceding failed attempt was diagnosed exactly: `ma_test_record` wrote an 11,755-byte
`capture.sqfdata`, then tried to verify it with bounded `file_read`; `$BUFFER_OVERFLOW$` raised a
runtime error after PNG creation and aborted the transport worker. Large reports now verify write +
existence without bounded read-back, and a static regression test locks this behavior.

## FAILURE TEST

PASS offline/simulated live: too-small shell returns `INFEASIBLE` before any apply, gateway apply
count stays zero, and diagnostics identify preflight. Apply failure taxonomy preserves safe-stop
and reports whether owned objects exist in actual state.

## CLEANUP

PASS in both automated and real live tests. Cleanup deleted only the 11 current generation IDs,
preserved the four pre-existing probe objects, left no owned IDs, and restored the exact initial
scene fingerprint. The CLI also supports `--cleanup-generation <artifact>` for interrupted sessions.

## CLI

`run_room_generator.py` defaults to dry-run. It supports plan-only, dry-run, explicit live, saved
brief replay, seed, shell size, search budgets, `--keep`, and `--interactive` (wait for Enter before
ownership-scoped cleanup).

## AUTOMATED TESTS

17/17 Phase 6 tests PASS: capacities 1–4, small/too-small, optional drop, bounded backtracking,
same/different seeds, dry-run immutability, simulated live read-back/screenshots, failure cleanliness,
ownership cleanup, Planner-called-once, unsupported geometry and regenerate replay.

## REGRESSION

Phase 1: 18/18; Phase 2: 10/10 plus 4/4 live-catalog artifact checks; Phase 3: 16/16;
Phase 4: 15/15; Phase 5: 9/9. All offline regression suites PASS.

## FILES CREATED

- `Tools/MapAutomation/room_generator/{__init__,model,gateway,generator}.py`
- `Tools/MapAutomation/run_room_generator.py`
- `Tools/MapAutomation/test_room_generator.py`
- `Tools/MapAutomation/validate_phase6.py`
- `Tools/MapAutomation/artifacts/phase6_generation_matrix.json`
- `Docs/AI_MAP_GENERATOR_PHASE6_REPORT.md`

## FILES MODIFIED

- `Tools/MapAutomation/spatial/{__init__,model,solver}.py`
- `Tools/MapAutomation/semantic/pipeline.py`
- `Tools/MapAutomation/placement_intent.schema.json`
- `Tools/MapAutomation/test_placement_solver.py`
- `Src/Editor/MapAutomation/MapAutomation_capture.sqf`
- `Src/Editor/MapAutomation/MapAutomation_tests.sqf`
- `Tools/MapAutomation/test_static.py`
- `Tools/MapAutomation/README.md`
- `Docs/AI_MAP_GENERATOR_PLAN.md`

## LIMITATIONS

One room type/pattern; upright rectangular shells; probe fixture materializes floor/door references
but does not design building shells. No rollback exists below Phase 1: failed engine patch requires
explicit observed-state reconcile. Pair-specific furniture sockets and semantic-slot editing are
future work, though stable slot ownership permits them. No vision or aesthetic repair is included.

## PHASE 6 STATUS

`PASS`

## READY FOR PHASE 7

`YES`

## NEXT

Screenshots → Vision Critic → structured visual diagnostics → bounded repair. Phase 7 must preserve
the same deterministic Solver/validator/apply boundary and may not let vision output call Eden directly.
