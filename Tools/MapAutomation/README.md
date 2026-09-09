# Phase 1 — Automation Round-Trip Probe

Архитектурный source of truth: [полный план](../../Docs/AI_MAP_GENERATOR_PLAN.md).

**Статус: PASS. Внутренние операции, Copy/Paste identity и внешний Python → Eden → Python
transport подтверждены в настоящем Eden 2026-09-09.**

## Что реализовано

- Модуль подключён через `componentInit(MapAutomation)` перед `Core_postInit`.
- Создание через GOLib, transform через GOLib/Eden, hashData через штатную сериализацию.
- Типизированные create/delete/setTransform/setProperties, inspectObject/inspectScene.
- Read-back transform, class, identity и свойств; проверка удаления по Eden entities.
- Editor-only `__ai = [semanticId, "MapAutomation", parentId]`; `mark` не изменяется.
- Обработка Core onPaste: новая identity копии, затем safe stop до reconcile.
- Диагностика duplicate semantic IDs и восстановление уникальности после Undo/Redo.
- Revision одного подтверждённого patch, fingerprint объектов Eden, safe stop.
- Камера, два тестовых ракурса, screenshot, проверка существования файла, revision в результате.
- Smoke, save/load, create/move undo/redo, частичный failure и явная очистка fixture.
- JSON FileManager transport, whitelist dispatch, expectedRevision и requestId idempotency.
- Внешний Python acceptance runner с create/read/update/read/capture/idempotency/stale/delete.

## Безопасная тестовая среда

Используется только `Src/Editor/Bin/Maps/AI_AutomationProbe.cpp`. Она уже подготовлена
из штатного `TEMP_MAP.cpp`, с именем `AI_AutomationProbe` и специальным marker
`__automationProbe = MapAutomation-v1` в common storage. API требует оба признака.
Существующие игровые карты не изменены.

Штатное открытие карты и save/load используют рабочий `mission.sqm`, как MapsManager.
Поэтому **сначала сохраните свою текущую карту штатным способом**, затем откройте probe.
Не запускайте тесты параллельно и не редактируйте сцену между командами теста.
Тестовая композиция проверяет transform, а не архитектурное качество или опору на пол.

Подготовка нужна только если fixture ещё отсутствует:

```powershell
python Tools/MapAutomation/prepare_probe.py
```

Повторный запуск откажется перезаписывать существующий файл. Это ожидаемая защита.

## Ручной запуск в ReSDK / Eden

1. Запустите ReSDK с обычным набором модов и рабочим ReBridge/FileManager.
2. Сохраните текущую карту. В меню ReSDK выберите **Карта → Открыть карту → AI_AutomationProbe**.
   Дождитесь окончания загрузки классов и `[MapAutomation]` со статусом `READY` в RPT.
   Если редактор был запущен до обновления исходников, выполните штатную перекомпиляцию/перезапуск редактора.
3. Откройте **Инструменты → Системные инструменты → Консоль отладки**.
   Если раздел скрыт, включите системные инструменты в настройках редактора.
   Выполняйте код локально. Команды с `spawn` запускают scheduled test: дождитесь результата,
   а не возвращённого script handle.
4. Проверьте загрузку API и доступность классов (только при диагностике; для external E2E
   Eden console не используется):

   ```sqf
   call ma_getCapabilities
   ```

   `classDiagnostics` должен содержать пустые diagnostics для всех трёх классов.
   Ожидаются `transport=true`, `transportKind="FileManager JSON queue"`.
5. Запустите создание, изменение и read-back:

   ```sqf
   [] spawn ma_test_smoke
   ```

   Ожидается `TEST smoke` со `status=PASS`. Будут созданы `floor_1`, `wall_1`, `arch_1`.
   Проверьте фактические данные:

   ```sqf
   call ma_inspectScene
   ["wall_1"] call ma_inspectObject
   ```

   Стена: class `ConcreteGreenWall`, position `[4008.25,4000.5,10.25]`, rotation `[5,10,95]`, scale `1`.
   В customProps — русское имя и описание с кавычками. При первом запуске от revision 0
   smoke подтверждает три patch и заканчивается revision 3.
6. Выполните save/load round trip:

   ```sqf
   [] spawn ma_test_roundTrip
   ```

   Тест вызывает Eden MissionSave, MapsManager save, проверяет содержимое копии файла,
   загружает её через тот же file-copy/Core_reloadEditorFull путь, что MapsManager.
   Для копирования обратно применяется штатный `file_copyAsync`: он ожидает снятия
   блокировки `mission.sqm` и использует существующий механизм смены фокуса окна.
   Возможна краткая потеря фокуса Arma. Результат callback и содержимое назначения проверяются.
   Ожидаются `LOAD_COPY_PENDING`, `WAITING_FOR_RELOAD`, перезагрузка и затем `TEST roundtrip` со `PASS`.
   При отказе diagnostics содержат COPY_FAILED/LOCK_TIMEOUT и состояние блокировки файла.
   Повторно сравниваются class, position, vectorDir/up, semantic identity, customProps и scale.
   Eden entity ID может измениться при загрузке и намеренно не используется как semantic ID.
7. Сделайте screenshot после reload. Запустите с задержкой, чтобы успеть закрыть консоль:

   ```sqf
   [] spawn {uiSleep 3; [] call ma_test_capture;}
   ```

   Не двигайте камеру во время теста. Ожидается `TEST capture`, `status=OK`, два результата
   с path, sessionId и revision. По окончании возвращается камера Eden.
   По умолчанию файлы `MapAutomation_*.png` ищутся в `Documents\Arma 3\Screenshots`;
   с `-profiles` — в `profiles\Users\<profileName>\Screenshots`.
   **Точный проверенный путь возвращается в capture result.** Откройте оба PNG: должна
   быть видна композиция с двух сторон. Проверка существования файла не подтверждает качество картинки.
8. Проверьте history:

   ```sqf
   [] spawn ma_test_history
   ```

   Тест создаёт дополнительную арку, делает Undo/Redo с read-back, перемещает её,
   повторяет Undo/Redo и удаляет арку. Ожидается `TEST history`, `PASS`, исходные три объекта.
9. Проверьте частичный отказ:

   ```sqf
   call ma_test_failure
   ```

   Ожидается `TEST failure`, `PASS`, **stopped=true**. Внутри результата `failedPatch.status=FAIL`,
   diagnostics `UNSUPPORTED_SCALE`; следующая попытка изменения заблокирована.
   Объект `failure_1` остаётся в известном состоянии `[4031,4000,10]`, rotation `[0,0,45]`.
   Revision не повышается за ошибочный patch. PASS здесь означает правильную обработку отказа.
10. Прочитайте результат и только затем явно подтвердите текущее состояние:

    ```sqf
    call ma_inspectScene
    // Следующие команды выполняются отдельно после просмотра результата:
    call ma_reconcile
    ["failure_1"] call ma_delete
    ```

    Для полного удаления объектов probe, включая частично созданные, есть отдельная команда:

    ```sqf
    [] spawn ma_test_reset
    ```

    Reset удаляет только объекты с provenance MapAutomation и проверяет отсутствие их в Eden.
    Это очистка, не восстановление snapshot. После reset smoke можно запустить повторно.

## Автоматизированная проверка Copy/Paste semantic ID

После успешного smoke и в reconciled-состоянии выполните одну команду:

```sqf
[] spawn ma_test_copyPaste
```

Тест сам выделяет `floor_1`, вызывает Eden `CopyUnit`, ждёт `OnPaste`, проверяет сохранение
ID оригинала A и новый `copy_...` ID B, затем выполняет Undo/Redo и проверяет отсутствие
duplicate IDs. После этого он делает штатный save/load с перезагрузкой редактора и повторяет
проверку A/B и uniqueness. Ожидаются:

- `copy_paste_pre_reload.sqfdata` со `status=PASS`;
- `roundtrip.sqfdata` со `status=PASS`;
- `copy_paste.sqfdata` со `status=PASS` после reload.

Любые duplicates возвращаются как `DUPLICATE_SEMANTIC_IDS` с ID, количеством и Eden IDs.
После любого Undo/Redo automation остаётся в safe-stop до явного `call ma_reconcile`.

## Внешний JSON transport

Очередь работает автоматически, когда открыта карта `AI_AutomationProbe` и в RPT есть
`[MapAutomation] ... READY`. Никакой HTTP/WebSocket server и никакой исполняемый SQF во входе
нет. Python атомарно кладёт JSON request в:

```text
Tools\MapAutomation\queue\requests\<requestId>.json
```

SQF читает его через `FromJSON`, проверяет protocol/session/revision/operation/arguments,
вызывает только разрешённую функцию и пишет JSON response в:

```text
Tools\MapAutomation\queue\responses\<requestId>.json
```

Request содержит `protocolVersion`, `requestId`, `sessionId`, `expectedRevision`, `operation`,
`arguments`. Response содержит `requestId`, `status`, `revision`, `result`, `diagnostics`, а также
`protocolVersion`, `sessionId`, `stopped`. Повтор того же requestId и того же JSON возвращает
закэшированный ответ. Повтор requestId с другим JSON получает `REQUEST_ID_REUSE_CONFLICT`.
Для `applyPatch` и `captureViews` stale revision возвращает `FAIL / REVISION_MISMATCH` до вызова API.

Разрешённые внешние операции: `getCapabilities`, `inspectScene`, `inspectObjects`, `applyPatch`,
`captureViews`. Patch ограничен `create`, `delete`, `setTransform`, `setProperties`; scale только `1`.

## Главный внешний acceptance test

1. Откройте `AI_AutomationProbe`, дождитесь `READY`. Если код обновлён при уже открытом Eden,
   выполните штатную перекомпиляцию/перезагрузку редактора один раз.
2. Убедитесь, что probe не в safe-stop. Если он остановлен после ручного изменения/history,
   сначала осмотрите сцену и явно выполните `call ma_reconcile`.
3. Из PowerShell в корне миссии запустите:

```powershell
python Tools/MapAutomation/run_e2e.py
```

Для ручного визуального наблюдения используйте интерактивный режим:

```powershell
python Tools/MapAutomation/run_e2e.py --timeout 45 --interactive
```

Он создаёт временный `WoodenArch` рядом с основной группой в `[4004,4004,10]` и ждёт Enter
после создания, после перемещения в `[4006,4005,10.5]`, после screenshots и перед удалением.
Камера Eden автоматически не переводится: перед запуском наведите viewport на объекты probe около
`[4000,4000,10]`. Не нажимайте Enter, пока не проверили соответствующий этап.

После запуска Python весь цикл выполняется без Eden console: capabilities → inspectScene → create
`external_probe_*` → read-back → transform → read-back → два screenshots → duplicate requestId →
stale expectedRevision → delete → финальное сравнение сцены. В Eden кратко появится `WoodenArch`
около `[4050,4050,10]`, переместится в `[4052,4051,10.5]`, затем будет удалена.

Успех заканчивается строкой `PASS: external Phase 1 cycle completed`. Полный transcript сохраняется
в `Tools\MapAutomation\artifacts\external_e2e_YYYYMMDD_HHMMSS.json`. Ответы остаются в
`Tools\MapAutomation\queue\responses`. Для каждого screenshot runner печатает точный абсолютный
путь PNG из ответа Eden. Каждый PNG требует проверки человеком: `REQUIRES MANUAL PNG REVIEW`.

## Внутренний контракт

```sqf
["id","BigConcreteFloor",[4000,4000,10],[0,0,0],1,""] call ma_create
["id",[4001,4000,10],[0,0,90],1] call ma_setTransform
["id",[["name","Название"],["desc","Описание"]]] call ma_setProperties
["id"] call ma_inspectObject
call ma_inspectScene
["id"] call ma_delete
```

Для явной optimistic revision check:

```sqf
[[["setTransform",["id",[4001,4000,10],[0,0,90],1]]],ma_revision] call ma_applyPatch
```

Response — SQF HashMap с `status`, `sessionId`, `revision`, `stopped`, `result`, `diagnostics`.
`inspectScene.result` содержит только объекты MapAutomation; fingerprint учитывает position,
rotation и init всех Object entities сцены. Другие типы Eden entities в этом probe не поддержаны.
Scale строго 1. Properties пока только строковые name/desc. Произвольного executeSQF нет.
HashData использует существующий доверенный механизм Relicta; загрузка сторонних недоверенных карт
не становится безопасной благодаря этому API.

## Результаты и диагностика

- Последний ответ: `uiNamespace getVariable ["ma_lastResult",[]]`.
- Snapshot перед последним patch: `uiNamespace getVariable ["ma_beforePatch",[]]`.
- Отчёты: `Tools/MapAutomation/artifacts/{smoke,roundtrip,capture,history,failure,reset}.sqfdata`.
  Это текстовое SQF-представление, **не JSON**, не исполняйте содержимое отчётов.
- В RPT: строки `[MapAutomation]`, первый ScriptError и его контекст.
- При `REPORT_WRITE_FAILED` используйте RPT и ma_lastResult: тест не притворяется,
  что файл отчёта сохранён. При таймауте reload сохраните также последний WAITING_FOR_RELOAD.
- При ошибке screenshot пришлите capture result, фактический путь Screenshots и оба PNG,
  если они появились. Для нестандартного профиля можно указать реальный каталог:

  ```sqf
  uiNamespace setVariable ["ma_screenshotRoot","D:\ActualProfile\Screenshots\"];
  ```

  Override меняет только место проверки, а не каталог, куда Arma сохраняет screenshot.
- Если операция аварийно оставила busy=true, не сбрасывайте флаги вслепую:
  сохраните diagnostics, перезагрузите probe, проверьте сцену и выполните reconcile/reset явно.

## Offline checks

Из корня репозитория:

```powershell
python Tools/MapAutomation/test_static.py
git diff --check
```

Проверяются подготовка fixture без перезаписи, сохранность mission.sqm, объявления классов,
подключение модуля, парность SQF delimiters, разрешение локальных вызовов, отсутствие
динамического выполнения в API и полнота сохранённого архитектурного документа.
Это не SQF compiler и не замена engine tests.

## Ограничения и статус Phase 1

Нет rollback, persistent journal или связи semantic revision с каждым состоянием Eden history.
При ошибке возвращаются before/actual, revision остаётся прежней, требуется explicit reconcile.
Revision/session живут в uiNamespace до завершения процесса Arma; semantic ID хранится в карте.
Снимки подтверждаются существованием нового файла, без анализа PNG и без vision.
Группы, слои, multiplayer, runtime map export и поведение больших сцен не тестируются.
PNG-файлы требуют ручного просмотра: `REQUIRES MANUAL PNG REVIEW`; создание файлов, PNG signature,
размер 1920x1080, revision, scene fingerprint и camera pose проверены автоматически.

Внешний acceptance подтверждён `external_e2e_20260909_153639.json`. Copy/Paste подтверждён
`copy_paste_pre_reload.sqfdata` (A=`floor_1`, B=`copy_6`, Undo/Redo, no duplicates) и последующим
`roundtrip.sqfdata` (PASS после save/load на revision 19, оба ID уникальны). Гонка двух post-load continuation,
из-за которой старый `copy_paste.sqfdata` не перезаписывался, устранена сериализацией проверки.
Phase 1 — **PASS**. Следующий milestone — только
`Phase 2 — Object Catalog + Geometry Foundation`; он здесь не начинается.
