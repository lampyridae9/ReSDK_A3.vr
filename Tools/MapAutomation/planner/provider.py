"""Planner provider abstraction and OpenAI Responses API implementation."""
from __future__ import annotations

from abc import ABC, abstractmethod
import json
import socket
import time
from typing import Any
from urllib import error, request

from .model import PlannerStatus, ProviderResponse


class PlannerProvider(ABC):
    name = "abstract"

    @abstractmethod
    def plan_room(self, *, system_prompt: str, user_prompt: str, schema: dict[str, Any], timeout: float) -> ProviderResponse:
        raise NotImplementedError


class OpenAIResponsesProvider(PlannerProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-5.6-luna", endpoint: str = "https://api.openai.com/v1/responses"):
        if not api_key: raise ValueError("OPENAI_API_KEY is required")
        self.api_key = api_key; self.model = model; self.endpoint = endpoint

    def plan_room(self, *, system_prompt: str, user_prompt: str, schema: dict[str, Any], timeout: float) -> ProviderResponse:
        started=time.perf_counter()
        payload={
            "model":self.model,
            "instructions":system_prompt,
            "input":user_prompt,
            "reasoning":{"effort":"low"},
            "max_output_tokens":800,
            "store":False,
            "text":{"format":{"type":"json_schema","name":"planner_room_brief","strict":True,"schema":schema}},
        }
        call=request.Request(self.endpoint,data=json.dumps(payload,ensure_ascii=False).encode("utf-8"),method="POST",
            headers={"Authorization":"Bearer "+self.api_key,"Content-Type":"application/json"})
        try:
            with request.urlopen(call,timeout=timeout) as response:
                doc=json.loads(response.read().decode("utf-8"))
        except (TimeoutError,socket.timeout) as exc:
            return ProviderResponse(PlannerStatus.TIMEOUT,diagnostics=[{"code":"PROVIDER_TIMEOUT","message":str(exc)}],latency_ms=int((time.perf_counter()-started)*1000))
        except error.HTTPError as exc:
            body=exc.read().decode("utf-8",errors="replace")[:2000]
            return ProviderResponse(PlannerStatus.PROVIDER_ERROR,diagnostics=[{"code":"OPENAI_HTTP_ERROR","httpStatus":exc.code,"message":body}],latency_ms=int((time.perf_counter()-started)*1000))
        except (error.URLError,OSError,json.JSONDecodeError) as exc:
            return ProviderResponse(PlannerStatus.PROVIDER_ERROR,diagnostics=[{"code":"OPENAI_PROVIDER_ERROR","message":str(exc)}],latency_ms=int((time.perf_counter()-started)*1000))
        usage=doc.get("usage",{})
        normalized={"inputTokens":usage.get("input_tokens"),"outputTokens":usage.get("output_tokens"),"totalTokens":usage.get("total_tokens")}
        refusal=None;text=None
        for item in doc.get("output",[]):
            if item.get("type")!="message": continue
            for content in item.get("content",[]):
                if content.get("type")=="refusal": refusal=content.get("refusal","provider refusal")
                elif content.get("type")=="output_text": text=content.get("text")
        latency=int((time.perf_counter()-started)*1000)
        if refusal is not None:
            return ProviderResponse(PlannerStatus.REFUSED,raw_output=refusal,diagnostics=[{"code":"PROVIDER_REFUSAL","message":refusal}],usage=normalized,latency_ms=latency,response_id=doc.get("id"))
        if not isinstance(text,str):
            return ProviderResponse(PlannerStatus.INVALID_OUTPUT,diagnostics=[{"code":"MISSING_STRUCTURED_OUTPUT"}],usage=normalized,latency_ms=latency,response_id=doc.get("id"))
        try: output=json.loads(text)
        except json.JSONDecodeError as exc:
            return ProviderResponse(PlannerStatus.INVALID_OUTPUT,raw_output=text,diagnostics=[{"code":"INVALID_JSON","message":str(exc)}],usage=normalized,latency_ms=latency,response_id=doc.get("id"))
        return ProviderResponse(PlannerStatus.SUCCESS,output=output,raw_output=text,usage=normalized,latency_ms=latency,response_id=doc.get("id"))
