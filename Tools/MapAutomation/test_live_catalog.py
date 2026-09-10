"""Fresh evidence validation and historical/live comparison policy."""
import copy
import unittest
from compare_live_catalog import compare_geometry, door_summary


class LiveComparisonTests(unittest.TestCase):
    def setUp(self):
        self.old=dict(model='asset.p3d',visualBounds=dict(value=[[0,0,0],[1,1,1]]),dimensions=dict(value=[1,1,1]))
        self.live=dict(model='asset.p3d',visualBounds=[[0,0,0],[1,1,1]],dimensions=[1,1,1],source='engineMeasured',status='VERIFIED')

    def test_tolerances_and_preserve_historical(self):
        original=copy.deepcopy(self.old)
        for delta,expected in [(0,'MATCH'),(.004,'MATCH'),(.015,'MINOR_DIFFERENCE'),(.03,'SIGNIFICANT_DIFFERENCE')]:
            p=copy.deepcopy(self.live);p['visualBounds'][1][0]+=delta;p['dimensions'][0]+=delta
            self.assertEqual(compare_geometry(self.old,p)['classification'],expected)
        self.assertEqual(self.old,original)

    def test_model_change_cannot_match(self):
        self.live['model']='other.p3d'
        self.assertEqual(compare_geometry(self.old,self.live)['classification'],'SIGNIFICANT_DIFFERENCE')

    def test_missing_and_nan_are_not_measurements(self):
        self.assertEqual(compare_geometry(self.old,None)['classification'],'MISSING_DATA')
        self.live['dimensions'][0]=float('nan')
        self.assertEqual(compare_geometry(self.old,self.live)['classification'],'MISSING_DATA')

    def test_door_requires_readback_not_just_requested_phase(self):
        samples=[dict(actualPhase=i/10,requestedPhase=i/10,visualBounds=[[0,0,0],[1,1,1]],selectionPositions=[['xlamdoor',[i/10,0,0]]]) for i in range(8)]
        result=door_summary(dict(doorSamples=samples,lodEvidence={'Memory':{'namedPositions':[['xlamdoor_axis',[0,0,0]]]}}))
        self.assertEqual(result['status'],'VERIFIED_PHASES')
        self.assertEqual(result['sampledOpeningEnvelope']['status'],'APPROXIMATE')
        self.assertEqual(result['hingeSide']['value'],'negativeX')
        self.assertEqual(result['trackedSelectionMotion']['value'],[0.7,0,0])
        samples[-1]['actualPhase']=0
        self.assertEqual(door_summary(dict(doorSamples=samples))['status'],'FAIL')
        self.assertEqual(door_summary(None)['status'],'UNKNOWN')


if __name__=='__main__': unittest.main()
