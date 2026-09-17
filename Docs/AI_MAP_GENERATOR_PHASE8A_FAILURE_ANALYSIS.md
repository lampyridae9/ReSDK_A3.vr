# BUILDING FAILURE ANALYSIS

Дата: 2026-09-15. Phase 8A: **PARTIAL**. READY TO CONTINUE PHASE 8: **NO**.

Это отчёт Step 1 и архитектурная контрольная точка по пункту 53 запроса,
а не итоговый acceptance report. Генератор и существующая сцена не исправлялись.
District/City работы не выполнялись.

## VISIBLE PROBLEMS FROM SCREENSHOTS

- #1: протяжённые горизонтальные разрывы, нижний пояс стен поднят над полом;
  этажи воспринимаются независимыми слоями.
- #2: низ кирпичных стен находится около верхней части дверей; комнаты открыты
  снизу. Это систематический дефект, а не ошибка одной двери.
- #3–4: внутренние и наружные стены имеют общие разрывы; отдельные углы выглядят
  пересечёнными. Точный объём пересечений по этим ракурсам не доказан.
- #5–6: плиты выступают в область вертикальной связи. Полное перекрытие лестницы
  и проходимость персонажем по одному ракурсу не установлены. Эти два изображения
  показывают практически один и тот же вид и не являются независимыми проверками.
- Кирпич доминирует; жёлтые маркеры и длинные линии мешают архитектурному обзору.
- Направление открывания двери, коллизии мебели, walkable поверхности и замкнутость
  всех сторон требуют дополнительных измерений/видов.

## ROOT CAUSE IN CODE

Критически важно различать текущий исходный код и сцену со скриншотов.
Read-only inspectScene: session `probe_2026_9_15_2_56_20_952`, revision 1,
113 объектов. Стены BrickThinWall имеют Eden Z 11.7843 и 15.0843;
мебель/двери — 10.1343 и 13.4343. Стены подняты относительно этих уровней на 1.65 м.
Текущий `building_generator/generator.py::_shell_operations` уже передаёт стенам
`floor.elevation + positionZOffset`, где offset отсутствует в профиле и равен 0.
Следовательно, текущая сцена не является результатом проверки текущего алгоритма.
Исторический runtime artifact ссылается на `building_generation_727065a40ed54419`.
Связь конкретного screenshot с точным git commit не установлена.

| Дефект | Классификация | Основание |
| --- | --- | --- |
| Систематически поднятые стены в старой сцене | SYSTEMIC_GENERATOR_BUG | read-back + видимый общий сдвиг; точный Eden anchor ещё требует измерения |
| Несогласованные высоты профиля | ASSET_METADATA_BUG | 3.3 м этаж, 3.0 м кирпичная стена, плита визуально 0.1845104 м |
| Проём лестницы по центрам плит | SYSTEMIC_GENERATOR_BUG | `opening.contains(cx,cy)` игнорирует пересечение краёв |
| SUCCESS без физической проверки оболочки | SYSTEMIC_GENERATOR_BUG | orchestration запускает furnishing после graph check и генерации операций |
| Однообразие/несгруппированные материалы | STYLE_ISSUE | основной критерий подбора — длина; сдвиг списка по индексу, нет material regions |
| Предполагаемые коллизии дверей/мебели | Пока не классифицировано | нет достаточных измерений для утверждения конкретного столкновения |

## COORDINATE / PIVOT PROBLEMS

`layout.py::_candidate` строит геометрию сразу в world XY. BuildingFrame отсутствует.
`FloorPlan.elevation` существует, но его физическая семантика не подкреплена anchors.
Пол использует `z - .0922552`, стены — datum, дверь — datum,
лестница — datum + 1.65. Это разные соглашения, не общий преобразователь.

`MapAutomation_api.sqf` передаёт координаты в `golib_om_createObject`.
`GOLib_objectManager.sqf::golib_om_setPosition` вызывает `set3DENAttribute position`.
В этом пути нет собственного преобразования по wall bottom. Нельзя считать
комментарий о floor-based GOLib frame доказательством физической опоры.
Нужно измерить связь Eden position, model origin и contact plane конкретного config.

Phase 2 измерения выполнены на local simple object, а не на установленном Eden config.
Для BrickThinWall visual/geometry bounds Z [-1.5, 1.5], modelInfo offset Z -1.49354.
Для ConcretePanel visual Z [-.0922552, .0922552], geometry Z [-.08125, .08125].
Visual footprint 2.03604 x 4.01182 отличается от geometry bounds 1.95 x 3.9.
Ни visual AABB, ни Geometry AABB сами по себе не подтверждают Roadway/опорную поверхность.
Просто добавить/вычесть minZ снова — недостаточно обоснованное исправление.

## WALL/FLOOR ANCHORING

Нет bottom/top/inner/outer anchors и независимого contact validator.
`minZ` в wallModules хранится, но в текущем размещении не используется.
`wallThickness=0.2` расходится с измеренной толщиной BrickThinWall 0.3.
Выбор window asset заменяет только classname и сохраняет геометрию исходного модуля.
Совместимость этих модулей не проверяется в assembler.

Если кирпич опирается на datum, его верх на datum+3.0. При следующем datum+3.3
и visual slab thickness .1845104 низ верхней плиты находится на datum+3.1154896.
Остаётся 0.1154896 м. Это расчёт по visual bounds при корректной опоре,
а не измерение реального зазора в текущей сцене. Более низкие wood/steel модули
увеличивают несогласованность. Нужен structural layer/header либо совместимый профиль;
сокращать этаж без проверки подъёма лестницы нельзя.

## PORTAL / DOOR PROBLEM

Уже существуют WallSegment, owners и PortalPlan с wall_segment. Код вырезает
левый/правый интервалы вокруг двери. Утверждение «дверь просто ставится в сплошную
стену» не описывает всю текущую реализацию.

Но opening не имеет height/bottom и полного structural контракта. Header отсутствует.
Используется global doorClearWidth вместо portal.width. Один physical run допускает
только один portal; collinear fragments объединяются без сохранения границ owners
в физической реализации. Остатки <= .25 м просто пропускаются. Одномодульный fit
может принимать расхождение длины, не закрывая его. Нет проверки solid intersection,
центровки frame, подходов и открывания двери по собранным объектам.

## MULTI-FLOOR PROBLEM

Общий storeyHeight существует — его не нужно создавать заново. Но это независимая
константа, не проверяемое равенство wall height + structural layer.
Shared logical walls тоже уже существуют в `_walls`; переписывать их с нуля не нужно.
RoomGenerator получает идеальные поверхности до доказательства совпадения с shell.
Старые tests 25/26 проверяют заданный Z и числа ширины, а не геометрический контакт.

## STAIR PROBLEM

Вертикальная связь имеет footprint и два landing rectangles, но верхний и нижний
получают один и тот же прямоугольник. Это может быть допустимо для U-shaped stair,
однако не доказывает точные точки входа/выхода и их высоты.
Нет отдельного FloorOpening; проём выводится из occupied_region и центров плит.
Края оставленных плит могут пересекать требуемый проём; удалённые плиты могут
убрать нужный landing. Проверка графа этажей не проверяет rise, collision или headroom.
Исторический `RUNTIME_LOAD_PASS` явно оставляет traversal APPROXIMATE.

## MATERIAL / STYLE PROBLEM

Реальные brick, metal, wood классы перечислены в профиле, но подбор не ограничивает
совместимость attachment planes и высот, не задаёт material runs или facade intent.
Существующая сцена содержит только BrickThinWall для стен, поэтому нынешний palette
код ещё не проверен этими screenshots. MaterialPalette/MassingPlan/style pass отсутствуют.
Нужно сначала обеспечить геометрическую совместимость, затем contiguous material regions.

## EXISTING MAP EVIDENCE

Добавлен read-only `Tools/MapAutomation/mine_structural_patterns.py`.
Он обработал все девять запрошенных catalog/instances файлов. Артефакт:
`Tools/MapAutomation/artifacts/phase8a_structural_mining.json`.
Сохранены hashes источников, role counts, class pairs, повторяющиеся world XYZ deltas,
исходные entity IDs/positions/rotations. Это кандидаты, не автоматически curated anchors.

Пример dorm: BigStoneWall -> BigStoneWall, delta [6,0,0], 16 направленных
наблюдений; entity 7059 -> 7058, [4031,3931,19.4869] -> [4037,3931,19.4869].
Обратные связи могут считать ту же физическую пару повторно.
Частоты нельзя трактовать как независимые строительные образцы.

Метод: role heuristic по classname, ближайший XY сосед <= 8 м и |dZ| <= 5 м.
Это не распознавание зданий и не доказательство wall/floor contact. Для hunt
эвристика не нашла structural classes; это не доказывает отсутствия конструкций.
Дверные пары необходимо проверить в локальной системе и по реальному проёму.
Материальные co-occurrence внутри здания пока не извлечены.

## PROPOSED ARCHITECTURE CHANGES

Минимальная миграция, без общего rewrite:

1. Сохранить BuildingBrief, planner, room generation и транспорт.
2. Ввести BuildingFrame и authoritative FloorLevel; перевести structural расчёты
   в local XYZ, сделать один преобразователь к Eden с измеренными asset anchors.
3. Расширить существующие WallSegment/PortalPlan: thickness/height/material run,
   Opening(height,bottom,offset), FloorOpening и landing anchors.
4. Вынести assembly из `_shell_operations`; получать операции и physical envelopes
   с provenance, не только список create.
5. Ввести FloorAssemblyValidator/BuildingShellValidator и обязательный gate
   перед RoomGenerator; отсутствие anchors означает непроверенный shell, не PASS.
6. После shell acceptance добавить palette/style, paired semantic captures и review stages.

Migration impact: новая версия layout/artifact schema; прежние artifacts остаются
историческими evidence, не пригодными для нового structural PASS. Gateway операции
и semantic ownership сохраняются. Tests с жёстким равенством Z заменяются независимыми
контактными проверками. Старые SUCCESS не мигрируют автоматически в Phase 8A PASS.

## IMPLEMENTATION ORDER

1. Live profile floor, brick/metal/wood walls, door, stair в отдельных пробах:
   Eden position -> model/contact planes, native orientation, read-back, снимки.
2. Согласованный одноступенчатый профиль: floor + single-floor shell, без мебели.
3. Физические door openings и независимые негативные тесты.
4. Single-floor visual acceptance.
5. Второй этаж + exact floor opening/landings + shell acceptance.
6. Контролируемые material regions, сохранение storage в acceptance brief.
7. Furnishing только после shell/portal/accessibility gates.
8. Семь paired captures, Vision Critic, ручная Eden проверка.
9. Save/build/runtime и walkthrough; cleanup только по явному подтверждению.

По пункту 53 запроса работа остановлена на этой существенной архитектурной
контрольной точке. Автоматического удаления сцены или скрытого rewrite не было.

## RISKS

- Native modules могут не замостить выбранные размеры и проёмы: нужно менять
  layout constraints или curated modules, не разрешать неограниченные overlaps.
- Замена высоты этажа может нарушить измеренный rise лестницы 3.3 м.
- Модельный origin и Eden anchor нельзя смешивать; нужны измерения installed config.
- Полный collision/Roadway не восстанавливается из AABB.
- `--interactive --keep` сейчас всё равно предлагает Enter для cleanup;
  стадийных пауз нет. Этот режим нуждается в исправлении перед acceptance run.
- Live orchestration проверяет наличие IDs, но не равенство всех transforms.
- Vision в BuildingGenerator пока не вызывается (`visionCalls=0`); старый SUCCESS
  ничего не сообщает о visual acceptance.
- Storage optional и может быть удалён: acceptance house должен требовать storage.

## VERIFICATION AND STATUS

Проверено: 26/26 существующих building unit tests PASS; read-only live scene snapshot;
структурный mining всех девяти источников; исходный код transform/assembly/validation.
Снимок read-back сохранён в `Tools/MapAutomation/artifacts/phase8a_scene_audit.json`.
Тесты Phase 1–7 не перезапускались. Production maps и live scene не менялись.
Новый дом, новые anchors, исправленный shell, after screenshots, Vision review,
ручной Eden PASS и новый runtime walkthrough пока не выполнены.

Phase 8A: **PARTIAL**. READY TO CONTINUE PHASE 8: **NO**.
