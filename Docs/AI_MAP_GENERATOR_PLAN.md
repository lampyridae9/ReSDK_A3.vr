# AI Map Generator / AI Level Designer для Relicta

## Project Status

- Research: COMPLETE
- Automation Gateway: PHASE 1 COMPLETE
- Object Catalog: PHASE 2 COMPLETE — live reflection: 2894 OOP / 2305 GameObject / 2182 editor-placeable
- Existing Map Usage Mining: COMPLETE — 9 maps, 21170 placed objects, runtime counts matched
- Geometry Foundation: PHASE 2 COMPLETE — 41/41 Core probed; 41 M2C MATCH; explicit geometry/contact UNKNOWN fields retained
- Placement Solver: PHASE 3 COMPLETE — live Eden acceptance PASS, 9 generator-enabled curated assets
- Room Generator: PHASE 6 COMPLETE — full natural-language live generation PASS
- Vision Feedback: NOT STARTED
- Building Generator: NOT STARTED
- City Generator: NOT STARTED

## Current Milestone

`Phase 7 — Vision Feedback / Repair`

Архитектурный source of truth. Ниже сохранён полный результат исследовательской фазы; описания предлагаемых систем не являются утверждением об их реализации. Текущий ход реализации и инструкции тестирования: [MapAutomation README](../Tools/MapAutomation/README.md).

Текущее состояние Phase 1: `PASS`. Внутренние Eden create/read/update/delete, semantic ID,
save/load, screenshot, history, failure handling, stopped-state и reconcile подтверждены.
Автоматизированный Copy/Paste test подтвердил новый ID копии, uniqueness после Undo/Redo и
сохранение обоих ID после save/load. Data-only JSON FileManager transport и Python runner
подтвердили requestId idempotency, expectedRevision protection и полный внешний цикл в настоящем
Eden 2026-09-09. Transcript и engine-отчёты сохранены в `Tools/MapAutomation/artifacts`.
Содержимое PNG не анализируется автоматически: `REQUIRES MANUAL PNG REVIEW`.

Phase 2: `PASS`. Реализованы воспроизводимый анализ девяти существующих карт,
каталог source candidates, M2C geometry, curated набор из 41 объекта, валидаторы,
OOP reflection exporter и geometry probe через тот же Automation Gateway.
Подсчитано 21170 размещённых объектов / 939 используемых классов. Источник офлайн-каталога
не следует путать с подтверждённой editor availability: Eden reflection получен 2026-09-09,
2182 editor-placeable из 2305 GameObject; все 2303 source candidates найдены, дополнительно
5mm_ammo и 9vbattery. Все 41 Core модели разрешены и измерены fresh engine probe;
cleanup/scene preservation подтверждены для каждого и для batch. Historical/live comparison:
41 MATCH, без различий или missing data. Geometry LOD AABB валиден для 40/41;
degenerate профиль явно UNKNOWN. LandContact не дал named selections, а engine отклонил
`Roadway` enum для `selectionNames`, поэтому эти данные не выданы за доказательство контакта.
Строгий validator и 14 tests проходят. Placement/contact/semantic front остаются curated
APPROXIMATE или UNKNOWN там, где engine evidence недостаточно.
Отчёт: [Phase 2 results](AI_MAP_GENERATOR_PHASE2_REPORT.md).
Воспроизведение и отдельный engine test: [Catalog guide](../Tools/MapAutomation/CATALOG.md).
Phase 3 реализует deterministic placement layer на curated interior subset. Она не включает
RoomPattern, LLM, генератор комнаты или Vision Critic. Текущие результаты и воспроизведение:
[Phase 3 report](AI_MAP_GENERATOR_PHASE3_REPORT.md).

Phase 4: `PASS`. Реализован детерминированный слой `Structured Room Brief → RoomPattern →
RoomPlan → SemanticSlot → AssetResolver → PlacementIntent[] → Phase 3 dryRun`. Первый pattern
`poor_bedroom` поддерживает 1–4 жильцов, required/preferred/optional cardinality, три стратегии,
stable semantic IDs, feasibility preflight и structured diagnostics. Строгий Planner Contract
запрещает transforms, код и произвольные classname. Manual fixture для двух рабочих прошёл
offline и live Eden demonstration с read-back/cleanup; Phase 1–3 остаются `PASS`.
После visual review support transforms переведены на spatial catalog v2: bed, table, cabinet и
door откалиброваны в Eden placement frame и повторно подтверждены live screenshots.
Отчёт: [Phase 4 results](AI_MAP_GENERATOR_PHASE4_REPORT.md).

Phase 5: `PASS`. OpenAI Structured Outputs Planner переводит русский/английский natural-language
request в строгий brief; cache/replay, bounded repair, token/latency artifacts и one-call live path
подтверждены. Отчёт: [Phase 5 results](AI_MAP_GENERATOR_PHASE5_REPORT.md).

Phase 6: `PASS`. Orchestration, shell inspection, one-brief pipeline, bounded deterministic backtracking,
optional degradation, one-patch transaction, actual read-back validation, ownership, cleanup,
capture metadata, replay/regenerate и safe-by-default CLI реализованы. Offline matrix 4 capacities ×
3 sizes × 5 seeds: 60 controlled outcomes, 45 SUCCESS / 15 INFEASIBLE, navigation valid во всех
SUCCESS. Финальный live acceptance выполнил uncached LLM planning, one-patch apply, actual read-back,
final spatial validation, три screenshots, manual visual review и ownership cleanup с восстановлением
исходного fingerprint. Отчёт: [Phase 6 results](AI_MAP_GENERATOR_PHASE6_REPORT.md). Phase 7 — `NEXT`.

## Roadmap Revision — 2026-09-10

Ранний roadmap ниже отражал порядок исследовательских прототипов. После завершения реального
Automation Round-Trip и каталога нумерация зафиксирована заново, не меняя историю Phase 1/2:

| Phase | Назначение | Статус |
|---:|---|---|
| 0 | Research: editor architecture, map lifecycle, object system, feasibility | COMPLETE |
| 1 | Automation / Identity / Transport: Python ↔ Eden, stable IDs, revisions, typed ScenePatch, read-back, screenshots, safe-stop | PASS |
| 2 | Object Catalog / Geometry / Existing Map Mining: live reflection, geometry profiles, Core Asset Set, human-made maps | PASS |
| 3 | Placement Solver / Spatial Validation: support, orientation, OBB, clearance, doors, accessibility, deterministic candidates | PASS |
| 4 | Pattern System / Room Semantics: RoomPattern, roles, zones, semantic relations, AssetResolver, RoomPlan, Planner Contract | PASS |
| 5 | LLM Planner Integration: natural language → structured semantic plan | PASS |
| 6 | AI Single Room Generator: первый полный AI generation loop | PASS |
| 7 | Vision Feedback / Repair: screenshots → repair goals → deterministic correction | NEXT |
| 8 | Building Generator | PLANNED |
| 9 | District Generator | PLANNED |
| 10 | City Generator + Gamemode Integration | PLANNED |
| 11 | RP Evaluation | PLANNED |
| 12 | Optimization / Scale | PLANNED |

## AI Architecture: Planner / Solver / Critic

**Planner** — будущая LLM/reasoning model — отвечает на вопрос «что строить?»: назначение,
required/optional functions, стиль, социальная функция, отношения элементов, high-level pattern
и дизайнерские компромиссы. Planner выдаёт семантическое намерение и не вычисляет world transforms.

**Solver** — детерминированный код — отвечает на вопрос «как физически разместить?»: support,
orientation, точные transforms, intersections, clearance, door sweep, accessibility, генерация и
оценка candidates, затем typed ScenePatch. Именно этот слой создаётся в Phase 3.

**Critic** — будущий vision/reasoning слой — оценивает внешний вид и функцию по screenshots,
scene metadata, diagnostics и semantic structure. Он возвращает структурированные repair goals.
Critic не изменяет Eden: исправления снова разрешает Solver и применяет MapAutomation.

```text
Designer
   ↓
Natural-language request
   ↓
LLM Planner
   ↓
Semantic Design Plan
   ↓
Pattern System
   ↓
Placement Solver
   ↓
Spatial Validators
   ↓
ScenePatch
   ↓
MapAutomation
   ↓
Eden
   ↓
Screenshots + Runtime Validation
   ↓
Vision Critic
   ↓
Repair Goals
   ↓
Placement Solver
```

Фундаментальная граница: Planner может потребовать «две кровати вдоль стен с центральным
проходом», но не задаёт `SingleWhiteBed position/rotation`. Он передаёт `PlacementIntent`,
например asset `SingleWhiteBed`, relation `againstWall`, `keepAccessible=true`; Solver находит
валидный transform. `PlacementIntent` намеренно не содержит координат.

## 1. Executive Summary

**Систему реализовать можно. Итоговая оценка — High для предложенной гибридной архитектуры; Medium для полностью автономного создания законченных RP-городов без участия дизайнера.**

Главное положительное открытие: базовые механизмы уже существуют. Relicta располагает программируемым редактором поверх Eden, библиотекой игровых классов, сборщиком карт, системой потоковой загрузки объектов, экспортом габаритов моделей, программными камерами, генерацией скриншотов, процедурными пещерами и собственной навигационной системой.

Главная сложность — превратить эти механизмы в надёжный процесс проектирования. Сейчас нет единой семантической модели города, библиотеки проверенных пространственных паттернов, универсальных правил контакта объектов и транзакционного интерфейса для внешнего агента.

**Рекомендуемая архитектура:**

- внешний планировщик и детерминированный генератор;
- семантический граф города, зданий, комнат и связей;
- каталог реальных классов и геометрии моделей;
- небольшой адаптер внутренних функций редактора;
- существующие сохранение, сборка и игровой загрузчик;
- геометрические проверки до применения и проверки движком после применения;
- программные снимки сцены и ограниченный цикл визуальных исправлений.

LLM принимает дизайнерские решения. Обычный код вычисляет координаты, проверяет ограничения и применяет изменения.

**Граница исследования:** выводы основаны на чтении реализаций и цепочек вызовов. Arma 3 не запускалась для экспериментальной проверки, FPS не измерялся, скриншоты редактора в этой сессии не снимались. Репозитории не изменены. Поэтому ниже отдельно отмечены возможности, подтверждённые кодом, и проверки первого прототипа.

---

## 2. Current Map Architecture

### Карта существует в двух основных представлениях

| Представление | Хранение | Назначение |
|---|---|---|
| Редактируемая карта | `Src/Editor/Bin/Maps/*.cpp` | Сохранённая сцена Eden |
| Текущая рабочая сцена | `mission.sqm` | Файл миссии, открываемый Eden |
| Собранная игровая карта | `Src/host/MapManager/Maps/*.sqf` | Исполняемые инструкции создания объектов |
| Старые карты | `Src/host/MapManager/Maps old_editor/*.map` | Устаревший путь, не основа новой системы |

В текущем дереве обнаружены 17 редакторских `.cpp` и 16 игровых `.sqf`; это не означает соответствие файлов один к одному.

Название «бинарная карта» в коде может ввести в заблуждение. Например, [SandboxMap.cpp](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/Bin/Maps/SandboxMap.cpp:1>) — **текстовый конфигурационный формат Arma**, с `class EditorData`, `class Mission`, объектами, слоями, ID и `binarizationWanted=0`. Это не исходный C++ и не JSON.

Пути и расширения определены в [Core_pathes.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/Core/Core_pathes.sqf:8>).

### Что сериализуется у объекта

Eden сохраняет свои атрибуты: модель через конфигурационный класс, позицию, вращение, ID, слой и прочие данные сцены.

Relicta дополнительно сохраняет собственную карту свойств внутри атрибута Eden `init`:

```text
{
    createHashMapFromArray [
        ["class", "..."],
        ["customProps", createHashMapFromArray [...]],
        ...
    ]
}
```

Реальные ключи включают:

- `class`;
- `customProps`;
- `mark`;
- `prob`, `rdir`, `rpos`;
- `containerContent`;
- `edConnected`;
- `initCode`, `code_onInit`;
- `invisible`.

Сериализация реализована в `golib_serializeHashData`, чтение — в `golib_getHashData` и `golib_deserializeHashData`. Сейчас чтение выполняет `compile` сохранённого выражения: это **исполняемое представление данных**, а не безопасный универсальный формат обмена с AI. [GOLib_hashData.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/GameObjectsLibrary/GOLib_hashData.sqf:25>)

### Полный жизненный цикл

```text
Действия в Eden / внутренние функции Relicta
    ↓
Атрибуты Eden + Relicta hashData в init
    ↓
MissionSave → mission.sqm
    ↓
onSaving → mm_saveCurrentMapToFile
    ↓
Src/Editor/Bin/Maps/<name>.cpp

Редакторская сцена
    ↓
mm_build → mm_handleObjectSave
    ↓
Src/host/MapManager/Maps/<name>.sqf
    ↓
GamemodeFunctions → mapManager_load
    ↓
InitItem / InitStruct / InitDecor
    ↓
Создание OOP-экземпляра → InitModel → регистрация в NOEngine
    ↓
Клиент запрашивает соседние чанки
    ↓
noe_client_spawnObject → локальная модель, свет, анимация, радио
```

Подтверждённые детали:

- `mm_saveCurrentMapToFile` копирует уже сохранённый `mission.sqm`. Поэтому вызвать только эту функцию недостаточно для сохранения актуального состояния Eden.
- Автокопирование после сохранения зависит от `cfg_map_autosaveBinary`.
- `mm_build` собирает объекты из `all3DENEntities`, исключает служебное хранилище, проверяет классы и генерирует SQF.
- `mm_handleObjectSave` выбирает инициализатор по `getChunkType`, сохраняет свойства, содержимое контейнеров, метки, связи и код инициализации.
- Игровой `mapManager_load` проверяет версию, затем исполняет собранный SQF.
- Режим игры выбирает карту через `getMapName`.

Основные реализации: [Maps_manager_common.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/MapsManager/Maps_manager_common.sqf:20>), [Core_postInit.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/Core/Core_postInit.sqf:88>), [map_manager.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/MapManager/map_manager.sqf>), [NOEngine_initializers.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/NOEngine/NOEngine_initializers.sqf:8>).

### Альтернативный загрузчик

`DynamicMapLoader.sqf` содержит реальный путь:

```text
dml_loadMap
→ dml_parseMap
→ loadConfig
→ dml_prepMapConfig
→ BinaryMapInstructions
→ compile подготовленных инструкций
```

Он читает конфигурационную карту, включая дерево `Mission/Entities`. Однако найденный штатный запуск режима использует `mapManager_load` и собранный SQF. Не следует без необходимости менять этот путь.

`mm_virt_build` в редакторском `Maps_manager_virtualMap.sqf` — пустая заготовка. Её нельзя считать готовым виртуальным генератором. [DynamicMapLoader.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/MapManager/DynamicMapLoader.sqf:8>)

### Архитектурный вывод

**Не делать собранный SQF главным редактируемым документом AI.** Он содержит исполняемый код, часть переменных формируется из координат, а исходная дизайнерская иерархия в нём не сохраняется.

Источник состояния при работе — сцена Eden; рядом хранится дополнительный семантический документ генератора. SQF остаётся выходным игровым артефактом.

---

## 3. Editor Architecture

Редактор Relicta — расширение Eden с собственными компонентами:

- `Core`: события, настройки, файловый доступ, жизненный цикл;
- `GameObjectsAssembly`: сборка и рефлексия игровых классов;
- `GameObjectsLibrary`: каталог, создание объектов, метаданные;
- `GameObjectsInspector`: редактирование свойств;
- `MapsManager`: сохранение и сборка;
- `Simulation`: запуск игрового предпросмотра;
- `VisualComponents`: специализированные редакторы;
- `SystemTools`: проверки, свет, габариты, экспорт изображений.

Порядок подключения виден в [Editor_init.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/Editor_init.sqf:114>).

### Создание и трансформации

`golib_om_createObject`:

1. проверяет `InterfaceClass`;
2. определяет конфигурационный класс по игровой модели;
3. создаёт `create3DENEntity`;
4. записывает Relicta hashData;
5. применяет позицию и вращение;
6. подключает события;
7. отдельно обрабатывает `EffectClass`.

Позиция и вращение читаются и устанавливаются через `get3DENAttribute` / `set3DENAttribute`.

Основные функции:

- `golib_om_createObject`;
- `golib_om_getPosition`, `golib_om_setPosition`;
- `golib_om_getRotation`, `golib_om_setRotation`;
- `golib_getSelectedObjects`, `golib_setSelectedObjects`;
- `golib_searchObjectsBy`.

Реализация: [GOLib_objectManager.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/GameObjectsLibrary/GOLib_objectManager.sqf:77>).

### Выделение, копирование, слои

Множественное выделение реализовано через Eden. Копирование использует, в частности, `do3DENAction "CopyUnit"`. На `OnPaste` Relicta повторно подключает события объектов и синхронизирует метки.

Есть дерево слоёв, родительские и дочерние слои, скрытие и блокировка. **Слой — организационная структура, а не автоматически наследуемый transform здания.**

Для генератора дублирование лучше реализовать как явное клонирование набора объектов с новыми ID и переназначением внутренних связей, используя существующее создание объектов.

### Привязки и выравнивание

Подтверждены:

- сетка перемещения;
- сетка вращения;
- изменение шага через `bis_fnc_3DENGrid`;
- surface snapping через `SurfaceSnapToggle`;
- raycast-позиционирование;
- редактор относительных точек.

Это инструменты редактирования, **не готовый constraint solver**. Универсальной функции «поставь произвольную модель ножками на выбранный этаж» в исследованной цепочке нет.

Привязки подключены в [Widget_init.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/Widgets/Widget_init.sqf:73>).

### Undo/redo

Используется `collect3DENHistory`. Relicta слушает `onUndo` / `onRedo`, обновляет метки и обрабатывает служебные этапы истории.

Важные ограничения:

- некоторые setters по умолчанию не создают отдельный блок истории;
- код создания отмечает проблему истории в том же кадре;
- синхронизация меток может менять данные;
- история Eden не является долговременной системой версий семантического графа.

Реализация: [GOLib_cacheStorage.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/GameObjectsLibrary/GOLib_cacheStorage.sqf:144>).

### Камера и preview

Есть:

- `get3DENCamera`;
- `move3DENCamera`;
- программная фиксация цели камеры;
- отдельные камеры через `camCreate`;
- установка позиции, цели, FOV и переключение camera effect.

`golib_vis_jumpToSelected` вычисляет положение камеры из bounding box. [GOLib_visual.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/GameObjectsLibrary/GOLib_visual.sqf:655>)

Preview запускается через `sim_internal_processLaunchSim`: при соответствующей настройке собирает карту, записывает SDK-параметры и вызывает `MissionPreview`. Для нормального игрового теста нужен режим и роль. [Simulation_init.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/Simulation/Simulation_init.sqf:134>)

**Ответ на главный вопрос: да, AI может управлять сценой без эмуляции мыши. Но внешнего стабильного MapAutomation API сейчас нет.**

---

## 4. Object System

### Базовая модель

Игровые объекты определены SQF-макросами `class(...) extends(...)`.

Главные ветви:

```text
ManagedObject
└── GameObject
    ├── IDestructible
    │   ├── Item
    │   ├── IStruct
    │   └── Decor
    └── семейство BasicMob / Mob
```

OOP-сборщик формирует таблицы классов, наследования, полей и атрибутов. Для каталога следует читать результат этой сборки, а не пытаться восстановить всю семантику регулярными выражениями.

Подтверждены `__inhlist`, `__allfields`, `__allfields_map`, данные объявления и атрибуты. [oop_main_loader.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/OOP_engine/oop_main_loader.sqf:215>)

### Категории и фактическая семантика

В таблице «чанк» означает механизм загрузки NOEngine, а не гарантированный радиус видимости.

| Реальная категория / семейство | Назначение | Render behaviour | Геометрия и взаимодействие | Использование AI |
|---|---|---|---|---|
| `Decor` | Крупное окружение, стены, полы, здания, камни | DECOR, чанк 65 м | Зависит от модели; Decor не означает отсутствие коллизии | Оболочка города, крупные конструкции |
| `IStruct` | Стационарные структуры и функциональные объекты | STRUCTURE, 30 м | Базово simple object; игровые действия и повреждения задаются классом | Мебель, оборудование, небольшие конструкции |
| `Item` | Предметы мира, инвентаря и контейнеров | ITEM, 10 м для предмета в мире | Перенос, вес, размер, действия; возможны NGO-прокси | Лут, посуда, инструменты |
| `DynamicStruct` | Объекты с конфигурацией и анимациями | STRUCTURE; `createVehicleLocal` | Отличается от simple object | Анимируемые устройства и двери |
| `IStructNonReplicated` | Служебные объекты | Особая обработка репликации | Не обычный видимый объект окружения | Логические точки и зоны |
| `BigConstructions`, `BigHouse`, `BigFloor`, семейство больших стен | Крупная строительная геометрия | Наследуют DECOR | Проходимость определяется LOD модели | Здания, крупные полы, оболочки |
| `SmallWall`, `SmallFloor` | Небольшие строительные элементы | Через `Constructions`, ветвь STRUCTURE | Могут иметь игровую разрушаемость | Модульные интерьеры с учётом дистанции загрузки |
| `Furniture`, `IChair`, `BedBase`, семейства диванов и скамеек | Функциональная мебель | Обычно STRUCTURE | Посадочные точки, направления, пользовательские действия | Обстановка с рабочими зонами использования |
| `ItemBaseChair`, `IChairAsItem` | Переносимые стулья | ITEM | Посадка плюс поведение предмета | Мебель, которую игроки могут уносить |
| `IContainerStruct`, `SContainer`; контейнеры Item | Хранение | По базовой ветви | Вместимость, допустимый размер, содержимое, loot template | Шкафы, ящики, сумки |
| `DoorStatic` | Дверь со сменой позиции/направления | STRUCTURE | Геометрия перемещается программно | Проём и резерв пространства открывания |
| `DoorDynamic` | Анимированная дверь | STRUCTURE, dynamic model | Анимация и её репликация | Дверной модуль с состояниями |
| `ILightibleStruct`, `EffectAsStruct` | Свет и эффекты | STRUCTURE плюс эмиттеры | Свет не равен одному объекту рендера | Освещение, атмосферные эффекты |
| `ElectronicDevice`, `ElectronicDeviceNode` | Электропитание и устройства | По наследованию STRUCTURE | Связи, состояние, функциональность | Электрическая инфраструктура |
| `SpawnPoint`, `CollectionSpawnPoint` | Именованные точки появления | Наследуют `IStructNonReplicated` | Editor helper отличается от runtime | Точки ролей, группы случайного спавна |
| `TeleportBase`, `TeleportInteractible`, `LadderBase`, `SewercoverBase` | Специальные переходы | По конкретному классу | Не обязательно обычное пешее соединение | Лестницы, люки, переходы канализации |
| `BasicMob` / `Mob`, `ai_createMob` | Персонажи и AI | Отдельный actor lifecycle | Сеть, инвентарь, поведение, навигация | Через адаптер режима/NPC, не обычный InitStruct |

Базовые реализации: [Decor.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/GameObjects/Decors/Decor.sqf:25>), [IStruct.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/GameObjects/Structures/IStruct.sqf:22>), [Item.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/GameObjects/Items/Item.sqf:19>), [Spawners.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/GameObjects/Structures/Tools/Spawners.sqf:118>).

**INTERACTIVE, LIGHT, CONTAINER, FURNITURE — не дополнительные равноправные типы чанков.** Это возможности и семейства внутри основной объектной иерархии.

### Данные объекта

Существуют:

- classname и наследование;
- `model`, отображаемые имя и описание;
- `material`, параметры повреждений;
- вес и инвентарный размер;
- runtime `pointer`;
- `loc`, связывающий игровой объект с моделью или владельцем;
- состояния контейнеров, дверей, электроники;
- editor attributes и переопределения конкретного экземпляра.

**Инвентарный `size` нельзя использовать как геометрические размеры в метрах.**

Runtime `pointer` нельзя считать стабильным идентификатором между загрузками карты.

### Prefab и составные конструкции

`goasm_prefab_createPrefab` создаёт **новый игровой класс-наследник** с заданными свойствами и добавляет его в исходный файл. Это не библиотека комнат из нескольких объектов. [GOAsm_prefabCreator.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/GameObjectsAssembly/GOAsm_prefabCreator.sqf:152>)

Для составных сцен уже полезны слои, относительные точки, метки и связи. Но готового универсального механизма «экземпляр комнаты → дочерние объекты → адаптация размеров → регенерация» в исследованных реализациях не найдено.

### Render distance и performance budget

Фактический алгоритм:

```text
chunk = floor(position.xy / chunkSize)
loaded = текущий чанк + 8 соседей
```

Размеры:

| Тип | Сторона чанка | Сторона объединения 3×3 |
|---|---:|---:|
| ITEM | 10 м | 30 м |
| STRUCTURE | 30 м | 90 м |
| DECOR | 65 м | 195 м |

Это квадратная область, смещённая относительно игрока в зависимости от его положения внутри чанка. **Нельзя писать «Decor виден ровно на 65 м».**

Разбиение не учитывает Z. Этажи над одной XY-областью попадают в те же чанки. Источники: [NOEngine.hpp](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/NOEngine/NOEngine.hpp:8>), [NOEngine_Shared.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/NOEngine/NOEngine_Shared.sqf:8>), [NOEngineClientInit.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/client/NOEngineClient/NOEngineClientInit.sqf:159>).

В редакторе уже есть локальные эвристики:

- 80 Item на чанк;
- 100 IStruct на чанк;
- 150 Decor на чанк.

Они находятся в `pertest_optimalObjectCount`. Это **пороги существующего предупреждения**, а не доказанные пределы движка. Отдельный `pertest_start` прямо помечен `Not work`; действующую логику визуального подсчёта следует переиспользовать осмысленно. [PerformanceObjectsTest.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/SystemTools/PerformanceObjectsTest.sqf:9>)

Неправильная классификация опасна:

- крупная стена в STRUCTURE может выгружаться слишком близко;
- мелочь в DECOR увеличивает область её загрузки;
- замена функционального класса на Decor может потерять игровое поведение;
- одна большая модель не обязательно дешевле нескольких малых.

Клиент создаёт локальные visual objects; сервер хранит игровые экземпляры и рассылает изменения подписчикам чанков. Поэтому стоимость разделяется на серверную, клиентскую и сетевую. [NOEngineClient_ObjectManager.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/client/NOEngineClient/NOEngineClient_ObjectManager.sqf:11>)

Не найдены подтверждённые универсальные лимиты общего числа объектов карты, draw calls или интерактивных объектов. Найденный `ai_maxAICount=100` вне `EDITOR` — локальное ограничение создания AI, а не допустимое население города или multiplayer limit.

Нужно учитывать:

- число объектов на чанк и в объединении 3×3;
- все этажи;
- дополнительные NGO-объекты;
- фактическое число light/particle emitters;
- обновляемые устройства и NPC;
- объём и частоту сетевых изменений;
- клиентское время кадра, серверное время цикла, загрузочные пики.

Нельзя рассчитывать на активный дополнительный culling только по наличию файла: `NOEngineClient_Rendering.sqf` исключён из загрузчика, а `LESC_ENABLE_CULLING` в исследованном модуле света закомментирован.

---

## 5. Map Modification API

Статусы относятся к возможностям внутри запущенного редактора. Внешний транспорт ещё предстоит создать.

| Операция | Статус | Реализация и оговорки |
|---|---|---|
| Создать объект | **YES** | `golib_om_createObject` |
| Удалить объект | **YES** | `delete3DENEntities`; требуется корректная обработка связанных меток |
| Переместить | **YES** | `golib_om_setPosition` |
| Повернуть | **YES** | `golib_om_setRotation` |
| Прочитать объект | **YES** | getters transform, `golib_getHashData`, рефлексия класса |
| Изменить игровые свойства | **YES** | hashData/customProps; требуется проверка допустимости |
| Выделить несколько объектов | **YES** | `set3DENSelected`, обёртки GOLib |
| Дублировать | **PARTIAL** | Eden copy/paste есть; безопасное переназначение semantic ID и связей нужно добавить |
| Сохранить исходную карту | **YES** | `MissionSave` → подтверждение сохранения → `mm_saveCurrentMapToFile` |
| Собрать игровую карту | **YES** | `mm_build` |
| Загрузить исходную карту без диалога | **PARTIAL** | Низкоуровневые copy/reload уже есть; текущая пользовательская обёртка диалоговая |
| Undo/redo | **PARTIAL** | Eden history есть; нет общей транзакции с внешним графом |
| Масштабировать произвольный объект с сохранением в runtime | **PARTIAL** | Команды масштабирования встречаются, но сквозного поля scale в исследованном экспортном/сетевом формате нет |
| Создать NPC как обычный объект карты | **NO** | Для Mob отдельный путь; нужен адаптер режима и `ai_createMob`/существующего actor lifecycle |
| Вызвать всё это внешним агентом через готовый публичный API | **NO** | Такой фасад предстоит написать |

Удаление уже используется внутри операций замены модели в [GOLib_objectManager.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/GameObjectsLibrary/GOLib_objectManager.sqf:470>).

### Почему нужен адаптер

Некоторые функции зависят от:

- `inspector_allSelectedObjects`;
- `inspector_otherObjects`;
- `golib_internal_lastBatchUpdateMode`;
- текущего слоя;
- состояния истории и кэшей.

Например, `golib_setHashData` содержит логику массового изменения объектов инспектора. Вызов из внешнего агента должен явно изолировать этот контекст.

**Выбранный интерфейс:** ограниченные операции с типизированными данными. Не предоставлять LLM команду «выполнить произвольный SQF».

---

## 6. Visual Feedback Feasibility

**Программные снимки без мыши реалистичны и подтверждены существующим кодом.**

`GenerateItemIcons.sqf` уже:

1. создаёт камеру;
2. вычисляет ракурс из bounding box;
3. устанавливает позицию и FOV;
4. проверяет проекцию углов модели;
5. ожидает загрузку объекта;
6. вызывает `screenshot`;
7. восстанавливает камеру Eden.

Точка сохранения — [GenerateItemIcons.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/SystemTools/GenerateItemIcons.sqf:331>). Папки профиля обрабатываются в том же модуле.

`GenerateModelData.sqf` тоже содержит screenshot exporter, но одна из его функций прямо помечена `do not use`. Для нового сервиса лучше брать отдельные механизмы из рабочего экспорта иконок, не запускать весь старый exporter.

### Что возможно

| Возможность | Оценка |
|---|---|
| Сохранить изображение сцены программно | Да |
| Установить камеру в координаты | Да |
| Автоматически выбрать несколько ракурсов | Да, вычислением camera poses |
| Получить изображение без мыши | Да |
| Получить готовый render buffer как массив пикселей | В исследованном API не найдено |
| Получить depth/object-ID pass | Готовый путь не найден |
| Рендерить на dedicated/headless server | Не подтверждено; базовый подход требует графического клиента |
| Надёжно снимать свёрнутое окно | Не проверено |
| Получать состояние именно editor UI | Отдельный screen-capture слой при необходимости |

У команды `screenshot` есть ограничения хранения в профиле; сервис должен проверять результат и фактическое появление файла. [Документация Bohemia: screenshot](https://community.bistudio.com/wiki/screenshot)

### Рекомендуемый pipeline

```text
Применить patch
→ завершить обновление объектов/света
→ зафиксировать revision
→ выбрать обзорные и пользовательские ракурсы
→ установить камеру
→ дождаться стабилизации кадра
→ screenshot
→ проверить файл
→ передать изображение + camera metadata + semantic IDs
→ получить замечания
→ подтвердить геометрические замечания измерениями
→ подготовить ограниченный patch
→ повторить validation и съёмку
```

Для комнаты нужны:

- вид от входа;
- вид из противоположного угла;
- ракурс на функциональный центр;
- отдельный диагностический вид планировки.

Обзор без крыши допустим как диагностический режим, но визуальное качество и свет оцениваются также при штатной оболочке.

### Два вида визуального контроля

**Редакторский:** композиция, размещение, первичная плотность.

**Игровой:** фактическая загрузка по чанкам, рабочий свет, двери, интерактивность, вид от игрока.

Редактор уже умеет симулировать свет через `lsim_setMode`. Однако это не доказательство полной идентичности runtime. [LigthSimulation.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/SystemTools/LigthSimulation.sqf:116>)

В runtime перемещение только камеры недостаточно: NOEngine выбирает чанки по позиции игрока. Capture harness должен перемещать и наблюдателя либо явно обеспечивать нужную подписку.

**Vision-модель не должна выдавать точную глубину пересечения в метрах по одному изображению.** Она указывает подозрительную область и объекты; численное подтверждение делает геометрический слой.

---

## 7. Geometry Awareness

### Что уже доступно

| Данные | Доступность | Ограничение |
|---|---|---|
| Bounding box модели | Уже извлекается | Не описывает полости и проёмы |
| Размеры XYZ | Вычисляются из min/max | Не совпадают с инвентарным размером |
| Модельный origin/pivot | Через модельные координаты и преобразования | Не гарантирует контакт с полом |
| Orientation | Eden rotation, vectorDir/vectorUp | Семантический «перед» не всегда совпадает с осью |
| Raycast и нормаль поверхности | `lineIntersectsSurfaces` | Результат зависит от LOD |
| Walkable surface | Через ROADWAY-запросы навигации | Не вся видимая поверхность ходибельна |
| Collision bounds | Частично через bounding box по LOD | Не полноценный collision mesh |
| Контакт с полом/стеной/потолком | Универсального каталога нет | Нужно извлечение и проверка |
| Посадочные точки | Есть у соответствующих классов | Это точки использования, не опоры мебели |
| Door states | Есть поведение и параметры | Нужен вычисленный объём открывания |

### Уже существующая база габаритов

`systools_internal_generateModelData`:

- перебирает `CfgVehicles`;
- создаёт `createSimpleObject`;
- вызывает `boundingBoxReal`;
- пишет данные в `Src/M2C.sqf`.

`regmodel` формирует:

- `core_cfg2model`;
- `core_model2cfg`;
- `core_modelBBX`;
- отображение моделей в числовые ID.

Это готовая основа геометрического каталога. [GenerateModelData.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/SystemTools/GenerateModelData.sqf:24>), [ModelConfig_header.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/GENERATED/ModelConfig_header.sqf:10>).

Современный `boundingBoxReal` поддерживает выбор clipping type и отдельных LOD, включая Geometry и LandContact. Доступность нужного синтаксиса необходимо проверить на установленной версии Arma. [Документация Bohemia: boundingBoxReal](https://community.bistudio.com/wiki/boundingBoxReal?useskin=vector)

### Особый случай NGO

Relicta содержит таблицу моделей с дополнительной геометрией:

```text
model → offset, scale, proxy class
```

Прокси создаются отдельно на клиенте и сервере. Поэтому нужно различать:

1. видимую геометрию;
2. геометрию для попаданий/взаимодействий;
3. физические препятствия;
4. ROADWAY.

NGO нельзя автоматически считать физическим препятствием: код, в частности, отключает physics collision flag. [NOEngine_NGO.hpp](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/NOEngine/NOEngine_NGO.hpp:13>), [NOEngine_NGOServer.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/NOEngine/NOEngine_NGOServer.sqf:22>).

### Извлечение недостающих данных

Для каждого разрешённого в генераторе model/state:

1. получить visual и geometry bounds;
2. снять несколько ракурсов;
3. исследовать опорные поверхности лучами;
4. определить кандидаты floor/wall/ceiling anchors;
5. извлечь известные offsets использования;
6. проверить дверь в закрытом и открытом состоянии;
7. сохранить зоны доступа, открывания и обслуживания;
8. подтвердить критические anchors вручную или тестовой сценой.

Размещение выполняется относительно **явно выбранной поверхности**, а не «первого попадания вниз». Иначе в многоэтажном здании объект может попасть на крышу или другой этаж.

При контакте используется преобразованная локальная опорная точка. Простое вычитание `bbox.min.z` допустимо только для проверенного вертикального объекта на плоском полу.

### Навигация

Есть собственная HPA*:

- регионы 10×10 м;
- сетка с шагом 1 м;
- многослойные попадания ROADWAY;
- A*;
- обновление регионов;
- функции поиска пути;
- C++-ускорение через RVEngine.

Реализации: [HPAstar/core.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/AI/HPAstar/core.sqf:55>), [HPAstar/native.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/AI/HPAstar/native.sqf:11>).

Но текущая генерация:

- трассирует от фиксированной высоты до нуля;
- исключает terrain-попадания;
- содержит специальное исключение открытой верхней поверхности;
- проверяет соединения лучами, а не полным объёмом игрока.

Следовательно, её нужно **переиспользовать как навигационный backend**, дополненный проверкой ширины, высоты, ступеней и дверей. Копировать как окончательный AccessibilityValidator нельзя.

Для закрытых дверей нужны два графа: геометрическое состояние сейчас и потенциальная доступность при допустимом открывании. Замки проверяются с учётом роли.

---

## 8. Semantic Object Database

### Выбранный подход: hybrid

Источники в порядке надёжности:

1. рефлексия загруженных игровых классов;
2. измерения движка и данные M2C;
3. существующие интерфейсы, offsets, light configs, loot templates;
4. правила по наследованию и свойствам;
5. AI/vision-классификация стиля и контекста;
6. ручная проверка anchors и обязательных элементов.

**Classname — ключ идентичности, не достаточное описание назначения.**

### Предлагаемая структура

```text
ObjectType
  classname
  inheritance
  editorPlaceable
  editorAttributes
  effectiveProperties
  modelVariants[]
  chunkType
  capabilities[]
  semanticCategory
  semanticSubcategory
  contexts[]
  styles[]
  materialFamily
  placementRules
  geometryProfileId
  interactionProfileId
  costProfileId
  provenance
  confidence
  reviewed

GeometryProfile
  modelPath
  assetFingerprint
  visualBounds
  geometryBounds
  roadwayEvidence
  pivot
  semanticFront
  anchors[]
  supportSurfaces[]
  occupiedVolumes[]
  clearanceVolumes[]
  stateVariants[]
  ngoProfile

PlacementRule
  supportType: floor | wall | ceiling | socket | free
  allowedOrientations
  requiredClearance
  compatibleSockets
  allowedContacts
  forbiddenContexts
```

В `costProfile` хранить отдельные измерения и признаки: simple/dynamic, число эмиттеров, дополнительные прокси, серверные обновления, источник измерения. Не сводить стоимость к выдуманному `render_cost=5`.

Для каждого вывода сохранять происхождение: `source`, `engineMeasured`, `ruleDerived`, `visionSuggested`, `humanVerified`.

### Почему нужен каталог по модели и по классу

Одна модель может использоваться несколькими игровыми классами с разной функциональностью. Один класс допускает переопределение модели экземпляром.

Поэтому:

- геометрия кешируется по модели и состоянию;
- поведение — по классу;
- итоговые параметры экземпляра объединяют класс и `customProps`.

Наличие P3D в соседнем GameAssets само по себе не означает доступность модели в запущенной игре: нужно подтвердить загруженный addon/config. Начальный каталог строится по текущему загруженному набору ресурсов.

---

## 9. Proposed Architecture

```text
Запрос дизайнера
       ↓
Brief Planner
       ↓
DesignGraph: функции, районы, комнаты, маршруты, роли
       ↓
Pattern Planner ← ObjectCatalog + PatternLibrary
       ↓
Детерминированный Layout / Placement Solver
       ↓
Предварительные validators + бюджет
       ↓
ScenePatch со стабильными ID
       ↓
Automation Gateway → внутренние функции Relicta/Eden
       ↓
Прочитанное обратно состояние сцены
       ↓
Проверки движком + игровой preview
       ↓
CaptureService → изображения + ракурсы + ID
       ↓
VisionReviewer
       ↓
Ограниченные замечания и repair goals
       └────────→ повторный solver / patch
```

Все состояния связаны с revision и snapshot.

### Представление пространства

Выбираю сочетание:

- **семантический граф**: назначение и социальная роль;
- **иерархия владения**: город → район → здание → комната → объект;
- **граф связности**: улицы, проёмы, лестницы, люки, телепорты;
- **полигоны помещений и поверхности этажей**;
- **пространственный индекс AABB/OBB** для объектов;
- **локальные occupancy grids** для проверки интерьеров;
- **существующая HPA*** для проверки реальной сцены.

Полный плотный voxel-grid города не нужен как основное представление. Разрежённые объёмные данные допустимы локально для сложной геометрии.

Объект может принадлежать комнате, но участвовать в нескольких связях. Например, дверь принадлежит зданию и соединяет две комнаты; электропитание пересекает границы помещений. Поэтому дерево владения и граф связей должны быть разными структурами.

### Иерархия генерации

Предложенные уровни подходят с тремя изменениями:

1. обследование участка, выбор ассетов и бюджет предшествуют layout;
2. навигационные коридоры и функциональные зоны резервируются до мебели;
3. validation выполняется после каждого уровня, а не только в конце.

Последовательность:

```text
Brief и обследование
→ RP-функции и ограничения
→ граф районов и маршрутов
→ объёмы зданий и этажей
→ комнаты, проёмы, инженерные связи
→ функциональные объекты
→ мебель
→ декор
→ игровой и визуальный контроль
→ локальные исправления
```

### Patterns

Выбираю **адаптируемые patterns как основной способ генерации**.

Pattern комнаты задаёт:

- обязательные и необязательные функции;
- функциональные зоны;
- допустимые формы;
- входы и сервисные связи;
- наборы объектов;
- правила соседства;
- зоны доступа;
- стиль и плотность;
- ограничения и критерии качества.

Бар описывается через вход, зал, стойку, рабочую область, посадочные группы, склад и служебный доступ. Solver подбирает конкретные модули и размещение.

Размеры адаптируются выбором модулей, числом секций и раскладкой. Произвольное растягивание моделей в первой версии исключается.

### RP-семантика

Для зон хранить:

| Понятие | Формализация |
|---|---|
| Публичность | public / semi-public / private / restricted |
| Социальная функция | торговля, работа, лечение, управление, отдых |
| Вместимость | целевой одновременный спрос из сценария |
| Связи | обязана соседствовать / желательно рядом / должна быть отделена |
| Конфликт | зоны встреч, контроля, риска, отступления |
| Приватность | линии видимости и проверяемая акустическая модель |
| Навигация | доступность, альтернативные маршруты, читаемость входов |
| Скрытость | обнаружимость и альтернативный доступ |
| Событийность | свободное место и подключаемые сценарные точки |
| Принадлежность | роль, организация, доступ и ключи |

«Скрытая» зона не считается ошибочно недоступной, если её специальный путь явно указан. Акустическую приватность нельзя гарантировать только стенами на плане: её нужно отдельно сопоставить с работающей голосовой системой.

### Incremental editing

Команда «сделай Building_17 подпольной клиникой» превращается в изменение назначения узла, затем — в ограниченный patch.

Алгоритм:

1. найти узел по stable ID;
2. прочитать актуальную сцену;
3. определить затронутые зависимости;
4. сохранить закреплённые элементы;
5. пересчитать только необходимую область;
6. проверить соседние маршруты и связи;
7. применить diff;
8. сохранить before/after.

Изменение улицы затрагивает входы соседних зданий. Изменение стиля комнаты обычно не должно менять её оболочку.

Для существующих карт сначала создаётся инвентаризация и консервативная семантическая разметка. Неуверенно распознанные зоны не получают автоматического разрешения на перестройку.

---

## 10. AI vs deterministic responsibilities

| AI / reasoning model | Детерминированный код |
|---|---|
| Интерпретирует запрос | Проверяет структуру запроса |
| Определяет социальные функции | Рассчитывает площади и допустимость размещения |
| Выбирает patterns и стили | Подбирает совместимые размеры модулей |
| Предлагает связи районов | Строит и проверяет пространственный граф |
| Выбирает группы подходящих объектов | Размещает экземпляры и рассчитывает transforms |
| Решает дизайнерские компромиссы | Проверяет коллизии, опоры и доступ |
| Анализирует композицию | Измеряет плотность и геометрические зазоры |
| Предлагает локальное улучшение | Вычисляет patch и его границы |
| Объясняет результат | Обеспечивает ID, revision, snapshots и повторяемость |

VisionReviewer:

- оценивает визуальную читаемость и целостность;
- отмечает подозрительные пересечения и ошибки ориентации;
- предлагает дополнительные ракурсы;
- формирует цели исправления.

VisionReviewer **не применяет изменения сам**.

Если solver не находит допустимого решения, возвращается объяснение конфликта ограничений. Планировщик меняет pattern или требования. Система не должна молча сужать проходы и отключать проверки.

---

## 11. Required New Systems

| Система | Назначение |
|---|---|
| `AutomationGateway` | Типизированный интерфейс сцены, очередь операций и статусы |
| `SceneIdentity` | Stable ID, сопоставление Eden и семантических узлов |
| `DesignGraphStore` | Семантическая модель и версии |
| `ObjectCatalogExporter` | Извлечение рефлексии, моделей, возможностей |
| `GeometryProfiler` | Anchors, LOD bounds, состояния и зоны доступа |
| `PatternLibrary` | Комнаты, здания, районы и композиционные группы |
| `LayoutSolver` | Планировка, маршруты, комнаты |
| `PlacementSolver` | Размещение модулей, мебели и декора |
| `ValidationSuite` | Машиночитаемые ошибки и предупреждения |
| `CaptureService` | Камеры, снимки, привязка к revision |
| `VisionReviewer` | Визуальные замечания |
| `RepairPlanner` | Локальные исправления с ограниченным числом итераций |
| `RuntimeProbe` | Проверки в игровом режиме и измерение производительности |

### Validators

| Validator | Проверка |
|---|---|
| Schema/Class | Класс существует и допустим; свойства корректны |
| Transform | Координаты, ориентация, поддерживаемый масштаб |
| Geometry | Пересечения занятых объёмов |
| Support | Опоры, контакт со стеной/полом/потолком |
| Accessibility | Ширина, высота, связность, состояния дверей |
| Interaction | Доступ к посадке, контейнеру, прибору |
| References | Метки, электрические связи, переходы, spawn names |
| Pattern | Выполнение обязательных функций помещения |
| Performance | Чанки, эмиттеры, активность, измеренные бюджеты |
| RP | Доступ ролей, социальные центры, альтернативные пути |
| Visual | Плотность, ориентиры, однообразие и композиция |
| RoundTrip | Сохранение → загрузка → эквивалентное состояние |

Пример **предлагаемого**, а не уже существующего диагностического результата:

```text
severity: ERROR
code: ACCESS_PORTAL_BLOCKED
revision: ...
subjects: [Room_17, Door_4, Cabinet_9]
region: ...
evidence: измеренный свободный проход
required: ограничение профиля движения
repairHint: переместить Cabinet_9 вне зоны доступа Door_4
confidence: engineMeasured
```

Обязательно различать:

- точное измерение;
- пересечение приближённых bounds;
- эвристическое предупреждение;
- предположение vision.

Большой bounding box здания не означает, что его внутреннее пространство занято сплошной геометрией.

---

## 12. Existing Systems We Can Reuse

| Уже существующая система | Что переиспользовать | Что не считать готовым |
|---|---|---|
| GOLib object manager | Создание, transforms, выборка | Внешний транзакционный API |
| HashData и OOP reflection | Классы, поля, свойства, атрибуты | Полную пространственную семантику |
| MapsManager | Сохранение и сборку | Дизайнерский граф |
| NOEngine | Runtime spawn, чанки, репликацию | Автоматический бюджет качества/FPS |
| M2C и GenerateModelData | Модель↔config, bounding boxes | Anchors и точную форму проёмов |
| GenerateItemIcons | Камеру, подбор FOV, screenshot | Готовый scene capture service |
| LigthSimulation | Предпросмотр света | Полную эквивалентность runtime |
| HPA* и RVEngine | Региональные пути и обновления | Гарантированную проходимость игрока |
| CaveSystem | Сетку, ветвящиеся пути, callbacks размещения | Генератор RP-города |
| LootSystem | Контекстные наборы предметов | Расстановку мебели |
| SpawnPoint | Именованные spawn locations | Полное создание роли/NPC |
| Электрические связи | `edConnected`, метки, подключение | Автоматическое проектирование сети |
| Class/Light validators | Проверку существования и параметров | Универсальную проверку карты |
| PerformanceObjectsTest | Подсчёт объектов по чанкам | Измеренный FPS |
| Layers и RelativePositionEditor | Организацию и авторинг точек | Иерархию зависимых transforms |
| ReBridge / FileManager | Обмен SQF↔внешний процесс | Готовый протокол агента |

### Procedural generation действительно существует

`CaveSystem` хранит сетку, строит путь между входом и выходом, добавляет ветви, затем вызывает `preCreate`, `handleCreate`, `postCreate`.

Имеются конкретные генераторы `cave_preyLoad` и `cave_dirtpitLoad`, вызываемые игровыми режимами. Это не только демонстрационный комментарий. [CaveSystem.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/CaveSystem/CaveSystem.sqf:124>), [CaveSystemInit.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/CaveSystem/CaveSystemInit.sqf:69>).

Но в системе много глобального контекста, фиксированных предположений о блоках и случайных смещений. Её следует адаптировать как генератор пещерного окружения/туннелей, а не расширять до универсального редактора города.

### Loot уже семантически организован

LootSystem загружает YAML, имеет шаблоны и теги, вероятности и тематические коллекции: кухня, офис, инструменты, мусор и другие.

Контейнеры поддерживают `preinit@__lootTemplate`; редактор сохраняет и явное содержимое. [LootSystem_init.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/LootSystem/LootSystem_init.sqf:28>), [IContainer.Interface](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/host/GameObjects/Interfaces/IContainer.Interface:35>).

### Внешний обмен уже имеет фундамент

`rescript_callCommand` вызывает C#-модули. `ScriptContext.AddCallback` возвращает события в SQF. `FileWatcher` использует этот механизм.

Для первого прототипа достаточно существующего FileManager и небольшой очереди файлов. Текущий hot-reload watcher не следует использовать как очередь команд: он имеет собственные фильтры, хранение последнего события и зависимость от фокуса игры.

Источники: [ReScript.sqf](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/ReBridge/ReScript.sqf:30>), [FileWatcher.cs](</C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Scripts/FileWatcher.cs:11>).

---

## 13. Risks

### Technical risks

- Смешение ATL, ASL, PositionWorld, модельных координат и порядка координат config.
- Неполное соответствие геометрии editor/server/client.
- Зависимость внутренних функций от UI-контекста.
- Частично применённая операция при ошибке.
- Неатомарность сохранения нескольких файлов.
- Runtime-формат не содержит универсального scale.
- Ограничения буфера файлового моста: `file_read` уже обрабатывает `$BUFFER_OVERFLOW$`.

### AI risks

- Выбор существующей модели с неподходящим поведением.
- Выдуманные свойства и несовместимые функции.
- Попытки исправлять геометрию по неточным визуальным оценкам.
- Циклические исправления: улучшение одного ракурса портит другой.
- Формальная оптимизация RP-метрик без интересного игрового пространства.

### Performance risks

- Перегрузка соседних чанков, особенно по вертикали.
- Массовые light/particle emitters.
- Слишком много постоянно работающих устройств и NPC.
- Скачки времени кадра при входе в плотный чанк.
- Ошибочное предположение, что simple object бесплатен.
- Массовое использование runtime-random scatter, нарушающего проверенную планировку.

### Editor limitations

- Графическая сессия нужна для выбранного screenshot pipeline.
- Undo Eden не заменяет snapshots.
- Загрузка сцены перезапускает редактор.
- Некоторые validators исправляют данные, а не только читают их.
- Синхронизация меток может переименовать дубликаты и удалить некорректные связи.

### Content / metadata problems

- Неодинаковые pivots и семантические направления.
- Неполная или некорректная геометрия моделей.
- Визуально похожие объекты с разной игровой функцией.
- Отсутствие socket metadata для большинства строительных модулей.
- Устаревание каталога после обновления addons.

### Map quality problems

- Монотонные повторяющиеся комнаты.
- Формально связная, но плохо читаемая навигация.
- Недостаточная приватность.
- Избыточные расстояния между социальными центрами.
- «Красивые» помещения, где нельзя пользоваться мебелью.
- Несоответствие карты ролям, экономике и сценарию режима.

---

## 14. MVP

**Лучший MVP — бедная спальня с небольшим коридором и рабочей дверью, а не изолированная красиво обставленная коробка.**

Коридор нужен, чтобы проверить реальный вход, доступность и направление открывания.

### Вход

```text
Создай бедную спальню на два спальных места.
Нужны хранение вещей, небольшой стол и локальный свет.
Сохрани свободный путь от двери к обоим спальным местам.
```

### Ограничения MVP

- только проверенный набор существующих классов;
- один этаж;
- один модульный строительный комплект;
- единичный scale;
- фиксированный seed;
- никаких новых моделей и игровых классов;
- работа в отдельной тестовой карте;
- существующий минимальный режим preview;
- без NPC и сложной электросети.

### Проверяемый цикл

1. Выбор pattern и стиля.
2. Создание пола, стен, потолка и дверного проёма.
3. Установка рабочей двери.
4. Расстановка кроватей, хранения, стола и света.
5. Умеренный декор.
6. Проверка опор, пересечений и проходов.
7. Снимки с нескольких ракурсов.
8. Vision review.
9. Локальная коррекция.
10. Сохранение, сборка, повторная загрузка.
11. Проверка в игровом режиме.
12. Undo/redo и восстановление snapshot.

### Критерии успеха

- Все обязательные функции помещения выполнены.
- Нет неподтверждённых критических геометрических ошибок.
- Игрок проходит от коридора к функциональным точкам.
- Дверь работает в обоих состояниях.
- Объекты не перемещаются неожиданно после round trip.
- Повтор запроса с тем же seed и версией каталога воспроизводит результат.
- Повторная доставка одного patch не создаёт дубликаты.
- Исправление интерьера сохраняет оболочку и ID незатронутых объектов.
- В тестовой сцене с намеренно внесённой ошибкой полный цикл обнаруживает и исправляет её.
- При неудаче исправления восстанавливается последняя валидная версия.

Перед этим MVP нужен ещё меньший **интеграционный прототип без AI**.

---

## 15. Historical Development Roadmap

Этот раздел сохранён как исследовательский baseline. Актуальная нумерация и статусы находятся
в **Roadmap Revision — 2026-09-10** в начале документа.

| Этап | Цель и реализация | Зависимости | Критерий готовности |
|---|---|---|---|
| **Phase 0 — Research baseline** | Зафиксировать найденные API, версии, координатные соглашения и тестовые сцены | Текущий отчёт | Есть проверяемый integration test plan |
| **Phase 1 — Automation + identity** | Типизированные операции, очередь, stable ID, read-back, rollback | Phase 0 | Внешний процесс меняет сцену без мыши; повтор запроса безопасен |
| **Phase 2 — Early capture + round trip** | Камера, screenshot, save/load/build, snapshot | Phase 1 | Полный цикл проходит на нескольких объектах; снимок соответствует revision |
| **Phase 3 — Object catalog** | Экспорт рефлексии, моделей, bounds, capabilities, curated allowlist | Phase 1 | Каждый MVP-объект имеет проверенный профиль |
| **Phase 4 — Placement + validators** | Опоры, sockets, OBB/occupancy, clearance, бюджет чанков | Phase 3 | Набор геометрических тестов проходит и в editor, и в runtime |
| **Phase 5 — Single room** | Pattern спальни, детерминированная раскладка, семантический brief | Phases 2–4 | Комната и коридор воспроизводимо проходимы |
| **Phase 6 — Visual repair** | Vision замечания, локальные patches, остановка цикла | Phase 5 | Намеренные дефекты исправляются без регрессий |
| **Phase 7 — Buildings** | Несколько комнат, этажи, лестницы, служебные связи | Phase 6 | Здание связно, двери и вертикальные переходы проверены |
| **Phase 8 — Districts** | Улицы, площади, фронты зданий, ориентиры | Phase 7 | Район имеет требуемые функции и альтернативные маршруты |
| **Phase 9 — Cities + gamemode integration** | Межрайонный граф, роли, spawns, торговые/сервисные функции | Phase 8 | Карта запускается как целевой игровой сценарий |
| **Phase 10 — RP evaluation** | Плейтесты, доступ ролей, социальные потоки, приватность | Phase 9 | Оценка подтверждается игровыми сессиями, не только метриками |
| **Phase 11 — Optimization and scale** | Калибровка стоимости, streaming hotspots, ускорение solver | Все этапы | Целевые карты укладываются в измеренные бюджеты |

Performance validation начинается с ранних этапов. Последний этап — масштабирование и настройка, а не первое знакомство с производительностью.

### Versioning и undo

С самого Phase 1 нужны:

- неизменяемые snapshots исходной карты и семантического документа;
- журнал операций;
- revision у сцены;
- соответствие revision → граф → screenshots → validation;
- группировка изменений через Eden history;
- обновление внешнего состояния при undo/redo;
- восстановление после перезапуска;
- отдельные seeds для районов, зданий и комнат.

Частичная регенерация сохраняет внешние соединения и закреплённые элементы. Изменение комнаты не должно менять seed соседнего района.

---

## 16. Recommended first implementation

### Первый шаг: Automation Round-Trip Probe

**Не начинать с LLM.** Сначала доказать, что внешний процесс может надёжно управлять небольшой сценой, получать результат и восстанавливать состояние.

### Первые новые модули

В каталоге `C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Src/Editor/MapAutomation/` создать:

- `MapAutomation_init.sqf` — регистрация, lifecycle, события;
- `MapAutomation_api.sqf` — операции сцены, изоляция контекста, ID и read-back;
- `MapAutomation_transport.sqf` — приём небольших запросов, очередь, ответы;
- `MapAutomation_capture.sqf` — камера и снимок текущей revision;
- `MapAutomation_tests.sqf` — интеграционные проверки в Eden.

Внешний runner расположить в `C:/Users/lampyridae/Documents/Arma 3/missions/ReSDK_A3.vr/Tools/MapAutomation/`.

Это предлагаемые пути; файлы сейчас не создавались.

### Изменения существующего кода

1. Подключить компонент в `Editor_init.sqf` перед `Core_postInit`.
2. Добавить документированное editor-only поле `__ai` в список hashData-ключей.
3. Обработать создание, paste, удаление, undo и redo для semantic ID.
4. Использовать текущие MapsManager и FileManager; игровой загрузчик не менять.

`__ai` хранит только идентичность и связь с графом: object ID, parent node ID, provenance. Полный граф остаётся во внешнем документе.

Существующие `mark` сохраняются для игровых ссылок. Не заменять их semantic ID и не назначать глобальную runtime-метку каждой декорации.

### Минимальный контракт

```text
Request:
  protocolVersion
  requestId
  sessionId
  mapId
  expectedRevision
  operation
  arguments

Response:
  requestId
  status
  revision
  result
  diagnostics[]
```

Начальные операции:

```text
getCapabilities
inspectScene
inspectObjects
applyPatch
captureViews
saveSource
buildRuntime
loadSource
undo
redo
restoreSnapshot
```

Patch содержит только:

```text
create
delete
setTransform
setProperties
assignSemanticParent
```

Модель transforms: мировая позиция модельного origin в абсолютной системе и `vectorDir/vectorUp`. Адаптер преобразует её в Eden и проверяет результат чтением обратно. Нельзя отождествлять эту позицию с `getPosATL` для всех моделей.

В первой версии `scale=1`; другое значение отклоняется с понятной ошибкой.

### Выбранный транспорт первого прототипа

Локальная файловая очередь поверх существующего FileManager:

- внешние документы и журнал — JSON;
- сообщения в SQF — ограниченное представление простых массивов;
- разбор через `parseSimpleArray`, без выполнения поступившего кода;
- файл запроса публикуется атомарным переименованием;
- сцена изменяется последовательно в основном контексте редактора;
- большие ответы разбиваются на страницы с учётом фактического буферного лимита;
- запрос с уже завершённым `requestId` возвращает прежний результат;
- несовпадение revision останавливает применение;
- очередь хранится вне дерева hot-reload исходников.

Для первой версии новый C# networking service не нужен. Его можно добавить позже, сохранив контракт.

### Семантика транзакции

1. Проверить запрос и preconditions.
2. Снять before-state.
3. Очистить влияние batch-контекста инспектора на время операции.
4. Применить ограниченный набор изменений.
5. Прочитать фактические transforms и свойства.
6. Проверить ID, ссылки и результат.
7. Зафиксировать revision и snapshot.
8. Вернуть успех только после read-back.

При ошибке вернуть before-state; если восстановление невозможно — остановить очередь и явно отметить частичное состояние. Не продолжать генерацию поверх неизвестного результата.

Историю Eden и семантические версии связать служебной revision в common storage. При undo/redo восстанавливать соответствующий семантический snapshot и сверять сцену.

### Обязательные тесты первого шага

- создание известных классов `BigConcreteFloor`, `ConcreteGreenWall`, `WoodenArch`;
- перемещение и наклон с чтением фактического transform;
- сохранение, загрузка и сравнение;
- сборка через `mm_build`;
- снимки с заданных ракурсов;
- undo/redo создания, перемещения и удаления;
- чужое выделение и активный инспектор не затрагиваются;
- повторная доставка запроса;
- ошибка посередине patch;
- дублирование объекта создаёт новый semantic ID;
- сохранение русских строк;
- обработка блокировки файла и переполнения ответа.

Критический итог прототипа: **после сохранения, загрузки и отката сцена соответствует ожидаемому состоянию, а снимок однозначно связан с её версией.**

---

## Какую архитектуру я выбрал бы сам

Я выбрал бы **внешний Python-процесс с семантическим графом и детерминированным solver, соединённый с Relicta небольшим SQF Automation Gateway**.

Внешний процесс отвечает за планировку, каталог, patterns, версии и обращения к AI. Внутри Arma остаются операции Eden, геометрические запросы, проверки реального поведения и рендер.

Причины выбора:

1. Внутренние операции редактора уже существуют.
2. Не требуется менять формат игровых карт и сетевую архитектуру.
3. Сложные алгоритмы удобно тестировать отдельно от SQF.
4. Графические и collision-проверки остаются в движке, где видна настоящая модель.
5. Семантический граф обеспечивает локальное редактирование.
6. Patterns делают качество воспроизводимым.
7. AI можно подключать последовательно, не ставя надёжность сохранения в зависимость от модели.

Сцена Eden остаётся авторитетным фактическим состоянием. Семантический документ описывает намерение и структуру. Перед каждым patch эти представления сверяются.

**Не строил бы систему на управлении мышью, свободном генерировании SQF или выдаче LLM списка тысяч координат.**

---

## VERDICT

1. **Реализуемо ли вообще?**  
   Да. Ключевые механизмы редактора, объектов, загрузки и изображения уже есть.

2. **Можно ли создавать полноценные RP-города?**  
   Да, постепенно: через проверенные patterns, семантический граф, validators и плейтесты. Полная автономность высокого качества пока не доказана.

3. **Может ли AI работать через текущий editor?**  
   Да, через новый фасад существующих внутренних функций Eden/Relicta.

4. **Может ли получать screenshots?**  
   Да. Программный screenshot pipeline уже используется в проекте. Надёжность автоматического цикла нужно проверить на установленной Arma.

5. **Самые сложные части?**  
   Семантика ассетов, опоры и проёмы, соответствие editor/runtime, локальная регенерация, RP-качество и производительность города.

6. **Что уже сильно облегчает задачу?**  
   GOLib, MapsManager, NOEngine, M2C, screenshot exporter, HPA*/RVEngine, CaveSystem, LootSystem, слои, метки и игровые интерфейсы.

7. **Главное неизвестное сейчас?**  
   Насколько устойчиво полный автоматический цикл сохраняет геометрию и состояние при переходах editor → save/load → runtime, особенно для дверей, NGO и многоуровневых проходов.

8. **Первый технический прототип?**  
   Automation Round-Trip Probe без LLM: создать → изменить → прочитать → сохранить → загрузить → снять изображение → откатить.

9. **Размер проекта?**  
   **Очень большой** для автономного проектировщика RP-городов. Комнатный MVP значительно меньше и может последовательно проверить фундаментальные гипотезы.

10. **Есть ли архитектурная причина отказаться?**  
    Нет. Есть причина строго ограничить первые версии: проверенные ассеты, модульные patterns, неизменённый runtime и измеряемые критерии качества. Текущая Relicta даёт достаточный фундамент для такого подхода.

---

## Phase 5 — LLM Planner Integration

Состояние: **PASS**. Structured Planner, real-model evaluation, deterministic dry-run и natural-language live test на `AI_AutomationProbe` завершены.

Граница Phase 5: OpenAI Responses API переводит natural-language запрос только в `planner_room_brief.schema.json`. Локальная validation обязательна. PatternPipeline, AssetResolver, PlacementSolver и MapAutomation по-прежнему единолично выбирают assets, transforms и операции Eden.

Production provider: `OpenAIResponsesProvider`; модель по умолчанию `gpt-5.6-luna`, меняется через `RELICTA_PLANNER_MODEL`. Prompt: `room-planner-v1`. Контекст ограничен bedroom, стилями и функциональными ролями. Максимум две попытки; schema/semantic ошибки допускают repair, provider/timeout/refusal завершаются сразу, spatial ошибки модели не возвращаются.

CLI: `run_planner.py` работает в plan-only по умолчанию, `--dry-run` запускает deterministic stack без Eden, `--live` явно разрешает тестовую запись через существующий gateway `AI_AutomationProbe`. `--fixture` воспроизводит сохранённый brief без сети.

Неоднозначная «комната для двух» получает `UNSUPPORTED_REQUEST` с diagnostic `AMBIGUOUS_ROOM_TYPE`. Неподдерживаемые room types отклоняются локально и не превращаются в bedroom.
