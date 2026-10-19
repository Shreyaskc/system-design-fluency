const fs=require('fs'),vm=require('vm'),assert=require('assert');
(async()=>{
 const listeners={},stored={};
 const box={dataset:{study:'one'},checked:false,addEventListener:(n,f)=>listeners[n]=f};
 const input={value:'',addEventListener:(n,f)=>listeners.search=f};
 const links=['storage.html','chat.html'].map(h=>({textContent:h,parentElement:{hidden:false},getAttribute:()=>h}));
 const termListeners={},attributes={}; let explanation;
 const term={title:'A durable correctness rule',textContent:'Invariant',setAttribute:(k,v)=>attributes[k]=v,after:x=>explanation=x,addEventListener:(k,v)=>termListeners[k]=v};
 const context={document:{createElement:()=>({}),querySelector:()=>input,querySelectorAll:s=>s==='[data-study]'?[box]:s==='#navigation a'?links:s==='abbr[title]'?[term]:[]},localStorage:{getItem:k=>stored[k],setItem:(k,v)=>stored[k]=v},fetch:async()=>({json:async()=>[{title:'Storage',url:'storage.html',text:'transaction invariant'},{title:'Chat',url:'chat.html',text:'connection'}]})};
 vm.runInNewContext(fs.readFileSync('app.js','utf8'),context);
 input.value='TRANSACTION'; await listeners.search();assert.equal(links[0].parentElement.hidden,false);assert.equal(links[1].parentElement.hidden,true);
 input.value='';await listeners.search();assert(links.every(x=>!x.parentElement.hidden));
 box.checked=true;listeners.change();assert.equal(stored['sdf-study:one'],'1');
 box.checked=false;listeners.change();assert.equal(stored['sdf-study:one'],'0');
 assert.equal(attributes['aria-controls'],explanation.id);assert.equal(explanation.hidden,true);
 termListeners.click();assert.equal(explanation.hidden,false);
 for(const key of ['Enter',' ']){termListeners.keydown({key,preventDefault(){}});}
 assert.equal(explanation.hidden,false);termListeners.keydown({key:'Escape'});assert.equal(explanation.hidden,true);
 console.log('PASS: definitions click/Enter/Space/Escape, aria-controls; full-text search, case folding, reset, independent study persistence');
})().catch(e=>{console.error(e);process.exit(1)});
