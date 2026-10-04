"""Finalize shared pointer navigation and check the fourth trip through real controls."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'index.html';s=p.read_text()
s=s.replace("const row=guide.closest('[data-table-day],.day-row');nav.pendingDay=el?.dataset.visitDay?Number(el.dataset.visitDay)","const row=guide.closest('[data-table-day],.day-row');nav.pendingDay=guide?.dataset.visitDay?Number(guide.dataset.visitDay)")
button='<button type="button" class="journey-btn" data-journey-start="kyoto">京都往復をたどる${arrow()}</button>'
if 'data-journey-start="kyoto"' not in s:s=s.replace('<button type="button" class="journey-btn" data-journey-start="main">本番をたどる${arrow()}</button>','<button type="button" class="journey-btn" data-journey-start="main">本番をたどる${arrow()}</button>'+button,1)
s=s.replace('Changes: cropped to Kyushu,','Changes: extended and cropped to western Japan,')
p.write_text(s)
p=ROOT/'scripts/test_kyoto.py';s=p.read_text();marker="  assert not errors,errors;browser.close()"
if 'Actual pointer and keyboard controls' not in s:
 s=s.replace(marker,"""  # Actual pointer and keyboard controls must preserve the selected visit.
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
"""+marker,1)
p.write_text(s)
print('Ready for final pointer, keyboard and itinerary verification.')
