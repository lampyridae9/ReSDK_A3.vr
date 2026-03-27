// ======================================================
// Copyright (c) 2017-2026 the ReSDK_A3 project
// sdk.relicta.ru
// ======================================================

#include "..\..\host\lang.hpp"
namespace(clientData,cd_)

// TODO: change render distance for smd_allInGameMobs
decl(void())
esc_settings_loader_graphic = {
	if !([1] call esc_settings_beginLoadSection) exitWith {};

	#define setting_element_size_x 10

	private _ctg = getSettingsList;

	private _setList = count cd_settingsKeyboard;
	private _d = getDisplay;

	call esc_settings_clearSettingList;

	private _data = [];
};
