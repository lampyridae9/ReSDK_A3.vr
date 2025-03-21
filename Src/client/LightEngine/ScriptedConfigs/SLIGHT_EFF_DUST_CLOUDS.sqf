// ======================================================
// Copyright (c) 2017-2025 the ReSDK_A3 project
// sdk.relicta.ru
// ======================================================

regScriptEmit(SLIGHT_EFF_DUST_CLOUDS)
	[
		"pt",
		null,
		_emitAlias("Пыль")
		["linkToSrc",[0,0,0]],
		["setParticleParams",[["\A3\data_f\ParticleEffects\Universal\Universal.p3d",16,12,13,0],"","Billboard",1,10,[0,0,0],[0,0,0.2],0,0.0525,0.04,0.05,[4.6,3.5],[[0.403772,0.4,0.395348,0.06],[0.5,0.49223,0.483805,0.11],[0.298466,0.290041,0.3,0.06],[0.395348,0.391135,0.3,0.05],[0.5,0.500654,0.49223,0.015],[0.509079,0.5,0.4,0]],[1000],0.1,0.05,"","","",0,false,0,[[0,0,0,0]]]],
		["setParticleRandom",[2.12,[2,2,1.2],[0.06,0.06,0.45],10,0.2,[0,0,0,0],0,0,0,0]],
		["setParticleCircle",[10,[1,1,0]]],
		["setDropInterval",0.101]
	]
endScriptEmit