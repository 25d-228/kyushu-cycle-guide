"""Final editorial review of the already downloaded and tested photo guide."""
from pathlib import Path
import hashlib,html,io,json,re,urllib.parse,urllib.request
from PIL import Image,ImageOps
root=Path(__file__).resolve().parents[1];out=root/'assets/photos'
m=json.loads((out/'manifest.json').read_text())
headers={'User-Agent':'KyushuCycleGuide/1.0 (https://github.com/25d-228/kyushu-cycle-guide)'}
wanted={'熊本港':('Kumamoto-Port ferry terminal 1.jpg','熊本港フェリーターミナル'),'黒神':('Buried torii near Kurokami-Cho, Kagoshima.JPG','黒神埋没鳥居'),'宮崎科学技術館':('H-I-FullScaledModel-20090827.jpg','宮崎科学技術館の屋外ロケット展示')}
params={'action':'query','format':'json','formatversion':2,'prop':'imageinfo','iiprop':'url|size|extmetadata','iiurlwidth':640,'titles':'|'.join('File:'+v[0] for v in wanted.values())}
url='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode(params)
with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as response:data=json.load(response)
files={p['title'].removeprefix('File:'):p['imageinfo'][0] for p in data['query']['pages'] if p.get('imageinfo')}
def clean(value):return html.unescape(re.sub('<[^>]+>','',value or '')).strip()
for city,(name,label) in wanted.items():
    info=files[name];meta=info['extmetadata'];license=clean(meta.get('LicenseShortName',{}).get('value',''))
    assert re.search(r'CC BY|CC0|Public domain',license,re.I),(name,license)
    author=clean(meta.get('Artist',{}).get('value',''))
    assert author,name
    urls=[info.get('thumburl',''),info.get('url','')]
    source=next(u for u in urls if urllib.parse.urlparse(u).hostname in ['thumb.wikimedia.org','upload.wikimedia.org'])
    with urllib.request.urlopen(urllib.request.Request(source,headers=headers),timeout=30) as response:raw=response.read()
    image=ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert('RGB');image.thumbnail((960,720))
    filename=hashlib.sha256(name.encode()).hexdigest()[:18]+'.jpg';image.save(out/filename,quality=84,optimize=True)
    p={'src':'assets/photos/'+filename,'label':label,'article':city,'author':author,'license':license,'license_url':meta.get('LicenseUrl',{}).get('value','').replace('http://','https://'),'source':info['descriptionurl'],'width':image.width,'height':image.height,'original':name}
    if city=='宮崎科学技術館':m['rest']['宮崎'].insert(1,p)
    else:m['places'][city]=[p]
    print('CURATED',city,name,author,license,flush=True)
labels={'鞍手':'古月横穴','宮若':'脇田温泉','朝倉':'菱野の三連水車','うきは':'筑後吉井の白壁の町並み','小石原':'小石原焼伝統産業会館','岡垣':'三里松原海岸','伊万里':'大川内山','有田':'有田駅周辺','佐世保':'九十九島','芦北':'芦北海浜総合公園','水俣':'エコパーク水俣のバラ園','出水':'出水麓武家屋敷群','鹿児島港':'城山から望む鹿児島市街と桜島','桜島港':'桜島（フェリーからの眺め）','桜島南':'桜島（フェリーからの眺め）','垂水':'海潟と桜島','日南':'鵜戸神宮','高鍋':'高鍋大師','臼杵':'臼杵石仏','小倉':'小倉城庭園'}
for city,label in labels.items():m['places'][city][0]['label']=label
m['places']['冷水峠'][0]['context']='写真は峠周辺の筑前山家駅です。冷水峠そのものを写した写真ではありません。'
m['places']['鹿児島港'][0]['context']='鹿児島港周辺の景色を、城山から撮影した写真です。'
m['places']['臼杵'][0]['context']='市中心部から離れた観光候補です。この写真の場所への立ち寄りは、日程に自動では追加されません。'
m['rest']['日田']=[p for p in m['rest']['日田'] if p['article']!='日田市']
m['places']['桜島']=m['places']['桜島港']
def all_photos():
    return [p for group in ['places','rest'] for ps in m[group].values() for p in ps]+list(m['sights'].values())
for p in all_photos():p['license_url']=p.get('license_url','').replace('http://','https://')
m['version']='2026-09-25-photos-ja-v2'
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
(out/'data.js').write_text('window.JOURNEY_PHOTOS='+json.dumps(m,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n')
credits=['# 写真の出典','各写真は表示用に縮小し、画面上では一部をトリミングしています。写真ごとの利用許諾条件は以下の出典で確認できます。','']
seen=set()
for p in all_photos():
    if p['original'] in seen:continue
    seen.add(p['original']);credits.append(f"- {p['label']} — {p['author']} — {p['license']} — {p['source']}")
(root/'PHOTO-CREDITS.md').write_text('\n'.join(credits)+'\n')
(out/'import-debug.json').unlink(missing_ok=True)
report={'missing':[],'places':len(m['places']),'rest':{city:len(ps) for city,ps in m['rest'].items()},'sights':len(m['sights']),'uniquePhotographsUsed':len(seen)}
(root/'photo-build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
# Enable the current official Wikimedia thumbnail host for future rebuilds.
p=root/'scripts/prepare_site.py';s=p.read_text();s=s.replace("u.startswith('https://upload.wikimedia.org/')", "urllib.parse.urlparse(u).hostname in ['thumb.wikimedia.org','upload.wikimedia.org']")
p.write_text(s)
# The source and data are both local; no runtime Wikimedia API is required.
s=(root/'index.html').read_text();s=s.replace('写真: Wikipedia / Wikimedia Commons','写真の出典は各写真に掲載しています。');(root/'index.html').write_text(s)
print('FINALIZED',json.dumps(report,ensure_ascii=False),flush=True)
