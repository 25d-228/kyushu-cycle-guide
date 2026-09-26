"""End-to-end checks for the new trial, on a local server or the published site."""
from pathlib import Path
import os,json,time,subprocess,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('SITE_URL','http://127.0.0.1:8768/')
server=None;errors=[];report={'url':BASE,'tests':[]}
if not os.environ.get('SITE_URL'):
    server=subprocess.Popen(['python','-m','http.server','8768','--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
def close(page):
    if page.locator('#destinationDialog').is_visible():page.evaluate('closeDestination()')
def wait(page):page.wait_for_timeout(200)
try:
 with sync_playwright() as pw:
    browser=pw.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1000})
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(BASE,wait_until='networkidle');page.wait_for_function('window.JourneySettings&&window.JourneyNavigator&&typeof TRIP_META!=="undefined"')
    assert page.locator('[data-mode=kaikyo]').count()==1
    for mode,length in [('small',4),('kaikyo',5),('main',14)]:
        page.locator('[data-mode='+mode+']').click();wait(page)
        assert page.evaluate('JourneyNavigator.getState().mode')==mode
        assert page.locator('#itineraryRows tr').count()==length
        assert mode in page.evaluate('Object.keys(TRAVEL.overnight)')
    page.evaluate('setMode("compare")');wait(page)
    assert set(page.locator('#routeLayer [data-route-mode]').evaluate_all('nodes=>nodes.map(n=>n.dataset.routeMode)'))=={'small','kaikyo','main'}
    assert page.locator('#panelBody [data-open-mode]').count()==3
    report['tests'].append('Three independent trip selectors, comparison cards and route layers')
    page.evaluate('setMode("kaikyo")');wait(page)
    assert page.locator('#kaikyokanTripNotes').is_visible()
    assert '輪行' in page.locator('#kaikyokanTripNotes').inner_text()
    dates={'small':'2027-04-01','kaikyo':'2027-04-10','main':'2027-05-01'}
    for mode,date in dates.items():
        page.locator('[data-schedule='+mode+']').click();page.locator('#startDate').fill(date);page.locator('#startDate').dispatch_event('change')
    assert page.evaluate('state.dates')==dates
    page.reload(wait_until='networkidle');assert page.evaluate('state.dates')==dates
    page.evaluate('setMode("kaikyo")');wait(page)
    assert page.locator('#itineraryRows tr').count()==5
    assert '4泊' in page.locator('#staySectionSummary').inner_text()
    report['tests'].append('Each trip keeps a separate start date across reloads; new trip has four hotel nights')
    positions=page.evaluate('DATA.kaikyo.flatMap(d=>d.stops.map((place,index)=>({day:d.day,index,place})))')
    for pos in positions:
        state=page.evaluate('p=>{JourneyNavigator.select("kaikyo",p.day,p.index);return JourneyNavigator.getState()}',pos)
        assert state['mode']=='kaikyo' and state['place']==pos['place'] and state['index']==pos['index']
        page.evaluate('p=>openPlace(p.place,"kaikyo","sights")',pos)
        assert '試走B' in page.locator('#dialogTripLabel').inner_text()
        assert page.evaluate('JourneyNavigator.getState().index')==pos['index'],'repeat index preserved'
        images=page.locator('#dialogBody .journey-gallery img')
        assert images.count()>0,pos
        images.evaluate_all("items=>items.forEach(i=>i.loading='eager')")
        page.wait_for_function('Array.from(document.querySelectorAll("#dialogBody .journey-gallery img")).every(i=>i.complete&&i.naturalWidth>0)')
        close(page)
    page.evaluate('JourneyNavigator.select("kaikyo",3,DATA.kaikyo[2].stops.length-1);JourneyNavigator.next()')
    assert page.evaluate('JourneyNavigator.getState().day')==4
    assert page.evaluate('JourneyNavigator.getState().place')=='海響館'
    page.evaluate('JourneyNavigator.next()');assert page.evaluate('JourneyNavigator.getState().day')==5
    page.evaluate('JourneyNavigator.previous()');assert page.evaluate('JourneyNavigator.getState().day')==4
    assert page.locator('#routeLayer path[data-transport=rail]').count()==2
    assert page.locator('#routeLayer path[data-transport=walk]').count()==1
    assert page.evaluate('DATA.kaikyo[3].km')==[0,0]
    report['tests'].append('Every new waypoint opens correctly; arrival/rest/departure navigation preserves the rest day; rail and pushing are separate transport modes')
    page.evaluate('openPlace("海響館","kaikyo","rest")');wait(page)
    assert page.evaluate('explorer.place')=='下関'
    for variant in ['light','rain','slow']:
        page.locator('[data-rest-variant='+variant+']').click();wait(page)
        assert '海響館' in page.locator('#dialogBody').inner_text()
        assert '14:00' in page.locator('#dialogBody').inner_text()
    assert page.locator('.journey-rest-gallery img').count()>=3
    page.locator('[data-rest-variant=light]').click()
    page.locator('.journey-rest-gallery img').evaluate_all("items=>items.forEach(i=>i.loading='eager')")
    page.wait_for_function('Array.from(document.querySelectorAll(".journey-rest-gallery img")).every(i=>i.complete&&i.naturalWidth>0)')
    page.screenshot(path=str(ROOT/'kaikyokan-rest-desktop.png'))
    page.locator('#hotelTab').click();wait(page)
    assert '下関グランドホテル' in page.locator('#dialogBody').inner_text()
    assert '2連泊' in page.locator('#dialogBody').inner_text() or '2泊' in page.locator('#dialogBody').inner_text()
    assert page.locator('#dialogBody a[href*="jalan.net/yad339935"]').count()>0
    close(page)
    page.locator('#uxPlaceSearch').fill('海響館');page.locator('.ux-search button').click();wait(page)
    assert page.evaluate('JourneyNavigator.getState().mode')=='kaikyo';close(page)
    page.locator('#openSiteSettings').click();assert page.locator('#siteSettingsDialog').is_visible()
    page.locator('#uxWidth').fill('88');page.locator('#uxSaveSettings').click();wait(page)
    page.evaluate('openPlace("海響館","kaikyo","rest")');wait(page)
    assert abs(page.locator('#destinationDialog').bounding_box()['width']-1440*.88)<3
    assert page.locator('#dialogSizeTools,#dialogResizeGrip').count()==0
    close(page)
    report['tests'].append('Aquarium rest-day variants, 2-night Jalan hotel, search and main-page size settings remain usable')
    layouts=[]
    for w,h in [(1440,1000),(1024,768),(768,1024),(390,844),(320,568),(844,390)]:
        page.set_viewport_size({'width':w,'height':h});page.evaluate('setMode("kaikyo")');wait(page)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),[w,h]
        if w==1440:
            page.evaluate('document.getElementById("workspace").scrollIntoView()');page.screenshot(path=str(ROOT/'kaikyokan-map-desktop.png'))
        page.evaluate('openPlace("海響館","kaikyo","rest")');wait(page)
        metrics=page.locator('#destinationDialog').evaluate('e=>{const r=e.getBoundingClientRect();return {cx:Math.abs(r.x+r.width/2-innerWidth/2),cy:Math.abs(r.y+r.height/2-innerHeight/2),w:r.width,h:r.height}}')
        assert metrics['cx']<2 and metrics['cy']<2 and metrics['w']<=w+1 and metrics['h']<=h+1,metrics
        body=page.locator('#dialogBody').evaluate('e=>({h:e.clientHeight,w:e.clientWidth,sw:e.scrollWidth})')
        assert body['h']>=80 and body['sw']<=body['w']+1,(w,h,body)
        if w==390:page.screenshot(path=str(ROOT/'kaikyokan-rest-mobile.png'))
        close(page);layouts.append([w,h])
    assert not errors,errors
    report.update(status='passed',newNavigationPositions=len(positions),newRestDay=4,layouts=layouts,pageErrors=errors)
    browser.close()
 (ROOT/'kaikyokan-test-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False),flush=True)
finally:
 if server:server.terminate()
