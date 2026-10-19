import unittest
from design import TokenBucket, Reservations, FencedJob
class DesignTests(unittest.TestCase):
    def test_retry_does_not_consume_twice(self):
        r=Reservations(3)
        self.assertTrue(r.reserve('a',2)); self.assertTrue(r.reserve('a',2))
        self.assertEqual(r.remaining,1); self.assertFalse(r.reserve('b',2))
    def test_key_payload_mismatch(self):
        r=Reservations(3); r.reserve('a',1)
        with self.assertRaises(ValueError): r.reserve('a',2)
        self.assertEqual(r.remaining,2)
    def test_invalid_quantity(self):
        with self.assertRaises(ValueError): Reservations(2).reserve('a',-1)
    def test_bucket_boundary_and_cap(self):
        b=TokenBucket(2,1,0)
        self.assertFalse(b.allow(.999)); self.assertTrue(b.allow(1))
        b.allow(100); self.assertEqual(b.tokens,1)
        with self.assertRaises(ValueError): b.allow(99)
    def test_fence_rejects_late_worker(self):
        j=FencedJob(); old=j.claim(); new=j.claim()
        self.assertFalse(j.complete(old,'bad')); self.assertTrue(j.complete(new,'ok'))
        self.assertFalse(j.complete(new,'duplicate')); self.assertEqual(j.result,'ok')
    def test_units(self):
        self.assertEqual(86400000/86400,1000)
        self.assertEqual(1000*500*86400,43200000000)
        self.assertAlmostEqual(1000*.2,200)
        self.assertAlmostEqual(30*24*60*.001,43.2)
if __name__=='__main__': unittest.main()
