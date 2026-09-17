"""Bounded building semantic overlays using the existing Phase 7 renderer."""
from .structure import BuildingFrame
from vision_critic.capture import render_semantic_overlay


def semantic_placements(plan, asl_offset=0, limit=24):
    frame=BuildingFrame(tuple(plan['frame']['origin']))
    points=[]
    def add(label,point):
        world=frame.world(point);world[2]+=asl_offset
        points.append({'id':label,'asset':'','transform':{'position':world}})
    # Floors and portals first, then a bounded selection of logical walls.
    for floor in plan['floors']:
        z=floor['level']['datum_z']
        add(floor['level']['id'],[0,0,z])
        for wall in floor['walls']:
            horizontal=abs(wall['start'][1]-wall['end'][1])<1e-6
            for opening in wall['openings']:
                p=list(wall['start']);p[0 if horizontal else 1]+=opening['offset_along_wall']+opening['width']/2
                p[2]+=opening['height']/2;add(opening['id'],p)
        for hole in floor['floorOpenings']:
            x0,y0,x1,y1=hole['rectangle'];add(hole['vertical_connection_id'],[(x0+x1)/2,(y0+y1)/2,z])
    for floor in plan['floors']:
        for wall in floor['walls']:
            p=[(a+b)/2 for a,b in zip(wall['start'],wall['end'])];p[2]+=wall['height']/2
            add(wall['id'],p)
    return points[:limit]


def render_building_overlay(clean_path,overlay_path,plan,pose,asl_offset):
    render_semantic_overlay(clean_path,overlay_path,
        {'placements':semantic_placements(plan,asl_offset),'semanticOnly':True,'avoidLabelOverlap':True},pose)
