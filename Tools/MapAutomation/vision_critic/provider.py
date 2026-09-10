"""Vision-provider abstraction, intentionally separate from PlannerProvider."""
from __future__ import annotations

from abc import ABC,abstractmethod
import base64
import json
from pathlib import Path
import socket
import time
from typing import Any
from urllib import error,request

from .capture import CaptureBundle
from .model import CriticStatus,ProviderResponse


class CriticProvider(ABC):
    name="abstract"
    @abstractmethod
    def review_capture(self,*,bundle:CaptureBundle,context:str,system_prompt:str,schema:dict[str,Any],timeout:float)->ProviderResponse: raise NotImplementedError


class OpenAICriticProvider(CriticProvider):
    name="openai"
    def __init__(self,api_key:str,model:str="gpt-5",endpoint:str="https://api.openai.com/v1/responses"):
        if not api_key: raise ValueError("OPENAI_API_KEY is required")
        self.api_key=api_key;self.model=model;self.endpoint=endpoint

    @staticmethod
    def _image(path:str)->dict[str,Any]:
        raw=Path(path).read_bytes();encoded=base64.b64encode(raw).decode("ascii")
        return {"type":"input_image","image_url":"data:image/png;base64,"+encoded,"detail":"high"}

    def review_capture(self,*,bundle:CaptureBundle,context:str,system_prompt:str,schema:dict[str,Any],timeout:float)->ProviderResponse:
        started=time.perf_counter();content=[{"type":"input_text","text":context}]
        for view in bundle.views:
            content.append({"type":"input_text","text":f"View {view.view_id}; role={view.camera_role}; mode=CLEAN"});content.append(self._image(view.clean_image))
            if view.class_overlay_image:
                content.append({"type":"input_text","text":f"View {view.view_id}; role={view.camera_role}; mode=CLASS_OVERLAY; same pose/revision"});content.append(self._image(view.class_overlay_image))
        payload={"model":self.model,"instructions":system_prompt,"input":[{"role":"user","content":content}],
            "reasoning":{"effort":"low"},"max_output_tokens":1600,"store":False,
            "text":{"format":{"type":"json_schema","name":"relicta_room_vision_critic","strict":True,"schema":schema}}}
        call=request.Request(self.endpoint,data=json.dumps(payload,ensure_ascii=False).encode(),method="POST",
            headers={"Authorization":"Bearer "+self.api_key,"Content-Type":"application/json"})
        try:
            with request.urlopen(call,timeout=timeout) as response: doc=json.loads(response.read().decode())
        except (TimeoutError,socket.timeout) as exc:
            return ProviderResponse(CriticStatus.TIMEOUT,diagnostics=[{"code":"PROVIDER_TIMEOUT","message":str(exc)}],latency_ms=int((time.perf_counter()-started)*1000))
        except error.HTTPError as exc:
            return ProviderResponse(CriticStatus.PROVIDER_ERROR,diagnostics=[{"code":"OPENAI_HTTP_ERROR","httpStatus":exc.code,"message":exc.read().decode(errors="replace")[:2000]}],latency_ms=int((time.perf_counter()-started)*1000))
        except (error.URLError,OSError,json.JSONDecodeError) as exc:
            return ProviderResponse(CriticStatus.PROVIDER_ERROR,diagnostics=[{"code":"OPENAI_PROVIDER_ERROR","message":str(exc)}],latency_ms=int((time.perf_counter()-started)*1000))
        text=None;refusal=None
        for item in doc.get("output",[]):
            if item.get("type")!="message": continue
            for part in item.get("content",[]):
                if part.get("type")=="output_text": text=part.get("text")
                elif part.get("type")=="refusal": refusal=part.get("refusal")
        usage=doc.get("usage",{});normalized={"inputTokens":usage.get("input_tokens"),"outputTokens":usage.get("output_tokens"),"totalTokens":usage.get("total_tokens")}
        latency=int((time.perf_counter()-started)*1000)
        if refusal:return ProviderResponse(CriticStatus.REFUSED,raw_output=refusal,usage=normalized,latency_ms=latency,response_id=doc.get("id"))
        if not isinstance(text,str):return ProviderResponse(CriticStatus.INVALID_OUTPUT,diagnostics=[{"code":"MISSING_STRUCTURED_OUTPUT"}],usage=normalized,latency_ms=latency,response_id=doc.get("id"))
        try: output=json.loads(text)
        except json.JSONDecodeError as exc:return ProviderResponse(CriticStatus.INVALID_OUTPUT,raw_output=text,diagnostics=[{"code":"INVALID_JSON","message":str(exc)}],usage=normalized,latency_ms=latency,response_id=doc.get("id"))
        return ProviderResponse(CriticStatus.SUCCESS,output,text,[],normalized,latency,doc.get("id"))
