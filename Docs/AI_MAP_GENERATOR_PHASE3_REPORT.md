# Phase 3 — Placement Solver + Spatial Validation

## GROUNDING CORRECTION — 2026-09-10

Live visual review of the Phase 4 bedroom invalidated the original assumption that raw
`visualBounds.minZ` is directly usable as an Eden position offset. It lifted `SingleWhiteBed`,
`SmallWoodenTable`, `SteelGreenCabinet` and `WoodenDoor` above the support surface by exactly
0.473423, 0.432296, 0.7785 and 1.11276 m. Spatial catalog version
`phase2-live-v1+phase3-spatial-v2` adds explicit `edenCalibration`: support position is the floor
height, while measured bounds and clearance volumes are rebased into that Eden frame. Chair was
already effectively zero-offset. Phase 3 unit tests and live read-back were repeated; latest live
artifact is `Tools/MapAutomation/artifacts/phase3_live_20260910_041430.json`. A subsequent Phase 4
capture visually confirms floor contact for the corrected assets. Scene cleanup remains verified.

## STATUS

`PASS` — deterministic implementation, primitive tests и live Eden acceptance завершены.
Phase 1 и Phase 2 остаются `PASS`.

## ARCHITECTURE

Стабильная цепочка: `PlacementIntent → PlacementSolver → ResolvedPlacement → ScenePatch →
MapAutomation → Eden read-back → validation actual state`. Solver не вызывает низкоуровневые
Eden API напрямую. Hard constraints фильтруют candidates до soft scoring.

## SPATIAL TRANSFORM

`SpatialTransform` явно хранит coordinate space, XYZ position, `[pitch, roll, yaw]`, scale.
MVP поддерживает upright scale=1. WORLD и EDEN эквивалентны только в явной gateway conversion;
ATL↔ASL требует переданного offset. Arma yaw: 0 вдоль local/world +Y, 90 вдоль +X.

## CURATED ASSETS

Subset: `ConcretePanel`, `WoodenSmallFloor`, `ConcreteGreenWall`, `WoodenDoor`,
`SingleWhiteBed`, `SmallWoodenTable`, `WoodenChair`, `SteelGreenCabinet`, `LampCeiling`.
После live PASS у этих девяти и только у них `generatorAllowed=true`; остальные 32 Core Asset
остаются запрещены. `SteelGreenCabinet` выбран как storage/container, `LampCeiling` — как light.

## PLACEMENT INTENT

JSON contract описывает asset, region, `onSurface`, optional `againstWall`, hard constraints,
soft preferences, reachability и seed. Поля transforms запрещены. Пример:

```json
{"schemaVersion":1,"id":"bed_1","asset":"SingleWhiteBed","region":"room_1",
 "onSurface":"floor_1","againstWall":"south_wall",
 "hardConstraints":["OnSurface","AgainstWall","InsideRegion","AvoidIntersection","KeepClearance","Reachable"],
 "softPreferences":["PreferWallCenter"],"requirements":{"reachable":true},"seed":301}
```

## SUPPORT SURFACES

`SupportSurface` хранит id/type/owner, WORLD plane origin/normal, tangent axes и rectangular
bounds. MVP-типы: floor, wall, ceiling. Curated support plane используется вместо общего
предположения `bbox.min.z`; floor/wall/ceiling tolerances централизованы в policy.

## SEMANTIC FRONT

Для bed, chair, cabinet и door задан model-local semantic front с APPROXIMATE provenance и
confidence. У table и rotationally symmetric light meaningful horizontal front отсутствует.
Door opening direction остаётся UNKNOWN до visual/human confirmation.

## OBB / INTERSECTIONS

OBB строится из engine visual bounds и transform; доступны corners, footprint, region check и
полный 3D Separating Axis Theorem (до 15 axes). Это APPROXIMATE occupied volume, не collision mesh.
`GeometryValidator` не имеет side effects и выдаёт `INTERSECTION` / `OUTSIDE_REGION`.

## CLEARANCE

Visual, occupied и clearance volumes разделены. APPROXIMATE boxes заданы для bed usable side,
chair, cabinet opening и door approaches/sweep. `ClearanceValidator` отдельно ловит физически
непересекающиеся, но нефункциональные placements.

## DOOR HANDLING

`DoorProfile` сохраняет portal, engine-measured `xlamdoor` phases/axis evidence и conservative
full radial sweep box вокруг приблизительной hinge. Furniture inside sweep отклоняется. Точная
animated collision и openingDirection не заявлены как VERIFIED.

## ACCESSIBILITY

Локальный occupancy grid ограничен room polygon. OBB footprints inflates на agent radius /
minimum passage width; BFS проверяет entrance → required interaction point. Resolution 0.25 m,
radius 0.35 m, height 1.8 m, passage 0.8 m — prototype APPROXIMATE, не gameplay truth.

## CANDIDATE GENERATION / SCORING

OnSurface использует упорядоченную grid sampling; AgainstWall строит допустимый interval после
end margins и footprint projection. Seed участвует только в детерминированном tie-break.
Soft score поддерживает wall center, compactness и circulation; hard failures не компенсируются.

## DRY RUN

Dry-run возвращает выбранный transform, diagnostics, OBB/clearance corners, navigation path,
rejected candidates и proposed ScenePatch, не меняя `SceneState` или Eden.

## AUTOMATED TESTS

15/15 PASS: A floor support, B floating, C penetration, D wall intersection, E AgainstWall,
F collision, G clearance, H blocked door, I accessibility, J blocked accessibility,
K deterministic, L dry-run, rotated OBB SAT, explicit ATL/ASL conversion и intent contract.

## DEVELOPER COMPOSITION

После primitive PASS последовательно разрешены пять PlacementIntent: bed against wall, table,
chair, storage against wall и ceiling light. Envelope из четырёх floor modules, двух wall modules,
door и отдельного ConcretePanel smoke probe создавался только как временный typed ScenePatch.
Это проверка совместимости primitives, а не RoomPattern или Room Generator.

## LIVE EDEN TESTS

PASS 2026-09-10 на `AI_AutomationProbe`, session `probe_2026_9_10_1_9_12_283`.
После grounding correction spatial v2 тест повторён: revisions 20→21→22. Создано и прочитано обратно 13
временных объектов, представляющих все девять curated классов. Для bed/table/chair/storage/light
повторная проверка actual Eden transforms дала 0 diagnostics; путь entrance → bed usable region —
20 grid points. A–L дали ожидаемые positive/negative коды, deterministic и dry-run подтверждены.
После удаления `sceneUnchanged=true`; production maps не открывались и не изменялись.

Evidence: `Tools/MapAutomation/artifacts/phase3_live_latest.json` и timestamped transcript
`Tools/MapAutomation/artifacts/phase3_live_20260910_041430.json`.

## VERIFIED / APPROXIMATE / UNKNOWN

- VERIFIED: Phase 2 live class/model/bounds; pure solver invariants и unit tests.
- HUMAN VERIFIED: Eden grounding calibration for bed, table, cabinet and door.
- APPROXIMATE: occupied OBB, remaining support/contact planes, semantic fronts, clearance, door sweep,
  navigation agent/grid parameters.
- UNKNOWN: exact collision mesh, exact door animated collision/opening direction, authoritative
  player capsule, arbitrary sloped supports, terrain placement.

## LIMITATIONS

Upright scale=1 interiors only; rectangular planar supports; no sloped/terrain solver; local BFS,
not global navigation; no runtime physics mesh query. Debug geometry is returned as data and does
not leave Eden helpers. No RoomPattern, LLM, RoomGenerator or Vision Critic implemented.

## FILES

Созданы: `Tools/MapAutomation/spatial/{model,solver,__init__}.py`, `phase3_assets.json`,
`placement_intent.schema.json`, `test_placement_solver.py`, `run_phase3_live.py`,
`validate_phase3.py`, `finalize_phase3.py`, `catalog/phase3_validation.json` и этот отчёт.

Изменены: `Docs/AI_MAP_GENERATOR_PLAN.md`, `Tools/MapAutomation/CATALOG.md`, gateway capability /
curated transport allowlist, `catalog/core_assets.json` и его hash в `catalog/build_state.json`.
Dataset-карты, `AI_AutomationProbe.cpp` и `mission.sqm` не изменены.

## READY FOR PHASE 4

`YES`. Placement Solver прошёл Phase 3 acceptance. Phase 4 не начиналась.

## PHASE 3 STATUS

`PASS`

## FUTURE LLM INTEGRATION

Phase 4: RoomPattern / RoomPlan / Planner Contract. Phase 5: LLM Planner. Phase 6: AI Single
Room Generator. Phase 7: Vision Critic. Эти системы в Phase 3 не реализованы.
