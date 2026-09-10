"""Coordinate-explicit spatial primitives used by the Phase 3 solver.

The solver is deliberately limited to upright interior placement. Eden rotations are
stored as [pitch, roll, yaw] degrees, and only pitch=roll=0 is accepted for OBB math.
Arma yaw is clockwise from +Y: yaw 0 -> +Y, yaw 90 -> +X.
ATL/ASL conversion is never implicit; callers must supply the vertical offset.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math
from typing import Any, Iterable

Vec3 = tuple[float, float, float]
Vec2 = tuple[float, float]


def vadd(a: Vec3, b: Vec3) -> Vec3: return tuple(x + y for x, y in zip(a, b))  # type: ignore[return-value]
def vsub(a: Vec3, b: Vec3) -> Vec3: return tuple(x - y for x, y in zip(a, b))  # type: ignore[return-value]
def vmul(a: Vec3, k: float) -> Vec3: return tuple(x * k for x in a)  # type: ignore[return-value]
def dot(a: Vec3, b: Vec3) -> float: return sum(x * y for x, y in zip(a, b))
def cross(a: Vec3, b: Vec3) -> Vec3:
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def length(a: Vec3) -> float: return math.sqrt(dot(a, a))
def unit(a: Vec3) -> Vec3:
    n = length(a)
    if n <= 1e-12: raise ValueError("zero-length vector")
    return vmul(a, 1/n)


@dataclass(frozen=True)
class SpatialTransform:
    """One transform with an explicit coordinate space.

    WORLD is an abstract solver frame. EDEN is the Position/rotation representation
    accepted by MapAutomation. ATL and ASL require an explicit conversion offset.
    """
    position: Vec3
    rotation_deg: Vec3 = (0.0, 0.0, 0.0)
    space: str = "WORLD"
    scale: float = 1.0

    def __post_init__(self) -> None:
        if self.space not in {"MODEL", "WORLD", "EDEN", "ATL", "ASL"}:
            raise ValueError(f"unsupported coordinate space: {self.space}")
        if self.scale != 1:
            raise ValueError("Phase 3 supports scale=1 only")
        if any(not math.isfinite(x) for x in (*self.position, *self.rotation_deg)):
            raise ValueError("non-finite transform")

    @property
    def yaw(self) -> float: return self.rotation_deg[2]

    def require_upright(self, tolerance: float = 1e-6) -> None:
        if abs(self.rotation_deg[0]) > tolerance or abs(self.rotation_deg[1]) > tolerance:
            raise ValueError("Phase 3 OBB supports upright pitch/roll only")

    def axes(self) -> tuple[Vec3, Vec3, Vec3]:
        self.require_upright()
        a = math.radians(self.yaw); c, s = math.cos(a), math.sin(a)
        # Clockwise Arma yaw around world +Z.
        return ((c, -s, 0.0), (s, c, 0.0), (0.0, 0.0, 1.0))

    def vector_to_world(self, local: Vec3) -> Vec3:
        axes = self.axes()
        return tuple(sum(local[j] * axes[j][i] for j in range(3)) for i in range(3))  # type: ignore[return-value]

    def point_to_world(self, local: Vec3) -> Vec3:
        return vadd(self.position, self.vector_to_world(local))

    def with_space(self, target: str, *, asl_minus_atl: float | None = None) -> "SpatialTransform":
        if target == self.space: return self
        aliases = {"WORLD", "EDEN"}
        if self.space in aliases and target in aliases:
            return SpatialTransform(self.position, self.rotation_deg, target, self.scale)
        if {self.space, target} == {"ATL", "ASL"}:
            if asl_minus_atl is None: raise ValueError("ATL/ASL conversion requires explicit asl_minus_atl")
            dz = asl_minus_atl if self.space == "ATL" else -asl_minus_atl
            return SpatialTransform((self.position[0], self.position[1], self.position[2]+dz), self.rotation_deg, target, self.scale)
        raise ValueError(f"no implicit conversion from {self.space} to {target}")

    def gateway(self) -> dict[str, Any]:
        t = self.with_space("EDEN")
        return {"position": list(t.position), "rotation": list(t.rotation_deg), "scale": 1}


@dataclass(frozen=True)
class OBB:
    center: Vec3
    half_extents: Vec3
    axes: tuple[Vec3, Vec3, Vec3]
    provenance: str = "approximate"

    @classmethod
    def from_local_bounds(cls, bounds: tuple[Vec3, Vec3], transform: SpatialTransform, provenance: str = "engineMeasured") -> "OBB":
        lo, hi = bounds
        center_local = tuple((a+b)/2 for a, b in zip(lo, hi))  # type: ignore[assignment]
        half = tuple((b-a)/2 for a, b in zip(lo, hi))  # type: ignore[assignment]
        if any(x <= 0 for x in half): raise ValueError("degenerate OBB")
        return cls(transform.point_to_world(center_local), half, transform.axes(), provenance)

    def corners(self) -> list[Vec3]:
        result=[]
        for sx in (-1,1):
            for sy in (-1,1):
                for sz in (-1,1):
                    p=self.center
                    for axis,half,sign in zip(self.axes,self.half_extents,(sx,sy,sz)):
                        p=vadd(p,vmul(axis,half*sign))
                    result.append(p)
        return result

    def footprint(self) -> list[Vec2]:
        points={(round(p[0],9),round(p[1],9)) for p in self.corners()}
        cx=sum(x for x,_ in points)/len(points); cy=sum(y for _,y in points)/len(points)
        return sorted(points,key=lambda p:math.atan2(p[1]-cy,p[0]-cx))

    def intersects(self, other: "OBB", tolerance: float = 0.005) -> bool:
        """Full 3D SAT using face normals and cross products (15 axes maximum)."""
        delta=vsub(other.center,self.center)
        axes=list(self.axes)+list(other.axes)
        axes.extend(cross(a,b) for a in self.axes for b in other.axes)
        for raw in axes:
            if length(raw) <= 1e-9: continue
            axis=unit(raw)
            distance=abs(dot(delta,axis))
            ra=sum(self.half_extents[i]*abs(dot(self.axes[i],axis)) for i in range(3))
            rb=sum(other.half_extents[i]*abs(dot(other.axes[i],axis)) for i in range(3))
            if distance >= ra+rb-tolerance: return False
        return True

    def contains_xy(self, point: Vec2, inflation: float = 0.0) -> bool:
        d=(point[0]-self.center[0],point[1]-self.center[1],0.0)
        return all(abs(dot(d,self.axes[i])) <= self.half_extents[i]+inflation for i in (0,1))


@dataclass(frozen=True)
class ClearanceVolume:
    role: str
    local_center: Vec3
    half_extents: Vec3
    provenance: str = "approximate"
    confidence: float = 0.5

    def world_obb(self, transform: SpatialTransform) -> OBB:
        return OBB(transform.point_to_world(self.local_center),self.half_extents,transform.axes(),self.provenance)


@dataclass(frozen=True)
class AssetProfile:
    classname: str
    bounds: tuple[Vec3, Vec3]
    placement_type: str
    support_local_z: float | None
    support_surface_types: tuple[str, ...]
    support_alignment: str
    semantic_front: Vec3 | None
    semantic_back: Vec3 | None
    clearance: tuple[ClearanceVolume, ...]
    allowed_yaw: tuple[float, ...]
    generator_allowed: bool
    provenance: dict[str, Any]

    def occupied(self, transform: SpatialTransform) -> OBB:
        return OBB.from_local_bounds(self.bounds,transform,"engineMeasured visual AABB; approximate occupied volume")


@dataclass(frozen=True)
class SupportSurface:
    id: str
    type: str
    owner: str
    origin: Vec3
    normal: Vec3
    u_axis: Vec3
    v_axis: Vec3
    half_extents: Vec2
    space: str = "WORLD"
    provenance: str = "engineMeasured+approximate"

    def __post_init__(self) -> None:
        if self.type not in {"floor","wall","ceiling"}: raise ValueError("unsupported support surface type")
        if self.space != "WORLD": raise ValueError("solver SupportSurface must be WORLD")
        for a in (self.normal,self.u_axis,self.v_axis): unit(a)
        if abs(dot(self.normal,self.u_axis))>1e-6 or abs(dot(self.normal,self.v_axis))>1e-6: raise ValueError("surface axes not tangent")

    def coordinates(self, p: Vec3) -> tuple[float,float,float]:
        d=vsub(p,self.origin)
        return dot(d,self.u_axis),dot(d,self.v_axis),dot(d,self.normal)

    def contains_projected(self, points: Iterable[Vec3], tolerance: float) -> bool:
        return all(abs(self.coordinates(p)[0]) <= self.half_extents[0]+tolerance and abs(self.coordinates(p)[1]) <= self.half_extents[1]+tolerance for p in points)


@dataclass(frozen=True)
class ResolvedObject:
    id: str
    asset: AssetProfile
    transform: SpatialTransform
    occupied: OBB
    clearance: tuple[ClearanceVolume, ...] = ()

    @classmethod
    def create(cls, id: str, asset: AssetProfile, transform: SpatialTransform) -> "ResolvedObject":
        return cls(id,asset,transform,asset.occupied(transform),asset.clearance)

    def clearance_obbs(self) -> list[OBB]: return [x.world_obb(self.transform) for x in self.clearance]


@dataclass(frozen=True)
class Diagnostic:
    code: str
    subjects: tuple[str, ...]
    measurements: dict[str, Any]
    provenance: str
    repair_hint: str | None = None

    def json(self) -> dict[str, Any]:
        return {"code":self.code,"subjects":list(self.subjects),"measurements":self.measurements,
            "provenance":self.provenance,"repairHint":self.repair_hint}


@dataclass
class SceneState:
    region_id: str
    region_polygon: list[Vec2]
    surfaces: dict[str,SupportSurface]
    objects: list[ResolvedObject] = field(default_factory=list)
    entrance: Vec2 | None = None
    required_targets: list[Vec2] = field(default_factory=list)

    def fingerprint(self) -> str:
        data={"region":self.region_polygon,"surfaces":sorted(self.surfaces),"objects":[
            [o.id,o.asset.classname,o.transform.position,o.transform.rotation_deg] for o in sorted(self.objects,key=lambda x:x.id)]}
        return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),default=list).encode()).hexdigest()


@dataclass(frozen=True)
class PlacementIntent:
    id: str
    asset: str
    region: str
    on_surface: str
    against_wall: str | None = None
    hard: tuple[str,...] = ("OnSurface","InsideRegion","AvoidIntersection","KeepClearance")
    soft: tuple[str,...] = ()
    reachable: bool = False
    facing_direction: Vec2 | None = None
    seed: int = 0

    @classmethod
    def from_json(cls,value: dict[str,Any]) -> "PlacementIntent":
        required={"id","asset","region","onSurface"}
        if not isinstance(value,dict) or not required <= value.keys(): raise ValueError("invalid PlacementIntent required fields")
        known=required|{"againstWall","hardConstraints","softPreferences","requirements","facingDirection","seed","schemaVersion"}
        if set(value)-known: raise ValueError("unknown PlacementIntent fields: "+str(sorted(set(value)-known)))
        requirements=value.get("requirements",{})
        default_hard=("OnSurface","InsideRegion","AvoidIntersection","KeepClearance")
        return cls(str(value['id']),str(value['asset']),str(value['region']),str(value['onSurface']),
            str(value['againstWall']) if value.get('againstWall') is not None else None,
            tuple(value.get('hardConstraints',default_hard)),tuple(value.get('softPreferences',[])),
            bool(requirements.get('reachable',False)),tuple(value['facingDirection']) if value.get('facingDirection') else None,
            int(value.get('seed',0)))

    def json(self) -> dict[str,Any]:
        return {"schemaVersion":1,"id":self.id,"asset":self.asset,"region":self.region,
            "onSurface":self.on_surface,"againstWall":self.against_wall,"hardConstraints":list(self.hard),
            "softPreferences":list(self.soft),"requirements":{"reachable":self.reachable},
            "facingDirection":list(self.facing_direction) if self.facing_direction else None,"seed":self.seed}
