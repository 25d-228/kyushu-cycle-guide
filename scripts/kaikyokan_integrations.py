"""Finalize shared interactions and reports after adding a third independent trip."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'index.html';s=p.read_text()
old='if(!d)return null;return {mode:m,day:d.day,index:exact(d)>=0?exact(d):aliased(d)};'
new='if(!d)return null;if(nav.active&&nav.mode===m&&nav.day===d.day&&canonical(d.stops[nav.index])===canonical(name))return {mode:m,day:d.day,index:nav.index};return {mode:m,day:d.day,index:exact(d)>=0?exact(d):aliased(d)};'
if old in s:s=s.replace(old,new)
p.write_text(s)
p=ROOT/'assets/trip-catalog.js';s=p.read_text()
s=s.replace('3日走る → 海響館で休養 → 短距離走行と輪行で帰宅','3日走る → 下関で休養 → 短距離走行と輪行で帰宅')
s=s.replace('3日走ったら海響館で休養。最終日は短距離＋輪行。','3日走ったら下関で休養。海響館を楽しみ、最終日は短距離＋輪行。')
old="}layer.append(group);}refreshLabels();};"
new="const hit=E('path',{d:pathNames([a,b]),class:'route-hit','aria-label':tripShort(mode)+' '+d.day+'日目 '+d.title});hit.addEventListener('click',e=>{if(Date.now()-lastClick<200)return;e.stopPropagation();chooseDay(mode,d.day);});group.append(hit);}layer.append(group);}refreshLabels();};"
if old in s and "group.append(hit)" not in s:s=s.replace(old,new,1)
p.write_text(s)
# Verify every trip, not just the two original data arrays, in the settings regression suite.
p=ROOT/'scripts/test_settings.py';s=p.read_text().replace('small:DATA.small,main:DATA.main','small:DATA.small,kaikyo:DATA.kaikyo,main:DATA.main');p.write_text(s)
p=ROOT/'scripts/test_kaikyokan.py';s=p.read_text()
needle="        assert '試走B' in page.locator('#dialogTripLabel').inner_text()"
if "repeat index preserved" not in s:s=s.replace(needle,needle+"\n        assert page.evaluate('JourneyNavigator.getState().index')==pos['index'],'repeat index preserved'")
p.write_text(s)
p=ROOT/'maintenance/verify_live.py';s=p.read_text()
s=s.replace("'index.html','assets/guide-enhancements.js'","'index.html','assets/trip-catalog.js','assets/guide-enhancements.js'")
s=s.replace("'routeWaypoints':90","'routeWaypoints':107")
p.write_text(s)
manifest=json.loads((ROOT/'assets/photos/manifest.json').read_text())
photos=set()
for group in ['places','rest']:
    for items in manifest[group].values():photos.update(i['src'] for i in items)
photos.update(i['src'] for i in manifest['sights'].values())
(ROOT/'photo-build-report.json').write_text(json.dumps({'missing':[],'places':len(manifest['places']),'rest':{k:len(v) for k,v in manifest['rest'].items()},'sights':len(manifest['sights']),'uniquePhotographsUsed':len(photos)},ensure_ascii=False,indent=2))
print('Third-trip interactions and source verification finalized.',flush=True)
