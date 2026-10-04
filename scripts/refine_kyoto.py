"""Targeted usability and photographic relevance fixes for the fourth itinerary."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'assets/kyoto-trip.js';s=p.read_text();marker='/* Four-trip controls stay inside narrow screens. */'
if marker not in s:
 s=s.replace(' .dot.kyoto{', ''' /* Four-trip controls stay inside narrow screens. */
 .small-switch{min-width:0;max-width:100%;flex-shrink:1;flex-wrap:wrap}
 @media(max-width:680px){.section-head{min-width:0}.small-switch{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));width:100%;box-sizing:border-box}.small-switch button{min-width:0;white-space:normal}.rhythm{max-width:100%;box-sizing:border-box}}
 .dot.kyoto{''',1)
p.write_text(s)
p=ROOT/'scripts/kyoto_data.py';s=p.read_text();line="PHOTO_TITLES['明石']=['明石城']\nREST_PHOTOS['松江']=['松江城','島根県立美術館']\n"
if "PHOTO_TITLES['明石']=" not in s:s=s.replace('TOTAL=[',line+'TOTAL=[',1)
p.write_text(s)
p=ROOT/'assets/kyoto-details.js';s=p.read_text().replace('架空の宿や未確認の料金は表示しません。','料金・空室・自転車の保管条件は、リンク先や宿への問い合わせで確認してください。');p.write_text(s)
