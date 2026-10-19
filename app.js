const search = document.querySelector('#search');
let indexPromise;
search?.addEventListener('input', async () => {
 let index;
 try { indexPromise ??= fetch('search-index.json').then(response=>response.json()); index=await indexPromise; } catch { index=[]; }
 const query=search.value.trim().toLowerCase();
 document.querySelectorAll('#navigation a').forEach(a=>{
  const item=index.find(x=>x.url===a.getAttribute('href'));
  a.parentElement.hidden=!(item ? `${item.title} ${item.text}` : a.textContent).toLowerCase().includes(query);
 });
});
for(const box of document.querySelectorAll('[data-study]')){
 const key=`sdf-study:${box.dataset.study}`;
 try{box.checked=localStorage.getItem(key)==='1';}catch{}
 box.addEventListener('change',()=>{try{localStorage.setItem(key,box.checked?'1':'0');}catch{}});
}
// Definitions work with touch, mouse and keyboard; the full glossary is a no-JS fallback.
let definitionId=0;
for(const term of document.querySelectorAll('abbr[title]')){
 const definition=term.title;
 term.tabIndex=0;term.setAttribute('role','button');term.setAttribute('aria-expanded','false');
 term.setAttribute('aria-label',`${term.textContent}: show definition`);
 const explanation=document.createElement('span');explanation.className='definition';explanation.hidden=true;explanation.textContent=definition;
 explanation.id=`definition-${++definitionId}`;term.setAttribute('aria-controls',explanation.id);term.after(explanation);
 const toggle=()=>{explanation.hidden=!explanation.hidden;term.setAttribute('aria-expanded',String(!explanation.hidden));};
 term.addEventListener('click',toggle);
 term.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();toggle();}if(event.key==='Escape'){explanation.hidden=true;term.setAttribute('aria-expanded','false');}});
}
