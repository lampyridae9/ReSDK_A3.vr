# Phase 2 — Object Catalog / Geometry / Existing Map Usage

Phase 1 остаётся PASS и не перезапускается. Phase 2: **PASS** — live reflection,
41 Core probes, M2C comparison и strict validation завершены. Итоги:
`Docs/AI_MAP_GENERATOR_PHASE2_REPORT.md`.

## Воспроизведение без Arma

Из корня репозитория (Python 3.10+, только стандартная библиотека):

```powershell
python Tools/MapAutomation/build_catalog.py --build
python Tools/MapAutomation/validate_catalog.py
python -m unittest discover -s Tools/MapAutomation -p test_catalog.py -v
python Tools/MapAutomation/report_catalog.py
python Tools/MapAutomation/build_catalog.py --top 30
python Tools/MapAutomation/build_catalog.py --class BlockDirt
```

Входы: девять найденных по basename `.cpp` в `Src/Editor/Bin/Maps`, соответствующие
`.sqf` в `Src/host/MapManager/Maps`, `Src/M2C.sqf`, декларации GameObjects/GameModes,
`core_asset_policy.json`, опциональные live `reflection.json` / `engine_geometry.json`.
Выходы: только `Tools/MapAutomation/catalog/` и отчёт в Docs. Карты не изменяются.
Ни исходные init, ни SQF runtime не исполняются.

## Авторитетность данных

`objects.json.authority=PROVISIONAL_SOURCE_INDEX` означает вспомогательный индекс
деклараций, **не** список реально загруженных editor-placeable классов. Он лексически
читает `class/extends`, литералы `var` и getters. Не вычисляет выражения, не раскрывает
Interface includes или условные препроцессорные ветки. Разрешает только локальные
простые псевдонимы parent, например `REPLACE_REQUIRED → FalloutPort`.
Неизвестные выражения сохраняются текстом. Это дополнение для офлайн-анализа,
а не замена OOP reflection. Полный экспорт реализован отдельно через gateway.

Текущий live export содержит 2305 GameObject-классов и 2182 editor-placeable.
Source-only классы не подмешиваются в авторитетный каталог. `editorPlaceable` означает:
нет InterfaceClass,
конфигурация GOLib (включая EffectClass conversion) резолвится в CfgVehicles.
Это не доказательство успешного создания каждого объекта, физической безопасности
или видимости в UI: HiddenClass/allChild и все атрибуты экспортируются отдельно.

`source` допускает: `source`, `engineMeasured`, `ruleDerived`, `mapUsageDerived`,
`aiSuggested`, `humanVerified`. Последние два сейчас не используются. Пользовательские
наблюдения хранятся отдельно как `humanHint`, не повышают статус до humanVerified.
`status` описывает точность: VERIFIED / APPROXIMATE / UNKNOWN; `confidence` — доверие
к правилу классификации, не статистическая вероятность. `reviewed=false` означает,
что подтверждения человеком нет.

## Файлы каталога

| Файл | Назначение |
|---|---|
| objects.json | Профили, chain, model/config, attributes, capabilities, usage, ссылки на properties |
| source_declarations.json | Однократное хранение деклараций; effective properties восстанавливаются parent-first |
| reflection.json | Авторитетный live export: все effective field expressions, методы, атрибуты |
| models.json | Используемая часть M2C, configs, исторические visual bounds |
| geometry.json | Core geometry profiles, при наличии дополнены live probes |
| engine_geometry.json | Свежие измерения 41 Core; productVersion/session и batch preservation |
| maps.json | Manifest, SHA-256, рекурсивный аудит counts, исключения, runtime comparison |
| instances/*.json | Все размещённые объекты: entity ID, transforms, hashData, overrides |
| usage.json | Global/per-map counts, rank, map sets |
| model_usage.json | Частоты пары classname + effective model, включая overrides |
| top_objects.json | Global, ITEM/STRUCTURE/DECOR, primitives, across maps |
| core_assets.json | 41 кандидат из редактируемой `../core_asset_policy.json` |
| cooccurrence.json | Top 20 соседей для каждого класса, карта и 5м 3D origins |
| terrain_neighbors.json | Top 20 non-terrain соседей в 15м, число anchors и median ΔZ |
| spatial.json | Ближайший экземпляр того же класса без ограничения радиуса, deltas, yaw, ATL offsets |
| compositions.json | Повторы локальных transforms; кандидаты, не функциональные комнаты |
| validation.json | Integrity отдельно от Phase 2 readiness |
| build_state.json / build_summary.json | Завершённость сборки, hashes входов/выходов, аудит source index |

JSON schemaVersion=1. Usage считает **размещённые объекты**, без умножения содержимого
контейнеров и loot/spawner runtime contents. Все эти метаданные сохранены в instances.
`mapsUsedIn` не включает карты с нулём; отсутствие карты в perMapCounts означает 0.
Rank: count descending, classname ascending при равенстве. Статистика условных объектов
описывает авторскую сцену, а не ожидаемое число объектов после probability/spawn.

Одинаковые p3d не означают одинаковый ассет: например BlockDirt/BlockBrick/BlockStone
различаются конфигурацией/внешним видом. Live exporter сохраняет configTextures.
Overrides входят в model_usage, но не заменяют default model класса.

## Координаты и ограничения геометрии

SQM PositionInfo `position[]={X,Z,Y}` переставляется в XYZ. Исходные Euler angles
сохраняются в радианах в нативном порядке SQM; yaw статистика берёт второй компонент.
Это не готовый transform для gateway. `atlOffset` хранится отдельно и **не** является
высотой относительно ближайшего floor. Шаги и расстояния относятся к origins.

M2C построен существующим GenerateModelData через createSimpleObject + boundingBoxReal.
Его bounds — историческое engine evidence с неизвестной свежестью. Dimensions,
опорная плоскость minZ и occupied AABB volume — APPROXIMATE. Bounding box не является
точной collision geometry. Origin [0,0,0] — координатное определение, не contact pivot.
Simple-object probe измеряет нейтральную модель. Для `WoodenDoor` дополнительно проверяет
восемь фаз model animation `xlamdoor`; это не создаёт DoorDynamic runtime instance.

Geometry LOD AABB используется уже в `GameObject.sqf`, `Atmos_raycasts.sqf`; live probe
получает такой AABB отдельным полем. Geometry AABB валиден для 40/41 Core; degenerate
результат сохраняется UNKNOWN. LandContact named selections пусты, а эта версия engine
отклоняет Roadway как `selectionNames` enum, поэтому contact samples, wall/ceiling
contact и точный door sweep остаются UNKNOWN. ROADWAY raycasts есть в HPAstar; их можно использовать
в следующей фазе для выборочных проверок. AABB этих LOD не заменяет mesh/contact samples.

Паттерны: anchor + до четырёх ближайших соседей в 5м; относительные позиции округлены
до 5см, абсолютные углы — до 0.001 rad. Только translation matching, без rotation invariance.
Перекрывающиеся occurrences остаются; повтор сам по себе не доказывает prefab.
Выгружены локально повторяющиеся сигнатуры, не полный cross-map clustering.

## MANUAL ENGINE TEST — только Phase 2

1. Запустить Arma с обычным набором модов ReSDK. Открыть существующую отдельную карту
   `AI_AutomationProbe` штатным MapsManager. Девять dataset-карт не открывать для probes.
2. Перезапустить/перекомпилировать редактор, дождаться загрузки OOP и READY.
   Новый `getCapabilities` должен содержать `catalogVersion=1`.
3. Из корня репозитория выполнить:

```powershell
python Tools/MapAutomation/export_catalog.py --geometry --timeout 45
python Tools/MapAutomation/ingest_live_catalog.py
python Tools/MapAutomation/validate_catalog.py --require-engine
python -m unittest discover -s Tools/MapAutomation -p "test*catalog.py" -v
```

4. Проверить `reflection.json` и `engine_geometry.json`: уникальные классы, Core
   editorPlaceable=true, конечные положительные bounds, model совпадает. Сравнить
   live размеры с M2C; отличия требуют обновления/расследования, не замалчиваются.
5. Убедиться, что RPT не содержит ошибок probes, сцена и revision не изменились.
   Probe автоматически сравнивает fingerprint и удаляет временный simple object.
6. Отдельно вручную проверить у 41 кандидата: опору, направление, проём/анимацию дверей,
   доступ к мебели/контейнерам, точки посадки, крепление ламп. Записать evidence и
   осознанно обновить reviewed/metadata. Не снимать генераторный запрет автоматически.

Ни save/load/build, ни undo/redo, ни E2E Phase 1 не запускаются.
Экспорт не предоставляет arbitrary SQF, клиентских путей, getter names или model paths.
`catalogPage`: integer offset >=0, limit 1..4. `probeGeometry`: только classname из reflection.
Все запросы идут через существующий JSON file gateway, с session и expectedRevision.
Экспорт проверяет смену generation при recompilation и публикует результат атомарно.
При ошибке весь процесс прекращается; исследуйте diagnostics и штатно восстановите probe.
`--require-engine` требует complete live profiles, preservation evidence и M2C comparison.

### Обновление только live evidence

`ingest_live_catalog.py` сверяет complete reflection/probes, сохраняет M2C в `models.json`
и `geometry.json.profiles[].historical`, обновляет Object/Core/Geometry profiles без
повторного mining карт. `m2c_comparison.json` содержит сравнение каждого Core Asset;
`live_validation.json` — счётчики, ошибки и восемь read-back фаз WoodenDoor.
Manifest помечается незавершённым до записи и COMPLETE только после обновления hashes.
Не запускайте offline report generator поверх вручную дополненного live-отчёта.

При остановке после полного reflection доступен `export_catalog.py --geometry
--resume-reflection`: повторно используется только экспорт той же session/generation/revision.
После перекомпиляции требуется полный export. Незавершённый geometry batch не публикуется.
Неподтверждённые semantic front/contact/clearance остаются UNKNOWN или APPROXIMATE;
`reviewed=false` сам по себе не блокирует Phase 2 PASS и не разрешает размещение без проверок.

## Следующая фаза

Placement Solver не реализован. Для Phase 3 отдельно спроектировать
контакты/OBB broad phase, ориентацию, clearance, дверь/проход, deterministic patches и
малый набор положительных/отрицательных spatial checks в отдельной test map.
