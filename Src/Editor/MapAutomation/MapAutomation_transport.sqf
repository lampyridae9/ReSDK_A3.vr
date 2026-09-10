// Data-only JSON file queue. Input is decoded with fromJSON and never compiled/called.
// State is initialized by ma_initialize; this include contains declarations only.

function(ma_transportResponse)
{
    params ["_requestId","_status",["_result",[]],["_diagnostics",[]]];
    createHashMapFromArray [
        ["protocolVersion",1],["requestId",_requestId],["sessionId",ma_session],
        ["status",_status],["revision",ma_revision],["result",_result],
        ["diagnostics",_diagnostics],["stopped",ma_stopped]
    ]
}

function(ma_transportWrapInternal)
{
    params ["_requestId","_internal"];
    [_requestId,_internal get "status",_internal get "result",_internal get "diagnostics"] call ma_transportResponse
}

function(ma_transportPatchToInternal)
{
    params ["_external"];
    private _operations = [];
    private _errors = [];
    if !(_external isEqualType [] && {count _external > 0} && {count _external <= 32}) exitWith {
        [[],[["PATCH_EXPECTS_1_TO_32_OPERATIONS"]]]
    };
    {
        if !(_x isEqualType createHashMap) then {
            _errors pushBack ["OPERATION_MUST_BE_OBJECT",_forEachIndex];
            continue;
        };
        private _op = _x getOrDefault ["operation",""];
        private _a = _x getOrDefault ["arguments",createHashMap];
        if !(_a isEqualType createHashMap) then {
            _errors pushBack ["ARGUMENTS_MUST_BE_OBJECT",_forEachIndex];
            continue;
        };
        private _converted = switch (_op) do {
            case "create": {[
                _a getOrDefault ["semanticId",""],_a getOrDefault ["class",""],
                _a getOrDefault ["position",[]],_a getOrDefault ["rotation",[]],
                _a getOrDefault ["scale",1],_a getOrDefault ["parentId",""]
            ]};
            case "delete": {[_a getOrDefault ["semanticId",""]]};
            case "setTransform": {[
                _a getOrDefault ["semanticId",""],_a getOrDefault ["position",[]],
                _a getOrDefault ["rotation",[]],_a getOrDefault ["scale",1]
            ]};
            case "setProperties": {
                private _properties = _a getOrDefault ["properties",createHashMap];
                if !(_properties isEqualType createHashMap) then {[]} else {
                    private _keys = keys _properties;
                    _keys sort true;
                    [_a getOrDefault ["semanticId",""],_keys apply {[_x,_properties get _x]}]
                }
            };
            default {[]};
        };
        if !(_op in ["create","delete","setTransform","setProperties"]) then {
            _errors pushBack ["UNKNOWN_PATCH_OPERATION",_forEachIndex,_op];
            continue;
        };
        if (_converted isEqualTo []) then {
            _errors pushBack ["INVALID_PATCH_ARGUMENTS",_forEachIndex,_op];
            continue;
        };
        _operations pushBack [_op,_converted];
    } forEach _external;
    [_operations,_errors]
}

function(ma_transportDispatch)
{
    params ["_requestId","_request"];
    if !(_request isEqualType createHashMap) exitWith {
        [_requestId,"FAIL",[],[["REQUEST_MUST_BE_JSON_OBJECT"]]] call ma_transportResponse
    };
    private _version = _request getOrDefault ["protocolVersion",-1];
    private _embeddedId = _request getOrDefault ["requestId",""];
    private _sessionId = _request getOrDefault ["sessionId",""];
    private _expected = _request getOrDefault ["expectedRevision",-999999];
    private _operation = _request getOrDefault ["operation",""];
    private _arguments = _request getOrDefault ["arguments",createHashMap];
    if (_version isNotEqualTo 1) exitWith {[_requestId,"FAIL",[],[["UNSUPPORTED_PROTOCOL_VERSION",_version]]] call ma_transportResponse};
    if (_embeddedId isNotEqualTo _requestId) exitWith {[_requestId,"FAIL",[],[["REQUEST_ID_FILENAME_MISMATCH",_embeddedId]]] call ma_transportResponse};
    if !(_expected isEqualType 0) exitWith {[_requestId,"FAIL",[],[["EXPECTED_REVISION_MUST_BE_NUMBER"]]] call ma_transportResponse};
    if !(_arguments isEqualType createHashMap) exitWith {[_requestId,"FAIL",[],[["ARGUMENTS_MUST_BE_JSON_OBJECT"]]] call ma_transportResponse};
    if !(_operation in ["getCapabilities","inspectScene","inspectObjects","applyPatch","captureViews","catalogPage","probeGeometry"]) exitWith {
        [_requestId,"FAIL",[],[["UNKNOWN_OPERATION",_operation]]] call ma_transportResponse
    };
    if (_operation != "getCapabilities" && {_sessionId isNotEqualTo ma_session}) exitWith {
        [_requestId,"FAIL",[],[["SESSION_MISMATCH",_sessionId,ma_session]]] call ma_transportResponse
    };
    if (_operation in ["applyPatch","captureViews","catalogPage","probeGeometry"] && {_expected isNotEqualTo ma_revision}) exitWith {
        [_requestId,"FAIL",call ma_sceneData,[["REVISION_MISMATCH",_expected,ma_revision]]] call ma_transportResponse
    };
    if (_operation == "getCapabilities") exitWith {[_requestId,call ma_getCapabilities] call ma_transportWrapInternal};
    if (_operation == "catalogPage") exitWith {[_requestId,[_arguments] call ma_catalogPage] call ma_transportWrapInternal};
    if (_operation == "probeGeometry") exitWith {[_requestId,[_arguments] call ma_probeGeometry] call ma_transportWrapInternal};
    if (_operation == "inspectScene") exitWith {[_requestId,call ma_inspectScene] call ma_transportWrapInternal};
    if (_operation == "inspectObjects") exitWith {
        private _ids = _arguments getOrDefault ["semanticIds",[]];
        if !(_ids isEqualType []) exitWith {[_requestId,"FAIL",[],[["SEMANTIC_IDS_MUST_BE_ARRAY"]]] call ma_transportResponse};
        private _result = [];
        private _errors = [];
        {
            if !(_x isEqualType "") then {_errors pushBack ["INVALID_SEMANTIC_ID",_forEachIndex]; continue};
            private _o = [_x] call ma_find;
            if (_o isEqualTo objNull) then {_errors pushBack ["ID_MISSING_OR_DUPLICATED",_x]} else {_result pushBack ([_o] call ma_readObject)};
        } forEach _ids;
        [_requestId,if (_errors isEqualTo []) then {"OK"} else {"FAIL"},_result,_errors] call ma_transportResponse
    };
    if (_operation == "applyPatch") exitWith {
        private _converted = [_arguments getOrDefault ["operations",[]]] call ma_transportPatchToInternal;
        _converted params ["_operations","_errors"];
        if (_errors isNotEqualTo []) exitWith {[_requestId,"FAIL",[],[["INVALID_PATCH",_errors]]] call ma_transportResponse};
        [_requestId,[_operations,_expected] call ma_applyPatch] call ma_transportWrapInternal
    };
    private _externalViews = _arguments getOrDefault ["views",[]];
    if !(_externalViews isEqualType []) exitWith {[_requestId,"FAIL",[],[["VIEWS_MUST_BE_ARRAY"]]] call ma_transportResponse};
    private _views = [];
    private _errors = [];
    {
        if !(_x isEqualType createHashMap) then {_errors pushBack ["VIEW_MUST_BE_OBJECT",_forEachIndex]; continue};
        _views pushBack [
            _x getOrDefault ["positionASL",[]],_x getOrDefault ["targetASL",[]],
            _x getOrDefault ["fov",-1],_x getOrDefault ["viewId",format ["view_%1",_forEachIndex]],
            _x getOrDefault ["cameraRole",format ["view_%1",_forEachIndex]],
            _x getOrDefault ["captureClassOverlay",false]
        ];
    } forEach _externalViews;
    if (_errors isNotEqualTo []) exitWith {[_requestId,"FAIL",[],[["INVALID_VIEWS",_errors]]] call ma_transportResponse};
    [_requestId,[_views] call ma_captureViews] call ma_transportWrapInternal
}

function(ma_transportProcessFile)
{
    params ["_name"];
    if !([_name,"^[A-Za-z0-9][A-Za-z0-9_.-]{0,100}\.json$"] call regex_isMatch) exitWith {};
    private _requestId = _name select [0,count _name - 5];
    private _requestPath = ma_transportRequestDir + "\" + _name;
    private _responsePath = ma_transportResponseDir + "\" + _name;
    if ([_responsePath] call file_exists) exitWith {[_requestPath] call file_delete};
    private _raw = [_requestPath] call file_read;
    private _cached = ma_transportCache getOrDefault [_requestId,[]];
    if (_cached isNotEqualTo []) exitWith {
        private _response = if ((_cached select 0) isEqualTo _raw) then {_cached select 1} else {
            [_requestId,"FAIL",[],[["REQUEST_ID_REUSE_CONFLICT"]]] call ma_transportResponse
        };
        if ([_responsePath,toJSON _response] call file_write) then {[_requestPath] call file_delete};
    };
    private _request = nil;
    private _parseFailed = isNil {_request = FromJSON _raw; _request};
    private _response = if (_parseFailed) then {
        [_requestId,"FAIL",[],[["INVALID_JSON"]]] call ma_transportResponse
    } else {
        [_requestId,_request] call ma_transportDispatch
    };
    ma_transportCache set [_requestId,[_raw,_response]];
    if ([_responsePath,toJSON _response] call file_write) then {[_requestPath] call file_delete};
}

function(ma_transportLoop)
{
    while {true} do {
        if (ma_ready && {call ma_isProbe}) then {
            private _files = [ma_transportRequestDir,true,"*.json",false] call file_getFileList;
            _files sort true;
            {[_x] call ma_transportProcessFile;} forEach _files;
        };
        uiSleep 0.1;
    };
}
