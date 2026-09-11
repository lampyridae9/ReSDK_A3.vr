# AI Map Generator — Phase 8 Building Generator

Дата: 2026-09-11  
Scope: одно автономное здание типа `poor_worker_dormitory`; Phase 9 не начиналась.

## BUILDING ARCHITECTURE

Реализован отдельный pipeline `BuildingBrief → BuildingPlan/BuildingGraph → BuildingLayoutSolver →
shell/portals → RoomGenerator → building validators → bounded MapAutomation transaction`. Building
geometry не перенесена в Phase 3 PlacementSolver, а Vision Critic не используется вместо layout solver.

## BUILDING PLANNER

Добавлен versioned prompt `building-planner-v1` и `BuildingPlannerService` с локальной strict validation,
не более чем двумя попытками, cache/replay и одним LLM-вызовом на здание. Real uncached natural-language
test вернул `2 floors / 4 bedrooms / 8 residents / 1 entrance` и завершился `SUCCESS` за 3396 ms.
Geometry, assets и solver internals модели не передаются.

## BUILDING BRIEF

`building_brief.schema.json` и dependency-free validator допускают только узкий dormitory vocabulary.
Запрещены coordinates, transforms, rotations, class/classname, ScenePatch, Eden IDs, SQF, Python и shell.
Capacity fail-closed: не более четырёх жителей на спальню и не менее одного на required bedroom.

## BUILDING GRAPH

Поддержаны node types `building`, `floor`, `room`, `corridor`, `entrance`, `portal`,
`vertical_connection` и edges `contains`, `connectedByDoor`, `accessibleFrom`, `verticalConnection`.
Physical portal graph сверяется с semantic graph.

## HIERARCHICAL SEMANTIC IDS

Building/floor/room/portal/stair IDs детерминированы. RoomGenerator получил opt-in namespace; gateway-safe
слоты имеют вид `bedroom_001__sleeping_001`. Точки не используются, так как MapAutomation отвергает их.

## BUILDING LAYOUT SOLVER

Использована простая constrained rectangular subdivision: central corridor делит footprint на две полосы,
затем каждая полоса детерминированно режется по числу room slots. Seed выбирает ось и mirror variant.
Search ограничен `maxLayoutCandidates`, `maxPartitionAttempts` и `timeBudgetMs`; случайного цикла до успеха нет.

## FLOOR PLAN

Каждый этаж хранит index, elevation, footprint, spaces, walls, portals и vertical connections. Storey height
4.23924 m берётся из verified live AABB выбранного `ConcreteGreenWall`, а не из LLM. Совпадение высоты стены и
межэтажного перекрытия подтверждено live capture; gameplay/contact semantics остаются `APPROXIMATE`.

## ROOM PARTITIONING

Hard validation проверяет footprint containment, positive non-overlap, minimum dimensions/area и corridor
width. Prototype bedroom constraints: min 3.4 × 3.8 m, minimum 13 m², preferred 18 m² (`APPROXIMATE`).

## CORRIDORS

Corridor — отдельное circulation space шириной минимум 1.5 m. Он не вызывает RoomGenerator и может быть пустым.
Exterior entrance, все room portals и stair connection входят в один accessibility graph.

## WALLS / FLOORS

Shared walls представлены один раз как floor-owned atomic `WallSegment` с одним или двумя owners. Shell pass
использует реальные allowlisted `ConcretePanel` и `ConcreteGreenWall`. Их модули не масштабируются. Floor grid
теперь использует полное покрытие footprint с детерминированным overlap вместо незакрытого border; wall runs
раскладываются с выравниванием крайних модулей. Live overview не показал очевидных сквозных щелей, стены и roof
совпадают по высоте. Точный collision/contact overlap модулей остаётся `APPROXIMATE`.

## PORTALS / DOORS

Portal содержит from/to space, shared wall, opening center/width и `WoodenDoor`. Validator подтверждает wall
ownership, opening fit и graph correspondence. Door sweep/approach основаны на существующем Phase 3 approximate
profile. Реальный building-level door runtime test не завершён.

## VERTICAL CONNECTION / STAIRS

`VerticalConnection` связывает corridor этажей и резервирует lower/upper landing regions. Dataset evidence:
`SteelRustyStairs` встречается 63 раза в шести картах (detective 19, saloonv2 11, dorm 1, barony 1).
Однако asset отсутствует в Phase 3 spatial subset и не имеет traversal proof. `stairGeneratorAllowed=false`;
двухэтажный live apply fail-closed до отдельного curated review. Статус: `APPROXIMATE` representation,
`UNKNOWN` gameplay traversal.

## ROOM GENERATOR INTEGRATION

Bedroom placement code не дублировался. BuildingPlan детерминированно расширяет один brief в RoomBrief на
каждую спальню, затем вызывает существующий RoomGenerator без дополнительных LLM calls. Реальный 2-floor
dry-run создал четыре solver-validated bedroom plans с уникальными slot IDs.

## BUILDING ACCESSIBILITY

`BuildingAccessibilityValidator` выполняет BFS от `EXTERIOR`, проверяет все required rooms, upper floors,
physical portals и semantic portal edges. Local room navigation остаётся ответственностью RoomGenerator.

## BUILDING FEASIBILITY

Результаты `FEASIBLE/TIGHT/INFEASIBLE` вычисляются до Eden mutation. Required room не удаляется и capacity
не уменьшается. Optional storage room может быть отброшена только с `OPTIONAL_ROOM_DROPPED`.

## LAYOUT SEARCH / BACKTRACKING

54-case matrix: floors 1/2 × bedrooms 2/3/4 × footprints small/medium/large × seeds 0/1/2.
Результат: 36 `FEASIBLE`, 18 controlled `INFEASIBLE`, 0 uncontrolled failures. Room backtracking метрики
суммируются отдельно.

## OWNERSHIP / TRANSACTION

Каждый planned operation записывает generationId, buildingId, floorId, ownerId, semanticId и stage в artifact.
Apply order: floors → walls → doors → stairs → furniture → lights. Одна logical transaction физически разбита
на read-back batches максимум по 32 операции; cleanup также пакетный и удаляет только generation-owned IDs.
После reconcile реальные shell-only (58 objects) и fully furnished (70 objects) транзакции завершились `SUCCESS`.
Cleanup прошёл за 2/3 delete batches соответственно и оба раза восстановил исходные 4 объекта и точный fingerprint
`ca3a8e07…b87b3`.

## PERFORMANCE / CHUNK BUDGET

`BuildingBudgetReport` считает total/STRUCTURE/ITEM/DECOR, 10 m chunk distribution и informational hotspots.
Threshold не объявлен engine limit. После structural-contact correction single-floor full dry-run: 70 objects,
5986 ms; two-floor: 123 objects, 11977 ms. Рост вызван полным покрытием floor/roof без масштабирования модулей.

## EXISTING MAP REFERENCES

Whole-map sanity counts, не room-semantic facts:

| map | objects | floors | walls | doors | stairs/ladders |
|---|---:|---:|---:|---:|---:|
| dorm | 2552 | 88 | 413 | 45 | 10 |
| detective | 1085 | 72 | 132 | 26 | 33 |
| saloonv2 | 3707 | 192 | 593 | 107 | 28 |
| barony | 2809 | 284 | 399 | 43 | 22 |
| theatre | 2324 | 421 | 449 | 21 | 31 |

Эти числа используются только как evidence существования/repetition structural families. Layouts не копировались.

## SINGLE-FLOOR ACCEPTANCE

Offline full dry-run `2 bedrooms / corridor / entrance / capacity 4`: `SUCCESS`, 70 objects, 3 portals,
оба RoomGenerator calls `SUCCESS`. После ручного `call ma_reconcile` выполнены реальные shell-only и fully
furnished live acceptance. Финальный artifact `building_generation_302d333a2ef5423b.json`: 70 owned objects,
6 staged apply batches, 3 captures, обе спальни `SUCCESS`, cleanup `CLEAN`, 15201 ms. Ограничения 32 operations/patch,
запрещённая точка в semantic ID и пакетная cleanup устранены.

## TWO-FLOOR ACCEPTANCE

Offline full dry-run `4 bedrooms / 2 corridors / entrance / vertical connection / capacity 8`: `SUCCESS`,
123 objects, 5 portals, all required rooms graph-reachable. Live two-floor acceptance намеренно заблокирован
непроверенным stair asset.

## VISION / HUMAN REVIEW

Phase 7 не переписывалась. Live captures проверены вручную для exterior, floor overview и representative furnished
bedroom. Исправлены две найденные ошибки: storey height не совпадал с wall AABB, а camera poses не переводили ATL
в ASL. Повторные кадры показывают замкнутый одноэтажный shell, ровный roof/floor и мебель внутри спальни без
очевидного прохождения через внешнюю стену. Полный stair view и runtime human review остаются `UNKNOWN`.

## RUNTIME BUILD / LOAD TEST

Не выполнен: до save/build/runtime необходимо завершить structurally valid live shell и stair review.
Статус: `UNKNOWN`.

## TEST MATRIX

24/24 Phase 8 unit tests PASS. Matrix 54/54 controlled outcomes PASS. Artifact:
`Tools/MapAutomation/artifacts/phase8_offline_matrix.json`.

## METRICS

- Real Building Planner: 1 LLM call, 3396 ms.
- Single-floor dry-run: layout attempts 1, rooms 2, portals 3, objects 70, total 5986 ms.
- Single-floor live furnished: rooms 2, portals 3, objects 70, 6 apply batches, total 15201 ms, cleanup `CLEAN`.
- Two-floor dry-run: layout attempts 1, rooms 4, portals 5, objects 123, total 11977 ms.
- Vision calls: 0.

## REGRESSION

Phase 4 PatternSystem: 15/15 PASS. Phase 6 RoomGenerator: 17/17 PASS. Полный discovery после
Phase 8 дал 129/130 PASS; единственный pre-existing catalog-integrity failure сообщает о stale generated
hashes (`core_assets.json` и catalog builder inputs), а не о Building Generator. Полный Phase 1–7 green
regression поэтому не заявляется.

## FILES CREATED

- `Tools/MapAutomation/building_generator/{model,planner,layout,validator,generator}.py`
- `Tools/MapAutomation/building_brief.schema.json`
- `Tools/MapAutomation/building_profile.json`
- `Tools/MapAutomation/planner/building_planner_prompt_v1.txt`
- `Tools/MapAutomation/run_building_generator.py`
- `Tools/MapAutomation/test_building_generator.py`
- `Tools/MapAutomation/validate_phase8.py`
- `Tools/MapAutomation/fixtures/poor_worker_dormitory_{1f,2f}.json`

## FILES MODIFIED

- `Tools/MapAutomation/semantic/pipeline.py` — opt-in safe slot namespace.
- `Tools/MapAutomation/room_generator/generator.py` — namespace passthrough.
- `Tools/MapAutomation/room_generator/gateway.py` — revision-safe cleanup batches по 32 операции.
- `Tools/MapAutomation/building_profile.json` — storey height привязан к measured wall module height.
- `Tools/MapAutomation/README.md` — Phase 8 CLI and fail-closed policy.
- `Docs/AI_MAP_GENERATOR_PLAN.md` — current milestone/status.

Production maps не изменены.

## VERIFIED / APPROXIMATE / UNKNOWN

### VERIFIED

Strict planner boundary; real semantic planner call; deterministic plan/layout; seed reproducibility/variation;
rect containment/non-overlap; shared wall/portal graph; exterior-to-room connectivity; RoomGenerator reuse;
required failure; optional degradation; dry-run immutability; budget report; offline 1F/2F acceptance.
Также verified: 1F live shell/full furnishing, staged read-back, three filesystem captures, manual 1F visual review,
building-wide cleanup >32 objects и точное восстановление исходной сцены.

### APPROXIMATE

Room size prototypes; 1.5 m corridor; structural contact/collision; wall/floor module overlap;
door sweep/approach; `SteelRustyStairs` footprint and landings; chunk hotspot warning threshold.

### UNKNOWN

Player capsule gameplay traversal; stair traversal/orientation; door runtime interaction; save/build/runtime load;
sustained building-scale performance.

## LIMITATIONS

Only rectangular upright worker dormitories are supported. No polygonal shell, universal room catalog,
clutter pass, whole-building Vision Critic, district, street or city generation. Door openings have no separate
curated lintel module, and non-scaled structural modules intentionally overlap to cover arbitrary footprints.

## PHASE 8 STATUS

`PARTIAL`

## READY FOR PHASE 9

`NO`
