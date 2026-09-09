version=54;
class EditorData
{
	moveGridStep=0.125;
	angleGridStep=0.2617994;
	scaleGridStep=100;
	autoGroupingDist=10;
	toggles=2;
	class ItemIDProvider
	{
		nextID=2213;
	};
	class LayerIndexProvider
	{
		nextID=198;
	};
	class Camera
	{
		pos[]={4012.8921,24.208452,4018.1101};
		dir[]={-0.60760164,-0.30342758,-0.73409373};
		up[]={-0.19349915,0.95283097,-0.23378053};
		aside[]={-0.77041173,-7.5402204e-07,0.63766617};
	};
};
binarizationWanted=0;
sourceName="ReSDK_A3";
addons[]=
{
	"A3_Characters_F",
	"A3_Props_F_Orange_Humanitarian_Supplies",
	"cba_xeh",
	"CUP_A2_EditorObjects",
	"A3_Structures_F_Exp_Military_Pillboxes",
	"exodus"
};
class AddonsMetaData
{
	class List
	{
		items=5;
		class Item0
		{
			className="A3_Characters_F";
			name="Arma 3 Alpha - Characters and Clothing";
			author="Bohemia Interactive";
			url="https://www.arma3.com";
		};
		class Item1
		{
			className="A3_Props_F_Orange";
			name="Arma 3 Orange - Decorative and Mission Objects";
			author="Bohemia Interactive";
			url="https://www.arma3.com";
		};
		class Item2
		{
			className="CUP_A2_EditorObjects";
			name="CUP_A2_EditorObjects";
			author="MemphisBelle";
		};
		class Item3
		{
			className="A3_Structures_F_Exp";
			name="Arma 3 Apex - Buildings and Structures";
			author="Bohemia Interactive";
			url="https://www.arma3.com";
		};
		class Item4
		{
			className="exodus";
			name="exodus";
		};
	};
};
dlcs[]=
{
	"Orange",
	"Expansion"
};
randomSeed=11605075;
class ScenarioData
{
	author="Septima";
	saving=0;
};
class CustomAttributes
{
	class Category0
	{
		name="Multiplayer";
		class Attribute0
		{
			property="RespawnTemplates";
			expression="true";
			class Value
			{
				class data
				{
					singleType="ARRAY";
					class value
					{
						items=1;
						class Item0
						{
							class data
							{
								singleType="STRING";
								value="None";
							};
						};
					};
				};
			};
		};
		nAttributes=1;
	};
	class Category1
	{
		name="Scenario";
		class Attribute0
		{
			property="EnableTargetDebug";
			expression="true";
			class Value
			{
				class data
				{
					singleType="SCALAR";
					value=1;
				};
			};
		};
		class Attribute1
		{
			property="EnableDebugConsole";
			expression="true";
			class Value
			{
				class data
				{
					singleType="SCALAR";
					value=2;
				};
			};
		};
		nAttributes=2;
	};
};
class Mission
{
	class Intel
	{
		timeOfChanges=1800.0002;
		startWeather=0;
		startWind=0;
		startWaves=0.1;
		forecastWeather=0;
		forecastWind=0;
		forecastWaves=0.1;
		forecastLightnings=0.1;
		rainForced=1;
		windForced=1;
		day=20;
		hour=13;
		minute=-20;
		startFogDecay=0.014;
		forecastFogDecay=0.014;
	};
	class Entities
	{
		items=7;
		class Item0
		{
			dataType="Group";
			side="West";
			class Entities
			{
				items=1;
				class Item0
				{
					dataType="Object";
					class PositionInfo
					{
						position[]={11.849326,5.092412,8141.3096};
						angles[]={0,1.5586488,0};
					};
					side="West";
					flags=7;
					class Attributes
					{
						isPlayer=1;
						class Inventory
						{
						};
					};
					id=1;
					type="B_Survivor_F";
					atlOffset=0.0909729;
					class CustomAttributes
					{
						class Attribute0
						{
							property="speaker";
							expression="_this setspeaker _value;";
							class Value
							{
								class data
								{
									singleType="STRING";
									value="Male04ENG";
								};
							};
						};
						class Attribute1
						{
							property="pitch";
							expression="_this setpitch _value;";
							class Value
							{
								class data
								{
									singleType="SCALAR";
									value=0.97000003;
								};
							};
						};
						class Attribute2
						{
							property="face";
							expression="_this setface _value;";
							class Value
							{
								class data
								{
									singleType="STRING";
									value="WhiteHead_06";
								};
							};
						};
						nAttributes=3;
					};
				};
			};
			class Attributes
			{
			};
			id=0;
			atlOffset=0.0909729;
		};
		class Item1
		{
			dataType="Group";
			side="West";
			class Entities
			{
				items=1;
				class Item0
				{
					dataType="Object";
					class PositionInfo
					{
						position[]={17.72065,5.0014391,8141.2852};
						angles[]={0,4.7971487,0};
					};
					side="West";
					flags=7;
					class Attributes
					{
						name="vasya";
						class Inventory
						{
						};
					};
					id=19;
					type="B_Survivor_F";
					class CustomAttributes
					{
						class Attribute0
						{
							property="speaker";
							expression="_this setspeaker _value;";
							class Value
							{
								class data
								{
									singleType="STRING";
									value="Male10ENG";
								};
							};
						};
						class Attribute1
						{
							property="pitch";
							expression="_this setpitch _value;";
							class Value
							{
								class data
								{
									singleType="SCALAR";
									value=0.95999998;
								};
							};
						};
						nAttributes=2;
					};
				};
			};
			class Attributes
			{
			};
			id=18;
		};
		class Item2
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={14,-994.9588,8100};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="call{{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""missionName"",""AI_AutomationProbe""],[""__automationProbe"",""MapAutomation-v1""],[""version"",5]]}}";
			};
			id=2205;
			type="Land_Orange_01_F";
			atlOffset=-1000;
		};
		class Item3
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4000,14.950068,4000};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""floor_1"",""MapAutomation"",""""]],[""class"",""BigConcreteFloor""]]}";
			};
			id=2206;
			type="CUP_A2_rail_najazdovarampa";
			atlOffset=10;
		};
		class Item4
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4008.25,15.339174,4000.5};
				angles[]={0.08726646,1.6580628,0.17453292};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[[""name"",""Проверка стены""],[""desc"",""Probe: quoted """"text"""" remains data""]]],[""__ai"",[""wall_1"",""MapAutomation"",""""]],[""class"",""ConcreteGreenWall""]]}";
			};
			id=2207;
			type="Land_PillboxWall_01_3m_F";
			atlOffset=10.25;
		};
		class Item5
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4000,16.391039,4008};
				angles[]={0,3.1415927,0};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""arch_1"",""MapAutomation"",""""]],[""class"",""WoodenArch""]]}";
			};
			id=2208;
			type="woodarka";
			atlOffset=10.000001;
		};
		class Item6
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4000,14.950068,4000};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""copy_6"",""MapAutomation"",""""]],[""class"",""BigConcreteFloor""]]}";
			};
			id=2212;
			type="CUP_A2_rail_najazdovarampa";
			atlOffset=10;
		};
	};
};
