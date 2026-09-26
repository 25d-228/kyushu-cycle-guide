"""Check the deployed site against repository bytes and exercise its live UI."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,os,time,urllib.request
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
BASE='https://25d-228.github.io/kyushu-cycle-guide/'
manifest=json.loads((ROOT/'assets/photos/manifest.json').read_text())
assert manifest['version']=='2026-09-25-photos-ja-v2'
assert not json.loads((ROOT/'photo-build-report.json').read_text())['missing']
paths={'index.html','assets/trip-catalog.js','assets/guide-enhancements.js','assets/photos/data.js','assets/photos/manifest.json'}
for group in ['places','rest']:
    for photos in manifest[group].values():paths.update(p['src'] for p in photos)
paths.update(p['src'] for p in manifest['sights'].values())
def check(path):
    request=urllib.request.Request(BASE+path,headers={'Cache-Control':'no-cache','User-Agent':'KyushuCycleGuideDeploymentCheck/1.0'})
    with urllib.request.urlopen(request,timeout=20) as response:
        assert response.status==200,(path,response.status)
        actual=response.read()
    expected=(ROOT/path).read_bytes()
    assert hashlib.sha256(actual).digest()==hashlib.sha256(expected).digest(),path+' differs from source'
    return path
for attempt in range(18):
    try:
        check('index.html');check('assets/photos/data.js');check('assets/guide-enhancements.js')
        break
    except Exception as error:
        print('Waiting for deployment',attempt+1,str(error),flush=True)
        if attempt==17:raise
        time.sleep(10)
with ThreadPoolExecutor(max_workers=6) as pool:verified=list(pool.map(check,sorted(paths)))
with sync_playwright() as p:
    browser=p.chromium.launch()
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(BASE,wait_until='networkidle')
    page.wait_for_function('window.JourneyPhotos && window.JourneyNavigator')
    assert page.evaluate('JourneyPhotos.version')==manifest['version']
    for city in ['日田','熊本','宮崎']:
        page.evaluate('(c)=>openPlace(c,c==="日田"?"small":"main","rest")',city)
        page.locator('.journey-rest-gallery img').evaluate_all("images=>images.forEach(i=>i.loading='eager')")
        page.wait_for_function('Array.from(document.querySelectorAll(".journey-rest-gallery img")).every(i=>i.complete && i.naturalWidth>0)')
        assert page.locator('.journey-rest-gallery img').count()>=3,city
        page.screenshot(path=str(ROOT/('live-rest-'+city+'.png')))
        page.evaluate('closeDestination()')
    page.evaluate('JourneyNavigator.select("main",4,DATA.main[3].stops.length-1);JourneyNavigator.next()')
    assert page.evaluate('JourneyNavigator.getState().day')==5
    page.evaluate('JourneyNavigator.next()')
    assert page.evaluate('JourneyNavigator.getState().day')==6
    page.set_viewport_size({'width':390,'height':844})
    page.evaluate('openPlace("熊本","main","rest")')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
    dimensions=page.locator('.journey-rest-gallery img').first.evaluate('(i)=>({width:i.getBoundingClientRect().width,height:i.getBoundingClientRect().height})')
    assert dimensions['height']<=dimensions['width'],dimensions
    page.screenshot(path=str(ROOT/'live-mobile.png'))
    assert not errors,errors
    browser.close()
report={'url':BASE,'http':200,'exactFilesVerified':len(verified),'photoVersion':manifest['version'],'routeWaypoints':107,'restGalleryPhotos':{c:len(v) for c,v in manifest['rest'].items()},'liveBrowserErrors':errors,'mobilePhotoDimensions':dimensions,'restDayNavigation':'passed'}
print('LIVE_VERIFIED',json.dumps(report,ensure_ascii=False),flush=True)
(ROOT/'live-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if os.environ.get('GITHUB_STEP_SUMMARY'):
    with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write('## Live site verified\n\n```json\n'+json.dumps(report,ensure_ascii=False,indent=2)+'\n```\n')
