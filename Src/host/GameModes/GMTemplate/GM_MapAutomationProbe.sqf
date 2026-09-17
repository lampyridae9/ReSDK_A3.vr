// Editor-only walkthrough of the retained Phase 8A acceptance fixture.
#include <..\GameMode.h>

#ifdef EDITOR
editor_attribute("CodeOnyGamemode")
class(GMMapAutomationProbe) extends(GMBase)
    var(name,"AI Map Generator: проверка дома");
    var(desc,"Проверка дверей, лестницы и мебели в AI_AutomationProbe.");
    getterconst_func(isPlayableGamemode,false);
    getterconst_func(getProbability,0);
    getterconst_func(getMapName,"AI_AutomationProbe");
    getterconst_func(canPlayEvents,false);
    getterconst_func(getLobbyRoles,["RMapAutomationProbe"]);
    getterconst_func(getLateRoles,[]);
    getterconst_func(conditionToStart,true);
    getterconst_func(getUnsleepGameInfo,null);
    func(preSetup)
    {
        objParams();
        {
            callFuncParams(_x,lightSetMode,true);
        } foreach (["ElectronicDeviceLighting"] call getAllObjectsInWorldTypeOf);
    };
endclass

class(RMapAutomationProbe) extends(BasicRole_SimulationReSDK)
    var(name,"Проверяющий дом");
    // Fixed replay fixture: origin [5040,4700,10], inside the ground corridor.
    getter_func(getInitialPos,vec3(5044,4696,10.05));
    getter_func(getInitialDir,315);
    func(getEquipment)
    {
        objParams_1(_mob);
        ["NomadCloth12",_mob,INV_CLOTH] call createItemInInventory;
    };
endclass
#endif
