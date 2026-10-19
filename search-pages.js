/* Live validation uses only public pk_homes; no private contacts are fetched. */
(async function(){
 'use strict';
 const box=document.getElementById('page-content'),status=document.getElementById('freshness');
 const cfg=window.PK_CONFIG,kind=document.body.dataset.kind,key=document.body.dataset.key;
 const builtIds=new Set(Array.from(box.querySelectorAll('a[href^="/houses/"]')).map(a=>a.getAttribute('href').split('/').pop().replace('.html','')));
 function e(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
 function url(v){return typeof v==='string'&&v.startsWith('https://')?v:''}
 function money(v){return 'KSh '+Number(v).toLocaleString('en-KE')}
 function card(x){return '<article class="card"><a href="'+(builtIds.has(x.id)?'/houses/'+encodeURIComponent(x.id)+'.html':'/?listing='+encodeURIComponent(x.id))+'">'+(url(x.photos?.[0])?'<img loading="lazy" src="'+e(x.photos[0])+'" alt="'+e(x.category+' in '+x.estate)+'">':'')+'<div><strong>'+money(x.rent)+(String(x.category).startsWith('Short stay')?' / night':' / month')+'</strong><h2>'+e(x.category+' in '+x.estate+', '+x.town)+'</h2><p>'+e(x.plot_name)+'</p><span>View house →</span></div></a></article>'}
 try{
  if(!cfg||cfg.SUPABASE_URL.includes('PASTE'))throw Error('Config');
  const r=await fetch(cfg.SUPABASE_URL+'/rest/v1/rpc/pk_homes',{method:'POST',headers:{apikey:cfg.SUPABASE_ANON_KEY,'Content-Type':'application/json'},body:'{}',signal:AbortSignal.timeout(20000)});
  if(!r.ok)throw Error('Unavailable');const rows=await r.json();if(!Array.isArray(rows))throw Error('Data');
  if(kind==='house'){
   const x=rows.find(x=>x.id===key);
   if(!x){box.innerHTML='<h2>This advert is no longer publicly available</h2><p>It may be taken, paused, expired or awaiting confirmation.</p><a class="button" href="/">Find other homes</a>';const m=document.createElement('meta');m.name='robots';m.content='noindex';document.head.appendChild(m);status.textContent='Availability checked just now.';return}
   const period=String(x.category).startsWith('Short stay')?' / night':' / month';
   const fields=[['service_monthly','Monthly service charge'],['water_monthly','Fixed monthly water charge'],['water_deposit','Water deposit'],['electricity_deposit','Electricity deposit'],['agent_fee','Agent fee'],['other_once','Other compulsory one-time charges']];
   const costs=x.pk_costs||{};
   const heading=x.category+' in '+x.estate+', '+x.town;
   document.querySelector('h1').textContent=heading;document.title=heading+' | PataKeja';
   box.innerHTML='<div class="gallery">'+(x.photos||[]).filter(url).map((p,i)=>'<img loading="lazy" src="'+e(p)+'" alt="'+e(heading+' — photo '+(i+1))+'">').join('')+'</div><p class="price">'+money(x.rent)+period+'</p><h2>'+e(x.plot_name)+'</h2><p>'+e(x.description||'Contact the advertiser for more details.')+'</p><p>'+e(x.landmark||'')+'</p><p>'+e((x.amenities||[]).join(' · '))+'</p><dl><dt>Deposit</dt><dd>'+(x.deposit==null?'Not disclosed':money(x.deposit))+'</dd>'+fields.map(([k,label])=>'<dt>'+label+'</dt><dd>'+(typeof costs[k]==='number'?money(costs[k]):'Not disclosed')+'</dd>').join('')+'</dl><p>Variable usage charges may apply. Confirm the full move-in cost before agreeing.</p><p>'+e(x.pk_area_info||'')+'</p><a class="button" href="/?listing='+encodeURIComponent(x.id)+'">View current details, contact & request viewing</a>';

   status.textContent='Advert is currently published. Confirm vacancy and current charges with the advertiser.';
   box.querySelectorAll('a.button').forEach(a=>a.textContent='View current details, contact & request viewing');
  } else if(kind==='town'){
   const list=rows.filter(x=>x.town===key),grid=box.querySelector('.grid');
   if(grid)grid.innerHTML=list.length?list.map(card).join(''):'<p>No current listings in this town. <a href="/">Search other towns</a>.</p>';
   status.textContent=list.length+' currently published listings. Details below are refreshed from PataKeja.';
   const intro=box.querySelector('p');if(intro)intro.textContent='Browse current properties in '+key+'. Compare rent periods, areas and disclosed charges. Confirm availability before travelling.';
  } else status.textContent='Use the main search for the latest listings across all towns.';
 }catch(ignore){status.textContent+=' Live availability could not be checked. Open the main search to confirm current details.';}
})();
