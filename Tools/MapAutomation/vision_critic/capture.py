"""Versioned filesystem-reference capture bundle; PNG bytes never enter Eden transport."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct
from typing import Any

from PIL import Image,ImageDraw,ImageFont


def _hash_file(path:Path)->str:
    digest=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""): digest.update(chunk)
    return digest.hexdigest()


def png_dimensions(path:Path)->tuple[int,int]|None:
    with path.open("rb") as stream: header=stream.read(24)
    if len(header)>=24 and header[:8]==b"\x89PNG\r\n\x1a\n" and header[12:16]==b"IHDR": return struct.unpack(">II",header[16:24])
    return None


def render_semantic_overlay(clean_path:str,overlay_path:str,generation:dict[str,Any],pose:dict[str,Any])->None:
    """Label known generated objects when Eden's class UI is absent from PNG output."""
    import math
    camera=pose.get("positionASL");target=pose.get("targetASL")
    if not camera or not target:return
    def unit(v):
        length=math.sqrt(sum(x*x for x in v))
        return tuple(x/length for x in v) if length else (0.,0.,0.)
    def dot(a,b):return sum(x*y for x,y in zip(a,b))
    forward=unit(tuple(target[i]-camera[i] for i in range(3)));right=unit((forward[1],-forward[0],0.))
    up=unit((right[1]*forward[2]-right[2]*forward[1],right[2]*forward[0]-right[0]*forward[2],right[0]*forward[1]-right[1]*forward[0]))
    with Image.open(clean_path) as source:
        image=source.convert("RGB");draw=ImageDraw.Draw(image);width,height=image.size
        try:font=ImageFont.truetype("arial.ttf",max(18,height//45))
        except OSError:font=ImageFont.load_default()
        focal=height/(2*math.tan(float(pose.get("fov",.8))/2));points={};label_boxes=[]
        for row in generation.get("placements",[]):
            position=(row.get("transform") or {}).get("position")
            if not position:continue
            delta=tuple(position[i]-camera[i] for i in range(3));depth=dot(delta,forward)
            if depth<=.1:continue
            sx=width/2+dot(delta,right)*focal/depth;sy=height/2-dot(delta,up)*focal/depth
            if not (-80<=sx<=width+80 and -80<=sy<=height+80):continue
            label=row['id'] if generation.get('semanticOnly') else f'{row["id"]} · {row.get("asset","")}'
            box=draw.textbbox((sx+13,sy-15),label,font=font,stroke_width=2)
            if generation.get('avoidLabelOverlap') and any(box[0]<b[2]+10 and box[2]>b[0]-10 and box[1]<b[3]+10 and box[3]>b[1]-10 for b in label_boxes):continue
            label_boxes.append(box);points[row["id"]]=(sx,sy)
            draw.rectangle((box[0]-5,box[1]-3,box[2]+5,box[3]+3),fill=(10,10,10),outline=(255,210,0),width=2)
            draw.ellipse((sx-7,sy-7,sx+7,sy+7),fill=(255,210,0),outline=(0,0,0),width=2)
            draw.text((sx+13,sy-15),label,font=font,fill=(255,255,255),stroke_width=1,stroke_fill=(0,0,0))
        chair=points.get("seating_001");table=points.get("work_surface_001")
        if chair and table:draw.line((chair[0],chair[1],table[0],table[1]),fill=(255,70,210),width=4)
        draw.rectangle((12,12,505,48),fill=(10,10,10),outline=(255,210,0),width=2)
        title='BUILDING STRUCTURE · semantic IDs' if generation.get('semanticOnly') else 'SEMANTIC CLASS OVERLAY · generated objects'
        draw.text((22,17),title,font=font,fill=(255,255,255))
        image.save(overlay_path,"PNG")


@dataclass(frozen=True)
class CaptureView:
    view_id:str; camera_role:str; camera_pose:dict[str,Any]; fov:float
    clean_image:str; class_overlay_image:str|None=None; semantic_overlay_image:str|None=None

    def json(self)->dict[str,Any]:
        return {"viewId":self.view_id,"cameraRole":self.camera_role,"cameraPose":self.camera_pose,"fov":self.fov,
            "cleanImage":self.clean_image,"classOverlayImage":self.class_overlay_image,"semanticOverlayImage":self.semantic_overlay_image}


@dataclass(frozen=True)
class CaptureBundle:
    generation_id:str; room_id:str; revision:int; scene_fingerprint:str
    views:tuple[CaptureView,...]; scene_manifest:dict[str,Any]; validator_summary:dict[str,Any]; schema_version:int=1

    def json(self)->dict[str,Any]:
        return {"schemaVersion":self.schema_version,"generationId":self.generation_id,"roomId":self.room_id,
            "revision":self.revision,"sceneFingerprint":self.scene_fingerprint,"views":[x.json() for x in self.views],
            "sceneManifest":self.scene_manifest,"validatorSummary":self.validator_summary}

    def image_telemetry(self,require_files:bool=True)->list[dict[str,Any]]:
        rows=[]
        for view in self.views:
            for mode,raw in (("clean",view.clean_image),("class_overlay",view.class_overlay_image),("semantic_overlay",view.semantic_overlay_image)):
                if not raw: continue
                path=Path(raw)
                if not path.is_file():
                    if require_files: raise FileNotFoundError(path)
                    rows.append({"viewId":view.view_id,"mode":mode,"path":str(path),"exists":False});continue
                dims=png_dimensions(path)
                rows.append({"viewId":view.view_id,"mode":mode,"path":str(path),"exists":True,"bytes":path.stat().st_size,
                    "width":dims[0] if dims else None,"height":dims[1] if dims else None,"sha256":_hash_file(path)})
        return rows

    def cache_fingerprint(self,prompt_version:str,model:str,schema:dict[str,Any])->str:
        payload={"images":self.image_telemetry(),"manifest":self.scene_manifest,"promptVersion":prompt_version,"model":model,"schema":schema}
        return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()


def build_capture_bundle(generation:dict[str,Any],*,iteration:int=0)->CaptureBundle:
    """Convert Phase 7 GenerationResult JSON into the deliberately small critic input."""
    room_plan=generation.get("roomPlan") or {};slots=room_plan.get("slots") or []
    objects=[]
    placement_classes={x.get("id"):x.get("asset") for x in generation.get("placements",[]) if isinstance(x,dict)}
    for slot in slots:
        if slot.get("placement")=="virtual" or slot.get("status","").startswith("DROPPED"): continue
        objects.append({"semanticId":slot["id"],"role":slot["function"],"classname":slot.get("asset") or placement_classes.get(slot["id"]),
            "priority":slot["priority"],"relations":slot.get("relations",[])})
    views=[]
    captured_revisions=set();captured_fingerprints=[]
    for index,row in enumerate(generation.get("screenshots",[])):
        artifact=row.get("artifact",{});pose=row.get("cameraPose",{})
        clean=artifact.get("cleanPath") or artifact.get("path")
        if not clean: continue
        raw_revision=row.get("revision",artifact.get("revision"))
        if raw_revision is not None: captured_revisions.add(int(raw_revision))
        if artifact.get("sceneFingerprint") is not None:captured_fingerprints.append(artifact["sceneFingerprint"])
        role=artifact.get("cameraRole") or pose.get("name") or f"view_{index}"
        view_id=artifact.get("viewId") or role
        overlay=artifact.get("classOverlayPath")
        if overlay:render_semantic_overlay(clean,overlay,generation,pose)
        views.append(CaptureView(view_id,role,{"positionASL":pose.get("positionASL",artifact.get("positionASL")),
            "targetASL":pose.get("targetASL",artifact.get("targetASL"))},float(pose.get("fov",artifact.get("fov",.8))),
            clean,overlay,artifact.get("semanticOverlayPath")))
    if len(captured_revisions)>1: raise ValueError("capture bundle mixes screenshot revisions")
    revision=next(iter(captured_revisions),int(generation.get("sceneRevisionAfter") or 0))
    manifest={"schemaVersion":1,"generationId":generation["generationId"],"roomId":generation["roomId"],
        "revision":revision,"iteration":iteration,"objects":objects}
    navigation=generation.get("metrics",{}).get("navigationResult")
    hard_failure_codes={"FINAL_PREFLIGHT_VALIDATION_FAILED","ROOM_PLAN_VALIDATION_FAILED","VALIDATION_FAILED"}
    hard_diagnostics=[x for x in generation.get("diagnostics",[]) if x.get("code") in hard_failure_codes]
    # Capture/provider failures do not rewrite the already completed Phase 3 fact.
    object_facts=[]
    for row in generation.get("dryRunPlacements",[]):
        intent=row.get("intent") or {};placement=row.get("placement") or {}
        if row.get("status")=="VALID" and intent.get("id"):
            object_facts.append({"semanticId":intent["id"],"solverStatus":"VALID",
                "passedHardConstraints":intent.get("hardConstraints",[]),"againstWall":intent.get("againstWall"),
                "supportSurface":intent.get("onSurface")})
    validator={"authority":"ENGINE_SOLVER_FACT","spatialPass":bool(navigation and navigation.get("reachable")) and not hard_diagnostics,
        "navigation":navigation,"objects":object_facts,"diagnostics":hard_diagnostics}
    scene_fingerprint=generation.get("sceneFingerprintAfter") or generation.get("sceneFingerprintBefore") or "unknown"
    if generation.get("status")!="SUCCESS" and captured_fingerprints:
        scene_fingerprint=hashlib.sha256(json.dumps(captured_fingerprints[0],sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    return CaptureBundle(generation["generationId"],generation["roomId"],revision,scene_fingerprint,tuple(views),manifest,validator)
