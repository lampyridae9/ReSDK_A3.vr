// All destructive tests require the prepared marker and exact probe map name.
// PASS is emitted only by the engine harness after actual comparisons.

function(ma_test_record)
{
    params ["_name","_result"];
    private _path = "Tools\MapAutomation\artifacts\" + _name + ".sqfdata";
    private _text = str _result;
    private _written = [_path,_text] call file_write;
    if (!_written || {([_path] call file_read) isNotEqualTo _text}) then {
        diag_log text ("[MapAutomation] REPORT_WRITE_FAILED " + _path + "; use RPT / uiNamespace ma_lastResult");
    };
    diag_log text format ["[MapAutomation] TEST %1: %2",_name,_result];
    _result
}

function(ma_test_compare)
{
    params ["_expected","_actual"];
    private _errors = [];
    private _ids = _actual apply {_x get "semanticId"};
    if (count _actual != count _expected) then {_errors pushBack ["OBJECT_COUNT",count _expected,count _actual]};
    if (count (_ids arrayIntersect _ids) != count _ids) then {_errors pushBack ["DUPLICATE_IDS"]};
    {
        private _e = _x;
        private _id = _e get "semanticId";
        private _i = _actual findIf {(_x get "semanticId") isEqualTo _id};
        if (_i == -1) then {_errors pushBack ["MISSING_ID",_id]; continue};
        private _a = _actual select _i;
        {
            if ((_e get _x) isNotEqualTo (_a get _x)) then {_errors pushBack [_id,_x,_e get _x,_a get _x]};
        } forEach ["class","identity","customProps"];
        if (((_e get "position") distance (_a get "position")) > 0.01) then {
            _errors pushBack [_id,"position",_e get "position",_a get "position"];
        };
        {
            if (((_e get _x) distance (_a get _x)) > 0.001) then {_errors pushBack [_id,_x,_e get _x,_a get _x]};
        } forEach ["vectorDir","vectorUp"];
        if (abs ((_a get "scale") - 1) > 0.0001) then {_errors pushBack [_id,"scale",_a get "scale"]};
    } forEach _expected;
    _errors
}

function(ma_test_finish)
{
    params ["_name","_errors"];
    if (_errors isNotEqualTo []) then {ma_stopped = true; call ma_storeState};
    private _r = [if (_errors isEqualTo []) then {"PASS"} else {"FAIL"},call ma_sceneData,_errors] call ma_response;
    [_name,_r] call ma_test_record;
    _r
}

function(ma_test_smoke)
{
    if (!canSuspend) exitWith {["FAIL",[],["USE [] spawn ma_test_smoke"]] call ma_response};
    if (!(call ma_isProbe) || {!ma_ready} || {ma_busy} || {ma_stopped}) exitWith {
        ["FAIL",[],["NOT_READY_OR_SAFE_STOP"]] call ma_response
    };
    if ((call ma_owned) isNotEqualTo []) exitWith {["FAIL",call ma_sceneData,["PROBE_NOT_EMPTY: run ma_test_reset explicitly"]] call ma_response};
    private _errors = [];
    { private _e = [_x] call ma_classDiagnostics; if (_e isNotEqualTo []) then {_errors pushBack _e}; } forEach ma_allowedClasses;
    if (_errors isNotEqualTo []) exitWith {["smoke",_errors] call ma_test_finish};
    private _r = [[
        ["create",["floor_1","BigConcreteFloor",[4000,4000,10],[0,0,0],1,""]],
        ["create",["wall_1","ConcreteGreenWall",[4008,4000,10],[0,0,90],1,""]],
        ["create",["arch_1","WoodenArch",[4000,4008,10],[0,0,180],1,""]]
    ],ma_revision] call ma_applyPatch;
    if ((_r get "status") != "OK") exitWith {["smoke",[_r]] call ma_test_finish};
    uiSleep 0.2;
    _r = ["wall_1",[4008.25,4000.5,10.25],[5,10,95],1] call ma_setTransform;
    if ((_r get "status") != "OK") exitWith {["smoke",[_r]] call ma_test_finish};
    _r = ["wall_1",[["name","Проверка стены"],["desc","Probe: quoted ""text"" remains data"]]] call ma_setProperties;
    if ((_r get "status") != "OK") exitWith {["smoke",[_r]] call ma_test_finish};
    private _expected = call ma_sceneData;
    uiSleep 0.3;
    _errors = [_expected,call ma_sceneData] call ma_test_compare;
    // Independently compare the requested transforms, not only two snapshots.
    {
        _x params ["_id","_p","_rot"];
        private _o = [_id] call ma_find;
        if (_o isEqualTo objNull) then {_errors pushBack ["MISSING",_id]} else {
            _errors append ([_o,_p,_rot] call ma_checkTransform);
        };
    } forEach [
        ["floor_1",[4000,4000,10],[0,0,0]],
        ["wall_1",[4008.25,4000.5,10.25],[5,10,95]],
        ["arch_1",[4000,4008,10],[0,0,180]]
    ];
    uiNamespace setVariable ["ma_smokePassed",_errors isEqualTo []];
    ["smoke",_errors] call ma_test_finish
}

function(ma_test_history)
{
    if (!canSuspend || {!(call ma_isProbe)} || {ma_busy} || {ma_stopped}) exitWith {
        ["FAIL",[],["USE_SPAWN_IN_READY_PROBE"]] call ma_response
    };
    private _before = call ma_sceneData;
    private _r = ["history_1","WoodenArch",[4020,4000,10],[0,0,35],1,""] call ma_create;
    if ((_r get "status") != "OK") exitWith {["history",[_r]] call ma_test_finish};
    uiSleep 0.3;
    private _created = call ma_sceneData;
    do3DENAction "Undo";
    uiSleep 0.5;
    private _errors = [_before,call ma_sceneData] call ma_test_compare;
    if (_errors isNotEqualTo []) exitWith {["history_create_undo",_errors] call ma_test_finish};
    do3DENAction "Redo";
    uiSleep 0.5;
    _errors = [_created,call ma_sceneData] call ma_test_compare;
    if (_errors isNotEqualTo []) exitWith {["history_create_redo",_errors] call ma_test_finish};
    call ma_reconcile;
    _r = ["history_1",[4021,4002,10.5],[5,0,65],1] call ma_setTransform;
    if ((_r get "status") != "OK") exitWith {["history_move",[_r]] call ma_test_finish};
    uiSleep 0.3;
    private _moved = call ma_sceneData;
    do3DENAction "Undo";
    uiSleep 0.5;
    _errors = [_created,call ma_sceneData] call ma_test_compare;
    if (_errors isNotEqualTo []) exitWith {["history_move_undo",_errors] call ma_test_finish};
    do3DENAction "Redo";
    uiSleep 0.5;
    _errors = [_moved,call ma_sceneData] call ma_test_compare;
    if (_errors isNotEqualTo []) exitWith {["history_move_redo",_errors] call ma_test_finish};
    call ma_reconcile;
    _r = ["history_1"] call ma_delete;
    if ((_r get "status") != "OK") then {_errors pushBack _r};
    ["history",_errors] call ma_test_finish
}

function(ma_test_copyPaste)
{
    if (!canSuspend || {!(call ma_isProbe)} || {ma_busy} || {ma_stopped}) exitWith {
        ["FAIL",[],["USE_SPAWN_IN_READY_RECONCILED_PROBE"]] call ma_response
    };
    private _original = ["floor_1"] call ma_find;
    if (_original isEqualTo objNull) exitWith {["FAIL",[],["FLOOR_1_MISSING"]] call ma_response};
    private _before = call ma_sceneData;
    private _beforeCount = count _before;
    private _originalEdenId = get3DENEntityID _original;
    private _identityA = +(([_original,false] call golib_getHashData) get "__ai");
    private _serial = ma_pasteSerial;
    private _edenCountBefore = count (all3DENEntities select 0);
    private _edenIdsBefore = (all3DENEntities select 0) apply {get3DENEntityID _x};
    private _oldSelection = call golib_getSelectedObjects;
    [_original,false] call golib_setSelectedObjects;
    do3DENAction "CopyUnit";
    // Action IDs differ between Eden builds. Try only known native paste actions and stop
    // immediately after an entity is actually added; OnPaste performs identity reassignment.
    uiSleep 0.1;
    private _pasteActionsTried = [];
    private _pasteActionUsed = "";
    call {
        scopeName "ma_copyPaste_actionSearch";
        {
            _pasteActionsTried pushBack _x;
            do3DENAction _x;
            uiSleep 0.3;
            if (count (all3DENEntities select 0) > _edenCountBefore) then {
                _pasteActionUsed = _x;
                breakOut "ma_copyPaste_actionSearch";
            };
        } forEach ["Paste","PasteUnitOrig","PasteItems"];
    };
    private _deadline = diag_tickTime + 5;
    waitUntil {uiSleep 0.1; ma_pasteSerial > _serial || {diag_tickTime > _deadline}};
    [_oldSelection,false] call golib_setSelectedObjects;
    private _errors = [];
    if (ma_pasteSerial <= _serial) then {_errors pushBack ["ONPASTE_TIMEOUT",_pasteActionsTried]};
    if (_pasteActionUsed == "") then {_errors pushBack ["NO_EDEN_PASTE_ACTION_CREATED_ENTITY",_pasteActionsTried]};
    private _afterPaste = call ma_sceneData;
    if (count _afterPaste != _beforeCount + 1) then {_errors pushBack ["PASTE_OBJECT_COUNT",_beforeCount + 1,count _afterPaste]};
    private _originalAfter = [_identityA select 0] call ma_find;
    if (_originalAfter isEqualTo objNull || {get3DENEntityID _originalAfter != _originalEdenId}) then {
        _errors pushBack ["ORIGINAL_IDENTITY_A_NOT_PRESERVED",_identityA select 0,_originalEdenId]
    };
    private _copies = _afterPaste select {(_x get "edenId") != _originalEdenId && {(_x get "semanticId") find "copy_" == 0}};
    private _identityB = if (count _copies == 1) then {(_copies select 0) get "semanticId"} else {""};
    if (_identityB == "" || {_identityB == (_identityA select 0)}) then {_errors pushBack ["COPY_IDENTITY_B_INVALID",_identityB]};
    private _duplicates = call ma_duplicateIdDiagnostics;
    if (_duplicates isNotEqualTo []) then {_errors pushBack ["DUPLICATE_AFTER_PASTE",_duplicates]};
    if (_errors isNotEqualTo []) exitWith {
        private _addedByTest = (all3DENEntities select 0) select {!((get3DENEntityID _x) in _edenIdsBefore)};
        if (_addedByTest isNotEqualTo []) then {
            private _removedIds = _addedByTest apply {get3DENEntityID _x};
            delete3DENEntities _addedByTest;
            uiSleep 0.2;
            _errors pushBack ["FAILED_TEST_CLEANUP",_removedIds];
        };
        ["copy_paste",_errors] call ma_test_finish
    };
    call ma_reconcile;
    ma_suppressHistoryIdentityRepair = true;
    private _undoSteps = 0;
    while {count (all3DENEntities select 0) > _edenCountBefore && {_undoSteps < 6}} do {
        do3DENAction "Undo";
        _undoSteps = _undoSteps + 1;
        uiSleep 0.6;
    };
    private _afterUndo = call ma_sceneData;
    if (count _afterUndo != _beforeCount) then {_errors pushBack ["UNDO_OBJECT_COUNT",_beforeCount,count _afterUndo]};
    if ((call ma_duplicateIdDiagnostics) isNotEqualTo []) then {_errors pushBack ["DUPLICATE_AFTER_UNDO",call ma_duplicateIdDiagnostics]};
    if (([_identityA select 0] call ma_find) isEqualTo objNull) then {_errors pushBack ["ORIGINAL_A_MISSING_AFTER_UNDO"]};
    call ma_reconcile;
    for "_i" from 1 to _undoSteps do {
        do3DENAction "Redo";
        uiSleep 0.6;
    };
    ma_suppressHistoryIdentityRepair = false;
    call ma_repairDuplicateIds;
    private _afterRedo = call ma_sceneData;
    if (count _afterRedo != _beforeCount + 1) then {_errors pushBack ["REDO_OBJECT_COUNT",_beforeCount + 1,count _afterRedo]};
    if ((call ma_duplicateIdDiagnostics) isNotEqualTo []) then {_errors pushBack ["DUPLICATE_AFTER_REDO",call ma_duplicateIdDiagnostics]};
    if (([_identityA select 0] call ma_find) isEqualTo objNull) then {_errors pushBack ["ORIGINAL_A_MISSING_AFTER_REDO"]};
    if (([_identityB] call ma_find) isEqualTo objNull) then {
        private _redoCopies = _afterRedo select {
            (_x get "edenId") != _originalEdenId && {(_x get "semanticId") find "copy_" == 0}
        };
        if (count _redoCopies == 1) then {
            _identityB = (_redoCopies select 0) get "semanticId";
        } else {
            _errors pushBack ["COPY_ID_MISSING_AFTER_REDO",_identityB,_redoCopies apply {_x get "semanticId"}]
        };
    };
    if (_errors isNotEqualTo []) exitWith {["copy_paste",_errors] call ma_test_finish};
    call ma_reconcile;
    uiNamespace setVariable ["ma_copyPastePending",[_afterRedo,_identityA select 0,_identityB]];
    ["copy_paste_pre_reload",createHashMapFromArray [
        ["status","PASS"],["originalId",_identityA select 0],["copyId",_identityB],
        ["pasteAction",_pasteActionUsed],["undoSteps",_undoSteps],
        ["duplicates",call ma_duplicateIdDiagnostics],["scene",_afterRedo]
    ]] call ma_test_record;
    [true] call ma_test_roundTrip
}

function(ma_test_finishCopyPasteContext)
{
    params ["_pending"];
    _pending params ["_expected","_identityA","_identityB"];
    uiNamespace setVariable ["ma_copyPastePending",[]];
    private _errors = [_expected,call ma_sceneData] call ma_test_compare;
    private _duplicates = call ma_duplicateIdDiagnostics;
    if (_duplicates isNotEqualTo []) then {_errors pushBack ["DUPLICATE_AFTER_SAVE_LOAD",_duplicates]};
    if (([_identityA] call ma_find) isEqualTo objNull) then {_errors pushBack ["ORIGINAL_A_MISSING_AFTER_SAVE_LOAD",_identityA]};
    if (([_identityB] call ma_find) isEqualTo objNull) then {_errors pushBack ["COPY_B_MISSING_AFTER_SAVE_LOAD",_identityB]};
    ["copy_paste",_errors] call ma_test_finish;
}

function(ma_test_resumeCopyPaste)
{
    uiSleep 0.8;
    private _pending = uiNamespace getVariable ["ma_copyPastePending",[]];
    if (_pending isEqualTo [] || {!(call ma_isProbe)}) exitWith {};
    [_pending] call ma_test_finishCopyPasteContext;
}

function(ma_test_failure)
{
    if (!(call ma_isProbe) || {ma_busy} || {ma_stopped}) exitWith {["FAIL",[],["PROBE_NOT_READY"]] call ma_response};
    private _rev = ma_revision;
    private _r = [[
        ["create",["failure_1","WoodenArch",[4030,4000,10],[0,0,0],1,""]],
        ["setTransform",["failure_1",[4031,4000,10],[0,0,45],1]],
        ["setTransform",["failure_1",[4031,4000,10],[0,0,45],2]]
    ],ma_revision] call ma_applyPatch;
    private _errors = [];
    if ((_r get "status") != "FAIL" || {!ma_stopped} || {ma_revision != _rev}) then {_errors pushBack ["FAILURE_NOT_STOPPED",_r]};
    private _o = ["failure_1"] call ma_find;
    if (_o isEqualTo objNull) then {_errors pushBack ["PARTIAL_STATE_NOT_PRESENT"]} else {
        _errors append ([_o,[4031,4000,10],[0,0,45]] call ma_checkTransform);
    };
    private _known = call ma_fingerprint;
    private _blocked = ["failure_1"] call ma_delete;
    if ((_blocked get "status") != "FAIL" || {(call ma_fingerprint) isNotEqualTo _known}) then {_errors pushBack ["SAFE_STOP_BYPASSED"]};
    // A PASS here means the failure contract worked, NOT that the patch passed.
    private _result = [if (_errors isEqualTo []) then {"PASS"} else {"FAIL"},
        createHashMapFromArray [["failedPatch",_r],["blockedNextMutation",_blocked],["actual",call ma_sceneData]],
        _errors + ["EXPECTED_SAFE_STOP: no rollback; call ma_reconcile explicitly after inspection"]] call ma_response;
    ["failure",_result] call ma_test_record
}

function(ma_test_roundTrip)
{
    params [["_allowVerifiedExistingScene",false]];
    if (!canSuspend || {!(call ma_isProbe)} || {ma_busy} || {ma_stopped}) exitWith {
        ["FAIL",[],["USE_SPAWN_IN_READY_PROBE"]] call ma_response
    };
    if (!(uiNamespace getVariable ["ma_smokePassed",false]) && {!_allowVerifiedExistingScene}) exitWith {["FAIL",[],["SMOKE_MUST_PASS_FIRST"]] call ma_response};
    if ((call ma_fingerprint) isNotEqualTo ma_baseline) exitWith {
        ma_stopped = true; call ma_storeState;
        ["FAIL",call ma_sceneData,["SCENE_CHANGED"]] call ma_response
    };
    private _expected = call ma_sceneData;
    ma_busy = true;
    ma_engineErrors = [];
    private _serial = ma_saveSerial;
    do3DENAction "MissionSave";
    private _deadline = diag_tickTime + 15;
    waitUntil {uiSleep 0.1; ma_saveSerial > _serial || {diag_tickTime > _deadline}};
    if (ma_saveSerial <= _serial) exitWith {
        ma_busy = false; ["roundtrip",["MISSION_SAVE_EVENT_TIMEOUT"]] call ma_test_finish
    };
    uiSleep 0.5;
    [false] call mm_saveCurrentMapToFile;
    private _path = core_path_maps + "/" + ma_mapName + core_path_binarizedMapFileExt;
    private _source = ["mission.sqm"] call file_read;
    private _saved = [_path] call file_read;
    if (_source == "" || {_saved isNotEqualTo _source}) exitWith {
        ma_busy = false; ["roundtrip",["SAVE_COPY_READBACK_FAILED",_path]] call ma_test_finish
    };
    private _errors = [_expected,call ma_sceneData] call ma_test_compare;
    if (_errors isNotEqualTo []) exitWith {ma_busy = false; ["roundtrip",_errors] call ma_test_finish};
    // MapsManager waits for Eden's mission.sqm lock before overwriting it.
    // Callback state is global because the callback may run on a later frame.
    // ma_busy prevents another automation round trip from sharing this state.
    ma_loadCopyState = "PENDING";
    private _lockedBefore = ["mission.sqm"] call file_isLocked;
    ["LOAD_COPY_PENDING",[],[["destinationLocked",_lockedBefore],["source",_path]]] call ma_response;
    private _accepted = [_path,"mission.sqm",true,{
        params ["_copied"];
        ma_loadCopyState = if (_copied) then {"COPIED"} else {"COPY_FAILED"};
    },{
        ma_loadCopyState = "LOCK_TIMEOUT";
    }] call file_copyAsync;
    if (!_accepted) exitWith {
        ma_busy = false; ["roundtrip",["LOAD_COPY_REJECTED",_path]] call ma_test_finish
    };
    private _copyDeadline = diag_tickTime + file_const_defaultAsyncWriteTimeout + 5;
    waitUntil {uiSleep 0.1; ma_loadCopyState != "PENDING" || {diag_tickTime > _copyDeadline}};
    if (ma_loadCopyState != "COPIED") exitWith {
        ma_busy = false;
        ["roundtrip",["LOAD_COPY_FAILED",ma_loadCopyState,
            ["destinationLockedBefore",_lockedBefore],
            ["destinationLockedNow",["mission.sqm"] call file_isLocked],
            ["source",_path]]] call ma_test_finish
    };
    // A callback alone is not evidence that the destination contains the saved map.
    private _loadedText = ["mission.sqm"] call file_read;
    if (_loadedText == "" || {_loadedText isNotEqualTo _saved}) exitWith {
        ma_busy = false; ["roundtrip",["LOAD_COPY_READBACK_FAILED",_path]] call ma_test_finish
    };
    _errors = [_expected,call ma_sceneData] call ma_test_compare;
    if (ma_engineErrors isNotEqualTo []) then {_errors pushBack ["ENGINE_SCRIPT_ERRORS",ma_engineErrors]};
    if (!(call ma_isProbe) || {(call ma_fingerprint) isNotEqualTo ma_baseline}) then {
        _errors pushBack ["SCENE_CHANGED_DURING_LOAD_COPY"];
    };
    if (_errors isNotEqualTo []) exitWith {ma_busy = false; ["roundtrip",_errors] call ma_test_finish};
    // Carry an optional Copy/Paste acceptance context in the same continuation.
    // Separate spawned continuations race after reload: the generic round-trip used
    // to clear ma_copyPastePending before the Copy/Paste verifier could read it.
    private _copyPasteContext = uiNamespace getVariable ["ma_copyPastePending",[]];
    uiNamespace setVariable ["ma_roundTripPending",[_expected,ma_session,ma_revision,_copyPasteContext]];
    ma_busy = false;
    ["WAITING_FOR_RELOAD",[],["Continuation runs on onEditorLoaded"]] call ma_response;
    [false] spawn Core_reloadEditorFull;
}

function(ma_test_resumeRoundTrip)
{
    uiSleep 0.5;
    private _pending = uiNamespace getVariable ["ma_roundTripPending",[]];
    if (_pending isEqualTo [] || {!(call ma_isProbe)}) exitWith {};
    _pending params ["_expected","_session","_revision",["_copyPasteContext",[]]];
    uiNamespace setVariable ["ma_roundTripPending",[]];
    private _errors = [_expected,call ma_sceneData] call ma_test_compare;
    if (_session != ma_session || {_revision != ma_revision}) then {_errors pushBack ["SESSION_OR_REVISION_CHANGED"]};
    if (_errors isEqualTo []) then {
        ma_baseline = call ma_fingerprint;
        // Loading the same confirmed scene does not count as a new patch.
        ma_stopped = false; call ma_storeState;
    };
    ["roundtrip",_errors] call ma_test_finish;
    if (_copyPasteContext isNotEqualTo []) then {
        [_copyPasteContext] call ma_test_finishCopyPasteContext;
    } else {
        // Backward-compatible fallback for a pending test started before this code
        // was compiled. It is safe because the generic continuation is now done.
        private _legacyCopyPasteContext = uiNamespace getVariable ["ma_copyPastePending",[]];
        if (_legacyCopyPasteContext isNotEqualTo []) then {
            [_legacyCopyPasteContext] call ma_test_finishCopyPasteContext;
        };
    };
}

// Explicit cleanup only. Not rollback: removes probe-owned objects and reads back.
function(ma_test_reset)
{
    if (!canSuspend || {!(call ma_isProbe)} || {ma_busy}) exitWith {["FAIL",[],["USE_SPAWN_IN_PROBE"]] call ma_response};
    ma_stopped = true; call ma_storeState;
    private _owned = call ma_owned;
    ["MapAutomation reset", "Remove owned probe objects", ""] collect3DENHistory { delete3DENEntities _owned; };
    uiSleep 0.3;
    if ((call ma_owned) isNotEqualTo []) exitWith {["reset",["DELETE_READBACK_FAILED"]] call ma_test_finish};
    uiNamespace setVariable ["ma_smokePassed",false];
    uiNamespace setVariable ["ma_roundTripPending",[]];
    call ma_reconcile;
    ["reset",[]] call ma_test_finish
}

// Explicit recovery for a failed paste test: preserve the lowest Eden ID for each
// semantic ID and remove additional duplicates plus prior copy_* test artifacts.
function(ma_test_cleanupDuplicateEntities)
{
    if (!(call ma_isProbe) || {ma_busy}) exitWith {["FAIL",[],["NOT_PROBE_OR_BUSY"]] call ma_response};
    private _duplicates = call ma_duplicateIdDiagnostics;
    private _remove = [];
    {
        _x params ["_semanticId"];
        private _matches = (call ma_owned) select {
            ((([_x,false] call golib_getHashData) get "__ai") select 0) isEqualTo _semanticId
        };
        private _ordered = _matches apply {[get3DENEntityID _x,_x]};
        _ordered sort true;
        for "_i" from 1 to (count _ordered - 1) do {_remove pushBack ((_ordered select _i) select 1)};
    } forEach _duplicates;
    {
        private _hd = [_x,false] call golib_getHashData;
        private _identity = _hd getOrDefault ["__ai",[]];
        if (_identity isEqualType [] && {count _identity == 3} && {((_identity select 0) find "copy_") == 0}) then {
            _remove pushBackUnique _x;
        };
    } forEach (call ma_owned);
    private _removedIds = _remove apply {get3DENEntityID _x};
    if (_remove isNotEqualTo []) then {delete3DENEntities _remove};
    if ((call ma_duplicateIdDiagnostics) isNotEqualTo []) exitWith {
        ma_stopped = true; call ma_storeState;
        ["FAIL",call ma_sceneData,[["DUPLICATE_CLEANUP_FAILED",call ma_duplicateIdDiagnostics]]] call ma_response
    };
    ma_baseline = call ma_fingerprint;
    ma_revision = ma_revision + 1;
    ma_stopped = false;
    call ma_storeState;
    ["OK",call ma_sceneData,[["DUPLICATE_ENTITIES_REMOVED",_removedIds]]] call ma_response
}
