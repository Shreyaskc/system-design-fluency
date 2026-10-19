/* One media element, explicit playback intent, and local-only resumable state. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else { const api = factory(); api.mount(document, window); }
}(this, function () {
  const KEY = 'system-design-fluency-audio-v1';
  const trackLabel = t => (t.chapterTitle || t.chapter || 'Course') + ' · ' + t.title;
  function createController({audio, tracks, storage, onChange=()=>{}, clock=()=>Date.now(), mediaSession, Metadata}) {
    tracks = tracks.map(t=>({...t, section:t.section||t.chapter||'Course narration', lesson:t.chapterUrl||t.lesson, status:t.status||'Recording unavailable'}));
    const byId = new Map(tracks.map(t=>[t.id,t]));
    const sources = new Map();
    let saved, storageOK=!!storage;
    let raw;
    try { raw=storage?.getItem(KEY); } catch (_) {storageOK=false;}
    try {saved=JSON.parse(raw||'null');}catch(_){saved=null;}
    const positions={};
    if (saved?.version===1 && saved.positions && typeof saved.positions==='object') {
      for (const [id,value] of Object.entries(saved.positions)) if (byId.has(id) && Number.isFinite(value) && value>=0 && value<1e7) positions[id]=value;
    }
    let current=saved?.version===1 && byId.has(saved?.current) ? saved.current : tracks[0]?.id;
    let speed=saved?.version===1 && Number.isFinite(saved.speed) && saved.speed>=0.5 && saved.speed<=3 ? saved.speed : 1;
    let continuous=saved?.version===1 && saved.continuous===true;
    let terminalMessage=null;
    let armed=false, message='', generation=0, loaded=null, pendingSeek=null, lastWrite=-Infinity;
    const source=()=>sources.get(current)||byId.get(current)?.src;
    const snapshot=()=>({current, track:byId.get(current), speed, continuous, armed, message, storageOK, position:positions[current]||0, available:!!source()});
    function notify(){onChange(snapshot());}
    function persist(force=false){
      if (!force && clock()-lastWrite<5000) return;
      lastWrite=clock();
      try { storage?.setItem(KEY,JSON.stringify({version:1,current,speed,continuous,positions})); } catch (_) {storageOK=false;}
    }
    function capture(force=false){
      if (loaded===current && Number.isFinite(audio.currentTime) && audio.currentTime>=0) positions[current]=audio.currentTime;
      persist(force);
    }
    function metadata(){
      if (!mediaSession) return;
      try {
        if (Metadata) mediaSession.metadata=new Metadata({title:trackLabel(byId.get(current)),artist:'System Design Fluency'});
        mediaSession.playbackState=audio.paused?'paused':'playing';
        if (loaded===current && Number.isFinite(audio.duration) && audio.duration>0 && mediaSession.setPositionState) mediaSession.setPositionState({duration:audio.duration,playbackRate:speed,position:Math.min(audio.currentTime||0,audio.duration)});
      } catch (_) { /* Optional browser capability, never required for playback. */ }
    }
    function seekPending(){
      if (pendingSeek===null || loaded!==current || !Number.isFinite(audio.duration) || audio.duration<=0) return;
      audio.currentTime=Math.min(Math.max(pendingSeek,0),Math.max(0,audio.duration-0.01));
      positions[current]=audio.currentTime;pendingSeek=null;metadata();
    }
    function load(){
      if (!source()) return false;
      if (loaded!==current) {
        audio.pause();loaded=current;audio.src=source();pendingSeek=positions[current]||0;audio.load();
      }
      audio.playbackRate=speed;metadata();return true;
    }
    function pause(){terminalMessage=null;generation++;armed=false;audio.pause();capture(true);message='Paused. Press Resume to continue.';metadata();notify();}
    function select(id){
      if (!byId.has(id)) return false;
      pause();audio.removeAttribute('src');audio.load();current=id;loaded=null;pendingSeek=null;
      message=source()?'Ready. Press Play or Resume.':byId.get(id).status+'. Choose a local recording to preview.';
      persist(true);metadata();notify();return true;
    }
    async function play(){
      if (!source()) {armed=false;message='No recording for this section yet. Choose a local recording to preview.';notify();return false;}
      // Source preparation may pause old media; establish new intent afterward.
      terminalMessage=null;load();const request=++generation;armed=true;message='Starting playback…';notify();
      try {
        await audio.play();
        if (request!==generation) return false;
        message='Playing';metadata();notify();return true;
      } catch (_) {
        if (request===generation) {armed=false;message='Playback was blocked or interrupted. Tap Play or Resume to continue.';metadata();notify();}
        return false;
      }
    }
    function stop(){pause();positions[current]=0;pendingSeek=0;if(loaded===current)audio.currentTime=0;terminalMessage='Stopped. Position reset; continuous run cancelled.';message=terminalMessage;persist(true);notify();}
    function next(){const i=tracks.findIndex(t=>t.id===current);if(i+1<tracks.length)return select(tracks[i+1].id);pause();message='You reached the final section.';notify();return false;}
    function setSpeed(value){if(!Number.isFinite(value)||value<0.5||value>3)return;speed=value;audio.playbackRate=speed;persist(true);metadata();notify();}
    function setContinuous(value){continuous=value===true;persist(true);notify();}
    function setLocalSource(id,url){if(!byId.has(id))return;pause();sources.set(id,url);if(current===id){audio.removeAttribute('src');audio.load();loaded=null;}message='Local recording ready. Press Play or Resume.';notify();}
    audio.addEventListener('loadedmetadata',seekPending);
    audio.addEventListener('durationchange',seekPending);
    audio.addEventListener('timeupdate',()=>{capture();metadata();notify();});
    audio.addEventListener('seeked',()=>{capture(true);metadata();notify();});
    audio.addEventListener('ratechange',()=>{if(Number.isFinite(audio.playbackRate)&&audio.playbackRate>=0.5&&audio.playbackRate<=3){speed=audio.playbackRate;persist(true);notify();}});
    audio.addEventListener('play',()=>{if(audio.paused)return;armed=true;message='Playing';metadata();notify();});
    audio.addEventListener('pause',()=>{if(audio.paused && !audio.ended){generation++;armed=false;capture(true);message=terminalMessage||'Paused. Press Resume to continue.';metadata();notify();}});
    audio.addEventListener('waiting',()=>{if(!terminalMessage)message='Buffering…';notify();});
    audio.addEventListener('error',()=>{generation++;armed=false;terminalMessage='Recording unavailable or could not be decoded. Choose another recording or retry.';audio.pause();message=terminalMessage;capture(true);notify();});
    audio.addEventListener('ended',()=>{
      const proceed=armed && continuous;
      positions[current]=0;persist(true);armed=false;
      const i=tracks.findIndex(t=>t.id===current);
      if(!proceed){message='Section complete. Press Next to choose another section.';notify();return;}
      if(i+1>=tracks.length){message='You reached the final section.';notify();return;}
      select(tracks[i+1].id);
      if(!source()){message='Next section or chapter has no recording yet. Continuous playback stopped here.';notify();return;}
      play();
    });
    if(mediaSession?.setActionHandler){
      for(const [action,handler] of Object.entries({play, pause, stop, nexttrack:next, previoustrack:()=>{const i=tracks.findIndex(t=>t.id===current);if(i>0)select(tracks[i-1].id);}, seekto:e=>{if(Number.isFinite(e.seekTime)&&Number.isFinite(audio.duration)){audio.currentTime=Math.max(0,Math.min(e.seekTime,audio.duration));capture(true);}}})){
        try{mediaSession.setActionHandler(action,handler);}catch(_){}
      }
    }
    message='Choose Play or Resume. No audio starts automatically.';notify();
    return {play,pause,stop,next,select,setSpeed,setContinuous,setLocalSource,snapshot,flush:()=>capture(true)};
  }
  function mount(doc,win){
    const data=doc.getElementById('audio-data');if(!data)return null;
    let tracks;try{tracks=JSON.parse(data.textContent);}catch(_){return null;}
    if(tracks && !Array.isArray(tracks) && tracks.version===1)tracks=tracks.tracks;
    if(Array.isArray(tracks))tracks=tracks.map(t=>({...t,section:t.section||t.chapter||'Course narration',lesson:t.chapterUrl||t.lesson}));
    if(!Array.isArray(tracks)||!tracks.length)return null;
    const get=id=>doc.getElementById('audio-'+id);let storage;
    try{storage=win.localStorage;}catch(_){}
    const audio=doc.getElementById('course-audio');const localURLs=new Map();
    let hashReady=false,lastHashTrack=null;
    function updateHash(id){try{if(id!==lastHashTrack && win.history?.replaceState){win.history.replaceState(null,'','#'+encodeURIComponent(id));lastHashTrack=id;}}catch(_){}}
    const controller=createController({audio,tracks,storage,mediaSession:win.navigator?.mediaSession,Metadata:win.MediaMetadata,onChange:s=>{
      if(hashReady)updateHash(s.current);
      get('track').value=s.current;get('title').textContent=trackLabel(s.track);
      if(get('status').textContent!==s.message)get('status').textContent=s.message;
      get('storage').textContent=s.storageOK?'Resume state is saved in this browser only.':'Browser storage unavailable: resume works in this tab only.';
      get('position').textContent='Saved position: '+Math.floor(s.position/60)+':'+String(Math.floor(s.position%60)).padStart(2,'0');
      get('speed').value=String(s.speed);get('continue').checked=s.continuous;
      get('play').disabled=!s.available;get('resume').disabled=!s.available;
      get('resume').textContent='Resume at '+Math.floor(s.position/60)+':'+String(Math.floor(s.position%60)).padStart(2,'0');
      get('lesson').href=s.track.lesson;
      const url=localURLs.get(s.current)||s.track.src;get('download').hidden=!url;if(url)get('download').href=url;
      const transcript=s.track.transcript||'A matching narration transcript has not been authored for this section yet.';
      if(get('transcript').textContent!==transcript)get('transcript').textContent=transcript;
    }});
    for(const name of ['play','resume','pause','stop','next'])get(name).addEventListener('click',()=>controller[name==='resume'?'play':name]());
    get('track').addEventListener('change',()=>controller.select(get('track').value));
    get('speed').addEventListener('change',()=>controller.setSpeed(Number(get('speed').value)));
    get('continue').addEventListener('change',()=>controller.setContinuous(get('continue').checked));
    get('file').addEventListener('change',()=>{const file=get('file').files?.[0];if(!file)return;const id=controller.snapshot().current;const old=localURLs.get(id);const url=win.URL.createObjectURL(file);localURLs.set(id,url);controller.setLocalSource(id,url);if(old)win.URL.revokeObjectURL(old);get('file').value='';});
    win.addEventListener('pagehide',()=>{controller.flush();controller.pause();});
    win.addEventListener('pageshow',()=>controller.pause());
    doc.addEventListener('visibilitychange',()=>{if(doc.visibilityState==='hidden')controller.flush();});
    function selectHash(){
      try {
        const requested=decodeURIComponent((win.location?.hash||'').replace(/^#/,''));
        if(requested && tracks.some(t=>t.id===requested))return controller.select(requested);
      }catch(_){} // Malformed or unknown fragment leaves the saved selection intact.
      return false;
    }
    // Explicit known hashes take precedence over saved selection and legacy query links.
    let knownHash=selectHash();
    if(!knownHash){try {const requested=new URLSearchParams(win.location?.search||'').get('track');if(requested)controller.select(requested);}catch(_){}}
    win.addEventListener('hashchange',selectHash);
    hashReady=true;updateHash(controller.snapshot().current);
    doc.getElementById('listen-interactive').hidden=false;
    return controller;
  }
  return {KEY,createController,mount};
}));
