"""Fetch explicitly licensed location photos, resize locally, and extend the existing catalog."""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
import json,html,re,time,io,hashlib
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'assets/photos';P.mkdir(parents=True,exist_ok=True)
manifest=json.loads((P/'manifest.json').read_text())
UA={'User-Agent':'OrioCycleGuide/1.0 (https://github.com/25d-228/kyushu-cycle-guide; tourism planning)'}
added=[]
def get(url):
    err=None
    for n in range(3):
        try:
            with urlopen(Request(url,headers=UA),timeout=25) as r:return r.read()
        except Exception as e:err=e;time.sleep(n+1)
    raise err

def api(endpoint,**kw):return json.loads(get(endpoint+'?'+urlencode({'action':'query','format':'json','formatversion':2,**kw})))
def plain(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]+>','',str(s)))).strip()
def save_image(raw,key):
    dest=P/('kb-'+hashlib.sha256(key.encode()).hexdigest()[:16]+'.jpg')
    with Image.open(io.BytesIO(raw)) as im:
        im=ImageOps.exif_transpose(im).convert('RGB');im.thumbnail((1200,900));w,h=im.size
        im.save(dest,format='JPEG',quality=84,optimize=True)
    return str(dest.relative_to(ROOT)),w,h

def official(ident,label):
    url=f'https://yamaguchi-tourism.jp/photo/detail_{ident}.html'
    page=get(url).decode('utf-8')
    if '観光' not in page or '加工' not in page:raise RuntimeError('Photo terms not found: '+url)
    raw=get(f'https://yamaguchi-tourism.jp/lsc/api/photo/?src={ident}');path,w,h=save_image(raw,url)
    item=dict(src=path,label=label,article=label,author='山口県観光連盟・写真提供者',license='観光PR用の画像利用規約',license_url=url,source=url,width=w,height=h,original=str(ident),context='山口県の観光紹介として利用。写真は撮影当時の様子です。')
    added.append(item);return item

wiki_cache={}
def wiki(title,label=None):
    if title in wiki_cache:return dict(wiki_cache[title],label=label or title)
    pages=api('https://ja.wikipedia.org/w/api.php',prop='pageimages',piprop='name',pilimit=1,redirects=1,titles=title).get('query',{}).get('pages',[])
    names=[x.get('pageimage') for x in pages if x.get('pageimage')]
    if not names:raise RuntimeError('No lead photograph for '+title)
    name=names[0].replace('_',' ')
    if not re.search(r'\.(jpg|jpeg|png)$',name,re.I):raise RuntimeError('Not a photo: '+name)
    q=api('https://commons.wikimedia.org/w/api.php',prop='imageinfo',iiprop='url|size|extmetadata',iiurlwidth=1200,titles='File:'+name)
    items=[p.get('imageinfo',[{}])[0] for p in q.get('query',{}).get('pages',[])]
    if not items or not items[0].get('url'):raise RuntimeError('Missing Commons metadata: '+name)
    info=items[0];meta=info.get('extmetadata',{});license=plain(meta.get('LicenseShortName',{}).get('value',''))
    if not (license.startswith('CC BY') or license in ['CC0','Public domain']):raise RuntimeError('Review license '+license+' '+name)
    path,w,h=save_image(get(info.get('thumburl') or info['url']),info['descriptionurl'])
    result=dict(src=path,label=label or title,article=title,author=plain(meta.get('Artist',{}).get('value','出典ページを参照')),license=license,license_url=plain(meta.get('LicenseUrl',{}).get('value',info['descriptionurl'])).replace('http:','https:'),source=info['descriptionurl'],width=w,height=h,original=name)
    wiki_cache[title]=result;added.append(result);print('PHOTO',title,name,flush=True);return result

# Tourist-board photographs have explicit tourism-promotion reuse terms.
aquarium=official('1701036','海響館の外観')
dolphins=official('1700553','海響館のイルカショー（撮影当時）')
bridge=official('1400122','角島大橋')
tunnel=official('1700564','関門トンネル人道の内部')
beach=official('1700581','土井ヶ浜')
manifest['places']['海響館']=[aquarium]
manifest['places']['下関']=[aquarium]
manifest['places']['角島大橋']=[bridge]
manifest['places']['土井ヶ浜']=[beach]
manifest['places']['関門トンネル下関側']=[tunnel]
manifest['places']['関門トンネル門司側']=[dict(tunnel,context='両岸を結ぶ人道トンネル内部の写真です。門司側入口の外観ではありません。')]
places={
 '下関駅':['下関駅'],'吉見':['吉見駅'],'川棚温泉':['川棚温泉','川棚温泉駅'],
 '湯玉':['湯玉駅'],'角島灯台':['角島灯台'],'滝部':['滝部駅'],
 '豊田':['道の駅蛍街道西ノ市'],'菊川':['道の駅きくがわ'],
 '長府':['功山寺'],'赤間神宮':['赤間神宮'],'門司港':['門司港駅']}
missing=[]
for city,titles in places.items():
    errors=[]
    for title in titles:
        try:
            item=wiki(title)
            if city!=title:item['context']=city+'周辺の立ち寄り・移動の目印です。写真の場所は見出しで確認できます。'
            manifest['places'][city]=[item];break
        except Exception as e:errors.append(str(e))
    else:missing.append(city+': '+'; '.join(errors));print('MISSING',missing[-1],flush=True)
if missing:raise RuntimeError('\n'.join(missing))
karato=wiki('唐戸市場')
manifest['rest']['下関']=[aquarium,dolphins,karato]
manifest['sights'].update({'kb-aquarium':aquarium,'kb-karato':karato,'kb-kawatana':manifest['places']['川棚温泉'][0],'kb-bridge':bridge,'kb-lighthouse':manifest['places']['角島灯台'][0],'kb-tunnel':tunnel})
manifest['kaikyokanAdded']='2026-09-26'
(P/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(P/'data.js').write_text('window.JOURNEY_PHOTOS='+json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
credit=ROOT/'PHOTO-CREDITS.md'
old=credit.read_text(encoding='utf-8') if credit.exists() else '# Photo credits\n'
marker='\n## 試走B・海響館の追加写真'
if marker in old:old=old.split(marker)[0]
text=marker+'\n\n山口県観光連盟の写真は観光PR用の利用規約に基づいて掲載。Commons写真はそれぞれのライセンスに従い、表示用に縮小しています。\n\n'
unique={i['src']:i for i in added}
for i in unique.values():text+=f"- **{i['label']}** — {i['author']} — [{i['license']}]({i['license_url']}) — [出典]({i['source']}) — `{i['src']}`\n"
credit.write_text(old+text,encoding='utf-8')
report={'newPhotographs':len(unique),'newPlaces':len(places)+6,'restPhotos':len(manifest['rest']['下関']),'added':list(unique.values())}
(ROOT/'kaikyokan-photo-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('New trial photographs saved:',len(unique),flush=True)
