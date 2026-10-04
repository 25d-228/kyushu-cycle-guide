"""Extend the overview coastline and cache licensed real photographs for Kyoto travel."""
from pathlib import Path
import json,hashlib
import kyoto_data as K
ROOT=Path(__file__).resolve().parents[1]
# Reuse reviewed download and license-check functions, not the one-off importer.
base=ROOT/'scripts/kaikyokan_photos.py'
prefix=base.read_text().split('# Tourist-board photographs')[0].replace("'kb-'","'ky-'")
ns={'__file__':str(base)};exec(compile(prefix,str(base),'exec'),ns)
manifest=ns['manifest'];wiki=ns['wiki'];added=ns['added'];missing=[]
targets=dict(K.PHOTO_TITLES)
targets.update({'備前':['伊部駅'],'赤穂':['播州赤穂駅'],'豊岡':['豊岡駅 (兵庫県)'],'出雲':['出雲市駅'],'長門':['長門市駅']})
for city,titles in targets.items():
 if city in manifest['places'] and manifest.get('kyotoAdded'):continue
 errors=[]
 for title in titles:
  try:
   photo=wiki(title)
   if title!=city:photo=dict(photo,context=city+'の周辺紹介です。写真の具体的な場所は見出しで確認してください。')
   manifest['places'][city]=[photo];break
  except Exception as e:errors.append(str(e))
 else:missing.append(city+': '+'; '.join(errors))
for city,titles in K.REST_PHOTOS.items():
 items=[]
 for title in titles:
  try:
   p=wiki(title)
   if city=='京都' and title=='渡月橋':p=dict(p,context='嵐山の周辺紹介。二条城・鉄道博物館に追加する必須予定ではありません。')
   if not any(x['src']==p['src'] for x in items):items.append(p)
  except Exception as e:print('REST PHOTO unavailable',city,title,str(e),flush=True)
 if len(items)<(3 if city=='京都' else 2):missing.append(city+': not enough distinct rest photographs')
 manifest['rest'][city]=items
for city,title in {'岩国':'錦帯橋','広島':'広島平和記念公園','尾道':'尾道駅','倉敷':'倉敷美観地区','岡山':'後楽園','姫路':'姫路城','神戸':'メリケンパーク','京都':'二条城','福知山':'福知山城','鳥取':'鳥取砂丘','松江':'松江城','萩':'萩城下町'}.items():
 try:manifest['sights']['ky-'+city]=wiki(title)
 except Exception as e:print('No dedicated sightseeing photo',city,str(e),flush=True)
if len(manifest['rest'].get('京都',[]))>=2:manifest['sights']['ky-rail-museum']=manifest['rest']['京都'][1]
if missing:raise RuntimeError('\n'.join(missing))
manifest['kyotoAdded']=K.CHECKED
P=ROOT/'assets/photos'
(P/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(P/'data.js').write_text('window.JOURNEY_PHOTOS='+json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+';\n')
credit=ROOT/'PHOTO-CREDITS.md';s=credit.read_text();marker='\n## 京都往復の追加写真'
if marker in s:s=s.split(marker)[0]
unique={i['src']:i for city in K.PHOTO_TITLES for i in manifest['places'][city]}
for city in K.REST_PHOTOS:
 for i in manifest['rest'][city]:unique[i['src']]=i
for i in added:unique[i['src']]=i
s+=marker+'\n\n実際の撮影写真をライセンス確認後に保存しています。各写真は撮影当時の様子で、現在の営業・通行状況を示すものではありません。表示用の縮小・トリミングがあります。\n\n'
for i in unique.values():s+=f"- **{i['label']}** — {i['author']} — [{i['license']}]({i['license_url']}) — [出典]({i['source']}) — `{i['src']}`\n"
credit.write_text(s)
# Same GSHHG/Basemap coastline source as the original site, now including western Honshu.
from mpl_toolkits.basemap import Basemap
from shapely.geometry import Polygon
m=Basemap(projection='cyl',llcrnrlon=128.0,llcrnrlat=30.0,urcrnrlon=137.0,urcrnrlat=37.0,resolution='i')
land=[]
for poly in m.landpolygons:
 g=Polygon(poly.get_coords()).simplify(.002,preserve_topology=True)
 if g.area>.00015:land.append([[round(x,4),round(y,4)] for x,y in g.exterior.coords])
p=ROOT/'index.html';source=p.read_text();a=source.index('const DATA=')+len('const DATA=');data,n=json.JSONDecoder().raw_decode(source[a:]);data['geo']['land']=land;data['geo']['source']='GSHHG via Basemap (intermediate resolution); simplified overview of western Japan; not road routing'
source=source[:a]+json.dumps(data,ensure_ascii=False,separators=(',',':'))+source[a+n:];p.write_text(source)
allphotos=set()
for group in ['places','rest']:
 for items in manifest[group].values():allphotos.update(x['src'] for x in items)
allphotos.update(x['src'] for x in manifest['sights'].values())
(ROOT/'photo-build-report.json').write_text(json.dumps(dict(missing=[],places=len(manifest['places']),rest={k:len(v) for k,v in manifest['rest'].items()},sights=len(manifest['sights']),uniquePhotographsUsed=len(allphotos)),ensure_ascii=False,indent=2))
(ROOT/'kyoto-photo-report.json').write_text(json.dumps(dict(added=len(unique),photographs=list(unique.values()),rest={c:len(manifest['rest'][c]) for c in K.REST_PHOTOS},mapPolygons=len(land),mapBounds=[128,30,137,37]),ensure_ascii=False,indent=2))
print('Kyoto photos and western Japan coastline saved.',len(unique),len(land),flush=True)
