// Scheduled call only: [views] spawn ma_captureViews; view=[positionASL,targetASL,FOV].
function(ma_screenshotRoot)
{
    private _override = uiNamespace getVariable ["ma_screenshotRoot",""];
    if (_override != "") exitWith {_override};
    private _root = (getMissionPath "") + "..\..\Screenshots\";
    private _profiles = (call Core_getCliArgs) get "profiles";
    if (!isNil "_profiles") then {
        _root = format ["%1\Users\%2\Screenshots\",_profiles,profileName];
    };
    _root
}

function(ma_captureViews)
{
    params ["_views"];
    if (!canSuspend) exitWith {["FAIL",[],["CAPTURE_REQUIRES_SPAWN"]] call ma_response};
    if (!(call ma_isProbe) || {!ma_ready} || {ma_busy} || {ma_stopped}) exitWith {
        ["FAIL",[],["NOT_READY_OR_SAFE_STOP"]] call ma_response
    };
    if ((call ma_fingerprint) isNotEqualTo ma_baseline) exitWith {
        ma_stopped = true; call ma_storeState;
        ["FAIL",call ma_sceneData,["SCENE_CHANGED_BEFORE_CAPTURE"]] call ma_response
    };
    if !(_views isEqualType [] && {count _views > 0} && {count _views <= 8}) exitWith {
        ["FAIL",[],["EXPECTED_1_TO_8_VIEWS"]] call ma_response
    };
    if ((_views findIf {
        !(_x isEqualType []) || {count _x != 3} || {!([_x select 0] call ma_validVec)}
        || {!([_x select 1] call ma_validVec)} || {!((_x select 2) isEqualType 0)}
        || {!finite (_x select 2)} || {(_x select 2) < 0.1} || {(_x select 2) > 1.2}
    }) != -1) exitWith {["FAIL",[],["INVALID_CAMERA_VIEW"]] call ma_response};
    ma_busy = true;
    ma_engineErrors = [];
    private _revision = ma_revision;
    private _results = [];
    private _errors = [];
    private _camera = "camera" camCreate [0,0,0];
    if (_camera isEqualTo objNull) exitWith {
        ma_busy = false;
        ["FAIL",[],["CAMERA_CREATE_FAILED"]] call ma_response
    };
    _camera cameraEffect ["internal","back"];
    {
        _x params ["_position","_target","_fov"];
        _camera setPosASL _position;
        _camera camSetTarget (ASLToAGL _target);
        _camera camSetFov _fov;
        _camera camCommit 0;
        // Wait for streamed assets/exposure; a timeout never implies a valid file.
        uiSleep 1;
        private _file = format ["MapAutomation_%1_r%2_v%3_%4.png",ma_session,_revision,_forEachIndex,floor (diag_tickTime * 1000)];
        private _path = (call ma_screenshotRoot) + _file;
        if ([_path,false] call file_exists) exitWith {_errors pushBack ["CAPTURE_PATH_EXISTS",_path]};
        if !(screenshot _file) exitWith {_errors pushBack ["SCREENSHOT_COMMAND_FAILED",_path]};
        private _deadline = diag_tickTime + 10;
        waitUntil {uiSleep 0.1; ([_path,false] call file_exists) || {diag_tickTime > _deadline}};
        if !([_path,false] call file_exists) exitWith {_errors pushBack ["SCREENSHOT_FILE_MISSING",_path]};
        _results pushBack createHashMapFromArray [
            ["revision",_revision],["sessionId",ma_session],["viewIndex",_forEachIndex],["path",_path],
            ["sceneFingerprint",ma_baseline],
            ["positionASL",_position],["targetASL",_target],["fov",_fov],
            ["cameraPositionActualASL",getPosASL _camera]
        ];
    } forEach _views;
    _camera cameraEffect ["terminate","back"];
    camDestroy _camera;
    // get3DENCamera can transiently be objNull after an off-screen capture. Calling
    // cameraEffect on it aborts this scheduled transport worker after PNG creation,
    // leaving the request without a response and preventing ownership cleanup.
    private _edenCamera = get3DENCamera;
    if !(_edenCamera isEqualTo objNull) then {
        _edenCamera cameraEffect ["internal","back"];
    } else {
        _errors pushBack ["EDEN_CAMERA_RESTORE_UNAVAILABLE","Screenshots exist; editor camera was not restored"];
    };
    ma_busy = false;
    if (ma_engineErrors isNotEqualTo []) then {_errors pushBack ["ENGINE_SCRIPT_ERRORS",ma_engineErrors]};
    if ((call ma_fingerprint) isNotEqualTo ma_baseline || {ma_revision != _revision}) then {
        ma_stopped = true; call ma_storeState;
        _errors pushBack ["SCENE_CHANGED_DURING_CAPTURE: images are not accepted"];
    };
    private _response = [if (_errors isEqualTo []) then {"OK"} else {"FAIL"},_results,_errors] call ma_response;
    ["capture",_response] call ma_test_record;
    _response
}

function(ma_test_capture)
{
    if (!canSuspend) exitWith {["FAIL",[],["USE_SPAWN"]] call ma_response};
    // Test geometry is located at [4000,4000,10] in Eden's position space.
    private _o = ["floor_1"] call ma_find;
    if (_o isEqualTo objNull) exitWith {["FAIL",[],["RUN_SMOKE_FIRST"]] call ma_response};
    private _target = getPosASL _o;
    [[[_target vectorAdd [22,-28,22],_target,0.85],[_target vectorAdd [-20,-24,15],_target,0.85]]] call ma_captureViews
}
