# ClientData.hpp

## SKILL_BASE

Type: constant

Description: 


Replaced value:
```sqf
0
```
File: [client\ClientData\ClientData.hpp at line 10](../../../Src/client/ClientData/ClientData.hpp#L10)
## SKILL_MOD

Type: constant

Description: 


Replaced value:
```sqf
1
```
File: [client\ClientData\ClientData.hpp at line 11](../../../Src/client/ClientData/ClientData.hpp#L11)
## VIDEO_SETTINGS_MAX

Type: constant

Description: 


Replaced value:
```sqf
1
```
File: [client\ClientData\ClientData.hpp at line 15](../../../Src/client/ClientData/ClientData.hpp#L15)
## VIDEO_SETTINGS_MIN

Type: constant

Description: 


Replaced value:
```sqf
0
```
File: [client\ClientData\ClientData.hpp at line 16](../../../Src/client/ClientData/ClientData.hpp#L16)
# ClientData.sqf

## sk_nan

Type: constant

Description: 


Replaced value:
```sqf
[0,0]
```
File: [client\ClientData\ClientData.sqf at line 50](../../../Src/client/ClientData/ClientData.sqf#L50)
## printerr(code,text)

Type: constant

Description: 
- Param: code
- Param: text

Replaced value:
```sqf
if (_code == code) exitWith {[text] call (getDisplay getVariable ["printError",{}])}
```
File: [client\ClientData\ClientData.sqf at line 540](../../../Src/client/ClientData/ClientData.sqf#L540)
## cd_clientName

Type: Variable

Description: 


Initial value:
```sqf
""
```
File: [client\ClientData\ClientData.sqf at line 46](../../../Src/client/ClientData/ClientData.sqf#L46)
## cd_charName

Type: Variable

Description: 


Initial value:
```sqf
"Обитатель Сети"
```
File: [client\ClientData\ClientData.sqf at line 48](../../../Src/client/ClientData/ClientData.sqf#L48)
## cd_skillNames

Type: Variable

Description: 


Initial value:
```sqf
["СЛ","ИН","ЛВ","ЗД","ВНС","ВОЛЯ","ВОС","ЖЗ"]
```
File: [client\ClientData\ClientData.sqf at line 52](../../../Src/client/ClientData/ClientData.sqf#L52)
## cd_skills

Type: Variable

Description: 


Initial value:
```sqf
[sk_nan,sk_nan,sk_nan,sk_nan,sk_nan,sk_nan,sk_nan,sk_nan] //массив со скиллами
```
File: [client\ClientData\ClientData.sqf at line 54](../../../Src/client/ClientData/ClientData.sqf#L54)
## cd_stamina_cur

Type: Variable

Description: 


Initial value:
```sqf
100
```
File: [client\ClientData\ClientData.sqf at line 58](../../../Src/client/ClientData/ClientData.sqf#L58)
## cd_stamina_max

Type: Variable

Description: 


Initial value:
```sqf
100
```
File: [client\ClientData\ClientData.sqf at line 60](../../../Src/client/ClientData/ClientData.sqf#L60)
## cd_curSelection

Type: Variable

Description: 


Initial value:
```sqf
TARGET_ZONE_TORSO
```
File: [client\ClientData\ClientData.sqf at line 92](../../../Src/client/ClientData/ClientData.sqf#L92)
## cd_specialAction

Type: Variable

Description: 


Initial value:
```sqf
SPECIAL_ACTION_NO
```
File: [client\ClientData\ClientData.sqf at line 94](../../../Src/client/ClientData/ClientData.sqf#L94)
## cd_curDefType

Type: Variable

Description: combat


Initial value:
```sqf
DEF_TYPE_DODGE
```
File: [client\ClientData\ClientData.sqf at line 98](../../../Src/client/ClientData/ClientData.sqf#L98)
## cd_curCombatStyle

Type: Variable

Description: 


Initial value:
```sqf
COMBAT_STYLE_NO
```
File: [client\ClientData\ClientData.sqf at line 100](../../../Src/client/ClientData/ClientData.sqf#L100)
## cd_curAttackType

Type: Variable

Description: 


Initial value:
```sqf
ATTACK_TYPE_THRUST
```
File: [client\ClientData\ClientData.sqf at line 102](../../../Src/client/ClientData/ClientData.sqf#L102)
## cd_activeHand

Type: Variable

Description: 


Initial value:
```sqf
INV_HAND_L
```
File: [client\ClientData\ClientData.sqf at line 104](../../../Src/client/ClientData/ClientData.sqf#L104)
## cd_lca_r

Type: Variable

Description: 


Initial value:
```sqf
0
```
File: [client\ClientData\ClientData.sqf at line 107](../../../Src/client/ClientData/ClientData.sqf#L107)
## cd_lca_l

Type: Variable

Description: 


Initial value:
```sqf
0
```
File: [client\ClientData\ClientData.sqf at line 109](../../../Src/client/ClientData/ClientData.sqf#L109)
## cd_internal_lastTPPos

Type: Variable

Description: 


Initial value:
```sqf
vec3(0,0,0)
```
File: [client\ClientData\ClientData.sqf at line 253](../../../Src/client/ClientData/ClientData.sqf#L253)
## cd_internal_lastTPDir

Type: Variable

Description: 


Initial value:
```sqf
null
```
File: [client\ClientData\ClientData.sqf at line 255](../../../Src/client/ClientData/ClientData.sqf#L255)
## cd_internal_tpHandle

Type: Variable

Description: 


Initial value:
```sqf
-1
```
File: [client\ClientData\ClientData.sqf at line 257](../../../Src/client/ClientData/ClientData.sqf#L257)
## cd_internal_hasTPError

Type: Variable

Description: 


Initial value:
```sqf
false
```
File: [client\ClientData\ClientData.sqf at line 259](../../../Src/client/ClientData/ClientData.sqf#L259)
## cd_internal_lastTPObj

Type: Variable

Description: 


Initial value:
```sqf
objnull
```
File: [client\ClientData\ClientData.sqf at line 261](../../../Src/client/ClientData/ClientData.sqf#L261)
## cd_internal_startLoadTime

Type: Variable

Description: 


Initial value:
```sqf
0
```
File: [client\ClientData\ClientData.sqf at line 263](../../../Src/client/ClientData/ClientData.sqf#L263)
## cd_OnSkillsUpdate

Type: function

Description: 
- Param: _id
- Param: _val

File: [client\ClientData\ClientData.sqf at line 64](../../../Src/client/ClientData/ClientData.sqf#L64)
## cd_setVideoSettings

Type: function

Description: 
- Param: _value

File: [client\ClientData\ClientData.sqf at line 116](../../../Src/client/ClientData/ClientData.sqf#L116)
## cd_onPrepareClient

Type: function

Description: 
- Param: _atlPos
- Param: _vision

File: [client\ClientData\ClientData.sqf at line 138](../../../Src/client/ClientData/ClientData.sqf#L138)
## cd_tpLoad

Type: function

Description: 
- Param: _pos
- Param: _dir

File: [client\ClientData\ClientData.sqf at line 266](../../../Src/client/ClientData/ClientData.sqf#L266)
## cd_syncObjTransform

Type: function

Description: 
- Param: _src
- Param: _pos
- Param: _dir

File: [client\ClientData\ClientData.sqf at line 381](../../../Src/client/ClientData/ClientData.sqf#L381)
## cd_clientDisconnect

Type: function

Description: 
- Param: _args

File: [client\ClientData\ClientData.sqf at line 392](../../../Src/client/ClientData/ClientData.sqf#L392)
## cd_authproc

Type: function

Description: 


File: [client\ClientData\ClientData.sqf at line 420](../../../Src/client/ClientData/ClientData.sqf#L420)
## cd_openAuth

Type: function

Description: 
- Param: _mes

File: [client\ClientData\ClientData.sqf at line 427](../../../Src/client/ClientData/ClientData.sqf#L427)
## cd_authResult

Type: function

Description: 
- Param: _code
- Param: _nick

File: [client\ClientData\ClientData.sqf at line 533](../../../Src/client/ClientData/ClientData.sqf#L533)
## cd_switchMove_anim

Type: function

Description: 


File: [client\ClientData\ClientData.sqf at line 564](../../../Src/client/ClientData/ClientData.sqf#L564)
## cd_switchMove_force_anim

Type: function

Description: 


File: [client\ClientData\ClientData.sqf at line 569](../../../Src/client/ClientData/ClientData.sqf#L569)
## cd_playMove_anim

Type: function

Description: 


File: [client\ClientData\ClientData.sqf at line 576](../../../Src/client/ClientData/ClientData.sqf#L576)
## cd_setMimic_anim

Type: function

Description: 


File: [client\ClientData\ClientData.sqf at line 582](../../../Src/client/ClientData/ClientData.sqf#L582)
## cd_switchAction_anim

Type: function

Description: 


File: [client\ClientData\ClientData.sqf at line 587](../../../Src/client/ClientData/ClientData.sqf#L587)
## cd_syncongrabrot_setvdirup

Type: function

Description: 
- Param: _m

File: [client\ClientData\ClientData.sqf at line 592](../../../Src/client/ClientData/ClientData.sqf#L592)
## cd_camshake_proc

Type: function

Description: 


File: [client\ClientData\ClientData.sqf at line 601](../../../Src/client/ClientData/ClientData.sqf#L601)
## cd_replicate_replloc

Type: function

Description: 
- Param: _method
- Param: _ctx

File: [client\ClientData\ClientData.sqf at line 606](../../../Src/client/ClientData/ClientData.sqf#L606)
## repl_doLocal

Type: function

Description: 
- Param: _method
- Param: _ctx

File: [client\ClientData\ClientData.sqf at line 615](../../../Src/client/ClientData/ClientData.sqf#L615)
# ClientDataGamemode.sqf

## cd_onChangeGameState

Type: function

Description: 
- Param: _oldState
- Param: _newState

File: [client\ClientData\ClientDataGamemode.sqf at line 10](../../../Src/client/ClientData/ClientDataGamemode.sqf#L10)
# ClientDataUnconscious.sqf

## __UNCONSCIOUS_DELAY__

Type: constant

Description: 


Replaced value:
```sqf
0.1
```
File: [client\ClientData\ClientDataUnconscious.sqf at line 18](../../../Src/client/ClientData/ClientDataUnconscious.sqf#L18)
## cd_isUnconscious

Type: Variable

Description: 


Initial value:
```sqf
false //в бессознанке
```
File: [client\ClientData\ClientDataUnconscious.sqf at line 21](../../../Src/client/ClientData/ClientDataUnconscious.sqf#L21)
## cd_internal_uncState

Type: Variable

Description: 


Initial value:
```sqf
false //внутрення переменная перехода состояния
```
File: [client\ClientData\ClientDataUnconscious.sqf at line 23](../../../Src/client/ClientData/ClientDataUnconscious.sqf#L23)
## cd_onUnconsciousCode

Type: function

Description: 


File: [client\ClientData\ClientDataUnconscious.sqf at line 26](../../../Src/client/ClientData/ClientDataUnconscious.sqf#L26)
## cd_onUnconsciousEvent

Type: function

Description: 
- Param: _isUncState

File: [client\ClientData\ClientDataUnconscious.sqf at line 39](../../../Src/client/ClientData/ClientDataUnconscious.sqf#L39)
# ClientData_ConnectionManager.sqf

## PREPARE_PLAYER_POS_TIMEOUT

Type: constant

Description: 


Replaced value:
```sqf
120
```
File: [client\ClientData\ClientData_ConnectionManager.sqf at line 11](../../../Src/client/ClientData/ClientData_ConnectionManager.sqf#L11)
## SWITCH_PLAYER_TIMEOUT

Type: constant

Description: 


Replaced value:
```sqf
30
```
File: [client\ClientData\ClientData_ConnectionManager.sqf at line 14](../../../Src/client/ClientData/ClientData_ConnectionManager.sqf#L14)
## client_state

Type: Variable

Description: 


Initial value:
```sqf
"init"
```
File: [client\ClientData\ClientData_ConnectionManager.sqf at line 19](../../../Src/client/ClientData/ClientData_ConnectionManager.sqf#L19)
## client_getState

Type: function

Description: 


File: [client\ClientData\ClientData_ConnectionManager.sqf at line 21](../../../Src/client/ClientData/ClientData_ConnectionManager.sqf#L21)
## client_setState

Type: function

Description: 


File: [client\ClientData\ClientData_ConnectionManager.sqf at line 23](../../../Src/client/ClientData/ClientData_ConnectionManager.sqf#L23)
## client_isInGame

Type: function

Description: 


File: [client\ClientData\ClientData_ConnectionManager.sqf at line 25](../../../Src/client/ClientData/ClientData_ConnectionManager.sqf#L25)
## client_isInLobby

Type: function

Description: 


File: [client\ClientData\ClientData_ConnectionManager.sqf at line 27](../../../Src/client/ClientData/ClientData_ConnectionManager.sqf#L27)
## cd_prepPlayerPos

Type: function

Description: 
- Param: _pos
- Param: _mob

File: [client\ClientData\ClientData_ConnectionManager.sqf at line 31](../../../Src/client/ClientData/ClientData_ConnectionManager.sqf#L31)
## cd_processConnection

Type: function

Description: 
- Param: _isLinkTo
- Param: _mob
- Param: _prepareNextMode

File: [client\ClientData\ClientData_ConnectionManager.sqf at line 66](../../../Src/client/ClientData/ClientData_ConnectionManager.sqf#L66)
## cd_connectToMob

Type: function

Description: 
- Param: _mob
- Param: _nextAction (optional, default -1)

File: [client\ClientData\ClientData_ConnectionManager.sqf at line 194](../../../Src/client/ClientData/ClientData_ConnectionManager.sqf#L194)
## cd_onPlayingEnd

Type: function

Description: 
- Param: _mob
- Param: _nextAction (optional, default -1)

File: [client\ClientData\ClientData_ConnectionManager.sqf at line 201](../../../Src/client/ClientData/ClientData_ConnectionManager.sqf#L201)
# ClientData_customAnims.sqf

## cd_customAnim

Type: Variable

Description: 


Initial value:
```sqf
CUSTOM_ANIM_ACTION_NONE
```
File: [client\ClientData\ClientData_customAnims.sqf at line 12](../../../Src/client/ClientData/ClientData_customAnims.sqf#L12)
## cd_isCustomAnimEnabled

Type: function

Description: 


File: [client\ClientData\ClientData_customAnims.sqf at line 15](../../../Src/client/ClientData/ClientData_customAnims.sqf#L15)
## cd_handleRestCustomAnim

Type: function

Description: 


File: [client\ClientData\ClientData_customAnims.sqf at line 20](../../../Src/client/ClientData/ClientData_customAnims.sqf#L20)
# ClientData_forceWalk.sqf

## cd_fw_forceWalk

Type: Variable

Description: 


Initial value:
```sqf
false
```
File: [client\ClientData\ClientData_forceWalk.sqf at line 24](../../../Src/client/ClientData/ClientData_forceWalk.sqf#L24)
## cd_fw_hasBreakBone

Type: Variable

Description: 


Initial value:
```sqf
false
```
File: [client\ClientData\ClientData_forceWalk.sqf at line 27](../../../Src/client/ClientData/ClientData_forceWalk.sqf#L27)
## cd_sp_enabled

Type: Variable

Description: 


Initial value:
```sqf
true
```
File: [client\ClientData\ClientData_forceWalk.sqf at line 41](../../../Src/client/ClientData/ClientData_forceWalk.sqf#L41)
## cd_sp_lockedSetting

Type: Variable

Description: 


Initial value:
```sqf
false
```
File: [client\ClientData\ClientData_forceWalk.sqf at line 43](../../../Src/client/ClientData/ClientData_forceWalk.sqf#L43)
## cd_sp_grabbingMob

Type: Variable

Description: 


Initial value:
```sqf
false
```
File: [client\ClientData\ClientData_forceWalk.sqf at line 45](../../../Src/client/ClientData/ClientData_forceWalk.sqf#L45)
## cd_onSyncLegsBoneState

Type: function

Description: 
- Param: _unit
- Param: _hasBreak

File: [client\ClientData\ClientData_forceWalk.sqf at line 13](../../../Src/client/ClientData/ClientData_forceWalk.sqf#L13)
## cd_fw_isForceWalk

Type: function

Description: 


File: [client\ClientData\ClientData_forceWalk.sqf at line 29](../../../Src/client/ClientData/ClientData_forceWalk.sqf#L29)
## cd_fw_syncForceWalk

Type: function

Description: 
- Param: _mob

File: [client\ClientData\ClientData_forceWalk.sqf at line 31](../../../Src/client/ClientData/ClientData_forceWalk.sqf#L31)
## cd_sp_canSprint

Type: function

Description: 


File: [client\ClientData\ClientData_forceWalk.sqf at line 47](../../../Src/client/ClientData/ClientData_forceWalk.sqf#L47)
## cd_spr_sync

Type: function

Description: 


File: [client\ClientData\ClientData_forceWalk.sqf at line 50](../../../Src/client/ClientData/ClientData_forceWalk.sqf#L50)
# EscapeMenu.sqf

## ESC_MENU_SIZE_X

Type: constant

Description: 


Replaced value:
```sqf
20
```
File: [client\ClientData\EscapeMenu.sqf at line 12](../../../Src/client/ClientData/EscapeMenu.sqf#L12)
## ESC_MENU_SIZE_Y

Type: constant

Description: 


Replaced value:
```sqf
30
```
File: [client\ClientData\EscapeMenu.sqf at line 14](../../../Src/client/ClientData/EscapeMenu.sqf#L14)
## ESC_MENU_DEFAULT_BUTTON_BIAS_X

Type: constant

Description: 


Replaced value:
```sqf
5
```
File: [client\ClientData\EscapeMenu.sqf at line 16](../../../Src/client/ClientData/EscapeMenu.sqf#L16)
## ESC_MENU_DEFAULT_BUTTON_BIAS_Y

Type: constant

Description: 


Replaced value:
```sqf
5
```
File: [client\ClientData\EscapeMenu.sqf at line 18](../../../Src/client/ClientData/EscapeMenu.sqf#L18)
## ESC_MENU_BACKGROUND_COLOR_T3

Type: constant

Description: 


Replaced value:
```sqf
0.4
```
File: [client\ClientData\EscapeMenu.sqf at line 21](../../../Src/client/ClientData/EscapeMenu.sqf#L21)
## handleSettings(closerEv,OpenerEv)

Type: constant

Description: 
- Param: closerEv
- Param: OpenerEv

Replaced value:
```sqf
([closerEv,OpenerEv] call esc_internal_handleSettings)
```
File: [client\ClientData\EscapeMenu.sqf at line 24](../../../Src/client/ClientData/EscapeMenu.sqf#L24)
## addOpenerAndActivator(id)

Type: constant

Description: 
- Param: id

Replaced value:
```sqf
getDisplay createDisplay  "RscDisplayInterrupt"; ctrlActivate (findDisplay 49 displayCtrl id)
```
File: [client\ClientData\EscapeMenu.sqf at line 26](../../../Src/client/ClientData/EscapeMenu.sqf#L26)
## addCloseEventToSetting(id)

Type: constant

Description: 
- Param: id

Replaced value:
```sqf
(findDisplay id) displayAddEventHandler ["Unload",{(findDisplay 49) closeDisplay 0}]
```
File: [client\ClientData\EscapeMenu.sqf at line 28](../../../Src/client/ClientData/EscapeMenu.sqf#L28)
## ces_video

Type: constant

Description: 


Replaced value:
```sqf
5
```
File: [client\ClientData\EscapeMenu.sqf at line 30](../../../Src/client/ClientData/EscapeMenu.sqf#L30)
## set_ca_video

Type: constant

Description: 


Replaced value:
```sqf
301
```
File: [client\ClientData\EscapeMenu.sqf at line 32](../../../Src/client/ClientData/EscapeMenu.sqf#L32)
## ces_audio

Type: constant

Description: 


Replaced value:
```sqf
6
```
File: [client\ClientData\EscapeMenu.sqf at line 34](../../../Src/client/ClientData/EscapeMenu.sqf#L34)
## set_ca_audio

Type: constant

Description: 


Replaced value:
```sqf
302
```
File: [client\ClientData\EscapeMenu.sqf at line 36](../../../Src/client/ClientData/EscapeMenu.sqf#L36)
## ces_input

Type: constant

Description: 


Replaced value:
```sqf
4
```
File: [client\ClientData\EscapeMenu.sqf at line 38](../../../Src/client/ClientData/EscapeMenu.sqf#L38)
## set_ca_input

Type: constant

Description: 


Replaced value:
```sqf
303
```
File: [client\ClientData\EscapeMenu.sqf at line 40](../../../Src/client/ClientData/EscapeMenu.sqf#L40)
## getEscapeCtg

Type: constant

Description: 


Replaced value:
```sqf
(esc_widgets select 0)
```
File: [client\ClientData\EscapeMenu.sqf at line 47](../../../Src/client/ClientData/EscapeMenu.sqf#L47)
## getSettingsCtg

Type: constant

Description: 


Replaced value:
```sqf
(esc_settings_widgets select 0)
```
File: [client\ClientData\EscapeMenu.sqf at line 234](../../../Src/client/ClientData/EscapeMenu.sqf#L234)
## getSettingsList

Type: constant

Description: 


Replaced value:
```sqf
(esc_settings_widgets select 1)
```
File: [client\ClientData\EscapeMenu.sqf at line 236](../../../Src/client/ClientData/EscapeMenu.sqf#L236)
## getSettingsAccept

Type: constant

Description: 


Replaced value:
```sqf
(esc_settings_widgets select 2)
```
File: [client\ClientData\EscapeMenu.sqf at line 238](../../../Src/client/ClientData/EscapeMenu.sqf#L238)
## getSettingsAbort

Type: constant

Description: 


Replaced value:
```sqf
(esc_settings_widgets select 3)
```
File: [client\ClientData\EscapeMenu.sqf at line 240](../../../Src/client/ClientData/EscapeMenu.sqf#L240)
## ESC_GET_ALL_SETTINGS_TO_FADE

Type: constant

Description: 


Replaced value:
```sqf
[getSettingsAbort,getSettingsAccept,getSettingsList,getSettingsCtg]
```
File: [client\ClientData\EscapeMenu.sqf at line 243](../../../Src/client/ClientData/EscapeMenu.sqf#L243)
## SETTINGS_SIZE_X

Type: constant

Description: 


Replaced value:
```sqf
60
```
File: [client\ClientData\EscapeMenu.sqf at line 246](../../../Src/client/ClientData/EscapeMenu.sqf#L246)
## SETTINGS_SIZE_Y

Type: constant

Description: 


Replaced value:
```sqf
60
```
File: [client\ClientData\EscapeMenu.sqf at line 248](../../../Src/client/ClientData/EscapeMenu.sqf#L248)
## SETTINGS_MENU_BACKGROUND_COLOR_T3

Type: constant

Description: 


Replaced value:
```sqf
ESC_MENU_BACKGROUND_COLOR_T3
```
File: [client\ClientData\EscapeMenu.sqf at line 250](../../../Src/client/ClientData/EscapeMenu.sqf#L250)
## esc_isMenuOpened

Type: Variable

Description: 


Initial value:
```sqf
false
```
File: [client\ClientData\EscapeMenu.sqf at line 42](../../../Src/client/ClientData/EscapeMenu.sqf#L42)
## esc_widgets

Type: Variable

Description: 


Initial value:
```sqf
[widgetNull]
```
File: [client\ClientData\EscapeMenu.sqf at line 44](../../../Src/client/ClientData/EscapeMenu.sqf#L44)
## esc_buttonsData

Type: Variable

Description: 


Initial value:
```sqf
[...
```
File: [client\ClientData\EscapeMenu.sqf at line 64](../../../Src/client/ClientData/EscapeMenu.sqf#L64)
## esc_settings_widgets

Type: Variable

Description: 


Initial value:
```sqf
[widgetNull,widgetNull,widgetNull,widgetNull]
```
File: [client\ClientData\EscapeMenu.sqf at line 257](../../../Src/client/ClientData/EscapeMenu.sqf#L257)
## esc_settings_names

Type: Variable

Description: 


Initial value:
```sqf
[...
```
File: [client\ClientData\EscapeMenu.sqf at line 260](../../../Src/client/ClientData/EscapeMenu.sqf#L260)
## esc_settings_curIndex

Type: Variable

Description: 


Initial value:
```sqf
-1
```
File: [client\ClientData\EscapeMenu.sqf at line 267](../../../Src/client/ClientData/EscapeMenu.sqf#L267)
## cd_settingsVersion

Type: Variable

Description: 


Initial value:
```sqf
1.0
```
File: [client\ClientData\EscapeMenu.sqf at line 283](../../../Src/client/ClientData/EscapeMenu.sqf#L283)
## esc_internal_handleSettings

Type: function

Description: 
- Param: _closerEv
- Param: _openerEv

File: [client\ClientData\EscapeMenu.sqf at line 50](../../../Src/client/ClientData/EscapeMenu.sqf#L50)
## esc_openMenu

Type: function

Description: 
- Param: _isOpenedInLobby (optional, default false)

File: [client\ClientData\EscapeMenu.sqf at line 76](../../../Src/client/ClientData/EscapeMenu.sqf#L76)
## esc_confirmExit

Type: function

Description: 


File: [client\ClientData\EscapeMenu.sqf at line 136](../../../Src/client/ClientData/EscapeMenu.sqf#L136)
## esc_closeMenu

Type: function

Description: 


File: [client\ClientData\EscapeMenu.sqf at line 204](../../../Src/client/ClientData/EscapeMenu.sqf#L204)
## esc_settings_beginLoadSection

Type: function

Description: 
- Param: _newIndex

File: [client\ClientData\EscapeMenu.sqf at line 270](../../../Src/client/ClientData/EscapeMenu.sqf#L270)
## esc_settings_open

Type: function

Description: 


File: [client\ClientData\EscapeMenu.sqf at line 286](../../../Src/client/ClientData/EscapeMenu.sqf#L286)
## esc_settings_close

Type: function

Description: 
- Param: _isSaved (optional, default false)

File: [client\ClientData\EscapeMenu.sqf at line 349](../../../Src/client/ClientData/EscapeMenu.sqf#L349)
## esc_settings_clearSettingList

Type: function

Description: 


File: [client\ClientData\EscapeMenu.sqf at line 377](../../../Src/client/ClientData/EscapeMenu.sqf#L377)
# EscapeMenu_settingsGame.sqf

## SETTING_INDEX_NAME

Type: constant

Description: 


Replaced value:
```sqf
0
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 10](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L10)
## SETTING_INDEX_DESC

Type: constant

Description: 


Replaced value:
```sqf
1
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 11](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L11)
## SETTING_INDEX_TYPE

Type: constant

Description: 


Replaced value:
```sqf
2
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 12](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L12)
## SETTING_INDEX_RANGE

Type: constant

Description: 


Replaced value:
```sqf
3
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 13](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L13)
## SETTING_INDEX_VARNAME

Type: constant

Description: 


Replaced value:
```sqf
4
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 14](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L14)
## SETTING_INDEX_CURRENT

Type: constant

Description: 


Replaced value:
```sqf
5
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 15](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L15)
## SETTING_INDEX_DEFVALUE

Type: constant

Description: 


Replaced value:
```sqf
6
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 16](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L16)
## SETTING_INDEX_SERIALIZED

Type: constant

Description: 


Replaced value:
```sqf
7
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 17](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L17)
## SETTING_INDEX_EVENTONAPPLY

Type: constant

Description: 


Replaced value:
```sqf
8
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 18](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L18)
## SETTING_INDEX_EVENTONABORT

Type: constant

Description: 


Replaced value:
```sqf
9
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 19](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L19)
## SETTING_INDEX_EVENTONCHANGE

Type: constant

Description: 


Replaced value:
```sqf
10
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 20](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L20)
## SETTING_INDEX_STORAGE

Type: constant

Description: 


Replaced value:
```sqf
11
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 21](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L21)
## settingEx(name,desc,type,range,variable,event_on_apply,event_on_abort,event_on_change,storage)

Type: constant

Description: 
- Param: name
- Param: desc
- Param: type
- Param: range
- Param: variable
- Param: event_on_apply
- Param: event_on_abort
- Param: event_on_change
- Param: storage

Replaced value:
```sqf
[name,desc,type,range,#variable,variable,variable,variable,event_on_apply,event_on_abort,event_on_change,storage]
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 25](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L25)
## setting(name,desc,type,range,variable,event_on_apply,event_on_abort,event_on_change)

Type: constant

Description: 
- Param: name
- Param: desc
- Param: type
- Param: range
- Param: variable
- Param: event_on_apply
- Param: event_on_abort
- Param: event_on_change

Replaced value:
```sqf
settingEx(name,desc,type,range,variable,event_on_apply,event_on_abort,event_on_change,SETTING_STORAGE_SERVER)
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 25](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L25)
## settingTEvent(name,desc,type,range,variable,__EVNT__)

Type: constant

Description: 
- Param: name
- Param: desc
- Param: type
- Param: range
- Param: variable
- Param: __EVNT__

Replaced value:
```sqf
settingEx(name,desc,type,range,variable,__EVNT__,__EVNT__,__EVNT__,SETTING_STORAGE_SERVER)
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 30](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L30)
## settingLocal(name,desc,type,range,variable,event_on_apply,event_on_abort,event_on_change)

Type: constant

Description: 
- Param: name
- Param: desc
- Param: type
- Param: range
- Param: variable
- Param: event_on_apply
- Param: event_on_abort
- Param: event_on_change

Replaced value:
```sqf
settingEx(name,desc,type,range,variable,event_on_apply,event_on_abort,event_on_change,SETTING_STORAGE_LOCAL)
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 32](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L32)
## nextRegion(nameof)

Type: constant

Description: 
- Param: nameof

Replaced value:
```sqf
[nameof]
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 35](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L35)
## COUNT_REGION_SETTINGS

Type: constant

Description: 


Replaced value:
```sqf
1
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 37](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L37)
## COLOR_BACKGROUND_REGION_NAME

Type: constant

Description: 


Replaced value:
```sqf
[0.2,0.2,0.2,0.9]
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 39](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L39)
## SETTING_STORAGE_SERVER

Type: constant

Description: 


Replaced value:
```sqf
0
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 41](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L41)
## SETTING_STORAGE_LOCAL

Type: constant

Description: 


Replaced value:
```sqf
1
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 43](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L43)
## typeInputFloat

Type: constant

Description: 


Replaced value:
```sqf
0
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 46](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L46)
## typeSwitcher

Type: constant

Description: 


Replaced value:
```sqf
1
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 47](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L47)
## typeSlider

Type: constant

Description: 


Replaced value:
```sqf
2
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 48](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L48)
## typeBool

Type: constant

Description: 


Replaced value:
```sqf
3
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 49](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L49)
## typeVoipInput

Type: constant

Description: 


Replaced value:
```sqf
4
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 50](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L50)
## centerize(val)

Type: constant

Description: 
- Param: val

Replaced value:
```sqf
"<t align='center'>" + val + "</t>"
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 54](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L54)
## boolRange

Type: constant

Description: 


Replaced value:
```sqf
[centerize("нет"),centerize("да")]
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 57](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L57)
## defRange(min,max)

Type: constant

Description: 
- Param: min
- Param: max

Replaced value:
```sqf
([min,max] call cd_internal_defRange)
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 59](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L59)
## voipInputRange(min,max,precision)

Type: constant

Description: 
- Param: min
- Param: max
- Param: precision

Replaced value:
```sqf
([min,max,precision] call cd_internal_voipInputRange)
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 61](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L61)
## NO_EVENT_ON_APPLY

Type: constant

Description: 


Replaced value:
```sqf
""
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 70](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L70)
## value

Type: constant

Description: 


Replaced value:
```sqf
cd_esc_settings_internal_curChangedValue
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 72](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L72)
## setting_element_size_x

Type: constant

Description: 


Replaced value:
```sqf
10
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 318](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L318)
## cd_esc_settings_internal_curChangedValue

Type: Variable

Description: 


Initial value:
```sqf
0
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 75](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L75)
## cd_settingsGame

Type: Variable

Description: 


Initial value:
```sqf
[...
```
File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 104](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L104)
## cd_internal_defRange

Type: function

Description: 
- Param: _mi
- Param: _ma

File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 64](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L64)
## cd_internal_voipInputRange

Type: function

Description: 
- Param: _mi
- Param: _ma
- Param: _prec

File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 66](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L66)
## esc_settings_game_isVoipConnected

Type: function

Description: 


File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 146](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L146)
## esc_settings_game_sanitizeVoipValue

Type: function

Description: 
- Param: _value (optional, default 1)

File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 152](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L152)
## esc_settings_game_formatVoipValue

Type: function

Description: 
- Param: _value
- Param: _precision (optional, default 1)

File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 161](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L161)
## esc_settings_game_updateVoipValueText

Type: function

Description: 
- Param: _wid
- Param: _value
- Param: _precision (optional, default 1)

File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 167](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L167)
## esc_settings_game_updateVoipTestButton

Type: function

Description: 


File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 180](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L180)
## esc_settings_game_stopVoipTest

Type: function

Description: 


File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 194](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L194)
## esc_settings_game_applyVoipValue

Type: function

Description: 
- Param: _value

File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 203](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L203)
## esc_settings_game_prepareLocalState

Type: function

Description: 


File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 225](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L225)
## esc_settings_game_onLeaveSection

Type: function

Description: 


File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 247](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L247)
## esc_settings_game_unloading

Type: function

Description: 
- Param: _mode

File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 254](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L254)
## esc_settings_loader_game

Type: function

Description: 


File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 314](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L314)
## esc_settings_eventOnInput

Type: function

Description: 
- Param: _bt
- Param: _key

File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 446](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L446)
## esc_settings_eventOnSwitcher

Type: function

Description: 
- Param: _bt

File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 464](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L464)
## esc_settings_eventOnSlider

Type: function

Description: 
- Param: _bt
- Param: _newValue

File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 488](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L488)
## esc_settings_eventOnBool

Type: function

Description: 
- Param: _bt

File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 503](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L503)
## esc_settings_eventOnVoipSlider

Type: function

Description: 
- Param: _bt
- Param: _newValue

File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 525](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L525)
## esc_settings_eventOnVoipTestButton

Type: function

Description: 
- Param: _bt

File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 555](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L555)
## esc_settings_event_onSyncGame

Type: function

Description: 


File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 572](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L572)
## cd_onLoadGameSettings

Type: function

Description: 
- Param: _list

File: [client\ClientData\EscapeMenu_settingsGame.sqf at line 581](../../../Src/client/ClientData/EscapeMenu_settingsGame.sqf#L581)
# EscapeMenu_settingsGraphics.sqf

## setting_element_size_x

Type: constant

Description: 


Replaced value:
```sqf
10
```
File: [client\ClientData\EscapeMenu_settingsGraphics.sqf at line 14](../../../Src/client/ClientData/EscapeMenu_settingsGraphics.sqf#L14)
## esc_settings_loader_graphic

Type: function

Description: 


File: [client\ClientData\EscapeMenu_settingsGraphics.sqf at line 11](../../../Src/client/ClientData/EscapeMenu_settingsGraphics.sqf#L11)
# EscapeMenu_settingsKeyboard.sqf

## setting_element_size_x

Type: constant

Description: 


Replaced value:
```sqf
10
```
File: [client\ClientData\EscapeMenu_settingsKeyboard.sqf at line 14](../../../Src/client/ClientData/EscapeMenu_settingsKeyboard.sqf#L14)
## __handled_event_type__

Type: constant

Description: 


Replaced value:
```sqf
"KeyUp"
```
File: [client\ClientData\EscapeMenu_settingsKeyboard.sqf at line 135](../../../Src/client/ClientData/EscapeMenu_settingsKeyboard.sqf#L135)
## esc_settings_loader_keyboard

Type: function

Description: 


File: [client\ClientData\EscapeMenu_settingsKeyboard.sqf at line 10](../../../Src/client/ClientData/EscapeMenu_settingsKeyboard.sqf#L10)
## esc_settings_onUpdateKeybinds

Type: function

Description: 
- Param: _enableAllButtons (optional, default false)

File: [client\ClientData\EscapeMenu_settingsKeyboard.sqf at line 58](../../../Src/client/ClientData/EscapeMenu_settingsKeyboard.sqf#L58)
## esc_settings_keyboard_changeButton

Type: function

Description: 
- Param: _button
- Param: _code
- Param: _shift
- Param: _control
- Param: _alt

File: [client\ClientData\EscapeMenu_settingsKeyboard.sqf at line 107](../../../Src/client/ClientData/EscapeMenu_settingsKeyboard.sqf#L107)
## esc_settings_event_onSyncKeyboard

Type: function

Description: 


File: [client\ClientData\EscapeMenu_settingsKeyboard.sqf at line 200](../../../Src/client/ClientData/EscapeMenu_settingsKeyboard.sqf#L200)
# EyeHandler.sqf

## check_state(str,action)

Type: constant

Description: 
- Param: str
- Param: action

Replaced value:
```sqf
if equals('str',_changeStateReason) exitWith {action}
```
File: [client\ClientData\EyeHandler.sqf at line 27](../../../Src/client/ClientData/EyeHandler.sqf#L27)
## cd_eyeState

Type: Variable

Description: 


Initial value:
```sqf
1 // 0 - ok > 0 - closed
```
File: [client\ClientData\EyeHandler.sqf at line 10](../../../Src/client/ClientData/EyeHandler.sqf#L10)
## cd_isEyesClosed

Type: function

Description: 


File: [client\ClientData\EyeHandler.sqf at line 13](../../../Src/client/ClientData/EyeHandler.sqf#L13)
## cd_onChangeEyeState

Type: function

Description: 
- Param: _newState
- Param: _changeStateReason

File: [client\ClientData\EyeHandler.sqf at line 16](../../../Src/client/ClientData/EyeHandler.sqf#L16)
# SendCommand.sqf

## SC_SIZE_W

Type: constant

Description: 


Replaced value:
```sqf
40
```
File: [client\ClientData\SendCommand.sqf at line 12](../../../Src/client/ClientData/SendCommand.sqf#L12)
## SC_SIZE_H

Type: constant

Description: 


Replaced value:
```sqf
30
```
File: [client\ClientData\SendCommand.sqf at line 14](../../../Src/client/ClientData/SendCommand.sqf#L14)
## CD_MAX_COMMANDS_HISTORY_COUNT

Type: constant

Description: 


Replaced value:
```sqf
100
```
File: [client\ClientData\SendCommand.sqf at line 17](../../../Src/client/ClientData/SendCommand.sqf#L17)
## localCommand(name)

Type: constant

Description: 
- Param: name

Replaced value:
```sqf
_cd_map_dataCode = []; cd_commands_localCommandsList set [name,_cd_map_dataCode]; _cd_map_dataCode pushBack
```
File: [client\ClientData\SendCommand.sqf at line 315](../../../Src/client/ClientData/SendCommand.sqf#L315)
## arguments

Type: constant

Description: 


Replaced value:
```sqf
cd_internal_cmd_thisArguments
```
File: [client\ClientData\SendCommand.sqf at line 318](../../../Src/client/ClientData/SendCommand.sqf#L318)
## cd_commandHistoryBuffer

Type: Variable

Description: 


Initial value:
```sqf
[]
```
File: [client\ClientData\SendCommand.sqf at line 20](../../../Src/client/ClientData/SendCommand.sqf#L20)
## cd_commandHistoryBuffer

Type: Variable

> Exists if **EDITOR** not defined

Description: 


Initial value:
```sqf
[]
```
File: [client\ClientData\SendCommand.sqf at line 31](../../../Src/client/ClientData/SendCommand.sqf#L31)
## cd_commands_localCommandsList

Type: Variable

Description: 


Initial value:
```sqf
createHashMap
```
File: [client\ClientData\SendCommand.sqf at line 312](../../../Src/client/ClientData/SendCommand.sqf#L312)
## cd_openSendCommandWindow

Type: function

Description: 
- Param: _isLobbyContext (optional, default false)

File: [client\ClientData\SendCommand.sqf at line 36](../../../Src/client/ClientData/SendCommand.sqf#L36)
## cd_closeSendCommandWindow

Type: function

Description: 


File: [client\ClientData\SendCommand.sqf at line 269](../../../Src/client/ClientData/SendCommand.sqf#L269)
## cd_openAhelp

Type: function

Description: 


File: [client\ClientData\SendCommand.sqf at line 285](../../../Src/client/ClientData/SendCommand.sqf#L285)
## cd_onLocalCmdCall

Type: function

Description: 
- Param: _cmd
- Param: _args (optional, default 0)

File: [client\ClientData\SendCommand.sqf at line 299](../../../Src/client/ClientData/SendCommand.sqf#L299)
# VersionViewer.sqf

## versionviewer_timeout_init_clientname

Type: constant

Description: 


Replaced value:
```sqf
30
```
File: [client\ClientData\VersionViewer.sqf at line 13](../../../Src/client/ClientData/VersionViewer.sqf#L13)
## versionviewer_size_x

Type: constant

Description: 


Replaced value:
```sqf
14
```
File: [client\ClientData\VersionViewer.sqf at line 16](../../../Src/client/ClientData/VersionViewer.sqf#L16)
## versionviewer_size_y

Type: constant

Description: 


Replaced value:
```sqf
10
```
File: [client\ClientData\VersionViewer.sqf at line 18](../../../Src/client/ClientData/VersionViewer.sqf#L18)
## cd_vv_widgets

Type: Variable

Description: 


Initial value:
```sqf
[_ctg,_back,_txt]
```
File: [client\ClientData\VersionViewer.sqf at line 33](../../../Src/client/ClientData/VersionViewer.sqf#L33)
## cd_vv_syncVisual

Type: function

Description: 
- Param: _cliName (optional, default cd_clientName)

File: [client\ClientData\VersionViewer.sqf at line 36](../../../Src/client/ClientData/VersionViewer.sqf#L36)
