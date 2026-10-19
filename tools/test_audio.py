import copy,importlib.util,json,tempfile,unittest
from pathlib import Path
import audio
class NarrationTests(unittest.TestCase):
 def setUp(self):
  self.original=audio.ROOT;self.tmp=tempfile.TemporaryDirectory();audio.ROOT=Path(self.tmp.name)
  (audio.ROOT/'content').mkdir();(audio.ROOT/'audio').mkdir()
  for name in audio.ORDER:(audio.ROOT/'content'/f'{name}.json').write_text('[]')
  (audio.ROOT/'audio/code-narration.json').write_text('{}')
  self.source=audio.ROOT/'content/start.json'
  self.source.write_text(json.dumps([{'slug':'sample','title':'Sample','body':'<p>First request.</p><h2>Next</h2><p>One invariant.</p>'}]))
 def tearDown(self):audio.ROOT=self.original;self.tmp.cleanup()
 def test_all_sections_and_stable_ids(self):
  tracks=audio.sync();self.assertEqual(len({q['id'] for q in tracks}),2);self.assertTrue(all(q['id'].startswith('sample-') for q in tracks));self.assertEqual(len(audio.validate(False)),2)
 def test_changed_source_invalidates_asset(self):
  tracks=audio.sync();tracks[0].update(src='audio/media/old.m4a',duration=2,sha256='fake',provenance='x')
  audio.save(audio.ROOT/'audio/catalog.json',{'version':1,'tracks':tracks})
  self.source.write_text(self.source.read_text().replace('First request.','Changed request.'))
  with self.assertRaises(AssertionError):audio.validate(False)
  self.assertIsNone(audio.sync()[0]['src'])
 def test_new_section_detected(self):
  audio.sync();self.source.write_text(self.source.read_text().replace('</p>"','</p><h2>New</h2><p>New lesson.</p>"'))
  with self.assertRaises(AssertionError):audio.validate(False)
 def test_narration_preserves_boundaries_and_math(self):
  s=audio.speak('<p>Use 2 × 3 GB, p99.</p><p>Then retry.</p>',{})
  self.assertIn('times',s);self.assertIn('gigabytes',s);self.assertIn('\n\nThen retry',s)
 def test_unmapped_diagram_fails_closed(self):
  with self.assertRaises(AssertionError):audio.speak('<pre>A → B</pre>',{})
 def test_unregistered_content_fails(self):
  (audio.ROOT/'content/unregistered.json').write_text('[]')
  with self.assertRaises(AssertionError):audio.expected()
 def test_math_is_spoken(self):
  s=audio.speak('<p>10^9 and R + W > N.</p>',{})
  self.assertIn('10 to the power 9',s);self.assertIn('R plus W greater than N',s)
 def test_inline_formulas_are_explained(self):
  bucket=audio.speak('<p><code>available = min(B, old_tokens + r × dt)</code></p>',{})
  self.assertIn('smaller of bucket capacity',bucket);self.assertNotIn('min(',bucket)
  stock=audio.speak('<p><code>sellable - reserved - sold &gt;= requested_quantity</code></p>',{})
  self.assertIn('must be at least the requested quantity',stock)
  self.assertIn('divided by',audio.speak('<p>1,000 / 86,400</p>',{}))
 def test_insertions_preserve_unchanged_track_identity(self):
  before={q['title']:q['id'] for q in audio.expected()}
  self.source.write_text(self.source.read_text().replace('<h2>Next</h2>','<h2>Inserted</h2><p>New material.</p><h2>Next</h2>'))
  after={q['title']:q['id'] for q in audio.expected()}
  self.assertEqual(before['Introduction'],after['Introduction']);self.assertEqual(before['Next'],after['Next'])
 def test_body_change_versions_track_identity(self):
  before=audio.expected()[0]['id'];self.source.write_text(self.source.read_text().replace('First request.','Changed request.'))
  self.assertNotEqual(before,audio.expected()[0]['id'])
 def test_legacy_identity_migration_keeps_matching_audio(self):
  tracks=audio.sync();canonical=tracks[0]['id'];tracks[0]['id']='sample-01'
  tracks[0].update(src='audio/media/existing.m4a',duration=12,sha256='fixture',provenance='audio/provenance/existing.json')
  audio.save(audio.ROOT/'audio/catalog.json',{'version':1,'tracks':tracks})
  migrated=audio.sync()[0]
  self.assertEqual(migrated['id'],canonical);self.assertEqual(migrated['src'],'audio/media/existing.m4a')
 def test_missing_recordings_fail_gate(self):
  audio.sync()
  with self.assertRaises(AssertionError):audio.validate()
if __name__=='__main__':unittest.main()
