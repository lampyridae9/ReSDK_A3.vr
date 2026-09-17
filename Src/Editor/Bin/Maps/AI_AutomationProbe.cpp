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
		nextID=2618;
	};
	class LayerIndexProvider
	{
		nextID=198;
	};
	class Camera
	{
		pos[]={4709.1084,19.829643,4724.7144};
		dir[]={0.5176807,-0.17495205,0.83760756};
		up[]={0.092013277,0.98455083,0.14887844};
		aside[]={0.85073692,1.1072843e-06,-0.52578849};
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
	"exodus",
	"A3_Structures_F_Enoch_Infrastructure_Roads",
	"csa_objects",
	"xlamdoor",
	"RELICTA_models",
	"Model_14_10",
	"A3_Structures_F_EPA_Civ_Camping",
	"A3_Structures_F_Furniture",
	"AtmObjects",
	"ml_exonew",
	"A3_Structures_F_Exp_Walls_Concrete"
};
class AddonsMetaData
{
	class List
	{
		items=14;
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
		class Item5
		{
			className="A3_Structures_F_Enoch_Infrastructure";
			name="Arma 3 Contact Platform - Infrastructure Objects";
			author="Bohemia Interactive";
			url="https://www.arma3.com";
		};
		class Item6
		{
			className="csa_objects";
			name="csa_objects";
		};
		class Item7
		{
			className="xlamdoor";
			name="xlamdoor";
		};
		class Item8
		{
			className="RELICTA_models";
			name="RELICTA_models";
			author="Yodes and Alien";
		};
		class Item9
		{
			className="Model_14_10";
			name="Model_14_10";
		};
		class Item10
		{
			className="A3_Structures_F_EPA";
			name="Arma 3 Survive Episode - Buildings and Structures";
			author="Bohemia Interactive";
			url="https://www.arma3.com";
		};
		class Item11
		{
			className="A3_Structures_F";
			name="Arma 3 - Buildings and Structures";
			author="Bohemia Interactive";
			url="https://www.arma3.com";
		};
		class Item12
		{
			className="AtmObjects";
			name="AtmObjects";
		};
		class Item13
		{
			className="ml_exonew";
			name="ml_exonew";
		};
	};
};
dlcs[]=
{
	"Orange",
	"Expansion",
	"Enoch"
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
		items=194;
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
		class Item7
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4695.0181,15.042006,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_001"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2431;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item8
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4695.0181,15.042006,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_002"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2432;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item9
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4695.0181,15.042006,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_003"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2433;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item10
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4697.0107,15.042006,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_004"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2434;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item11
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4697.0107,15.042006,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_005"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2435;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item12
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4697.0107,15.042006,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_006"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2436;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item13
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4699.0034,15.042006,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_007"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2437;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item14
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4699.0034,15.042006,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_008"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2438;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item15
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4699.0034,15.042006,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_009"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2439;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item16
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4700.9966,15.042006,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_010"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2440;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item17
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4700.9966,15.042006,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_011"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2441;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item18
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4700.9966,15.042006,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_012"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2442;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item19
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.9893,15.042006,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_013"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2443;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item20
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.9893,15.042006,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_014"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2444;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item21
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.9893,15.042006,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_015"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2445;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item22
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4704.9819,15.042006,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_016"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2446;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item23
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4704.9819,15.042006,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_017"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2447;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item24
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4704.9819,15.042006,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__floor_module_018"",""MapAutomation"",""floor_001""]],[""class"",""ConcretePanel""]]}";
			};
			id=2448;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=10.042006;
		};
		class Item25
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4695.0181,18.342007,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__floor_module_001"",""MapAutomation"",""floor_002""]],[""class"",""ConcretePanel""]]}";
			};
			id=2449;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077456;
		};
		class Item26
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4695.0181,18.342007,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__floor_module_002"",""MapAutomation"",""floor_002""]],[""class"",""ConcretePanel""]]}";
			};
			id=2450;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=2.7146044;
		};
		class Item27
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4695.0181,18.342007,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__floor_module_003"",""MapAutomation"",""floor_002""]],[""class"",""ConcretePanel""]]}";
			};
			id=2451;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077456;
		};
		class Item28
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4697.0107,18.342007,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__floor_module_004"",""MapAutomation"",""floor_002""]],[""class"",""ConcretePanel""]]}";
			};
			id=2452;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077456;
		};
		class Item29
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4697.0107,18.342007,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__floor_module_005"",""MapAutomation"",""floor_002""]],[""class"",""ConcretePanel""]]}";
			};
			id=2453;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077456;
		};
		class Item30
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4697.0107,18.342007,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__floor_module_006"",""MapAutomation"",""floor_002""]],[""class"",""ConcretePanel""]]}";
			};
			id=2454;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077456;
		};
		class Item31
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4699.0034,18.342007,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__floor_module_007"",""MapAutomation"",""floor_002""]],[""class"",""ConcretePanel""]]}";
			};
			id=2455;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077456;
		};
		class Item32
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4700.9966,18.342007,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__floor_module_010"",""MapAutomation"",""floor_002""]],[""class"",""ConcretePanel""]]}";
			};
			id=2456;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077456;
		};
		class Item33
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.9893,18.342007,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__floor_module_013"",""MapAutomation"",""floor_002""]],[""class"",""ConcretePanel""]]}";
			};
			id=2457;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077456;
		};
		class Item34
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.9893,18.342007,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__floor_module_014"",""MapAutomation"",""floor_002""]],[""class"",""ConcretePanel""]]}";
			};
			id=2458;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=2.7146044;
		};
		class Item35
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.9893,18.342007,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__floor_module_015"",""MapAutomation"",""floor_002""]],[""class"",""ConcretePanel""]]}";
			};
			id=2459;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077456;
		};
		class Item36
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4704.9819,18.342007,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__floor_module_016"",""MapAutomation"",""floor_002""]],[""class"",""ConcretePanel""]]}";
			};
			id=2460;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=2.7146044;
		};
		class Item37
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4704.9819,18.342007,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__floor_module_017"",""MapAutomation"",""floor_002""]],[""class"",""ConcretePanel""]]}";
			};
			id=2461;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077456;
		};
		class Item38
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4704.9819,18.342007,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__floor_module_018"",""MapAutomation"",""floor_002""]],[""class"",""ConcretePanel""]]}";
			};
			id=2462;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077456;
		};
		class Item39
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4695.0181,21.642006,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_001"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2463;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077446;
		};
		class Item40
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4695.0181,21.642006,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_002"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2464;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=2.7146053;
		};
		class Item41
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4695.0181,21.642006,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_003"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2465;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077446;
		};
		class Item42
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4697.0107,21.642006,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_004"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2466;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077446;
		};
		class Item43
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4697.0107,21.642006,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_005"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2467;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077446;
		};
		class Item44
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4697.0107,21.642006,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_006"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2468;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077446;
		};
		class Item45
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4699.0034,21.642006,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_007"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2469;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077446;
		};
		class Item46
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4699.0034,21.642006,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_008"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2470;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=1.5577755;
		};
		class Item47
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4699.0034,21.642006,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_009"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2471;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.4847221;
		};
		class Item48
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4700.9966,21.642006,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_010"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2472;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077446;
		};
		class Item49
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4700.9966,21.642006,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_011"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2473;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=1.5577755;
		};
		class Item50
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4700.9966,21.642006,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_012"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2474;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=2.9307613;
		};
		class Item51
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.9893,21.642006,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_013"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2475;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077446;
		};
		class Item52
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.9893,21.642006,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_014"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2476;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=2.7146053;
		};
		class Item53
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.9893,21.642006,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_015"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2477;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077446;
		};
		class Item54
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4704.9819,21.642006,4697.5059};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_016"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2478;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=2.3431549;
		};
		class Item55
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4704.9819,21.642006,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_017"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2479;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077446;
		};
		class Item56
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4704.9819,21.642006,4702.4941};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__roof__floor_module_018"",""MapAutomation"",""roof""]],[""class"",""ConcretePanel""]]}";
			};
			id=2480;
			type="Land_ConcretePanels_02_single_v1_F";
			atlOffset=3.2077446;
		};
		class Item57
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4694,18.2778,4698.5};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_001__module_001"",""MapAutomation"",""floor_001__wall_001""]],[""class"",""BrickThinWall""]]}";
			};
			id=2481;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item58
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4694,18.2778,4701.5};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_001__module_002"",""MapAutomation"",""floor_001__wall_001""]],[""class"",""BrickThinWall""]]}";
			};
			id=2482;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item59
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4696.1748,18.2778,4695.5};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_002__module_001"",""MapAutomation"",""floor_001__wall_002""]],[""class"",""BrickThinWall""]]}";
			};
			id=2483;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item60
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4696.1748,18.2778,4704.5};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_003__module_001"",""MapAutomation"",""floor_001__wall_003""]],[""class"",""BrickThinWall""]]}";
			};
			id=2484;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item61
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4698.3501,18.2778,4695.7495};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_004__module_001"",""MapAutomation"",""floor_001__wall_004""]],[""class"",""BrickThinWall""]]}";
			};
			id=2485;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item62
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4698.3501,18.2778,4700.7495};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_004__module_002"",""MapAutomation"",""floor_001__wall_004""]],[""class"",""BrickThinWall""]]}";
			};
			id=2486;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item63
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4698.9248,18.2778,4695.5};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_005__module_001"",""MapAutomation"",""floor_001__wall_005""]],[""class"",""BrickThinWall""]]}";
			};
			id=2487;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item64
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4701.0752,18.2778,4695.5};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_005__module_002"",""MapAutomation"",""floor_001__wall_005""]],[""class"",""BrickThinWall""]]}";
			};
			id=2488;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item65
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4700,18.2778,4704.5};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_006__module_001"",""MapAutomation"",""floor_001__wall_006""]],[""class"",""BrickThinWall""]]}";
			};
			id=2489;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item66
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4701.6499,18.2778,4695.7495};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_007__module_001"",""MapAutomation"",""floor_001__wall_007""]],[""class"",""BrickThinWall""]]}";
			};
			id=2490;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item67
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4701.6499,18.2778,4700.7495};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_007__module_002"",""MapAutomation"",""floor_001__wall_007""]],[""class"",""BrickThinWall""]]}";
			};
			id=2491;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item68
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4703.8252,18.2778,4695.5};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_008__module_001"",""MapAutomation"",""floor_001__wall_008""]],[""class"",""BrickThinWall""]]}";
			};
			id=2492;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item69
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4703.8252,18.2778,4704.5};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_009__module_001"",""MapAutomation"",""floor_001__wall_009""]],[""class"",""BrickThinWall""]]}";
			};
			id=2493;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item70
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4706,18.2778,4698.5};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_010__module_001"",""MapAutomation"",""floor_001__wall_010""]],[""class"",""BrickThinWall""]]}";
			};
			id=2494;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item71
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4706,18.2778,4701.5};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_001__wall_010__module_002"",""MapAutomation"",""floor_001__wall_010""]],[""class"",""BrickThinWall""]]}";
			};
			id=2495;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500006;
		};
		class Item72
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4694,21.577801,4698.5};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__wall_001__module_001"",""MapAutomation"",""floor_002__wall_001""]],[""class"",""BrickThinWall""]]}";
			};
			id=2496;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500015;
		};
		class Item73
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4694,21.577801,4701.5};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__wall_001__module_002"",""MapAutomation"",""floor_002__wall_001""]],[""class"",""BrickThinWall""]]}";
			};
			id=2497;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500015;
		};
		class Item74
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4696.1748,21.577801,4695.5};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__wall_002__module_001"",""MapAutomation"",""floor_002__wall_002""]],[""class"",""BrickThinWall""]]}";
			};
			id=2498;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500015;
		};
		class Item75
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4696.1748,21.577801,4704.5};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__wall_003__module_001"",""MapAutomation"",""floor_002__wall_003""]],[""class"",""BrickThinWall""]]}";
			};
			id=2499;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500015;
		};
		class Item76
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4698.3501,21.577801,4695.7495};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__wall_004__module_001"",""MapAutomation"",""floor_002__wall_004""]],[""class"",""BrickThinWall""]]}";
			};
			id=2500;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500015;
		};
		class Item77
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4698.3501,21.577801,4700.7495};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__wall_004__module_002"",""MapAutomation"",""floor_002__wall_004""]],[""class"",""BrickThinWall""]]}";
			};
			id=2501;
			type="Land_kr_stena_3x6";
			atlOffset=4.9500017;
		};
		class Item78
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4700,21.577801,4695.5};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__wall_005__module_001"",""MapAutomation"",""floor_002__wall_005""]],[""class"",""BrickThinWall""]]}";
			};
			id=2502;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500015;
		};
		class Item79
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4700,21.577801,4704.5};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__wall_006__module_001"",""MapAutomation"",""floor_002__wall_006""]],[""class"",""BrickThinWall""]]}";
			};
			id=2503;
			type="Land_kr_stena_3x6";
			atlOffset=1.650032;
		};
		class Item80
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4701.6499,21.577801,4695.7495};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__wall_007__module_001"",""MapAutomation"",""floor_002__wall_007""]],[""class"",""BrickThinWall""]]}";
			};
			id=2504;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500015;
		};
		class Item81
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4701.6499,21.577801,4700.7495};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__wall_007__module_002"",""MapAutomation"",""floor_002__wall_007""]],[""class"",""BrickThinWall""]]}";
			};
			id=2505;
			type="Land_kr_stena_3x6";
			atlOffset=4.9500017;
		};
		class Item82
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4703.8252,21.577801,4695.5};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__wall_008__module_001"",""MapAutomation"",""floor_002__wall_008""]],[""class"",""BrickThinWall""]]}";
			};
			id=2506;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500015;
		};
		class Item83
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4703.8252,21.577801,4704.5};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__wall_009__module_001"",""MapAutomation"",""floor_002__wall_009""]],[""class"",""BrickThinWall""]]}";
			};
			id=2507;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500015;
		};
		class Item84
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4706,21.577801,4698.5};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__wall_010__module_001"",""MapAutomation"",""floor_002__wall_010""]],[""class"",""BrickThinWall""]]}";
			};
			id=2508;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500015;
		};
		class Item85
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4706,21.577801,4701.5};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__floor_002__wall_010__module_002"",""MapAutomation"",""floor_002__wall_010""]],[""class"",""BrickThinWall""]]}";
			};
			id=2509;
			type="Land_kr_stena_3x6";
			atlOffset=1.6500015;
		};
		class Item86
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4698.3501,16.226217,4696.499};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__portal_001"",""MapAutomation"",""portal_001""]],[""class"",""WoodenDoor""]]}";
			};
			id=2510;
			type="Land_xlamdoor";
			atlOffset=9.5367432e-07;
		};
		class Item87
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4701.6499,16.226217,4696.499};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__portal_002"",""MapAutomation"",""portal_002""]],[""class"",""WoodenDoor""]]}";
			};
			id=2511;
			type="Land_xlamdoor";
			atlOffset=9.5367432e-07;
		};
		class Item88
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4700,16.226217,4695.5};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__portal_003"",""MapAutomation"",""portal_003""]],[""class"",""WoodenDoor""]]}";
			};
			id=2512;
			type="Land_xlamdoor";
			atlOffset=9.5367432e-07;
		};
		class Item89
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4698.3501,19.526217,4696.499};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__portal_004"",""MapAutomation"",""portal_004""]],[""class"",""WoodenDoor""]]}";
			};
			id=2513;
			type="Land_xlamdoor";
		};
		class Item90
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4701.6499,19.526217,4696.499};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__portal_005"",""MapAutomation"",""portal_005""]],[""class"",""WoodenDoor""]]}";
			};
			id=2514;
			type="Land_xlamdoor";
		};
		class Item91
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4700,18.434231,4701.499};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""building_001__stairs_001"",""MapAutomation"",""stairs_001""]],[""class"",""StoneBigLadderDouble""]]}";
			};
			id=2515;
			type="Land_lest_kletka";
			atlOffset=1.6499987;
		};
		class Item92
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4695.1934,15.607686,4700};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_001__sleeping_001"",""MapAutomation"",""bedroom_001""]],[""class"",""SingleWhiteBed""]]}";
			};
			id=2516;
			type="bed4";
			atlOffset=9.5367432e-07;
		};
		class Item93
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4695.1934,15.607686,4698.646};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_001__sleeping_002"",""MapAutomation"",""bedroom_001""]],[""class"",""SingleWhiteBed""]]}";
			};
			id=2517;
			type="bed4";
			atlOffset=9.5367432e-07;
		};
		class Item94
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4694.6514,15.916462,4701.124};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_001__storage_001"",""MapAutomation"",""bedroom_001""]],[""class"",""SteelGreenCabinet""]]}";
			};
			id=2518;
			type="shkafsin";
			atlOffset=9.5367432e-07;
		};
		class Item95
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4697.75,15.566558,4703.75};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_001__work_surface_001"",""MapAutomation"",""bedroom_001""]],[""class"",""SmallWoodenTable""]]}";
			};
			id=2519;
			type="Land_WoodenTable_small_F";
			atlOffset=9.5367432e-07;
		};
		class Item96
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4696.7563,15.133606,4703.6992};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_001__seating_001"",""MapAutomation"",""bedroom_001""]],[""class"",""WoodenChair""]]}";
			};
			id=2520;
			type="Land_ChairWood_F";
			atlOffset=9.5367432e-07;
		};
		class Item97
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.8433,15.607686,4700};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_002__sleeping_001"",""MapAutomation"",""bedroom_002""]],[""class"",""SingleWhiteBed""]]}";
			};
			id=2521;
			type="bed4";
			atlOffset=9.5367432e-07;
		};
		class Item98
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4704.8066,15.607686,4697.896};
				angles[]={0,4.712389,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_002__sleeping_002"",""MapAutomation"",""bedroom_002""]],[""class"",""SingleWhiteBed""]]}";
			};
			id=2522;
			type="bed4";
			atlOffset=9.5367432e-07;
		};
		class Item99
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.3013,15.916462,4701.124};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_002__storage_001"",""MapAutomation"",""bedroom_002""]],[""class"",""SteelGreenCabinet""]]}";
			};
			id=2523;
			type="shkafsin";
			atlOffset=9.5367432e-07;
		};
		class Item100
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4705.3999,15.566558,4703.75};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_002__work_surface_001"",""MapAutomation"",""bedroom_002""]],[""class"",""SmallWoodenTable""]]}";
			};
			id=2524;
			type="Land_WoodenTable_small_F";
			atlOffset=9.5367432e-07;
		};
		class Item101
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4704.4062,15.133606,4703.6992};
				angles[]={0,4.712389,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_002__seating_001"",""MapAutomation"",""bedroom_002""]],[""class"",""WoodenChair""]]}";
			};
			id=2525;
			type="Land_ChairWood_F";
			atlOffset=9.5367432e-07;
		};
		class Item102
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4695.1934,18.907684,4700};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_003__sleeping_001"",""MapAutomation"",""bedroom_003""]],[""class"",""SingleWhiteBed""]]}";
			};
			id=2526;
			type="bed4";
		};
		class Item103
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4696.1748,18.907684,4703.3066};
				angles[]={0,3.1415927,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_003__sleeping_002"",""MapAutomation"",""bedroom_003""]],[""class"",""SingleWhiteBed""]]}";
			};
			id=2527;
			type="bed4";
		};
		class Item104
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4694.6514,19.216461,4701.124};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_003__storage_001"",""MapAutomation"",""bedroom_003""]],[""class"",""SteelGreenCabinet""]]}";
			};
			id=2528;
			type="shkafsin";
		};
		class Item105
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4694.75,18.866556,4696.25};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_003__work_surface_001"",""MapAutomation"",""bedroom_003""]],[""class"",""SmallWoodenTable""]]}";
			};
			id=2529;
			type="Land_WoodenTable_small_F";
		};
		class Item106
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4695.7563,18.433605,4696.1992};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_003__seating_001"",""MapAutomation"",""bedroom_003""]],[""class"",""WoodenChair""]]}";
			};
			id=2530;
			type="Land_ChairWood_F";
		};
		class Item107
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.8433,18.907684,4700};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_004__sleeping_001"",""MapAutomation"",""bedroom_004""]],[""class"",""SingleWhiteBed""]]}";
			};
			id=2531;
			type="bed4";
		};
		class Item108
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.8433,18.907684,4701.396};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_004__sleeping_002"",""MapAutomation"",""bedroom_004""]],[""class"",""SingleWhiteBed""]]}";
			};
			id=2532;
			type="bed4";
		};
		class Item109
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.3013,19.216461,4702.624};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_004__storage_001"",""MapAutomation"",""bedroom_004""]],[""class"",""SteelGreenCabinet""]]}";
			};
			id=2533;
			type="shkafsin";
		};
		class Item110
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4705.3999,18.866556,4697};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_004__work_surface_001"",""MapAutomation"",""bedroom_004""]],[""class"",""SmallWoodenTable""]]}";
			};
			id=2534;
			type="Land_WoodenTable_small_F";
		};
		class Item111
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4705.4062,18.433605,4695.9492};
				angles[]={0,3.1415927,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_004__seating_001"",""MapAutomation"",""bedroom_004""]],[""class"",""WoodenChair""]]}";
			};
			id=2535;
			type="Land_ChairWood_F";
		};
		class Item112
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4696.75,18.37426,4700.25};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_001__lighting_001"",""MapAutomation"",""bedroom_001""]],[""class"",""LampCeiling""]]}";
			};
			id=2536;
			type="Lamp_tarelka";
			atlOffset=3.0783777;
		};
		class Item113
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4702.3999,18.37426,4696.25};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_002__lighting_001"",""MapAutomation"",""bedroom_002""]],[""class"",""LampCeiling""]]}";
			};
			id=2537;
			type="Lamp_tarelka";
			atlOffset=3.0783777;
		};
		class Item114
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4697.25,21.674261,4701.5};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_003__lighting_001"",""MapAutomation"",""bedroom_003""]],[""class"",""LampCeiling""]]}";
			};
			id=2538;
			type="Lamp_tarelka";
			atlOffset=3.0783787;
		};
		class Item115
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={4703.3999,21.674261,4702.5};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""bedroom_004__lighting_001"",""MapAutomation"",""bedroom_004""]],[""class"",""LampCeiling""]]}";
			};
			id=2539;
			type="Lamp_tarelka";
			atlOffset=3.0783787;
		};
		class Item116
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5035.5,14.8475,4697};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__floor_module_001"",""MapAutomation"",""b8d79c0234c33__floor_001""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2540;
			type="Land_plita_3x6";
			atlOffset=9.6922359;
		};
		class Item117
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5035.5,14.8475,4703};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__floor_module_002"",""MapAutomation"",""b8d79c0234c33__floor_001""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2541;
			type="Land_plita_3x6";
			atlOffset=9.6922359;
		};
		class Item118
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.5,14.8475,4697};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__floor_module_003"",""MapAutomation"",""b8d79c0234c33__floor_001""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2542;
			type="Land_plita_3x6";
			atlOffset=9.6922359;
		};
		class Item119
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.5,14.8475,4703};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__floor_module_004"",""MapAutomation"",""b8d79c0234c33__floor_001""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2543;
			type="Land_plita_3x6";
			atlOffset=9.6922359;
		};
		class Item120
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5041.5,14.8475,4697};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__floor_module_005"",""MapAutomation"",""b8d79c0234c33__floor_001""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2544;
			type="Land_plita_3x6";
			atlOffset=9.6922359;
		};
		class Item121
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5041.5,14.8475,4703};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__floor_module_006"",""MapAutomation"",""b8d79c0234c33__floor_001""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2545;
			type="Land_plita_3x6";
			atlOffset=9.6922359;
		};
		class Item122
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5044.5,14.8475,4697};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__floor_module_007"",""MapAutomation"",""b8d79c0234c33__floor_001""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2546;
			type="Land_plita_3x6";
			atlOffset=9.6922359;
		};
		class Item123
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5044.5,14.8475,4703};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__floor_module_008"",""MapAutomation"",""b8d79c0234c33__floor_001""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2547;
			type="Land_plita_3x6";
			atlOffset=9.6922359;
		};
		class Item124
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5035.5,18.1525,4697};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__floor_module_001"",""MapAutomation"",""b8d79c0234c33__floor_002""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2548;
			type="Land_plita_3x6";
			atlOffset=2.504096;
		};
		class Item125
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5035.5,18.1525,4703};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__floor_module_002"",""MapAutomation"",""b8d79c0234c33__floor_002""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2549;
			type="Land_plita_3x6";
			atlOffset=2.9972363;
		};
		class Item126
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.5,18.1525,4697};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__floor_module_003"",""MapAutomation"",""b8d79c0234c33__floor_002""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2550;
			type="Land_plita_3x6";
			atlOffset=2.9972363;
		};
		class Item127
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.5,18.1525,4703};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__floor_module_004"",""MapAutomation"",""b8d79c0234c33__floor_002""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2551;
			type="Land_plita_3x6";
			atlOffset=2.9972363;
		};
		class Item128
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5043,18.1525,4695.5};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__floor_module_005"",""MapAutomation"",""b8d79c0234c33__floor_002""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2552;
			type="Land_plita_3x6";
			atlOffset=2.9972363;
		};
		class Item129
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5043,18.1525,4704.5};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__floor_module_006"",""MapAutomation"",""b8d79c0234c33__floor_002""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2553;
			type="Land_plita_3x6";
			atlOffset=2.9972363;
		};
		class Item130
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5044.5,18.1525,4700};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__floor_module_007"",""MapAutomation"",""b8d79c0234c33__floor_002""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2554;
			type="Land_plita_3x6";
			atlOffset=2.9972363;
		};
		class Item131
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5035.5,21.4575,4697};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__roof__floor_module_001"",""MapAutomation"",""b8d79c0234c33__roof""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2555;
			type="Land_plita_3x6";
			atlOffset=2.9972363;
		};
		class Item132
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5035.5,21.4575,4703};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__roof__floor_module_002"",""MapAutomation"",""b8d79c0234c33__roof""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2556;
			type="Land_plita_3x6";
			atlOffset=2.9972363;
		};
		class Item133
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.5,21.4575,4697};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__roof__floor_module_003"",""MapAutomation"",""b8d79c0234c33__roof""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2557;
			type="Land_plita_3x6";
			atlOffset=2.9972363;
		};
		class Item134
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.5,21.4575,4703};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__roof__floor_module_004"",""MapAutomation"",""b8d79c0234c33__roof""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2558;
			type="Land_plita_3x6";
			atlOffset=2.9972363;
		};
		class Item135
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5041.5,21.4575,4697};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__roof__floor_module_005"",""MapAutomation"",""b8d79c0234c33__roof""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2559;
			type="Land_plita_3x6";
			atlOffset=2.9972363;
		};
		class Item136
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5041.5,21.4575,4703};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__roof__floor_module_006"",""MapAutomation"",""b8d79c0234c33__roof""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2560;
			type="Land_plita_3x6";
			atlOffset=2.9972363;
		};
		class Item137
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5044.5,21.4575,4697};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__roof__floor_module_007"",""MapAutomation"",""b8d79c0234c33__roof""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2561;
			type="Land_plita_3x6";
			atlOffset=2.9972363;
		};
		class Item138
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5044.5,21.4575,4703};
			};
			side="Empty";
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__roof__floor_module_008"",""MapAutomation"",""b8d79c0234c33__roof""]],[""class"",""MediumConcreteFloor""]]}";
			};
			id=2562;
			type="Land_plita_3x6";
			atlOffset=2.9972363;
		};
		class Item139
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5035.5,16.499996,4694.1499};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_001__module_001"",""MapAutomation"",""b8d79c0234c33__floor_001__run_001""]],[""class"",""BrickThinWallSmall""]]}";
			};
			id=2563;
			type="Land_kr_stena_3x3";
			atlOffset=0.00028991699;
		};
		class Item140
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5037.7393,16.489912,4694.1499};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_001__module_002"",""MapAutomation"",""b8d79c0234c33__floor_001__run_001""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2564;
			type="land_ganzazhelezo3";
			atlOffset=0.027409554;
		};
		class Item141
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5039.2178,16.489912,4694.1499};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_001__module_003"",""MapAutomation"",""b8d79c0234c33__floor_001__run_001""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2565;
			type="land_ganzazhelezo3";
			atlOffset=0.027409554;
		};
		class Item142
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5043.0215,16.499996,4694.1499};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_001__module_004"",""MapAutomation"",""b8d79c0234c33__floor_001__run_001""]],[""class"",""BrickThinWallSmall""]]}";
			};
			id=2566;
			type="Land_kr_stena_3x3";
			atlOffset=0.00028991699;
		};
		class Item143
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5045.2607,16.489912,4694.1499};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_001__module_005"",""MapAutomation"",""b8d79c0234c33__floor_001__run_001""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2567;
			type="land_ganzazhelezo3";
			atlOffset=0.027409554;
		};
		class Item144
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5035.5,16.499996,4700};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_002__module_001"",""MapAutomation"",""b8d79c0234c33__floor_001__run_002""]],[""class"",""BrickThinWallSmall""]]}";
			};
			id=2568;
			type="Land_kr_stena_3x3";
			atlOffset=0.00028991699;
		};
		class Item145
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5037.7393,16.489912,4700};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_002__module_002"",""MapAutomation"",""b8d79c0234c33__floor_001__run_002""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2569;
			type="land_ganzazhelezo3";
			atlOffset=0.027409554;
		};
		class Item146
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5037,16.499998,4705.8501};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_003__module_001"",""MapAutomation"",""b8d79c0234c33__floor_001__run_003""]],[""class"",""BrickThinWall""]]}";
			};
			id=2570;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064601898;
		};
		class Item147
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5043,16.499998,4705.8501};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_003__module_002"",""MapAutomation"",""b8d79c0234c33__floor_001__run_003""]],[""class"",""BrickThinWall""]]}";
			};
			id=2571;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064601898;
		};
		class Item148
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5034.1499,16.499998,4697};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_004__module_001"",""MapAutomation"",""b8d79c0234c33__floor_001__run_004""]],[""class"",""BrickThinWall""]]}";
			};
			id=2572;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064601898;
		};
		class Item149
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5034.1499,16.499998,4703};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_004__module_002"",""MapAutomation"",""b8d79c0234c33__floor_001__run_004""]],[""class"",""BrickThinWall""]]}";
			};
			id=2573;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064601898;
		};
		class Item150
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,16.489912,4694.7393};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_005__module_001"",""MapAutomation"",""b8d79c0234c33__floor_001__run_005""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2574;
			type="land_ganzazhelezo3";
			atlOffset=0.027409554;
		};
		class Item151
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,16.489912,4697.7822};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_005__module_002"",""MapAutomation"",""b8d79c0234c33__floor_001__run_005""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2575;
			type="land_ganzazhelezo3";
			atlOffset=0.027409554;
		};
		class Item152
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,16.489912,4699.2607};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_005__module_003"",""MapAutomation"",""b8d79c0234c33__floor_001__run_005""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2576;
			type="land_ganzazhelezo3";
			atlOffset=0.027409554;
		};
		class Item153
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,16.489912,4700.7393};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_005__module_004"",""MapAutomation"",""b8d79c0234c33__floor_001__run_005""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2577;
			type="land_ganzazhelezo3";
			atlOffset=0.027409554;
		};
		class Item154
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,16.489912,4703.7822};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_005__module_005"",""MapAutomation"",""b8d79c0234c33__floor_001__run_005""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2578;
			type="land_ganzazhelezo3";
			atlOffset=0.027409554;
		};
		class Item155
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,16.489912,4705.2607};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_005__module_006"",""MapAutomation"",""b8d79c0234c33__floor_001__run_005""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2579;
			type="land_ganzazhelezo3";
			atlOffset=0.027409554;
		};
		class Item156
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5045.8501,16.499998,4697};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_006__module_001"",""MapAutomation"",""b8d79c0234c33__floor_001__run_006""]],[""class"",""BrickThinWall""]]}";
			};
			id=2580;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064601898;
		};
		class Item157
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5045.8501,16.499998,4703};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_001__run_006__module_002"",""MapAutomation"",""b8d79c0234c33__floor_001__run_006""]],[""class"",""BrickThinWall""]]}";
			};
			id=2581;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064601898;
		};
		class Item158
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5037,19.804996,4694.1499};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__run_001__module_001"",""MapAutomation"",""b8d79c0234c33__floor_002__run_001""]],[""class"",""BrickThinWall""]]}";
			};
			id=2582;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064582825;
		};
		class Item159
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5043,19.804996,4694.1499};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__run_001__module_002"",""MapAutomation"",""b8d79c0234c33__floor_002__run_001""]],[""class"",""BrickThinWall""]]}";
			};
			id=2583;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064582825;
		};
		class Item160
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5037,19.804996,4705.8501};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__run_002__module_001"",""MapAutomation"",""b8d79c0234c33__floor_002__run_002""]],[""class"",""BrickThinWall""]]}";
			};
			id=2584;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064582825;
		};
		class Item161
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5043,19.804996,4705.8501};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__run_002__module_002"",""MapAutomation"",""b8d79c0234c33__floor_002__run_002""]],[""class"",""BrickThinWall""]]}";
			};
			id=2585;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064582825;
		};
		class Item162
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5034.1499,19.804996,4697};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__run_003__module_001"",""MapAutomation"",""b8d79c0234c33__floor_002__run_003""]],[""class"",""BrickThinWall""]]}";
			};
			id=2586;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064582825;
		};
		class Item163
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5034.1499,19.804996,4703};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__run_003__module_002"",""MapAutomation"",""b8d79c0234c33__floor_002__run_003""]],[""class"",""BrickThinWall""]]}";
			};
			id=2587;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064582825;
		};
		class Item164
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,19.794912,4694.7393};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__run_004__module_001"",""MapAutomation"",""b8d79c0234c33__floor_002__run_004""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2588;
			type="land_ganzazhelezo3";
			atlOffset=0.0274086;
		};
		class Item165
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,19.804996,4700.043};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__run_004__module_002"",""MapAutomation"",""b8d79c0234c33__floor_002__run_004""]],[""class"",""BrickThinWall""]]}";
			};
			id=2589;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064582825;
		};
		class Item166
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,19.794912,4703.7822};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__run_004__module_003"",""MapAutomation"",""b8d79c0234c33__floor_002__run_004""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2590;
			type="land_ganzazhelezo3";
			atlOffset=0.0274086;
		};
		class Item167
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,19.794912,4705.2607};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__run_004__module_004"",""MapAutomation"",""b8d79c0234c33__floor_002__run_004""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2591;
			type="land_ganzazhelezo3";
			atlOffset=0.0274086;
		};
		class Item168
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5045.8501,19.804996,4697};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__run_005__module_001"",""MapAutomation"",""b8d79c0234c33__floor_002__run_005""]],[""class"",""BrickThinWall""]]}";
			};
			id=2592;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064582825;
		};
		class Item169
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5045.8501,19.804996,4703};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__floor_002__run_005__module_002"",""MapAutomation"",""b8d79c0234c33__floor_002__run_005""]],[""class"",""BrickThinWall""]]}";
			};
			id=2593;
			type="Land_kr_stena_3x6";
			atlOffset=0.0064582825;
		};
		class Item170
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,17.737249,4696.2607};
				angles[]={1.5707964,0,0};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__portal_001__lintel"",""MapAutomation"",""b8d79c0234c33__portal_001""]],[""class"",""ConcreteSmallPole""]]}";
			};
			id=2594;
			type="Land_ConcreteWall_01_l_pole_F";
			atlOffset=1.7568703;
		};
		class Item171
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,17.737249,4702.2607};
				angles[]={1.5707964,0,0};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__portal_002__lintel"",""MapAutomation"",""b8d79c0234c33__portal_002""]],[""class"",""ConcreteSmallPole""]]}";
			};
			id=2595;
			type="Land_ConcreteWall_01_l_pole_F";
			atlOffset=1.7568703;
		};
		class Item172
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5040.7393,17.737249,4694.1499};
				angles[]={0,0,1.5707964};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__portal_003__lintel"",""MapAutomation"",""b8d79c0234c33__portal_003""]],[""class"",""ConcreteSmallPole""]]}";
			};
			id=2596;
			type="Land_ConcreteWall_01_l_pole_F";
			atlOffset=1.7568703;
		};
		class Item173
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,21.04225,4696.2607};
				angles[]={1.5707964,0,0};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__portal_004__lintel"",""MapAutomation"",""b8d79c0234c33__portal_004""]],[""class"",""ConcreteSmallPole""]]}";
			};
			id=2597;
			type="Land_ConcreteWall_01_l_pole_F";
			atlOffset=1.7568703;
		};
		class Item174
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,16.112755,4696.2607};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__portal_001"",""MapAutomation"",""b8d79c0234c33__portal_001""]],[""class"",""WoodenDoor""]]}";
			};
			id=2598;
			type="Land_xlamdoor";
			atlOffset=0.020799637;
		};
		class Item175
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,16.112755,4702.2607};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__portal_002"",""MapAutomation"",""b8d79c0234c33__portal_002""]],[""class"",""WoodenDoor""]]}";
			};
			id=2599;
			type="Land_xlamdoor";
			atlOffset=0.020799637;
		};
		class Item176
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5040.7393,16.112755,4694.1499};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__portal_003"",""MapAutomation"",""b8d79c0234c33__portal_003""]],[""class"",""WoodenDoor""]]}";
			};
			id=2600;
			type="Land_xlamdoor";
			atlOffset=0.020799637;
		};
		class Item177
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5038.4785,19.417755,4696.2607};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__portal_004"",""MapAutomation"",""b8d79c0234c33__portal_004""]],[""class"",""WoodenDoor""]]}";
			};
			id=2601;
			type="Land_xlamdoor";
			atlOffset=0.020799637;
		};
		class Item178
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5041.5,16.65,4700};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__stairs_001"",""MapAutomation"",""b8d79c0234c33__stairs_001""]],[""class"",""StoneBigLadderDouble""]]}";
			};
			id=2602;
			type="Land_lest_kletka";
			atlOffset=2.9563904e-05;
		};
		class Item179
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5039.9053,19.044245,4698.5};
				angles[]={1.5707964,1.5707964,0};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__stairs_001__guard_0"",""MapAutomation"",""b8d79c0234c33__stairs_001""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2603;
			type="land_ganzazhelezo3";
			atlOffset=2.5817413;
		};
		class Item180
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5039.9053,19.044245,4701.5};
				angles[]={1.5707964,1.5707964,0};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__stairs_001__guard_1"",""MapAutomation"",""b8d79c0234c33__stairs_001""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2604;
			type="land_ganzazhelezo3";
			atlOffset=2.5817413;
		};
		class Item181
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5043.0947,19.044245,4698.5};
				angles[]={1.5707964,1.5707964,0};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__stairs_001__guard_2"",""MapAutomation"",""b8d79c0234c33__stairs_001""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2605;
			type="land_ganzazhelezo3";
			atlOffset=2.5817413;
		};
		class Item182
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5043.0947,19.044245,4701.5};
				angles[]={1.5707964,1.5707964,0};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__stairs_001__guard_3"",""MapAutomation"",""b8d79c0234c33__stairs_001""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2606;
			type="land_ganzazhelezo3";
			atlOffset=2.5817413;
		};
		class Item183
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5041.5,19.044245,4703.0947};
				angles[]={0,0,1.5707964};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__stairs_001__guard_4"",""MapAutomation"",""b8d79c0234c33__stairs_001""]],[""class"",""SteelThinWallSmall""]]}";
			};
			id=2607;
			type="land_ganzazhelezo3";
			atlOffset=2.5817413;
		};
		class Item184
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5035.4932,15.473424,4697};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__bedroom_001__sleeping_001"",""MapAutomation"",""b8d79c0234c33__bedroom_001""]],[""class"",""SingleWhiteBed""]]}";
			};
			id=2608;
			type="bed4";
		};
		class Item185
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5035.4932,15.473424,4698.1958};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__bedroom_001__sleeping_002"",""MapAutomation"",""b8d79c0234c33__bedroom_001""]],[""class"",""SingleWhiteBed""]]}";
			};
			id=2609;
			type="bed4";
		};
		class Item186
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5034.9512,15.7822,4695.9243};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__bedroom_001__storage_001"",""MapAutomation"",""b8d79c0234c33__bedroom_001""]],[""class"",""SteelGreenCabinet""]]}";
			};
			id=2610;
			type="shkafsin";
		};
		class Item187
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5035.4932,18.778423,4700};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__bedroom_002__sleeping_001"",""MapAutomation"",""b8d79c0234c33__bedroom_002""]],[""class"",""SingleWhiteBed""]]}";
			};
			id=2611;
			type="bed4";
		};
		class Item188
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5036.9854,18.778423,4702.1958};
				angles[]={0,4.712389,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__bedroom_002__sleeping_002"",""MapAutomation"",""b8d79c0234c33__bedroom_002""]],[""class"",""SingleWhiteBed""]]}";
			};
			id=2612;
			type="bed4";
		};
		class Item189
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5034.9512,19.0872,4698.9243};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=5;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__bedroom_002__storage_001"",""MapAutomation"",""b8d79c0234c33__bedroom_002""]],[""class"",""SteelGreenCabinet""]]}";
			};
			id=2613;
			type="shkafsin";
		};
		class Item190
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5035.0498,18.737295,4695.0498};
				angles[]={0,1.5707964,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__bedroom_002__work_surface_001"",""MapAutomation"",""b8d79c0234c33__bedroom_002""]],[""class"",""SmallWoodenTable""]]}";
			};
			id=2614;
			type="Land_WoodenTable_small_F";
		};
		class Item191
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5035.0562,18.304344,4695.999};
				angles[]={0,4.712389,0};
			};
			side="Empty";
			flags=4;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__bedroom_002__seating_001"",""MapAutomation"",""b8d79c0234c33__bedroom_002""]],[""class"",""WoodenChair""]]}";
			};
			id=2615;
			type="Land_ChairWood_F";
		};
		class Item192
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5035.5498,17.939999,4697.5498};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__bedroom_001__lighting_001"",""MapAutomation"",""b8d79c0234c33__bedroom_001""]],[""class"",""LampCeiling""]]}";
			};
			id=2616;
			type="Lamp_tarelka";
			atlOffset=2.2852373;
		};
		class Item193
		{
			dataType="Object";
			class PositionInfo
			{
				position[]={5037.2998,21.244999,4699.2998};
			};
			side="Empty";
			flags=1;
			class Attributes
			{
				init="{createHashMapFromArray[[""customProps"",createHashMapFromArray[]],[""__ai"",[""b8d79c0234c33__bedroom_002__lighting_001"",""MapAutomation"",""b8d79c0234c33__bedroom_002""]],[""class"",""LampCeiling""]]}";
			};
			id=2617;
			type="Lamp_tarelka";
			atlOffset=2.7783775;
		};
	};
};
