const assert=require('assert');
const {KEY,createController,mount}=require('../podcast.js');
const tracks=[
 {id:'a',title:'Foundations',chapter:'Core',chapterTitle:'Foundation Chapter',src:'a.m4a',status:'Ready',transcript:'Features and targets.',chapterUrl:'course/01-foundations.html'},
 {id:'b',title:'Math',chapter:'Core',src:'b.m4a',status:'Ready',transcript:'Vectors.',chapterUrl:'course/02-math.html'},
 {id:'c',title:'Probability',chapter:'Core',src:null,status:'Not generated',transcript:'',chapterUrl:'course/03-probability.html'}
];
function fixture(saved,options={}){
 let now=0,writes=0,raw=saved===undefined?null:typeof saved==='string'?saved:JSON.stringify(saved);
 const handlers={};
 const audio={paused:true,ended:false,currentTime:0,duration:NaN,playbackRate:1,playCalls:0,loadCalls:0,
 addEventListener(k,fn){(handlers[k]??=[]).push(fn);},emit(k){for(const fn of handlers[k]||[])fn();},
 pause(){const was=this.paused;this.paused=true;if(!was)this.emit('pause');},
 removeAttribute(k){if(k==='src')this.src='';},
 load(){this.loadCalls++;this.duration=NaN;this.currentTime=0;this.ended=false;},
 play(){this.playCalls++;if(options.reject)return Promise.reject(Error('NotAllowedError'));this.duration=120;this.emit('loadedmetadata');this.ended=false;this.paused=false;this.emit('play');return options.pending?new Promise(resolve=>options.resolve=resolve):Promise.resolve();},
 finish(){this.currentTime=this.duration;this.ended=true;this.paused=true;this.emit('pause');this.emit('ended');}
 };
 const storage=options.storage || {getItem(){return raw;},setItem(k,v){assert.equal(k,KEY);writes++;raw=v;}};
 const states=[];const api=createController({audio,tracks:options.tracks||tracks,storage,clock:()=>now,onChange:s=>states.push(s),mediaSession:options.mediaSession,Metadata:options.Metadata});
 return {api,audio,states,setNow(v){now=v;},raw(){return JSON.parse(raw);},writes(){return writes;}};
}
const tick=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
 let f=fixture();assert.equal(f.audio.playCalls,0);assert.equal(f.api.snapshot().continuous,false);await f.api.play();assert.equal(f.audio.src,'a.m4a');assert(f.api.snapshot().armed);
 f.api.setContinuous(true);f.audio.finish();await tick();assert.equal(f.api.snapshot().current,'b');assert.equal(f.audio.src,'b.m4a');assert.equal(f.audio.playCalls,2);console.log('PASS: explicit first play and opt-in continuation reuse one audio element');
 f.audio.finish();await tick();assert.equal(f.api.snapshot().current,'c');assert(!f.api.snapshot().armed);assert(f.api.snapshot().message.includes('no recording'));assert.equal(f.audio.src,'');console.log('PASS: missing next chapter stops instead of silently skipping');
 f=fixture();await f.api.play();f.audio.currentTime=42;f.audio.emit('timeupdate');let writes=f.writes();f.setNow(1000);f.audio.currentTime=46;f.audio.emit('timeupdate');assert.equal(f.writes(),writes);f.api.pause();assert.equal(f.raw().positions.a,46);assert(!f.api.snapshot().armed);
 f.api.setSpeed(1.5);f.api.setContinuous(true);const restored=fixture(f.raw());assert.equal(restored.audio.playCalls,0);assert.equal(restored.api.snapshot().position,46);assert.equal(restored.api.snapshot().speed,1.5);assert.equal(restored.api.snapshot().continuous,true);await restored.api.play();assert.equal(restored.audio.currentTime,46);assert.equal(restored.audio.playbackRate,1.5);console.log('PASS: throttled persistence, pause flush, silent reload and exact-position resume');
 f.api.stop();assert.equal(f.api.snapshot().position,0);assert(!f.api.snapshot().armed);f.audio.finish();await tick();assert.equal(f.api.snapshot().current,'a');console.log('PASS: Stop resets position and cancels the current continuous run');
 f=fixture();await f.api.play();f.api.setContinuous(true);f.api.pause();f.audio.finish();await tick();assert.equal(f.api.snapshot().current,'a');f.api.select('b');assert(f.audio.paused);assert.equal(f.audio.src,'');assert.equal(f.api.snapshot().current,'b');console.log('PASS: pause cancels continuation; manual chapter changes clear stale source and remain paused');
 const blocked=fixture(undefined,{reject:true});assert.equal(await blocked.api.play(),false);assert(!blocked.api.snapshot().armed);assert(blocked.api.snapshot().message.includes('Tap Play'));console.log('PASS: rejected play presents explicit tap-to-continue recovery');
 const opts={pending:true};f=fixture(undefined,opts);const promise=f.api.play();f.api.pause();opts.resolve();assert.equal(await promise,false);assert(!f.api.snapshot().armed);const nativeOptions={pending:true};const native=fixture(undefined,nativeOptions);const nativePromise=native.api.play();native.audio.pause();nativeOptions.resolve();assert.equal(await nativePromise,false);assert(!native.api.snapshot().armed);assert(native.api.snapshot().message.includes('Paused'));console.log('PASS: custom/native pause while play is pending invalidates its completion');
 f=fixture({version:1,current:'b',positions:{b:999999,a:-1,c:'bad',unknown:12},speed:100,continuous:true});assert.equal(f.api.snapshot().speed,1);await f.api.play();assert(f.audio.currentTime<120);assert(f.audio.currentTime>119);f.audio.currentTime=35;f.audio.emit('seeked');assert.equal(f.raw().positions.b,35);console.log('PASS: corrupt position/speed sanitization, duration clamping and seek persistence');
 for(const saved of ['{broken',[],{version:99,current:'b',positions:{a:50},speed:2}]){f=fixture(saved);assert.equal(f.api.snapshot().current,'a');assert.equal(f.api.snapshot().position,0);assert.equal(f.audio.playCalls,0);}
 f=fixture(undefined,{storage:{getItem(){throw Error('denied');},setItem(){throw Error('quota');}}});await f.api.play();f.api.pause();assert.equal(f.api.snapshot().storageOK,false);console.log('PASS: malformed/versioned/denied storage leaves playback usable');
 f=fixture(undefined,{tracks:tracks.slice(0,2)});f.api.select('b');f.api.setContinuous(true);await f.api.play();f.audio.finish();assert.equal(f.api.snapshot().current,'b');assert(f.api.snapshot().message.includes('final'));assert(!f.api.snapshot().armed);console.log('PASS: final chapter ends without wrapping');
 f=fixture();await f.api.play();f.api.setContinuous(true);f.audio.emit('waiting');assert(f.api.snapshot().armed);f.audio.emit('error');assert(!f.api.snapshot().armed);assert(f.api.snapshot().message.includes('unavailable'));f.audio.emit('pause');assert(f.api.snapshot().message.includes('unavailable'));f.api.stop();f.audio.emit('pause');assert(f.api.snapshot().message.includes('Stopped'));console.log('PASS: buffering preserves intent; decoding/network error cancels continuation');
 f=fixture();f.api.select('c');assert.equal(await f.api.play(),false);f.api.setLocalSource('c','blob:private');await f.api.play();assert.equal(f.audio.src,'blob:private');assert(!JSON.stringify(f.raw()).includes('blob:'));assert.equal(tracks[2].src,null);console.log('PASS: local file source remains ephemeral, unuploaded and outside persisted state');
 const actions={};const session={setActionHandler(k,fn){actions[k]=fn;},setPositionState(s){assert(s.position<=s.duration);}};
 f=fixture(undefined,{mediaSession:session,Metadata:function(v){Object.assign(this,v);}});await actions.play();assert(session.metadata.title.includes('Foundations'));actions.pause();assert(!f.api.snapshot().armed);actions.nexttrack();assert.equal(f.api.snapshot().current,'b');assert(f.audio.paused);console.log('PASS: optional Media Session metadata, play/pause and paused chapter selection');
 // DOM-double wiring; this does not claim rendered or native-browser behavior.
 const ids={};function el(){return {handlers:{},textContent:'',value:'',checked:false,hidden:true,files:[],addEventListener(k,fn){this.handlers[k]=fn;}};}
 for(const name of ['track','title','status','storage','position','speed','continue','play','resume','pause','stop','next','lesson','download','transcript','file'])ids['audio-'+name]=el();
 f=fixture();ids['course-audio']=f.audio;ids['audio-data']={textContent:JSON.stringify(tracks)};ids['listen-interactive']=el();
 const doc={handlers:{},getElementById(id){return ids[id];},addEventListener(k,fn){this.handlers[k]=fn;}};
 const win={handlers:{},navigator:{},URL:{createObjectURL(){return 'blob:chosen';},revokeObjectURL(){}},addEventListener(k,fn){this.handlers[k]=fn;}};
 Object.defineProperty(win,'localStorage',{get(){throw Error('denied');}});
 const ui=mount(doc,win);assert.equal(ids['listen-interactive'].hidden,false);assert(ids['audio-storage'].textContent.includes('unavailable'));await ids['audio-play'].handlers.click();ids['audio-continue'].checked=true;ids['audio-continue'].handlers.change();assert(ui.snapshot().continuous);win.handlers.pagehide();assert(!ui.snapshot().armed);win.handlers.pageshow();assert(f.audio.paused);ids['audio-track'].value='c';ids['audio-track'].handlers.change();assert(ids['audio-play'].disabled);ids['audio-file'].files=[{name:'sample.m4a'}];ids['audio-file'].handlers.change();assert(!ids['audio-play'].disabled);assert.equal(ids['audio-download'].href,'blob:chosen');console.log('PASS: DOM controls, local-file selection, storage denial and page lifecycle wiring');
 assert.equal(KEY,'system-design-fluency-audio-v1');
 function hashFixture(hash,saved='b'){
  const nodes={};for(const name of ['track','title','status','storage','position','speed','continue','play','resume','pause','stop','next','lesson','download','transcript','file'])nodes['audio-'+name]=el();
  const media=fixture().audio;nodes['course-audio']=media;nodes['audio-data']={textContent:JSON.stringify({version:1,tracks})};nodes['listen-interactive']=el();
  const document={getElementById:id=>nodes[id],addEventListener(){}};
  const window={handlers:{},navigator:{},location:{hash,search:''},localStorage:{getItem:()=>JSON.stringify({version:1,current:saved,positions:{b:25}}),setItem(){}},addEventListener(k,v){this.handlers[k]=v;}};
  window.history={replaceState(a,b,url){window.location.hash=url;}};
  return {api:mount(document,window),window,media,nodes};
 }
 const linked=hashFixture('#a');assert.equal(linked.api.snapshot().current,'a');assert.equal(linked.media.playCalls,0);assert(linked.nodes['audio-title'].textContent.includes('Foundation Chapter'));
 await linked.api.play();linked.window.location.hash='#b';linked.window.handlers.hashchange();assert.equal(linked.api.snapshot().current,'b');assert(linked.media.paused);assert(!linked.api.snapshot().armed);
 const playCalls=linked.media.playCalls;linked.window.location.hash='#unknown';linked.window.handlers.hashchange();assert.equal(linked.api.snapshot().current,'b');assert.equal(linked.media.playCalls,playCalls);
 const unknown=hashFixture('#unknown');assert.equal(unknown.api.snapshot().current,'b');assert.equal(unknown.api.snapshot().position,25);assert.equal(unknown.media.playCalls,0);
 unknown.window.location.hash='#%broken';unknown.window.handlers.hashchange();assert.equal(unknown.api.snapshot().current,'b');
 linked.api.select('a');assert.equal(linked.window.location.hash,'#a');linked.api.select('b');assert.equal(linked.window.location.hash,'#b');
 console.log('PASS: selected section updates URL for truthful reload/resume; known hashes override saved selection paused; hashchange pauses; unknown/malformed hashes preserve state; chapter and section title labels');
 console.log('PASS: 15 audio behavior groups (media/DOM doubles; no real-browser/background playback claim)');
})().catch(error=>{console.error(error);process.exitCode=1;});

// Generator integration checks with temporary local fixtures, not decoded audio.
require('child_process').execFileSync('python3',['-c', String.raw`
import importlib.util, json, tempfile
from pathlib import Path
spec=importlib.util.spec_from_file_location('listen', 'tools/listen.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as d:
 r=Path(d);(r/'audio').mkdir();(r/'lesson.html').write_text('<h1>Lesson</h1>')
 (r/'audio/a.m4a').write_bytes(b'fixture');(r/'audio/a.txt').write_text('A <script> tag & a transcript.')
 q=dict(id='lesson-core',title='A <lesson>',chapter='lesson',chapterTitle='The Lesson Chapter',chapterUrl='lesson.html',src='audio/a.m4a',transcript='audio/a.txt',duration=12.5)
 def save(): (r/'audio/catalog.json').write_text(json.dumps(dict(version=1,tracks=[q])))
 save();items=m.tracks(r);assert items[0]['transcript'].startswith('A <script>')
 body=m.page(items);assert 'The Lesson Chapter · A &lt;lesson&gt;' in body and '<script> tag' not in body
 assert json.loads(m.safe_json(items))==items
 doc=m.write_page(r).read_text();assert 'preload="none"' in doc and 'autoplay' not in doc
 assert 'audio-continue' in doc and 'Matching transcript' in doc
 assert m.local_file(r,'audio/a.m4a','Recording',True).is_file()
 for field,value in [('src','../outside.m4a'),('chapterUrl','https://example.test/'),('duration',float('inf')),('transcript',None)]:
  old=q[field];q[field]=value;save()
  try: m.tracks(r)
  except ValueError: pass
  else: raise AssertionError(field+' accepted invalid value')
  q[field]=old
 print('PASS: catalog schema/local paths/transcripts/durations, safe JSON, no autoplay, standalone listening generator')
`],{stdio:'inherit',cwd:require('path').resolve(__dirname,'..')});
