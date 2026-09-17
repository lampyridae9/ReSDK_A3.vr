"""Calibrate native Eden placing points; retain owned samples for human review."""
from __future__ import annotations
import json
from pathlib import Path
from room_generator.gateway import MapAutomationRoomGateway

BASE = Path(__file__).resolve().parent
CLASSES = {
    'ConcretePanel': ('floor', 'concrete'),
    'BrickThinWall': ('wall', 'brick'),
    'BrickThinWallSmall': ('wall', 'brick'),
    'SteelThinWallSmall': ('wall', 'sheet_metal'),
    'SteelThinWallMedium': ('wall', 'sheet_metal'),
    'MediumWoodenWall': ('wall', 'wood'),
    'WoodenDoor': ('door', 'wood'),
    'StoneBigLadderDouble': ('stairs', 'stone'),
    'MediumConcreteFloor': ('floor', 'concrete'),
    'MediumConcreteFloor1': ('floor', 'concrete'),
    'BrickThinWallDoorwayCenter': ('wall', 'brick'),
    'BrickThinWallDoorwayBig': ('wall', 'brick'),
    'Wicket': ('door', 'sheet_metal'),
    'ConcreteSmallPole': ('support', 'concrete'),
}


def profile():
    gateway = MapAutomationRoomGateway(15)
    before = gateway.snapshot()
    existing = {x['semanticId']: x for x in before.objects}
    operations = []
    for i, name in enumerate(CLASSES):
        sid = 'phase8a_anchor__' + name
        if sid in existing:
            if existing[sid]['class'] != name:
                raise ValueError('calibration identity conflict: ' + sid)
            continue
        operations.append({'operation': 'create', 'arguments': {'semanticId': sid,
            'class': name, 'position': [4820 + i * 8, 4700, 10],
            'rotation': [0, 0, 0], 'scale': 1, 'parentId': 'phase8a_anchor_review'}})
    applied = gateway.apply(operations, before.revision) if operations else {'revision': before.revision, 'result': before.objects}
    # Preserve curated contact/portal facts when refreshing the native transforms.
    previous_path = BASE/'structural_assets.json'
    previous = json.loads(previous_path.read_text(encoding='utf-8'))['assets'] if previous_path.exists() else {}
    assets = dict(previous)
    for name, (role, material) in CLASSES.items():
        row = next(x for x in applied['result'] if x['semanticId'] == 'phase8a_anchor__' + name)
        if any(abs(a) > .001 for a in row['rotation']) or abs(row['scale'] - 1) > .001:
            raise ValueError('calibration requires upright native sample: ' + name)
        low, high = row['visualBoundsModel'][:2]
        placing = row['placingPointModel']
        observed = row['positionASL'][2] - row['modelOriginASL'][2]
        if abs(observed - placing[2]) > .002:
            raise ValueError('Eden placing point calibration mismatch: ' + name)
        cx, cy = [(low[i] + high[i]) / 2 for i in (0, 1)]
        anchors = {'bottomCenter': [cx, cy, low[2]], 'topCenter': [cx, cy, high[2]],
            'leftEdge': [low[0], cy, low[2]], 'rightEdge': [high[0], cy, low[2]],
            'innerFace': [cx, low[1], (low[2]+high[2])/2],
            'outerFace': [cx, high[1], (low[2]+high[2])/2]}
        assets[name] = {**previous.get(name, {}), 'role': role, 'materialFamily': material,
            'placingPoint': placing, 'bounds': [low, high], 'anchors': anchors,
            'geometryBounds': row['geometryBoundsModel'][:2],
            'dimensions': [high[i]-low[i] for i in range(3)],
            'provenance': {'status': 'EDEN_MEASURED_ENVELOPE', 'sessionId': before.session_id,
                'revision': applied['revision'], 'sampleId': row['semanticId'],
                'basis': 'Native upright Eden instance; visual envelope, not collision mesh'},
            'walkability': 'UNKNOWN', 'contactMesh': 'UNKNOWN'}
        if role == 'stairs':
            assets[name].setdefault('landingVerification', 'UNKNOWN')
        if role == 'door':
            assets[name].setdefault('hingeVerification', 'UNKNOWN')
    evidence = {'sessionId': before.session_id, 'revision': applied['revision'],
        'sceneBefore': before.fingerprint, 'samples': [x for x in applied['result'] if x['semanticId'].startswith('phase8a_anchor__')],
        'cleanup': 'KEPT_FOR_REVIEW'}
    (BASE/'artifacts/phase8a_anchor_readback.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
    output = BASE/'structural_assets.json'
    output.write_text(json.dumps({'schemaVersion': 1, 'assets': assets}, indent=2)+'\n', encoding='utf-8')
    print(output)


if __name__ == '__main__':
    profile()
