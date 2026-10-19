"""Independent recomputation of the numerical assumptions used in the course.
Decimal storage units; synthetic examples, no production throughput assertions.
"""
import unittest
class Arithmetic(unittest.TestCase):
 def test_shortener(self):
  self.assertAlmostEqual(1e6/86400,11.574074,places=5)
  self.assertAlmostEqual(100e6/86400*10,11574.074,places=3)
  self.assertEqual(1e6*500*365,182.5e9)
  self.assertAlmostEqual(365e6/(62**10),4.348e-10,delta=1e-13)
 def test_rate_limiter(self):
  self.assertAlmostEqual(100000*200/86400,231.48148,places=4)
  self.assertEqual(50000*200,10e6)
  self.assertEqual(200+100*3,500)
 def test_scheduler(self):
  self.assertAlmostEqual(1e6/86400*10*2/.7,330.68783,places=4)
  # Course rounds peak upward to116 before headroom: ceil(116*2/.7)=332.
  import math
  self.assertEqual(math.ceil(116*2/.7),332)
  self.assertEqual(1e6*30*1000,30e9)
 def test_analytics(self):
  self.assertEqual(100000*50*500,2.5e9)
  self.assertEqual(2.5e9*7*3,52.5e9)
  self.assertEqual(2000*20*2*1440,115200000)
  self.assertEqual(2.5e9*365,912.5e9)
 def test_feature_serving(self):
  self.assertEqual(232*200,46400)
  self.assertEqual(100000*20*8,16e6)
  self.assertEqual(40000*30*8,9.6e6)
  self.assertEqual(sum([10,20,25,40,15,40]),150)
 def test_booking_and_region(self):
  self.assertEqual(2000*100*90,18e6)
  self.assertEqual(18e6*200,3.6e9)
  self.assertEqual(200*.05,10)
  self.assertAlmostEqual(30*24*60*(1-.9995),21.6)
  self.assertGreater(.080,.050)
 def test_units_and_sensitivity(self):
  rate=1000;size=500;days=30
  self.assertEqual(rate*size*86400,43.2e9)
  self.assertEqual(2*rate*size*86400,86.4e9)
  self.assertEqual(rate*size*86400*days*2,2.592e12)
  self.assertEqual(1000*.2,200)
  self.assertEqual((1000-600)*60,24000)
  self.assertEqual(24000/(1400-1000),60)
if __name__=='__main__':unittest.main()
