"""Main-page settings, usability, and route regression tests, locally or on SITE_URL."""
import json, os, subprocess, time
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE=os.environ.get('SITE_URL','http://127.0.0.1:8767/')
server=None
if not os.environ.get('SITE_URL'):
    server=subprocess.Popen(['python','-m','http.server','8767','--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    time.sleep(1)
errors=[]
report={'url':BASE,'tests':[],'layouts':[]}

def wait(page): page.wait_for_timeout(180)
def settings(page):
    page.locator('#openSiteSettings').click()
    assert page.locator('#siteSettingsDialog').is_visible()
    assert page.evaluate('document.activeElement.id')=='uxSettingsTitle'
def change(page, width, height):
    page.locator('#uxWidth').fill(str(width));page.locator('#uxHeight').fill(str(height))
def save(page): page.locator('#uxSaveSettings').click();wait(page)
def close_place(page): page.locator('#closeDestination').click();wait(page)
def open_place(page,city='熊本',tab='rest'):
    page.evaluate('([c,t])=>openPlace(c,c==="日田"?"small":"main",t)',[city,tab]);wait(page)
def metrics(page,selector):
    return page.locator(selector).evaluate('e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,cx:Math.abs(r.x+r.width/2-innerWidth/2),cy:Math.abs(r.y+r.height/2-innerHeight/2),sw:e.scrollWidth,cw:e.clientWidth}}')
try:
    with sync_playwright() as p:
        browser=p.chromium.launch()
        context=browser.new_context(viewport={'width':1440,'height':1000})
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(BASE,wait_until='networkidle');page.wait_for_function('window.JourneySettings && window.JourneyNavigator')
        assert page.locator('#dialogSizeTools,#dialogResizeGrip').count()==0
        settings(page);initial=page.evaluate('JourneySettings.getState()');change(page,77,88)
        assert page.evaluate('JourneySettings.getState()')==initial,'draft applied before save'
        page.keyboard.press('Escape');assert page.evaluate('document.activeElement.id')=='openSiteSettings'
        settings(page);assert float(page.locator('#uxWidth').input_value())==initial['width']
        for _ in range(30):
            page.keyboard.press('Tab');assert page.evaluate('document.getElementById("siteSettingsDialog").contains(document.activeElement)')
        change(page,82,90);page.locator('#uxTextSize').select_option('large');page.locator('#uxReduceMotion').check();save(page)
        chosen=page.evaluate('JourneySettings.getState()');assert chosen['width']==82 and chosen['height']==90 and chosen['textSize']=='large' and chosen['reduceMotion']
        assert page.evaluate('document.documentElement.hasAttribute("data-ux-reduced")')
        page.reload(wait_until='networkidle');assert page.evaluate('JourneySettings.getState()')==chosen
        report['tests'].append('Settings open on main page; draft, cancel, save, focus containment, Escape, and reload persistence')
        page.locator('#uxPlaceSearch').fill('不存在の場所');page.locator('.ux-search button').click()
        assert page.locator('#uxPlaceSearch').get_attribute('aria-invalid')=='true';assert not page.locator('#destinationDialog').is_visible()
        page.locator('#uxPlaceSearch').fill('熊本');page.locator('.ux-search button').click();wait(page)
        assert page.locator('#destinationDialog').is_visible();assert page.locator('#dialogPlaceName').inner_text()=='熊本'
        m=metrics(page,'#destinationDialog');assert abs(m['w']-1440*.82)<2 and abs(m['h']-1000*.90)<2,m
        assert page.locator('#destinationDialog input[type=range],#dialogResizeGrip,#dialogSizeTools').count()==0
        before=page.evaluate('JourneyNavigator.getState()');page.locator('#sightTab').click();wait(page)
        page.locator('#dialogBody').evaluate('e=>e.scrollTop=350');page.locator('#hotelTab').click();wait(page)
        assert page.locator('#dialogBody .hotel-card').count()>0
        order=page.evaluate('()=>{const b=document.getElementById("dialogBody");return Array.from(b.children).findIndex(e=>e.classList.contains("hotel-card"))<Array.from(b.children).findIndex(e=>e.classList.contains("ux-location-photos"))}')
        assert order
        page.locator('#sightTab').click();wait(page);assert page.locator('#dialogBody').evaluate('e=>e.scrollTop')>300
        page.locator('#sightTab').focus();page.keyboard.press('ArrowRight');wait(page);assert page.locator('#hotelTab').get_attribute('aria-selected')=='true'
        assert page.evaluate('JourneyNavigator.getState()')==before
        close_place(page)
        assert page.evaluate('document.activeElement.id')=='uxPlaceSearch'
        report['tests'].append('Place search validation, no sizing controls in popups, hotel-first layout, tab reading position, arrow keys')
        names=page.evaluate('Object.keys(DATA.places)')
        for name in names:
            open_place(page,name,'sights');assert page.locator('#dialogBody .journey-gallery img').count()>0,name;page.evaluate('closeDestination()')
        positions=page.evaluate('Object.entries({small:DATA.small,main:DATA.main}).flatMap(([m,days])=>days.flatMap(d=>d.stops.map((place,index)=>({mode:m,day:d.day,index,place}))))')
        for pos in positions:
            current=page.evaluate('p=>{JourneyNavigator.select(p.mode,p.day,p.index);return JourneyNavigator.getState()}',pos)
            assert current['place']==pos['place'] and current['day']==pos['day']
        page.evaluate('JourneyNavigator.select("main",4,DATA.main[3].stops.length-1);JourneyNavigator.next()');assert page.evaluate('JourneyNavigator.getState().day')==5
        page.evaluate('JourneyNavigator.next()');assert page.evaluate('JourneyNavigator.getState().day')==6
        report.update(mappedPlaces=len(names),navigationPositions=len(positions));report['tests'].append('All map places, route positions, and arrival/rest/departure boundaries')
        page.evaluate('localStorage.setItem("orio-cycle-plan-v1",JSON.stringify({dates:{small:"2027-04-01",main:"2027-05-01"},checks:[1]}))')
        trip=page.evaluate('localStorage.getItem("orio-cycle-plan-v1")')
        settings(page);page.locator('#uxResetSettings').click();page.locator('#uxCancelSettings').click();assert page.evaluate('JourneySettings.getState()')==chosen
        settings(page);page.locator('#uxResetSettings').click();save(page);assert page.evaluate('localStorage.getItem("orio-cycle-plan-v1")')==trip
        report['tests'].append('Reset only display preferences; cancelling reset leaves settings unchanged')
        for width,height in [(1920,1080),(1440,1000),(1024,768),(768,1024),(390,844),(320,568),(844,390)]:
            page.set_viewport_size({'width':width,'height':height});wait(page);settings(page)
            m=metrics(page,'#siteSettingsDialog');assert m['cx']<2 and m['cy']<2 and m['sw']<=m['cw']+1,m
            assert page.locator('.ux-settings-body').evaluate('e=>e.scrollWidth<=e.clientWidth+1')
            assert page.locator('#uxSaveSettings').is_visible()
            if width in [1440,390]:page.screenshot(path=str(ROOT/f'settings-{width}.png'))
            change(page,45,50);save(page);open_place(page)
            m=metrics(page,'#destinationDialog');assert m['cx']<2 and m['cy']<2 and m['x']>=-1 and m['y']>=-1,m
            bm=page.locator('#dialogBody').evaluate('e=>({h:e.clientHeight,w:e.clientWidth,sw:e.scrollWidth})');assert bm['h']>=80 and bm['sw']<=bm['w']+1,(width,height,bm)
            assert page.locator('#dialogJourneyNav [data-journey-action=stop-next]').is_visible()
            close_place(page);settings(page);page.locator('[data-size-preset=full]').click();save(page);open_place(page)
            m=metrics(page,'#destinationDialog');assert abs(m['w']-width)<2 and abs(m['h']-height)<2,m
            page.locator('#sightTab').click();page.locator('#hotelTab').click();page.locator('#restTab').click();wait(page)
            if width in [1440,390]:page.screenshot(path=str(ROOT/f'settings-place-{width}.png'))
            close_place(page);report['layouts'].append({'viewport':[width,height],'passed':True})
        report['tests'].append('Settings, minimum popup sizes, fullscreen presets and tabs at seven viewport sizes')
        for city in ['日田','熊本','宮崎']:
            open_place(page,city)
            page.locator('.journey-rest-gallery img').evaluate_all("images=>images.forEach(i=>i.loading='eager')")
            page.wait_for_function('Array.from(document.querySelectorAll(".journey-rest-gallery img")).every(i=>i.complete&&i.naturalWidth>0)')
            page.get_by_role('button',name='時間割を見る',exact=True).click()
            assert page.locator('#dialogBody').evaluate('e=>e.scrollTop')>200
            assert page.evaluate('document.activeElement.classList.contains("rest-timeline-head")')
            close_place(page)
        report['tests'].append('Rest-day photo loading and direct jumps to the timetable')
        migration=browser.new_context()
        migration.add_init_script('localStorage.removeItem("orio-cycle-site-settings-v2");localStorage.setItem("orio-cycle-dialog-size-v1",JSON.stringify({width:79,height:87,maximized:false}))')
        mp=migration.new_page();mp.goto(BASE,wait_until='networkidle');assert mp.evaluate('JourneySettings.getState().width')==79;migration.close()
        blocked=browser.new_context()
        blocked.add_init_script('Object.defineProperty(window,"localStorage",{get(){throw new DOMException("Blocked","SecurityError")}})')
        bp=blocked.new_page();bp.on('pageerror',lambda e:errors.append(str(e)));bp.goto(BASE,wait_until='networkidle');settings(bp);change(bp,85,92);save(bp)
        assert bp.evaluate('JourneySettings.getState().width')==85
        assert '保存できない' in bp.locator('.ux-toast').inner_text();blocked.close()
        report['tests'].append('Previous size preferences migrate; storage-denied browsers show an honest fallback')
        assert not errors,errors
        report['pageErrors']=errors;report['status']='passed';browser.close()
    (ROOT/'settings-test-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False),flush=True)
finally:
    if server:server.terminate()
