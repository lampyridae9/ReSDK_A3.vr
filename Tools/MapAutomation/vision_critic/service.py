"""Critic prompt, filesystem image I/O, cache, telemetry, and local validation."""
from __future__ import annotations

import json
from pathlib import Path
import time
import uuid
from typing import Any

from .capture import CaptureBundle
from .model import CriticContractError,CriticResult,CriticStatus,validate_critic_output
from .provider import CriticProvider

ROOT=Path(__file__).resolve().parents[3]
SCHEMA_PATH=ROOT/"Tools/MapAutomation/critic_result.schema.json"
PROMPT_PATH=ROOT/"Tools/MapAutomation/vision_critic/critic_prompt_v1.txt"
ARTIFACTS=ROOT/"Tools/MapAutomation/artifacts/critic"
CACHE=ROOT/"Tools/MapAutomation/artifacts/critic_cache"
PROMPT_VERSION="room-vision-critic-v1.1"


class CriticService:
    def __init__(self,provider:CriticProvider,*,model:str,max_attempts:int=2,cache_enabled:bool=True,timeout:float=60,
        artifact_dir:Path=ARTIFACTS,cache_dir:Path=CACHE):
        if not 1<=max_attempts<=3: raise ValueError("max_attempts must be 1..3")
        self.provider=provider;self.model=model;self.max_attempts=max_attempts;self.cache_enabled=cache_enabled;self.timeout=timeout
        self.artifact_dir=artifact_dir;self.cache_dir=cache_dir
        self.schema=json.loads(SCHEMA_PATH.read_text(encoding="utf-8"));self.system_prompt=PROMPT_PATH.read_text(encoding="utf-8").strip()

    def _save(self,result:CriticResult,attempt_log:list[dict[str,Any]],bundle:CaptureBundle)->CriticResult:
        self.artifact_dir.mkdir(parents=True,exist_ok=True);path=self.artifact_dir/f"{result.review_id}.json"
        try: result.artifact_path=str(path.relative_to(ROOT)).replace("\\","/")
        except ValueError: result.artifact_path=str(path)
        doc=result.json();doc["timestampUtc"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime());doc["attemptLog"]=attempt_log
        doc["captureBundleMetadata"]=bundle.json()
        path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n");return result

    def review_capture(self,bundle:CaptureBundle,*,iteration:int=0,previous_issue:dict[str,Any]|None=None)->CriticResult:
        if not 1<=len(bundle.views)<=3: raise ValueError("Critic requires 1..3 useful views")
        telemetry=bundle.image_telemetry();known_ids={x["semanticId"] for x in bundle.scene_manifest.get("objects",[])}
        known_views={x.view_id for x in bundle.views};key=bundle.cache_fingerprint(PROMPT_VERSION,self.model,self.schema)
        cache_path=self.cache_dir/(key+".json")
        review_id="critic_"+uuid.uuid4().hex
        if self.cache_enabled and cache_path.is_file():
            output=validate_critic_output(json.loads(cache_path.read_text(encoding="utf-8"))["validatedOutput"],known_ids,known_views)
            return self._save(CriticResult(review_id,CriticStatus.SUCCESS,self.provider.name,self.model,PROMPT_VERSION,1,
                bundle.generation_id,bundle.room_id,bundle.revision,iteration,output,[],{},0,0,telemetry,True),[],bundle)
        context="Capture Bundle metadata (paths excluded; images follow):\n"+json.dumps({"generationId":bundle.generation_id,
            "roomId":bundle.room_id,"revision":bundle.revision,"sceneFingerprint":bundle.scene_fingerprint,
            "sceneManifest":bundle.scene_manifest,"validatorSummary":bundle.validator_summary,
            "previousIssue":previous_issue},ensure_ascii=False,separators=(",",":"))
        logs=[];usage={};latency=0;last_status=CriticStatus.INVALID_OUTPUT;diagnostics=[]
        for attempt in range(1,self.max_attempts+1):
            response=self.provider.review_capture(bundle=bundle,context=context,system_prompt=self.system_prompt,schema=self.schema,timeout=self.timeout)
            latency+=response.latency_ms
            usage={key:(sum(x for x in (usage.get(key),response.usage.get(key)) if isinstance(x,int))
                if any(isinstance(x,int) for x in (usage.get(key),response.usage.get(key))) else None)
                for key in {"inputTokens","outputTokens","totalTokens"}}
            last_status=response.status;diagnostics=response.diagnostics
            logs.append({"attempt":attempt,"status":response.status.value,"responseId":response.response_id,"diagnostics":response.diagnostics,
                "usage":response.usage,"latencyMs":response.latency_ms,"rawOutput":response.raw_output})
            if response.status!=CriticStatus.SUCCESS:
                if response.status in {CriticStatus.PROVIDER_ERROR,CriticStatus.TIMEOUT,CriticStatus.REFUSED}: break
                continue
            try: output=validate_critic_output(response.output,known_ids,known_views)
            except CriticContractError as exc:
                diagnostics=[{"code":"LOCAL_CRITIC_VALIDATION_FAILED","message":str(exc)}];logs[-1]["diagnostics"]+=diagnostics
                context += "\nPrevious output violated the local contract: "+str(exc)+". Correct it without inventing IDs."
                continue
            if self.cache_enabled:
                self.cache_dir.mkdir(parents=True,exist_ok=True);cache_path.write_text(json.dumps({"validatedOutput":output},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            return self._save(CriticResult(review_id,CriticStatus.SUCCESS,self.provider.name,self.model,PROMPT_VERSION,1,
                bundle.generation_id,bundle.room_id,bundle.revision,iteration,output,[],usage,latency,attempt,telemetry),logs,bundle)
        return self._save(CriticResult(review_id,last_status,self.provider.name,self.model,PROMPT_VERSION,1,
            bundle.generation_id,bundle.room_id,bundle.revision,iteration,None,diagnostics,usage,latency,len(logs),telemetry),logs,bundle)
