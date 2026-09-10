# Phase 2 — Object Catalog + Geometry Foundation + Existing Map Usage Mining

## LIVE VALIDATION — 2026-09-09

Статус: **PASS**. Полный live batch выполнен через настоящий Eden gateway на
`AI_AutomationProbe`, Arma 3 Stable 2.22.154045, generation `96.902`, revision 0.
Загружено **2894 OOP-класса**; ветка GameObject — **2305**, из них **2182**
editor-placeable по контракту GOLib/CfgVehicles. Все **2303 source candidates** найдены;
дополнительные live классы — `5mm_ammo`, `9vbattery`.

Все **41/41 Core Asset** разрешены, созданы как local simple object, измерены и удалены.
Каждый результат имеет `cleanupVerified=true` и `sceneUnchanged=true`. Batch fingerprint
и `simpleObjectCount=3` до/после совпали; production maps не открывались и не сохранялись.
Historical M2C сохранён отдельно. Сравнение: **41 MATCH**, 0 MINOR_DIFFERENCE,
0 SIGNIFICANT_DIFFERENCE, 0 MISSING_DATA.

Fresh visual AABB/dimensions и model origin получены для 41/41. Geometry LOD AABB валиден
для 40/41; у `MediumPileOfDirtAndStones` движок вернул одну точку, поэтому поле явно UNKNOWN.
LandContact query выполнен, но named selections пусты у 41/41 — это не доказывает отсутствие
LOD. Эта версия движка отклоняет `Roadway` как enum для `selectionNames`; ROADWAY evidence
у 41/41 явно UNKNOWN с причиной. Bounding boxes нигде не названы точной collision geometry.

Для `WoodenDoor` подтверждены animation source `xlamdoor`, closed phase 0, configured open
phase 0.7 и read-back восьми фаз 0.0…0.7. Memory selection `xlamdoor_axis` измерен;
hinge side `negativeX` — APPROXIMATE ruleDerived (confidence 0.7). Движение именованной
Geometry selection между крайними фазами измерено, однако semantic front, физическое
направление открывания и interaction clearance остаются UNKNOWN. Union sampled AABB хранится
как APPROXIMATE и не считается continuous collision sweep.

Добавлены `compare_live_catalog.py`, `ingest_live_catalog.py`, `test_live_catalog.py`.
Ingest обновил live-часть без повторного mining девяти карт и сохранил historical M2C.
Строгий validator: integrity PASS, Phase 2 PASS, errors 0, pending 0. **14 Python tests PASS**.
Manual semantic/contact review остаётся требованием для Phase 3 placement policy, но не
блокирует завершение Phase 2; неизвестные поля сохранены как UNKNOWN.

## IMPLEMENTED

Воспроизводимый data-only parser Eden, независимая сверка runtime Init* calls, usage/frequency, model variants, spatial statistics, локальные composition candidates, M2C geometry, curated Core policy, reflection exporter и типизированный geometry probe через существующий gateway. Карты не изменены. Phase 1 не повторялась; PlacementSolver/RoomGenerator/LLM/Vision не реализованы.

## FILES CREATED

- `Src/Editor/MapAutomation/MapAutomation_catalog.sqf`
- `Tools/MapAutomation/{catalog_parser,build_catalog,export_catalog,compare_live_catalog,ingest_live_catalog,validate_catalog,test_catalog,test_live_catalog,report_catalog}.py`
- `Tools/MapAutomation/core_asset_policy.json`, `CATALOG.md`
- `Tools/MapAutomation/catalog/`: objects, source_declarations, reflection, models, geometry,
  engine_geometry, m2c_comparison, live_validation, usage, model_usage, maps, top_objects,
  core_assets, cooccurrence, terrain_neighbors, spatial, compositions, validation и instances
  для девяти карт
- Этот отчёт.

## FILES MODIFIED

- `Src/Editor/MapAutomation/MapAutomation_init.sqf`: include и generation.
- `MapAutomation_transport.sqf`: две разрешённые операции и revision guard.
- `MapAutomation_api.sqf`: объявление catalog capabilities.
- `Docs/AI_MAP_GENERATOR_PLAN.md`, `Tools/MapAutomation/README.md`: статус/ссылки.

## OBJECT CATALOG

Обнаружено **2303 source candidates**, **939 разных классов** реально встречаются в dataset.
Live reflection содержит **2305 GameObject-классов**, из них **2182 editor-placeable**.
Source candidate остаётся отдельным понятием и не считается автоматически placeable.
Здесь editor-placeable означает тот же технический контракт, что использует GOLib creation:
не `InterfaceClass`, CfgVehicles config разрешён (с EffectClass conversion). Среди них 15
имеют `HiddenClass`: их можно технически создать, но видимость в стандартном дереве зависит
от настройки `objlib_showHiddenClasses`. Атрибут сохранён, поэтому allowlist может их исключить.

Авторитетный exporter читает assembled `__inhlistCase`, `__motherClass`, `__allfields_map`, `__allmethods`, `_redit_attrib*`, GOLib config resolution и getChunkType. Effective properties экспортируются выражениями без вызова произвольных getters. Офлайн-индекс сохраняет literal values, остальные expressions и inheritance; интерфейсы и conditional compilation не исполняет.

Семейства: terrain, floor, wall, door, bed, table, chair, storage, container, light, rock, debris, garbage, mushroom, industrial, pipe, decoration. Capabilities по inheritance — свидетельства, а отсутствие совпадения не доказывает отсутствие функции. Интерактивность остаётся UNKNOWN.

Live inheritance evidence отмечает: item 813, container 469, seating 68, door 31,
light 48, electronic 54. Это пересекающиеся capability families, не взаимоисключающие
категории и не functional tests. Interactive capability намеренно UNKNOWN для всех классов.

`IStruct`: 560 объектов, **245 вариантов model**. Не включён как универсальный генераторный ассет: classname-only статистика скрывает разные модели.

`Decor`: 326 объектов, **106 вариантов model**. Не включён как универсальный генераторный ассет: classname-only статистика скрывает разные модели.

## EXISTING MAP ANALYSIS

Главный dataset: текстовые `Src/Editor/Bin/Maps/*.cpp`. Сравнение: одноимённые `Src/host/MapManager/Maps/*.sqf` (Detective runtime имеет нижний регистр). SHA-256 обоих источников сохранён. Source entities включает группы/слои, source objects — только Object. Items контейнеров не прибавляются к placed objects.

### minimap

- Source entities: **3177**; Object: **3168** → parsed Relicta: **3164** → recognized source classes: **3164**.
- Runtime direct Init*: **3164**; расхождений per-class: **0**.
- Исключения: nonRelictaObject=3, commonStorage=1.
- Top: `BlockDirt` 353, `Decor` 129, `BlockStone` 98, `LargeConcreteWallWithReinforcement` 62, `BlockBrick` 61.
- Три terrain-блока: **512 (16.18%)**; DECOR=687, STRUCTURE=1970, ITEM=507.

- `BlockDirt`: median nearest same-class origin **10.000 м**. Это измеренный шаг origins, не размер комнаты.

### saloonv2

- Source entities: **3826**; Object: **3710** → parsed Relicta: **3707** → recognized source classes: **3707**.
- Runtime direct Init*: **3707**; расхождений per-class: **0**.
- Исключения: nonRelictaObject=2, commonStorage=1.
- Top: `LargeConcreteWallWithReinforcement` 238, `BlockBrick` 173, `BlockStone` 143, `IStruct` 76, `Decor` 73.
- Три terrain-блока: **322 (8.69%)**; DECOR=569, STRUCTURE=2368, ITEM=770.

- `BlockBrick`: median nearest same-class origin **10.000 м**. Это измеренный шаг origins, не размер комнаты.

### barony

- Source entities: **2868**; Object: **2812** → parsed Relicta: **2809** → recognized source classes: **2809**.
- Runtime direct Init*: **2809**; расхождений per-class: **0**.
- Исключения: nonRelictaObject=2, commonStorage=1.
- Top: `BlockDirt` 115, `SmallDirtGrey` 113, `BigDarkRock` 112, `ShortPipeBlueMetal` 108, `ConcreteGreenSmallFloor` 75.
- Три terrain-блока: **178 (6.34%)**; STRUCTURE=1920, DECOR=371, ITEM=518.

- `BlockDirt`: median nearest same-class origin **9.000 м**. Это измеренный шаг origins, не размер комнаты.

### detective

- Source entities: **1091**; Object: **1088** → parsed Relicta: **1085** → recognized source classes: **1085**.
- Runtime direct Init*: **1085**; расхождений per-class: **0**.
- Исключения: nonRelictaObject=2, commonStorage=1.
- Top: `Decor` 97, `IStruct` 74, `LargeConcreteWallWithReinforcement` 52, `LampCeiling` 34, `BrickThinWall` 28.
- Три terrain-блока: **41 (3.78%)**; DECOR=152, STRUCTURE=728, ITEM=205.

- `BlockDirt`: median nearest same-class origin **10.194 м**. Это измеренный шаг origins, не размер комнаты.

### dorm

- Source entities: **2629**; Object: **2555** → parsed Relicta: **2552** → recognized source classes: **2552**.
- Runtime direct Init*: **2552**; расхождений per-class: **0**.
- Исключения: nonRelictaObject=2, commonStorage=1.
- Top: `MediumPileOfDirtAndStones` 195, `BlockStone` 165, `BigStoneWall` 164, `BlockBrick` 122, `IStruct` 65.
- Три terrain-блока: **293 (11.48%)**; STRUCTURE=1409, ITEM=617, DECOR=526.

- `BlockStone`: median nearest same-class origin **10.000 м**. Это измеренный шаг origins, не размер комнаты.

### truba

- Source entities: **3179**; Object: **3107** → parsed Relicta: **3104** → recognized source classes: **3104**.
- Runtime direct Init*: **3104**; расхождений per-class: **0**.
- Исключения: nonRelictaObject=2, commonStorage=1.
- Top: `BlockStone` 286, `BigGreenRock` 166, `BlockDirt` 160, `TrapEnabled` 132, `BigConcretePipe` 115.
- Три terrain-блока: **446 (14.37%)**; STRUCTURE=1637, ITEM=669, DECOR=798.

- `BlockStone`: median nearest same-class origin **9.404 м**. Это измеренный шаг origins, не размер комнаты.

### theatre

- Source entities: **2408**; Object: **2327** → parsed Relicta: **2324** → recognized source classes: **2324**.
- Runtime direct Init*: **2324**; расхождений per-class: **0**.
- Исключения: nonRelictaObject=2, commonStorage=1.
- Top: `BlockBrick` 186, `SmallBlueConcreteWall` 159, `ConcreteSmallFloor2` 151, `SheetMetalTinFence` 89, `ThickLightConcreteColumn` 85.
- Три terrain-блока: **186 (8.00%)**; STRUCTURE=1641, ITEM=358, DECOR=325.

- `BlockBrick`: median nearest same-class origin **10.000 м**. Это измеренный шаг origins, не размер комнаты.

### holiday

- Source entities: **2109**; Object: **2005** → parsed Relicta: **2002** → recognized source classes: **2002**.
- Runtime direct Init*: **2002**; расхождений per-class: **0**.
- Исключения: nonRelictaObject=2, commonStorage=1.
- Top: `WoodenSmallFloor` 83, `SpirtBottle` 81, `IStruct` 46, `LampCeiling` 46, `BlockStone` 40.
- Три terrain-блока: **70 (3.50%)**; STRUCTURE=1431, ITEM=427, DECOR=144.

- `BlockStone`: median nearest same-class origin **9.876 м**. Это измеренный шаг origins, не размер комнаты.

### hunt

- Source entities: **429**; Object: **426** → parsed Relicta: **423** → recognized source classes: **423**.
- Runtime direct Init*: **423**; расхождений per-class: **0**.
- Исключения: nonRelictaObject=2, commonStorage=1.
- Top: `BlockDirt` 151, `IStruct` 134, `Egg` 42, `Decor` 26, `SteelBrownContainer` 13.
- Три terrain-блока: **151 (35.70%)**; DECOR=177, STRUCTURE=171, ITEM=75.

- `BlockDirt`: median nearest same-class origin **10.378 м**. Это измеренный шаг origins, не размер комнаты.

## GLOBAL TOP OBJECTS

| Rank | Class | Count | Maps | Chunk | Category |
|---:|---|---:|---:|---|---|
| 1 | BlockDirt | 846 | 8 | DECOR | terrain |
| 2 | BlockStone | 805 | 7 | DECOR | terrain |
| 3 | IStruct | 560 | 9 | STRUCTURE | unclassified |
| 4 | BlockBrick | 548 | 5 | DECOR | terrain |
| 5 | LargeConcreteWallWithReinforcement | 509 | 8 | STRUCTURE | wall |
| 6 | Decor | 326 | 5 | DECOR | decoration |
| 7 | BigStoneWall | 322 | 8 | DECOR | wall |
| 8 | LampCeiling | 304 | 8 | STRUCTURE | light |
| 9 | MediumPileOfDirtAndStones | 300 | 6 | STRUCTURE | rock |
| 10 | SmallDirtGrey | 296 | 7 | STRUCTURE | decoration |
| 11 | SpirtBottle | 259 | 8 | ITEM | unclassified |
| 12 | WoodenSmallFloor | 204 | 6 | STRUCTURE | floor |
| 13 | WoodenDoor | 180 | 8 | STRUCTURE | door |
| 14 | SquareWoodenBox | 177 | 8 | STRUCTURE | container |
| 15 | ConcreteSmallFloor2 | 174 | 4 | STRUCTURE | floor |
| 16 | ShortRottenBoards | 174 | 8 | STRUCTURE | floor |
| 17 | BigGreenRock | 167 | 2 | DECOR | rock |
| 18 | DirtCraterLong | 166 | 6 | STRUCTURE | decoration |
| 19 | BigConcretePipe | 165 | 5 | STRUCTURE | industrial |
| 20 | EffectAsStruct | 161 | 6 | STRUCTURE | unclassified |
| 21 | SmallBlueConcreteWall | 161 | 2 | STRUCTURE | wall |
| 22 | WoodenChair | 153 | 7 | ITEM | chair |
| 23 | ThickLightConcreteColumn | 151 | 7 | STRUCTURE | unclassified |
| 24 | TrapEnabled | 146 | 3 | ITEM | unclassified |
| 25 | BrickThinWall | 141 | 7 | STRUCTURE | wall |
| 26 | SteelThinWallSmall | 139 | 8 | STRUCTURE | wall |
| 27 | TinFence | 131 | 6 | STRUCTURE | unclassified |
| 28 | StreetLamp | 129 | 7 | STRUCTURE | light |
| 29 | ShortPipeBlueMetal | 127 | 5 | STRUCTURE | pipe |
| 30 | SmallDirtBrown | 124 | 8 | STRUCTURE | unclassified |

Top 20: **31.38%**, Top 50: **47.73%**, Top 80: **56.84%**. 70–80% для первых 80 объектов в этом dataset не подтверждается. Это доли числа объектов, не занимаемой площади/объёма.

Глобальные пропорции: DECOR: **3749 (17.71%)**, STRUCTURE: **13275 (62.71%)**, ITEM: **4146 (19.58%)**. Top per chunk и per map доступны в JSON.

## TERRAIN / BASE GEOMETRY

| Map | BlockDirt | BlockBrick | BlockStone |
|---|---:|---:|---:|
| minimap | 353 | 61 | 98 |
| saloonv2 | 6 | 173 | 143 |
| barony | 115 | 0 | 63 |
| detective | 25 | 6 | 10 |
| dorm | 6 | 122 | 165 |
| truba | 160 | 0 | 286 |
| theatre | 0 | 186 | 0 |
| holiday | 30 | 0 | 40 |
| hunt | 151 | 0 | 0 |
| TOTAL | 846 | 548 | 805 |

Вместе **2199 объектов: 10.39% всех placed objects, 58.66% DECOR**. Dirt присутствует на 8 картах, Stone на 7, Brick на 5. Они действительно основные повторяемые terrain primitives, но доля числа объектов не равна доле геометрии.

В исходнике Dirt называется «Земля», Brick — «Кирпич», Stone — «Камень». Практическая трактовка Brick как тёмной почвы остаётся human hint. Все три резолвятся M2C в `rel_vox\obj\block_dirt.p3d`; размеры AABB ≈ **11.307 × 11.604 × 11.263 м**. Разные configs нельзя слить в один визуальный ассет. Цвет и текстуры требуют engine/config проверки.

Для многих карт median nearest spacing ≈9–10 м; размеры AABB больше шага. Это поддерживает интерпретацию перекрывающихся блоков как основы массы/поверхности. Но не доказывает непроницаемость коллизии. Настоящие grid дельты, yaw и ATL offsets сохранены в spatial.json.

Другие строительные опоры: `LargeConcreteWallWithReinforcement`, `BigStoneWall`, `WoodenSmallFloor`, `ConcreteSmallFloor2`, `BrickThinWall`, `ThickLightConcreteColumn`, `BigConcretePipe`. `MediumPileOfDirtAndStones`, `BigGreenRock`, `BigDarkRock` подходят для крупной вариации; `SmallDirtGrey`, `DirtCraterLong`, мусор и грибы — кандидаты на поверхностное оформление. Это interpretation source+usage, не engine semantic truth.

### Соседства terrain

Радиус 5м от центра 11-метрового блока часто не охватывает детали над поверхностью. Поэтому дополнительно посчитан 15м 3D origin radius; ниже реальные соседства (число пар, не число уникальных объектов). В JSON есть число anchors с таким соседом и median ΔZ.

- minimap / `BlockDirt`: `Decor` 406, `LargeConcreteWallWithReinforcement` 221, `SteelThinWallMedium` 212, `SleepingMatras` 212, `SmallDirtBrown` 206, `CollectionSpawnPoint` 186.
- barony / `BlockDirt`: `ShortPipeBlueMetal` 475, `SmallDirtGrey` 459, `TinFence` 399, `ShortRottenBoards` 299, `SmallStoneRoad` 290, `WoodenSmallFence` 193.
- dorm / `BlockBrick`: `MediumPileOfDirtAndStones` 678, `BigStoneWall` 415, `DirtCraterLong` 107, `BigStoneWall2` 75, `TrapEnabled` 64, `SmallStoneFragments` 50.
- truba / `BlockStone`: `TrapEnabled` 418, `DirtCraterLong` 254, `ShortRottenBoards` 237, `SmallDirtGrey` 231, `EffectAsStruct` 214, `MediumPileOfDirtAndStones` 191.
- hunt / `BlockDirt`: `IStruct` 1088, `Egg` 298, `Decor` 193, `SteelBrownContainer` 103, `LampCeiling` 78, `SteelMedicalBox` 78.

Эти результаты различают базовую массу и соседний detailing статистически. Порядок размещения автором, опора на конкретную поверхность и причинная связь из них не следуют. Scatter камней не заменяет terrain foundation.

## CORE ASSET SET

**41 кандидатов**, отдельная curated policy. Это подготовленный review set; `generatorAllowed=false` до проверки. Отбор сочетает usage, source family, M2C resolution и размер/роль. Никаких автоматически объявленных humanVerified свойств.

- **terrain**: `BlockDirt`, `BlockStone`, `BlockBrick`.
- **floor**: `ConcretePanel`, `WoodenSmallFloor`, `ConcreteSmallFloor2`.
- **wall**: `LargeConcreteWallWithReinforcement`, `ConcreteGreenWall`, `BrickThinWall`.
- **door**: `WoodenDoor`, `SteelDoorThinSmall`, `WoodenArch`.
- **bed**: `SingleWhiteBed`, `SleepingMatras`, `BedOld`.
- **table**: `MediumWoodenTable`, `SmallWoodenTable`.
- **chair**: `WoodenChair`, `ChairCasual`, `BrownLeatherChair`.
- **storage**: `Shelves`, `WoodenSmallShelf`.
- **light**: `LampCeiling`, `Candle`.
- **container**: `SquareWoodenBox`, `SteelGreenCabinet`, `BoardWoodenBox`.
- **decoration**: `SmallDirtGrey`, `DirtCraterLong`.
- **rock**: `BigGreenRock`, `BigDarkRock`, `MediumPileOfDirtAndStones`.
- **garbage**: `ConcreteGarbage`, `SheetMetalGarbage1`.
- **debris**: `LogDebris1`, `ClothDebris1`.
- **mushroom**: `BigMushroom3`, `SmallMushroom1`.
- **industrial**: `PowerGenerator`, `IndPipeValve`, `BigConcretePipe`.

Для первого bedroom: `ConcretePanel` или `WoodenSmallFloor`, `ConcreteGreenWall` / `BrickThinWall`, `WoodenDoor`, `SingleWhiteBed`, `SmallWoodenTable`, `WoodenChair`, `SquareWoodenBox` / `SteelGreenCabinet`, `LampCeiling`. Это набор для будущего проектирования; совместимость модулей и clearance ещё не доказаны.

## GEOMETRY

Исторические M2C profiles и fresh engine probes есть у **41/41 Core Asset**. Все 41
visual bounds/dimensions совпали с M2C по принятому правилу MATCH. Geometry LOD AABB:
40 VERIFIED, 1 UNKNOWN (`MediumPileOfDirtAndStones`, degenerate point returned by engine).

| Class | Dimensions XYZ, m (AABB) | Placement proposal | Orientation proposal |
|---|---|---|---|
| BlockDirt | 11.307 × 11.604 × 11.263 | terrain | UNKNOWN |
| BlockStone | 11.307 × 11.604 × 11.263 | terrain | UNKNOWN |
| BlockBrick | 11.307 × 11.604 × 11.263 | terrain | UNKNOWN |
| ConcretePanel | 2.036 × 4.012 × 0.185 | free | UNKNOWN |
| WoodenSmallFloor | 3.827 × 3.540 × 0.269 | free | UNKNOWN |
| ConcreteSmallFloor2 | 2.832 × 4.572 × 0.248 | free | UNKNOWN |
| SingleWhiteBed | 1.192 × 2.286 × 0.947 | floor | vertical |
| SleepingMatras | 2.349 × 1.234 × 0.279 | floor | vertical |
| BedOld | 1.379 × 2.193 × 0.346 | floor | vertical |
| MediumWoodenTable | 1.167 × 2.210 × 0.865 | floor | vertical |
| SmallWoodenTable | 1.167 × 1.477 × 0.865 | floor | vertical |
| WoodenChair | 0.442 × 0.530 × 1.017 | floor | vertical |
| ChairCasual | 0.698 × 0.607 × 1.250 | floor | vertical |
| BrownLeatherChair | 1.377 × 1.049 × 1.054 | floor | vertical |
| LampCeiling | 0.424 × 0.416 × 0.443 | ceiling | vertical |
| Candle | 0.063 × 0.062 × 0.168 | floor | vertical |

Pivot [0,0,0] — подтверждённый model-space origin с world read-back, но не contact pivot.
MinZ — приблизительная опорная плоскость. Dimensions подтверждены для 41/41;
placement/orientation остаются curated proposals, semantic front и functional contact UNKNOWN.

Live probe создаёт local simple object по доверенному классу, измеряет boundingBoxReal,
Geometry LOD AABB, modelInfo и basis, удаляет объект и сверяет fingerprint. Все 41 cleanup
прошли. Probe не создаёт игровой runtime instance; взаимодействия и функциональная безопасность
этим не подтверждаются.

## SEMANTICS

Автоматически: source inheritance/capability families и осторожные classname rules. Из map usage: frequency, diversity, model variants, neighbors, step/yaw distributions. Curated: 41 конкретный класс, category, предполагаемое крепление/вертикальность. Human hints: три terrain-блока, сохранены отдельно. Все semantic reviews пока false.

Найдено **31 локально повторяющихся сигнатур** anchor+neighbors. Это кандидаты (5см translation quantization), не подтверждённые «стол+4 стула» или комнаты. Полные transforms выгружены для следующего анализа.

## VALIDATION

Integrity: **PASS**. Проверены сохранение количества Object, все nested items, исключения, 9 независимых runtime per-class counts, SHA-256, unique IDs, classname refs, parent chains, M2C bounds/dimensions, usage ranks/maps, Core refs/provenance.

14 tests проверяют parser fixtures, реальные Hunt/Minimap/SaloonV2 counts, 3D spatial pairs,
engine bounds, M2C comparison thresholds, смену модели, NaN и door phase read-back.
Live reflection/probe операции дополнительно подтверждены настоящим Eden batch.

Проблемы M2C/нефизических source candidates перечислены в validation.json; они не скрываются и не попадают в Core без профиля. Все размещённые классы dataset распознаны в source index, включая классы GameModes и FalloutPort parent alias. Это не заменяет проверку загруженных классов.

## MANUAL ENGINE TEST

Live test выполнен. Для воспроизведения точная последовательность и контракт находятся в
`Tools/MapAutomation/CATALOG.md`. Открыть только AI_AutomationProbe, дождаться READY и выполнить:

```powershell
python Tools/MapAutomation/export_catalog.py --geometry --timeout 45
python Tools/MapAutomation/ingest_live_catalog.py
python Tools/MapAutomation/validate_catalog.py --require-engine
python -m unittest discover -s Tools/MapAutomation -p "test*catalog.py" -v
```

Проверить reflection availability, 41 probe, RPT и неизменность сцены. Затем вручную проверить контакты, переднюю сторону, двери и interaction clearance. Phase 1 тесты не запускаются.

## PROBLEMS / LIMITATIONS

- 43 live класса не имеют historical M2C resolution; это в основном непредметные/base или ammo-related классы и не Core Asset.
- Geometry LOD у `MediumPileOfDirtAndStones` degenerate; поле остаётся UNKNOWN.
- LandContact named selections пусты у Core, ROADWAY enum недоступен через выбранный API; отсутствие LOD не утверждается.
- M2C исторический; config/model resolution не доказывает наличие актуального asset в установленном наборе модов.
- Bounding volumes не collision mesh; LandContact/ROADWAY support points, occupied mesh, clearance, wall/ceiling contact, door sweep остаются UNKNOWN.
- Source fallback не исполняет препроцессор и interfaces; обязательна сверка reflection.
- Не восстановлены комнаты, проходы или факт стыковки стены с полом. Нет утверждений о типичных размерах комнат.
- Co-occurrence зависит от размера карты, origins, плотности и радиуса; не нормализован как причинная связь.
- Подсчёт относится к этому dataset, не ко всем картам Relicta.

### Что размечать вручную

Semantic front; contact pivot/опорные точки; пригодность floor/wall/ceiling attachment; usable top surface; дверь/петля/сектор открывания; interaction и seating clearance; направление подхода; material/texture role; безопасность портированных/динамических моделей; семантика generic model overrides. Эти задачи нельзя надёжно закрыть одним classname или AABB.

## PHASE 2 STATUS

PASS

## RECOMMENDED PHASE 3

**Phase 3 — Placement Solver + Spatial Validation**:

1. Контракт model-space transforms, curated contacts и orientation для Core.
2. Детерминированное размещение по surfaces/sockets, broad-phase AABB/OBB с явной точностью.
3. Engine narrow checks для опоры, пересечений и ROADWAY.
4. Door/interaction clearance и связность прохода.
5. Typed patches через тот же gateway и небольшой набор позитивных/негативных тестов в отдельной карте.

Не реализовано в этой фазе.
