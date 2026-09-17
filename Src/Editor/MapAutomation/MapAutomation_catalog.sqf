// Phase 2: read assembled types and measure one trusted model at a time.
// External input is data only. No client expression, path or getter is executed.

function(ma_catalogClasses)
{
    private _classes = ["GameObject",true,true] call oop_getAllObjectsOfType;
    // Child lists contain lowercase keys; export the assembled canonical name.
    _classes = _classes apply {(missionNamespace getVariable ["pt_" + _x,locationNull]) getVariable "classname"};
    _classes sort true;
    _classes
}

function(ma_catalogProfile)
{
    params ["_class"];
    private _type = missionNamespace getVariable ["pt_" + _class,locationNull];
    private _fields = _type getVariable ["__allfields_map",createHashMap];
    private _model = [_class,"model",true] call oop_getFieldBaseValue;
    if (isNil "_model" || {!(_model isEqualType "")}) then {_model = ""};
    private _cfg = if (_model == "") then {""} else {[_model,false] call golib_om_getConfigByModel};
    private _effect = [_class,"EffectClass"] call goasm_attributes_hasAttributeClass;
    if (_effect) then {_cfg = [_class,_cfg] call goasm_iapi_effect_convertConfig};
    private _resolved = getText (configFile >> "CfgVehicles" >> _cfg >> "model");
    private _chunk = locationNull call (_type getVariable ["getChunkType",{-1}]);
    private _chunkName = switch (_chunk) do {case 0:{"ITEM"};case 1:{"STRUCTURE"};case 2:{"DECOR"};default {"UNKNOWN"}};
    private _properties = createHashMap;
    { _properties set [_x,createHashMapFromArray [["expression",_fields get _x],["source","source"],["evidence","assembled __allfields_map"]]]; } forEach keys _fields;
    private _inheritance = +(_type getVariable ["__inhlistCase",[]]);
    _inheritance = _inheritance select {_x != _class};
    createHashMapFromArray [
        ["classname",_class],["parent",_type getVariable ["__motherClass",""]],
        ["configTextures",getArray (configFile >> "CfgVehicles" >> _cfg >> "hiddenSelectionsTextures")],
        ["inheritance",_inheritance],["model",_model],["config",_cfg],["engineResolvedModel",_resolved],
        ["editorPlaceable",!([_class,"InterfaceClass"] call goasm_attributes_hasAttributeClass) && {isClass (configFile >> "CfgVehicles" >> _cfg)}],
        ["effectClass",_effect],["chunkType",_chunkName],["chunkTypeRaw",_chunk],
        ["displayNameExpression",_fields getOrDefault ["name",""]],["descriptionExpression",_fields getOrDefault ["desc",""]],
        ["effectiveProperties",_properties],["methods",_type getVariable ["__allmethods",[]]],
        ["editorAttributes",keys (_type getVariable ["_redit_attribClass",createHashMap])],
        ["attributeData",createHashMapFromArray [
            ["class",_type getVariable ["_redit_attribClass",createHashMap]],
            ["fields",_type getVariable ["_redit_attribFields",createHashMap]],
            ["methods",_type getVariable ["_redit_attribMethods",createHashMap]]]],
        ["source","source"],["evidence","assembled OOP reflection"],
        ["declaration",_type getVariable ["__decl_info__",[]]]
    ]
}

function(ma_catalogPage)
{
    params ["_args"];
    if (!(call ma_isProbe) || {ma_busy} || {ma_stopped}) exitWith {["FAIL",[],["NOT_READY_PROBE"]] call ma_response};
    private _offset = _args getOrDefault ["offset",0];
    private _limit = _args getOrDefault ["limit",1];
    if !(_offset isEqualType 0 && {_limit isEqualType 0} && {finite _offset} && {finite _limit} && {_offset >= 0} && {_offset == floor _offset} && {_limit >= 1} && {_limit <= 4} && {_limit == floor _limit}) exitWith {["FAIL",[],["INVALID_PAGE"]] call ma_response};
    private _classes = call ma_catalogClasses;
    private _rows = [];
    ma_busy = true;
    ma_engineErrors = [];
    private _failed = isNil {
        _rows = (_classes select [_offset,_limit]) apply {[_x] call ma_catalogProfile};
        true
    };
    ma_busy = false;
    if (_failed || {ma_engineErrors isNotEqualTo []}) exitWith {
        ma_stopped = true; call ma_storeState;
        ["FAIL",[],["REFLECTION_EXPORT_FAILED",ma_engineErrors]] call ma_response
    };
    ["OK",createHashMapFromArray [["offset",_offset],["total",count _classes],["allOopLoadedCount",count p_table_allclassnames],["objects",_rows],["generation",ma_catalogGeneration],["productVersion",productVersion],["sceneFingerprint",call ma_fingerprint],["simpleObjectCount",count (allSimpleObjects [])]],[]] call ma_response
}

function(ma_probeGeometry)
{
    params ["_args"];
    if (!(call ma_isProbe) || {ma_busy} || {ma_stopped}) exitWith {["FAIL",[],["NOT_READY_PROBE"]] call ma_response};
    private _class = _args getOrDefault ["classname",""];
    // Data-only, bounded model-space rays. No client code or scene mutation.
    private _rays = _args getOrDefault ["surfaceRays",[]];
    if !(_rays isEqualType [] && {count _rays <= 256}) exitWith {["FAIL",[],["INVALID_SURFACE_RAYS"]] call ma_response};
    private _badRay = _rays findIf {
        !(_x isEqualType [] && {count _x == 3} && {(_x select 2) in ["GEOM","VIEW","ROADWAY"]} && {
            ((_x select [0,2]) findIf {!(_x isEqualType [] && {count _x == 3} && {(_x findIf {!(_x isEqualType 0) || {!finite _x} || {abs _x > 100}}) == -1})}) == -1
        })
    };
    if (_badRay != -1) exitWith {["FAIL",[],["INVALID_SURFACE_RAY",_badRay]] call ma_response};
    if !(_class isEqualType "" && {_class in (call ma_catalogClasses)}) exitWith {["FAIL",[],["UNKNOWN_CLASS"]] call ma_response};
    private _profile = [_class] call ma_catalogProfile;
    if (!(_profile get "editorPlaceable") || {_profile get "effectClass"}) exitWith {["FAIL",[],["NOT_STATIC_PLACEABLE_MODEL"]] call ma_response};
    private _model = _profile get "engineResolvedModel";
    if (_model == "") exitWith {["FAIL",[],["MODEL_UNRESOLVED"]] call ma_response};
    private _before = call ma_fingerprint;
    private _simpleBefore = allSimpleObjects [];
    private _obj = objNull;
    private _result = createHashMap;
    ma_busy = true;
    ma_engineErrors = [];
    private _failed = isNil {
        _obj = createSimpleObject [_model,[0,0,1000],true];
        if (isNullReference(_obj)) then {nil} else {
            _obj setVectorDirAndUp [[0,1,0],[0,0,1]];
            private _bounds = boundingBoxReal _obj;
            private _geometryBounds = boundingBoxReal [_obj,"Geometry"];
            private _dimensions = (_bounds select 1) vectorDiff (_bounds select 0);
            if ((_dimensions findIf {!(finite _x) || {_x <= 0}}) != -1) exitWith {nil};
            _result = createHashMapFromArray [
                ["classname",_class],["model",_model],["source","engineMeasured"],
                ["status","VERIFIED"],["visualBounds",_bounds],
                ["dimensions",_dimensions],["generation",ma_catalogGeneration],
                ["modelOriginASL",_obj modelToWorldWorld [0,0,0]],
                ["vectorDir",vectorDir _obj],["vectorUp",vectorUp _obj],
                ["modelInfo",getModelInfo _obj],["productVersion",productVersion],
                ["geometryBounds",_geometryBounds],["geometryBoundsStatus","MEASURED_AABB_NOT_MESH"],["semanticFrontStatus","UNKNOWN"],
                ["measurement","boundingBoxReal default on local simple object; NOT collision geometry"]
            ];
            private _lodEvidence = createHashMap;
            {
                private _lod = _x;
                private _names = _obj selectionNames _lod;
                _lodEvidence set [_lod,createHashMapFromArray [
                    ["selectionNames",_names],
                    ["namedPositions",(_names select [0,64]) apply {[_x,_obj selectionPosition [_x,_lod]]}],
                    ["interpretation","Named selections only; empty names do not prove missing LOD; positions are selection centres, not a full contact mesh"]
                ]];
            } forEach ["Memory","Geometry","LandContact"];
            _lodEvidence set ["Roadway",createHashMapFromArray [
                ["selectionNames",[]],["namedPositions",[]],["queryStatus","UNKNOWN"],
                ["interpretation","This engine rejects Roadway as a selectionNames LOD enum; absence is not asserted"]
            ]];
            _result set ["lodEvidence",_lodEvidence];
            private _surfaceSamples = [];
            {
                _x params ["_start","_end","_lod"];
                private _hits = lineIntersectsSurfaces [_obj modelToWorldWorld _start,_obj modelToWorldWorld _end,objNull,objNull,true,8,_lod,"NONE",false];
                _hits = _hits select {(_x select 2) isEqualTo _obj || {(_x select 3) isEqualTo _obj}};
                _surfaceSamples pushBack (createHashMapFromArray [
                    ["ray",_x],["hits",_hits apply {createHashMapFromArray [
                        ["positionModel",(_x select 0) vectorDiff (_obj modelToWorldWorld [0,0,0])],
                        ["normal",_x select 1],["selections",_x select 4]
                    ]}]
                ]);
            } forEach _rays;
            _result set ["surfaceSamples",_surfaceSamples];
            true
        }
    };
    // DoorDynamic uses animate. Read after a frame; no client animation code.
    if (!_failed && {_class == "WoodenDoor"} && {ma_engineErrors isEqualTo []}) then {
        private _samples = [];
        for "_step" from 0 to 7 do {
            private _phase = _step / 10;
            _obj animate ["xlamdoor",_phase,true];
            uiSleep 0.05;
            _samples pushBack (createHashMapFromArray [
                ["requestedPhase",_phase],["actualPhase",_obj animationPhase "xlamdoor"],
                ["visualBounds",boundingBoxReal _obj],["geometryBounds",boundingBoxReal [_obj,"Geometry"]],
                ["selectionPositions",((_obj selectionNames "Geometry") select [0,64]) apply {[_x,_obj selectionPosition [_x,"Geometry"]]}]
            ]);
        };
        _result set ["doorSamples",_samples];
        _result set ["doorContract",["WoodenDoor","xlamdoor",0,0.7,"DoorDynamic.animateSource / WoodenDoors.sqf"]];
    };
    if (!isNullReference(_obj)) then {deleteVehicle _obj};
    uiSleep 0.05;
    private _simpleAfter = allSimpleObjects [];
    private _clean = isNullReference(_obj) && {(_simpleAfter - _simpleBefore) isEqualTo []} && {(_simpleBefore - _simpleAfter) isEqualTo []};
    ma_busy = false;
    if (_failed || {!_clean} || {ma_engineErrors isNotEqualTo []} || {(call ma_fingerprint) isNotEqualTo _before}) exitWith {
        ma_stopped = true; call ma_storeState;
        ["FAIL",[],["GEOMETRY_PROBE_FAILED_OR_SCENE_CHANGED",ma_engineErrors]] call ma_response
    };
    _result set ["cleanupVerified",_clean];
    _result set ["sceneUnchanged",true];
    ["OK",_result,[]] call ma_response
}
