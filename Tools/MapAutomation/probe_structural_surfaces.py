"""Reproducible native surface evidence; never equates sampled rays with walkthrough."""
from __future__ import annotations
import json
from pathlib import Path
from room_generator.gateway import MapAutomationRoomGateway

BASE = Path(__file__).resolve().parent


def doorway_rays():
    # Include positive controls in jambs/header, and boundary samples on both sides.
    return [[[x, -1, z], [x, 1, z], lod]
            for lod in ('GEOM', 'VIEW')
            for x in (-2, -.7, -.61, -.59, 0, .59, .61, .7, 2)
            for z in (-1.4, 0, .49, .51, 1)]


def roadway_rays(width, depth, steps=12):
    return [[[x, y, 5], [x, y, -5], 'ROADWAY']
            for x in (-width/2+.1, 0, width/2-.1)
            for y in (-depth/2+.1+i*(depth-.2)/steps for i in range(steps+1))]


def measure(gateway, revision, classname, rays):
    samples = []
    result = None
    # Keep JSON below the extension's string transport limit, even with floats.
    for start in range(0, len(rays), 32):
        result = gateway.probe_geometry(revision, classname, rays[start:start+32])['result']
        batch = result.get('surfaceSamples')
        if batch is None or len(batch) != len(rays[start:start+32]):
            raise ValueError('SURFACE_PROBE_NOT_LOADED: recompile Eden editor before measuring')
        if not result.get('cleanupVerified') or not result.get('sceneUnchanged'):
            raise ValueError('SURFACE_PROBE_CHANGED_SCENE')
        samples.extend(batch)
    return {**result, 'surfaceSamples': samples}


def main():
    gateway = MapAutomationRoomGateway(20)
    before = gateway.snapshot()
    candidates = {
        'BrickThinWallDoorwayCenter': doorway_rays(),
        'MediumConcreteFloor': roadway_rays(3, 6),
        'MediumConcreteFloor1': roadway_rays(6, 6),
        'StoneBigLadderDouble': roadway_rays(3.1, 6.00222, 60),
    }
    evidence = {'sessionId': before.session_id, 'revision': before.revision, 'assets': {}}
    for name, rays in candidates.items():
        row = measure(gateway, before.revision, name, rays)
        evidence['assets'][name] = row
        print(name, 'hits', sum(bool(s['hits']) for s in row['surfaceSamples']), '/', len(rays), flush=True)
    after = gateway.snapshot()
    if after.fingerprint != before.fingerprint:
        raise ValueError('SCENE_CHANGED_DURING_PROFILING')
    evidence['sceneUnchanged'] = True
    path = BASE/'artifacts/phase8a_structural_surfaces.json'
    path.write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
    print(path)


if __name__ == '__main__':
    main()
