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
s=s.replace('冷水峠|冷水峠\n','冷水峠|冷水峠|筑前山家駅\n')
s=s.replace("['豆田町','天領日田資料館','日田市']", "['豆田町','天領日田資料館','日田市','日田駅']")
s=s.replace('空中写真\'', '空中写真|Himeji|Hiroshige|Plattegrond|Kato-Kiyomasa|Blomhoff|Landsat|model|模型|裁断屑|JapanHomes|Miss Shanshan|aerial|空撮\'')
# Explicit photographs avoid unrelated image-navigation templates in encyclopedia pages.
overrides={
 '出島':['Dejima.jpg'],
 '天領日田資料館':['Hita Tenryo Museum 20161231.jpg'],
 '桜島':['View of Sakurajima from the ferry.jpg'],
 '鵜戸神宮':['Udo-jingu Shrine.jpg'],
 '宇土城':['Uto Castle (Kinsei), honmaru.jpg'],
 '延岡城':['Nobeoka castle ishigaki1.JPG'],
 '中津城':['Nakatsu Castle 20221023-2.jpg'],
 '旧伊藤伝右衛門邸':['Old Ito Den-emon Residence 4.JPG']
}
marker='def file_candidates(title):\n'
s=s.replace(marker, 'PHOTO_FILES='+repr(overrides)+'\n'+marker+'    if title in PHOTO_FILES:return PHOTO_FILES[title]\n',1)
# Thumbnail services may return a non-upload host. In that case, use the original
# public Wikimedia image and resize it locally rather than silently dropping it.
s=s.replace("if not author:continue", "if not author:\n            print('SKIP_NO_AUTHOR',name,str(meta)[:700],flush=True);continue")
s=s.replace("url=info.get('thumburl') or info.get('url','')\n        if not url.startswith('https://upload.wikimedia.org/'):continue", """urls=[info.get('thumburl',''),info.get('url','')]
        urls=['https:'+u if u.startswith('//') else u for u in urls]
        url=next((u for u in urls if u.startswith('https://upload.wikimedia.org/')),'')
        if not url:
            print('SKIP_URL',name,urls,flush=True);continue""")
s=s.replace("if min(image.size)<100:continue", "if min(image.size)<100:\n                    print('SKIP_DIMENSIONS',name,image.size,url,flush=True);continue")
s=s.replace("resolved={}; downloaded={}", "(OUT/'import-debug.json').write_text(json.dumps({'articles':articles,'infos':infos},ensure_ascii=False))\nresolved={}; downloaded={}")
p.write_text(s)
