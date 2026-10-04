"""Add the Kyoto itinerary without changing the existing trip definitions."""
from pathlib import Path
import json,re,hashlib
import kyoto_data as K
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'index.html';source=p.read_text(encoding='utf-8')
def read(name):
 a=source.index('const '+name+'=')+len('const '+name+'=');v,n=json.JSONDecoder().raw_decode(source[a:]);return v,a,a+n
def write(name,v):
 global source
 _,a,b=read(name);source=source[:a]+json.dumps(v,ensure_ascii=False,separators=(',',':'))+source[b:]
D,_,_=read('DATA');T,_,_=read('TRAVEL');R,_,_=read('REST')
old={m:json.dumps(D[m],ensure_ascii=False,sort_keys=True) for m in ['small','kaikyo','main']}
D['places'].update(K.COORDS);D['kyoto']=K.DAYS
T['places'].update(K.PLACES);T['overnight']['kyoto']=K.OVERNIGHT;T['kyotoJalan']=K.JALAN
T['hotels']=[h for h in T['hotels'] if not h['id'].startswith('ky-h')]+K.HOTELS
R['sources'].update(K.SOURCES);R['cities'].update(K.REST_CITIES)
for name,obj in [('DATA',D),('TRAVEL',T),('REST',R)]:write(name,obj)
for a,b in [("['small','kaikyo','main']","['small','kaikyo','main','kyoto']"),("['small','kaikyo','main','compare']","['small','kaikyo','main','kyoto','compare']"),("['main','small','kaikyo','compare']","['main','small','kaikyo','kyoto','compare']")]:source=source.replace(a,b)
source=source.replace("const colors={kaikyo:","const colors={kyoto:'#78589a',kaikyo:")
source=source.replace("dates:{small:'',kaikyo:'',main:''}","dates:{small:'',kaikyo:'',main:'',kyoto:''}")
source=source.replace("last:{small:{day:1,index:0},kaikyo:{day:1,index:0},main:{day:1,index:0}}","last:{small:{day:1,index:0},kaikyo:{day:1,index:0},main:{day:1,index:0},kyoto:{day:1,index:0}}")
if 'data-mode="kyoto"' not in source:source=source.replace('<button class="trip-tab" data-mode="compare"','<button class="trip-tab" data-mode="kyoto" role="tab" aria-selected="false" aria-controls="workspace"><span class="dot kyoto"></span>京都往復 28日間</button><button class="trip-tab" data-mode="compare"',1)
if 'data-schedule="kyoto"' not in source:source=source.replace('<button data-schedule="main"','<button data-schedule="kyoto">京都往復 28日間</button><button data-schedule="main"',1)
if 'data-ex-mode="kyoto"' not in source:source=source.replace('<button type="button" data-ex-mode="main"','<button type="button" data-ex-mode="kyoto" aria-pressed="false">京都往復 28日間</button><button type="button" data-ex-mode="main"',1)
source=source.replace('3つを比較','4つを比較').replace('3つの周遊プラン','4つの周遊プラン').replace('3つの旅','4つの旅').replace('3つの独立した旅','4つの独立した旅')
source=source.replace('内陸を走る試走A、海響館へ行く試走B、その先に九州一周。','内陸を走る試走A、海響館へ行く試走B、九州一周、そして京都往復。')
source=source.replace('内陸を巡る試走A、海響館を訪ねる試走B、その先に九州一周。','内陸を巡る試走A、海響館を訪ねる試走B、九州一周、そして京都往復。')
source=source.replace("${mode==='small'?'試走A':mode==='kaikyo'?'試走B':'本番'}",'${tripShort(mode)}')
source=source.replace("${state.mode==='small'?'試走A・4日間':state.mode==='kaikyo'?'試走B・5日間':'本番14日間'}",'${TRIP_META[state.mode]?.label||state.mode}')
if 'src="assets/kyoto-trip.js' not in source:
 source=re.sub(r'(<script src="assets/trip-catalog.js[^>]+></script>)',r'\1\n<script src="assets/kyoto-trip.js?v=kyoto-20261004"></script>',source,count=1)
if 'src="assets/kyoto-details.js' not in source:source=source.replace('</body>','<script src="assets/kyoto-details.js?v=kyoto-20261004"></script>\n</body>')
source=re.sub(r'assets/guide-enhancements\.js(?:\?[^"\s]*)?','assets/guide-enhancements.js?v=kyoto-20261004',source)
source=re.sub(r'assets/trip-catalog\.js(?:\?[^"\s]*)?','assets/trip-catalog.js?v=kyoto-20261004',source)
a="function nightAt(city,mode){return (TRAVEL.overnight[mode]||[]).find(x=>x.city===city);}"
b="function nightAt(city,mode){const matches=(TRAVEL.overnight[mode]||[]).filter(x=>x.city===city),day=state.mode===mode?state.day:null;return matches.find(n=>day&&n.days.includes(day))||matches.find(n=>day&&n.days.at(-1)+1===day)||matches.find(n=>day&&n.days[0]>=day)||matches[0];}"
source=source.replace(a,b)
source=source.replace("`${n.days[0]}・${n.days.at(-1)}日目の夜・${n.days.length}連泊`","`${n.days[0]}${n.days.length>2?'〜':'・'}${n.days.at(-1)}日目の夜・${n.days.length}連泊`")
helper="""function restProfile(city,mode=explorer.mode,day=null){const p=REST.cities[city];if(!p||p.mode!==mode)return null;const chosen=day??(state.mode===mode?state.day:null);return p.secondDay&&chosen===p.secondDay.day?{...p,...p.secondDay}:p;}
"""
if 'function restProfile(' not in source:source=source.replace('function restDate(city)',helper+'function restDate(city)',1)
def patch_function(name,transform):
 global source
 m=re.search(r'function '+name+r'\(',source)
 if not m:raise RuntimeError('Missing function '+name)
 n=re.search(r'\nfunction ',source[m.end():]);end=m.end()+n.start() if n else len(source)
 source=source[:m.start()]+transform(source[m.start():end])+source[end:]
for name in ['openPlace','renderDestination','restClosureNotice','renderRestPlan','restPlanText']:
 patch_function(name,lambda s:s.replace('REST.cities[explorer.place]','restProfile(explorer.place,explorer.mode)').replace('REST.cities[city]','restProfile(city,explorer.mode)'))
source=source.replace("function restDate(city){const p=REST.cities[city];return fullDate(p.day,p.mode)||`${p.day}日目・日付未定`;}","function restDate(city){const base=REST.cities[city],p=restProfile(city,base.mode)||base;return fullDate(p.day,p.mode)||`${p.day}日目・日付未定`;}")
source=source.replace("const p=REST.cities[explorer.place];return (p?","const p=restProfile(explorer.place);return (p?")
source=source.replace("if(tab==='rest'&&REST.cities[canonical(name)]){const r=REST.cities[canonical(name)];m=r.mode;return {mode:m,day:r.day,index:0};}","if(tab==='rest'&&restProfile(canonical(name),m)){const r=restProfile(canonical(name),m,nav.pendingDay||((nav.active&&nav.mode===m)?nav.day:null));return {mode:m,day:r.day,index:0};}")
source=source.replace("REST.cities[explorer.place].day!==nav.day","restProfile(explorer.place,nav.mode)?.day!==nav.day").replace("${REST.cities[explorer.place].day}日目の予定","${restProfile(explorer.place,nav.mode)?.day}日目の予定")
source=source.replace("x.day===REST.cities[explorer.place].day","x.day===restProfile(explorer.place,explorer.mode)?.day")
source=source.replace("自転車0km・同じ宿に2泊", "自転車0km・同じ宿に${nightAt(city,p.mode)?.days.length||2}泊")
source=source.replace("${esc(restDate(city))} ／ 同じ宿に2泊","${p.days?p.days.map(n=>fullDate(n,p.mode)||n+'日目').join('・'):esc(restDate(city))} ／ 同じ宿に${p.days?3:2}泊")
source=source.replace("${p.day}日目の過ごし方を見る","${p.days?p.days.join('・'):p.day}日目の過ごし方を見る")
patch_function('renderRestPrint',lambda s:s.replace('Object.entries(REST.cities).map(([city,p])=>','Object.entries(REST.cities).flatMap(([city,p])=>(p.days||[p.day]).map(day=>[city,restProfile(city,p.mode,day)])).map(([city,p])=>').replace('${esc(restDate(city))}','${esc(fullDate(p.day,p.mode)||p.day+\'日目\')}'))
source=source.replace("p=REST.cities[d?.stay]","p=restProfile(d?.stay,state.schedule,day)")
source=source.replace("list.length+'軒のじゃらん掲載宿から候補を選ぶ'","list.length?list.length+'軒のじゃらん掲載宿から候補を選ぶ':'じゃらんで地域の宿を探す'")
source=source.replace("${mode==='kaikyo'?'試走Bの情報確認：2026/09/26':", "${mode==='kyoto'?'京都往復の情報確認：2026/10/04':mode==='kaikyo'?'試走Bの情報確認：2026/09/26':")
source=source.replace('data-place-open="${esc(n.city)}" data-travel-mode="${mode}"','data-visit-day="${n.days[0]}" data-place-open="${esc(n.city)}" data-travel-mode="${mode}"')
source=source.replace("nav.pendingDay=row?Number(row.dataset.tableDay||row.id.replace('dayRow','')):null;","nav.pendingDay=el?.dataset.visitDay?Number(el.dataset.visitDay):row?Number(row.dataset.tableDay||row.id.replace('dayRow','')):null;")
p.write_text(source,encoding='utf-8')
for rel in ['assets/trip-catalog.js','assets/main-settings.js','assets/guide-enhancements.js']:
 p=ROOT/rel;s=p.read_text()
 s=s.replace("['small','kaikyo','main']","['small','kaikyo','main','kyoto']").replace("['main','small','kaikyo']","['main','small','kaikyo','kyoto']")
 s=s.replace('3つの独立した旅','4つの独立した旅').replace('3つの別々の旅','4つの別々の旅').replace('3つの独立した旅行','4つの独立した旅行')
 s=s.replace("mode==='small'?smallColors[d.day]:colors[mode]","mode==='small'?smallColors[d.day]:mode==='kyoto'&&d.phase==='return'?'#2b7c83':colors[mode]")
 p.write_text(s)
p=ROOT/'assets/kyoto-trip.js';p.write_text(p.read_text().replace('寄り道し','寄り道'))
for rel in ['scripts/test_site.py','scripts/test_settings.py']:
 p=ROOT/rel;s=p.read_text().replace('small:DATA.small,kaikyo:DATA.kaikyo,main:DATA.main','small:DATA.small,kaikyo:DATA.kaikyo,main:DATA.main,kyoto:DATA.kyoto')
 if rel.endswith('test_site.py'):s=s.replace("page.locator('.rest-city-card .journey-place-cover').count()==4","page.locator('.rest-city-card .journey-place-cover').count()==page.evaluate('Object.keys(REST.cities).length')")
 p.write_text(s)
p=ROOT/'scripts/test_kaikyokan.py';s=p.read_text().replace("=={'small','kaikyo','main'}","=={'small','kaikyo','main','kyoto'}").replace("page.locator('#panelBody [data-open-mode]').count()==3","page.locator('#panelBody [data-open-mode]').count()==4").replace("'main':'2027-05-01'}","'main':'2027-05-01','kyoto':'2027-10-01'}")
p.write_text(s)
p=ROOT/'maintenance/verify_live.py';s=p.read_text().replace("'index.html','assets/trip-catalog.js'","'index.html','assets/kyoto-trip.js','assets/kyoto-details.js','assets/trip-catalog.js'").replace("'routeWaypoints':107","'routeWaypoints':len(manifest['places'])")
p.write_text(s)
D,_,_=read('DATA');assert all(old[m]==json.dumps(D[m],ensure_ascii=False,sort_keys=True) for m in old)
(ROOT/'kyoto-build-report.json').write_text(json.dumps(dict(days=28,ridingDays=22,restDays=[6,10,13,14,20,25],nights=27,cyclingKm=K.TOTAL,railLegs=0,ferryLegs=0,walkingLegs=2,oldItinerariesUnchanged=True),ensure_ascii=False,indent=2))
print('Kyoto itinerary integrated; existing trip definitions unchanged.')
