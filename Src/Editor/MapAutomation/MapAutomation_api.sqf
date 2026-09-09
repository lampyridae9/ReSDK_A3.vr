// All public mutations are limited to the marked probe map and owned objects.
// Transforms use Eden get3DENAttribute position/rotation (degrees), scale = 1.

function(ma_isProbe)
{
    if (!is3DEN || {isNil "golib_com_object"} || {golib_com_object isEqualTo objNull}) exitWith {false};
    private _hd = [golib_com_object,false] call golib_getHashData;
    (_hd getOrDefault ["missionName",""]) == "AI_AutomationProbe"
        && {(_hd getOrDefault ["__automationProbe",""]) == "MapAutomation-v1"}
}

function(ma_storeState)
{
    uiNamespace setVariable ["ma_revision",ma_revision];
    uiNamespace setVariable ["ma_stopped",ma_stopped];
}

function(ma_response)
{
    params ["_status",["_result",[]],["_diagnostics",[]]];
    private _r = createHashMapFromArray [
        ["status",_status],["revision",ma_revision],["sessionId",ma_session],
        ["stopped",ma_stopped],["result",_result],["diagnostics",_diagnostics]
    ];
    uiNamespace setVariable ["ma_lastResult",_r];
    diag_log text ("[MapAutomation] " + str _r);
    _r
}

function(ma_fingerprint)
{
    private _rows = (all3DENEntities select 0) apply {
        [get3DENEntityID _x,_x get3DENAttribute "position",_x get3DENAttribute "rotation",_x get3DENAttribute "init"]
    };
    _rows sort true;
    _rows
}

function(ma_owned)
{
    (all3DENEntities select 0) select {
        private _hd = [_x,false] call golib_getHashData;
        private _a = _hd getOrDefault ["__ai",[]];
        _a isEqualType [] && {count _a == 3} && {(_a select 1) isEqualTo "MapAutomation"}
    }
}

function(ma_find)
{
    params ["_id"];
    private _matches = (call ma_owned) select {
        ((([_x,false] call golib_getHashData) get "__ai") select 0) isEqualTo _id
    };
    if (count _matches == 1) then {_matches select 0} else {objNull}
}

function(ma_readObject)
{
    params ["_o"];
    private _hd = [_o,false] call golib_getHashData;
    private _props = _hd getOrDefault ["customProps",createHashMap];
    private _keys = keys _props;
    _keys sort true;
    createHashMapFromArray [
        ["semanticId",(_hd get "__ai") select 0],
        ["identity",+(_hd get "__ai")],["class",_hd get "class"],
        ["position",_o call golib_om_getPosition],["positionASL",getPosASL _o],["rotation",_o call golib_om_getRotation],
        ["vectorDir",vectorDir _o],["vectorUp",vectorUp _o],
        ["scale",getObjectScale _o],["customProps",_keys apply {[_x,_props get _x]}],
        ["edenId",get3DENEntityID _o],["rawInit",(_o get3DENAttribute "init") select 0]
    ]
}

function(ma_duplicateIdDiagnostics)
{
    private _scene = call ma_sceneData;
    private _ids = _scene apply {_x get "semanticId"};
    private _unique = _ids arrayIntersect _ids;
    private _duplicates = [];
    {
        private _id = _x;
        private _matches = _scene select {(_x get "semanticId") isEqualTo _id};
        if (count _matches > 1) then {
            _duplicates pushBack [_id,count _matches,_matches apply {_x get "edenId"}];
        };
    } forEach _unique;
    _duplicates
}

function(ma_sceneData)
{
    private _ordered = (call ma_owned) apply {
        [(([_x,false] call golib_getHashData) get "__ai") select 0,get3DENEntityID _x,_x]
    };
    _ordered sort true;
    _ordered apply {[_x select 2] call ma_readObject}
}

function(ma_inspectScene)
{
    if !(call ma_isProbe) exitWith {["FAIL",[],["NOT_PROBE_MAP"]] call ma_response};
    if (ma_ready && {!ma_busy} && {(call ma_fingerprint) isNotEqualTo ma_baseline}) then {
        ma_stopped = true;
        call ma_storeState;
    };
    private _scene = call ma_sceneData;
    private _duplicates = call ma_duplicateIdDiagnostics;
    if (_duplicates isNotEqualTo []) exitWith {
        ma_stopped = true; call ma_storeState;
        ["FAIL",_scene,[["DUPLICATE_SEMANTIC_IDS",_duplicates]]] call ma_response
    };
    ["OK",_scene,if (ma_stopped) then {["SAFE_STOP: inspect, then explicitly reconcile"]} else {[]}] call ma_response
}

function(ma_inspectObject)
{
    params ["_id"];
    if !(call ma_isProbe) exitWith {["FAIL",[],["NOT_PROBE_MAP"]] call ma_response};
    private _o = [_id] call ma_find;
    if (_o isEqualTo objNull) exitWith {["FAIL",[],["ID_MISSING_OR_DUPLICATED",_id]] call ma_response};
    ["OK",[_o] call ma_readObject] call ma_response
}

// Explicit manual acknowledgement; never called automatically after a patch failure.
function(ma_reconcile)
{
    if (!(call ma_isProbe) || {ma_busy}) exitWith {["FAIL",[],["NOT_PROBE_OR_BUSY"]] call ma_response};
    private _scene = call ma_sceneData;
    private _duplicates = call ma_duplicateIdDiagnostics;
    if (_duplicates isNotEqualTo []) exitWith {
        ["FAIL",_scene,[["DUPLICATE_SEMANTIC_IDS",_duplicates]]] call ma_response
    };
    ma_baseline = call ma_fingerprint;
    ma_revision = ma_revision + 1;
    ma_stopped = false;
    ma_engineErrors = [];
    call ma_storeState;
    ["OK",_scene,["RECONCILED_OBSERVED_STATE"]] call ma_response
}

function(ma_validId)
{
    params ["_id"];
    _id isEqualType "" && {[_id,"^[A-Za-z][A-Za-z0-9_-]{0,63}$"] call regex_isMatch}
}

function(ma_validVec)
{
    params ["_v"];
    _v isEqualType [] && {count _v == 3} && {(_v findIf {!(_x isEqualType 0) || {!finite _x}}) == -1}
}

// GOLib reads global inspector state. It cannot be shadowed with SQF private.
// Call these only inside the unscheduled isNil blocks below.
function(ma_saveInspectorContext)
{
    private _saved = [inspector_allSelectedObjects,inspector_otherObjects,golib_internal_lastBatchUpdateMode];
    inspector_allSelectedObjects = _this;
    inspector_otherObjects = [];
    golib_internal_lastBatchUpdateMode = [];
    _saved
}

function(ma_restoreInspectorContext)
{
    inspector_allSelectedObjects = _this select 0;
    inspector_otherObjects = _this select 1;
    golib_internal_lastBatchUpdateMode = _this select 2;
}

function(ma_writeHash)
{
    params ["_o","_hd"];
    isNil {
        private _context = [_o] call ma_saveInspectorContext;
        [_o,_hd,false] call golib_setHashData;
        _context call ma_restoreInspectorContext;
    };
}

function(ma_checkTransform)
{
    params ["_o","_pos","_rot"];
    private _diff = [];
    private _p = _o call golib_om_getPosition;
    private _r = _o call golib_om_getRotation;
    if ((_p distance _pos) > 0.01) then {_diff pushBack ["POSITION",_pos,_p]};
    for "_i" from 0 to 2 do {
        private _d = abs (((((_r select _i) - (_rot select _i)) mod 360) + 540) mod 360 - 180);
        if (_d > 0.05) then {_diff pushBack ["ROTATION",_i,_rot select _i,_r select _i]};
    };
    if (abs ((getObjectScale _o) - 1) > 0.0001) then {_diff pushBack ["SCALE",getObjectScale _o]};
    _diff
}

function(ma_putTransform)
{
    params ["_o","_pos","_rot"];
    isNil {
        private _context = [_o] call ma_saveInspectorContext;
        [_o,_pos,false] call golib_om_setPosition;
        [_o,_rot,false] call golib_om_setRotation;
        _context call ma_restoreInspectorContext;
    };
    [_o,_pos,_rot] call ma_checkTransform
}

function(ma_classDiagnostics)
{
    params ["_class"];
    if !(_class in ma_allowedClasses) exitWith {["CLASS_NOT_IN_PROBE_ALLOWLIST",_class]};
    if !([_class] call oop_isImplementClass) exitWith {["CLASS_NOT_LOADED",_class]};
    if ([_class,"InterfaceClass"] call goasm_attributes_hasAttributeClass) exitWith {["CLASS_NOT_PLACEABLE",_class]};
    if (([_class,false] call golib_om_getConfigByGameObject) == "") exitWith {["MODEL_CONFIG_UNAVAILABLE",_class]};
    []
}

// Private executor: [operation, args] -> diagnostics. No string is compiled.
function(ma_execute)
{
    params ["_op","_args"];
    if !(_args isEqualType []) exitWith {["ARGUMENTS_MUST_BE_ARRAY"]};
    if !(_op in ["create","delete","setTransform","setProperties"]) exitWith {["UNKNOWN_OPERATION",_op]};
    private _id = _args param [0,""];
    if !([_id] call ma_validId) exitWith {["INVALID_ID"]};
    private _o = [_id] call ma_find;
    if (_op == "create") exitWith {
        if (count _args != 6) exitWith {["CREATE_EXPECTS_ID_CLASS_POSITION_ROTATION_SCALE_PARENT"]};
        _args params ["_id","_class","_pos","_rot","_scale","_parent"];
        if (((call ma_sceneData) findIf {(_x get "semanticId") isEqualTo _id}) != -1) exitWith {["ID_EXISTS",_id]};
        if !(_class isEqualType "") exitWith {["INVALID_CLASS"]};
        private _err = [_class] call ma_classDiagnostics;
        if (_err isNotEqualTo []) exitWith {_err};
        if !(_scale isEqualTo 1) exitWith {["UNSUPPORTED_SCALE",_scale,"Only scale=1 is supported"]};
        if (!([_pos] call ma_validVec) || {!([_rot] call ma_validVec)}) exitWith {["INVALID_TRANSFORM"]};
        if !(_parent isEqualType "" && {_parent == "" || {[_parent] call ma_validId}}) exitWith {["INVALID_PARENT"]};
        isNil {
            private _context = [objNull] call ma_saveInspectorContext;
            _o = [_class,_pos,_rot] call golib_om_createObject;
            _context call ma_restoreInspectorContext;
        };
        if (isNil "_o") exitWith {["CREATE_RETURNED_NIL"]};
        if (_o isEqualTo objNull) exitWith {["CREATE_FAILED"]};
        private _hd = [_o,false] call golib_getHashData;
        _hd set ["__ai",[_id,"MapAutomation",_parent]];
        [_o,_hd] call ma_writeHash;
        _err = [_o,_pos,_rot] call ma_checkTransform;
        private _actual = [_o] call ma_readObject;
        if ((_actual get "identity") isNotEqualTo [_id,"MapAutomation",_parent]) then {_err pushBack ["IDENTITY_READBACK"]};
        if ((_actual get "class") isNotEqualTo _class) then {_err pushBack ["CLASS_READBACK"]};
        _err
    };
    if (_o isEqualTo objNull) exitWith {["ID_MISSING_OR_DUPLICATED",_id]};
    if (_op == "delete") exitWith {
        if (count _args != 1) exitWith {["DELETE_EXPECTS_ID"]};
        delete3DENEntities [_o];
        if (_o in (all3DENEntities select 0)) then {["DELETE_READBACK_FAILED",_id]} else {[]}
    };
    if (_op == "setTransform") exitWith {
        if (count _args != 4) exitWith {["TRANSFORM_EXPECTS_ID_POSITION_ROTATION_SCALE"]};
        _args params ["_id","_pos","_rot","_scale"];
        if !(_scale isEqualTo 1) exitWith {["UNSUPPORTED_SCALE",_scale,"Only scale=1 is supported"]};
        if (!([_pos] call ma_validVec) || {!([_rot] call ma_validVec)}) exitWith {["INVALID_TRANSFORM"]};
        private _identity = +(([_o,false] call golib_getHashData) get "__ai");
        private _err = [_o,_pos,_rot] call ma_putTransform;
        if ((([_o,false] call golib_getHashData) get "__ai") isNotEqualTo _identity) then {_err pushBack ["IDENTITY_CHANGED"]};
        _err
    };
    if (count _args != 2) exitWith {["PROPERTIES_EXPECTS_ID_PAIRS"]};
    private _pairs = _args select 1;
    if !(_pairs isEqualType []) exitWith {["PROPERTIES_MUST_BE_PAIRS"]};
    // Deliberately narrow: model, initCode, mark, links, __ai cannot be injected.
    private _invalid = _pairs findIf {
        !(_x isEqualType []) || {count _x != 2} || {!((_x select 0) in ["name","desc"])} || {!((_x select 1) isEqualType "")}
    };
    if (_invalid != -1) exitWith {["PROPERTY_NOT_ALLOWED","Only string name/desc supported"]};
    private _keys = _pairs apply {_x select 0};
    if (count (_keys arrayIntersect _keys) != count _keys) exitWith {["DUPLICATE_PROPERTY"]};
    private _hd = [_o,false] call golib_getHashData;
    private _props = _hd get "customProps";
    { _props set _x; } forEach _pairs;
    [_o,_hd] call ma_writeHash;
    private _actual = ([_o,false] call golib_getHashData) get "customProps";
    private _errors = [];
    { if ((_actual getOrDefault [_x select 0,""]) isNotEqualTo (_x select 1)) then {_errors pushBack ["PROPERTY_READBACK",_x]}; } forEach _pairs;
    _errors
}

// One confirmed patch advances revision once. Failure preserves revision and stops.
function(ma_applyPatch)
{
    params ["_operations","_expectedRevision"];
    if (!(call ma_isProbe) || {!ma_ready}) exitWith {["FAIL",[],["NOT_READY_OR_NOT_PROBE"]] call ma_response};
    if (ma_busy || {ma_stopped}) exitWith {["FAIL",call ma_sceneData,["BUSY_OR_SAFE_STOP"]] call ma_response};
    if !(_expectedRevision isEqualTo ma_revision) exitWith {
        ["FAIL",call ma_sceneData,[["REVISION_MISMATCH",_expectedRevision,ma_revision]]] call ma_response
    };
    if ((call ma_fingerprint) isNotEqualTo ma_baseline) exitWith {
        ma_stopped = true; call ma_storeState;
        ["FAIL",call ma_sceneData,["SCENE_CHANGED_OUTSIDE_AUTOMATION"]] call ma_response
    };
    if !(_operations isEqualType [] && {count _operations > 0} && {count _operations <= 32}) exitWith {
        ["FAIL",[],["PATCH_EXPECTS_1_TO_32_OPERATIONS"]] call ma_response
    };
    private _before = call ma_sceneData;
    uiNamespace setVariable ["ma_beforePatch",_before];
    private _errors = [];
    ma_busy = true;
    ma_engineErrors = [];
    // Persist a stop BEFORE calling engine code. An SQF engine error may not throw.
    ma_stopped = true; call ma_storeState;
    ["MapAutomation patch", "Probe: typed operations", ""] collect3DENHistory {
        {
            if !(_x isEqualType [] && {count _x == 2}) exitWith {_errors = ["INVALID_OPERATION",_forEachIndex]};
            private _err = _x call ma_execute;
            if (ma_engineErrors isNotEqualTo []) exitWith {_errors = ["ENGINE_ERROR_SAFE_STOP",_forEachIndex]};
            if (isNil "_err") exitWith {_errors = ["NO_OPERATION_RESULT",_forEachIndex]};
            if (_err isNotEqualTo []) exitWith {_errors = ["OPERATION_FAILED",_forEachIndex,_err]};
        } forEach _operations;
    };
    private _actual = call ma_sceneData;
    if (ma_engineErrors isNotEqualTo []) then {_errors pushBack ["ENGINE_SCRIPT_ERRORS",ma_engineErrors]};
    ma_baseline = call ma_fingerprint;
    ma_busy = false;
    if (_errors isNotEqualTo []) exitWith {
        // Include all Eden Object entities, even if creation failed before __ai was written.
        ["FAIL",createHashMapFromArray [["before",_before],["actual",_actual],["edenState",ma_baseline]],_errors] call ma_response
    };
    ma_revision = ma_revision + 1;
    ma_stopped = false; call ma_storeState;
    ["OK",_actual,["READBACK_CONFIRMED"]] call ma_response
}

function(ma_create) { [[ ["create",_this] ],ma_revision] call ma_applyPatch }
function(ma_delete) { [[ ["delete",_this] ],ma_revision] call ma_applyPatch }
function(ma_setTransform) { [[ ["setTransform",_this] ],ma_revision] call ma_applyPatch }
function(ma_setProperties) { [[ ["setProperties",_this] ],ma_revision] call ma_applyPatch }

function(ma_getCapabilities)
{
    ["OK",createHashMapFromArray [
        ["protocolVersion",1],["internalOnly",false],["transport",true],
        ["classes",ma_allowedClasses],["scale",1],["properties",["name","desc"]],
        ["transformSpace","Eden position attribute; rotation degrees"],
        ["classDiagnostics",ma_allowedClasses apply {[_x,[_x] call ma_classDiagnostics]}],
        ["transportKind","FileManager JSON queue"],["engineStatus","READY_IN_PROBE"]
    ]] call ma_response
}

function(ma_nextCopyId)
{
    private _counter = uiNamespace getVariable ["ma_idCounter",0];
    private _newId = "";
    while {_newId == "" || {((call ma_sceneData) findIf {(_x get "semanticId") isEqualTo _newId}) != -1}} do {
        _counter = _counter + 1;
        _newId = format ["copy_%1",_counter];
    };
    uiNamespace setVariable ["ma_idCounter",_counter];
    _newId
}

function(ma_repairDuplicateIds)
{
    private _repairs = [];
    private _duplicates = call ma_duplicateIdDiagnostics;
    {
        _x params ["_duplicateId"];
        private _matches = (call ma_owned) select {
            ((([_x,false] call golib_getHashData) get "__ai") select 0) isEqualTo _duplicateId
        };
        private _ordered = _matches apply {[get3DENEntityID _x,_x]};
        _ordered sort true;
        for "_i" from 1 to (count _ordered - 1) do {
            private _o = (_ordered select _i) select 1;
            private _hd = [_o,false] call golib_getHashData;
            private _identity = +(_hd get "__ai");
            private _newId = call ma_nextCopyId;
            _identity set [0,_newId];
            _hd set ["__ai",_identity];
            [_o,_hd] call ma_writeHash;
            _repairs pushBack [_duplicateId,_newId,get3DENEntityID _o];
        };
    } forEach _duplicates;
    _repairs
}

function(ma_onHistoryIdentity)
{
    uiSleep 0.2;
    if !(call ma_isProbe) exitWith {};
    private _repairs = call ma_repairDuplicateIds;
    ma_stopped = true;
    call ma_storeState;
    ["STOPPED",call ma_sceneData,[
        ["HISTORY_IDENTITY_CHECK",if (_repairs isEqualTo []) then {"UNIQUE"} else {"REPAIRED"}],
        ["repairs",_repairs],["duplicates",call ma_duplicateIdDiagnostics],
        "RECONCILE_REQUIRED"
    ]] call ma_response;
}

function(ma_onEntityAddedIdentity)
{
    params ["_entity"];
    uiSleep 0.15;
    if (ma_suppressHistoryIdentityRepair) exitWith {};
    if (!(call ma_isProbe) || {!(_entity isEqualType objNull)} || {!(_entity in (all3DENEntities select 0))}) exitWith {};
    private _hd = [_entity,false] call golib_getHashData;
    private _identity = _hd getOrDefault ["__ai",[]];
    if !(_identity isEqualType [] && {count _identity == 3} && {(_identity select 1) == "MapAutomation"}) exitWith {};
    private _repairs = call ma_repairDuplicateIds;
    if (_repairs isEqualTo []) exitWith {};
    ma_pasteSerial = ma_pasteSerial + 1;
    ma_stopped = true;
    call ma_storeState;
    ["STOPPED",call ma_sceneData,[
        ["ENTITY_ADDED_DUPLICATE_IDS_REPAIRED",_repairs],
        ["duplicates",call ma_duplicateIdDiagnostics],"RECONCILE_REQUIRED"
    ]] call ma_response;
}

function(ma_onPaste)
{
    params ["_entities"];
    uiSleep 0.1;
    if !(call ma_isProbe) exitWith {};
    if (ma_suppressHistoryIdentityRepair) exitWith {};
    ma_stopped = true; call ma_storeState;
    ma_pasteSerial = ma_pasteSerial + 1;
    private _errors = [];
    private _assigned = [];
    {
        if !(_x isEqualType objNull) then {continue};
        private _hd = [_x,false] call golib_getHashData;
        private _a = _hd getOrDefault ["__ai",[]];
        if !(_a isEqualType [] && {count _a == 3} && {(_a select 1) == "MapAutomation"}) then {continue};
        private _sourceId = _a select 0;
        private _sameId = (call ma_sceneData) select {(_x get "semanticId") isEqualTo _sourceId};
        // OnEditableEntityAdded may already have repaired this paste before OnPaste resumes.
        if (count _sameId <= 1) then {continue};
        private _newId = call ma_nextCopyId;
        _hd set ["__ai",[_newId,"MapAutomation",_a select 2]];
        [_x,_hd] call ma_writeHash;
        _assigned pushBack [_sourceId,_newId,get3DENEntityID _x];
        if ((([_x,false] call golib_getHashData) get "__ai" select 0) != _newId) then {_errors pushBack ["PASTE_ID_READBACK",_newId]};
    } forEach _entities;
    private _duplicates = call ma_duplicateIdDiagnostics;
    if (_duplicates isNotEqualTo []) then {_errors pushBack ["DUPLICATE_SEMANTIC_IDS",_duplicates]};
    ["STOPPED",call ma_sceneData,[["PASTE_IDS_REASSIGNED",_assigned],["errors",_errors],"RECONCILE_REQUIRED"]] call ma_response;
}
