/* Context-aware lodging and the two consecutive non-riding days in Kyoto. */
(()=>{
 'use strict';
 const priorHotels=renderHotels;
 renderHotels=function(){
  if(explorer.mode!=='kyoto')return priorHotels();
  const {city,n,d}=modalContext(),area=TRAVEL.kyotoJalan[city];
  let html=priorHotels();
  if(n&&!hotelsAt(city).length){html=`<div class="context-note jalan-note"><div><strong>${esc(city)}の宿は、まだ個別に選定していません。</strong><br>じゃらんの地域別検索を用意しています。料金・空室・自転車の保管条件は、リンク先や宿への問い合わせで確認してください。</div></div><div class="booking-conditions"><div><strong>${nightLabel(n)}</strong><small>${esc(nightsText(n,'kyoto',true))}</small><small>リンク先では宿泊日と人数を指定してください。</small></div><button type="button" class="copy-conditions" id="copyConditions">日程をコピー</button></div><div class="copy-feedback" id="copyFeedback"></div><div class="bike-check"><strong>予約前に自転車の保管条件を確認してください。</strong>屋内保管・施錠・輪行袋・洗濯設備・早朝出発の条件は宿によって異なります。休養地では日中の客室利用と清掃時間も確認してください。</div>`;}
  if(n&&area)html=`<div class="context-note"><div><strong>${esc(city)}の宿泊条件を比較</strong><br><a href="${esc(area.url)}" target="_blank" rel="noopener noreferrer">${esc(area.label)} ↗</a><br>県別ページの場合は、地図や地域名から${esc(city)}を選んでください。現在の空室や価格をこのページに自動取得する機能ではありません。</div></div>`+html;
  if(city==='下関')html='<div class="context-note"><div><strong>京都往復では、下関は往路と帰路に各1泊です。</strong><br>1日目と27日目は別々の宿泊。海響館の試走Bの連泊とは区別しています。</div></div>'+html;
  return html;
 };
 const originalRest=renderRestPlan;
 renderRestPlan=function(){const html=originalRest();if(explorer.mode!=='kyoto'||explorer.place!=='京都')return html;const day=restProfile('京都','kyoto').day;return `<div class="rest-inline-invite"><strong>京都は3連泊、休養は2日間。</strong><p>13日目と14日目の内容を切り替えられます。休館日に合わせて見学先を入れ替えても、午後の休息は残します。「街を楽しむ・雨の日・休息多め」の保存は京都の両日に共通です。</p><div class="rest-variant-switch" role="group" aria-label="京都の休養日を選ぶ"><button type="button" data-kyoto-rest-day="13" aria-pressed="${day===13}">13日目・二条城</button><button type="button" data-kyoto-rest-day="14" aria-pressed="${day===14}">14日目・鉄道博物館</button></div></div>`+html;};
 document.addEventListener('click',e=>{const b=e.target.closest?.('[data-kyoto-rest-day]');if(!b)return;e.preventDefault();const day=Number(b.dataset.kyotoRestDay);JourneyNavigator.select('kyoto',day,0);openPlace('京都','kyoto','rest');},true);
 const originalDestination=renderDestination;
 renderDestination=function(){originalDestination();if(explorer.mode!=='kyoto')return;
  if(explorer.place==='下関'){$('dialogDescription').textContent='京都往復の往路・帰路の宿泊地です。1日目と27日目は別々の1泊で、休養日は設定していません。関門海峡では人道トンネルを押し歩きで渡ります。';$('restTab').hidden=true;}
  $('dialogFooterNote').innerHTML='京都往復の掲載情報確認：2026/10/04。<br>走行経路・営業・料金・空室は出発前に再確認。保存は予約ではありません。';
  document.querySelectorAll('#dialogBody .source-checked').forEach(el=>el.textContent='京都往復の計画作成：2026年10月4日。各施設の営業日・料金・駐輪条件は公式案内で再確認してください。');
  if(explorer.place==='下関')document.querySelectorAll('#dialogBody .rest-inline-invite').forEach(el=>el.remove());
 };
 window.KyotoJourney=Object.freeze({version:'2026-10-04',days:28,restDays:[6,10,13,14,20,25]});
 renderPanel();renderSchedule();renderMapUI();drawGuideOverview();
})();
