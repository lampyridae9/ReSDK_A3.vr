"""Offline checks only: these do NOT execute SQF or certify engine behavior."""
from __future__ import annotations

import re
import shutil
import uuid
import unittest
import json
from pathlib import Path

from prepare_probe import DESTINATION, TEMPLATE, build_fixture, prepare
from transport import FileQueueClient

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "Src/Editor/MapAutomation"


def sqf_tokens(text: str) -> str:
    """Remove SQF strings/comments for delimiter and public-surface inspection."""
    pattern = r'"(?:""|[^\"])*"|\x27(?:\x27\x27|[^\x27])*\x27|/\*[\s\S]*?\*/|//[^\n]*'
    return re.sub(pattern, lambda m: "\n" * m.group().count("\n"), text)


class FixtureTests(unittest.TestCase):
    def test_exact_template_metadata_change(self):
        template = (ROOT / TEMPLATE).read_text(encoding="utf-8-sig")
        result = build_fixture(template)
        self.assertIn('""__automationProbe"",""MapAutomation-v1""', result)
        self.assertNotIn('[""missionName"",""TEMP""]', result)
        self.assertEqual(template.count("class Item"), result.count("class Item"))

    def test_missing_or_ambiguous_metadata_rejected(self):
        token = '[""missionName"",""TEMP""]'
        for invalid in ("", "TEMP", token + token):
            with self.assertRaises(ValueError):
                build_fixture(invalid)

    def test_no_production_write_and_no_overwrite(self):
        scratch = ROOT / "Tools/MapAutomation/artifacts"
        scratch.mkdir(parents=True, exist_ok=True)
        root = scratch / ("fixture_" + uuid.uuid4().hex)
        root.mkdir()
        try:
            self.assertTrue(root.resolve().is_relative_to(scratch.resolve()))
            template = root / TEMPLATE
            template.parent.mkdir(parents=True)
            template.write_text('[""missionName"",""TEMP""]', encoding="utf-8")
            mission = root / "mission.sqm"
            mission.write_text("production sentinel", encoding="utf-8")
            target = prepare(root)
            self.assertEqual(target, root / DESTINATION)
            first = target.read_bytes()
            with self.assertRaises(FileExistsError):
                prepare(root)
            self.assertEqual(target.read_bytes(), first)
            self.assertEqual(mission.read_text(), "production sentinel")
        finally:
            if not root.resolve().is_relative_to(scratch.resolve()):
                raise RuntimeError("Refusing cleanup outside test scratch directory")
            shutil.rmtree(root)


class SourceChecks(unittest.TestCase):
    def test_large_reports_do_not_use_bounded_file_read(self):
        text = (MODULE / "MapAutomation_tests.sqf").read_text(encoding="utf-8")
        body = text.split("function(ma_test_record)", 1)[1].split("function(ma_test_compare)", 1)[0]
        self.assertIn("count _text <= 4096", body)
        self.assertIn("call file_exists", body)
        self.assertLess(body.index("count _text <= 4096"), body.index("call file_read"))

    def test_roundtrip_uses_checked_async_copy(self):
        text = (MODULE / "MapAutomation_tests.sqf").read_text(encoding="utf-8")
        self.assertIn("call file_copyAsync", text)
        self.assertNotRegex(text, r'\bcall\s+file_copy\s*;')
        self.assertIn('_loadedText isNotEqualTo _saved', text)
        self.assertIn('ma_loadCopyState != "COPIED"', text)
        helper = (ROOT / "Src/Editor/Core/Core_io_helper.sqf").read_text(encoding="utf-8-sig")
        body = helper.split("function(file_copyAsync)", 1)[1].split("function(file_unlockAsync)", 1)[0]
        self.assertNotIn("[true,_path] call _onCopy", body)
        self.assertIn("[_result,_path] call _onCopy", body)
        self.assertIn("[_result,_f] call _onCopy", body)

    def test_no_engine_isnull_macro_collision(self):
        # Relicta defines isNull(val) as an isNil macro, not the native object check.
        for path in MODULE.glob("*.sqf"):
            text = sqf_tokens(path.read_text(encoding="utf-8"))
            self.assertIsNone(re.search(r'\bisNull\b', text), path.name)

    def test_private_assignment_requires_local_name(self):
        # Regression: `private inspector_... =` is invalid SQF, despite balanced braces.
        for path in MODULE.glob("*.sqf"):
            text = sqf_tokens(path.read_text(encoding="utf-8"))
            names = re.findall(r'\bprivate\s+([A-Za-z_]\w*)\s*=', text)
            self.assertEqual([name for name in names if not name.startswith("_")], [], path.name)

    def test_balanced_delimiters(self):
        for path in MODULE.glob("*.sqf"):
            with self.subTest(file=path.name):
                text = sqf_tokens(path.read_text(encoding="utf-8"))
                stack = []
                for c in text:
                    if c in "([{":
                        stack.append(c)
                    elif c in ")]}":
                        self.assertTrue(stack, f"Unexpected {c} in {path}")
                        self.assertEqual(stack.pop(), dict(zip(")]}", "([{"))[c])
                self.assertEqual(stack, [])

    def test_unique_functions_and_resolved_local_calls(self):
        text = "\n".join(p.read_text(encoding="utf-8") for p in MODULE.glob("*.sqf"))
        definitions = re.findall(r'(?:init_)?function\((ma_\w+)\)', text)
        self.assertEqual(len(definitions), len(set(definitions)))
        calls = set(re.findall(r'\b(?:call|spawn)\s+(ma_\w+)', sqf_tokens(text)))
        self.assertEqual(calls - set(definitions), set())

    def test_no_dynamic_execution_in_gateway(self):
        text = sqf_tokens("\n".join(
            (MODULE / name).read_text(encoding="utf-8")
            for name in ("MapAutomation_api.sqf", "MapAutomation_transport.sqf")
        ))
        self.assertIsNone(re.search(r'\b(?:compile|compileFinal|preprocessFile|callExtension)\b', text))

    def test_transport_is_wired_and_data_only(self):
        init = (MODULE / "MapAutomation_init.sqf").read_text(encoding="utf-8")
        transport = (MODULE / "MapAutomation_transport.sqf").read_text(encoding="utf-8")
        self.assertIn('#include "MapAutomation_transport.sqf"', init)
        # EditorEngine's function(...) macro supplies the separator between declarations.
        # Executable assignments between included function files cause an Eden "Missing ;".
        preamble = transport.split("function(", 1)[0]
        self.assertEqual(sqf_tokens(preamble).strip(), "")
        self.assertIn("FromJSON _raw", transport)
        self.assertIn("toJSON _response", transport)
        for operation in ("getCapabilities", "inspectScene", "inspectObjects", "applyPatch", "captureViews"):
            self.assertIn(f'"{operation}"', transport)
        self.assertIn('"REVISION_MISMATCH"', transport)
        self.assertIn('"REQUEST_ID_REUSE_CONFLICT"', transport)

    def test_python_protocol_envelope(self):
        client = FileQueueClient(timeout=0.01)
        request = client.envelope("inspectScene", 12, {}, "request_1")
        self.assertEqual(set(request), {
            "protocolVersion", "requestId", "sessionId", "expectedRevision", "operation", "arguments"
        })
        self.assertEqual(json.loads(json.dumps(request)), request)

    def test_existing_classes_declared_and_module_wired(self):
        floor = (ROOT / "Src/host/GameObjects/Decors/BigFloor.sqf").read_text(encoding="utf-8-sig")
        walls = (ROOT / "Src/host/GameObjects/Structures/Constructions/Walls.sqf").read_text(encoding="utf-8-sig")
        for classname in ("BigConcreteFloor", "ConcreteGreenWall", "WoodenArch"):
            self.assertIn(f"class({classname})", floor + walls)
        loader = (ROOT / "Src/Editor/Editor_init.sqf").read_text(encoding="utf-8-sig")
        self.assertLess(loader.index('componentInit(MapAutomation)'), loader.index('componentInit(Core_postInit)'))

    def test_selection_helper_declares_unlock_layer_parameter(self):
        manager = (ROOT / "Src/Editor/GameObjectsLibrary/GOLib_objectManager.sqf").read_text(encoding="utf-8-sig")
        body = manager.split("function(golib_setSelectedObjects)", 1)[1].split("function(golib_getSelectedObjects)", 1)[0]
        self.assertIn('params [["_objList",[]],["_unlockLayer",false]];', body)

    def test_copy_paste_test_invokes_both_eden_actions(self):
        tests = (MODULE / "MapAutomation_tests.sqf").read_text(encoding="utf-8")
        copy_index = tests.index('do3DENAction "CopyUnit"')
        paste_index = tests.index('["Paste","PasteUnitOrig","PasteItems"]')
        self.assertLess(copy_index, paste_index)
        self.assertIn("FAILED_TEST_CLEANUP", tests)

    def test_copy_paste_post_load_verification_is_serialized(self):
        tests = (MODULE / "MapAutomation_tests.sqf").read_text(encoding="utf-8")
        init = (MODULE / "MapAutomation_init.sqf").read_text(encoding="utf-8")
        self.assertIn('ma_roundTripPending",[_expected,ma_session,ma_revision,_copyPasteContext]', tests)
        resume = tests.split("function(ma_test_resumeRoundTrip)", 1)[1].split(
            "function(ma_test_reset)", 1
        )[0]
        self.assertIn("call ma_test_finishCopyPasteContext", resume)
        roundtrip_branch = init.split(
            'uiNamespace getVariable ["ma_roundTripPending",[]]', 1
        )[1].split("if (isNil", 1)[0]
        self.assertIn("} else {", roundtrip_branch)

    def test_entity_added_identity_fallback_is_wired(self):
        init = (MODULE / "MapAutomation_init.sqf").read_text(encoding="utf-8")
        api = (MODULE / "MapAutomation_api.sqf").read_text(encoding="utf-8")
        self.assertIn('"onEntityAdded"', init)
        self.assertIn("spawn ma_onEntityAddedIdentity", init)
        self.assertIn("function(ma_onEntityAddedIdentity)", api)
        self.assertIn("ma_suppressHistoryIdentityRepair", init)

    def test_full_architecture_saved(self):
        text = (ROOT / "Docs/AI_MAP_GENERATOR_PLAN.md").read_text(encoding="utf-8")
        self.assertGreater(len(text), 50000)
        self.assertEqual(len(re.findall(r'^## \d+\.', text, re.M)), 16)
        self.assertIn("## VERDICT", text)
        self.assertIn("Research: COMPLETE", text)
        self.assertIn("Automation Gateway: PHASE 1 COMPLETE", text)
        self.assertIn("Текущее состояние Phase 1: `PASS`", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
