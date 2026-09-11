"""Deterministic building-level validators and informational object budget."""
from __future__ import annotations

from collections import defaultdict,deque
from typing import Any

from .model import BuildingLayout,BuildingPlan


class BuildingAccessibilityValidator:
    def validate(self,layout:BuildingLayout,plan:BuildingPlan)->list[dict[str,Any]]:
        diagnostics=[];adj:dict[str,set[str]]=defaultdict(set);physical=set()
        for floor in layout.floors:
            spaces={x.id for x in floor.spaces}
            walls={x.id:x for x in floor.walls}
            for portal in floor.portals:
                wall=walls.get(portal.wall_segment)
                expected={portal.to_space} if portal.exterior else {portal.from_space,portal.to_space}
                if not wall or set(wall.owners)!=expected:
                    diagnostics.append({"code":"PORTAL_INVALID","portalId":portal.id,"details":{"expectedOwners":sorted(expected)}});continue
                a,b=portal.from_space,portal.to_space;adj[a].add(b);adj[b].add(a);physical.add(portal.id)
            for vertical in floor.vertical_connections:
                if vertical.from_floor==floor.id:
                    lower=next((f for f in layout.floors if f.id==vertical.from_floor),None)
                    upper=next((f for f in layout.floors if f.id==vertical.to_floor),None)
                    if not lower or not upper:diagnostics.append({"code":"VERTICAL_CONNECTION_INVALID","connectionId":vertical.id});continue
                    adj[lower.spaces[0].id].add(upper.spaces[0].id);adj[upper.spaces[0].id].add(lower.spaces[0].id)
        queue=deque(["EXTERIOR"]);seen={"EXTERIOR"}
        while queue:
            current=queue.popleft()
            for target in adj[current]:
                if target not in seen:seen.add(target);queue.append(target)
        for slot in plan.room_slots:
            if slot["required"] and slot["id"] not in seen:diagnostics.append({"code":"ROOM_DISCONNECTED","roomId":slot["id"]})
        for floor in layout.floors:
            if floor.index>0 and floor.spaces[0].id not in seen:diagnostics.append({"code":"FLOOR_DISCONNECTED","floorId":floor.id})
        graph_portals={edge.get("portalId") for edge in layout.graph.edges if edge["type"]=="connectedByDoor"}
        missing=graph_portals-physical
        if missing:diagnostics.append({"code":"PORTAL_GRAPH_MISMATCH","portalIds":sorted(missing)})
        return diagnostics


def budget_report(operations:list[dict[str,Any]],chunk_by_class:dict[str,str]|None=None,chunk_size:float=10.0)->dict[str,Any]:
    chunks=defaultdict(int);types=defaultdict(int);chunk_by_class=chunk_by_class or {}
    for op in operations:
        args=op.get("arguments",{});pos=args.get("position",[0,0,0]);key=f"{int(pos[0]//chunk_size)}:{int(pos[1]//chunk_size)}:{int(pos[2]//chunk_size)}"
        chunks[key]+=1;types[chunk_by_class.get(args.get("class"),"UNKNOWN")]+=1
    hotspots=[{"chunk":key,"count":count} for key,count in sorted(chunks.items()) if count>=20]
    warnings=[]
    if hotspots:warnings.append({"code":"BUILDING_BUDGET_WARNING","message":"Informational hotspot threshold reached; not an engine limit","hotspots":hotspots})
    return {"totalObjects":len(operations),"structureCount":types["STRUCTURE"],"itemCount":types["ITEM"],
        "decorCount":types["DECOR"],"unknownCount":types["UNKNOWN"],"objectsPerChunk":dict(sorted(chunks.items())),
        "hotspots":hotspots,"warnings":warnings,"thresholdProvenance":"heuristic informational only"}
