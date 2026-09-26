"""Browser smoke tests for the navigator, photo galleries, and centered dialogs."""
import json, subprocess, time
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'assets/photos/manifest.json').read_text())
assert len(manifest['places'])>=90
assert all(len(v)>=2 for v in manifest['rest'].values())
for path in (ROOT/'assets/photos').glob('*.jpg'):
    with Image.open(path) as image:image.verify()
server=subprocess.Popen(['python','-m','http.server','8765','--bind','127.0.0.1'],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    time.sleep(1)
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=browser.new_page(viewport={'width':1440,'height':1000})
        errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
        page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
        page.wait_for_function('window.JourneyPhotos && window.JourneyNavigator && window.JourneyDialogSize')
        assert page.locator('.rest-city-card .journey-place-cover').count()==4
        for city in page.evaluate('Object.keys(DATA.places)'):
            page.evaluate('(city)=>openPlace(city, "main", "sights")',city)
            assert page.locator('#dialogBody .journey-gallery img').count()>0,city
            page.evaluate('closeDestination()')
        positions=page.evaluate('Object.entries({small:DATA.small,kaikyo:DATA.kaikyo,main:DATA.main}).flatMap(([mode,days])=>days.flatMap(d=>d.stops.map((place,index)=>({mode,day:d.day,index,place}))))')
        for pos in positions:
            result=page.evaluate('(p)=>{JourneyNavigator.select(p.mode,p.day,p.index);return JourneyNavigator.getState()}',pos)
            assert result['place']==pos['place'] and result['day']==pos['day'],pos
        page.evaluate('JourneyNavigator.select("main",4,DATA.main[3].stops.length-1);JourneyNavigator.next()')
        assert page.evaluate('JourneyNavigator.getState().day')==5
        page.evaluate('JourneyNavigator.next()')
        assert page.evaluate('JourneyNavigator.getState().day')==6
        for city in ['日田','熊本','宮崎']:
            page.evaluate('(city)=>openPlace(city,city==="日田"?"small":"main","rest")',city)
            page.locator('.journey-rest-gallery img').evaluate_all("images=>images.forEach(i=>i.loading='eager')")
            page.wait_for_function('Array.from(document.querySelectorAll(".journey-rest-gallery img")).every(i=>i.complete && i.naturalWidth>0)')
            page.screenshot(path=str(ROOT/('test-rest-'+city+'.png')))
            page.evaluate('closeDestination()')
        page.set_viewport_size({'width':390,'height':844})
        page.evaluate('openPlace("熊本","main","rest")')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
        assert page.evaluate('document.getElementById("destinationDialog").getBoundingClientRect().width <= innerWidth+1')
        page.screenshot(path=str(ROOT/'test-mobile.png'))
        page.evaluate('closeDestination()')
        dialog_layouts=[]
        for width,height in [(1440,1000),(1920,1080),(1024,768),(768,1024),(390,844),(320,568),(844,390)]:
            page.set_viewport_size({'width':width,'height':height})
            for city,mode in [('熊本','main'),('日田','small'),('宮崎','main')]:
                page.evaluate('([city,mode])=>openPlace(city,mode,"rest")',[city,mode])
                page.wait_for_timeout(100)
                metrics=page.evaluate('''()=>{
                    const dialog=document.getElementById('destinationDialog');
                    const body=document.getElementById('dialogBody');
                    const r=dialog.getBoundingClientRect();
                    return {x:r.x,y:r.y,width:r.width,height:r.height,
                        centerErrorX:Math.abs(r.x+r.width/2-innerWidth/2),
                        centerErrorY:Math.abs(r.y+r.height/2-innerHeight/2),
                        bodyHeight:body.clientHeight,bodyWidth:body.clientWidth,
                        scrollWidth:body.scrollWidth};
                }''')
                assert metrics['centerErrorX']<2 and metrics['centerErrorY']<2,(city,metrics)
                assert metrics['width']<=width+1 and metrics['height']<=height+1,metrics
                assert metrics['bodyHeight']>=90,metrics
                assert metrics['scrollWidth']<=metrics['bodyWidth']+1,metrics
                if width>=1200:assert abs(metrics['width']-width*.94)<2,metrics
                for tab in ['#sightTab','#hotelTab','#restTab']:
                    page.locator(tab).click()
                    assert page.locator('#destinationDialog').is_visible()
                page.evaluate('document.getElementById("dialogBody").scrollTop=200')
                assert page.evaluate('document.getElementById("dialogBody").scrollTop')>0
                page.locator('#closeDestination').click()
                assert not page.locator('#destinationDialog').is_visible()
                dialog_layouts.append({'viewport':[width,height],'city':city,**metrics})
        page.evaluate('openPlace("唐津","main","sights")')
        page.keyboard.press('Escape')
        assert not page.locator('#destinationDialog').is_visible()
        assert not errors,errors
        browser.close()
    report={'waypointsWithPhotos':len(manifest['places']),'navigationPositionsTested':len(positions),'restDayGalleries':{k:len(v) for k,v in manifest['rest'].items()},'pageErrors':errors,'mobileLayout':'passed','centeredDialogLayouts':dialog_layouts}
    (ROOT/'browser-test-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False),flush=True)
finally:
    server.terminate()
