# Phase 4 — Pattern System / Room Semantics

## PATTERN ARCHITECTURE

Production chain реализована как `Structured Room Brief → PatternPipeline → RoomPattern →
RoomPlan → SemanticSlot → AssetResolver → PlacementIntent[] → Phase 3 PlacementSolver`.
Semantic layer не вычисляет transforms и не дублирует OBB, support, clearance, door sweep или
navigation. Геометрия остаётся в Phase 3. В Phase 4 нет LLM/API/vision/natural-language calls.

После первого пользовательского visual review исправлена Phase 3 grounding-конвенция. Raw
`visualBounds.minZ` больше не прибавляется к Eden floor position: bed, table, cabinet и door
получают позицию ровно на support height, а их bounds/clearance проходят отдельный rebasing.

## ROOM PATTERN FORMAT

`RoomPattern` — immutable Python representation, загружаемая из versioned JSON. Она содержит
room type, допустимые styles, capacity `min/preferred/max`, requirements с priority, semantic
relations, стратегии и provenance. Pattern не содержит world coordinates, classname и Eden ID.

## POOR BEDROOM

`poor_bedroom` поддерживает 1–4 жильцов. Required: entrance, sleeping по capacity, storage,
lighting, circulation. Preferred: один work surface. Optional: seating. Кровати и шкаф требуют
стену и достижимость от входа; центральная проходимость представлена hard accessibility и
clearance плюс soft `MaximizeCirculation`. Стратегии: `parallel_beds`, `opposite_beds`,
`adjacent_beds`; стены выбираются по normals, без координат в pattern.

## FUNCTIONAL ROLES

Минимальный vocabulary: `entrance`, `sleeping`, `storage`, `lighting`, `work_surface`, `seating`,
`circulation`. Styles: `poor`, `utilitarian`, `neutral`. Relations: `againstWall`, `near`,
`awayFrom`, `groupedWith`, `accessibleFrom`, `mustNotBlock`, `faces`. Runtime отклоняет неизвестные
roles/relations. В production pattern используются только отношения, которые текущий Phase 3
contract может выразить без потери hard semantics.

## ROOM PLAN

`RoomPlan` — конкретный deterministic instance: собственный ID, pattern, room type, styles,
capacity, seed, catalog version, Phase 3 region ID, entrance ID, список существующих surface IDs,
strategy и slots. Геометрия surfaces не копируется: plan ссылается на реальные Phase 3
`SceneState`/`SupportSurface` abstractions.

## SEMANTIC SLOTS

Stable IDs строятся из роли и ordinal: `entrance_001`, `circulation_001`, `sleeping_001`,
`sleeping_002`, `storage_001`, `lighting_001`, `work_surface_001`, `seating_001`. Furnishing slot ID
без изменения становится MapAutomation `semanticId` в ScenePatch. Одинаковые pattern, validated
brief, seed и catalog version дают идентичный RoomPlan; runtime/Eden entity IDs не участвуют.

## ASSET RESOLVER

Resolver использует явные role rules и проверяет Phase 2 category/capability/semantic confidence,
map usage, Phase 3 placement compatibility и style overlap. Mapping первого pattern:

| Role | Asset | Catalog evidence |
|---|---|---|
| sleeping | `SingleWhiteBed` | category `bed`, 44 placements / 8 maps |
| storage | `SteelGreenCabinet` | category `container`, container capability, 64 / 8 |
| lighting | `LampCeiling` | category `light`, light capability, 304 / 8 |
| work_surface | `SmallWoodenTable` | category `table`, 63 / 7 |
| seating | `WoodenChair` | category `chair`, seating capability, 153 / 7 |

Оба источника allowlist — `phase3_assets.json` и Core Asset Set — обязаны иметь
`generatorAllowed=true`. Любой false исключает asset. Developer override существует только как
явный constructor option и покрыт отдельным negative test; production pipeline его не включает.

## EXISTING MAP REFERENCES

Phase 2 data использованы как evidence для узкого mapping, но не как доказательство найденных
спален. `SingleWhiteBed` встречается в dorm 9 раз, detective 3, barony 1, minimap 8; также в
saloonv2 11, truba 7, theatre 3, holiday 2. В пределах 5 m dataset co-occurrence bed имеет
42 пары с `LampCeiling`, 23 с `WoodenChair`, 19 с `SmallWoodenTable`. Cabinet имеет 48 пар с
ceiling light и 24 с chair. Table/chair — 57 пар. Это 3D origin-distance и correlation only.

Ручная классификация комнат в Phase 2 не сохранена, поэтому density, wall distance и orientation
не выдаются за bedroom defaults. Phase 4 использует лишь подтверждённые общие сочетания и
Phase 3 размеры; production maps не открывались и не изменялись.

## FEASIBILITY

Preflight суммирует footprint resolved assets с 15% reserve и отдельным reserve входа/прохода,
сравнивая это с площадью Phase 3 region polygon. Возвращает `FEASIBLE`, `TIGHT` или `INFEASIBLE`.
Это ранняя оценка; Phase 3 Solver остаётся authoritative и может отклонить preflight-FEASIBLE
plan из-за формы, стены, collision, clearance или reachability.

## GRACEFUL DEGRADATION

Placement идёт required → preferred → optional. Failure required slot немедленно возвращает
`INFEASIBLE`; обязательный slot не удаляется. Failed preferred/optional получает
`DROPPED_PREFERRED`/`DROPPED_OPTIONAL` и structured `OPTIONAL_DROPPED`. После каждого optional
placement повторно проверяются пути ко всем уже размещённым required reachable slots; regression
отменяет optional object.

## PLANNER CONTRACT

Schema: `Tools/MapAutomation/planner_room_brief.schema.json`, JSON Schema draft 2020-12,
`additionalProperties=false` на каждом object. Тот же strict contract проверяется dependency-free
runtime validator. Валидный будущий Planner output и текущий manual fixture:

```json
{
  "schemaVersion": 1,
  "intent": "create_room",
  "roomType": "bedroom",
  "style": ["poor", "utilitarian"],
  "capacity": {"people": 2},
  "requirements": {"sleeping": 2, "storage": 1, "lighting": 1},
  "preferences": {"workSurface": true, "seating": true, "compact": true},
  "seed": 12345
}
```

## SECURITY / REJECTION

Contract разрешает только version, intent, enum room/style, bounded cardinalities, booleans и
seed. Рекурсивно запрещены `position`, `rotation`, `rawSQF`, `executeCode`, `python`, `shell`,
`class`, `classname` независимо от регистра. Unknown fields, room types, styles и schema versions
отклоняются. AssetResolver, а не будущий LLM, выбирает classname.

## PLACEMENT INTENTS

Примеры translation:

- `sleeping_001 againstWall:east_wall + accessibleFrom:entrance_001` → `SingleWhiteBed`,
  `OnSurface/AgainstWall/InsideRegion/AvoidIntersection/KeepClearance/Reachable`,
  `PreferWallCenter/MaximizeCirculation`.
- `storage_001 againstWall:east_wall + accessibleFrom:entrance_001` → `SteelGreenCabinet` с теми
  же hard spatial checks и interaction reachability.
- `seating_001 groupedWith:work_surface_001` → `WoodenChair`, hard geometry/clearance и Phase 3
  `Compact` soft preference.

Manual fixture выбрал `parallel_beds` и дал 6 valid dry-run placements: 2 beds, cabinet, ceiling
light, table, chair. Все ScenePatch IDs совпадают со slot IDs. Input SceneState fingerprint не
изменился.

## AUTOMATED TESTS

15/15 Phase 4 tests PASS: valid two-person room, one person cardinality, missing sleeping,
unknown room/style, generatorAllowed gate, preferred table drop, required-bed infeasibility,
same/different seed, coordinate/classname rejection, semantic translation, full Phase 3 dry-run
и fixture/schema consistency. Phase 3 tests: 15/15 PASS. Phase 1 static tests: 17/17 PASS.

## LIVE EDEN TEST

PASS 2026-09-10 на `AI_AutomationProbe`, session `probe_2026_9_10_1_9_12_283`, revisions 24→25→26.
Manual fixture создал 11 временных объектов: 4 reference floor modules, accessible `WoodenDoor`,
2 `SingleWhiteBed`, `SteelGreenCabinet`, `LampCeiling`, `SmallWoodenTable`, `WoodenChair`.
Read-back всех 11 semantic IDs прошёл; actual furnishing transforms повторно проверены Phase 3
support/intersection/clearance и required accessibility. Cleanup восстановил исходную сцену,
`sceneUnchanged=true`, `productionMapsTouched=false`.

Два автоматических Eden screenshots проверены после grounding correction. Bed legs, table legs,
chair и cabinet стоят на floor surface; door опирается на тот же уровень. Ceiling light остаётся
на заданной ceiling surface, хотя ceiling shell в этой developer composition не рисуется.

Evidence: `Tools/MapAutomation/artifacts/phase4_live_latest.json` и timestamped transcript
`Tools/MapAutomation/artifacts/phase4_live_20260910_041621.json`.

## REGRESSION

Phase 1 static suite, Phase 2 catalog validation/tests и Phase 3 solver/validator проходят.
Placement Solver не переписан; Phase 4 импортирует его public model/solver API.

## FILES CREATED

- `Tools/MapAutomation/semantic/{__init__,model,pipeline}.py`
- `Tools/MapAutomation/patterns/poor_bedroom.json`
- `Tools/MapAutomation/semantic_assets.json`
- `Tools/MapAutomation/planner_room_brief.schema.json`
- `Tools/MapAutomation/fixtures/poor_bedroom_two_workers.json`
- `Tools/MapAutomation/test_pattern_system.py`
- `Tools/MapAutomation/run_phase4_live.py`
- `Tools/MapAutomation/validate_phase4.py`
- `Tools/MapAutomation/catalog/phase4_validation.json`
- Phase 4 live artifacts и этот отчёт.

## FILES MODIFIED

- `Docs/AI_MAP_GENERATOR_PLAN.md`
- `Docs/AI_MAP_GENERATOR_PHASE3_REPORT.md`
- `Tools/MapAutomation/README.md`
- `Tools/MapAutomation/phase3_assets.json`
- `Tools/MapAutomation/spatial/solver.py`
- `Tools/MapAutomation/test_placement_solver.py`
- `Tools/MapAutomation/run_phase3_live.py`
- `Tools/MapAutomation/validate_phase3.py`

Production maps, `mission.sqm`, MapAutomation gateway и Phase 3 solver не изменены.

## LIMITATIONS

Один room type и один pattern; upright rectangular interior assumptions inherited from Phase 3.
Feasibility основана на площади, а не packing proof. Semantic grouping использует существующий
общий `Compact` score, без pair-specific socket. Room shell приходит извне; Phase 4 его не строит.
Map mining не имеет verified bedroom labels. Visual quality, atmosphere, clutter, terrain,
natural-language interpretation и LLM integration остаются за пределами Phase 4.

## PHASE 4 STATUS

`PASS`

## READY FOR LLM

`YES`

## PHASE 5

Следующий scope: LLM переводит natural language только в `planner_room_brief.schema.json`;
локальный strict validator отклоняет лишние/опасные поля, затем текущий deterministic pipeline
строит и проверяет plan. Нужны model/prompt selection, constrained structured output,
repair по semantic diagnostics, timeout/retry и token/context policy. Ничего из Phase 5 здесь
не реализовано.
