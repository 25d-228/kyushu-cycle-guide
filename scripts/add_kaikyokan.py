"""Integrate the independent Kaikyokan trial into the existing static navigator."""
from pathlib import Path
import json,re,sys
sys.path.insert(0,str(Path(__file__).parent))
import kaikyokan_data as K
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'index.html';source=p.read_text(encoding='utf-8')

def read_obj(name):
    start=source.index('const '+name+'=')+len('const '+name+'=')
    value,end=json.JSONDecoder().raw_decode(source[start:])
    return value,start,start+end

def write_obj(name,value):
    global source
    _,a,b=read_obj(name)
    source=source[:a]+json.dumps(value,ensure_ascii=False,separators=(',',':'))+source[b:]

D,_,_=read_obj('DATA');T,_,_=read_obj('TRAVEL');R,_,_=read_obj('REST')
original_trips={m:json.dumps(D[m],ensure_ascii=False,sort_keys=True) for m in ['small','main']}
D['places'].update(K.COORDS);D['kaikyo']=K.DAYS
T['places'].update(K.PLACES);T['aliases'].update(K.ALIASES)
T['hotels']=[h for h in T['hotels'] if h['id'] not in {h['id'] for h in K.HOTELS}]+K.HOTELS
T['overnight']['kaikyo']=K.OVERNIGHT
R['sources'].update(K.SOURCES);R['cities']['下関']=K.REST_CITY
v=R['cities']['下関']['variants']
if 'quiet' in v:v['slow']=v.pop('quiet')
R['cities']['下関']['checked']=K.CHECKED
for city in K.PLACES:T['places'][city]['checked']=K.CHECKED
for name,value in [('DATA',D),('TRAVEL',T),('REST',R)]:write_obj(name,value)
# Introduce the mode everywhere the application validates a trip identifier.
for old,new in [("['small','main']","['small','kaikyo','main']"),("['small','main','compare']","['small','kaikyo','main','compare']"),("['main','small','compare']","['main','small','kaikyo','compare']")]:source=source.replace(old,new)
source=source.replace("const colors={small:","const colors={kaikyo:'#287ea0',small:") if "const colors={kaikyo:" not in source else source
source=source.replace("dates:{small:'',main:''}","dates:{small:'',kaikyo:'',main:''}")
source=source.replace("last:{small:{day:1,index:0},main:{day:1,index:0}}","last:{small:{day:1,index:0},kaikyo:{day:1,index:0},main:{day:1,index:0}}")
source=source.replace("const shortTrip=m=>m==='small'?'試走':'本番';","const shortTrip=m=>tripShort(m);")
source=source.replace("function tripLabel(mode){return mode==='small'?'試走 4日間':'本番 14日間';}","function tripLabel(mode){return TRIP_META[mode]?.label||'旅行プラン';}")
source=source.replace("return TRAVEL.overnight[mode].find(","return (TRAVEL.overnight[mode]||[]).find(")
source=source.replace("(TRAVEL.places[explorer.place]?.mode==='small'?'small':'main')","(TRAVEL.places[explorer.place]?.mode||'main')")
source=source.replace("${mode==='small'?'試走':'本番'}・${order.length}エリア","${tripShort(mode)}・${order.length}エリア")
source=source.replace("${p.mode==='small'?'試走':'本番'}の休養日","${tripShort(p.mode)}の休養日")
source=source.replace("同じ宿に連泊。自転車で自転車に乗らずに休む日。","同じ宿に連泊し、自転車には乗らずに過ごします。")
source=source.replace("const tag=d.rest?'休養':d.ferry.length?'フェリー':","const tag=d.rest?'休養':d.transfers?.length?'輪行＋走行':d.ferry.length?'フェリー':")
source=source.replace("${mode==='small'?'試走':'本番'}の${day}日目","${mode==='small'?'試走A':mode==='kaikyo'?'試走B':'本番'}の${day}日目")
source=source.replace("${state.mode==='small'?'試走4日間':'本番14日間'}を表示しています","${state.mode==='small'?'試走A・4日間':state.mode==='kaikyo'?'試走B・5日間':'本番14日間'}を表示しています")
source=source.replace("'試走と本番を重ねて表示しています'","'3つの旅行プランを重ねて表示しています'")
# Correct the otherwise hard-coded two-itinerary accommodation count.
source=re.sub(r"\$\('staySectionSummary'\)\.textContent=[^;]+;", "$('staySectionSummary').textContent=TRAVEL.overnight[mode].length+'か所・'+TRAVEL.overnight[mode].reduce((n,x)=>n+x.days.length,0)+'泊';",source)
# The separate sources retain their original checked dates.
source=source.replace("${explorer.tab==='rest'?'休養プランの情報確認：2026/09/23':'観光・ホテル情報の確認：2026/09/22'}", "${mode==='kaikyo'?'試走Bの情報確認：2026/09/26':explorer.tab==='rest'?'休養プランの情報確認：2026/09/23':'観光・ホテル情報の確認：2026/09/22'}")
source=source.replace('休養プランの施設情報確認：2026年9月23日。','休養プランの施設情報確認：${p.checked||REST.checked}。')
# Rail and walking legs must never be described as cycling or a ferry ride.
source=source.replace("ferry=d.ferry.some(f=>f[0]===pair[0]&&f[1]===pair[1])","ferry=nonRide(d,pair[0],pair[1])")
source=source.replace("d.ferry.some(f=>f[0]===d.stops[i-1]&&f[1]===name)","nonRide(d,d.stops[i-1],name)")
source=source.replace("nonRide(d,d.stops[i-1],name)?icon('ship'):'›'","nonRide(d,d.stops[i-1],name)?esc(segmentText(d,d.stops[i-1],name)):'›'")
source=source.replace("d.ferry.length?'船の区間は点線':'順路で表示'","d.transfers?.length?'点線はJR・押し歩き':d.ferry.length?'船の区間は点線':'順路で表示'")
source=source.replace("return d.ferry.some(f=>f.includes(d.stops[index]))?", "if((d.transfers||[]).some(f=>f.includes(d.stops[index])))return 'JRの乗降地点 · 輪行袋を使用';if((d.walks||[]).some(f=>f.includes(d.stops[index])))return '人道トンネル · 自転車は押し歩き';return d.ferry.some(f=>f.includes(d.stops[index]))?")
source=source.replace('<button type="button" class="journey-btn" data-journey-start="small">試走をたどる${arrow()}</button>', '<button type="button" class="journey-btn" data-journey-start="small">試走Aをたどる${arrow()}</button><button type="button" class="journey-btn" data-journey-start="kaikyo">試走Bをたどる${arrow()}</button>')
# The static controls are inserted before listeners are attached by the original scripts.
if 'data-mode="kaikyo"' not in source:
    source=source.replace('<button class="trip-tab" data-mode="main"', '<button class="trip-tab" data-mode="kaikyo" role="tab" aria-selected="false" aria-controls="workspace"><span class="dot blue"></span>試走B・海響館 5日間</button><button class="trip-tab" data-mode="main"',1)
if 'data-schedule="kaikyo"' not in source:
    source=source.replace('<button data-schedule="main"','<button data-schedule="kaikyo">試走B・海響館 5日間</button><button data-schedule="main"',1)
if 'data-ex-mode="kaikyo"' not in source:
    source=source.replace('<button type="button" data-ex-mode="main"','<button type="button" data-ex-mode="kaikyo" aria-pressed="false">試走B・海響館 5日間</button><button type="button" data-ex-mode="main"',1)
# Clear labels at all three independent trip selectors, and in the page introduction.
source=source.replace('>試走 4日間</button>','>試走A・内陸 4日間</button>')
source=source.replace('>重ねて比較</button>','>3つを比較</button>')
source=source.replace('ふたつの周遊プラン','3つの周遊プラン').replace('ふたつの旅','3つの旅').replace('ふたつのルート','3つのルート').replace('2つの旅を表示中','3つの旅を表示中')
source=source.replace('まずは内陸を巡る旅で試走し、本番は九州をぐるっと一周。休養日も設けて、走る時間と休む時間の両方を楽しみましょう。','内陸を巡る試走A、海響館を訪ねる試走B、その先に九州一周。3つの独立した旅を、休養日も含めて計画しましょう。')
source=source.replace('試走3日目・本番5日目と10日目。','試走Aの3日目・試走Bの4日目・本番の5日目と10日目。')
source=source.replace('試走は走行3日＋休養1日。本番は走行12日＋休養2日です。両者は別々の旅行として想定し、連続18日間を勧めるものではありません。','試走Aは走行3日＋休養1日、試走Bは走行4日（最終日は短距離）＋休養1日。本番は走行12日＋休養2日です。3つは別々の旅行で、連続した日程ではありません。試走Bは往復のアプローチにJRでの輪行を使います。')
source=source.replace('施設情報は2026年9月22日に確認。','試走A・本番の宿情報は2026年9月22日、試走Bは9月26日に確認。')
source=source.replace('日田・熊本・宮崎は連泊を想定。','日田・下関・熊本・宮崎は連泊を想定。')
if '海響館の休養日</button>' not in source:
    source=source.replace('<div class="launch-actions">','<div class="launch-actions"><button type="button" data-place-open="下関" data-travel-mode="kaikyo" data-guide-tab="rest">海響館の休養日</button>',1)
# The catalog wraps the core renderers before travel and navigator wrappers capture them.
if 'src="assets/trip-catalog.js' not in source:
    pos=source.index('</script>',source.index('<script>'))+len('</script>')
    source=source[:pos]+'\n<script src="assets/trip-catalog.js?v=kaikyokan-20260926"></script>\n'+source[pos:]
source=re.sub(r'assets/guide-enhancements\.js(?:\?[^"\s]*)?', 'assets/guide-enhancements.js?v=kaikyokan-20260926',source)
p.write_text(source,encoding='utf-8')
# Keep both the editable settings source and its production bundle in sync.
for rel in ['assets/main-settings.js','assets/guide-enhancements.js']:
    path=ROOT/rel;s=path.read_text(encoding='utf-8')
    s=s.replace("['small','main'].filter", "['small','kaikyo','main'].filter")
    s=s.replace('例：日田、熊本、宮崎','例：日田、海響館、熊本')
    path.write_text(s,encoding='utf-8')
# Existing tests should keep checking every old route, plus the new one.
p=ROOT/'scripts/test_site.py';s=p.read_text()
s=s.replace(".count()==3", ".count()==4")
s=s.replace('small:DATA.small,main:DATA.main','small:DATA.small,kaikyo:DATA.kaikyo,main:DATA.main')
p.write_text(s)
# Preserve prior trip definitions exactly: no accidental itinerary changes.
updated,_,_=read_obj('DATA')
assert all(original_trips[m]==json.dumps(updated[m],ensure_ascii=False,sort_keys=True) for m in original_trips)
assert len(updated['kaikyo'])==5
(ROOT/'kaikyokan-build-report.json').write_text(json.dumps({'days':5,'restDay':4,'cyclingKm':[183,235],'railLegs':2,'walkingLegs':1,'oldItinerariesUnchanged':True},ensure_ascii=False,indent=2))
print('Integrated the third trip; prior itineraries and settings retained.',flush=True)
