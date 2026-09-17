"""Deterministic Phase 4 planner-contract to Phase 3 dry-run pipeline."""
from __future__ import annotations

from dataclasses import dataclass
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from spatial.model import Diagnostic, PlacementIntent, SceneState, SupportSurface
from spatial.solver import PlacementSolver, load_phase3_assets
from .model import (
    Cardinality, FUNCTIONAL_ROLES, RELATIONS, STYLES, Requirement, RoomPattern,
    RoomPlan, SemanticDiagnostic, SemanticRelation, SemanticSlot,
)

ROOT = Path(__file__).resolve().parents[3]
PATTERNS = ROOT / "Tools/MapAutomation/patterns"
ASSET_RULES = ROOT / "Tools/MapAutomation/semantic_assets.json"
PLANNER_SCHEMA = ROOT / "Tools/MapAutomation/planner_room_brief.schema.json"
FORBIDDEN_FIELDS = {"position", "rotation", "rawsqf", "executecode", "python", "shell", "classname", "class"}


class PlannerContractError(ValueError): pass


def _exact_keys(value: dict[str, Any], allowed: set[str], required: set[str], path: str) -> None:
    unknown = set(value) - allowed
    missing = required - set(value)
    if unknown: raise PlannerContractError(f"{path}: unknown fields {sorted(unknown)}")
    if missing: raise PlannerContractError(f"{path}: missing fields {sorted(missing)}")


def _scan_forbidden(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_FIELDS: raise PlannerContractError(f"{path}.{key}: forbidden planner field")
            _scan_forbidden(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value): _scan_forbidden(child, f"{path}[{index}]")


def validate_planner_brief(value: Any) -> dict[str, Any]:
    """Dependency-free strict validation equivalent to planner_room_brief.schema.json."""
    if not isinstance(value, dict): raise PlannerContractError("$: expected object")
    _scan_forbidden(value)
    top = {"schemaVersion", "intent", "roomType", "style", "capacity", "requirements", "preferences", "seed"}
    _exact_keys(value, top, top, "$")
    if type(value["schemaVersion"]) is not int or value["schemaVersion"] != 1: raise PlannerContractError("schemaVersion must equal 1")
    if value["intent"] != "create_room": raise PlannerContractError("intent must be create_room")
    if value["roomType"] != "bedroom": raise PlannerContractError("unknown roomType")
    styles = value["style"]
    if not isinstance(styles, list) or not styles or any(type(x) is not str for x in styles) or len(styles) != len(set(styles)):
        raise PlannerContractError("style must be a non-empty unique string array")
    unknown_styles = set(styles) - STYLES
    if unknown_styles: raise PlannerContractError("unknown style: "+str(sorted(unknown_styles)))
    capacity = value["capacity"]
    if not isinstance(capacity, dict): raise PlannerContractError("capacity must be object")
    _exact_keys(capacity, {"people"}, {"people"}, "capacity")
    people = capacity["people"]
    if type(people) is not int or not 1 <= people <= 4: raise PlannerContractError("capacity.people must be integer 1..4")
    req = value["requirements"]
    if not isinstance(req, dict): raise PlannerContractError("requirements must be object")
    _exact_keys(req, {"sleeping", "storage", "lighting"}, {"sleeping", "storage", "lighting"}, "requirements")
    limits = {"sleeping": (1, 4), "storage": (1, 2), "lighting": (1, 1)}
    for key, (lo, hi) in limits.items():
        if type(req[key]) is not int or not lo <= req[key] <= hi: raise PlannerContractError(f"requirements.{key} out of range")
    if req["sleeping"] < people: raise PlannerContractError("sleeping requirement is below people capacity")
    prefs = value["preferences"]
    if not isinstance(prefs, dict): raise PlannerContractError("preferences must be object")
    preference_keys = {"workSurface", "seating", "compact"}
    _exact_keys(prefs, preference_keys, preference_keys, "preferences")
    if any(type(v) is not bool for v in prefs.values()): raise PlannerContractError("preference values must be boolean")
    if type(value["seed"]) is not int or not 0 <= value["seed"] <= 2147483647: raise PlannerContractError("seed out of range")
    return copy.deepcopy(value)


def _cardinality(raw: dict[str, Any]) -> Cardinality:
    return Cardinality(int(raw["min"]), int(raw["preferred"]), int(raw["max"]))


def load_patterns(directory: Path = PATTERNS) -> dict[str, RoomPattern]:
    result = {}
    for path in sorted(directory.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        requirements = tuple(Requirement(x["function"], x["priority"], _cardinality(x["cardinality"])) for x in raw["requirements"])
        relations = {role: tuple(SemanticRelation(x["kind"], x["target"], bool(x.get("hard", False))) for x in rows)
            for role, rows in raw.get("relations", {}).items()}
        pattern = RoomPattern(raw["id"], raw["roomType"], tuple(raw["styles"]), _cardinality(raw["capacity"]["people"]),
            requirements, tuple(raw["strategies"]), relations, raw.get("provenance", {}))
        if pattern.id in result: raise ValueError("duplicate pattern: "+pattern.id)
        result[pattern.id] = pattern
    return result


class AssetResolver:
    """Resolve semantic roles only through catalog evidence and the Phase 3 hard gate."""
    def __init__(self, *, allow_developer_override: bool = False):
        self.assets, self.phase3 = load_phase3_assets()
        self.rules = json.loads(ASSET_RULES.read_text(encoding="utf-8"))
        core = json.loads((ROOT/"Tools/MapAutomation/catalog/core_assets.json").read_text(encoding="utf-8"))
        objects = json.loads((ROOT/"Tools/MapAutomation/catalog/objects.json").read_text(encoding="utf-8"))
        self.core = {x["classname"]: x for x in core["assets"]}
        self.objects = {x["classname"]: x for x in objects["objects"]}
        self.allow_developer_override = allow_developer_override

    def candidates(self, function: str, styles: tuple[str, ...], placement: str) -> list[str]:
        candidates = []
        for rule in self.rules["roles"].get(function, []):
            name = rule["classname"]
            asset = self.assets.get(name)
            catalog = self.core.get(name)
            obj = self.objects.get(name, {})
            if not asset or not catalog: continue
            if (not asset.generator_allowed or not catalog.get("generatorAllowed")) and not self.allow_developer_override: continue
            if asset.placement_type != placement or catalog.get("category") != rule["category"]: continue
            capability = rule.get("requiredCapability")
            if capability and obj.get("capabilities", {}).get(capability, {}).get("value") is not True: continue
            overlap = len(set(styles) & set(rule.get("style", [])))
            usage = int(catalog.get("usage", {}).get("totalCount", 0))
            confidence = float(catalog.get("semantic", {}).get("confidence", 0))
            candidates.append((overlap, confidence, usage, name))
        return [x[3] for x in sorted(candidates, reverse=True)]

    def resolve(self, slot: SemanticSlot) -> str:
        candidates = self.candidates(slot.function, slot.style, slot.placement)
        if not candidates: raise ValueError("UNRESOLVED_ASSET: "+slot.function)
        return candidates[0]


@dataclass
class PipelineResult:
    status: str
    feasibility: str
    plan: RoomPlan
    intents: list[PlacementIntent]
    placements: list[Any]
    diagnostics: list[SemanticDiagnostic]
    scene_patch: dict[str, Any]

    def json(self) -> dict[str, Any]:
        return {"schemaVersion": 1, "status": self.status, "feasibility": self.feasibility,
            "roomPlan": self.plan.json(), "placementIntents": [x.json() for x in self.intents],
            "placements": [x.json() for x in self.placements], "diagnostics": [x.json() for x in self.diagnostics],
            "scenePatch": self.scene_patch}


def _area(polygon: list[tuple[float, float]]) -> float:
    return abs(sum(polygon[i][0]*polygon[(i+1)%len(polygon)][1]-polygon[(i+1)%len(polygon)][0]*polygon[i][1] for i in range(len(polygon)))/2)


class PatternFeasibility:
    """Conservative area preflight; Phase 3 remains authoritative."""
    def __init__(self, asset_resolver: AssetResolver): self.asset_resolver = asset_resolver

    def evaluate(self, plan: RoomPlan, scene: SceneState) -> str:
        required_area = 0.8 * 1.5
        preferred_area = required_area
        for slot in plan.slots:
            if slot.placement == "virtual": continue
            try: name = self.asset_resolver.resolve(slot)
            except ValueError:
                if slot.priority == "required": return "INFEASIBLE"
                continue
            asset = self.asset_resolver.assets[name]
            dx = asset.bounds[1][0]-asset.bounds[0][0]; dy = asset.bounds[1][1]-asset.bounds[0][1]
            footprint = dx*dy*1.15
            preferred_area += footprint
            if slot.priority == "required": required_area += footprint
        available = _area(scene.region_polygon)
        if available < required_area: return "INFEASIBLE"
        if available < preferred_area*1.2: return "TIGHT"
        return "FEASIBLE"


class PatternValidator:
    """Structured semantic validation suitable for planner repair feedback."""
    def __init__(self, patterns: dict[str, RoomPattern]): self.patterns = patterns

    def validate(self, plan: RoomPlan) -> list[SemanticDiagnostic]:
        diagnostics = []
        pattern = self.patterns[plan.pattern_id]
        valid_targets = {s.id for s in plan.slots} | set(plan.surfaces) | {"roomCenter"}
        for req in pattern.requirements:
            count = sum(s.function == req.function and s.status in {"PLANNED", "RESOLVED", "PLACED", "SATISFIED"} for s in plan.slots)
            minimum = plan.capacity if req.function == "sleeping" else req.cardinality.minimum
            if count < minimum:
                code = "REQUIRED_FUNCTION_MISSING" if count == 0 and req.priority == "required" else "CARDINALITY_VIOLATION"
                diagnostics.append(SemanticDiagnostic(code, (req.function,), "ERROR",
                    {"minimum": minimum, "preferred": req.cardinality.preferred, "maximum": req.cardinality.maximum, "actual": count},
                    "restore the required semantic slots"))
        for slot in plan.slots:
            if slot.function not in FUNCTIONAL_ROLES:
                diagnostics.append(SemanticDiagnostic("INVALID_RELATION", (slot.id,), "ERROR", {"function": slot.function}))
            for rel in slot.relations:
                if rel.kind not in RELATIONS or (rel.target not in valid_targets and rel.hard):
                    diagnostics.append(SemanticDiagnostic("INVALID_RELATION", (slot.id,), "ERROR", {"relation": rel.kind, "target": rel.target}))
            if slot.placement != "virtual" and slot.asset is None and slot.status not in {"DROPPED_OPTIONAL", "DROPPED_PREFERRED"}:
                diagnostics.append(SemanticDiagnostic("UNRESOLVED_ASSET", (slot.id,), "ERROR", {}))
        return diagnostics


class PatternPipeline:
    def __init__(self, *, asset_resolver: AssetResolver | None = None):
        self.patterns = load_patterns()
        self.asset_resolver = asset_resolver or AssetResolver()
        self.solver = PlacementSolver(self.asset_resolver.assets, self.asset_resolver.phase3)
        self.preflight = PatternFeasibility(self.asset_resolver)
        self.validator = PatternValidator(self.patterns)

    def select_pattern(self, brief: dict[str, Any]) -> RoomPattern:
        matches = [p for p in self.patterns.values() if p.room_type == brief["roomType"] and set(brief["style"]) <= set(p.styles)]
        if not matches: raise PlannerContractError("no pattern for roomType/style")
        return sorted(matches, key=lambda p: p.id)[0]

    def create_plan(self, raw_brief: Any, scene: SceneState, *, room_id: str = "room_001",
        slot_namespace: str | None = None, strategy: str | None = None) -> RoomPlan:
        brief = validate_planner_brief(raw_brief); pattern = self.select_pattern(brief)
        if scene.entrance is None: raise ValueError("room context has no entrance")
        walls = sorted(k for k, v in scene.surfaces.items() if v.type == "wall")
        if not walls: raise ValueError("room context has no wall surfaces")
        digest = hashlib.sha256(f'{pattern.id}|{brief["seed"]}|{self.asset_resolver.phase3["catalogVersion"]}'.encode()).digest()
        if strategy is not None and strategy not in pattern.strategies:
            raise ValueError("unknown pattern strategy: "+strategy)
        strategy = strategy or pattern.strategies[int.from_bytes(digest[:4], "big") % len(pattern.strategies)]
        slots = [
            SemanticSlot("entrance_001", "entrance", "required", 1, "virtual", (), tuple(brief["style"]), status="SATISFIED"),
            SemanticSlot("circulation_001", "circulation", "required", 1, "virtual", (), tuple(brief["style"]), status="SATISFIED"),
        ]
        requested = dict(brief["requirements"])
        requested["work_surface"] = 1 if brief["preferences"].get("workSurface") else 0
        requested["seating"] = 1 if brief["preferences"].get("seating") else 0
        for requirement in pattern.requirements:
            if requirement.function in {"entrance", "circulation"}: continue
            count = requested.get(requirement.function, requirement.cardinality.preferred)
            count = min(requirement.cardinality.maximum, count)
            placement = "ceiling" if requirement.function == "lighting" else "floor"
            for index in range(1, count+1):
                rels = []
                for rel in pattern.relations.get(requirement.function, ()):
                    target = rel.target
                    if target == "strategyWall": target = self._strategy_wall(strategy, walls, scene, index)
                    rels.append(SemanticRelation(rel.kind, target, rel.hard))
                slots.append(SemanticSlot(f"{requirement.function}_{index:03d}", requirement.function,
                    requirement.priority, index, placement, tuple(rels), tuple(brief["style"])))
        if slot_namespace:
            # MapAutomation's semantic-ID grammar intentionally excludes dots.
            # A double underscore preserves an unambiguous room namespace while
            # remaining valid in Eden transport and generated SQF metadata.
            prefix=slot_namespace+"__"
            mapping={slot.id:prefix+slot.id for slot in slots}
            for slot in slots:
                slot.id=mapping[slot.id]
                slot.relations=tuple(SemanticRelation(rel.kind,mapping.get(rel.target,rel.target),rel.hard) for rel in slot.relations)
        return RoomPlan(room_id, pattern.id, pattern.room_type, tuple(brief["style"]), brief["capacity"]["people"], brief["seed"],
            self.asset_resolver.phase3["catalogVersion"], scene.region_id, "entrance_001", tuple(sorted(scene.surfaces)), strategy, slots)

    @staticmethod
    def _strategy_wall(strategy: str, walls: list[str], scene: SceneState, index: int) -> str:
        first = walls[0]
        normal = scene.surfaces[first].normal
        dot2 = lambda other: normal[0]*scene.surfaces[other].normal[0] + normal[1]*scene.surfaces[other].normal[1]
        opposite = next((w for w in walls[1:] if dot2(w) < -.9), first)
        adjacent = next((w for w in walls[1:] if abs(dot2(w)) < .1), first)
        if strategy == "parallel_beds": return first
        if strategy == "opposite_beds": return first if index % 2 else opposite
        return first if index % 2 else adjacent

    def feasibility(self, plan: RoomPlan, scene: SceneState) -> str:
        return self.preflight.evaluate(plan, scene)

    def _intent(self, slot: SemanticSlot, plan: RoomPlan, scene: SceneState) -> PlacementIntent:
        hard = ["OnSurface", "InsideRegion", "AvoidIntersection", "KeepClearance"]
        soft = []
        wall = None; reachable = False; preferred_near = None
        for rel in slot.relations:
            if rel.kind == "againstWall": wall = rel.target; hard.append("AgainstWall"); soft.append("PreferWallCenter")
            elif rel.kind == "accessibleFrom": reachable = True; hard.append("Reachable")
            elif rel.kind in {"near", "groupedWith"}: soft.append("Compact"); preferred_near = rel.target
            elif rel.kind in {"awayFrom", "mustNotBlock"}: soft.append("MaximizeCirculation")
        surface = next((k for k, v in sorted(scene.surfaces.items()) if v.type == slot.placement), None)
        if surface is None: raise ValueError("missing support surface for "+slot.placement)
        unique = lambda xs: tuple(dict.fromkeys(xs))
        return PlacementIntent(slot.id, slot.asset or "", scene.region_id, surface, wall, unique(hard), unique(soft), reachable, None,
            plan.seed + slot.index + sum(ord(c) for c in slot.function), preferred_near)

    def placement_intent(self, slot: SemanticSlot, plan: RoomPlan, scene: SceneState) -> PlacementIntent:
        """Public semantic translation boundary for orchestration layers."""
        return self._intent(slot, plan, scene)

    def validate_plan(self, plan: RoomPlan) -> list[SemanticDiagnostic]:
        return self.validator.validate(plan)

    def run(self, raw_brief: Any, scene: SceneState, *, room_id: str = "room_001") -> PipelineResult:
        plan = self.create_plan(raw_brief, scene, room_id=room_id); diagnostics = []
        feasibility = self.feasibility(plan, scene)
        if feasibility == "INFEASIBLE":
            d = SemanticDiagnostic("PATTERN_INFEASIBLE", (plan.id,), "ERROR", {"stage": "preflight"}, "use a larger room or reduce capacity")
            plan.diagnostics.append(d)
            return PipelineResult("INFEASIBLE", feasibility, plan, [], [], [d], {"operations": []})
        working = copy.deepcopy(scene); intents = []; placements = []
        ordered = sorted((s for s in plan.slots if s.placement != "virtual"), key=lambda s: ({"required":0,"preferred":1,"optional":2}[s.priority], s.id))
        for slot in ordered:
            try:
                slot.asset = self.asset_resolver.resolve(slot)
                intent = self._intent(slot, plan, working)
                result = self.solver.resolve(intent, working, dry_run=True)
            except (ValueError, KeyError) as exc:
                result = None
                failure = "UNRESOLVED_ASSET" if "UNRESOLVED_ASSET" in str(exc) else "PATTERN_INFEASIBLE"
            if result is None or result.status != "VALID":
                if slot.priority == "required":
                    d = SemanticDiagnostic(failure if result is None else "PATTERN_INFEASIBLE", (slot.id,), "ERROR",
                        {"stage": "assetResolution" if result is None else "placement", "reason": str(exc) if result is None else "NO_VALID_CANDIDATE"})
                    diagnostics.append(d); slot.status = "FAILED_REQUIRED"
                    plan.diagnostics.extend(diagnostics)
                    return PipelineResult("INFEASIBLE", feasibility, plan, intents, placements, diagnostics, {"operations": []})
                slot.status = "DROPPED_OPTIONAL" if slot.priority == "optional" else "DROPPED_PREFERRED"
                d = SemanticDiagnostic("OPTIONAL_DROPPED", (slot.id,), "INFO", {"priority": slot.priority, "reason": "NO_VALID_CANDIDATE"})
                diagnostics.append(d); continue
            tentative = copy.deepcopy(working); tentative.objects.append(result.placement)
            broken = []
            for placed in placements:
                if placed.intent.reachable:
                    ds, _ = self.solver.access.validate(tentative, self.solver._interaction_target(placed.placement), placed.placement.id)
                    broken.extend(ds)
            if broken and slot.priority != "required":
                slot.status = "DROPPED_OPTIONAL" if slot.priority == "optional" else "DROPPED_PREFERRED"
                diagnostics.append(SemanticDiagnostic("OPTIONAL_DROPPED", (slot.id,), "INFO", {"reason": "required accessibility regression"}))
                continue
            slot.status = "PLACED"; intents.append(intent); placements.append(result); working = tentative
        plan.diagnostics.extend(diagnostics)
        validation = self.validate_plan(plan); diagnostics.extend(validation); plan.diagnostics.extend(validation)
        status = "PASS" if not any(d.severity == "ERROR" for d in diagnostics) else "INFEASIBLE"
        operations = [r.scene_patch["operations"][0] for r in placements if r.scene_patch]
        return PipelineResult(status, feasibility, plan, intents, placements, diagnostics, {"operations": operations})


def build_room_context(*, base: tuple[float,float,float] = (4700.0,4700.0,10.134262), half: float = 3.5) -> SceneState:
    """A test-room reference using only Phase 3 public abstractions; shell geometry is external."""
    x,y,z = base
    surfaces = {
        "floor_1": SupportSurface("floor_1", "floor", "room_shell", (x,y,z), (0,0,1), (1,0,0), (0,1,0), (half,half)),
        "ceiling_1": SupportSurface("ceiling_1", "ceiling", "room_shell", (x,y,z+3), (0,0,-1), (1,0,0), (0,1,0), (half,half)),
        "east_wall": SupportSurface("east_wall", "wall", "room_shell", (x+half,y,z+1.5), (-1,0,0), (0,1,0), (0,0,1), (half-.2,1.5)),
        "north_wall": SupportSurface("north_wall", "wall", "room_shell", (x,y+half,z+1.5), (0,-1,0), (1,0,0), (0,0,1), (half-.2,1.5)),
        "south_wall": SupportSurface("south_wall", "wall", "room_shell", (x,y-half,z+1.5), (0,1,0), (1,0,0), (0,0,1), (half-.2,1.5)),
        "west_wall": SupportSurface("west_wall", "wall", "room_shell", (x-half,y,z+1.5), (1,0,0), (0,1,0), (0,0,1), (half-.2,1.5)),
    }
    region = [(x-half,y-half),(x+half,y-half),(x+half,y+half),(x-half,y+half)]
    assets, _ = load_phase3_assets()
    from spatial.model import ResolvedObject, SpatialTransform
    door = ResolvedObject.create("entrance_shell_001", assets["WoodenDoor"],
        SpatialTransform((x, y-half-.08, z), (0,0,0), "WORLD"))
    return SceneState("room_region_001", region, surfaces, [door], (x,y-half+.45), [])
