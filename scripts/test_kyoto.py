"""Functional regression tests for the independent Kyoto round trip, locally or live."""
from pathlib import Path
import json,os,subprocess,time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
server=None;url=os.environ.get('SITE_URL')
if not url:
 server=subprocess.Popen(['python','-m','http.server','8878','--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1);url='http://127.0.0.1:8878/'
errors=[];layouts=[]
try:
 with sync_playwright() as p:
  browser=p.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1000});page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(url,wait_until='networkidle');page.wait_for_function('window.KyotoJourney && window.JourneyNavigator && window.JourneyPhotos')
  assert set(page.locator('[data-mode]').evaluate_all('(a)=>a.map(x=>x.dataset.mode)'))=={'small','kaikyo','main','kyoto','compare'}
  page.locator('[data-mode="kyoto"]').click();assert page.locator('#itineraryRows tr').count()==28
  d=page.evaluate('DATA.kyoto');assert len(d)==28 and sum(x['rest'] for x in d)==6
  assert [x['day'] for x in d if x['rest']]==[6,10,13,14,20,25]
  assert not any(x.get('transfers') or x['ferry'] for x in d)
  assert sum(len(x['walks']) for x in d)==2
  assert d[0]['stops'][0]=='折尾' and d[-1]['stops'][-1]=='折尾'
  assert page.evaluate('DATA.geo.land.flat().some(p=>p[0]>135.8 && p[1]>35)')
  assert page.evaluate('TRAVEL.overnight.kyoto.reduce((n,x)=>n+x.days.length,0)')==27
  assert page.evaluate('TRAVEL.overnight.kyoto.find(x=>x.city==="京都").days')==[12,13,14]
  assert page.evaluate('TRAVEL.overnight.kyoto.filter(x=>x.city==="下関").map(x=>x.days)')==[[1],[27]]
  page.evaluate('()=>{state.dates={small:"2027-04-01",kaikyo:"2027-04-20",main:"2027-05-01",kyoto:"2027-10-01"};save()}')
  page.reload(wait_until='networkidle');assert page.evaluate('state.dates.kyoto')=='2027-10-01';assert page.evaluate('state.dates.main')=='2027-05-01'
  positions=0
  for day in d:
   for i,name in enumerate(day['stops']):
    result=page.evaluate('([n,i,name])=>{JourneyNavigator.select("kyoto",n,i);openPlace(name,"kyoto","sights");return {nav:JourneyNavigator.getState(),mode:explorer.mode}}',[day['day'],i,name])
    assert result['mode']=='kyoto' and result['nav']['day']==day['day'] and result['nav']['index']==i,(day,i,result)
    assert page.locator('#dialogBody .journey-gallery img').count()>0,name
    page.evaluate('closeDestination()');positions+=1
  page.evaluate('JourneyNavigator.select("kyoto",12,DATA.kyoto[11].stops.length-1);JourneyNavigator.next()');assert page.evaluate('JourneyNavigator.getState().day')==13
  page.evaluate('openPlace("京都","kyoto","rest")');assert '二条城' in page.locator('.rest-plan-header').inner_text()
  page.locator('[data-kyoto-rest-day="14"]').click();assert page.evaluate('JourneyNavigator.getState().day')==14;assert '鉄道博物館' in page.locator('.rest-plan-header').inner_text()
  assert '14日目' in page.locator('.rest-plan-header').inner_text();assert '13日目の予定' not in page.locator('#dialogJourneyNav').inner_text()
  page.locator('#hotelTab').click();assert '3連泊' in page.locator('.booking-conditions').inner_text()
  page.evaluate('closeDestination();JourneyNavigator.next()');assert page.evaluate('JourneyNavigator.getState().day')==15
  for n,i in [(1,len(d[0]['stops'])-1),(27,2)]:
   page.evaluate('([n,i])=>{JourneyNavigator.select("kyoto",n,i);openPlace("下関","kyoto","hotels")}',[n,i]);assert page.evaluate('explorer.mode')=='kyoto'
   assert str(n)+'日目の夜・1泊' in page.locator('.booking-conditions').inner_text();assert page.locator('#restTab').is_hidden();page.evaluate('closeDestination()')
  page.evaluate('JourneyNavigator.select("kyoto",21,DATA.kyoto[20].stops.length-1);openPlace("大田","kyoto","hotels")');assert 'まだ個別に選定していません' in page.locator('#dialogBody').inner_text();page.evaluate('closeDestination()')
  page.evaluate('setMode("compare")');assert page.locator('[data-open-mode="kyoto"]').count()==1
  assert page.locator('#routeLayer [data-route-mode="kyoto"]').count()==22
  for w,h in [(1920,1080),(1440,1000),(1024,768),(768,1024),(390,844),(320,568),(844,390)]:
   page.set_viewport_size({'width':w,'height':h});page.evaluate('JourneyNavigator.select("kyoto",14,0);openPlace("京都","kyoto","rest")');page.wait_for_timeout(100)
   m=page.evaluate('()=>{const r=destinationDialog.getBoundingClientRect(),b=document.getElementById("dialogBody");return {x:r.x,y:r.y,w:r.width,h:r.height,scroll:b.scrollWidth,client:b.clientWidth,body:b.clientHeight}}')
   assert abs(m['x']+m['w']/2-w/2)<2 and abs(m['y']+m['h']/2-h/2)<2,m
   assert m['w']<=w+1 and m['h']<=h+1 and m['scroll']<=m['client']+1,m
   assert page.locator('#destinationDialog #dialogSizeTools').count()==0
   assert page.locator('#destinationDialog #dialogResizeGrip').count()==0
   if w in (1440,390):
    page.locator('.journey-rest-gallery img').evaluate_all("a=>a.forEach(i=>i.loading='eager')")
    page.wait_for_function('Array.from(document.querySelectorAll(".journey-rest-gallery img")).every(i=>i.complete&&i.naturalWidth>0)')
    page.screenshot(path=str(ROOT/f'kyoto-rest-{w}.png'))
   layouts.append([w,h,m]);page.evaluate('closeDestination()')
  page.set_viewport_size({'width':1440,'height':1000});page.evaluate('setMode("kyoto")');page.wait_for_timeout(350);page.screenshot(path=str(ROOT/'kyoto-map.png'))
  # Actual pointer and keyboard controls must preserve the selected visit.
  page.evaluate('setMode("kyoto")')
  page.locator('#stayGrid [data-place-open="京都"]').click()
  assert '3連泊' in page.locator('.booking-conditions').inner_text()
  page.evaluate('closeDestination()')
  page.locator('#stayGrid [data-visit-day="27"][data-place-open="下関"]').click()
  assert '27日目の夜・1泊' in page.locator('.booking-conditions').inner_text()
  page.evaluate('closeDestination()')
  rest_link=page.locator('[data-table-day="14"] [data-guide-tab="rest"]')
  rest_link.focus();rest_link.press('Enter')
  assert page.evaluate('JourneyNavigator.getState().day')==14
  assert '京都鉄道博物館' in page.locator('.rest-plan-header').inner_text()
  page.evaluate('closeDestination()')
  page.locator('#kyotoTripNotes [data-place-open="京都"]').click()
  assert page.evaluate('explorer.mode')=='kyoto'
  page.evaluate('closeDestination()')
  page.locator('#fitMap').click();page.wait_for_timeout(450)
  page.locator('#map').screenshot(path=str(ROOT/'kyoto-overview-map.png'))
  assert not errors,errors;browser.close()
 report=dict(url=url,status='passed',navigationPositions=positions,days=28,restDays=6,kyotoNights=3,noRailOrFerry=True,walkingCrossings=2,distinctShimonosekiBookings=True,layouts=layouts,pageErrors=errors)
 (ROOT/'kyoto-test-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False),flush=True)
finally:
 if server:server.terminate()
