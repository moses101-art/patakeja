#!/usr/bin/env python3
"""Build public search pages. Uses only the existing anonymous, RLS-filtered RPC."""
import argparse, datetime, html, json, re, urllib.request, pathlib, uuid
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE='https://patakeja.top'
def esc(x): return html.escape(str(x if x is not None else ''),quote=True)
def slug(x): return re.sub('[^a-z0-9]+','-',x.lower()).strip('-')
def safeurl(x):
    return x if isinstance(x,str) and x.startswith('https://') else ''
def href(x): return '/houses/'+str(uuid.UUID(x['id']))+'.html'
def price(x): return 'KSh '+format(float(x['rent']),',.0f')+(' / night' if x['category'].startswith('Short stay') else ' / month')
def title(x): return x['category']+' in '+x['estate']+', '+x['town']
def card(x):
    photo=next((safeurl(u) for u in x.get('photos',[]) if safeurl(u)),None)
    return '<article class="card"><a href="'+href(x)+'">'+(('<img loading="lazy" width="640" height="420" src="'+esc(photo)+'" alt="'+esc(title(x))+'">') if photo else '')+'<div><strong>'+esc(price(x))+'</strong><h2>'+esc(title(x))+'</h2><p>'+esc(x['plot_name'])+'</p><span>View house →</span></div></a></article>'
def shell(path,name,desc,body,kind,identifier):
    schema={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'PataKeja','item':BASE+'/'},{'@type':'ListItem','position':2,'name':name,'item':BASE+path}]}
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(name)+' | PataKeja</title><meta name="description" content="'+esc(desc)+'"><link rel="canonical" href="'+BASE+path+'"><meta property="og:title" content="'+esc(name)+' | PataKeja"><meta property="og:description" content="'+esc(desc)+'"><meta property="og:url" content="'+BASE+path+'"><meta property="og:type" content="website"><link rel="stylesheet" href="/search-pages.css"><script type="application/ld+json">'+json.dumps(schema).replace('<','\\u003c')+'</script></head><body data-kind="'+kind+'" data-key="'+esc(identifier)+'"><header><a class="brand" href="/">⌂ PataKeja</a><nav><a href="/">Search homes</a><a href="/towns/">Browse towns</a><a href="/?help=1">Support</a></nav></header><main><p><a href="/">Home</a> / <a href="/towns/">Towns</a></p><h1>'+esc(name)+'</h1><p id="freshness" role="status">Snapshot updated '+STAMP+'. Checking current availability…</p><section id="page-content">'+body+'</section><aside><h2>View first. Pay safely.</h2><p>Confirm availability and all charges with the advertiser. Visit the property before paying. PataKeja connects people; it does not reserve properties or collect rent. A listing or badge is not a guarantee of safety.</p><a href="/terms.html">Terms, safety and privacy</a></aside></main><footer><a href="/">PataKeja · Pata keja, bila stress</a></footer><script src="/config.js"></script><script src="/search-pages.js" defer></script></body></html>'
def detail(x):
    photos=''.join('<img width="800" height="520" loading="lazy" src="'+esc(safeurl(p))+'" alt="'+esc(title(x))+' — photo '+str(i+1)+'">' for i,p in enumerate(x.get('photos',[])) if safeurl(p))
    costs=x.get('pk_costs') or {}; costrows=''
    for key,label in [('service_monthly','Monthly service charge'),('water_monthly','Fixed monthly water charge'),('water_deposit','Water deposit'),('electricity_deposit','Electricity deposit'),('agent_fee','Agent fee'),('other_once','Other compulsory one-time charges')]:
        costrows+='<dt>'+label+'</dt><dd>'+('KSh '+format(costs[key],',.0f') if isinstance(costs.get(key),(int,float)) else 'Not disclosed')+'</dd>'
    return '<div class="gallery">'+photos+'</div><p class="price">'+esc(price(x))+'</p><h2>'+esc(x['plot_name'])+'</h2><p>'+esc(x.get('description') or 'Contact the advertiser for more property details.')+'</p><p>'+esc(x.get('landmark') or '')+'</p><p>'+esc(' · '.join(x.get('amenities',[])))+'</p><dl><dt>Deposit</dt><dd>'+('KSh '+format(x['deposit'],',.0f') if x.get('deposit') is not None else 'Not disclosed')+'</dd>'+costrows+'</dl><p>Variable usage charges may apply. Confirm the full move-in cost before agreeing.</p><p>'+esc(x.get('pk_area_info') or '')+'</p><a class="button" href="/?listing='+esc(x['id'])+'">Check availability, contact & request viewing</a><p><a href="/towns/'+slug(x['town'])+'.html">More listings in '+esc(x['town'])+'</a></p>'
def build(rows):
    global STAMP
    STAMP=datetime.datetime.now(datetime.timezone.utc).strftime('%d %b %Y, %H:%M UTC')
    # Validate before replacing any generated output. Do not publish private fields.
    for x in rows:
        uuid.UUID(x['id']);assert all(isinstance(x[k],str) and x[k] for k in ('town','estate','category','plot_name'));assert isinstance(x['rent'],(int,float))
    towns=sorted(set(x['town'] for x in rows)); out={}
    for x in rows:
        p=href(x);out[p]=shell(p,title(x),title(x)+' at '+price(x)+'. '+x['plot_name']+'. View photos, disclosed charges and contact options on PataKeja.',detail(x),'house',x['id'])
    for town in towns:
        homes=[x for x in rows if x['town']==town];name='Houses, rentals & short stays in '+town
        intro='<p>Browse '+str(len(homes))+' advertised properties in '+esc(town)+'. Compare rent periods, areas and disclosed charges. Availability can change; confirm with the advertiser before travelling.</p>'
        # Use only actual inventory facts, not invented neighbourhood or market claims.
        intro+='<p>Areas with listings: '+esc(', '.join(sorted(set(x['estate'] for x in homes))))+'.</p><div class="grid">'+''.join(map(card,homes))+'</div>'
        p='/towns/'+slug(town)+'.html';out[p]=shell(p,name,'Explore advertised rentals and short stays in '+town+', Kenya. Compare photos, prices and locations on PataKeja.',intro,'town',town)
    body='<p>Choose a town with listings in this snapshot. For all Kenyan towns, use the <a href="/">main house search</a>.</p><div class="grid">'+''.join('<article class="card"><a href="/towns/'+slug(t)+'.html"><div><h2>'+esc(t)+'</h2><p>'+str(sum(x['town']==t for x in rows))+' listings · Explore →</p></div></a></article>' for t in towns)+'</div>'
    out['/towns/index.html']=shell('/towns/','Find a property by town in Kenya','Browse PataKeja listings by Kenyan town, with links to individual property pages.',body,'directory','')
    for folder in ('houses','towns'):
        dest=ROOT/folder;dest.mkdir(exist_ok=True)
        for f in dest.glob('*.html'):
            if '/'+folder+'/'+f.name not in out: f.unlink()
    for p,v in out.items(): (ROOT/p.lstrip('/')).write_text(v)
    urls=[BASE+'/',BASE+'/terms.html']+[BASE+('/towns/' if p=='/towns/index.html' else p) for p in sorted(out)]
    (ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join('  <url><loc>'+esc(u)+'</loc></url>\n' for u in urls)+'</urlset>\n')
    print('Built',len(rows),'house pages,',len(towns),'town pages and directory;',len(urls),'sitemap URLs.')
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--snapshot');args=ap.parse_args()
    if args.snapshot: rows=json.loads(pathlib.Path(args.snapshot).read_text())
    else:
        cfg=(ROOT/'config.js').read_text();url=re.search(r'SUPABASE_URL\s*:\s*"([^"]+)"',cfg)[1];key=re.search(r'SUPABASE_ANON_KEY\s*:\s*"([^"]+)"',cfg)[1]
        assert url.startswith('https://') and 'PASTE' not in key, 'Use the working public config.js'
        # Never use service-role credentials for a public search build.
        import base64
        if key.startswith('eyJ'):
            claims=json.loads(base64.urlsafe_b64decode(key.split('.')[1]+'==='));assert claims.get('role')=='anon','Only the anonymous public key is permitted'
        req=urllib.request.Request(url.rstrip('/')+'/rest/v1/rpc/pk_homes',data=b'{}',headers={'apikey':key,'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=45) as response: rows=json.load(response)
    assert isinstance(rows,list), 'Unexpected public listing response; existing files retained'
    build(rows)
