"""Promote measured contact facts without claiming runtime/player acceptance."""
import json
import hashlib
from pathlib import Path

BASE=Path(__file__).resolve().parent


def curate():
    path=BASE/'structural_assets.json'
    document=json.loads(path.read_text(encoding='utf-8'));assets=document['assets']
    source=BASE/'artifacts/phase8a_structural_surfaces.json'
    evidence=json.loads(source.read_text(encoding='utf-8'))
    provenance={'method':'lineIntersectsSurfaces, native simple object, no fallback LOD',
        'sessionId':evidence['sessionId'],'revision':evidence['revision'],
        'evidenceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'runtimeWalkthrough':'UNKNOWN'}
    for name in ('MediumConcreteFloor','MediumConcreteFloor1'):
        asset=assets[name];row=evidence['assets'][name]
        samples=row['surfaceSamples']
        if len(samples)!=39 or any(not s['hits'] for s in samples):
            raise ValueError('INCOMPLETE_FLOOR_SURFACE_SAMPLES: '+name)
        heights=[s['hits'][0]['positionModel'][2] for s in samples]
        if max(heights)-min(heights)>.001 or any(s['hits'][0]['normal'][2]<.99 for s in samples):
            raise ValueError('FLOOR_SUPPORT_NOT_FLAT: '+name)
        asset['supportSurface']={'topModelZ':sum(heights)/len(heights),
            'footprint':[-asset['dimensions'][0]/2,-asset['dimensions'][1]/2,
                         asset['dimensions'][0]/2,asset['dimensions'][1]/2],
            'tilingIncrement':asset['dimensions'][:2], 'verification':'ROADWAY_SAMPLED',
            'samples':samples,'provenance':provenance}
    asset=assets['BrickThinWallDoorwayCenter']
    samples=evidence['assets']['BrickThinWallDoorwayCenter']['surfaceSamples']
    for s in samples:
        x,_,z=s['ray'][0]
        expected=abs(x)>=.6 or z>=.5
        if bool(s['hits'])!=expected:
            raise ValueError('DOORWAY_SURFACE_CONTRADICTS_PROFILE')
    asset['nativeOpening']={'rectangleXZ':[-.6,-1.5,.6,.5],
        'verification':'SURFACE_SAMPLED','boundaryTolerance':.01,
        'samples':samples,'provenance':provenance}
    # Bottom entry is underneath the overhead top platform. A ray from above
    # that platform cannot establish the lower entry height.
    bottom_source=BASE/'artifacts/phase8a_stair_bottom_surfaces.json'
    bottom=json.loads(bottom_source.read_text(encoding='utf-8'))['surfaceSamples']
    measured=[s for s in bottom if s['ray'][0]==[-1,-1,-.3]]
    if len(measured)!=1 or not measured[0]['hits']:
        raise ValueError('STAIR_BOTTOM_ENTRY_NOT_MEASURED')
    z=measured[0]['hits'][0]['positionModel'][2]
    if abs(z+1.65)>.002:raise ValueError('STAIR_BOTTOM_ENTRY_MISMATCH')
    assets['StoneBigLadderDouble']['landings']={'bottom':[-1,-1,z], 'top':[0,-2,1.65002]}
    assets['StoneBigLadderDouble']['landingVerification']='VERIFIED'
    assets['StoneBigLadderDouble']['landingEvidence']={**provenance,
        'interpretation':'Geometric sampled entry and exit only; not player acceptance',
        'bottomSamples':bottom,'roadwaySamples':evidence['assets']['StoneBigLadderDouble']['surfaceSamples']}
    path.write_text(json.dumps(document,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':curate()
