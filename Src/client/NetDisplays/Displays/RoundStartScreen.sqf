// ======================================================
// Copyright (c) 2017-2026 the ReSDK_A3 project
// sdk.relicta.ru
// ======================================================

#include <..\..\..\host\lang.hpp>

// Экран начала раунда (пробуждение персонажа)
// Данные: [_headerLine, _charInfoLine, _descriptionText]
//   _headerLine - верхняя строка (колено, смена, локация)
//   _charInfoLine - информация о персонаже (имя, роль, возраст)
//   _descriptionText - описание роли и задачи
struct(RoundStartScreen) base(NDBase)

	decl(override) def(process)
	{
		params ["_args","_isFirstCall"];

		private _disp = self getv(thisDisplay);

		if (_isFirstCall) then {
			private _ctg = [_disp,WIDGETGROUP,[0,0,100,100]] call createWidget;
			nd_internal_currentStructObj callp(addSavedWidget, _ctg);

			// Полноэкранный чёрный фон
			private _bg = [_disp,BACKGROUND,[0,0,100,100],_ctg] call createWidget;
			_bg setBackgroundColor [0,0,0,1];
		};

		private _ctg = (nd_internal_currentStructObj callv(getSavedWidgets)) select 0;

		call nd_cleanupData;

		_args params [
			["_headerLine",""],
			["_charInfoLine",""],
			["_descriptionText",""]
		];

		// === Верхняя строка: "Шестое колено. Смена 143. Грязноямск." ===
		private _wid = [TEXT,[0,15,100,10],_ctg] call nd_regWidget;
		[_wid, format[
			"<t align='center' size='1.6' font='RobotoCondensed' color='#C0B8A0' shadow='2' shadowColor='#000000'>%1</t>",
			_headerLine
		]] call widgetSetText;

		// === Информация о персонаже ===
		// "Моё имя Хоба Савин. Я кухарь в баре Кабак."
		// "Мне 36 циклов."
		_wid = [TEXT,[0,28,100,12],_ctg] call nd_regWidget;
		[_wid, format[
			"<t align='center' size='1.3' font='RobotoCondensed' color='#C0B8A0' shadow='2' shadowColor='#000000'>%1</t>",
			_charInfoLine
		]] call widgetSetText;

		// === Описание роли (задачи, воспоминания и т.д.) ===
		if (_descriptionText != "") then {
			_wid = [TEXT,[15,44,70,20],_ctg] call nd_regWidget;
			[_wid, format[
				"<t align='center' size='0.95' font='RobotoCondensedLight' color='#A09880' shadow='1' shadowColor='#000000'>%1</t>",
				_descriptionText
			]] call widgetSetText;
		};

		// === Кнопка "Проснуться" ===
		private _btnClose = [_disp,[35,82,30,6],_ctg,true] call nd_addClosingButton;
		_btnClose ctrlSetText "Проснуться";
		_btnClose ctrlSetFont "RobotoCondensed";
		if (nd_lobby_isOpen) then {
			ctrlSetFocus _btnClose;
		};
	};

endstruct
