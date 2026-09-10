#!/usr/bin/env python3
from __future__ import annotations
import json,unittest,uuid
from pathlib import Path
from planner import PlannerInput,PlannerService,PlannerStatus
from planner.model import ProviderResponse
from planner.provider import PlannerProvider
from semantic.pipeline import PatternPipeline,build_room_context

BASE={"schemaVersion":1,"intent":"create_room","roomType":"bedroom","style":["poor","utilitarian"],"capacity":{"people":2},"requirements":{"sleeping":2,"storage":1,"lighting":1},"preferences":{"workSurface":True,"seating":True,"compact":True},"seed":12345}
ROOT=Path(__file__).resolve().parents[2]
class SequenceProvider(PlannerProvider):
    name="test-provider"
    def __init__(self,*responses): self.responses=list(responses);self.calls=0
    def plan_room(self,**kwargs): result=self.responses[min(self.calls,len(self.responses)-1)];self.calls+=1;return result
def ok(value=BASE): return ProviderResponse(PlannerStatus.SUCCESS,output=json.loads(json.dumps(value)),raw_output=json.dumps(value),usage={"inputTokens":10,"outputTokens":5,"totalTokens":15},latency_ms=7)
class PlannerTests(unittest.TestCase):
    def service(self,provider,max_attempts=2,cache=False): return PlannerService(provider,model="test-model",max_attempts=max_attempts,cache_enabled=cache)
    def test_baseline_reaches_deterministic_pipeline(self):
        result=self.service(SequenceProvider(ok())).plan_room(PlannerInput("Создай бедную спальню для двух рабочих с кроватями.",12345))
        self.assertEqual(result.status,PlannerStatus.SUCCESS);self.assertEqual(result.validated_output,BASE)
        scene=build_room_context();before=scene.fingerprint();run1=PatternPipeline().run(result.validated_output,scene);run2=PatternPipeline().run(result.validated_output,build_room_context())
        self.assertEqual(run1.status,"PASS");self.assertEqual(run1.json(),run2.json());self.assertEqual(scene.fingerprint(),before)
    def test_invalid_output_is_repaired_once(self):
        bad=dict(BASE);bad["rawSQF"]="code";provider=SequenceProvider(ok(bad),ok())
        result=self.service(provider).plan_room(PlannerInput("Create a bedroom for two with beds.",12345))
        self.assertEqual(result.status,PlannerStatus.SUCCESS);self.assertEqual(result.attempt_count,2);self.assertEqual(provider.calls,2)
    def test_repair_is_bounded(self):
        bad=dict(BASE);bad["roomType"]="bar";provider=SequenceProvider(ok(bad))
        result=self.service(provider,max_attempts=2).plan_room(PlannerInput("Create a bedroom with beds.",12345))
        self.assertEqual(result.status,PlannerStatus.SCHEMA_VALIDATION_FAILED);self.assertEqual(provider.calls,2)
    def test_provider_errors_are_not_retried(self):
        for status in (PlannerStatus.PROVIDER_ERROR,PlannerStatus.TIMEOUT,PlannerStatus.REFUSED):
            provider=SequenceProvider(ProviderResponse(status,diagnostics=[{"code":status.value}]))
            result=self.service(provider).plan_room(PlannerInput("Create a bedroom with one bed.",12345))
            self.assertEqual(result.status,status);self.assertEqual(provider.calls,1)
    def test_unsupported_and_ambiguous_do_not_call_provider(self):
        for prompt in ("Создай бар.","Make a room for two people."):
            provider=SequenceProvider(ok());result=self.service(provider).plan_room(PlannerInput(prompt,12345))
            self.assertEqual(result.status,PlannerStatus.UNSUPPORTED_REQUEST);self.assertEqual(provider.calls,0)
    def test_cache_reuses_validated_brief(self):
        provider=SequenceProvider(ok());service=self.service(provider,cache=True);request=PlannerInput("Create a bedroom for two with beds. "+uuid.uuid4().hex,12345)
        self.assertFalse(service.plan_room(request).cached);self.assertTrue(service.plan_room(request).cached);self.assertEqual(provider.calls,1)
    def test_artifact_contains_no_api_secret(self):
        result=self.service(SequenceProvider(ok())).plan_room(PlannerInput("Create a bedroom for two with beds.",12345))
        raw=(ROOT/result.artifact_path).read_text(encoding="utf-8")
        self.assertNotIn("api_key",raw.casefold());self.assertIn('"attemptCount": 1',raw)
    def test_seed_mismatch_requires_repair(self):
        mismatch=json.loads(json.dumps(BASE));mismatch["seed"]=9
        result=self.service(SequenceProvider(ok(mismatch)),max_attempts=1).plan_room(PlannerInput("Create a bedroom with beds.",12345))
        self.assertEqual(result.status,PlannerStatus.SCHEMA_VALIDATION_FAILED)
    def test_optional_chair_without_table_is_semantically_valid(self):
        brief=json.loads(json.dumps(BASE));brief["capacity"]["people"]=1;brief["requirements"]["sleeping"]=1;brief["preferences"]["workSurface"]=False
        result=self.service(SequenceProvider(ok(brief))).plan_room(PlannerInput("Create a bedroom with a bed and optional chair.",12345))
        self.assertEqual(result.status,PlannerStatus.SUCCESS)
if __name__=="__main__": unittest.main()
