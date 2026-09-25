"""One-time migration of the initial importer, safe to re-run."""
from pathlib import Path
p=Path('scripts/prepare_site.py');s=p.read_text()
start=s.index('def api(');end=s.index('\ndef text(',start)
s=s[:start]+'''def api(endpoint, **params):
    pages={}; result={}; continuation={}
    for batch in range(40):
        value=get(endpoint+'?'+urllib.parse.urlencode({'format':'json','formatversion':2,'action':'query',**params,**continuation}))
        if 'error' in value: raise RuntimeError(str(value['error']))
        q=value.get('query',{})
        for key in ['normalized','redirects']:
            result.setdefault(key,[]).extend(q.get(key,[]))
        for page in q.get('pages',[]):
            key=page.get('pageid',page['title'])
            old=pages.setdefault(key,{})
            for field,item in page.items():
                if field=='images':old.setdefault(field,[]).extend(item)
                else:old[field]=item
        # images is a list of page illustrations; imageinfo continuation is history,
        # which must not replace the current photo with an old file revision.
        if 'images' not in params.get('prop','').split('|') or not value.get('continue'):break
        continuation=value['continue']
    result['pages']=list(pages.values())
    return result
''' + s[end:]
s=s.replace("piprop='name',imlimit=8", "piprop='name',pilimit=50,imlimit=500")
s=s.replace("n for n in names if usable_name(n)", "n.replace('_',' ') for n in names if usable_name(n)")
s=s.replace("'泊地':'宿泊地',", '')
s=s.replace('伊万里|大川内山|伊万里市','伊万里|伊万里市')
s=s.replace('小石原|小石原焼|小石原村|東峰村','小石原|小石原村|東峰村|小石原焼')
s=s.replace("['豆田町','天領日田資料館','日田市']", "['豆田町','天領日田資料館','日田市','日田駅']")
old="else:missing.append(city);print('MISSING',city,flush=True)"
new="""else:
        missing.append(city)
        print('MISSING',city,[(t, file_candidates(t), [(n, bool(infos.get(n)), text(infos.get(n,{}).get('extmetadata',{}).get('LicenseShortName',{}).get('value',''))) for n in file_candidates(t)]) for t in titles],flush=True)"""
s=s.replace(old,new)
p.write_text(s)
