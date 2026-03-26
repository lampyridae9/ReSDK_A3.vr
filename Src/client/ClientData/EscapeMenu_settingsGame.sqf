// ======================================================
// Copyright (c) 2017-2026 the ReSDK_A3 project
// sdk.relicta.ru
// ======================================================

#include "..\..\host\lang.hpp"
namespace(clientData,cd_)

enum(EscapeSettingDataIndex,SETTING_INDEX_)
#define SETTING_INDEX_NAME 0
#define SETTING_INDEX_DESC 1
#define SETTING_INDEX_TYPE 2
#define SETTING_INDEX_RANGE 3
#define SETTING_INDEX_VARNAME 4
#define SETTING_INDEX_CURRENT 5
#define SETTING_INDEX_DEFVALUE 6
#define SETTING_INDEX_SERIALIZED 7
#define SETTING_INDEX_EVENTONAPPLY 8
#define SETTING_INDEX_EVENTONABORT 9
#define SETTING_INDEX_EVENTONCHANGE 10
#define SETTING_INDEX_STORAGE 11
enumend

inline_macro
#define settingEx(name,desc,type,range,variable,event_on_apply,event_on_abort,event_on_change,storage) [name,desc,type,range,#variable,variable,variable,variable,event_on_apply,event_on_abort,event_on_change,storage]
inline_macro
#define setting(name,desc,type,range,variable,event_on_apply,event_on_abort,event_on_change) settingEx(name,desc,type,range,variable,event_on_apply,event_on_abort,event_on_change,SETTING_STORAGE_SERVER)
//Тоже что и setting но использует общее событие
inline_macro
#define settingTEvent(name,desc,type,range,variable,__EVNT__) settingEx(name,desc,type,range,variable,__EVNT__,__EVNT__,__EVNT__,SETTING_STORAGE_SERVER)
inline_macro
#define settingLocal(name,desc,type,range,variable,event_on_apply,event_on_abort,event_on_change) settingEx(name,desc,type,range,variable,event_on_apply,event_on_abort,event_on_change,SETTING_STORAGE_LOCAL)

inline_macro
#define nextRegion(nameof) [nameof]
macro_const(cd_COUNT_REGION_SETTINGS)
#define COUNT_REGION_SETTINGS 1
macro_const(cd_COLOR_BACKGROUND_REGION_NAME)
#define COLOR_BACKGROUND_REGION_NAME [0.2,0.2,0.2,0.9]
macro_const(cd_SETTING_STORAGE_SERVER)
#define SETTING_STORAGE_SERVER 0
macro_const(cd_SETTING_STORAGE_LOCAL)
#define SETTING_STORAGE_LOCAL 1

enum(EscapeSettingDataType,type)
#define typeInputFloat 0
#define typeSwitcher 1
#define typeSlider 2
#define typeBool 3
#define typeVoipInput 4
enumend

inline_macro
#define centerize(val) "<t align='center'>" + val + "</t>"

macro_const(cd_boolRange)
#define boolRange [centerize("нет"),centerize("да")]
inline_macro
#define defRange(min,max) ([min,max] call cd_internal_defRange)
inline_macro
#define voipInputRange(min,max,precision) ([min,max,precision] call cd_internal_voipInputRange)

decl(float[](float;float))
cd_internal_defRange = { params ["_mi","_ma"]; [_mi,_ma] };
decl(float[](float;float;float))
cd_internal_voipInputRange = { params ["_mi","_ma","_prec"]; [_mi,_ma,_prec] };

//отключенное событие просто будет устанавливать переменную по имени из SETTING_INDEX_VARNAME
macro_const(cd_NO_EVENT_ON_APPLY)
#define NO_EVENT_ON_APPLY ""

#define value cd_esc_settings_internal_curChangedValue

decl(any)
cd_esc_settings_internal_curChangedValue = 0;

// !!! only debug !!!
decl(float) somedebugvar1 = 1;
decl(float) somedebugvar2 = 1;
decl(bool) testbool = false;
decl(float) cd_voipVolSetting = 1;
decl(bool) cd_voipTestEnabled = false;
decl(bool) cd_voipSessionPrepared = false;
decl(widget[]) cd_voipWidgets = [widgetNull,widgetNull,widgetNull,widgetNull];

private _voipSettingCallbacks = [
	{
		value = [value] call esc_settings_game_sanitizeVoipValue;
		profileNamespace setVariable ["rel_voipvol",value];
		saveProfileNamespace;
		[value] call esc_settings_game_applyVoipValue;
		call esc_settings_game_stopVoipTest;
	},{
		value = [value] call esc_settings_game_sanitizeVoipValue;
		[value] call esc_settings_game_applyVoipValue;
		call esc_settings_game_stopVoipTest;
	},{
		value = [value] call esc_settings_game_sanitizeVoipValue;
		[value] call esc_settings_game_applyVoipValue;
	}
];

decl(any[])
cd_settingsGame = [
/*	nextRegion("Основные"),
	setting("Скрывать чат","Скрывает чат если нет новых сообщений",typeBool,boolRange,chat_isHideEnabled,NO_EVENT_ON_APPLY),
	setting("Время до скрытия чата","Через сколько секунд будет скрыт чат",typeInputFloat,defRange(0,60 * 5),chat_fadetime,NO_EVENT_ON_APPLY),
	nextRegion("Дополнительные"),
	setting("Тройная настройка","С 3 возможными режимами",typeSwitcher,[1 arg 10 arg 100],somedebugvar1,NO_EVENT_ON_APPLY),
	setting("Слайдерная настройка: %1","крути-верти!",typeSlider,defRange(1,10),somedebugvar2,NO_EVENT_ON_APPLY)*/
	nextRegion("Звук"),
	//nextRegion("	- не реализовано"), 
	setting("Музыка в лобби","Проигрывает музыку в лобби",typeBool,boolRange,lobby_isMusicEnabled,{lobby_isMusicEnabled = value; [lobby_isMusicEnabled] call lobby_handleMusic;}, {}, {}),
	settingLocal("Громкость VOIP","Регулирует громкость входящего войса.\nИзменение сохраняется локально в профиле.\n\nДефолтное значение: 1\nЗначения выше 1 усиливают звук.\nКнопка справа включает тестовый звук.",typeVoipInput,voipInputRange(0,10,1),cd_voipVolSetting,_voipSettingCallbacks select 0,_voipSettingCallbacks select 1,_voipSettingCallbacks select 2),
	nextRegion("Чат"),
	settingTEvent("Ширина","Ширина окна чата в процентах:\n\nМинимум: 20%\nМаксимум: 100%",typeSlider,defRange(20,100),chat_size_x,{[true] call chat_restoreVisible; chat_size_x = value; call chat_syncsize}),
	settingTEvent("Высота","Высота окна чата в процентах:\n\nМинимум: 15%\nМаксимум: 100%",typeSlider,defRange(15,100),chat_size_y,{[true] call chat_restoreVisible; chat_size_y = value; call chat_syncsize}),
	settingTEvent("Скрывать чат","Скрывает чат если нет новых сообщений по таймеру",typeBool,boolRange,chat_isHideEnabled,{chat_isHideEnabled = value; [false] call chat_restoreVisible;}),
	settingTEvent("Время до скрытия чата","Через сколько секунд будет скрыт чат\nесли нет новых сообщений\n\nМинимум: 1 сек\nМаксимум: 5 мин",typeInputFloat,defRange(1,60 * 5),chat_hideAfter,{chat_hideAfter = value; [false] call chat_restoreVisible;}),
	
	nextRegion("Интерфейс"),
	setting("Инвентарь по удержанию","Переключает режим открытия инвентаря с нажатия на удержание",typeBool,boolRange,inventory_isHoldMode,{inventory_isHoldMode= value ;}, {}, {}),
	//setting("Отключить интерфейс","Полностью выключает отображение GUI элементов",typeBool,boolRange,testbool,{  }, {}, {}),
	
	setting("Скрывать иконки рук","Скрывает иконки рук по таймеру при закрытом инвентаре",typeBool,boolRange,inventory_canHideHands,{[value] call inventory_setHideHands;}, {}, {}),
	setting("Время до скрытия иконок рук","Через сколько секунд будут скрыты иконки рук\n\nМинимум: 1 сек\nМаксимум: 60 сек",typeInputFloat,defRange(1,60),inventory_hideafter,{inventory_hideafter= value;[true]call inventory_restoreHide;}, {}, {}),
	
	//setting("Сохранять позицию мыши в инвентаре","Сохраняет позицию мыши при повторном открытии инвентаря",typeBool,boolRange,testbool,{}, {}, {}),
	
	//NON USABLE
	//setting("Скрывать статусы","Скрывает статусы по таймеру",typeBool,boolRange,hud_canHide,{hud_canHide= value;call hud_updateTimestamp;[false arg false]call hud_hide_reset;}, {}, {}),
	//setting("Время до скрытия статусов","Через сколько секунд будут скрыты иконки рук\n\nМинимум: 1 сек\nМаксимум: 60 сек",typeInputFloat,defRange(1,60),hud_hideAfter,{hud_hideAfter=value; call hud_updateTimestamp;}, {}, {}),
	
	nextRegion("Отладка"),
	setting("Включить отображение отладчика","Активирует окно с основной системной информацией",typeBool,boolRange,clistat_isEnabled,{[value] call clistat_setLogVars;}, {}, {}),
	setting("Перезагрузить освещение (ОТКЛЮЧЕНО)","Перезагружает все источники света",typeBool,boolRange,testbool,{ }, {}, {})
];

decl(int)
cd_settingsGame_idxVoip = cd_settingsGame findif {
	count _x != COUNT_REGION_SETTINGS &&
	{(_x select SETTING_INDEX_VARNAME) == "cd_voipVolSetting"}
};

decl(bool())
esc_settings_game_isVoipConnected = {
	(missionNamespace getVariable ["vs_useReVoice",false]) &&
	{call (missionNamespace getVariable ["vs_isConnectedVoice",{false}])}
};

decl(float(any))
esc_settings_game_sanitizeVoipValue = {
	params [["_value",1]];
	if not_equalTypes(_value,0) then {
		_value = 1;
	};
	clamp(_value,0,10)
};

decl(string(any;int))
esc_settings_game_formatVoipValue = {
	params ["_value",["_precision",1]];
	([_value] call esc_settings_game_sanitizeVoipValue) toFixed _precision
};

decl(void(widget;any;int))
esc_settings_game_updateVoipValueText = {
	params ["_wid","_value",["_precision",1]];
	if equals(_wid,widgetNull) exitWith {};
	private _textVal = [_value arg _precision] call esc_settings_game_formatVoipValue;
	private _textColor = call {
		if (_value > 1) exitWith {"#E05B5B"};
		if (_value <= 1) exitWith {"#62C462"};
		"#FFFFFF"
	};
	[_wid,format["<t align='center' color='%2'>%1</t>",_textVal,_textColor]] call widgetSetText;
};

decl(void())
esc_settings_game_updateVoipTestButton = {
	private _bt = cd_voipWidgets select 2;
	if (_bt isEqualTo widgetNull) exitWith {};

	if (call esc_settings_game_isVoipConnected) then {
		_bt ctrlEnable true;
		_bt ctrlSetText (["Тест выкл","Тест вкл"] select cd_voipTestEnabled);
	} else {
		_bt ctrlEnable false;
		_bt ctrlSetText "Тест н/д";
	};
};

decl(void())
esc_settings_game_stopVoipTest = {
	if (cd_voipTestEnabled && {call esc_settings_game_isVoipConnected}) then {
		[false] call vs_setTestVolumeMode;
	};
	cd_voipTestEnabled = false;
	call esc_settings_game_updateVoipTestButton;
};

decl(void(any))
esc_settings_game_applyVoipValue = {
	params ["_value"];
	_value = [_value] call esc_settings_game_sanitizeVoipValue;
	cd_voipVolSetting = _value;
	vs_voipVolCurrent = _value;

	if (call esc_settings_game_isVoipConnected) then {
		[_value] call vs_setMasterVoiceVolume;
	};

	private _wid = cd_voipWidgets select 1;
	private _precision = 1;
	if (cd_settingsGame_idxVoip >= 0) then {
		private _range = cd_settingsGame select cd_settingsGame_idxVoip select SETTING_INDEX_RANGE;
		if (count _range > 2) then {
			_precision = _range select 2;
		};
	};
	[_wid,_value,_precision] call esc_settings_game_updateVoipValueText;
};

decl(void())
esc_settings_game_prepareLocalState = {
	if (cd_voipSessionPrepared) exitWith {};

	private _valueCurrent = missionNamespace getVariable ["vs_voipVolCurrent",1];
	_valueCurrent = [_valueCurrent] call esc_settings_game_sanitizeVoipValue;

	cd_voipVolSetting = _valueCurrent;
	vs_voipVolCurrent = _valueCurrent;
	cd_voipTestEnabled = false;
	cd_voipWidgets = [widgetNull,widgetNull,widgetNull,widgetNull];

	if (cd_settingsGame_idxVoip >= 0) then {
		private _entry = cd_settingsGame select cd_settingsGame_idxVoip;
		_entry set [SETTING_INDEX_CURRENT,_valueCurrent];
		_entry set [SETTING_INDEX_DEFVALUE,_valueCurrent];
		_entry set [SETTING_INDEX_SERIALIZED,_valueCurrent];
	};

	cd_voipSessionPrepared = true;
};

decl(void())
esc_settings_game_onLeaveSection = {
	call esc_settings_game_stopVoipTest;
	cd_voipWidgets = [widgetNull,widgetNull,widgetNull,widgetNull];
};

//событие выгрузки текущих настроек
decl(void(bool))
esc_settings_game_unloading = {
	private _mode = _this;
	call esc_settings_game_stopVoipTest;
	cd_voipWidgets = [widgetNull,widgetNull,widgetNull,widgetNull];
	if (_mode) then {
		
		private _serverSettings = [];
		
		_evc = null;
		{
			if (count _x == COUNT_REGION_SETTINGS) then {continue};
			
			// уже установленные настройки не применяются
			if equals(_x select SETTING_INDEX_CURRENT,_x select SETTING_INDEX_SERIALIZED) then {continue};
			
			_evc = _x select SETTING_INDEX_EVENTONAPPLY;
			if not_equals(_evc,"") then {
				value = _x select SETTING_INDEX_CURRENT;
				if equalTypes(_evc,"") then {
					call (missionNamespace getvariable [_evc,{}]);
				} else {
					call _evc;
				};
			} else {
				missionNamespace setVariable [_x select SETTING_INDEX_VARNAME,_x select SETTING_INDEX_CURRENT];
			};	
			
			if ((_x select SETTING_INDEX_STORAGE) == SETTING_STORAGE_SERVER) then {
				private _data = [tolower (_x select SETTING_INDEX_VARNAME),_x select SETTING_INDEX_CURRENT];
				_serverSettings pushBack _data;
				if equals(_x select SETTING_INDEX_CURRENT,_x select SETTING_INDEX_DEFVALUE) then {
					_data pushBack true;
				};
			};
		} foreach cd_settingsGame;
		
		//Отсылаем серверу настройки игры
		if (count _serverSettings > 0) then {
			rpcSendToServer("syncGameSettings",[_serverSettings arg clientOwner]);
		};
		
		{
			if (count _x == COUNT_REGION_SETTINGS) then {continue};
			(cd_settingsGame select _forEachIndex) set [SETTING_INDEX_SERIALIZED,_x select SETTING_INDEX_CURRENT];
		} foreach cd_settingsGame;
	} else {
		{
			if (count _x == COUNT_REGION_SETTINGS) then {continue};
			
			//Если настройка отличается от сериализованной вызываем событие onabort
			if not_equals(_x select SETTING_INDEX_CURRENT,_x select SETTING_INDEX_SERIALIZED) then {
				value = _x select SETTING_INDEX_SERIALIZED;
				call (_x select SETTING_INDEX_EVENTONABORT);
			};
			
			(cd_settingsGame select _forEachIndex) set [SETTING_INDEX_CURRENT,_x select SETTING_INDEX_SERIALIZED]
		} foreach cd_settingsGame;
	};
};
decl(void())
esc_settings_loader_game = {

	if !([2] call esc_settings_beginLoadSection) exitWith {};

	#define setting_element_size_x 10

	private _ctg = getSettingsList;

	private _setList = count cd_settingsGame;
	private _d = getDisplay;

	call esc_settings_game_prepareLocalState;
	call esc_settings_clearSettingList;

	_data = [];

	cd_voipWidgets = [widgetNull,widgetNull,widgetNull,widgetNull];

	//_applyType: 0 simple text (ctrlSetText), 1 call widgetSetText , 2 slider
	_allocType = {
		params ["_t"];
		call {
			if (_t == typeInputFloat) exitWith {[INPUT,["KeyDown",esc_settings_eventOnInput],3]};
			if (_t == typeSwitcher) exitWith {[BUTTON,["MouseButtonUp",esc_settings_eventOnSwitcher],0]};
			if (_t == typeSlider) exitWith {[SLIDERWNEW,["SliderPosChanged",esc_settings_eventOnSlider],2]};
			if (_t == typeBool) exitWith {[TEXT,["MouseButtonUp",esc_settings_eventOnBool],1]};
			if (_t == typeVoipInput) exitWith {[WIDGETGROUP,[],4]};
		}
	};

	for "_i" from 0 to _setList - 1 do {
		_setReg = (cd_settingsGame select _i);
		if (count _setReg == COUNT_REGION_SETTINGS) then {
			_minz = (20 * setting_element_size_x / 100);
			_dbt = [_d,TEXT,[0,setting_element_size_x * _i + _minz,100,setting_element_size_x -_minz*2],_ctg] call createWidget;
			[_dbt, centerize((_setReg select 0))] call widgetSetText;
			
			_dbt setBackgroundColor COLOR_BACKGROUND_REGION_NAME;
			_data pushBack [_dbt,widgetNull];
			continue;
		};	
		_setReg params ["_name","_desc","_type","_range","_var","_cur","_defval","_sv"];
		_dbt = [_d,TEXT,[0,setting_element_size_x * _i,50,setting_element_size_x],_ctg] call createWidget;
		_dbt ctrlSetTooltip _desc;
		[_dbt,_name] call widgetSetText;
		_dbt setvariable ["srcText",_name];

		([_type] call _allocType) params ["_wtype","_evtype","_applyType"];

		if (_applyType == 4) then {
			private _datGroup = [_d,_wtype,[50,setting_element_size_x * _i,50,setting_element_size_x],_ctg] call createWidget;
			private _slider = [_d,SLIDERWNEW,[0,0,56,100],_datGroup] call createWidget;
			private _valueText = [_d,TEXT,[58,0,14,100],_datGroup] call createWidget;
			private _toggle = [_d,BUTTON,[74,0,26,100],_datGroup] call createWidget;

			_slider ctrlAddEventHandler ["SliderPosChanged",esc_settings_eventOnVoipSlider];
			_toggle ctrlAddEventHandler ["MouseButtonUp",esc_settings_eventOnVoipTestButton];

			{
				_x ctrlSetTooltip _desc;
			} foreach [_slider,_valueText,_toggle];

			_slider setVariable ["index",_i];
			_slider setVariable ["range",_range];
			_slider setVariable ["valueText",_valueText];

			_toggle setVariable ["index",_i];

			_valueText setBackgroundColor [0.1,0.1,0.1,0.4];

				cd_voipWidgets = [_slider,_valueText,_toggle,_datGroup];

				__f_init = true;
				_slider sliderSetRange (_range select [0,2]);
				_slider sliderSetSpeed [0.1,0.1];
				_slider sliderSetPosition _cur;
				[_slider,_cur] call esc_settings_eventOnVoipSlider;
				call esc_settings_game_updateVoipTestButton;

			_data append [_dbt,_slider,_valueText,_toggle,_datGroup];
			continue;
		};

		_dat = [_d,_wtype,[50,setting_element_size_x * _i,50,setting_element_size_x],_ctg] call createWidget;
		_dat ctrlAddEventHandler _evtype;


		_dat setvariable ["index",_i];
		_dat setvariable ["range",_range];
		_dat setVariable ["src",_dbt];
		
		__f_init = true;
		
		call {
			//float input
			if (_applyType == 3) exitWith {
				_value = _cur;
				if not_equalTypes(_value,"") then {_value = str _value};
				_dat ctrlSetText _value;
			};
			//bool
			if (_applyType == 1) exitWith {
				_dat setvariable ["curvalue",!_cur];
				[_dat] call esc_settings_eventOnBool;
			};
			//slider
			if (_applyType == 2) exitWith {
				_dat sliderSetRange _range;
				_value = _cur;
				_dat sliderSetPosition _value;
				[_dat,_value] call esc_settings_eventOnSlider;
			};
			//switcher
			if (_applyType == 0) exitWith {
				_value = _cur;
				_dat setVariable ["curIdx",_range find _value];
				if not_equalTypes(_value,"") then {_value = str _value};
				_dat ctrlSetText _value;
			};
		};


		_data pushBack [_dbt,_dat];

	};

	_ctg setvariable ["listData",_data];

};

//событие ввода
decl(void(widget;int))
esc_settings_eventOnInput = {
	params ["_bt","_key"];

	_value = parseNumber((parseNumber( ctrlText _bt)) toFixed 4);
	(_bt getvariable "range") params ["_min","_max"];
	if (_value < _min) exitWith {_bt ctrlSetText str _min};
	if (_value > _max) exitWith {_bt ctrlSetText str _max};
	//if (str _value != ctrlText _value) exitWith {_bt ctrlSetText str _min}; //non-numbers
	
	cd_settingsGame select (_bt getvariable "index") set [SETTING_INDEX_CURRENT,_value];
	
	if !isNullVar(__f_init) exitWith {};
	value = _value;
	call (cd_settingsGame select (_bt getVariable "index") select SETTING_INDEX_EVENTONCHANGE);
};

//событие переключателя
decl(void(widget))
esc_settings_eventOnSwitcher = {
	params ["_bt"];
	_curIdx = _bt getVariable "curIdx";
	_rangeArr = _bt getVariable "range";

	INC(_curIdx);

	if (_curIdx >= count _rangeArr) then {_curIdx = 0};
	_newval = _rangeArr select _curIdx;
	if not_equalTypes(_newval,"") then {_newval = str _newval};
	
	_bt ctrlSetText _newval;

	_bt setVariable ["curIdx",_curIdx];
	
	cd_settingsGame select (_bt getvariable "index") set [SETTING_INDEX_CURRENT,_newval];
	
	if !isNullVar(__f_init) exitWith {};
	value = _newval;
	call (cd_settingsGame select (_bt getVariable "index") select SETTING_INDEX_EVENTONCHANGE);
};

// событие слайдера
decl(void(widget;float))
esc_settings_eventOnSlider = {
	params ["_bt", "_newValue"];

	_dbt = _bt getVariable "src";
	[_dbt,format[_dbt getvariable "srcText",_newValue]] call widgetSetText;
	
	cd_settingsGame select (_bt getvariable "index") set [SETTING_INDEX_CURRENT,_newValue];
	
	if !isNullVar(__f_init) exitWith {};
	value = _newValue;
	call (cd_settingsGame select (_bt getVariable "index") select SETTING_INDEX_EVENTONCHANGE);
};

// событие бинарного условия
decl(void(widget))
esc_settings_eventOnBool = {
	params ["_bt"];

	private _idx = _bt getvariable "index";
	
	_newCurValue = !(_bt getvariable "curvalue");
	_bt setvariable ["curvalue",_newCurValue];

	private _pickedText = (_bt getVariable "range") select _newCurValue;

	[_bt,_pickedText] call widgetSetText;


	cd_settingsGame select (_bt getvariable "index") set [SETTING_INDEX_CURRENT,_newCurValue];
	
	if !isNullVar(__f_init) exitWith {};
	value = _newCurValue;
	call (cd_settingsGame select _idx select SETTING_INDEX_EVENTONCHANGE);
};

// событие локального слайдера VOIP
decl(void(widget;float))
esc_settings_eventOnVoipSlider = {
	params ["_bt", "_newValue"];

	if (_bt getVariable ["voip_syncing",false]) exitWith {};

	private _range = _bt getVariable "range";
	_range params ["_min","_max",["_precision",1]];

	_newValue = (_newValue max _min) min _max;
	_newValue = parseNumber (_newValue toFixed _precision);

	if (abs (_newValue - sliderPosition _bt) > 0.0001) then {
		_bt setVariable ["voip_syncing",true];
		_bt sliderSetPosition _newValue;
		_bt setVariable ["voip_syncing",false];
	};

	private _idx = _bt getVariable "index";
	private _valueText = _bt getVariable ["valueText",widgetNull];

	cd_settingsGame select _idx set [SETTING_INDEX_CURRENT,_newValue];
	[_valueText,_newValue,_precision] call esc_settings_game_updateVoipValueText;

	if !isNullVar(__f_init) exitWith {};
	value = _newValue;
	call (cd_settingsGame select _idx select SETTING_INDEX_EVENTONCHANGE);
};

// событие переключения теста VOIP
decl(void(widget))
esc_settings_eventOnVoipTestButton = {
	params ["_bt"];

	if !(call esc_settings_game_isVoipConnected) exitWith {
		cd_voipTestEnabled = false;
		call esc_settings_game_updateVoipTestButton;
	};

	private _newState = !cd_voipTestEnabled;
	private _isSuccess = [_newState] call vs_setTestVolumeMode;
	cd_voipTestEnabled = if (_isSuccess) then {_newState} else {false};
	call esc_settings_game_updateVoipTestButton;
};


//событие синхронизирует все внешние изменения клавиш
decl(void())
esc_settings_event_onSyncGame = {
	{
		if (count _x == COUNT_REGION_SETTINGS) then {continue};
		if ((_x select SETTING_INDEX_STORAGE) == SETTING_STORAGE_LOCAL) then {continue};
		cd_settingsGame select _forEachIndex set [SETTING_INDEX_CURRENT,missionNamespace getVariable (_x select SETTING_INDEX_VARNAME)]
	} foreach cd_settingsGame;
};

decl(void(...any[]))
cd_onLoadGameSettings = {
	private _list = _this;
	private _listAllowedVarNames = cd_settingsGame apply {
		if (count _x == COUNT_REGION_SETTINGS) then {
			"<__system:region__>"
		} else {
			if ((_x select SETTING_INDEX_STORAGE) == SETTING_STORAGE_SERVER) then {
				tolower(_x select SETTING_INDEX_VARNAME)
			} else {
				"<__system:local__>"
			};
		}
	};
	private _remList = [];
	
	{
		_x params ["_varName","_state"];
		_varName = tolower _varName;
		
		private _idxKeySeg = cd_settingsGame findif {count _x != COUNT_REGION_SETTINGS && {_varName == tolower (_x select SETTING_INDEX_VARNAME)}};
		if (_idxKeySeg == -1) then {
			//Не должно выпадать
			errorformat("rpc::onLoadGameSettings() - Unexpected error at line %1",__LINE__);
			continue;
		};
		
		//Если такой настройки не существует по имени 
		// или значение является дефолтным значением
		// или значение является текущим, то нужно удалить из списка
		if (
			!array_exists(_listAllowedVarNames,_varName) || 
			{equals(cd_settingsGame select _idxKeySeg select SETTING_INDEX_DEFVALUE,_state)} ||
			{equals(cd_settingsGame select _idxKeySeg select SETTING_INDEX_CURRENT,_state)
			}
		) then {
			//errorformat("rpc::onLoadGameSettings() - %1:%2:%3 (state %4)",!array_exists(_listAllowedVarNames,_varName) arg equals(cd_settingsGame select _idxKeySeg select SETTING_INDEX_DEFVALUE,_state) arg equals(cd_settingsGame select _idxKeySeg select SETTING_INDEX_CURRENT,_state) arg _state);
			_remList pushBack [_varName,_state,true];
		} else {
			
			_evc = cd_settingsGame select _idxKeySeg select SETTING_INDEX_EVENTONAPPLY;
			if not_equals(_evc,"") then {
				value = _state;
				if equalTypes(_evc,"") then {
					call (missionNamespace getvariable [_evc,{}]);
				} else {
					call _evc;
				};
			} else {
				missionNamespace setVariable [_varName,_state];
			};

			cd_settingsGame select _idxKeySeg set [SETTING_INDEX_CURRENT,_state];
			cd_settingsGame select _idxKeySeg set [SETTING_INDEX_SERIALIZED,_state];
		};
		
	} foreach _list;
	
	//Ненайденные настройки выписываем с объекта сервер-клиента
	if (count _remList > 0) then {
		warningformat("rpc::onLoadGameSettings() - outdated keys found: %1",count _remList);
		rpcSendToServer("syncGameSettings",[_remList arg clientOwner]);
	};
}; rpcAdd("onLoadGameSettings",cd_onLoadGameSettings);


//validate variable settings
#ifdef DEBUG

{
	if (count _x == COUNT_REGION_SETTINGS) then {continue};
	
	_nulldef___ = isNull(_x select SETTING_INDEX_DEFVALUE);
	_nullcur__ = isNull(_x select SETTING_INDEX_CURRENT);
	_nullser__ = isNull(_x select SETTING_INDEX_SERIALIZED);
	if (_nulldef___ || _nullcur__ || _nullser__) exitWith {
		errorformat("[COMPILATION]: Validate game settings error: <%1, %2, %3> (EscapeMenu::settingGame at %4)",_nulldef___ arg _nullcur__ arg _nullser__ arg __LINE__);
		appExit(APPEXIT_REASON_COMPILATIOEXCEPTION);
	};
} foreach cd_settingsGame;


#endif
