"""Retained two-story contact section. This is not an accepted complete house."""
import json
from pathlib import Path
from building_generator.structure import load_structural_assets, anchor_position
from room_generator.gateway import MapAutomationRoomGateway

BASE=Path(__file__).resolve().parent


def main():
    assets=load_structural_assets();g=MapAutomationRoomGateway(20);before=g.snapshot()
    wall='BrickThinWallSmall';floor='ConcretePanel'
    h=assets[wall]['dimensions'][2];t=assets[floor]['dimensions'][2];story=h+t
    ops=[];expected={}
    for index in range(3):
        sid=f'phase8a_contact__floor_{index}'
        p=anchor_position(assets[floor],'topCenter',[4920,4700,10+index*story],90)
        ops.append({'operation':'create','arguments':{'semanticId':sid,'class':floor,'position':p,
            'rotation':[0,0,90],'scale':1,'parentId':'phase8a_contact'}})
        expected[sid]=('top',10+index*story)
    for index in range(2):
        sid=f'phase8a_contact__wall_{index}'
        p=anchor_position(assets[wall],'bottomCenter',[4920,4700,10+index*story])
        ops.append({'operation':'create','arguments':{'semanticId':sid,'class':wall,'position':p,
            'rotation':[0,0,0],'scale':1,'parentId':'phase8a_contact'}})
        expected[sid]=('bottom',10+index*story)
    old={x['semanticId']:x for x in before.objects}
    if any(x['arguments']['semanticId'] in old for x in ops):
        raise ValueError('Contact section already exists; inspect retained evidence before replacing it.')
    applied=g.apply(ops,before.revision);rows={x['semanticId']:x for x in applied['result']}
    if any(rows[sid]!=row for sid,row in old.items()):
        raise ValueError('Existing scene changed during contact test')
    errors=[];measurements=[]
    for sid,(face,z) in expected.items():
        row=rows[sid]
        dz=row['positionASL'][2]-row['position'][2]
        index=1 if face=='top' else 0
        actual=row['modelOriginASL'][2]+row['visualBoundsModel'][index][2]-dz
        error=actual-z
        measurements.append({'semanticId':sid,'face':face,'expectedEdenElevation':z,
            'measuredElevation':actual,'errorMeters':error,'readback':row})
        if abs(error)>.002:errors.append(sid)
    artifact={'status':'CONTACT_PASS' if not errors else 'CONTACT_FAIL','scope':'native Eden visual envelope contacts; not whole shell acceptance',
        'measurements':measurements,'errors':errors,'storyHeight':story,'scenePreserved':True,
        'kept':True,'revision':applied['revision'],'captures':[]}
    output=BASE/'artifacts/phase8a_contact_live.json'
    output.write_text(json.dumps(artifact,indent=2)+'\n',encoding='utf-8')
    if errors:raise ValueError(str(errors))
    try:
        dz=rows['phase8a_contact__floor_0']['positionASL'][2]-rows['phase8a_contact__floor_0']['position'][2]
        captured=g.capture(applied['revision'],[{'viewId':'contact_section','cameraRole':'structural_contact',
            'positionASL':[4926,4690,13+dz],'targetASL':[4920,4700,13+dz],
            'fov':.7,'captureClassOverlay':False}])
        artifact['captures']=captured['result']
    except Exception as exc:
        artifact['captureError']=str(exc)
    output.write_text(json.dumps(artifact,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':artifact['status'],'artifact':str(output),'captures':artifact['captures']}))


if __name__=='__main__':main()
