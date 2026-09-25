"""Exercise the actual size controls locally or on SITE_URL; no application state is mocked."""
import json, os, subprocess, time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
base = os.environ.get('SITE_URL', 'http://127.0.0.1:8766/')
server = None
if not os.environ.get('SITE_URL'):
    server = subprocess.Popen(['python', '-m', 'http.server', '8766', '--bind', '127.0.0.1'], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

METRICS = '''()=>{
 const d=document.getElementById('destinationDialog'),r=d.getBoundingClientRect(),b=document.getElementById('dialogBody');
 return {x:r.x,y:r.y,width:r.width,height:r.height,viewportWidth:innerWidth,viewportHeight:innerHeight,
 centerX:Math.abs(r.x+r.width/2-innerWidth/2),centerY:Math.abs(r.y+r.height/2-innerHeight/2),
 bodyHeight:b.clientHeight,bodyWidth:b.clientWidth,bodyScrollWidth:b.scrollWidth,
 count:document.querySelectorAll('#dialogSizeTools').length};
}'''

def metrics(page):
    page.wait_for_timeout(70)
    m = page.evaluate(METRICS)
    assert m['centerX'] < 2 and m['centerY'] < 2, m
    assert m['x'] >= -1 and m['y'] >= -1, m
    assert m['width'] <= m['viewportWidth']+1 and m['height'] <= m['viewportHeight']+1, m
    assert m['bodyHeight'] >= 70 and m['bodyScrollWidth'] <= m['bodyWidth']+1, m
    assert m['count'] == 1, m
    assert page.locator('#closeDestination').is_visible()
    return m

def open_place(page, city='熊本', tab='rest'):
    page.evaluate('([city,tab])=>openPlace(city,city==="日田"?"small":"main",tab)', [city,tab])

def expand(page):
    if page.locator('#dialogSizeControls').is_hidden():
        page.locator('#dialogSizeToggle').click()

def slider(page, selector, value):
    expand(page)
    page.locator(selector).evaluate('(input,value)=>{input.value=String(value);input.dispatchEvent(new Event("input",{bubbles:true}));input.dispatchEvent(new Event("change",{bubbles:true}));}', value)

report = {'url':base, 'tests':[], 'layouts':[]}
errors = []
try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={'width':1920,'height':1080})
        page = context.new_page()
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(base, wait_until='networkidle')
        page.wait_for_function('window.JourneyDialogSize && window.JourneyNavigator')
        open_place(page)
        original = metrics(page)
        assert original['width'] > 1700, original
        assert abs(original['width']-1920*.94)<2 and abs(original['height']-1080*.94)<2, original
        page.screenshot(path=str(ROOT/'resizable-desktop.png'))
        report['tests'].append('larger default without 1120px cap')
        slider(page, '#dialogWidthRange', 75)
        slider(page, '#dialogHeightRange', 80)
        custom = metrics(page)
        assert abs(custom['width']-1440)<2 and abs(custom['height']-864)<2, custom
        # Real keyboard interaction, not only programmatic range input.
        page.locator('#dialogWidthRange').focus()
        page.keyboard.press('ArrowRight')
        assert page.evaluate('JourneyDialogSize.getState().width') == 76
        slider(page, '#dialogWidthRange', 75)
        report['tests'].append('independent width and height controls and keyboard input')
        page.locator('#dialogSizeMax').click()
        full = metrics(page)
        assert full['width']==1920 and full['height']==1080, full
        assert page.locator('#dialogSizeMax').get_attribute('aria-pressed')=='true'
        page.locator('#dialogSizeMax').click()
        restored=metrics(page)
        assert restored['width']==custom['width'] and restored['height']==custom['height'], restored
        report['tests'].append('maximize and restore previous custom dimensions')
        grip=page.locator('#dialogResizeGrip').bounding_box()
        x,y=grip['x']+grip['width']/2,grip['y']+grip['height']/2
        page.mouse.move(x,y);page.mouse.down();page.mouse.move(x-60,y-40,steps=8);page.mouse.up()
        dragged=metrics(page)
        assert abs(dragged['width']-(custom['width']-120))<3, dragged
        assert abs(dragged['height']-(custom['height']-80))<3, dragged
        saved=page.evaluate('JourneyDialogSize.getState()')
        report['tests'].append('pointer drag adjusts both dimensions and keeps popup centered')
        # Keep the size through tabs, stop changes, close/reopen, and a full reload.
        for selector in ['#sightTab','#hotelTab','#restTab']:
            page.locator(selector).click()
            assert metrics(page)['width']==dragged['width']
        page.locator('#dialogJourneyNav [data-journey-action="stop-next"]').click()
        assert metrics(page)['width']==dragged['width']
        page.evaluate('closeDestination()');open_place(page,'日田')
        assert metrics(page)['width']==dragged['width']
        page.reload(wait_until='networkidle')
        page.wait_for_function('window.JourneyDialogSize')
        open_place(page)
        assert page.evaluate('JourneyDialogSize.getState()')==saved
        assert metrics(page)['width']==dragged['width']
        page.locator('#dialogSizeMax').click()
        page.reload(wait_until='networkidle');page.wait_for_function('window.JourneyDialogSize');open_place(page)
        assert metrics(page)['width']==1920
        page.locator('#dialogSizeMax').click()
        assert metrics(page)['width']==dragged['width']
        report['tests'].append('size persists through navigation, tabs, closing, and reload including maximize/restore')
        page.locator('#dialogSizeReset').click()
        assert page.evaluate('JourneyDialogSize.getState()')=={'width':94,'height':94,'maximized':False}
        assert metrics(page)['width']==original['width']
        report['tests'].append('reset restores larger default')
        for w,h in [(1920,1080),(1440,1000),(1024,768),(768,1024),(390,844),(320,568),(844,390)]:
            page.evaluate('closeDestination()')
            page.set_viewport_size({'width':w,'height':h});page.wait_for_timeout(100)
            open_place(page)
            default=metrics(page)
            page.locator('#dialogSizeMax').click();maximized=metrics(page)
            assert maximized['width']==w and maximized['height']==h, maximized
            page.locator('#dialogSizeMax').click()
            expand(page)
            assert metrics(page)['bodyHeight']>=70
            if w==390:page.screenshot(path=str(ROOT/'resizable-mobile.png'))
            report['layouts'].append({'viewport':[w,h],'default':default,'maximized':maximized})
        report['tests'].append('seven desktop tablet and mobile layouts, including landscape and expanded controls')
        page.locator('#dialogResizeGrip').focus();page.keyboard.press('Home')
        page.keyboard.press('End');assert page.evaluate('JourneyDialogSize.getState().maximized')
        page.keyboard.press('ArrowLeft');assert not page.evaluate('JourneyDialogSize.getState().maximized')
        page.keyboard.press('Escape');assert not page.locator('#destinationDialog').is_visible()
        report['tests'].append('resize handle keyboard shortcuts and Escape close')
        # Storage may be disabled in privacy modes; resizing must still work.
        fallback=browser.new_context(viewport={'width':1440,'height':1000})
        fallback.add_init_script('Object.defineProperty(window,"localStorage",{get(){throw new Error("Storage is disabled")}})')
        other=fallback.new_page();other.on('pageerror',lambda e:errors.append(str(e)))
        other.goto(base,wait_until='networkidle');other.wait_for_function('window.JourneyDialogSize');open_place(other)
        other.locator('#dialogSizeMax').click();assert metrics(other)['width']==1440
        report['tests'].append('works when browser storage is disabled')
        assert not errors,errors
        browser.close()
    report['pageErrors']=errors;report['status']='passed'
    print('DIALOG_SIZE_VERIFIED',json.dumps(report,ensure_ascii=False),flush=True)
    (ROOT/'dialog-size-test-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
finally:
    if server:server.terminate()
