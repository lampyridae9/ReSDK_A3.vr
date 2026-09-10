"""Deterministic candidate generation, validation, scoring and accessibility.

Hard constraints always filter before scoring. Existing-map priors may only be
represented as soft scores and never bypass a validator.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from .model import (
    AssetProfile, ClearanceVolume, Diagnostic, OBB, PlacementIntent,
    ResolvedObject, SceneState, SpatialTransform, SupportSurface,
    Vec2, Vec3, dot, unit, vadd, vmul, vsub,
)

ROOT=Path(__file__).resolve().parents[3]
CATALOG=ROOT/'Tools/MapAutomation/catalog'
POLICY=ROOT/'Tools/MapAutomation/phase3_assets.json'


def _vec3(v: list[float]) -> Vec3: return (float(v[0]),float(v[1]),float(v[2]))


def load_phase3_assets(policy: Path=POLICY) -> tuple[dict[str,AssetProfile],dict[str,Any]]:
    doc=json.loads(policy.read_text(encoding='utf-8'))
    geometry={x['classname']:x for x in json.loads((CATALOG/'geometry.json').read_text(encoding='utf-8'))['profiles']}
    assets={}
    for row in doc['assets']:
        raw=row;name=raw['classname'];g=geometry[name]
        calibration=raw.get('edenCalibration',{})
        offset_z=float(calibration.get('modelBoundsOffsetZ',0.0))
        bounds=tuple((float(x[0]),float(x[1]),float(x[2])+offset_z) for x in g['visualBounds']['value'])
        if raw.get('geometrySha256') and raw['geometrySha256']!=hashlib.sha256(json.dumps(g['visualBounds']['value'],separators=(',',':')).encode()).hexdigest():
            raise ValueError(name+': curated metadata geometry binding changed')
        clear=tuple(ClearanceVolume(x['role'],(float(x['localCenter'][0]),float(x['localCenter'][1]),float(x['localCenter'][2])+offset_z),
            _vec3(x['halfExtents']),x['provenance'],float(x['confidence'])) for x in raw.get('clearanceVolumes',[]))
        front=_vec3(raw['semanticFront']['value']) if raw['semanticFront']['value'] is not None else None
        back=_vec3(raw['semanticBack']['value']) if raw['semanticBack']['value'] is not None else None
        assets[name]=AssetProfile(name,bounds,raw['placementType'],raw['support']['localPlaneZ'],tuple(raw['support']['surfaceTypes']),
            raw['support'].get('alignment','same'),front,back,clear,tuple(float(x) for x in raw['orientation']['allowedYawDegrees']),
            bool(raw['generatorAllowed']),raw['provenance'])
    return assets,doc


def _point_on_segment(p: Vec2,a: Vec2,b: Vec2,tol: float=1e-8) -> bool:
    cross=(p[0]-a[0])*(b[1]-a[1])-(p[1]-a[1])*(b[0]-a[0])
    return abs(cross)<=tol and min(a[0],b[0])-tol<=p[0]<=max(a[0],b[0])+tol and min(a[1],b[1])-tol<=p[1]<=max(a[1],b[1])+tol


def point_in_polygon(point: Vec2,polygon: list[Vec2],tolerance: float=1e-8) -> bool:
    if len(polygon)<3: return False
    if any(_point_on_segment(point,polygon[i],polygon[(i+1)%len(polygon)],tolerance) for i in range(len(polygon))): return True
    inside=False;x,y=point
    for i,a in enumerate(polygon):
        b=polygon[(i+1)%len(polygon)]
        if (a[1]>y)!=(b[1]>y):
            at_x=(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]
            if x<at_x: inside=not inside
    return inside


def _distance_to_segment(p: Vec2,a: Vec2,b: Vec2) -> float:
    dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy
    if den<=1e-16: return math.dist(p,a)
    t=max(0.0,min(1.0,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den))
    return math.dist(p,(a[0]+t*dx,a[1]+t*dy))


class GeometryValidator:
    def __init__(self,tolerances: dict[str,float]): self.t=tolerances

    def validate(self,candidate: ResolvedObject,scene: SceneState,*,check_region: bool=True,check_intersections: bool=True) -> list[Diagnostic]:
        out=[]
        if check_region:
            outside=[p for p in candidate.occupied.footprint() if not point_in_polygon(p,scene.region_polygon,self.t['region'])]
            if outside:
                out.append(Diagnostic('OUTSIDE_REGION',(candidate.id,scene.region_id),{'outsideCorners':outside},'engineMeasured+approximate','move inside room region'))
        if check_intersections:
            for other in scene.objects:
                if candidate.occupied.intersects(other.occupied,self.t['intersection']):
                    out.append(Diagnostic('INTERSECTION',(candidate.id,other.id),{'tolerance':self.t['intersection']},'engineMeasured+approximate','choose another candidate'))
        return out


class SupportValidator:
    def __init__(self,tolerances: dict[str,float]): self.t=tolerances

    def validate(self,candidate: ResolvedObject,surface: SupportSurface) -> list[Diagnostic]:
        asset=candidate.asset;out=[]
        if surface.type not in asset.support_surface_types or asset.support_local_z is None:
            return [Diagnostic('UNSUPPORTED_PLACEMENT',(candidate.id,surface.id),{'assetPlacementType':asset.placement_type,'surfaceType':surface.type},'approximate','select a compatible SupportSurface')]
        up=candidate.transform.axes()[2]
        expected=surface.normal if asset.support_alignment=='same' else vmul(surface.normal,-1)
        alignment=dot(up,expected)
        if alignment < math.cos(math.radians(self.t['normalDegrees'])):
            out.append(Diagnostic('SUPPORT_ORIENTATION',(candidate.id,surface.id),{'alignmentDot':alignment,'maxDegrees':self.t['normalDegrees']},'approximate','align local up with support rule'))
        lo,hi=asset.bounds;z=asset.support_local_z
        points=[candidate.transform.point_to_world((x,y,z)) for x in (lo[0],hi[0]) for y in (lo[1],hi[1])]
        gaps=[surface.coordinates(p)[2] for p in points]
        gap=max(gaps,key=abs)
        if gap > self.t['supportGap']:
            out.append(Diagnostic('SUPPORT_GAP',(candidate.id,surface.id),{'gap':gap,'tolerance':self.t['supportGap']},'engineMeasured+approximate','lower object to support plane'))
        elif gap < -self.t['penetration']:
            out.append(Diagnostic('SUPPORT_PENETRATION',(candidate.id,surface.id),{'penetration':-gap,'tolerance':self.t['penetration']},'engineMeasured+approximate','raise object to support plane'))
        if not surface.contains_projected(points,self.t['supportBounds']):
            out.append(Diagnostic('OUTSIDE_SUPPORT',(candidate.id,surface.id),{'surfaceHalfExtents':surface.half_extents},'engineMeasured+approximate','move contact footprint inside surface'))
        return out


class ClearanceValidator:
    def __init__(self,tolerances: dict[str,float]): self.t=tolerances

    def validate(self,candidate: ResolvedObject,scene: SceneState) -> list[Diagnostic]:
        out=[];candidate_clear=candidate.clearance_obbs()
        for other in scene.objects:
            roles=[]
            if any(candidate.occupied.intersects(c,self.t['clearance']) for c in other.clearance_obbs()): roles.append('candidate occupied vs existing clearance')
            if any(other.occupied.intersects(c,self.t['clearance']) for c in candidate_clear): roles.append('existing occupied vs candidate clearance')
            if roles:
                out.append(Diagnostic('CLEARANCE_BLOCKED',(candidate.id,other.id),{'relations':roles,'tolerance':self.t['clearance']},'approximate','preserve interaction/door clearance'))
        return out


@dataclass(frozen=True)
class NavigationAgentProfile:
    radius: float
    height: float
    minimum_passage_width: float
    grid_resolution: float
    provenance: str = 'approximate'


class AccessibilityValidator:
    def __init__(self,agent: NavigationAgentProfile): self.agent=agent

    def validate(self,scene: SceneState,target: Vec2,subject: str) -> tuple[list[Diagnostic],list[Vec2]]:
        if scene.entrance is None:
            return [Diagnostic('ACCESSIBILITY_INPUT_MISSING',(subject,),{'missing':'entrance'},'unknown','provide room entrance')],[]
        xs=[p[0] for p in scene.region_polygon];ys=[p[1] for p in scene.region_polygon];r=self.agent.grid_resolution
        nx=math.floor((max(xs)-min(xs))/r)+1;ny=math.floor((max(ys)-min(ys))/r)+1
        origin=(min(xs),min(ys));inflation=max(self.agent.radius,self.agent.minimum_passage_width/2)
        floor_z=min((s.origin[2] for s in scene.surfaces.values() if s.type=='floor'),default=0.0)
        def point(cell: tuple[int,int]) -> Vec2: return (origin[0]+cell[0]*r,origin[1]+cell[1]*r)
        def nearest(p: Vec2) -> tuple[int,int]: return (round((p[0]-origin[0])/r),round((p[1]-origin[1])/r))
        def blocked(cell: tuple[int,int]) -> bool:
            p=point(cell)
            if not point_in_polygon(p,scene.region_polygon): return True
            if min(_distance_to_segment(p,scene.region_polygon[i],scene.region_polygon[(i+1)%len(scene.region_polygon)]) for i in range(len(scene.region_polygon))) < self.agent.radius: return True
            def relevant(o):
                low=o.occupied.center[2]-o.occupied.half_extents[2];high=o.occupied.center[2]+o.occupied.half_extents[2]
                return high>floor_z+.02 and low<floor_z+self.agent.height
            return any(relevant(o) and o.occupied.contains_xy(p,inflation) for o in scene.objects)
        start=nearest(scene.entrance);goal=nearest(target)
        if blocked(start) or blocked(goal):
            return [Diagnostic('UNREACHABLE',(subject,),{'reason':'start_or_goal_blocked','gridResolution':r,'inflation':inflation},'approximate','move entrance/interaction point out of occupied footprint')],[]
        q=deque([start]);prev={start:None};found=False
        while q:
            cur=q.popleft()
            if cur==goal: found=True;break
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nxt=(cur[0]+dx,cur[1]+dy)
                if 0<=nxt[0]<nx and 0<=nxt[1]<ny and nxt not in prev and not blocked(nxt): prev[nxt]=cur;q.append(nxt)
        if not found:
            return [Diagnostic('UNREACHABLE',(subject,),{'gridResolution':r,'inflation':inflation,'visitedCells':len(prev)},'approximate','restore a continuous local passage')],[]
        cells=[];cur=goal
        while cur is not None: cells.append(point(cur));cur=prev[cur]
        cells.reverse();return [],cells


@dataclass
class SolverResult:
    status: str
    intent: PlacementIntent
    placement: ResolvedObject | None
    diagnostics: list[Diagnostic]
    rejected: list[dict[str,Any]]
    score: float | None
    path: list[Vec2]
    dry_run: bool
    scene_patch: dict[str,Any] | None

    def json(self) -> dict[str,Any]:
        placement=None
        if self.placement:
            placement={'id':self.placement.id,'asset':self.placement.asset.classname,
                'transform':self.placement.transform.gateway(),'occupiedCorners':self.placement.occupied.corners(),
                'clearance':[{'role':v.role,'corners':v.world_obb(self.placement.transform).corners()} for v in self.placement.clearance]}
        return {'status':self.status,'intent':self.intent.json(),'placement':placement,
            'diagnostics':[d.json() for d in self.diagnostics],'rejectedCandidates':self.rejected,
            'score':self.score,'navigationPath':self.path,'dryRun':self.dry_run,'scenePatch':self.scene_patch}


@dataclass
class CandidateBatch:
    """Ranked, already hard-validated alternatives for one placement intent."""
    intent: PlacementIntent
    candidates: list[SolverResult]
    rejected: list[dict[str,Any]]
    generated: int

    def json(self) -> dict[str,Any]:
        return {'intent':self.intent.json(),'generated':self.generated,'valid':len(self.candidates),
            'candidates':[x.json() for x in self.candidates],'rejectedCandidates':self.rejected}


class PlacementSolver:
    HARD={'OnSurface','AgainstWall','InsideRegion','AvoidIntersection','KeepClearance','Reachable','FacingDirection'}
    SOFT={'PreferWallCenter','Compact','MaximizeCirculation'}

    def __init__(self,assets: dict[str,AssetProfile],config: dict[str,Any],*,allow_candidate_assets: bool=False):
        self.assets=assets;self.config=config;self.allow_candidate_assets=allow_candidate_assets
        self.t=config['tolerances'];nav=config['navigationAgent']
        self.geometry=GeometryValidator(self.t);self.support=SupportValidator(self.t);self.clearance=ClearanceValidator(self.t)
        self.access=AccessibilityValidator(NavigationAgentProfile(nav['radius'],nav['height'],nav['minimumPassageWidth'],nav['gridResolution'],nav['provenance']))

    def _heading(self,v: Vec2) -> float: return math.degrees(math.atan2(v[0],v[1]))%360

    def _yaw_for_front(self,front: Vec3,target: Vec3) -> float:
        return (self._heading((target[0],target[1]))-self._heading((front[0],front[1])))%360

    def _surface_transform(self,asset: AssetProfile,surface: SupportSurface,u: float,v: float,yaw: float) -> SpatialTransform:
        if asset.support_local_z is None: raise ValueError('asset has no support plane')
        base=vadd(surface.origin,vadd(vmul(surface.u_axis,u),vmul(surface.v_axis,v)))
        # All MVP floor/ceiling surfaces are horizontal. No implicit arbitrary-plane Euler conversion.
        if abs(abs(surface.normal[2])-1)>1e-6: raise ValueError('OnSurface MVP supports horizontal floor/ceiling only')
        z=surface.origin[2]-asset.support_local_z
        return SpatialTransform((base[0],base[1],z),(0,0,yaw),'WORLD')

    def _grid_candidates(self,intent: PlacementIntent,asset: AssetProfile,surface: SupportSurface) -> list[SpatialTransform]:
        step=self.t['candidateStep'];values=[]
        for axis in range(2):
            half=surface.half_extents[axis];n=math.floor(2*half/step)
            vals=[-half+i*step for i in range(n+1)]+[half]
            values.append(sorted(set(round(x,6) for x in vals),key=lambda x:(abs(x),x)))
        yaws=asset.allowed_yaw
        if intent.facing_direction and asset.semantic_front:
            yaws=(self._yaw_for_front(asset.semantic_front,(intent.facing_direction[0],intent.facing_direction[1],0)),)
        return [self._surface_transform(asset,surface,u,v,yaw) for yaw in yaws for u in values[0] for v in values[1]]

    def _wall_candidates(self,intent: PlacementIntent,asset: AssetProfile,floor: SupportSurface,wall: SupportSurface) -> list[SpatialTransform]:
        if not asset.semantic_front: raise ValueError('AgainstWall requires semanticFront')
        yaw=self._yaw_for_front(asset.semantic_front,wall.normal)
        base=self._surface_transform(asset,floor,0,0,yaw)
        relative=asset.occupied(SpatialTransform((0,0,0),(0,0,yaw),'WORLD'))
        projections=[dot(c,wall.normal) for c in relative.corners()]
        along=[dot(c,wall.u_axis) for c in relative.corners()]
        inward=self.t['wallGap']-min(projections)
        margin=max(abs(min(along)),abs(max(along)))+self.t['wallEndMargin']
        lo=-wall.half_extents[0]+margin;hi=wall.half_extents[0]-margin
        if lo>hi: return []
        step=self.t['candidateStep'];n=math.floor((hi-lo)/step)
        values=sorted(set([round(lo+i*step,6) for i in range(n+1)]+[round(hi,6),0.0]),key=lambda x:(abs(x),x))
        result=[]
        for u in values:
            anchor=vadd(wall.origin,vadd(vmul(wall.u_axis,u),vmul(wall.normal,inward)))
            result.append(SpatialTransform((anchor[0],anchor[1],base.position[2]),(0,0,yaw),'WORLD'))
        return result

    def _interaction_target(self,obj: ResolvedObject) -> Vec2:
        preferred=next((v for v in obj.clearance if v.role in {'usable','approach','open'}),None)
        p=obj.transform.point_to_world(preferred.local_center if preferred else (0,0,0))
        return p[0],p[1]

    def _score(self,obj: ResolvedObject,intent: PlacementIntent,scene: SceneState,index: int) -> float:
        score=0.0
        if 'PreferWallCenter' in intent.soft and intent.against_wall:
            u,_,_=scene.surfaces[intent.against_wall].coordinates(obj.transform.position);score-=abs(u)
        if 'Compact' in intent.soft and scene.objects:
            score-=min(math.dist(obj.transform.position[:2],x.transform.position[:2]) for x in scene.objects)*0.05
        if intent.preferred_near:
            target=next((x for x in scene.objects if x.id==intent.preferred_near),None)
            if target is not None: score-=math.dist(obj.transform.position[:2],target.transform.position[:2])
        if 'MaximizeCirculation' in intent.soft and scene.objects:
            score+=min(math.dist(obj.transform.position[:2],x.transform.position[:2]) for x in scene.objects)*0.02
        # Seed is used only as a deterministic final tie breaker.
        intent_token=json.dumps(intent.json(),sort_keys=True,separators=(',',':'))
        token=f'{scene.fingerprint()}|{self.config["catalogVersion"]}|{intent_token}|{index}'.encode()
        score+=int.from_bytes(hashlib.sha256(token).digest()[:4],'big')/2**32*1e-9
        return score

    def resolve_candidates(self,intent: PlacementIntent,scene: SceneState,*,limit: int=5,dry_run: bool=True) -> CandidateBatch:
        """Return up to ``limit`` ranked valid candidates without mutating ``scene``.

        This is the bounded-search API used by higher-level generators.  ``resolve``
        remains the stable best-candidate API and delegates to this method.
        """
        if limit < 1: raise ValueError('candidate limit must be positive')
        if intent.region!=scene.region_id: raise ValueError('PlacementIntent region not present')
        if intent.asset not in self.assets: raise ValueError('asset outside Phase 3 curated subset')
        asset=self.assets[intent.asset]
        if not asset.generator_allowed and not self.allow_candidate_assets: raise ValueError('asset is not generatorAllowed')
        if intent.on_surface not in scene.surfaces: raise ValueError('OnSurface target missing')
        unknown=set(intent.hard)-self.HARD
        if unknown: raise ValueError('unknown hard constraints: '+str(sorted(unknown)))
        unknown=set(intent.soft)-self.SOFT
        if unknown: raise ValueError('unknown soft preferences: '+str(sorted(unknown)))
        if intent.preferred_near and intent.preferred_near not in {x.id for x in scene.objects}:
            raise ValueError('preferredNear target missing')
        if 'AgainstWall' in intent.hard and not intent.against_wall: raise ValueError('AgainstWall constraint requires againstWall')
        if ('FacingDirection' in intent.hard or intent.facing_direction is not None) and (intent.facing_direction is None or asset.semantic_front is None):
            raise ValueError('FacingDirection requires a direction and curated semanticFront')
        surface=scene.surfaces[intent.on_surface]
        if intent.against_wall:
            wall=scene.surfaces.get(intent.against_wall)
            if not wall or wall.type!='wall': raise ValueError('AgainstWall target missing/not wall')
            transforms=self._wall_candidates(intent,asset,surface,wall)
        else: transforms=self._grid_candidates(intent,asset,surface)
        rejected=[];valid=[]
        for index,t in enumerate(transforms):
            obj=ResolvedObject.create(intent.id,asset,t);diags=[]
            if 'OnSurface' in intent.hard: diags+=self.support.validate(obj,surface)
            if 'InsideRegion' in intent.hard or 'AvoidIntersection' in intent.hard:
                diags+=self.geometry.validate(obj,scene,check_region='InsideRegion' in intent.hard,check_intersections='AvoidIntersection' in intent.hard)
            if 'KeepClearance' in intent.hard: diags+=self.clearance.validate(obj,scene)
            path=[]
            if intent.reachable or 'Reachable' in intent.hard:
                temp=SceneState(scene.region_id,scene.region_polygon,scene.surfaces,scene.objects+[obj],scene.entrance,scene.required_targets)
                di,path=self.access.validate(temp,self._interaction_target(obj),obj.id);diags+=di
            if diags:
                rejected.append({'index':index,'transform':t.gateway(),'diagnostics':[d.json() for d in diags]})
            else: valid.append((self._score(obj,intent,scene,index),index,obj,path))
        ranked=sorted(valid,key=lambda row:(-row[0],row[1]))[:limit]
        candidates=[]
        for score,index,obj,path in ranked:
            patch={'operations':[{'operation':'create','arguments':{'semanticId':obj.id,'class':obj.asset.classname,
                **obj.transform.gateway(),'parentId':''}}]}
            candidates.append(SolverResult('VALID',intent,obj,[],[],score,path,dry_run,patch))
        return CandidateBatch(intent,candidates,rejected,len(transforms))

    def resolve(self,intent: PlacementIntent,scene: SceneState,*,dry_run: bool=True) -> SolverResult:
        batch=self.resolve_candidates(intent,scene,limit=1,dry_run=dry_run)
        if batch.candidates:
            result=batch.candidates[0]
            result.rejected=batch.rejected
            return result
        diagnostic=Diagnostic('NO_VALID_CANDIDATE',(intent.id,),{'generated':batch.generated,'rejected':len(batch.rejected)},'ruleDerived','relax soft intent or change hard spatial inputs')
        return SolverResult('FAIL',intent,None,[diagnostic],batch.rejected,None,[],dry_run,None)
