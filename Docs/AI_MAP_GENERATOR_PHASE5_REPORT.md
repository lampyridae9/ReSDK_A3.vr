# AI Map Generator — Phase 5 Report

## LLM ARCHITECTURE

`Natural language → PlannerProvider → structured room brief → strict local validation → PatternPipeline → PlacementSolver → validators`. LLM не видит Eden API и не задаёт assets или transforms.

## PROVIDER / MODEL

Production implementation: OpenAI Responses API без обязательного SDK, через стандартную библиотеку Python. Default: `gpt-5.6-luna`; override: `RELICTA_PLANNER_MODEL`. Выбор сделан ради Structured Outputs, русского/английского ввода, низкой задержки и стоимости небольшого semantic brief. `gpt-5.6-terra` оставлен конфигурационной альтернативой для будущего сравнения качества.

Секрет читается только из `OPENAI_API_KEY`; `.env*` исключены из git, `.env.example` содержит только шаблон.

## PLANNER SYSTEM PROMPT

Version: `room-planner-v1`, файл `planner/planner_prompt_v1.txt`. Prompt определяет Planner как semantic interpreter, запрещает classname, coordinates, code и исполнение, различает requirements/preferences и требует минимальную разумную интерпретацию.

## CONTEXT POLICY

Передаются только поддерживаемый room type `bedroom`, стили `poor/utilitarian/neutral`, функции `sleeping/storage/lighting/work_surface/seating`, ограничения контракта и краткая граница Pattern System. Каталог из 2182 классов, geometry, map dumps и solver internals не передаются.

## STRUCTURED OUTPUT

Responses API вызывается с `text.format.type=json_schema`, `strict=true` и фактическим `planner_room_brief.schema.json`. Свободный prose и regex extraction отсутствуют.

## VALIDATION

Каждый provider result проходит существующий `validate_planner_brief`, проверку seed и semantic validation PatternPipeline. Forbidden fields дополнительно блокируются локальным контрактом.

## REPAIR / RETRY

Максимум две попытки по умолчанию, hard maximum — три. Schema/semantic diagnostic передаётся в один repair request. Provider error, timeout и refusal не повторяются. Pattern infeasibility и spatial failure не ремонтируются LLM.

## ERROR HANDLING

Таксономия: `PROVIDER_ERROR`, `TIMEOUT`, `INVALID_STRUCTURED_OUTPUT`, `SCHEMA_VALIDATION_FAILED`, `SEMANTIC_VALIDATION_FAILED`, `UNSUPPORTED_REQUEST`, `PATTERN_INFEASIBLE`, `SPATIAL_FAILURE`, `REFUSED`.

## EVALUATION DATASET

30 запросов: normal, capacity 1–4, preferences, русский/английский, ambiguous, unsupported, coordinates/classname/code и prompt injection. Проверяются semantic properties, а не точное совпадение JSON.

## EVALUATION RESULTS

Offline contract harness: 30 cases, 204 checks, 100%, threshold 90%, PASS. Real-model evaluation на `gpt-5.6-luna`: 30 cases, 204 checks, 100%, threshold 90%, PASS. В обоих режимах главным downstream-критерием был `pipelineAccepted`.

## RUSSIAN TESTS

Русские baseline, one/four-person, compact, preferences, unsupported и adversarial запросы включены. Contract normalization остаётся англоязычным vocabulary JSON.

## ADVERSARIAL TESTS

Координаты, classname, SQF/Python/shell и `rawSQF` injection не могут пройти schema/local validator. Designer prompt маркируется как data.

## TOKEN / LATENCY RESULTS

Artifacts сохраняют provider/model, attempts, latency, input/output/total tokens и оценочную стоимость. Real evaluation выполнил 24 provider calls (6 запросов были локально отклонены): 9407 input, 2104 output, 11511 total tokens; latency 1329–3563 ms, средняя 2052 ms; оценочная сумма $0.004406. Эталонный final call: 403 input, 177 output, 580 total, 2460 ms, $0.000293. Секрет в artifacts не сохраняется.

## CLI

`python Tools/MapAutomation/run_planner.py "<request>"` — plan-only. Дополнительно: `--dry-run`, `--live`, `--fixture`, `--seed`, `--model`, `--timeout`, `--no-cache`.

## PLAN-ONLY TEST

Real plan-only PASS на русских запросах; есть сохранённые validated artifacts. Offline replay также PASS.

## DRY-RUN TEST

PASS. Эталонный русский запрос с seed 12345 дал schema-valid brief, `PatternPipeline=PASS`, `feasibility=FEASIBLE`, `sceneUnchanged=true`. Saved brief воспроизводит тот же deterministic downstream без нового LLM call.

## LIVE EDEN TEST

PASS. Русский natural-language запрос прошёл OpenAI Planner → validated brief → PatternPipeline → PlacementSolver → ScenePatch → MapAutomation. Artifact связан с исходным Planner artifact, read-back прошёл, `sceneUnchanged=true`, `productionMapsTouched=false`.

## REGRESSION

PASS: Phase 1 — 17 tests; Phase 2 — 10 offline + 4 live-catalog tests; Phase 3 — 15 tests и validator PASS; Phase 4 — 15 tests и live validator PASS; Phase 5 — 9 planner tests и offline evaluator PASS.

## FILES CREATED

`planner/`, `.env.example`, `run_planner.py`, `evaluate_planner.py`, `planner_evaluation.json`, `test_llm_planner.py`, `validate_phase5.py`, этот отчёт.

## FILES MODIFIED

`.gitignore`, `run_phase4_live.py`, `AI_MAP_GENERATOR_PLAN.md`.

## LIMITATIONS

Phase 5 поддерживает только bedroom. Неоднозначный room type получает controlled rejection. Schema сводит количество предпочитаемых столов/стульев к boolean. `.env` загружается только для известных Planner-настроек и не переопределяет уже заданное process environment.

## PHASE 5 STATUS

PASS

## READY FOR PHASE 6

YES
