"""Deterministic bounded rectangular subdivision for the Phase 8 dormitory MVP."""
from __future__ import annotations

import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import time
from typing import Any

from .model import (BuildingFootprint,BuildingGraph,BuildingLayout,BuildingOptions,BuildingPlan,FloorPlan,
    PortalPlan,Rect,SpacePlan,VerticalConnectionPlan,WallSegment)

ROOT=Path(__file__).resolve().parents[3]
PROFILE_PATH=ROOT/"Tools/MapAutomation/building_profile.json"


def load_profile()->dict[str,Any]:return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def expand_building_plan(brief:dict[str,Any],profile:dict[str,Any]|None=None)->BuildingPlan:
    profile=profile or load_profile();graph=BuildingGraph();building_id="building_001"
    graph.add_node(building_id,"building",buildingType=brief["buildingType"])
    floors=brief["floors"];bedrooms=brief["requirements"]["bedrooms"];residents=brief["capacity"]["residents"]
    per_floor=[bedrooms//floors+(1 if i<bedrooms%floors else 0) for i in range(floors)]
    capacities=[residents//bedrooms+(1 if i<residents%bedrooms else 0) for i in range(bedrooms)]
    slots=[];cursor=0
    for floor_index,count in enumerate(per_floor):
        floor_id=f"floor_{floor_index+1:03d}";corridor_id=f"corridor_{floor_index+1:03d}"
        graph.add_node(floor_id,"floor",index=floor_index);graph.add_edge(building_id,floor_id,"contains")
        graph.add_node(corridor_id,"corridor",floorId=floor_id);graph.add_edge(floor_id,corridor_id,"contains")
        for _ in range(count):
            room_id=f"bedroom_{cursor+1:03d}";slot={"id":room_id,"type":"bedroom","floorId":floor_id,
                "required":True,"capacity":capacities[cursor],"roomBrief":{
                    "schemaVersion":1,"intent":"create_room","roomType":"bedroom","style":brief["style"],
                    "capacity":{"people":capacities[cursor]},"requirements":{"sleeping":capacities[cursor],"storage":1,"lighting":1},
                    "preferences":{"workSurface":True,"seating":True,"compact":brief["preferences"]["compact"]},
                    "seed":brief["seed"]+cursor+1}}
            slots.append(slot);graph.add_node(room_id,"room",floorId=floor_id,required=True,capacity=capacities[cursor])
            graph.add_edge(floor_id,room_id,"contains");cursor+=1
    if brief["requirements"]["storage"]:
        slot={"id":"storage_001","type":"storage_room","floorId":"floor_001","required":True,"capacity":0,"roomBrief":None}
        slots.append(slot);graph.add_node("storage_001","room",floorId="floor_001",required=True,roomType="storage_room")
        graph.add_edge("floor_001","storage_001","contains")
    return BuildingPlan(building_id,brief["buildingType"],tuple(brief["style"]),brief["seed"],profile["storeyHeight"],slots,graph,
        {"buildingPlanner":"building-planner-v1","buildingProfile":profile["id"],"layoutSolver":"building-layout-v1"})


def _space_at(spaces:list[SpacePlan],x:float,y:float)->str|None:
    for space in spaces:
        r=space.rect
        if r.x+1e-6<x<r.x2-1e-6 and r.y+1e-6<y<r.y2-1e-6:return space.id
    return None


def _walls(floor_id:str,spaces:list[SpacePlan])->list[WallSegment]:
    xs=sorted({v for s in spaces for v in (s.rect.x,s.rect.x2)});ys=sorted({v for s in spaces for v in (s.rect.y,s.rect.y2)})
    raw=[];eps=1e-4
    for y in ys:
        for x1,x2 in zip(xs,xs[1:]):
            mid=(x1+x2)/2;owners=tuple(sorted(x for x in (_space_at(spaces,mid,y-eps),_space_at(spaces,mid,y+eps)) if x))
            if owners and len(set(owners))==len(owners):raw.append(((x1,y),(x2,y),owners,len(owners)==1))
    for x in xs:
        for y1,y2 in zip(ys,ys[1:]):
            mid=(y1+y2)/2;owners=tuple(sorted(v for v in (_space_at(spaces,x-eps,mid),_space_at(spaces,x+eps,mid)) if v))
            if owners and len(set(owners))==len(owners):raw.append(((x,y1),(x,y2),owners,len(owners)==1))
    raw.sort(key=lambda r:(r[0],r[1],r[2]))
    return [WallSegment(f"{floor_id}.wall_{i:03d}",floor_id,a,b,owners,exterior) for i,(a,b,owners,exterior) in enumerate(raw,1)]


def _wall_for(walls:list[WallSegment],a:str,b:str,center:tuple[float,float],exterior:bool=False)->WallSegment:
    wanted={a} if exterior else {a,b}
    for wall in walls:
        if set(wall.owners)!=wanted or wall.exterior!=exterior:continue
        x,y=center
        if abs(wall.start[0]-wall.end[0])<1e-6 and abs(x-wall.start[0])<1e-6 and min(wall.start[1],wall.end[1])-1e-6<=y<=max(wall.start[1],wall.end[1])+1e-6:return wall
        if abs(wall.start[1]-wall.end[1])<1e-6 and abs(y-wall.start[1])<1e-6 and min(wall.start[0],wall.end[0])-1e-6<=x<=max(wall.start[0],wall.end[0])+1e-6:return wall
    raise ValueError(f"PORTAL_INVALID: no wall for {a}->{b} at {center}")


class BuildingLayoutSolver:
    def __init__(self,profile:dict[str,Any]|None=None):self.profile=profile or load_profile()

    def solve(self,plan:BuildingPlan,footprint:BuildingFootprint,brief:dict[str,Any],options:BuildingOptions)->BuildingLayout:
        started=time.perf_counter();diagnostics=[]
        if brief["floors"]>footprint.max_floors:
            return BuildingLayout(plan.id,footprint,[],copy.deepcopy(plan.graph),{},"INFEASIBLE",[{"code":"FLOOR_COUNT_EXCEEDS_FOOTPRINT"}])
        variants=[]
        digest=int.from_bytes(hashlib.sha256(f'{plan.seed}|{footprint.width}|{footprint.depth}'.encode()).digest()[:4],"big")
        axes=["Y","X"] if digest%2==0 else ["X","Y"]
        if self.profile.get('layoutMode')=='one-sided-native-grid':
            axes=['Y']
        for axis in axes:
            for mirror in ((digest//2)%2==0,(digest//2)%2!=0):variants.append((axis,mirror))
        limit=min(options.max_layout_candidates,options.max_partition_attempts,len(variants));last=[]
        for attempt,(axis,mirror) in enumerate(variants[:limit],1):
            if (time.perf_counter()-started)*1000>options.time_budget_ms:
                diagnostics.append({"code":"LAYOUT_SEARCH_BUDGET_EXHAUSTED"});break
            try:
                floors,graph=self._candidate(plan,footprint,brief,axis,mirror)
                hard=self._hard_validate(floors,footprint)
                if hard and any(not x["required"] for x in plan.room_slots):
                    reduced=copy.deepcopy(plan);dropped={x["id"] for x in reduced.room_slots if not x["required"]}
                    reduced.room_slots=[x for x in reduced.room_slots if x["required"]]
                    reduced.graph.nodes=[x for x in reduced.graph.nodes if x["id"] not in dropped]
                    reduced.graph.edges=[x for x in reduced.graph.edges if x["source"] not in dropped and x["target"] not in dropped]
                    floors,graph=self._candidate(reduced,footprint,brief,axis,mirror);hard=self._hard_validate(floors,footprint)
                    if not hard:diagnostics.append({"code":"OPTIONAL_ROOM_DROPPED","roomIds":sorted(dropped),"reason":"minimum geometry"})
                if not hard:
                    area=sum(s.rect.area for f in floors for s in f.spaces if s.kind=="bedroom")
                    preferred=sum(self.profile["roomTypes"]["bedroom"]["preferredArea"] for _ in plan.room_slots)
                    feasibility="TIGHT" if area<preferred else "FEASIBLE"
                    return BuildingLayout(plan.id,footprint,floors,graph,{"attempt":attempt,"axis":axis,"mirrored":mirror,
                        "attemptsUsed":attempt,"maxLayoutCandidates":options.max_layout_candidates,
                        "maxPartitionAttempts":options.max_partition_attempts},feasibility,diagnostics)
                last=hard
            except ValueError as exc:last=[{"code":"PORTAL_INVALID","message":str(exc)}]
        return BuildingLayout(plan.id,footprint,[],copy.deepcopy(plan.graph),{"attemptsUsed":min(limit,len(variants)),
            "maxLayoutCandidates":options.max_layout_candidates,"maxPartitionAttempts":options.max_partition_attempts},"INFEASIBLE",diagnostics+last)

    def _candidate(self,plan:BuildingPlan,fp:BuildingFootprint,brief:dict[str,Any],axis:str,mirror:bool)->tuple[list[FloorPlan],BuildingGraph]:
        x0=fp.origin[0]-fp.width/2;y0=fp.origin[1]-fp.depth/2;base=Rect(x0,y0,fp.width,fp.depth)
        corridor_width=self.profile["corridorWidth"];portal_width=self.profile["portalWidth"];door=self.profile["structure"]["doorAsset"]
        graph=copy.deepcopy(plan.graph);floors=[];portal_counter=0
        graph.add_node("entrance_001","entrance");graph.add_edge(plan.id,"entrance_001","contains")
        for floor_index in range(brief["floors"]):
            floor_id=f"floor_{floor_index+1:03d}";corridor_id=f"corridor_{floor_index+1:03d}"
            slots=[x for x in plan.room_slots if x["floorId"]==floor_id]
            one_sided=self.profile.get('layoutMode')=='one-sided-native-grid'
            if axis=="Y":corridor=Rect(x0+(fp.width-corridor_width)/(1 if one_sided else 2),y0,corridor_width,fp.depth)
            else:corridor=Rect(x0,y0+(fp.depth-corridor_width)/2,fp.width,corridor_width)
            spaces=[SpacePlan(corridor_id,"corridor",floor_id,True,0,corridor)]
            # Alternate slots across the corridor.  This keeps required bedroom
            # doors near the entrance end when an optional room subdivides one
            # side, leaving the far end available for the stair core.
            groups=[slots,[]] if one_sided else [slots[::2],slots[1::2]]
            if mirror and not one_sided:groups.reverse()
            for side,group in enumerate(groups):
                if not group:continue
                for pos,slot in enumerate(group):
                    if axis=="Y":
                        width=(fp.width-corridor_width)/(1 if one_sided else 2);depth=fp.depth/len(group)
                        rect=Rect(x0 if side==0 else corridor.x2,y0+pos*depth,width,depth)
                    else:
                        width=fp.width/len(group);depth=(fp.depth-corridor_width)/2
                        rect=Rect(x0+pos*width,y0 if side==0 else corridor.y2,width,depth)
                    spaces.append(SpacePlan(slot["id"],slot["type"],floor_id,slot["required"],slot["capacity"],rect))
            walls=_walls(floor_id,spaces);portals=[]
            stair_depth=self.profile["structure"]["stairFootprint"][1] if brief["floors"]>1 else 0
            landing_depth=self.profile["structure"].get("stairLandingDepth",0) if brief["floors"]>1 else 0
            longitudinal=fp.depth if axis=="Y" else fp.width
            # Keep bedroom doors in a clean service bay before the stair landing.
            # The old midpoint formula pushed openings against the wall end, which
            # left sub-metre fragments that no real wall module could fill.
            free_length=longitudinal-stair_depth-landing_depth if brief["floors"]>1 else longitudinal
            free_center=min(2.25,free_length-portal_width/2-.02)
            free_center=max(portal_width/2+.02,free_center)
            for room in [s for s in spaces if s.kind in {"bedroom","storage_room"}]:
                if axis=="Y":
                    along=room.rect.y+self.profile['portalModuleOffset'] if one_sided else min(max(y0+free_center,room.rect.y+portal_width/2+.1),room.rect.y2-portal_width/2-.1)
                    center=(corridor.x if room.rect.x<corridor.x else corridor.x2,along)
                else:
                    along=min(max(x0+free_center,room.rect.x+portal_width/2+.1),room.rect.x2-portal_width/2-.1)
                    center=(along,corridor.y if room.rect.y<corridor.y else corridor.y2)
                wall=_wall_for(walls,room.id,corridor_id,center);portal_counter+=1
                portal=PortalPlan(f"portal_{portal_counter:03d}",floor_id,corridor_id,room.id,wall.id,center,portal_width,door)
                portals.append(portal);graph.add_node(portal.id,"portal",floorId=floor_id);graph.add_edge(floor_id,portal.id,"contains")
                graph.add_edge(corridor_id,room.id,"connectedByDoor",portalId=portal.id);graph.add_edge(room.id,corridor_id,"accessibleFrom",portalId=portal.id)
            if floor_index==0:
                center=(corridor.center[0],y0) if axis=="Y" else (x0,corridor.center[1])
                if one_sided:center=(corridor.x+self.profile['portalModuleOffset'],y0)
                wall=_wall_for(walls,corridor_id,"EXTERIOR",center,True);portal_counter+=1
                entrance=PortalPlan(f"portal_{portal_counter:03d}",floor_id,"EXTERIOR",corridor_id,wall.id,center,portal_width,door,True)
                portals.append(entrance);graph.add_node(entrance.id,"portal",floorId=floor_id,role="entrance")
                graph.add_edge("EXTERIOR",corridor_id,"connectedByDoor",portalId=entrance.id);graph.add_edge("entrance_001",entrance.id,"contains")
            floors.append(FloorPlan(floor_id,floor_index,fp.origin[2]+floor_index*plan.storey_height,base,spaces,walls,portals))
        if len(floors)>1:
            c=floors[0].spaces[0].rect;structure=self.profile["structure"]
            sw,sd=structure["stairFootprint"];ld=structure.get("stairLandingDepth",self.profile["portalApproachDepth"])
            if axis=="Y":
                occupied=Rect(c.center[0]-sw/2,c.y2-sd,sw,sd)
                landing=Rect(c.center[0]-sw/2,occupied.y-ld,sw,ld);yaw=0
            else:
                occupied=Rect(c.x2-sd,c.center[1]-sw/2,sd,sw)
                landing=Rect(occupied.x-ld,c.center[1]-sw/2,ld,sw);yaw=90
            vertical=VerticalConnectionPlan("stairs_001","stairs",floors[0].id,floors[1].id,occupied,landing,landing,
                structure["stairAsset"],self.profile["portalApproachDepth"],yaw,
                structure.get("stairModelOriginZOffset",0),structure.get("stairVerification","APPROXIMATE"))
            if structure.get('stairCoreLocal'):
                cx,cy=structure['stairCoreLocal'];cx+=fp.origin[0];cy+=fp.origin[1]
                occupied=Rect(cx-sw/2,cy-sd/2,sw,sd)
                ow,od=structure['stairOpeningSize']
                vertical=VerticalConnectionPlan('stairs_001','stairs',floors[0].id,floors[1].id,
                    occupied,Rect(cx-1.5,cy-1.8,1,.9),Rect(cx-1,cy-3.5,2,2),
                    structure['stairAsset'],self.profile['portalApproachDepth'],0,
                    structure.get('stairModelOriginZOffset',0),structure['stairVerification'],
                    Rect(cx-ow/2,cy-od/2,ow,od))
            floors[0].vertical_connections.append(vertical);floors[1].vertical_connections.append(vertical)
            graph.add_node(vertical.id,"vertical_connection",verification=vertical.verification)
            graph.add_edge(floors[0].spaces[0].id,floors[1].spaces[0].id,"verticalConnection",connectionId=vertical.id)
        inset=self.profile.get('exteriorWallInset',0)
        if inset:
            for floor in floors:
                shifts={}
                for i,wall in enumerate(floor.walls):
                    if not wall.exterior:continue
                    horizontal=abs(wall.start[1]-wall.end[1])<1e-6
                    axis=1 if horizontal else 0
                    center=fp.origin[axis]
                    delta=inset if wall.start[axis]<center else -inset
                    start=list(wall.start);end=list(wall.end);start[axis]+=delta;end[axis]+=delta
                    floor.walls[i]=replace(wall,start=tuple(start),end=tuple(end));shifts[wall.id]=(axis,delta)
                for i,portal in enumerate(floor.portals):
                    if portal.wall_segment in shifts:
                        axis,delta=shifts[portal.wall_segment];center=list(portal.center);center[axis]+=delta
                        floor.portals[i]=replace(portal,center=tuple(center))
        return floors,graph

    def _hard_validate(self,floors:list[FloorPlan],fp:BuildingFootprint)->list[dict[str,Any]]:
        result=[];corridor=self.profile["corridorWidth"]
        outer=Rect(fp.origin[0]-fp.width/2,fp.origin[1]-fp.depth/2,fp.width,fp.depth)
        for floor in floors:
            for space in floor.spaces:
                r=space.rect
                if r.x<outer.x-1e-6 or r.y<outer.y-1e-6 or r.x2>outer.x2+1e-6 or r.y2>outer.y2+1e-6:
                    result.append({"code":"ROOM_OUTSIDE_FOOTPRINT","spaceId":space.id})
                spec=self.profile["roomTypes"].get(space.kind)
                if spec and (r.width<spec["minWidth"] or r.depth<spec["minDepth"] or r.area<spec["minimumArea"]):
                    result.append({"code":"ROOM_MINIMUM_DIMENSIONS","spaceId":space.id,"rect":r.json()})
                if space.kind=="corridor" and min(r.width,r.depth)<corridor-1e-6:
                    result.append({"code":"CORRIDOR_TOO_NARROW","spaceId":space.id})
            rooms=floor.spaces
            for i,a in enumerate(rooms):
                for b in rooms[i+1:]:
                    overlap=max(0,min(a.rect.x2,b.rect.x2)-max(a.rect.x,b.rect.x))*max(0,min(a.rect.y2,b.rect.y2)-max(a.rect.y,b.rect.y))
                    if overlap>1e-6:result.append({"code":"ROOM_OVERLAP","spaces":[a.id,b.id],"area":overlap})
            for portal in floor.portals:
                wall=next((w for w in floor.walls if w.id==portal.wall_segment),None)
                if not wall or portal.width>wall.length-0.2:result.append({"code":"PORTAL_INVALID","portalId":portal.id})
                if wall:
                    depth=self.profile["portalApproachDepth"];horizontal=abs(wall.start[1]-wall.end[1])<1e-6
                    owner_rects=[s.rect for s in floor.spaces if s.id in wall.owners]
                    for owner in owner_rects:
                        cx,cy=portal.center
                        candidates=((cx,cy-depth),(cx,cy+depth)) if horizontal else ((cx-depth,cy),(cx+depth,cy))
                        if not any(owner.contains(px,py,-1e-5) for px,py in candidates):
                            result.append({"code":"PORTAL_INVALID","portalId":portal.id,"reason":"approach clearance outside space"})
            for vertical in floor.vertical_connections:
                corridor_space=floor.spaces[0].rect;region=vertical.entry_region_lower if vertical.from_floor==floor.id else vertical.entry_region_upper
                if not corridor_space.contains(vertical.occupied_region.x,vertical.occupied_region.y) or not corridor_space.contains(vertical.occupied_region.x2,vertical.occupied_region.y2):
                    result.append({"code":"VERTICAL_CONNECTION_INVALID","connectionId":vertical.id,"reason":"stair footprint outside corridor"})
                if not corridor_space.contains(region.x,region.y) or not corridor_space.contains(region.x2,region.y2):
                    result.append({"code":"VERTICAL_CONNECTION_INVALID","connectionId":vertical.id,"reason":"landing outside corridor"})
                for portal in floor.portals:
                    if vertical.occupied_region.contains(*portal.center):
                        result.append({"code":"VERTICAL_CONNECTION_INVALID","connectionId":vertical.id,"reason":"stair footprint blocks portal","portalId":portal.id})
        return result
