"""Build a static, attributed photo guide; retain the existing route and hotel data."""
from __future__ import annotations
import hashlib, html, io, json, re, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
UA='KyushuCycleGuide/1.0 (https://github.com/25d-228/kyushu-cycle-guide; attributed travel photography)'
WP='https://ja.wikipedia.org/w/api.php'
COMMONS='https://commons.wikimedia.org/w/api.php'
OUT=ROOT/'assets/photos';OUT.mkdir(parents=True,exist_ok=True)

def get(url, binary=False):
    for attempt in range(4):
        try:
            request=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'*/*' if binary else 'application/json'})
            with urllib.request.urlopen(request,timeout=35) as response: value=response.read()
            return value if binary else json.loads(value)
        except Exception:
            if attempt==3: raise
            time.sleep(2+attempt*3)

def api(endpoint, **params):
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

def text(value): return html.unescape(re.sub('<[^>]+>','',value or '')).strip()

# Articles refer to the actual waypoint or explicitly named nearby landmarks.
# No photos from a different overnight city are used as a silent fallback.
CANDIDATES='''折尾|折尾駅
鞍手|鞍手町|鞍手駅
宮若|宮若市|竹原古墳
飯塚|旧伊藤伝右衛門邸|飯塚市
桂川|桂川駅 (福岡県)|桂川町 (福岡県)
冷水峠|冷水峠|筑前山家駅
筑前|大刀洗平和記念館|筑前町
甘木|甘木公園|甘木駅|朝倉市
秋月|秋月城|秋月
朝倉|朝倉市
田主丸|田主丸駅|田主丸町
うきは|吉井町 (福岡県)|うきは市
原鶴|原鶴温泉
日田|豆田町|日田市
大鶴|大鶴駅
宝珠山|宝珠山駅|東峰村
小石原|小石原村|東峰村|小石原焼
添田|添田公園|添田駅|添田町
田川|石炭記念公園|田川市
福智|金田駅|福智町
直方|直方駅|直方市
中間|遠賀川水源地ポンプ室|中間市
芦屋|芦屋町
岡垣|岡垣町|海老津駅
宗像|宗像大社
福津|宮地嶽神社|福津市
福岡|大濠公園
糸島|二見ヶ浦 (糸島市)|桜井二見ヶ浦|糸島市
二丈|筑前深江駅|二丈町
唐津|唐津城
伊万里|伊万里市
有田|有田町
佐世保|九十九島 (西海国立公園)|佐世保市
早岐|早岐駅
東彼杵|彼杵駅|東彼杵町
大村|大村公園|大村市
諫早|諫早公園|諫早市
長崎|出島
愛野|愛野駅 (長崎県)|愛野町
国見|多比良駅|国見町 (長崎県)
島原|島原城
島原港|島原港
熊本港|熊本港
熊本|熊本城
宇土|宇土城|宇土市
八代|八代城|八代市
芦北|佐敷城|芦北町
水俣|エコパーク水俣|水俣駅|水俣市
出水|出水麓|出水市
阿久根|阿久根駅|阿久根市
薩摩川内|川内駅 (鹿児島県)|薩摩川内市
串木野|串木野駅|いちき串木野市
伊集院|伊集院駅
鹿児島|天文館|鹿児島市
鹿児島港|鹿児島港
桜島港|桜島港
桜島南|桜島
有村|有村溶岩展望所|桜島
黒神|黒神埋没鳥居|黒神町
垂水|垂水市
鹿屋|鹿屋市
大崎|大崎町
志布志|志布志鉄道記念公園|志布志駅|志布志市
串間|串間駅|串間市
南郷|南郷駅|南郷町 (宮崎県)
日南|日南市
鵜戸|鵜戸神宮
青島|青島神社|青島 (宮崎県)
宮崎|宮崎神宮
高鍋|高鍋城|高鍋町
都農|都農神社|都農町
日向|美々津|日向市
延岡|延岡城|延岡市
北川|北川駅|北川町
宗太郎|宗太郎駅
直川|直川駅
佐伯|佐伯城|佐伯市
津久見|津久見駅|津久見市
臼杵|二王座歴史の道|臼杵市
大分|大分駅|大分市
別府|竹瓦温泉|別府市
日出|日出城|日出町
宇佐|宇佐神宮
中津|中津城
豊前|宇島駅|豊前市
行橋|行橋駅
苅田|苅田駅
小倉|小倉城
戸畑|若戸大橋|戸畑駅
黒崎|黒崎駅'''
places={row.split('|')[0]:row.split('|')[1:] for row in CANDIDATES.splitlines()}
rest={'日田':['豆田町','天領日田資料館','日田市','日田駅'],'熊本':['熊本城','桜の馬場 城彩苑','熊本市現代美術館'],'宮崎':['宮崎神宮','宮崎科学技術館','宮崎駅']}
sight_titles={'s01':['鞍手町歴史民俗博物館'],'s02':['竹原古墳'],'s03':['旧伊藤伝右衛門邸']}
source=(ROOT/'index.html').read_text()

def extract(name):
    start=source.index('const '+name+'=')+len(name)+7
    obj,length=json.JSONDecoder().raw_decode(source[start:]);return obj,start,start+length
DATA,_,_=extract('DATA');TRAVEL,_,_=extract('TRAVEL');REST,_,_=extract('REST')
for city,p in TRAVEL['places'].items():
    for s in p['sights']:
        name=re.split('[（(]',s['name'])[0]
        aliases={'秋月城跡・杉の馬場':['秋月城'],'筑後吉井白壁の町並み':['吉井町 (福岡県)'],'豆田町の町並み':['豆田町'],'九十九島パールシーリゾート':['九十九島パールシーリゾート'],'天文館の街歩き':['天文館'],'青島神社・弥生橋':['青島神社'],'延岡城跡・城山公園':['延岡城'],'エコパーク水俣・海のゾーン':['エコパーク水俣'],'桜島溶岩なぎさ公園足湯':['桜島溶岩なぎさ公園'],'筑前町立大刀洗平和記念館':['大刀洗平和記念館']}
        sight_titles[s['id']]=aliases.get(name,[name])
all_titles=list(dict.fromkeys(t for group in [*places.values(),*rest.values(),*sight_titles.values()] for t in group))
articles={}; normalized={}
for start in range(0,len(all_titles),20):
    q=api(WP,titles='|'.join(all_titles[start:start+20]),redirects=1,prop='pageimages|images',piprop='name',pilimit=50,imlimit=500)
    for mapping in q.get('normalized',[])+q.get('redirects',[]): normalized[mapping['from']]=mapping['to']
    for page in q.get('pages',[]):
        if 'missing' not in page: articles[page['title']]=page
    time.sleep(.2)

def article(title):
    seen=set()
    while title in normalized and title not in seen: seen.add(title);title=normalized[title]
    return articles.get(title)

def usable_name(name):
    return bool(re.search(r'\.jpe?g$',name,re.I)) and not re.search(r'flag|logo|map\b|locator|seal|symbol|emblem|portrait|painting|drawing|紋章|位置図|地図|路線図|空中写真|Himeji|Hiroshige|Plattegrond|Kato-Kiyomasa|Blomhoff|Landsat|model|模型|裁断屑|JapanHomes|Miss Shanshan|aerial|空撮',name,re.I)

PHOTO_FILES={'出島': ['Dejima.jpg'], '天領日田資料館': ['Hita Tenryo Museum 20161231.jpg'], '桜島': ['View of Sakurajima from the ferry.jpg'], '鵜戸神宮': ['Udo-jingu Shrine.jpg'], '宇土城': ['Uto Castle (Kinsei), honmaru.jpg'], '延岡城': ['Nobeoka castle ishigaki1.JPG'], '中津城': ['Nakatsu Castle 20221023-2.jpg'], '旧伊藤伝右衛門邸': ['Old Ito Den-emon Residence 4.JPG']}
def file_candidates(title):
    if title in PHOTO_FILES:return PHOTO_FILES[title]
    p=article(title)
    if not p:return []
    names=([p['pageimage']] if p.get('pageimage') else [])+[i['title'].removeprefix('File:').removeprefix('ファイル:') for i in p.get('images',[])]
    return list(dict.fromkeys(n.replace('_',' ') for n in names if usable_name(n)))[:3]

files=list(dict.fromkeys(n for t in all_titles for n in file_candidates(t)))
infos={}
for start in range(0,len(files),8):
    q=api(COMMONS,titles='|'.join('File:'+f for f in files[start:start+8]),prop='imageinfo',iiprop='url|size|extmetadata',iiurlwidth=640)
    for p in q.get('pages',[]):
        if p.get('imageinfo'):infos[p['title'].removeprefix('File:')]=p['imageinfo'][0]
    time.sleep(.15)

(OUT/'import-debug.json').write_text(json.dumps({'articles':articles,'infos':infos},ensure_ascii=False))
resolved={}; downloaded={}

def photo(title):
    if title in resolved:return resolved[title]
    resolved[title]=None
    for name in file_candidates(title):
        info=infos.get(name)
        if not info:continue
        meta=info.get('extmetadata',{})
        licence=text(meta.get('LicenseShortName',{}).get('value',''))
        if not re.search(r'CC BY|CC0|Public domain|PD-|PDM',licence,re.I):continue
        author=text(meta.get('Artist',{}).get('value',''))
        if not author:author=text(meta.get('Credit',{}).get('value',''))
        if not author:
            print('SKIP_NO_AUTHOR',name,str(meta)[:700],flush=True);continue
        urls=[info.get('thumburl',''),info.get('url','')]
        urls=['https:'+u if u.startswith('//') else u for u in urls]
        url=next((u for u in urls if u.startswith('https://upload.wikimedia.org/')),'')
        if not url:
            print('SKIP_URL',name,urls,flush=True);continue
        digest=hashlib.sha256(name.encode()).hexdigest()[:18]
        path=OUT/(digest+'.jpg')
        try:
            if name not in downloaded:
                image=ImageOps.exif_transpose(Image.open(io.BytesIO(get(url,binary=True)))).convert('RGB')
                if min(image.size)<100:
                    print('SKIP_DIMENSIONS',name,image.size,url,flush=True);continue
                image.thumbnail((960,720));image.save(path,quality=84,optimize=True)
                downloaded[name]=image.size
            width,height=downloaded[name]
            page=article(title)
            item={'src':'assets/photos/'+path.name,'label':page['title'] if page else title,'article':title,'author':author,'license':licence,'license_url':meta.get('LicenseUrl',{}).get('value',''),'source':info.get('descriptionurl',''),'width':width,'height':height,'original':name}
            resolved[title]=item;return item
        except Exception as exc:print('PHOTO_FAILED',title,name,str(exc),flush=True)
    return None

manifest={'version':'2026-09-25-photos-ja-v1','places':{},'rest':{},'sights':{}}
missing=[]
for city,titles in places.items():
    p=next((p for title in titles if (p:=photo(title))),None)
    if p:
        p=dict(p)
        if p['label'] not in [city,city+'市',city+'町',city+'駅']:p['context']=city+'の立ち寄り候補・周辺の風景です。'
        manifest['places'][city]=[p]
        print('PLACE',city,p['label'],p['original'],p['license'],flush=True)
    else:missing.append(city);print('MISSING',city,flush=True)
manifest['places']['朝倉・甘木']=manifest['places'].get('甘木',[])
manifest['places']['桜島']=manifest['places'].get('桜島港',[])
for city,titles in rest.items():
    items=[]
    for title in titles:
        p=photo(title)
        if p and p['src'] not in [x['src'] for x in items]:items.append(dict(p))
    manifest['rest'][city]=items
    print('REST',city,[(x['label'],x['original']) for x in items],flush=True)
for sid,titles in sight_titles.items():
    p=next((p for title in titles if (p:=photo(title))),None)
    if p:manifest['sights'][sid]=p
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(OUT/'data.js').write_text('window.JOURNEY_PHOTOS='+json.dumps(manifest,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')+';\n')
report={'missing':missing,'places':len(manifest['places']),'rest':{c:len(p) for c,p in manifest['rest'].items()},'sights':len(manifest['sights']),'files':len(downloaded)}
(ROOT/'photo-build-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('PHOTO_REPORT',json.dumps(report,ensure_ascii=False),flush=True)
if missing:raise RuntimeError('Photo coverage incomplete: '+', '.join(missing))
if any(len(v)<2 for v in manifest['rest'].values()):raise RuntimeError('Rest-day gallery requires at least two real photos per city')

# Rewrite editorial prose without modifying routes, distances, dates or reservations.
intros='''折尾|試走も本番も、出発と帰着は折尾です。出発前には、荷物や自転車の状態を確認する時間を取りましょう。
鞍手|試走の最初に通るエリアです。立ち寄りは控えめにして、荷物の固定や走り心地を確かめましょう。
宮若|試走1日目に通ります。観光を組み込む場合は、甘木までの道順と到着時刻を確認しておきましょう。
飯塚|試走1日目の立ち寄り候補です。見学に時間をかける場合は、ほかの寄り道を減らして調整しましょう。
筑前|冷水峠を越えて甘木へ向かう途中のエリアです。到着までの時間と体力に余裕があれば立ち寄りましょう。
甘木|試走1日目の宿泊地です。翌日の準備を済ませたら、近くを少し散歩して過ごしましょう。
秋月|試走2日目に、甘木から立ち寄る城下町です。散策の後は、うきは方面を経由して日田へ向かいます。
うきは|試走2日目に通ります。日田への到着が遅くならない範囲で、町並みの散策を楽しみましょう。
日田|試走2・3日目は同じ宿に泊まります。3日目は自転車に乗らず、町歩きと休息を組み合わせて過ごしましょう。
小石原|試走4日目に通る山間のエリアです。帰宅までの余力を残し、立ち寄りは短めにしましょう。
添田|試走4日目に通ります。このプランでは英彦山へは登らず、田川方面へ進みます。
田川|試走4日目の立ち寄り候補です。到着時刻に合わせて、屋外の散策か展示の見学を選びましょう。
直方|試走の終盤に通ります。折尾への帰着まで時間に余裕があれば、ひと休みを兼ねて立ち寄りましょう。
中間|折尾への帰着前に通ります。余裕があれば、史跡の外観を短時間見学する案です。
宗像|本番1日目に通ります。唐津までの距離が長いため、参拝する場合は時間を決めて立ち寄りましょう。
福岡|本番1日目に通ります。観光を詰め込まず、唐津への到着時刻を優先して進みましょう。
唐津|本番1日目の宿泊地です。長距離を走った後なので、疲れている場合はお城の外観を眺めるだけでも十分です。
佐世保|本番2日目の宿泊地です。九十九島方面への観光は、追加の移動時間を見込んで組み込みましょう。
長崎|本番3日目の宿泊地です。翌日は島原からフェリーに乗るため、夜は早めに休みましょう。
熊本|本番4・5日目は同じ宿に泊まります。5日目は丸一日の休養日です。体調に合わせて、観光する時間と休む時間を調整しましょう。
水俣|本番6日目の宿泊地です。翌日の鹿児島までの走行に備え、到着後はゆっくり休みましょう。
鹿児島|本番7日目の宿泊地です。翌日は桜島フェリーに乗り、大隅半島へ向かいます。
桜島港|本番8日目にフェリーで到着します。時間に余裕があれば、出発前に近くの足湯でひと休みする案です。
志布志|本番8日目の宿泊地です。翌日は日南海岸を経由して宮崎へ向かいます。ここでは駅周辺に泊まる想定です。
日南|本番9日目に通ります。鵜戸神宮への立ち寄りを候補にし、宮崎までの到着時間に合わせて調整しましょう。
青島|本番9日目の立ち寄り候補です。散策の後は、宮崎市中心部の宿へ向かいます。
宮崎|本番9・10日目は同じ宿に泊まります。10日目は自転車に乗らず、近場での観光や食事を楽しみながら休みましょう。
延岡|本番11日目の宿泊地です。翌日の県境越えに備えて、観光は短めにしましょう。
臼杵|本番12日目の宿泊地です。延岡から長距離を走るため、到着後は近場の散策にとどめる案です。
別府|本番13日目に通ります。宿泊は中津の予定なので、温泉に立ち寄る場合も出発時刻を決めておきましょう。
中津|本番13日目の宿泊地です。翌日は折尾へ帰るので、最後の夜も睡眠時間を十分に取りましょう。'''
for row in intros.splitlines():
    key,value=row.split('|',1);TRAVEL['places'][key]['intro']=value

pairs={
'地名・日ごとにたどる｜折尾から、ふたつの一周。':'地名と日程でたどる｜折尾発、ふたつの周遊プラン',
'折尾から、ふたつの一周。':'折尾から、ふたつの周遊プラン。',
'まずは内陸で試す。本番は九州をぐるっと。休む日も、旅の一部に。':'まずは内陸を巡る旅で試走し、本番は九州をぐるっと一周。休養日も設けて、走る時間と休む時間の両方を楽しみましょう。',
'小さい旅で装備と回復を試してから、<br>別のルートで本番へ。':'短い旅で装備や疲れの残り方を確かめてから、<br>別のルートで九州一周へ。',
'走る場所を、分けて楽しむ。':'試走と本番、それぞれの景色を楽しむ。',
'試走は内陸、本番は外周寄り。':'試走は内陸を、本番は海沿いを中心に。',
'前の地名':'前の地点','次の地名':'次の地点',
'走行は0km。':'自転車での移動はありません。',
'移動しない日':'自転車に乗らずに休む日',
'日田で連泊し、走行は0km。豆田町と昼食を楽しみ、午後は宿で休む案。':'日田で連泊し、自転車には乗らずに過ごします。午前は豆田町の散策と昼食を楽しみ、午後は宿で休む案です。',
'4・5日目の夜は同じ宿へ。走行は0km。熊本城と城彩苑、雨なら現代美術館などを選び、午後の休息も確保。悪天候予備日とは別枠です。':'4・5日目は同じ宿に泊まります。熊本城と城彩苑、雨の日は現代美術館などから行き先を選び、午後は宿で休みましょう。この休養日は悪天候に備える予備日とは別に設けています。',
'9・10日目の夜は同じ宿へ。走行は0km。宮崎神宮と昼食、雨なら科学館とプラネタリウムを候補にし、午後は宿で休む。日南・青島への往復はしません。':'9・10日目は同じ宿に泊まります。宮崎神宮の参拝や近場での昼食、雨の日は科学館やプラネタリウムを候補にし、午後は宿で休みましょう。休養日に日南や青島まで往復する予定は入れていません。',
'翌日の休養を残し、明るい時間の到着を目指します。':'翌日の休養日を予定どおり取れるよう、明るいうちの到着を目指します。',
'周辺参考として、':'周辺の参考情報として、',
'地点間の移動時間は別途確認。':'地点間の移動時間は別途ご確認ください。',
'この地点は通過地として設定。':'この地点は通過地点として設定しています。',
'時間は、現地滞在の計画目安。':'所要時間は、現地で過ごす時間の目安です。',
'施設の公称値ではありません。移動・待ち時間・食事は原則別。観光を足す場合は走行日の余白から確保します。':'施設が案内している所要時間ではありません。移動や待ち時間、食事の時間は原則として含みません。観光を追加する場合は、その日の走行予定と合わせて調整してください。',
'この地点自体の観光情報は未収録。':'この地点の観光情報はまだ掲載していません。',
'計画・候補の保存のみ。予約は別途必要。':'保存できるのは計画と候補です。宿泊予約は別途お手続きください。',
'午前〜昼の外出枠':'午前から昼にかけての外出時間',
'歩行の計画目安・館内含む':'歩く時間の目安（館内を含む）',
'昼食・カフェ・入館の仮予算':'昼食・カフェ・入館料の予算目安',
'時刻は仮案・外出はいつでも短縮':'時刻は目安です。外出は途中で切り上げても構いません。',
'午前・気分で外出':'午前は体調に合わせて外出',
'午後・宿で3時間':'午後は宿で3時間休む',
'町並みとランチ、午後はのんびり。':'午前は町歩きとランチ、午後は宿でのんびり。',
'お城と城下の味を、半日だけ。':'半日かけて、お城と城下町の食事を楽しむ。',
'同じ宿に2連泊':'同じ宿に2泊',
'宿で休息。予定を入れない':'宿でゆっくり休む',
'次の地名へ':'次の地点へ',
'LOCAL GUIDE / ORIO CYCLE JOURNEY':'立ち寄りガイド / ORIO CYCLE JOURNEY',
'TWO LOOPS, ONE STARTING POINT':'試走と本番、どちらも折尾発着',
'YOUR TWO JOURNEYS':'ふたつの自転車旅',
'概略ルート / オフライン対応':'概略ルート／写真の出典は各詳細画面に掲載',
}
# Apply longer phrases first to avoid partial replacements.
def rewrite(value):
    if isinstance(value,str):
        for old,new in sorted(pairs.items(),key=lambda x:-len(x[0])):value=value.replace(old,new)
        return value
    if isinstance(value,list):return [rewrite(x) for x in value]
    if isinstance(value,dict):return {k:rewrite(v) for k,v in value.items()}
    return value

common={
'ゆっくり朝食':'起床を急がず、まずは朝食を取りましょう。朝食が付いていない宿の場合は、近くのお店を利用する想定です。',
'宿で休息。予定を入れない':'昼寝や読書、音楽など、好きな過ごし方で休みましょう。連泊中に部屋を使える時間や清掃の予定は、あらかじめ宿へご確認ください。',
'入浴・洗濯・ひと休み':'入浴や洗濯を済ませて、ひと休みしましょう。大浴場や洗濯設備の有無、利用できる時間は宿ごとにご確認ください。',
'宿の近くで夕食':'宿の近くで夕食を取りましょう。混雑している場合は持ち帰りなどに切り替え、遠くまで出かけずに済むようにします。',
'明日の準備を済ませる':'補給食、充電、着替え、翌日の天気を確認します。必要な買い物は近場で済ませ、自転車には乗らずに過ごしましょう。',
'早めに就寝':'生活リズムに合わせて、早めに休みましょう。翌朝の出発に慌てないよう、睡眠時間を十分に取る計画です。',
}
for city,p in REST['cities'].items():
    for v in p['variants'].values():
        for step in v['steps']:
            if step['title'] in common:step['detail']=common[step['title']]
for name,obj in [('DATA',DATA),('TRAVEL',TRAVEL),('REST',REST)]:
    _,start,end=extract(name);source=source[:start]+json.dumps(rewrite(obj),ensure_ascii=False,separators=(',',':'))+source[end:]
for old,new in sorted(pairs.items(),key=lambda x:-len(x[0])):source=source.replace(old,new)
source=re.sub(r'(?<!宿)泊地','宿泊地',source)
source=re.sub(r'\n?<!-- photo-guide-assets -->.*?<!-- /photo-guide-assets -->','',source,flags=re.S)
assets='\n<!-- photo-guide-assets -->\n<script src="assets/photos/data.js"></script>\n<script src="assets/guide-enhancements.js"></script>\n<!-- /photo-guide-assets -->\n'
assert '</body>' in source
source=source.replace('</body>',assets+'</body>',1)
(ROOT/'index.html').write_text(source)
(ROOT/'.nojekyll').touch()
credits=['# 写真の出典','各写真は表示用に縮小しています。画面上では一部をトリミングして表示します。','']
for title,p in sorted(resolved.items()):
    if p:credits.append(f"- {p['label']} — {p['author']} — {p['license']} — {p['source']}")
(ROOT/'PHOTO-CREDITS.md').write_text('\n'.join(credits)+'\n')
print('PREPARED',hashlib.sha256(source.encode()).hexdigest(),flush=True)
