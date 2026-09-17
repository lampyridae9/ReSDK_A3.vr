"""Read-only empirical construction evidence; proximity does not prove attachment."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent
MAPS = ('dorm', 'saloonv2', 'barony', 'detective', 'truba', 'theatre', 'holiday', 'hunt', 'minimap')


def family(name):
    name = name.lower()
    for category, tokens in (
        ('stairs', ('stairs', 'ladder')),
        ('doors', ('door', 'gate')),
        ('walls', ('wall',)),
        ('floors', ('floor', 'concretepanel', 'platform')),
    ):
        if any(token in name for token in tokens):
            return category
    return None


def mine():
    result = {'schemaVersion': 1, 'status': 'EMPIRICAL_CANDIDATES',
              'limitations': ['Class-name role heuristics require curation.',
                  'Nearest XY neighbor within 8m and vertical separation <= 5m is not a verified attachment.',
                  'SQM positions are absolute elevations; do not copy offsets to Eden without frame calibration.',
                  'Deltas are world XYZ, not model-local anchors; no walkability is inferred.'], 'maps': {}}
    for name in MAPS:
        path = BASE / 'catalog' / 'instances' / (name + '.json')
        rows = json.loads(path.read_text(encoding='utf-8'))
        groups = {kind: [r for r in rows if family(r.get('classname', '')) == kind]
                  for kind in ('floors', 'walls', 'doors', 'stairs')}
        pairs = []
        for source, target in (('walls', 'walls'), ('floors', 'walls'), ('doors', 'walls'), ('stairs', 'floors')):
            counts = Counter()
            examples = {}
            for a in groups[source]:
                candidates = []
                for b in groups[target]:
                    if a['entityId'] == b['entityId']:
                        continue
                    delta = [b['position'][i] - a['position'][i] for i in range(3)]
                    distance = math.hypot(*delta[:2])
                    if distance <= 8 and abs(delta[2]) <= 5:
                        candidates.append((distance, abs(delta[2]), b['entityId'], b, delta))
                if not candidates:
                    continue
                _, _, _, b, delta = min(candidates, key=lambda item: item[:3])
                key = (a['classname'], b['classname'], *(round(v, 1) for v in delta))
                counts[key] += 1
                examples.setdefault(key, {'sourceEntity': a['entityId'], 'targetEntity': b['entityId'],
                    'sourcePosition': a['position'], 'targetPosition': b['position'],
                    'sourceAnglesRadians': a.get('anglesRadians'), 'targetAnglesRadians': b.get('anglesRadians'),
                    'deltaXYZ': delta})
            pairs.append({'relation': source + '->' + target, 'topCandidates': [
                {'classes': list(k[:2]), 'roundedDeltaXYZ': list(k[2:]), 'count': n, 'example': examples[k]}
                for k, n in counts.most_common(12)]})
        result['maps'][name] = {'sourceSha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'roleCounts': {k: len(v) for k, v in groups.items()},
            'classes': {k: dict(Counter(r['classname'] for r in v).most_common(15)) for k, v in groups.items()},
            'relativeTransforms': pairs}
    return result


if __name__ == '__main__':
    output = BASE / 'artifacts' / 'phase8a_structural_mining.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(mine(), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(output)
