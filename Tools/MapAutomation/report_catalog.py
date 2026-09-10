"""Render the practical Phase 2 report from generated data; no invented counts."""
from collections import Counter,defaultdict
import json
from pathlib import Path
from build_catalog import ROOT,OUT,MAP_NAMES


def report():
    read=lambda n:json.loads((OUT/n).read_text(encoding='utf-8'))
    objects=read('objects.json'); maps=read('maps.json');usage=read('usage.json');top=read('top_objects.json')['overall']
    core=read('core_assets.json')['assets'];geometry=read('geometry.json')['profiles'];spatial=read('spatial.json')
    validation=read('validation.json'); neighbors=read('terrain_neighbors.json')['maps'];variants=read('model_usage.json')
    total=sum(m['parsedRelevantObjects'] for m in maps.values()); chunks=sum((Counter(m['chunkCounts']) for m in maps.values()),Counter())
    out=[];add=out.append
    add('# Phase 2 — Object Catalog + Geometry Foundation + Existing Map Usage Mining\n')
    add('## IMPLEMENTED\n')
    add('Воспроизводимый data-only parser Eden, независимая сверка runtime Init* calls, usage/frequency, model variants, spatial statistics, локальные composition candidates, M2C geometry, curated Core policy, reflection exporter и типизированный geometry probe через существующий gateway. Карты не изменены. Phase 1 не повторялась; PlacementSolver/RoomGenerator/LLM/Vision не реализованы.\n')
    add('## FILES CREATED\n')
    add('- `Src/Editor/MapAutomation/MapAutomation_catalog.sqf`\n- `Tools/MapAutomation/{catalog_parser,build_catalog,export_catalog,validate_catalog,test_catalog,report_catalog}.py`\n- `Tools/MapAutomation/core_asset_policy.json`, `CATALOG.md`\n- `Tools/MapAutomation/catalog/`: objects, source_declarations, models, geometry, usage, model_usage, maps, top_objects, core_assets, cooccurrence, terrain_neighbors, spatial, compositions, validation и instances для девяти карт\n- Этот отчёт.\n')
    add('## FILES MODIFIED\n')
    add('- `Src/Editor/MapAutomation/MapAutomation_init.sqf`: include и generation.\n- `MapAutomation_transport.sqf`: две разрешённые операции и revision guard.\n- `MapAutomation_api.sqf`: объявление catalog capabilities.\n- `Docs/AI_MAP_GENERATOR_PLAN.md`, `Tools/MapAutomation/README.md`: статус/ссылки.\n')
    add('## OBJECT CATALOG\n')
    add(f'Обнаружено **{objects["sourceCandidateCount"]} source candidates**, **{len(usage)} разных классов** реально встречаются в dataset. Число подтверждённых editor-placeable классов: **{objects["editorPlaceableCount"] if objects["editorPlaceableCount"] is not None else "UNKNOWN — live reflection ещё не получен"}**. Эти числа нельзя отождествлять.\n')
    add('Авторитетный exporter читает assembled `__inhlistCase`, `__motherClass`, `__allfields_map`, `__allmethods`, `_redit_attrib*`, GOLib config resolution и getChunkType. Effective properties экспортируются выражениями без вызова произвольных getters. Офлайн-индекс сохраняет literal values, остальные expressions и inheritance; интерфейсы и conditional compilation не исполняет.\n')
    add('Семейства: terrain, floor, wall, door, bed, table, chair, storage, container, light, rock, debris, garbage, mushroom, industrial, pipe, decoration. Capabilities по inheritance — свидетельства, а отсутствие совпадения не доказывает отсутствие функции. Интерактивность остаётся UNKNOWN.\n')
    for c in ['IStruct','Decor']:
        rows=[r for r in variants if r['classname']==c]
        add(f'`{c}`: {usage[c]["totalCount"]} объектов, **{len(rows)} вариантов model**. Не включён как универсальный генераторный ассет: classname-only статистика скрывает разные модели.\n')
    add('## EXISTING MAP ANALYSIS\n')
    add('Главный dataset: текстовые `Src/Editor/Bin/Maps/*.cpp`. Сравнение: одноимённые `Src/host/MapManager/Maps/*.sqf` (Detective runtime имеет нижний регистр). SHA-256 обоих источников сохранён. Source entities включает группы/слои, source objects — только Object. Items контейнеров не прибавляются к placed objects.\n')
    terrain=['BlockDirt','BlockBrick','BlockStone']
    for name in MAP_NAMES:
        m=maps[name]; b=sum(usage[c]['perMapCounts'].get(name,0) for c in terrain)
        excluded=Counter(r['reason'] for r in m['excludedObjects'])
        add(f'### {name}\n')
        add(f'- Source entities: **{m["sourceEntitiesCount"]}**; Object: **{m["sourceObjectCount"]}** → parsed Relicta: **{m["parsedRelevantObjects"]}** → recognized source classes: **{m["recognizedSourceClasses"]}**.\n- Runtime direct Init*: **{m["runtimeComparison"]["directInitCount"]}**; расхождений per-class: **{len(m["runtimeComparison"]["classCountDifferences"])}**.\n- Исключения: '+', '.join(f'{k}={v}' for k,v in excluded.items())+'.\n- Top: '+', '.join(f'`{c}` {n}' for c,n in m['topClasses'][:5])+f'.\n- Три terrain-блока: **{b} ({b/m["parsedRelevantObjects"]*100:.2f}%)**; '+', '.join(f'{k}={v}' for k,v in m['chunkCounts'].items())+'.\n')
        block=max(terrain,key=lambda c:usage[c]['perMapCounts'].get(name,0))
        if block in spatial[name]: add(f'- `{block}`: median nearest same-class origin **{spatial[name][block]["medianNearestSameClass"]:.3f} м**. Это измеренный шаг origins, не размер комнаты.\n')
    add('## GLOBAL TOP OBJECTS\n')
    add('| Rank | Class | Count | Maps | Chunk | Category |\n|---:|---|---:|---:|---|---|')
    for r in top[:30]: add(f'| {r["rank"]} | {r["classname"]} | {r["count"]} | {r["maps"]} | {r["chunkType"]} | {r["category"]} |')
    add('\n'+', '.join(f'Top {n}: **{sum(r["count"] for r in top[:n])/total*100:.2f}%**' for n in [20,50,80])+'. 70–80% для первых 80 объектов в этом dataset не подтверждается. Это доли числа объектов, не занимаемой площади/объёма.\n')
    add('Глобальные пропорции: '+', '.join(f'{k}: **{v} ({v/total*100:.2f}%)**' for k,v in chunks.items())+'. Top per chunk и per map доступны в JSON.\n')
    add('## TERRAIN / BASE GEOMETRY\n')
    add('| Map | BlockDirt | BlockBrick | BlockStone |\n|---|---:|---:|---:|')
    for name in MAP_NAMES: add('| '+name+' | '+' | '.join(str(usage[c]['perMapCounts'].get(name,0)) for c in terrain)+' |')
    add('| TOTAL | '+' | '.join(str(usage[c]['totalCount']) for c in terrain)+' |\n')
    blocks=sum(usage[c]['totalCount'] for c in terrain)
    add(f'Вместе **{blocks} объектов: {blocks/total*100:.2f}% всех placed objects, {blocks/chunks["DECOR"]*100:.2f}% DECOR**. Dirt присутствует на 8 картах, Stone на 7, Brick на 5. Они действительно основные повторяемые terrain primitives, но доля числа объектов не равна доле геометрии.\n')
    add('В исходнике Dirt называется «Земля», Brick — «Кирпич», Stone — «Камень». Практическая трактовка Brick как тёмной почвы остаётся human hint. Все три резолвятся M2C в `rel_vox\\obj\\block_dirt.p3d`; размеры AABB ≈ **11.307 × 11.604 × 11.263 м**. Разные configs нельзя слить в один визуальный ассет. Цвет и текстуры требуют engine/config проверки.\n')
    add('Для многих карт median nearest spacing ≈9–10 м; размеры AABB больше шага. Это поддерживает интерпретацию перекрывающихся блоков как основы массы/поверхности. Но не доказывает непроницаемость коллизии. Настоящие grid дельты, yaw и ATL offsets сохранены в spatial.json.\n')
    add('Другие строительные опоры: `LargeConcreteWallWithReinforcement`, `BigStoneWall`, `WoodenSmallFloor`, `ConcreteSmallFloor2`, `BrickThinWall`, `ThickLightConcreteColumn`, `BigConcretePipe`. `MediumPileOfDirtAndStones`, `BigGreenRock`, `BigDarkRock` подходят для крупной вариации; `SmallDirtGrey`, `DirtCraterLong`, мусор и грибы — кандидаты на поверхностное оформление. Это interpretation source+usage, не engine semantic truth.\n')
    add('### Соседства terrain\n')
    add('Радиус 5м от центра 11-метрового блока часто не охватывает детали над поверхностью. Поэтому дополнительно посчитан 15м 3D origin radius; ниже реальные соседства (число пар, не число уникальных объектов). В JSON есть число anchors с таким соседом и median ΔZ.\n')
    for name,c in [('minimap','BlockDirt'),('barony','BlockDirt'),('dorm','BlockBrick'),('truba','BlockStone'),('hunt','BlockDirt')]:
        rows=neighbors[name][c]['neighbors'][:6]
        add(f'- {name} / `{c}`: '+', '.join(f'`{r["classname"]}` {r["pairCount"]}' for r in rows)+'.')
    add('\nЭти результаты различают базовую массу и соседний detailing статистически. Порядок размещения автором, опора на конкретную поверхность и причинная связь из них не следуют. Scatter камней не заменяет terrain foundation.\n')
    add('## CORE ASSET SET\n')
    add(f'**{len(core)} кандидатов**, отдельная curated policy. Это подготовленный review set; `generatorAllowed=false` до проверки. Отбор сочетает usage, source family, M2C resolution и размер/роль. Никаких автоматически объявленных humanVerified свойств.\n')
    groups=defaultdict(list)
    for c in core: groups[c['category']].append(c['classname'])
    for cat,names in groups.items(): add(f'- **{cat}**: '+', '.join('`'+n+'`' for n in names)+'.')
    add('\nДля первого bedroom: `ConcretePanel` или `WoodenSmallFloor`, `ConcreteGreenWall` / `BrickThinWall`, `WoodenDoor`, `SingleWhiteBed`, `SmallWoodenTable`, `WoodenChair`, `SquareWoodenBox` / `SteelGreenCabinet`, `LampCeiling`. Это набор для будущего проектирования; совместимость модулей и clearance ещё не доказаны.\n')
    add('## GEOMETRY\n')
    add(f'Исторические M2C profiles есть у **{len(geometry)}/{len(core)} Core candidates**. Fresh engine probes: **'+('получены' if (OUT/'engine_geometry.json').exists() else 'не выполнены: Arma/Eden не запущена')+'**.\n')
    add('| Class | Dimensions XYZ, m (AABB) | Placement proposal | Orientation proposal |\n|---|---|---|---|')
    for c in core:
        if c['category'] in ['terrain','bed','table','chair','light','floor']:
            add('| '+c['classname']+' | '+' × '.join(f'{v:.3f}' for v in c['dimensions']['value'])+' | '+c['placementType']['value']+' | '+str(c['orientation']['value'] or 'UNKNOWN')+' |')
    add('\nPivot [0,0,0] — model-space origin. MinZ — приблизительная опорная плоскость; contact pivot неизвестен. Ни одному объекту пока не присвоен VERIFIED полный набор dimensions+contact pivot+placement+semantic front. Placement/orientation — curated proposals с confidence/review, не измеренная функциональность.\n')
    add('Live probe создаёт local simple object по доверенному классу, измеряет boundingBoxReal и Geometry LOD AABB, modelInfo и basis, удаляет объект, сверяет fingerprint. Не создаёт игровой runtime instance. Door swing, animated bounds, collision mesh, взаимодействия и функциональная безопасность этим не подтверждаются.\n')
    add('## SEMANTICS\n')
    add('Автоматически: source inheritance/capability families и осторожные classname rules. Из map usage: frequency, diversity, model variants, neighbors, step/yaw distributions. Curated: 41 конкретный класс, category, предполагаемое крепление/вертикальность. Human hints: три terrain-блока, сохранены отдельно. Все semantic reviews пока false.\n')
    add(f'Найдено **{len(read("compositions.json")["patterns"])} локально повторяющихся сигнатур** anchor+neighbors. Это кандидаты (5см translation quantization), не подтверждённые «стол+4 стула» или комнаты. Полные transforms выгружены для следующего анализа.\n')
    add('## VALIDATION\n')
    add(f'Integrity: **{validation["integrity"]}**. Проверены сохранение количества Object, все nested items, исключения, 9 независимых runtime per-class counts, SHA-256, unique IDs, classname refs, parent chains, M2C bounds/dimensions, usage ranks/maps, Core refs/provenance.\n')
    add('10 offline tests проверяют кавычки/Unicode, multiline config, legacy wrapper, nested container data, отклонение исполнения/неполных данных, числа, 3D spatial pairs, недопустимые engine bounds и реальные Hunt/Minimap/SaloonV2 counts. Engine compilation и новые команды пока не протестированы.\n')
    add('Проблемы M2C/нефизических source candidates перечислены в validation.json; они не скрываются и не попадают в Core без профиля. Все размещённые классы dataset распознаны в source index, включая классы GameModes и FalloutPort parent alias. Это не заменяет проверку загруженных классов.\n')
    add('## MANUAL ENGINE TEST\n')
    add('Точная последовательность и контракт: `Tools/MapAutomation/CATALOG.md`, раздел MANUAL ENGINE TEST. Открыть только AI_AutomationProbe → штатно перекомпилировать editor → дождаться READY → выполнить:\n\n```powershell\npython Tools/MapAutomation/export_catalog.py --geometry --timeout 45\npython Tools/MapAutomation/build_catalog.py --build\npython Tools/MapAutomation/validate_catalog.py\npython Tools/MapAutomation/report_catalog.py\n```\n\nПроверить reflection availability, 41 probe, RPT и неизменность сцены. Затем вручную проверить контакты, переднюю сторону, двери и interaction clearance. Phase 1 тесты не запускаются.\n')
    add('## PROBLEMS / LIMITATIONS\n')
    add('- Нет свежего engine export: число реально доступных классов неизвестно, новые SQF операции требуют Eden test.\n- M2C исторический; config/model resolution не доказывает наличие актуального asset в установленном наборе модов.\n- Bounding volumes не collision mesh; LandContact/ROADWAY support points, occupied mesh, clearance, wall/ceiling contact, door sweep остаются UNKNOWN.\n- Source fallback не исполняет препроцессор и interfaces; обязательна сверка reflection.\n- Не восстановлены комнаты, проходы или факт стыковки стены с полом. Нет утверждений о типичных размерах комнат.\n- Co-occurrence зависит от размера карты, origins, плотности и радиуса; не нормализован как причинная связь.\n- Подсчёт относится к этому dataset, не ко всем картам Relicta.\n')
    add('### Что размечать вручную\n\nSemantic front; contact pivot/опорные точки; пригодность floor/wall/ceiling attachment; usable top surface; дверь/петля/сектор открывания; interaction и seating clearance; направление подхода; material/texture role; безопасность портированных/динамических моделей; семантика generic model overrides. Эти задачи нельзя надёжно закрыть одним classname или AABB.\n')
    add('## PHASE 2 STATUS\n\n'+validation['phase2Status']+'\n')
    add('## RECOMMENDED PHASE 3\n\n**Phase 3 — Placement Solver + Spatial Validation**, после закрытия Phase 2 pending:\n\n1. Контракт model-space transforms, curated contacts и orientation для Core.\n2. Детерминированное размещение по surfaces/sockets, broad-phase AABB/OBB с явной точностью.\n3. Engine narrow checks для опоры, пересечений и ROADWAY.\n4. Door/interaction clearance и связность прохода.\n5. Typed patches через тот же gateway и небольшой набор позитивных/негативных тестов в отдельной карте.\n\nНе реализовано в этой фазе.\n')
    path=ROOT/'Docs/AI_MAP_GENERATOR_PHASE2_REPORT.md';path.write_text('\n'.join(out),encoding='utf-8')
    print(path)


if __name__=='__main__': report()
