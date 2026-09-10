"""Reproducible Phase 2 dataset builder. Run --help for queries.

Reflection is authoritative; source index is explicitly provisional, never a
claim that a class is loaded/placeable. All map entities are structurally parsed.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import math
from pathlib import Path
from catalog_parser import Reader, balanced, lex, literal, parse_config, parse_hashdata

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).parent / 'catalog'
MAP_NAMES = 'minimap saloonv2 barony detective dorm truba theatre holiday hunt'.split()


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def norm(model):
    model=model.lower().lstrip('\\').replace('/', '\\')
    return model+'.p3d' if '\\' in model and not model.endswith('.p3d') else model
def write(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
def fact(value, source='source', **kw): return dict(value=value, source=source, **kw)


def source_index():
    """Lex macro declarations, preserving expressions; do not evaluate preprocessor.

    This intentionally is NOT the Object Catalog exporter. Conditional branches,
    interface includes, generated classes and runtime getters require reflection.
    """
    classes, duplicates = {}, []
    paths=list((ROOT / 'Src/host/GameObjects').rglob('*.sqf'))+list((ROOT / 'Src/host/GameModes').rglob('*.sqf'))
    for path in sorted(paths):
        text = path.read_text(encoding='utf-8-sig'); ts = lex(text)
        # Only file-local single-identifier parent aliases (e.g. FalloutPort).
        # This is not a preprocessor: no conditional/function macro evaluation.
        aliases={}
        for line in text.splitlines():
            if line.strip().startswith('#define'):
                define=lex(line)
                if len(define)==4 and define[0].value=='#' and define[1].value=='define':
                    aliases[define[2].value]=define[3].value
        previous_end = 0
        for i, t in enumerate(ts):
            if t.kind == 'string' or t.value != 'class' or i+7 >= len(ts): continue
            if [x.value for x in ts[i+1:i+3]][:1] != ['(']: continue
            if ts[i+3].value != ')' or ts[i+4].value != 'extends': continue
            name, parent = ts[i+2].value, ts[i+6].value
            parent_expression=parent; parent=aliases.get(parent,parent)
            end = next((j for j in range(i+8, len(ts)) if ts[j].kind != 'string' and ts[j].value == 'endclass'), None)
            if end is None: raise ValueError(f'Missing endclass {path}:{name}')
            props, methods, attrs = {}, {}, []
            for j in range(previous_end, i):
                if ts[j].value == 'editor_attribute' and ts[j+1].value == '(':
                    attrs.append(ts[j+2].value)
            for j in range(i+8, end):
                macro = ts[j].value
                if macro not in ('var', 'getter_func', 'getterconst_func', 'func') or ts[j].kind == 'string': continue
                if ts[j+1].value != '(': continue
                k = balanced(ts, j+1)
                key = ts[j+2].value.lower()
                expr = text[ts[j+4].offset:ts[k].offset] if j+4 < k else ''
                entry = {'expression': expr, 'declaredIn': name, 'source': 'source'}
                try: entry['value'] = literal(expr)
                except ValueError: pass
                (props if macro == 'var' else methods)[key] = entry
            row = dict(classname=name, parent=parent, parentExpression=parent_expression, declaredProperties=props, declaredMethods=methods,
                       editorAttributes=attrs, sourceFile=path.relative_to(ROOT).as_posix(),
                       sourceLine=text.count('\n', 0, t.offset)+1, source='source',
                       availability='UNKNOWN_PENDING_REFLECTION')
            if name in classes: duplicates.append(name)
            classes[name] = row; previous_end = end+1
    def inherit(name, seen=()):
        if name in seen: raise ValueError(f'Inheritance cycle {seen} {name}')
        c = classes[name]; parent = c['parent']
        if 'inheritance' in c: return
        if parent in classes:
            inherit(parent, seen+(name,)); p = classes[parent]
            c['inheritance'] = [parent]+p['inheritance']
            c['effectiveProperties'] = {**p['effectiveProperties'], **c['declaredProperties']}
            c['effectiveMethods'] = {**p['effectiveMethods'], **c['declaredMethods']}
        else:
            c['inheritance'] = [parent]
            c['effectiveProperties'] = c['declaredProperties'].copy()
            c['effectiveMethods'] = c['declaredMethods'].copy()
        c['model'] = c['effectiveProperties'].get('model', {}).get('value')
        c['displayName'] = c['effectiveProperties'].get('name', {}).get('value')
        c['description'] = c['effectiveProperties'].get('desc', {}).get('value')
        chunk = c['effectiveMethods'].get('getchunktype', {}).get('expression', '').strip()
        c['chunkType'] = {'CHUNK_TYPE_ITEM':'ITEM', 'CHUNK_TYPE_STRUCTURE':'STRUCTURE', 'CHUNK_TYPE_DECOR':'DECOR'}.get(chunk, 'UNKNOWN')
    for name in classes: inherit(name)
    return {c:r for c,r in classes.items() if c=='GameObject' or 'GameObject' in r['inheritance']}, duplicates


def read_m2c():
    path = ROOT / 'Src/M2C.sqf'; models, configs = {}, {}
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        if not line.startswith('['): continue
        ts = lex(line); r = Reader(ts); cfg, model, bounds = r.literal()
        r.pop('_')
        if r.peek() is not None: raise ValueError('Unexpected M2C suffix')
        model = norm(model); configs[cfg.lower()] = model
        if model not in models:
            lo, hi = bounds[:2]
            if len(bounds) == 2: hi, lo = lo, [-x for x in lo]
            dims = [b-a for a,b in zip(lo,hi)]
            models[model] = dict(model=model, configs=[], visualBounds=fact([lo,hi], 'engineMeasured',
                status='VERIFIED', freshness='HISTORICAL_M2C_NOT_REPROBED', evidence='Src/M2C.sqf / GenerateModelData: boundingBoxReal'),
                dimensions=fact(dims, 'ruleDerived', status='APPROXIMATE', evidence='M2C AABB max-min'),
                geometryBounds=fact(None, status='UNKNOWN'), pivot=fact([0,0,0], 'ruleDerived', status='APPROXIMATE',
                meaning='model-space origin; not support point or Eden position'),
                occupiedVolume=fact(math.prod(dims), 'ruleDerived', status='APPROXIMATE', meaning='AABB volume, NOT collision volume'),
                supportPlane=fact(lo[2], 'ruleDerived', status='APPROXIMATE', meaning='AABB minimum Z, not LandContact'),
                orientation=fact(None, status='UNKNOWN'), semanticFront=fact(None, status='UNKNOWN'))
        models[model]['configs'].append(cfg)
    return models, configs


def read_map(path):
    text = path.read_text(encoding='utf-8-sig'); tree = parse_config(text)
    rows, excluded, kinds, containers, entity_ids = [], [], Counter(), [], []
    def visit(node, trail):
        children = node['children']
        if 'items' in node['properties']:
            actual = len(children)
            if node['properties']['items'] != actual:
                raise ValueError(f'{path}:{trail}: declared items != {actual}')
            containers.append(dict(path=trail, declared=actual, parsed=actual))
        for key, child in children.items():
            p = child['properties']; kind = p.get('dataType')
            if kind:
                kinds[kind] += 1
                if 'id' in p: entity_ids.append(p['id'])
            if kind == 'Object':
                attrs = child['children'].get('Attributes', {}).get('properties', {})
                init = attrs.get('init', '')
                hd = parse_hashdata(init) if init else {}
                if 'class' in hd:
                    pos = child['children']['PositionInfo']['properties']
                    xyz = pos['position']; angles = pos.get('angles', [0,0,0])
                    rows.append(dict(entityId=p['id'], classname=hd['class'], config=p.get('type'),
                        position=[xyz[0], xyz[2], xyz[1]], positionConvention='SQM PositionInfo X,Z,Y reordered to X,Y,Z; absolute elevation',
                        anglesRadians=angles, anglesConvention='SQM native Euler order retained',
                        atlOffset=p.get('atlOffset'), flags=p.get('flags'), layerPath=trail,
                        customProps=hd.get('customProps', {}), metadata=hd))
                else:
                    excluded.append(dict(entityId=p.get('id'), config=p.get('type'),
                        reason='commonStorage' if 'missionName' in hd else 'nonRelictaObject'))
            visit(child, trail+'/'+key)
    visit(tree['children']['Mission']['children']['Entities'], 'Mission/Entities')
    if len(entity_ids) != len(set(entity_ids)): raise ValueError(f'Duplicate entity ids {path}')
    # Independent lexical count checks the structural traversal (not init regex).
    ts = lex(text)
    lexical = sum(t.value=='dataType' and ts[i+2].value=='Object' for i,t in enumerate(ts[:-2]) if t.kind != 'string')
    if lexical != kinds['Object'] or len(rows)+len(excluded) != lexical: raise ValueError('Object conservation failed')
    return rows, dict(source=path.relative_to(ROOT).as_posix(), sha256=digest(path),
        sourceEntitiesCount=sum(kinds.values()), entityKinds=dict(kinds), sourceObjectCount=lexical,
        parsedRelevantObjects=len(rows), excludedObjects=excluded, entitiesContainers=containers,
        parserErrors=[], provenance='mapUsageDerived')


def runtime_counts(path):
    """Count generated direct Init* calls, independently of the Eden parser."""
    ts=lex(path.read_text(encoding='utf-8-sig')); stack=[]; counts=Counter(); chunks={}
    for i,t in enumerate(ts):
        if t.kind=='string': continue
        if t.value=='[': stack.append(i)
        elif t.value==']':
            if not stack: raise ValueError(f'Unbalanced runtime array {path}')
            start=stack.pop()
            if i+2<len(ts) and ts[i+1].value=='call' and ts[i+2].value in ('InitDecor','InitStruct','InitItem'):
                if ts[start+1].kind!='string': raise ValueError('Nonliteral runtime class')
                c=ts[start+1].value; counts[c]+=1
                chunks[c]={'InitDecor':'DECOR','InitStruct':'STRUCTURE','InitItem':'ITEM'}[ts[i+2].value]
    if stack: raise ValueError('Unclosed runtime array')
    return counts,chunks


RULES = [('bed',['BedBase']), ('chair',['IChair','IChairAsItem']), ('table',['TableBase']),
         ('container',['SContainer','Container']), ('door',['Door']), ('light',['BaseElectronicDeviceLighting','ILightible']),
         ('floor',['SmallFloor','BigFloor']), ('wall',['SmallWall','BigWall']), ('rock',['BigStoneDecor']),
         ('industrial',['ElectronicDevice'])]


def classify(c):
    name=c['classname']; chain=[name]+c.get('inheritance', [])
    if name in ('BlockDirt','BlockBrick','BlockStone'):
        return dict(category='terrain', source='ruleDerived', confidence=0.85, reviewed=False,
            evidence=['source declaration in Decors/Blocks/Blocks.sqf','initial user hint','map usage'],
            humanHint={'BlockDirt':'грунт / коричневая земля','BlockBrick':'тёмный блок / тёмная почва','BlockStone':'камень / серая земля'}[name])
    for cat, bases in RULES:
        if set(chain)&set(bases): return dict(category=cat, source='ruleDerived', confidence=0.8, reviewed=False, evidence='inheritance: '+','.join(sorted(set(chain)&set(bases))))
    low = name.lower()
    for cat, words in [('mushroom',['mushroom']), ('garbage',['garbage','trash']), ('debris',['debris']),
                       ('floor',['floor']), ('wall',['wall']), ('door',['door','arch']), ('rock',['rock','stone']),
                       ('storage',['cabinet','wardrobe','shelf','shelves']), ('light',['lamp','torch','candle','campfire']),
                       ('pipe',['pipe']), ('industrial',['barrel','generator','transformer']), ('table',['table']), ('chair',['chair'])]:
        if any(w in low for w in words): return dict(category=cat, source='ruleDerived', confidence=0.5, reviewed=False, evidence='classname token only')
    return dict(category='decoration' if c.get('chunkType')=='DECOR' else 'unclassified', source='ruleDerived', confidence=0.3, reviewed=False, evidence='chunk type only')


def spatial(rows, radius=5):
    cells=defaultdict(list); pairs=Counter(); nearest=defaultdict(list)
    byclass=defaultdict(list)
    for r in rows: byclass[r['classname']].append(r)
    degrees=defaultdict(Counter); zoffsets=defaultdict(Counter); delta=defaultdict(Counter)
    signatures=defaultdict(list)
    for i,r in enumerate(rows):
        p=r['position']; key=tuple(math.floor(x/radius) for x in p); cells[key].append(i)
    for i,a in enumerate(rows):
        p=a['position']; key=tuple(math.floor(x/radius) for x in p); neighbors=[]
        for offset in itertools.product((-1,0,1), repeat=3):
            for j in cells.get(tuple(x+y for x,y in zip(key,offset)), []):
                if i==j: continue
                b=rows[j]; d=math.dist(p,b['position'])
                if d>radius: continue
                neighbors.append((d,j))
                if j>i: pairs[tuple(sorted((a['classname'],b['classname'])))] += 1
        # Grid spacing must not be censored by the 5m co-occurrence radius:
        # terrain blocks themselves are roughly 11m wide.
        same=[(math.dist(p,b['position']),b) for b in byclass[a['classname']] if b['entityId']!=a['entityId'] and math.dist(p,b['position'])>0.001]
        best=min(same,key=lambda row:row[0]) if same else None
        if best:
            d,b=best; nearest[a['classname']].append(d)
            delta[a['classname']][tuple(round(y-x,2) for x,y in zip(p,b['position']))]+=1
        degrees[a['classname']][round(math.degrees(a['anglesRadians'][1])%360,1)]+=1
        if a['atlOffset'] is not None: zoffsets[a['classname']][round(a['atlOffset'],2)]+=1
        # Translation-only exact orientation + 5cm offsets; not rotation invariant.
        members=[]
        for d,j in sorted(neighbors)[:4]:
            b=rows[j]
            members.append((b['classname'],tuple(round((y-x)/0.05)*0.05 for x,y in zip(p,b['position'])),tuple(round(v,3) for v in b['anglesRadians'])))
        if len(members)>=2:
            signature=(a['classname'],tuple(round(v,3) for v in a['anglesRadians']),tuple(sorted(members)))
            signatures[signature].append(a['entityId'])
    stats={c:dict(neighborRadius=None, sampleCount=len(vals), medianNearestSameClass=sorted(vals)[len(vals)//2],
        topNearestDeltas=[dict(delta=list(d),count=n) for d,n in delta[c].most_common(8)],
        topYawDegrees=degrees[c].most_common(8), topAtlOffsets=zoffsets[c].most_common(8)) for c,vals in nearest.items()}
    patterns=[dict(patternId=hashlib.sha256(repr(k).encode()).hexdigest()[:16], anchorClass=k[0], anchorAngles=k[1],
        members=[dict(classname=m[0],relativePosition=m[1],anglesRadians=m[2]) for m in k[2]],
        occurrences=len(v), anchorEntityIds=v, confidence=0.4, source='mapUsageDerived', reviewed=False)
        for k,v in signatures.items() if len(v)>1]
    return pairs, stats, patterns


def model_variants(instances, classes, configs):
    variants=defaultdict(Counter)
    for name,rows in instances.items():
        for r in rows:
            m=r['customProps'].get('model') or classes.get(r['classname'],{}).get('model')
            m=norm(m) if isinstance(m,str) else None
            resolved=configs.get(m,m)
            variants[(r['classname'],resolved)]['totalCount']+=1
            variants[(r['classname'],resolved)][name]+=1
    return [dict(classname=c,model=m,totalCount=counts['totalCount'],perMapCounts={n:v for n,v in counts.items() if n!='totalCount'},source='mapUsageDerived')
        for (c,m),counts in sorted(variants.items(),key=lambda kv:(-kv[1]['totalCount'],kv[0][0],kv[0][1] or ''))]


def terrain_neighbors(instances, radius=15):
    terrain={'BlockDirt','BlockBrick','BlockStone'}; output={}
    for name,rows in instances.items():
        result={}
        for c in sorted(terrain):
            anchors=[r for r in rows if r['classname']==c]; counts=Counter(); supports=Counter(); dz=defaultdict(list)
            for a in anchors:
                found=set()
                for b in rows:
                    if b['classname'] in terrain: continue
                    if math.dist(a['position'],b['position'])<=radius:
                        cls=b['classname']; counts[cls]+=1; found.add(cls); dz[cls].append(b['position'][2]-a['position'][2])
                supports.update(found)
            result[c]=dict(anchorCount=len(anchors),neighbors=[dict(classname=cls,pairCount=n,anchorsWithNeighbor=supports[cls],
                medianOriginDeltaZ=sorted(dz[cls])[len(dz[cls])//2]) for cls,n in counts.most_common(20)])
        output[name]=result
    return dict(radiusMeters=radius,source='mapUsageDerived',meaning='3D origins; non-terrain neighbors; not contact/support proof; top20 per map and anchor class',maps=output)


def build():
    OUT.mkdir(exist_ok=True); (OUT/'instances').mkdir(exist_ok=True)
    write('build_state.json',dict(status='BUILDING',schemaVersion=1))
    classes, duplicates=source_index(); models, configs=read_m2c()
    source_count=len(classes)
    engine_path=OUT/'reflection.json'
    reflection=json.loads(engine_path.read_text(encoding='utf-8')) if engine_path.exists() else None
    if reflection:
        for r in reflection['objects']:
            old=classes.get(r['classname'], {})
            row={**old,**r, 'availability':'REFLECTION_RESOLVED' if r['editorPlaceable'] else 'NOT_PLACEABLE'}
            for key,field in [('displayName','name'),('description','desc')]:
                try: row[key]=literal(r['effectiveProperties'].get(field,{}).get('expression',''))
                except ValueError: row[key]=None
            classes[r['classname']]=row
        reflected_names={r['classname'] for r in reflection['objects']}
        classes={c:r for c,r in classes.items() if c in reflected_names}
    maps={}; usages=defaultdict(Counter); allpairs=Counter(); patterns=[]; spatial_stats={}; instances={}
    files=list((ROOT/'Src/Editor/Bin/Maps').glob('*'))
    for name in MAP_NAMES:
        matches=[p for p in files if p.stem.lower()==name]
        if len(matches)!=1: raise ValueError(f'Ambiguous/missing map {name}')
        rows,meta=read_map(matches[0]); instances[name]=rows
        counts=Counter(r['classname'] for r in rows)
        runtime_files=[p for p in (ROOT/'Src/host/MapManager/Maps').glob('*') if p.stem.lower()==name]
        if len(runtime_files)!=1: raise ValueError('Missing runtime comparison')
        rt,rt_chunks=runtime_counts(runtime_files[0])
        meta['runtimeComparison']=dict(source=runtime_files[0].relative_to(ROOT).as_posix(),sha256=digest(runtime_files[0]),
            directInitCount=sum(rt.values()),classCountDifferences={c:dict(editor=counts[c],runtime=rt[c]) for c in sorted(counts.keys()|rt.keys()) if counts[c]!=rt[c]},
            meaning='Compiled map may be older, probability-gated, or have author code; not added to editor counts')
        meta['recognizedSourceClasses']=sum(n for c,n in counts.items() if c in classes)
        meta['unknownClasses']={c:n for c,n in counts.items() if c not in classes}
        meta['topClasses']=counts.most_common(10)
        meta['chunkCounts']=dict(Counter(classes.get(r['classname'],{}).get('chunkType','UNKNOWN') for r in rows))
        meta['chunkDisagreements']={c:dict(source=classes[c]['chunkType'],runtime=k) for c,k in rt_chunks.items() if c in classes and classes[c]['chunkType']!=k}
        maps[name]=meta
        for c,n in counts.items(): usages[c][name]=n
        write(f'instances/{name}.json', rows)
        pairs,stats,pats=spatial(rows); allpairs.update(pairs); spatial_stats[name]=stats
        for pat in pats: pat['maps']=[name]
        patterns.extend(pats)
    ranked=sorted(usages,key=lambda c:(-sum(usages[c].values()),c)); usage={}
    for rank,c in enumerate(ranked,1):
        usage[c]=dict(totalCount=sum(usages[c].values()), mapsUsedIn=sorted(usages[c]), mapCount=len(usages[c]),
                      frequencyRank=rank, perMapCounts=dict(usages[c]), source='mapUsageDerived')
    for c,obj in classes.items():
        m=obj.get('model'); m=norm(m) if isinstance(m,str) else ''
        obj['resolvedModel']=norm(obj['engineResolvedModel']) if obj.get('engineResolvedModel') else configs.get(m,m if m in models else None)
        obj['modelResolution']=fact(obj['resolvedModel'], evidence='live CfgVehicles model' if obj.get('engineResolvedModel') else 'M2C registry; installed asset not yet checked')
        obj['provenance']={k:'source' for k in ['classname','parent','inheritance','model','displayName','description','chunkType','editorAttributes']}
        obj['provenance'].update(modelOverrides='mapUsageDerived',usage='mapUsageDerived',semantic='ruleDerived',capabilities='ruleDerived')
        obj['semantic']=classify(obj); obj['usage']=usage.get(c,dict(totalCount=0,mapCount=0,mapsUsedIn=[],perMapCounts={},frequencyRank=None,source='mapUsageDerived'))
        obj['semanticId']='relicta:'+c.lower()
        chain=set([c]+obj.get('inheritance',[]))
        obj['capabilities']={k:fact(True if chain&set(bases) else None, 'ruleDerived', confidence=0.8 if chain&set(bases) else 0,
            status='APPROXIMATE' if chain&set(bases) else 'UNKNOWN',
            evidence='inheritance family match' if chain&set(bases) else 'no family evidence; does not prove absence') for k,bases in {
            'container':['SContainer','Container'],'seating':['IChair','IChairAsItem'],'door':['Door'],
            'light':['ILightible','BaseElectronicDeviceLighting'],'electronic':['ElectronicDevice'], 'item':['Item']}.items()}
        obj['capabilities']['interactive']=fact(None, status='UNKNOWN', evidence='method presence alone cannot establish usable interaction')
        obj['modelOverrides']=[dict(map=name,entityId=r['entityId'],model=r['customProps']['model'])
            for name,rows in instances.items() for r in rows if r['classname']==c and 'model' in r['customProps']]
    core=[]
    policy=json.loads((OUT.parent/'core_asset_policy.json').read_text(encoding='utf-8'))
    for entry in policy['assets']:
            c=classes[entry['classname']]
            if c['resolvedModel'] not in models: raise ValueError('Core model missing: '+c['classname'])
            if 'InterfaceClass' in c.get('editorAttributes',[]) or c.get('availability')=='NOT_PLACEABLE': raise ValueError('Core not placeable: '+c['classname'])
            c['semantic']={k:v for k,v in entry.items() if k not in ['classname','placementType','orientation']}
            if c['classname'] in ['BlockDirt','BlockBrick','BlockStone']: c['semantic']['humanHint']=classify(c)['humanHint']
            geometry=models[c['resolvedModel']]
            core.append(dict(classname=c['classname'], model=c['resolvedModel'], category=entry['category'], chunkType=c['chunkType'],
                dimensions=geometry['dimensions'], usage=c['usage'], semantic=c['semantic'],
                placementType=fact(entry['placementType'],'ruleDerived',confidence=0.6,reviewed=False,evidence='core_asset_policy.json; intended attachment, not measured contact'),
                orientation=fact(entry['orientation'] if entry['orientation']!='UNKNOWN' else None,'ruleDerived',status='APPROXIMATE' if entry['orientation']!='UNKNOWN' else 'UNKNOWN',confidence=0.6,reviewed=False), availability=c['availability'],
                generatorAllowed=False, reviewRequired=['live reflection/model resolution','contact and orientation','functional clearance']))
    def top(predicate=lambda c:True):
        return [dict(rank=i,classname=c, count=usage[c]['totalCount'], maps=usage[c]['mapCount'],
                chunkType=classes.get(c,{}).get('chunkType','UNKNOWN'), model=classes.get(c,{}).get('resolvedModel'),
                category=classes.get(c,{}).get('semantic',{}).get('category','unknown')) for i,c in enumerate(ranked,1) if predicate(c)]
    tops=dict(overall=top(), perChunk={k:top(lambda c:classes.get(c,{}).get('chunkType')==k) for k in ['DECOR','STRUCTURE','ITEM']},
              primitives=top(lambda c:classes.get(c,{}).get('semantic',{}).get('category') in ['terrain','floor','wall']),
              acrossMaps=sorted(top(), key=lambda x:(-x['maps'],-x['count'],x['classname'])))
    map_pairs={a:sorted([dict(classname=b,maps=sorted(set(usages[a])&set(usages[b])),mapCount=len(set(usages[a])&set(usages[b])))
               for b in ranked if a!=b and len(set(usages[a])&set(usages[b]))>=2],key=lambda r:(-r['mapCount'],-usage[r['classname']]['totalCount'],r['classname']))[:20] for a in ranked}
    neighbors=defaultdict(list)
    for (a,b),n in allpairs.items():
        neighbors[a].append(dict(classname=b,pairCount=n))
        if a!=b: neighbors[b].append(dict(classname=a,pairCount=n))
    spatial_top={c:sorted(v,key=lambda r:(-r['pairCount'],r['classname']))[:20] for c,v in neighbors.items()}
    declarations={c:{k:v for k,v in obj.items() if k in ['parent','declaredProperties','declaredMethods','sourceFile','sourceLine','editorAttributes']} for c,obj in classes.items()}
    write('source_declarations.json',dict(schemaVersion=1,authority='PROVISIONAL_SOURCE_INDEX',classes=declarations))
    write('model_usage.json',model_variants(instances,classes,configs))
    write('terrain_neighbors.json',terrain_neighbors(instances))
    lean=[]
    for c,obj in classes.items():
        row={k:v for k,v in obj.items() if k not in ['declaredProperties','declaredMethods','effectiveProperties','effectiveMethods']}
        row['effectivePropertiesRef']=dict(file='source_declarations.json',classname=c,merge='parent-first, child overrides; provisional')
        if reflection and 'editorPlaceable' in obj: row['effectivePropertiesRef']=dict(file='reflection.json',classname=c,field='effectiveProperties')
        lean.append(row)
    write('objects.json',dict(schemaVersion=1, authority='reflection' if reflection else 'PROVISIONAL_SOURCE_INDEX',
        editorPlaceableCount=sum(r['editorPlaceable'] for r in reflection['objects']) if reflection else None,
        sourceCandidateCount=source_count, sourceIndexLimitations=['not preprocessed; only file-local single-identifier parent aliases resolved','interface includes not expanded','literal values only; expressions retained','not proof of availability'], objects=lean))
    referenced={obj['resolvedModel'] for obj in classes.values()}
    referenced.update(norm(r['customProps']['model']) for rows in instances.values() for r in rows if isinstance(r['customProps'].get('model'),str))
    write('models.json',dict(schemaVersion=1,m2cSha256=digest(ROOT/'Src/M2C.sqf'), totalM2cModels=len(models), models=[v for k,v in models.items() if k in referenced]))
    profiles=[dict(classname=c['classname'],chunkType=c['chunkType'],**models[c['model']]) for c in core]
    engine_path=OUT/'engine_geometry.json'
    if engine_path.exists():
        measured={r['classname']:r for r in json.loads(engine_path.read_text(encoding='utf-8'))['profiles']}
        for profile in profiles:
            if profile['classname'] in measured:
                r=measured[profile['classname']]
                if norm(r['model'])!=profile['model']: raise ValueError('Fresh geometry model mismatch: '+profile['classname'])
                profile['liveProbe']=r
                profile['visualBounds']=fact(r['visualBounds'][:2],'engineMeasured',status='VERIFIED',freshness='LIVE_PROBE')
                profile['dimensions']=fact(r['dimensions'],'engineMeasured',status='VERIFIED',meaning='measured AABB dimensions; not exact mesh')
                profile['supportPlane']=fact(r['visualBounds'][0][2],'ruleDerived',status='APPROXIMATE',meaning='live AABB minZ, not LandContact')
                profile['occupiedVolume']=fact(math.prod(r['dimensions']),'ruleDerived',status='APPROXIMATE',meaning='live AABB volume, NOT collision volume')
                if 'geometryBounds' in r:
                    gb=r['geometryBounds'][:2]
                    valid=len(gb)==2 and all(len(v)==3 for v in gb) and all(math.isfinite(b-a) and b>a for a,b in zip(*gb))
                    profile['geometryBounds']=fact(gb,'engineMeasured',status='VERIFIED' if valid else 'UNKNOWN',meaning='Geometry LOD AABB only; missing/degenerate bounds cannot certify collision')
        for c in core:
            c['dimensions']=next(p['dimensions'] for p in profiles if p['classname']==c['classname'])
    write('geometry.json',dict(schemaVersion=1, profiles=profiles,
        unknown=['LandContact','Geometry LOD mesh','ROADWAY','support points','wall/ceiling contact','clearance','door sweep','interaction clearance','semantic front']))
    write('usage.json',usage); write('maps.json',maps); write('top_objects.json',tops)
    write('core_assets.json',dict(schemaVersion=1,status='CANDIDATE_REVIEW_SET',assets=core))
    write('cooccurrence.json',dict(radiusMeters=5, distance='3D origin distance; no surface-distance or causality claim',
        spatialTop20=spatial_top,mapTop20=map_pairs, completeReconstruction='usage.json map sets and instances/*.json; rankings truncated to 20 neighbors per class'))
    write('spatial.json',spatial_stats)
    write('compositions.json',dict(method='translation-only; anchor plus nearest four origins in 5m, positions quantized 5cm, absolute Euler angles 0.001rad; overlapping occurrences retained',patterns=patterns))
    checks=dict(status='PARTIAL', errors=[], sourceDuplicates=duplicates,
        mapObjectConservation=all(m['sourceObjectCount']==m['parsedRelevantObjects']+len(m['excludedObjects']) for m in maps.values()),
        unknownMapClasses={n:m['unknownClasses'] for n,m in maps.items() if m['unknownClasses']},
        pending=['live reflection export','fresh geometry probes','human review of core assets'])
    write('build_summary.json',checks)
    generated=[p for p in OUT.rglob('*.json') if p.name not in ['build_state.json','validation.json','reflection.json','engine_geometry.json']]
    inputs={ROOT/'Src/M2C.sqf', OUT.parent/'core_asset_policy.json'}
    inputs.update(OUT.parent/name for name in ['build_catalog.py','catalog_parser.py'])
    inputs.update(ROOT/m['source'] for m in maps.values())
    inputs.update(ROOT/m['runtimeComparison']['source'] for m in maps.values())
    inputs.update(ROOT/r['sourceFile'] for r in classes.values() if 'sourceFile' in r)
    inputs.update(p for p in [OUT/'reflection.json',OUT/'engine_geometry.json'] if p.exists())
    write('build_state.json',dict(schemaVersion=1,status='COMPLETE',
        outputs={p.relative_to(OUT).as_posix():digest(p) for p in sorted(generated)},
        inputs={p.relative_to(ROOT).as_posix():digest(p) for p in sorted(inputs)}))
    return classes,maps,usage,core,tops


def main():
    p=argparse.ArgumentParser(); p.add_argument('--top',type=int); p.add_argument('--class',dest='classname'); p.add_argument('--build',action='store_true')
    args=p.parse_args()
    if args.build or not (OUT/'usage.json').exists():
        classes,maps,usage,core,tops=build()
        from validate_catalog import validate
        result=validate()
        if result['errors']: raise ValueError(result['errors'])
        print(json.dumps(dict(candidates=len(classes),objects=sum(m['parsedRelevantObjects'] for m in maps.values()),core=len(core)),ensure_ascii=False))
    if args.top: print(json.dumps(json.loads((OUT/'top_objects.json').read_text(encoding='utf-8'))['overall'][:args.top],ensure_ascii=False,indent=2))
    if args.classname: print(json.dumps(json.loads((OUT/'usage.json').read_text(encoding='utf-8')).get(args.classname),ensure_ascii=False,indent=2))


if __name__=='__main__': main()
