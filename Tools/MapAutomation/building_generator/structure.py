"""Phase 8A local structural plan, calibrated placement and shell validation.

Envelope validation is deliberately separate from collision/walkthrough acceptance.
Native modules are never stretched or silently omitted to make a plan pass.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import itertools
import json
import math
from pathlib import Path
from typing import Any

ASSETS_PATH = Path(__file__).resolve().parents[1] / 'structural_assets.json'


def load_structural_assets():
    assets = json.loads(ASSETS_PATH.read_text(encoding='utf-8'))['assets']
    for name, asset in assets.items():
        vectors = [asset['placingPoint'], *asset['bounds'], *asset['anchors'].values()]
        if any(len(v)!=3 or any(not isinstance(x,(int,float)) or not math.isfinite(x) for x in v) for v in vectors):
            raise ValueError('STRUCTURAL_ASSET_INVALID: '+name)
        if any(asset['bounds'][1][i]<=asset['bounds'][0][i] or abs(asset['dimensions'][i]-(asset['bounds'][1][i]-asset['bounds'][0][i]))>.002 for i in range(3)):
            raise ValueError('STRUCTURAL_ASSET_BOUNDS_MISMATCH: '+name)
    return assets


@dataclass(frozen=True)
class BuildingFrame:
    origin: tuple[float, float, float]
    yaw: float = 0

    @property
    def local_x(self):
        r = math.radians(self.yaw)
        return (math.cos(r), -math.sin(r), 0)

    @property
    def local_y(self):
        r = math.radians(self.yaw)
        return (math.sin(r), math.cos(r), 0)

    def world(self, point):
        x, y, z = point
        return [self.origin[i] + self.local_x[i]*x + self.local_y[i]*y + (z if i == 2 else 0) for i in range(3)]

    def local(self, point):
        d = [point[i]-self.origin[i] for i in range(3)]
        return [sum(d[i]*self.local_x[i] for i in range(3)), sum(d[i]*self.local_y[i] for i in range(3)), d[2]]

    def json(self):
        return {'origin': list(self.origin), 'localX': self.local_x, 'localY': self.local_y,
                'up': [0, 0, 1], 'floorDatum': 0, 'yaw': self.yaw}


@dataclass(frozen=True)
class FloorLevel:
    id: str
    story_index: int
    datum_z: float


@dataclass(frozen=True)
class Opening:
    id: str
    wall_segment_id: str
    offset_along_wall: float
    width: float
    height: float
    bottom: float = 0


@dataclass(frozen=True)
class FloorOpening:
    owner_floor: str
    rectangle: tuple[float, float, float, float]
    vertical_connection_id: str


@dataclass(frozen=True)
class BuildingStructuralProfile:
    story_height: float
    floor_thickness: float
    wall_height: float
    wall_thickness: float
    ceiling_offset: float
    provenance: str


@dataclass(frozen=True)
class BuildingMaterialPalette:
    primary_walls: tuple[str, ...]
    secondary_walls: tuple[str, ...]
    floors: tuple[str, ...]
    door_family: tuple[str, ...]
    provenance: str = 'curated families; contiguous runs; geometry compatibility required'


def rotate(point, yaw):
    if isinstance(yaw, (list, tuple)):
        pitch, bank, heading = map(math.radians, yaw)
        x,y,z = point
        x,y = x*math.cos(heading)+y*math.sin(heading),-x*math.sin(heading)+y*math.cos(heading)
        x,z = x*math.cos(bank)-z*math.sin(bank),x*math.sin(bank)+z*math.cos(bank)
        y,z = y*math.cos(pitch)+z*math.sin(pitch),-y*math.sin(pitch)+z*math.cos(pitch)
        return [x,y,z]
    r = math.radians(yaw)
    x, y, z = point
    return [x*math.cos(r)+y*math.sin(r), -x*math.sin(r)+y*math.cos(r), z]


def anchor_position(asset, anchor, target, yaw=0):
    """Eden position = target + native placing offset - rotated model anchor.

    Eden rotates about the model origin; the position attribute's placing offset
    stays in the original axes. Verified with upright and bank=90 native probes.
    """
    p = asset['placingPoint']
    a = asset['anchors'][anchor]
    rotated = rotate(a, yaw)
    return [target[i]+p[i]-rotated[i] for i in range(3)]


def physical_bounds(operation, assets):
    args = operation['arguments']
    asset = assets[args['class']]
    if args.get('scale', 1) != 1:
        raise ValueError('STRUCTURAL_TRANSFORM_UNSUPPORTED')
    yaw = args['rotation']
    corners = []
    for corner in itertools.product(*zip(*asset['bounds'])):
        relative = rotate(corner, yaw)
        corners.append([args['position'][i]-asset['placingPoint'][i]+relative[i] for i in range(3)])
    return [[min(p[i] for p in corners) for i in range(3)], [max(p[i] for p in corners) for i in range(3)]]


def model_point_world(operation, asset, point):
    args = operation['arguments']
    relative = rotate(point, args['rotation'])
    return [args['position'][i]-asset['placingPoint'][i]+relative[i] for i in range(3)]


def wall_solid_bounds(operation, assets):
    """Subtract only an explicitly measured native through-opening, never a plan hole."""
    asset = assets[operation['arguments']['class']]
    opening = asset.get('nativeOpening')
    if opening is None:
        return [physical_bounds(operation, assets)]
    if opening.get('verification') != 'SURFACE_SAMPLED':
        raise ValueError('NATIVE_OPENING_UNVERIFIED')
    low, high = asset['bounds']
    x0, z0, x1, z1 = opening['rectangleXZ']
    if not (low[0]<=x0<x1<=high[0] and low[2]<=z0<z1<=high[2]):
        raise ValueError('NATIVE_OPENING_OUTSIDE_ASSET')
    boxes = [(low, [x0, high[1], high[2]]),
             ([x1, low[1], low[2]], high),
             ([x0, low[1], low[2]], [x1, high[1], z0]),
             ([x0, low[1], z1], [x1, high[1], high[2]])]
    result = []
    for a,b in boxes:
        if any(b[i]-a[i]<1e-6 for i in range(3)):
            continue
        corners = [model_point_world(operation,asset,c) for c in itertools.product(*zip(a,b))]
        result.append([[min(c[i] for c in corners) for i in range(3)],
                       [max(c[i] for c in corners) for i in range(3)]])
    return result


def validate_stair_connection(connection, lower, upper, operations, assets, tolerance=.02):
    """Validate the placed instance, not just the asset's advertised rise."""
    errors = []
    def fail(code):
        errors.append({'code': code, 'connectionId': connection.id})
    stairs = [op for op in operations if op['stage']=='stairs' and op['arguments']['parentId']==connection.id]
    if len(stairs)!=1:
        fail('STAIR_MISSING_OR_DUPLICATED')
        return errors
    op = stairs[0]
    if op['arguments']['class'] != connection.asset:
        fail('STAIR_ASSET_MISMATCH')
        return errors
    asset = assets[connection.asset]
    if abs((op['arguments']['rotation'][2]-connection.yaw+180)%360-180)>tolerance:
        fail('STAIR_DIRECTION_MISMATCH')
    landings = asset.get('landings')
    if asset.get('landingVerification')!='VERIFIED' or not landings:
        fail('STAIR_LANDINGS_UNVERIFIED')
        return errors
    points = [model_point_world(op, asset, landings[name]) for name in ('bottom', 'top')]
    if abs((landings['top'][2]-landings['bottom'][2])-(upper.elevation-lower.elevation))>tolerance:
        fail('STAIR_RISE_MISMATCH')
    for name, point, floor, region in zip(('BOTTOM','TOP'),points,(lower,upper),
            (connection.entry_region_lower,connection.entry_region_upper)):
        if abs(point[2]-floor.elevation)>tolerance:
            fail('STAIR_'+name+'_LANDING_WRONG_DATUM')
        if not (region.x-tolerance<=point[0]<=region.x2+tolerance and region.y-tolerance<=point[1]<=region.y2+tolerance):
            fail('STAIR_'+name+'_LANDING_MISALIGNED')
    # Measured tread/roadway points define a traversable candidate path. Test
    # a conservative body envelope, leaving actual movement to runtime review.
    for point in asset.get('walkPathModel',[]):
        x,y,z=model_point_world(op,asset,point)
        body=(x-.25,y-.25,x+.25,y+.25)
        for other in operations:
            if other is op or other['stage'] in {'doors','stairs'}:continue
            try:
                boxes=wall_solid_bounds(other,assets) if other['stage']=='walls' else [physical_bounds(other,assets)]
            except (KeyError,ValueError):continue
            for lo,hi in boxes:
                if hi[2]>z+.15 and lo[2]<z+1.8 and overlap(body,(lo[0],lo[1],hi[0],hi[1]))>1e-5:
                    fail('STAIR_APPROACH_OR_HEADROOM_BLOCKED')
                    return errors
    return errors


def overlap(a, b):
    return max(0, min(a[2], b[2])-max(a[0], b[0])) * max(0, min(a[3], b[3])-max(a[1], b[1]))


def uncovered(target, rectangles, tolerance=1e-6):
    """Exact axis-aligned rectangle union by coordinate compression, no sampling grid."""
    x0, y0, x1, y1 = target
    xs = sorted({x0, x1, *(x for r in rectangles for x in (r[0], r[2]) if x0 < x < x1)})
    ys = sorted({y0, y1, *(y for r in rectangles for y in (r[1], r[3]) if y0 < y < y1)})
    missing = 0.0
    for a, b in zip(xs, xs[1:]):
        for c, d in zip(ys, ys[1:]):
            x, y = (a+b)/2, (c+d)/2
            if not any(r[0]-tolerance <= x <= r[2]+tolerance and r[1]-tolerance <= y <= r[3]+tolerance for r in rectangles):
                missing += (b-a)*(d-c)
    return missing


class FloorAssemblyValidator:
    def validate(self, level, tiles, openings, footprint, tolerance=.02):
        errors = []
        for tile in tiles:
            if abs(tile['top']-level.datum_z) > tolerance:
                errors.append({'code': 'FLOOR_WRONG_DATUM', 'floorId': level.id, 'objectId': tile['id']})
            for hole in openings:
                if overlap(tile['rect'], hole) > 1e-6:
                    errors.append({'code': 'FLOOR_OPENING_BLOCKED', 'floorId': level.id, 'objectId': tile['id']})
        for i, a in enumerate(tiles):
            for b in tiles[i+1:]:
                if overlap(a['rect'], b['rect']) > 1e-6:
                    errors.append({'code': 'FLOOR_MODULE_OVERLAP', 'objects': [a['id'], b['id']]})
        gap = uncovered(footprint, [t['rect'] for t in tiles]+openings)
        if gap > 1e-5:
            errors.append({'code': 'FLOOR_COVERAGE_GAP', 'floorId': level.id, 'area': gap})
        return errors


def tile_native_floor(width, depth, module, holes, max_nodes=10000):
    """Bounded exact cover with whole native slabs in either horizontal orientation."""
    cell=min(module);values=[width/cell,depth/cell,module[0]/cell,module[1]/cell]
    if any(abs(v-round(v))>1e-6 for v in values):
        raise ValueError('FLOOR_NOT_ON_NATIVE_GRID')
    nx,ny,mw,md=map(round,values);blocked=set()
    for ix in range(nx):
        for iy in range(ny):
            rect=(-width/2+ix*cell,-depth/2+iy*cell,-width/2+(ix+1)*cell,-depth/2+(iy+1)*cell)
            areas=[overlap(rect,h) for h in holes]
            if any(a>1e-6 for a in areas):
                if not any(abs(a-cell*cell)<1e-6 for a in areas):
                    raise ValueError('FLOOR_OPENING_NOT_ON_MODULE_GRID')
                blocked.add((ix,iy))
    remaining={(x,y) for x in range(nx) for y in range(ny)}-blocked
    nodes=0;dead=set()
    def solve(cells):
        nonlocal nodes
        nodes+=1
        if nodes>max_nodes:raise ValueError('FLOOR_TILING_SEARCH_BUDGET')
        if not cells:return []
        key=frozenset(cells)
        if key in dead:return None
        x,y=min(cells)
        for w,d,yaw in ((mw,md,0),(md,mw,90)):
            cover={(x+i,y+j) for i in range(w) for j in range(d)}
            if not cover<=cells:continue
            rest=solve(cells-cover)
            if rest is not None:
                return [(-width/2+(x+w/2)*cell,-depth/2+(y+d/2)*cell,yaw)]+rest
        dead.add(key)
        return None
    result=solve(remaining)
    if result is None:raise ValueError('FLOOR_UNTILABLE')
    return result


class StructuralAssembler:
    def __init__(self, profile, assets=None):
        self.profile = profile
        self.assets = assets if assets is not None else load_structural_assets()

    def compile(self, layout):
        """Migrate world layout v1 to a wholly local structural plan v2."""
        frame = BuildingFrame(layout.footprint.origin)
        structure = self.profile['structure']
        fa = self.assets[structure['floorAsset']]
        primary = self.assets[structure['wallAsset']]
        thickness = fa['dimensions'][2]
        profile = BuildingStructuralProfile(self.profile['storeyHeight'], thickness,
            primary['dimensions'][2], primary['dimensions'][1], self.profile['storeyHeight']-thickness,
            'structural_assets.json: native Eden measured envelopes')
        floors = []
        for f in layout.floors:
            walls = []
            for wall in f.walls:
                a = frame.local([*wall.start, f.elevation])
                b = frame.local([*wall.end, f.elevation])
                holes = []
                for p in f.portals:
                    if p.wall_segment != wall.id:
                        continue
                    center = frame.local([*p.center, f.elevation])
                    along = abs(center[0]-a[0])+abs(center[1]-a[1])
                    door = self.assets[p.door_asset]
                    native = self.assets.get(structure.get('doorwayAsset'), {}).get('nativeOpening')
                    height = native['rectangleXZ'][3]-native['rectangleXZ'][1] if native else door['dimensions'][2]+.02
                    if structure.get('lintelAsset'):
                        height = profile.wall_height-self.assets[structure['lintelAsset']]['dimensions'][0]
                    hole = Opening(p.id, wall.id, along-p.width/2, p.width, height)
                    holes.append({**asdict(hole), 'doorAsset': p.door_asset,
                        'spaces': [p.from_space, p.to_space]})
                walls.append({'id': wall.id, 'start': a, 'end': b, 'height': profile.wall_height,
                    'thickness': profile.wall_thickness, 'owners': list(wall.owners),
                    'exterior': wall.exterior, 'materialFamily': 'brick', 'openings': holes})
            openings = []
            for v in f.vertical_connections:
                if v.to_floor == f.id:
                    r = v.opening_region or v.occupied_region
                    a = frame.local([r.x, r.y, f.elevation]); b = frame.local([r.x2, r.y2, f.elevation])
                    openings.append(asdict(FloorOpening(f.id, (a[0], a[1], b[0], b[1]), v.id)))
            floors.append({'level': asdict(FloorLevel(f.id, f.index, f.elevation-frame.origin[2])),
                'walls': walls, 'floorOpenings': openings})
        return {'schemaVersion': 2, 'frame': frame.json(), 'profile': {**asdict(profile),
            'exterior_wall_inset':self.profile.get('exteriorWallInset',0)}, 'floors': floors,
            'materialPalette': asdict(BuildingMaterialPalette(('brick',), ('wood', 'sheet_metal'), ('concrete',), ('wood',))),
            'verification': 'ENVELOPE_ONLY; runtime collision and player traversal required'}

    def assemble(self, layout):
        # Import lazily to preserve the public helper used by older callers.
        from .generator import _physical_wall_runs, _fit_wall_modules
        plan = self.compile(layout)
        frame = BuildingFrame(layout.footprint.origin)
        ops, diagnostics = [], []
        structure = self.profile['structure']
        def emit(sid, classname, anchor, target, yaw, stage, owner, floor_id):
            local_position = anchor_position(self.assets[classname], anchor, target, yaw)
            ops.append({'operation': 'create', 'arguments': {'semanticId': sid.replace('.', '__'),
                'class': classname, 'position': frame.world(local_position), 'rotation': list(yaw) if isinstance(yaw,(list,tuple)) else [0, 0, yaw],
                'scale': 1, 'parentId': owner}, 'stage': stage, 'floorId': floor_id})
        floor_asset = self.assets[structure['floorAsset']]
        fw, fd = floor_asset['dimensions'][:2]
        fp = layout.footprint
        choices = []
        for yaw, w, d in ((0, fw, fd), (90, fd, fw)):
            nx, ny = max(1, round(fp.width/w)), max(1, round(fp.depth/d))
            choices.append((abs(nx*w-fp.width)+abs(ny*d-fp.depth), yaw, w, d, nx, ny))
        _, yaw, w, d, nx, ny = min(choices)
        levels = [(f['level']['id'], f['level']['datum_z'], f['floorOpenings']) for f in plan['floors']]
        levels.append(('roof', levels[-1][1]+self.profile['storeyHeight'], []))
        for level_id, z, openings in levels:
            if structure.get('mixedFloorOrientations'):
                try:
                    tiles=tile_native_floor(fp.width,fp.depth,(fw,fd),[h['rectangle'] for h in openings])
                    for i,(cx,cy,angle) in enumerate(tiles):
                        emit(f'building_001__{level_id}__floor_module_{i+1:03d}',structure['floorAsset'],
                            'topCenter',[cx,cy,z],angle,'floors',level_id,level_id)
                except ValueError as exc:
                    diagnostics.append({'code':str(exc),'floorId':level_id})
                continue
            for ix in range(nx):
                for iy in range(ny):
                    cx, cy = (ix-(nx-1)/2)*w, (iy-(ny-1)/2)*d
                    tile = (cx-w/2, cy-d/2, cx+w/2, cy+d/2)
                    intersections = [overlap(tile, h['rectangle']) for h in openings]
                    if any(a > 1e-6 for a in intersections):
                        if not any(abs(a-w*d) < 1e-5 for a in intersections):
                            diagnostics.append({'code': 'FLOOR_OPENING_NOT_ON_MODULE_GRID', 'floorId': level_id,
                                'tile': tile, 'reason': 'Native slab cannot be cut; adapt layout or module family'})
                        continue
                    emit(f'building_001__{level_id}__floor_module_{ix*ny+iy+1:03d}', structure['floorAsset'],
                        'topCenter', [cx, cy, z], yaw, 'floors', level_id, level_id)
        for floor in layout.floors:
            z = floor.elevation-frame.origin[2]
            for index, run in enumerate(_physical_wall_runs(floor), 1):
                horizontal = run['axis'] == 'H'
                associated = sorted([p for p in floor.portals if p.wall_segment in {w.id for w in run['walls']}],
                    key=lambda p: p.center[0] if horizontal else p.center[1])
                cursor = run['start']; intervals = []
                for portal in associated:
                    along = portal.center[0] if horizontal else portal.center[1]
                    doorway_class = structure.get('doorwayAsset')
                    native = self.assets.get(doorway_class, {}).get('nativeOpening')
                    span = portal.width
                    if native:
                        doorway = self.assets[doorway_class]
                        x0, _, x1, _ = native['rectangleXZ']
                        if abs((x1-x0)-portal.width)>.02:
                            diagnostics.append({'code':'PORTAL_NATIVE_WIDTH_MISMATCH','portalId':portal.id})
                        span = doorway['dimensions'][0]
                        center = along-(x0+x1)/2
                        target = frame.local([center if horizontal else run['fixed'],run['fixed'] if horizontal else center,floor.elevation])
                        emit('building_001__'+portal.id+'__opening',doorway_class,'bottomCenter',target,
                            0 if horizontal else 90,'walls',portal.wall_segment,floor.id)
                        left, right = center-span/2, center+span/2
                    else:
                        left, right = along-span/2, along+span/2
                    if left < cursor-1e-6 or right > run['end']+1e-6:
                        diagnostics.append({'code': 'OPENING_OUTSIDE_WALL_OR_OVERLAPPING', 'portalId': portal.id})
                    intervals.append((cursor, left)); cursor = right
                intervals.append((cursor, run['end']))
                # Keep runs grouped by material. No random tile-by-tile palette changes.
                candidates = []
                for item in structure['wallModules']:
                    asset = self.assets.get(item['asset'])
                    if asset is None:
                        continue
                    if abs(asset['dimensions'][2]-self.profile['wallHeight']) > self.profile.get('contactTolerance',.02):
                        continue
                    candidates.append({**item, 'length': asset['dimensions'][0]})
                count = 0
                for start, end in intervals:
                    if end-start < 1e-6:
                        continue
                    try:
                        chosen, seam = _fit_wall_modules(end-start, candidates, .02, 0)
                    except ValueError as exc:
                        diagnostics.append({'code': 'WALL_RUN_UNTILABLE', 'floorId': floor.id,
                            'wallIds': [x.id for x in run['walls']], 'interval': [start, end], 'message': str(exc)})
                        continue
                    cursor = start
                    for item in chosen:
                        count += 1
                        center = cursor+item['length']/2
                        world = [center if horizontal else run['fixed'], run['fixed'] if horizontal else center, floor.elevation]
                        target = frame.local(world)
                        emit(f'building_001__{floor.id}__run_{index:03d}__module_{count:03d}', item['asset'],
                            'bottomCenter', target, 0 if horizontal else 90, 'walls',
                            f'{floor.id}.run_{index:03d}', floor.id)
                        cursor += item['length']+seam
            for portal in floor.portals:
                wall = next(w for w in floor.walls if w.id == portal.wall_segment)
                horizontal = abs(wall.start[1]-wall.end[1]) < 1e-6
                if structure.get('lintelAsset'):
                    lintel_class=structure['lintelAsset'];asset=self.assets[lintel_class]
                    if 'lintelTop' not in asset['anchors']:
                        diagnostics.append({'code':'LINTEL_POSE_UNPROFILED','portalId':portal.id})
                    else:
                        emit('building_001__'+portal.id+'__lintel',lintel_class,'lintelTop' if horizontal else 'lintelTopY',
                            frame.local([*portal.center,floor.elevation+self.profile['wallHeight']]),
                            [0,90,0] if horizontal else [90,0,0],'headers',portal.id,floor.id)
                emit('building_001__'+portal.id, portal.door_asset, 'bottomCenter',
                    frame.local([*portal.center, floor.elevation]), (0 if horizontal else 90)+self.assets[portal.door_asset].get('insertionYaw',0), 'doors', portal.id, floor.id)
        for v in layout.floors[0].vertical_connections:
            emit('building_001__'+v.id, v.asset, 'bottomCenter', frame.local([*v.occupied_region.center, layout.floors[0].elevation]),
                v.yaw, 'stairs', v.id, v.from_floor)
            guard=structure.get('stairGuardAsset')
            if guard and v.opening_region:
                hole=v.opening_region;thickness=self.assets[guard]['dimensions'][1]
                top=next(f.elevation for f in layout.floors if f.id==v.to_floor)
                length=self.assets[guard]['dimensions'][2]
                # Leave the front edge open at the integrated exit platform.
                pieces=[]
                for edge in (hole.x-thickness/2,hole.x2+thickness/2):
                    count=round(hole.depth/length)
                    for i in range(count):pieces.append(([edge,hole.y+(i+.5)*hole.depth/count,top],[90,0,90]))
                pieces.append(([hole.center[0],hole.y2+thickness/2,top],[0,90,0]))
                for i,(target,rotation) in enumerate(pieces):
                    emit(f'building_001__{v.id}__guard_{i}',guard,'guardBottom',frame.local(target),
                        rotation,'guards',v.id,v.to_floor)
        return ops, diagnostics, plan


class BuildingShellValidator:
    def __init__(self, assets=None, tolerance=.02):
        self.assets = assets if assets is not None else load_structural_assets()
        self.tolerance = tolerance

    def validate(self, layout, operations, plan):
        errors = []
        frame = BuildingFrame(tuple(plan['frame']['origin']))
        physical = []
        for op in operations:
            try:
                low, high = physical_bounds(op, self.assets)
                physical.append((op, frame.local(low), frame.local(high)))
            except (KeyError, ValueError) as exc:
                errors.append({'code': 'STRUCTURAL_ASSET_UNPROFILED', 'message': str(exc)})
        profile = plan['profile']; tol = self.tolerance
        if abs(profile['story_height']-profile['wall_height']-profile['floor_thickness']) > tol:
            errors.append({'code': 'STORY_HEIGHT_INCOMPATIBLE', 'profile': profile})
        levels = [(f['level'], f['floorOpenings']) for f in plan['floors']]
        levels.append((asdict(FloorLevel('roof', len(levels), levels[-1][0]['datum_z']+profile['story_height'])), []))
        for level_dict, holes in levels:
            level = FloorLevel(**level_dict)
            tiles = [{'id': op['arguments']['semanticId'], 'rect': (a[0], a[1], b[0], b[1]), 'top': b[2]}
                for op, a, b in physical if op['stage'] == 'floors' and op['floorId'] == level.id]
            errors.extend(FloorAssemblyValidator().validate(level, tiles, [h['rectangle'] for h in holes],
                (-layout.footprint.width/2, -layout.footprint.depth/2, layout.footprint.width/2, layout.footprint.depth/2), tol))
        for floor in plan['floors']:
            level = floor['level']; datum = level['datum_z']
            walls = [(op, a, b) for op, a, b in physical if op['stage'] in {'walls','headers'} and op['floorId'] == level['id']]
            seen = set()
            # Enclosure must also reject a missing logical boundary, not only missing assets.
            fw,fd=layout.footprint.width/2,layout.footprint.depth/2
            inset=profile.get('exterior_wall_inset',0)
            for axis,fixed,start,end in ((0,-fd+inset,-fw,fw),(0,fd-inset,-fw,fw),(1,-fw+inset,-fd,fd),(1,fw-inset,-fd,fd)):
                spans=[]
                for wall in floor['walls']:
                    if wall.get('exterior') and abs(wall['start'][1-axis]-fixed)<tol and abs(wall['end'][1-axis]-fixed)<tol:
                        spans.append((wall['start'][axis],0,wall['end'][axis],1))
                if uncovered((start,0,end,1),spans)>tol:
                    errors.append({'code':'EXTERIOR_SHELL_OPEN','floorId':level['id'],'axis':axis,'fixed':fixed})
            for i,(op,a,b) in enumerate(walls):
                for other,c,d in walls[i+1:]:
                    if (b[0]-a[0]>b[1]-a[1]) != (d[0]-c[0]>d[1]-c[1]):continue
                    penetration=[min(b[k],d[k])-max(a[k],c[k]) for k in range(3)]
                    if min(penetration)>tol+1e-6:
                        # A lintel's ends bear inside its own portal jambs. This
                        # exception is spatially bounded to that measured joint.
                        header,ha,hb=(op,a,b) if op['stage']=='headers' else (other,c,d)
                        solid,sa,sb=(other,c,d) if op['stage']=='headers' else (op,a,b)
                        bearing=False
                        if header['stage']=='headers' and solid['stage']=='walls':
                            for wall in floor['walls']:
                                axis=0 if abs(wall['start'][1]-wall['end'][1])<tol else 1
                                for opening in wall['openings']:
                                    if header['arguments']['parentId']!=opening['id']:continue
                                    center=wall['start'][axis]+opening['offset_along_wall']+opening['width']/2
                                    joint=(hb[axis]-ha[axis]-opening['width'])/2
                                    left,right=center-opening['width']/2,center+opening['width']/2
                                    outside=sb[axis]<=left+tol or sa[axis]>=right-tol
                                    bearing=(0.15<=joint<=1 and outside and penetration[axis]<=joint+tol
                                        and abs((ha[axis]+hb[axis])/2-center)<tol
                                        and abs((ha[1-axis]+hb[1-axis])/2-wall['start'][1-axis])<tol
                                        and abs(hb[2]-datum-profile['wall_height'])<tol)
                        if bearing:continue
                        errors.append({'code':'STRUCTURAL_WALL_OVERLAP','objects':[op['arguments']['semanticId'],other['arguments']['semanticId']]})
            for wall in floor['walls']:
                key = (tuple(wall['start']), tuple(wall['end']))
                if key in seen:
                    errors.append({'code': 'SHARED_WALL_DUPLICATED', 'wallId': wall['id']})
                seen.add(key)
                horizontal = abs(wall['start'][1]-wall['end'][1]) < 1e-6
                axis, normal = (0, 1) if horizontal else (1, 0)
                start, end = wall['start'][axis], wall['end'][axis]
                fixed = wall['start'][normal]
                covers = []
                for op, a, b in walls:
                    if abs((a[normal]+b[normal])/2-fixed) > tol:
                        continue
                    if min(end,b[axis])-max(start,a[axis]) <= 1e-6:
                        continue
                    try:
                        for lo, hi in wall_solid_bounds(op, self.assets):
                            lo, hi = frame.local(lo), frame.local(hi)
                            covers.append((lo[axis],lo[2]-datum,hi[axis],hi[2]-datum))
                    except ValueError as exc:
                        errors.append({'code':str(exc),'objectId':op['arguments']['semanticId']})
                holes = [(start+h['offset_along_wall'], h['bottom'], start+h['offset_along_wall']+h['width'], h['bottom']+h['height']) for h in wall['openings']]
                gap = uncovered((start, 0, end, profile['ceiling_offset']), covers+holes)
                if gap > tol*(end-start+profile['wall_height']):
                    errors.append({'code': 'WALL_CONTINUITY_GAP', 'wallId': wall['id'], 'area': gap})
                for opening, hole in zip(wall['openings'], holes):
                    doors = [(op,a,b) for op,a,b in physical if op['stage']=='doors' and op['arguments']['parentId']==opening['id']]
                    if len(doors) != 1:
                        errors.append({'code': 'PORTAL_DOOR_MISSING_OR_DUPLICATED', 'portalId': opening['id']}); continue
                    _, a, b = doors[0]
                    if opening['width']+tol < b[axis]-a[axis] or opening['height']+tol < b[2]-a[2]:
                        errors.append({'code': 'OPENING_TOO_SMALL', 'portalId': opening['id']})
                    if abs((a[axis]+b[axis])/2-(hole[0]+hole[2])/2)>tol:
                        errors.append({'code': 'DOOR_NOT_CENTERED_IN_OPENING', 'portalId': opening['id']})
                    if abs((a[normal]+b[normal])/2-fixed)>tol or a[2]<datum+hole[1]-tol or b[2]>datum+hole[3]+tol:
                        errors.append({'code': 'DOOR_FRAME_OUTSIDE_WALL', 'portalId': opening['id']})
                    if len(set(opening['spaces'])) != 2 or set(wall['owners']) != set(s for s in opening['spaces'] if s!='EXTERIOR'):
                        errors.append({'code': 'PORTAL_NOT_CONNECTING_SPACES', 'portalId': opening['id']})
                    door_rect = (a[axis], a[2]-datum, b[axis], b[2]-datum)
                    if any(overlap(door_rect, solid)>1e-5 for solid in covers):
                        errors.append({'code': 'DOOR_INSIDE_SOLID_WALL', 'portalId': opening['id']})
            for op, a, b in walls:
                if op['stage']=='headers':continue
                delta = a[2]-datum
                sid = op['arguments']['semanticId']
                if abs(delta)>tol:
                    errors.append({'code': 'WALL_FLOATING' if delta>0 else 'WALL_SUNK', 'objectId':sid, 'delta':delta})
                    errors.append({'code': 'WALL_FLOOR_GAP' if delta>0 else 'WALL_FLOOR_OVERPENETRATION', 'objectId':sid})
                    if abs(delta)>profile['story_height']/2:
                        errors.append({'code':'WALL_WRONG_LEVEL','objectId':sid})
                if abs(b[2]-(datum+profile['wall_height']))>tol:
                    errors.append({'code':'WALL_TOP_MISMATCH','objectId':sid})
                axis=0 if b[0]-a[0]>b[1]-a[1] else 1
                fixed=(a[1-axis]+b[1-axis])/2
                supported=[]
                for tile,c,d in physical:
                    if tile['stage']=='floors' and tile['floorId']==level['id'] and c[1-axis]-tol<=fixed<=d[1-axis]+tol:
                        supported.append((c[axis],0,d[axis],1))
                if uncovered((a[axis],0,b[axis],1),supported)>tol:
                    errors.append({'code':'WALL_SUPPORT_MISSING','objectId':sid})
                if inset:
                    support_rects=[(c[0],c[1],d[0],d[1]) for tile,c,d in physical
                        if tile['stage']=='floors' and tile['floorId']==level['id']]
                    if uncovered((a[0],a[1],b[0],b[1]),support_rects)>tol*max(b[axis]-a[axis],1):
                        errors.append({'code':'WALL_BEARING_WIDTH_UNSUPPORTED','objectId':sid})
        for v in layout.floors[0].vertical_connections:
            lower = next(f for f in layout.floors if f.id==v.from_floor)
            upper = next(f for f in layout.floors if f.id==v.to_floor)
            errors.extend(validate_stair_connection(v, lower, upper, operations, self.assets, tol))
        return errors
