/* Licensed destination photography and Japanese-language UI improvements. */
'use strict';
(() => {
  const photos = window.JOURNEY_PHOTOS;
  if (!photos) return;
  const css = document.createElement('style');
  css.textContent = `
  .journey-gallery{margin:0 0 22px}.journey-gallery h3{margin:0 0 6px;font-size:15px}.journey-gallery-note{font-size:11px;color:#657669;line-height:1.75;margin:0 0 12px}
  .journey-photo-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.journey-photo-grid.single{grid-template-columns:1fr}
  .journey-photo{margin:0;overflow:hidden;border:1px solid #e0e5da;border-radius:12px;background:#fffefa}.journey-photo img{width:100%;aspect-ratio:4/3;display:block;object-fit:cover;background:#eef1e9}.journey-photo figcaption{padding:10px 12px;font-size:10px;line-height:1.65}.journey-photo strong{font-size:12px;display:block;margin-bottom:4px}.journey-photo a{text-underline-offset:3px}.journey-photo-credit{display:block;color:#75816f;overflow-wrap:anywhere;font-size:9px}.journey-photo-note{color:#667466;display:block;margin-bottom:4px}
  .journey-place-cover{width:100%;aspect-ratio:16/9;object-fit:cover;display:block;border-radius:10px;margin:0 0 12px;background:#eef1e9}.journey-cover-caption{font-size:10px;color:#75816f;display:block;margin:-5px 0 10px}.journey-site-photo{margin:12px 0 16px}.journey-site-photo img{aspect-ratio:16/9}.journey-rest-gallery .journey-photo-grid>figure:first-child{grid-column:1/-1}.journey-rest-gallery .journey-photo-grid>figure:first-child img{aspect-ratio:16/8}.photo-date-note{font-size:10px;color:#74806d;line-height:1.7;margin:14px 0 0}
  @media(max-width:600px){.journey-photo-grid{gap:9px}.journey-photo figcaption{padding:9px}.journey-photo-credit{font-size:8px}.journey-photo strong{font-size:11px}.journey-gallery-note{font-size:10px}}
  @media print{.journey-gallery,.journey-site-photo,.journey-place-cover,.journey-cover-caption{display:none}}
  `;
  document.head.append(css);
  const clean = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const link = value => /^https:\/\//.test(value || '') ? clean(value) : '#';
  const cityPhotos = city => photos.places[city] || photos.places[canonical(city)] || [];
  function figure(p, extra='') {
    return `<figure class="journey-photo ${extra}"><a href="${link(p.source)}" target="_blank" rel="noopener noreferrer" aria-label="${clean(p.label)}の写真と出典"><img src="${clean(p.src)}" alt="${clean(p.label)}の写真" width="${p.width}" height="${p.height}" loading="lazy" decoding="async"></a><figcaption><strong>${clean(p.label)}</strong>${p.context ? `<span class="journey-photo-note">${clean(p.context)}</span>` : ''}<span class="journey-photo-credit">撮影・提供：${clean(p.author)} ／ <a href="${link(p.license_url || p.source)}" target="_blank" rel="noopener noreferrer">${clean(p.license)}</a> ／ <a href="${link(p.source)}" target="_blank" rel="noopener noreferrer">写真の出典</a><br>表示用に縮小・トリミングしています。</span></figcaption></figure>`;
  }
  function gallery(city, rest=false) {
    const items = rest ? (photos.rest[city] || cityPhotos(city)) : cityPhotos(city);
    if (!items.length) return '';
    const prefix = rest ? '休養日に訪れる場所を写真で見る' : `${clean(city)}の風景`;
    const note = rest ? '日田・熊本・宮崎の休養日は、自転車には乗らずに過ごします。写真は下のプランに登場する場所や、その周辺の風景です。外出先は体調や天候に合わせて選びましょう。' : '写真の撮影場所は各写真の見出しで確認できます。経由地の周辺を紹介する写真も含みます。';
    return `<section class="journey-gallery ${rest?'journey-rest-gallery':''}" aria-label="${clean(city)}の写真"><h3>${prefix}</h3><p class="journey-gallery-note">${note}</p><div class="journey-photo-grid ${items.length===1?'single':''}">${items.map(p=>figure(p)).join('')}</div><p class="photo-date-note">写真は撮影当時の様子です。現在の営業状況や工事の有無は、各施設の公式案内でご確認ください。</p></section>`;
  }
  for (const name of ['renderSights','renderHotels']) {
    if (name==='renderSights') { const original=renderSights; renderSights=function(){return gallery(explorer.requested)+original();}; }
    else { const original=renderHotels; renderHotels=function(){return gallery(explorer.requested)+original();}; }
  }
  const originalRest = renderRestPlan;
  renderRestPlan = function(){return gallery(explorer.place,true)+originalRest();};
  const originalSight = sightCard;
  sightCard = function(city,s,nearby=false) {
    const html=originalSight(city,s,nearby), p=photos.sights[s.id];
    return p ? html.replace('</h3>', '</h3>'+figure(p,'journey-site-photo')) : html;
  };
  function addCover(element,city) {
    if (!element || element.querySelector('.journey-place-cover')) return;
    const p=cityPhotos(city)[0]; if(!p) return;
    const image=document.createElement('img'); image.className='journey-place-cover';image.src=p.src;image.alt=p.label+'の写真';image.loading='lazy';image.decoding='async';image.width=p.width;image.height=p.height;
    const caption=document.createElement('span');caption.className='journey-cover-caption';caption.textContent=p.label+'（写真の出典は詳細画面に掲載）';
    element.prepend(caption);element.prepend(image);
  }
  const originalGuide=drawGuideOverview;
  drawGuideOverview=function(){originalGuide();document.querySelectorAll('#stayGrid [data-place-open]').forEach(el=>addCover(el,el.dataset.placeOpen));};
  const originalOverview=renderRestOverview;
  renderRestOverview=function(){originalOverview();document.querySelectorAll('.rest-city-card').forEach(el=>addCover(el,el.querySelector('[data-place-open]')?.dataset.placeOpen));};
  drawGuideOverview();renderRestOverview();
  if(document.getElementById('destinationDialog').open)renderDestination();
  window.JourneyPhotos=Object.freeze({version:photos.version,places:Object.keys(photos.places),rest:Object.keys(photos.rest)});
})();
