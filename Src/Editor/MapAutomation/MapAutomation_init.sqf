// Relicta editor automation probe. No transport or generated SQF execution.
#include "MapAutomation_api.sqf"
#include "MapAutomation_capture.sqf"
#include "MapAutomation_transport.sqf"
#include "MapAutomation_tests.sqf"

init_function(ma_initialize)
{
    ma_transportRequestDir = "Tools\MapAutomation\queue\requests";
    ma_transportResponseDir = "Tools\MapAutomation\queue\responses";
    ma_transportCache = createHashMap;
    ma_mapName = "AI_AutomationProbe";
    ma_allowedClasses = ["BigConcreteFloor","ConcreteGreenWall","WoodenArch"];
    ma_busy = false;
    ma_engineErrors = [];
    ma_saveSerial = 0;
    ma_pasteSerial = 0;
    ma_suppressHistoryIdentityRepair = false;
    ma_baseline = [];
    ma_revision = uiNamespace getVariable ["ma_revision",0];
    ma_stopped = uiNamespace getVariable ["ma_stopped",false];
    ma_session = uiNamespace getVariable ["ma_session",""];
    if (ma_session == "") then {
        ma_session = "probe_" + ((systemTimeUTC apply {str _x}) joinString "_");
        uiNamespace setVariable ["ma_session",ma_session];
    };
    ma_ready = false;
    // Core clears ScriptError handlers on recompilation before this initializer.
    addMissionEventHandler ["ScriptError",{
        if (ma_busy) then {
            ma_engineErrors pushBack _this;
            ma_stopped = true;
            call ma_storeState;
        };
    }];
    ["onSaving",{ ma_saveSerial = ma_saveSerial + 1; }] call Core_addEventHandler;
    ["onUndo",{ if (ma_ready) then { ma_stopped = true; call ma_storeState; if (!ma_suppressHistoryIdentityRepair) then {[] spawn ma_onHistoryIdentity;}; }; }] call Core_addEventHandler;
    ["onRedo",{ if (ma_ready) then { ma_stopped = true; call ma_storeState; if (!ma_suppressHistoryIdentityRepair) then {[] spawn ma_onHistoryIdentity;}; }; }] call Core_addEventHandler;
    ["onPaste",{
        params ["_entities"];
        if (call ma_isProbe) then { [_entities] spawn ma_onPaste; };
    }] call Core_addEventHandler;
    ["onEntityAdded",{
        params ["_entity"];
        if (call ma_isProbe) then { [_entity] spawn ma_onEntityAddedIdentity; };
    }] call Core_addEventHandler;
    ["onEditorLoaded",{
        ma_ready = call ma_isProbe;
        if (ma_ready) then {
            ma_baseline = call ma_fingerprint;
            ["READY",[],["PHASE_1_ENGINE_VERIFIED","REQUIRES MANUAL PNG REVIEW"]] call ma_response;
            if ((uiNamespace getVariable ["ma_roundTripPending",[]]) isNotEqualTo []) then {
                [] spawn ma_test_resumeRoundTrip;
            } else {
                // Legacy/recovery path only. New Copy/Paste tests travel inside the
                // round-trip continuation so post-load verification is serialized.
                if ((uiNamespace getVariable ["ma_copyPastePending",[]]) isNotEqualTo []) then {
                [] spawn ma_test_resumeCopyPaste;
                };
            };
        };
    }] call Core_addEventHandler;
    if (isNil "ma_transportLoopHandle" || {scriptDone ma_transportLoopHandle}) then {
        ma_transportLoopHandle = [] spawn ma_transportLoop;
    };
}
