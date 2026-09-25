/* Licensed destination photography and Japanese-language UI improvements. */
'use strict';
(() => {
  const photos = window.JOURNEY_PHOTOS;
  if (!photos) return;
  const css = document.createElement('style');
  css.textContent = `
  .journey-gallery{margin:0 0 22px}.journey-gallery h3{margin:0 0 6px;font-size:15px}.journey-gallery-note{font-size:11px;color:#657669;line-height:1.75;margin:0 0 12px}
  .journey-photo-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.journey-photo-grid.single{grid-template-columns:1fr}
  .journey-photo{margin:0;overflow:hidden;border:1px solid #e0e5da;border-radius:12px;background:#fffefa}.journey-photo img{width:100%;height:auto;aspect-ratio:4/3;display:block;object-fit:cover;background:#eef1e9}.journey-photo figcaption{padding:10px 12px;font-size:10px;line-height:1.65}.journey-photo strong{font-size:12px;display:block;margin-bottom:4px}.journey-photo a{text-underline-offset:3px}.journey-photo-credit{display:block;color:#75816f;overflow-wrap:anywhere;font-size:9px}.journey-photo-note{color:#667466;display:block;margin-bottom:4px}
  .journey-place-cover{width:100%;height:auto;aspect-ratio:16/9;object-fit:cover;display:block;border-radius:10px;margin:0 0 12px;background:#eef1e9}.journey-cover-caption{font-size:10px;color:#75816f;display:block;margin:-5px 0 10px}.journey-site-photo{margin:12px 0 16px}.journey-site-photo img{aspect-ratio:16/9}.journey-rest-gallery .journey-photo-grid>figure:first-child{grid-column:1/-1}.journey-rest-gallery .journey-photo-grid>figure:first-child img{aspect-ratio:16/8}.photo-date-note{font-size:10px;color:#74806d;line-height:1.7;margin:14px 0 0}
  @media(max-width:600px){.journey-photo-grid{gap:9px}.journey-photo figcaption{padding:9px}.journey-photo-credit{font-size:8px}.journey-photo strong{font-size:11px}.journey-gallery-note{font-size:10px}}
  @media print{.journey-gallery,.journey-site-photo,.journey-place-cover,.journey-cover-caption{display:none}}
/* Centered, spacious place details; the body scrolls while controls stay visible. */
@media screen {
  #destinationDialog.destination-dialog {
    position: fixed;
    inset: 0;
    width: min(1120px, calc(100vw - 64px));
    max-width: calc(100vw - 64px);
    height: calc(100vh - 56px);
    height: calc(100dvh - 56px);
    max-height: 1040px;
    margin: auto;
    border: 1px solid #e1e2d8;
    border-radius: 22px;
  }
  #destinationDialog .dialog-shell-head { padding: 20px 32px 16px; }
  #destinationDialog .dialog-title-row { padding-right: 44px; }
  #destinationDialog .dialog-title-row h2 { font-size: 30px; }
  #destinationDialog .dialog-close { width: 40px; height: 40px; top: 18px; right: 22px; }
  #destinationDialog .dialog-tabs,
  #destinationDialog .dialog-footer { padding-left: 32px; padding-right: 32px; }
  #destinationDialog .dialog-body {
    min-height: 0;
    padding: 24px 32px 32px;
    overflow: auto;
    overscroll-behavior: contain;
    scrollbar-gutter: stable;
  }
  #destinationDialog .journey-photo-grid.single img { max-height: 320px; aspect-ratio: 16 / 7; }
}
@media screen and (min-width: 960px) {
  #destinationDialog .journey-rest-gallery .journey-photo-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  #destinationDialog .journey-rest-gallery .journey-photo-grid > figure:first-child { grid-column: auto; }
  #destinationDialog .journey-rest-gallery .journey-photo-grid > figure:first-child img { aspect-ratio: 4 / 3; }
}
@media screen and (max-width: 760px) {
  #destinationDialog.destination-dialog {
    width: calc(100vw - 24px);
    max-width: calc(100vw - 24px);
    height: calc(100vh - 24px);
    height: calc(100dvh - 24px);
    max-height: calc(100dvh - 24px);
    margin: auto;
    border-radius: 18px;
  }
  #destinationDialog .dialog-shell-head { padding: 14px 18px 10px; }
  #destinationDialog .dialog-title-row h2 { font-size: 24px; }
  #destinationDialog .dialog-close { width: 36px; height: 36px; top: 12px; right: 12px; }
  #destinationDialog .dialog-tabs,
  #destinationDialog .dialog-footer { padding-left: 16px; padding-right: 16px; }
  #destinationDialog .dialog-body { padding: 18px 16px 24px; }
  #destinationDialog .journey-photo-grid.single img { max-height: 260px; aspect-ratio: 16 / 9; }
}
@media screen and (max-height: 650px) {
  #destinationDialog .dialog-shell-head { padding-top: 10px; padding-bottom: 8px; }
  #destinationDialog .dialog-description,
  #destinationDialog .dialog-pref { display: none; }
}
@media screen and (max-height: 500px) {
  #destinationDialog.destination-dialog {
    width: calc(100vw - 24px);
    max-width: calc(100vw - 24px);
    height: calc(100vh - 24px);
    height: calc(100dvh - 24px);
    max-height: calc(100dvh - 24px);
  }
  #destinationDialog .dialog-context { display: none; }
  #destinationDialog .dialog-title-row h2 { font-size: 22px; }
  #destinationDialog .dialog-shell-head { padding: 8px 18px; }
  #destinationDialog .dialog-close { width: 32px; height: 32px; top: 5px; right: 12px; }
  #destinationDialog .dialog-tabs button { padding-top: 8px; padding-bottom: 8px; }
  #destinationDialog .dialog-footer { padding-top: 7px; padding-bottom: 7px; }
  #destinationDialog .dialog-body { padding: 14px 20px; }
  #destinationDialog .journey-mini-map { display: none; }
  #destinationDialog .dialog-journey { padding-top: 8px; padding-bottom: 8px; }
  #destinationDialog .dialog-journey .journey-stop-row { margin-top: 6px; }
}

  `;
  document.head.append(css);
  const clean = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const link = value => /^https?:\/\//.test(value || '') ? clean(value.replace(/^http:/,'https:')) : '#';
  const cityPhotos = city => photos.places[city] || photos.places[canonical(city)] || [];
  function figure(p, extra='') {
    return `<figure class="journey-photo ${extra}"><a href="${link(p.source)}" target="_blank" rel="noopener noreferrer" aria-label="${clean(p.label)}の写真と出典"><img src="${clean(p.src)}" alt="${clean(p.label)}の写真" width="${p.width}" height="${p.height}" loading="lazy" decoding="async"></a><figcaption><strong>${clean(p.label)}</strong>${p.context ? `<span class="journey-photo-note">${clean(p.context)}</span>` : ''}<span class="journey-photo-credit">撮影・提供：${clean(p.author)} ／ <a href="${link(p.license_url || p.source)}" target="_blank" rel="noopener noreferrer">${clean(p.license)}</a> ／ <a href="${link(p.source)}" target="_blank" rel="noopener noreferrer">写真の出典</a><br>表示用に縮小・トリミングしています。</span></figcaption></figure>`;
  }
  function gallery(city, rest=false) {
    const items = rest ? (photos.rest[city] || cityPhotos(city)) : cityPhotos(city);
    if (!items.length) return '';
    const prefix = rest ? '休養日に訪れる場所を写真で見る' : `${clean(city)}の風景`;
    const note = rest ? `${clean(city)}での休養日は、自転車に乗らずに過ごします。下のプランに登場する場所や周辺の風景を、写真で紹介します。外出先は体調や天候に合わせて選びましょう。` : '写真の撮影場所は各写真の見出しで確認できます。経由地の周辺を紹介する写真も含みます。';
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

/* User-adjustable dialog size; no server storage or fullscreen permission needed. */
(() => {
  'use strict';
  const dialog = document.getElementById('destinationDialog');
  if (!dialog || document.getElementById('dialogSizeTools')) return;
  const KEY = 'orio-cycle-dialog-size-v1';
  const defaults = {width: 94, height: 94, maximized: false};
  const clamp = (n, lo, hi) => Math.min(hi, Math.max(lo, n));
  let settings = {...defaults};
  let storageAvailable = true;
  try {
    const stored = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (stored && typeof stored === 'object') {
      settings.width = Number.isFinite(stored.width) ? clamp(stored.width, 45, 100) : 94;
      settings.height = Number.isFinite(stored.height) ? clamp(stored.height, 50, 100) : 94;
      settings.maximized = stored.maximized === true;
    }
  } catch (_) { storageAvailable = false; }
  const css = document.createElement('style');
  css.id = 'dialogSizeStyles';
  css.textContent = `
  @media screen {
    #destinationDialog.destination-dialog[data-user-size] {
      position:fixed;inset:0!important;margin:auto!important;
      width:var(--user-dialog-width)!important;height:var(--user-dialog-height)!important;
      min-width:0!important;min-height:0!important;max-width:100vw!important;
      max-height:100dvh!important;box-sizing:border-box;container-type:inline-size;
      transition:none;overflow:hidden;
    }
    #destinationDialog[data-size-maximized="true"] {border-radius:0!important;}
    #destinationDialog .dialog-size-tools {
      flex:0 0 auto;position:relative;z-index:2;background:#edf3eb;
      border-bottom:1px solid #dce3d7;padding:10px 24px;
      font-size:12px;line-height:1.4;color:#294b3e;
    }
    #destinationDialog .dialog-size-top {display:flex;align-items:center;gap:9px;flex-wrap:wrap;}
    #destinationDialog .dialog-size-title {font-size:12px;white-space:nowrap;}
    #destinationDialog .dialog-size-readout {font-size:11px;color:#647767;white-space:nowrap;font-variant-numeric:tabular-nums;}
    #destinationDialog .dialog-size-actions {display:flex;gap:6px;align-items:center;margin-left:auto;}
    #destinationDialog .dialog-size-tools button {
      border:1px solid #bacbbc;border-radius:7px;padding:7px 11px;
      background:#fffefa;color:#294b3e;font:inherit;font-size:11px;line-height:1.4;
      min-height:34px;white-space:nowrap;cursor:pointer;
    }
    #destinationDialog .dialog-size-tools button:hover {background:#e1eddf;}
    #destinationDialog .dialog-size-tools .dialog-size-max {background:#234f3f;color:#fff;border-color:#234f3f;}
    #destinationDialog .dialog-size-tools .dialog-size-max:hover {background:#163c2e;}
    #destinationDialog .dialog-size-controls {display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:10px;}
    #destinationDialog .dialog-size-controls[hidden] {display:none;}
    #destinationDialog .dialog-size-control {display:grid;grid-template-columns:38px minmax(50px,1fr) 44px;gap:9px;align-items:center;font-size:11px;}
    #destinationDialog .dialog-size-control input {width:100%;min-width:0;height:24px;margin:0;accent-color:#247759;cursor:ew-resize;}
    #destinationDialog .dialog-size-control output {text-align:right;font-variant-numeric:tabular-nums;}
    #destinationDialog .dialog-size-hint {margin:7px 0 0;font-size:10px;color:#6e7f70;}
    #destinationDialog .dialog-size-hint[hidden] {display:none;}
    #destinationDialog .dialog-resize-grip {
      position:absolute;z-index:5;bottom:2px;right:2px;width:28px;height:28px;
      border:0;border-radius:7px;background:#dce8d9;color:#365743;
      padding:5px;cursor:nwse-resize;touch-action:none;display:grid;place-items:center;
    }
    #destinationDialog .dialog-resize-grip svg {width:17px;height:17px;pointer-events:none;}
    #destinationDialog .dialog-footer {padding-right:44px;}
    #destinationDialog[data-size-dragging] {user-select:none;}
    #destinationDialog .journey-rest-gallery .journey-photo-grid {grid-template-columns:repeat(3,minmax(0,1fr));}
    #destinationDialog .journey-rest-gallery .journey-photo-grid>figure:first-child {grid-column:auto;}
    #destinationDialog .journey-rest-gallery .journey-photo-grid>figure:first-child img {aspect-ratio:4/3;}
    #destinationDialog[data-size-narrow] .dialog-size-tools {padding:8px 12px;}
    #destinationDialog[data-size-narrow] .dialog-size-title {font-size:11px;}
    #destinationDialog[data-size-narrow] .dialog-size-readout {font-size:10px;}
    #destinationDialog[data-size-narrow] .dialog-size-controls {grid-template-columns:1fr;gap:3px;margin-top:6px;}
    #destinationDialog[data-size-narrow] .dialog-size-actions {gap:4px;}
    #destinationDialog[data-size-narrow] .dialog-size-tools button {font-size:10px;padding:5px 8px;min-height:32px;}
    #destinationDialog[data-size-narrow] .dialog-size-hint {font-size:9px;}
    #destinationDialog[data-size-narrow] .dialog-shell-head {padding:10px 16px 8px;}
    #destinationDialog[data-size-narrow] .dialog-description {font-size:11px;}
    #destinationDialog[data-size-narrow] .dialog-title-row h2 {font-size:25px;}
    #destinationDialog[data-size-narrow] .dialog-body {padding:16px 14px 24px;}
    #destinationDialog[data-size-narrow] .dialog-tabs {padding:0 14px;}
    #destinationDialog[data-size-narrow] .journey-rest-gallery .journey-photo-grid {grid-template-columns:1fr 1fr;}
    #destinationDialog[data-size-narrow] .journey-rest-gallery .journey-photo-grid>figure:first-child {grid-column:1/-1;}
    #destinationDialog[data-size-narrow] .journey-rest-gallery .journey-photo-grid>figure:first-child img {aspect-ratio:16/8;}
    #destinationDialog[data-size-compact] .dialog-description,
    #destinationDialog[data-size-compact] .dialog-pref,
    #destinationDialog[data-size-compact] .dialog-context,
    #destinationDialog[data-size-compact] .journey-mini-map {display:none!important;}
    #destinationDialog[data-size-compact] .dialog-shell-head {padding:8px 16px;}
    #destinationDialog[data-size-compact] .dialog-title-row h2 {font-size:22px;}
    #destinationDialog[data-size-compact] .dialog-journey {padding-top:7px;padding-bottom:7px;}
    #destinationDialog[data-size-compact] .dialog-size-tools {padding:6px 12px;}
    #destinationDialog[data-size-compact] .dialog-size-hint {display:none;}
    #destinationDialog[data-size-compact] .dialog-footer {padding-top:6px;padding-bottom:6px;}
    #destinationDialog[data-size-compact] .dialog-tabs button {padding-top:7px;padding-bottom:7px;}
    #destinationDialog[data-size-tiny] .dialog-journey .journey-step-meta,
    #destinationDialog[data-size-tiny] .dialog-journey .journey-stop-row {display:none!important;}
    #destinationDialog[data-size-tiny] .dialog-size-controls {grid-template-columns:1fr 1fr;gap:8px;}
    #destinationDialog[data-size-tiny] .dialog-size-control {grid-template-columns:22px minmax(30px,1fr) 32px;gap:4px;font-size:10px;}
    #destinationDialog[data-size-tiny] .dialog-shell-head {padding-top:5px;padding-bottom:5px;}
    #destinationDialog[data-size-tiny] .dialog-kicker {display:none;}
  }
  @media print {.dialog-size-tools,.dialog-resize-grip{display:none!important;}}
  `;
  document.head.append(css);
  const tools = document.createElement('section');
  tools.className = 'dialog-size-tools';
  tools.id = 'dialogSizeTools';
  tools.setAttribute('aria-label', '詳細ウィンドウのサイズ');
  tools.innerHTML = `
    <div class="dialog-size-top"><strong class="dialog-size-title">ウィンドウの大きさ</strong>
      <output class="dialog-size-readout" id="dialogSizeReadout" aria-label="現在のウィンドウサイズ"></output>
      <div class="dialog-size-actions">
        <button type="button" id="dialogSizeToggle" aria-expanded="false" aria-controls="dialogSizeControls">サイズ調整</button>
        <button type="button" id="dialogSizeMax" class="dialog-size-max" aria-pressed="false">最大化</button>
        <button type="button" id="dialogSizeReset">初期サイズ</button>
      </div>
    </div>
    <div class="dialog-size-controls" id="dialogSizeControls" hidden>
      <label class="dialog-size-control" for="dialogWidthRange"><span>幅</span><input type="range" id="dialogWidthRange" min="45" max="100" step="1" value="94"><output id="dialogWidthValue" for="dialogWidthRange">94%</output></label>
      <label class="dialog-size-control" for="dialogHeightRange"><span>高さ</span><input type="range" id="dialogHeightRange" min="50" max="100" step="1" value="94"><output id="dialogHeightValue" for="dialogHeightRange">94%</output></label>
    </div>
    <p class="dialog-size-hint" id="dialogSizeHint" hidden>スライダーで幅と高さを変更できます。右下の角をドラッグして調整することもできます。設定はこのブラウザに保存されます。</p>
    <span class="sr-only" id="dialogSizeAnnouncement" role="status" aria-live="polite"></span>`;
  const head = dialog.querySelector('.dialog-shell-head');
  if (head) head.after(tools); else dialog.prepend(tools);
  const grip = document.createElement('button');
  grip.type = 'button';grip.id = 'dialogResizeGrip';grip.className = 'dialog-resize-grip';
  grip.setAttribute('aria-label','ウィンドウのサイズを変更。ドラッグ、または矢印キーで調整できます。');
  grip.title = 'ドラッグでサイズ変更／矢印キーでも調整できます';
  grip.innerHTML='<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 16 16 4M9 16l7-7m-2 7 2-2"/></svg>';
  dialog.append(grip);
  const widthRange = tools.querySelector('#dialogWidthRange');
  const heightRange = tools.querySelector('#dialogHeightRange');
  const toggle = tools.querySelector('#dialogSizeToggle');
  const maxButton = tools.querySelector('#dialogSizeMax');
  const controls = tools.querySelector('#dialogSizeControls');
  const hint = tools.querySelector('#dialogSizeHint');
  const announce = message => {tools.querySelector('#dialogSizeAnnouncement').textContent=message;};
  let resizeFrame = 0;
  let drag = null;
  function viewport() {
    return {width:document.documentElement.clientWidth || innerWidth, height:innerHeight};
  }
  function persist() {
    try {localStorage.setItem(KEY,JSON.stringify(settings));storageAvailable=true;}
    catch (_) {storageAvailable=false;}
    hint.textContent = 'スライダーで幅と高さを変更できます。右下の角をドラッグして調整することもできます。'+(storageAvailable?'設定はこのブラウザに保存されます。':'このブラウザでは設定を保存できません。ページを閉じるまでの間だけ適用します。');
  }
  function apply() {
    const v=viewport();
    const minWidth=Math.min(v.width,320), minHeight=Math.min(v.height,360);
    const width=settings.maximized?v.width:clamp(v.width*settings.width/100,minWidth,v.width);
    const height=settings.maximized?v.height:clamp(v.height*settings.height/100,minHeight,v.height);
    dialog.setAttribute('data-user-size','true');
    dialog.setAttribute('data-size-maximized',String(settings.maximized));
    dialog.toggleAttribute('data-size-narrow',width<760);
    dialog.toggleAttribute('data-size-compact',height<720);
    dialog.toggleAttribute('data-size-tiny',height<470);
    dialog.style.setProperty('--user-dialog-width',Math.round(width)+'px');
    dialog.style.setProperty('--user-dialog-height',Math.round(height)+'px');
    widthRange.min=String(Math.max(45,Math.ceil(minWidth/v.width*100)));
    heightRange.min=String(Math.max(50,Math.ceil(minHeight/v.height*100)));
    const w=settings.maximized?100:Math.max(Number(widthRange.min),settings.width);
    const h=settings.maximized?100:Math.max(Number(heightRange.min),settings.height);
    widthRange.value=String(Math.round(w));heightRange.value=String(Math.round(h));
    tools.querySelector('#dialogWidthValue').textContent=Math.round(w)+'%';
    tools.querySelector('#dialogHeightValue').textContent=Math.round(h)+'%';
    widthRange.setAttribute('aria-valuetext',Math.round(w)+'%、約'+Math.round(width)+'ピクセル');
    heightRange.setAttribute('aria-valuetext',Math.round(h)+'%、約'+Math.round(height)+'ピクセル');
    tools.querySelector('#dialogSizeReadout').textContent=Math.round(width)+' × '+Math.round(height)+' px';
    maxButton.textContent=settings.maximized?'元のサイズ':'最大化';
    maxButton.setAttribute('aria-pressed',String(settings.maximized));
  }
  function setExpanded(expanded) {
    toggle.setAttribute('aria-expanded',String(expanded));
    controls.hidden=!expanded;hint.hidden=!expanded;
    toggle.textContent=expanded?'調整を閉じる':'サイズ調整';
  }
  function useRanges() {
    settings={width:Number(widthRange.value),height:Number(heightRange.value),maximized:false};
    apply();persist();
  }
  widthRange.addEventListener('input',useRanges);heightRange.addEventListener('input',useRanges);
  for(const range of [widthRange,heightRange])range.addEventListener('change',()=>announce('ウィンドウのサイズを変更しました。'));
  toggle.addEventListener('click',()=>setExpanded(controls.hidden));
  maxButton.addEventListener('click',()=>{
    settings.maximized=!settings.maximized;apply();persist();
    announce(settings.maximized?'ウィンドウを画面いっぱいに広げました。':'調整前のサイズに戻しました。');
  });
  tools.querySelector('#dialogSizeReset').addEventListener('click',()=>{
    settings={...defaults};apply();persist();announce('初期サイズに戻しました。');
  });
  function startDrag(event) {
    if(event.button!==0 || !event.isPrimary)return;
    event.preventDefault();event.stopPropagation();
    const rect=dialog.getBoundingClientRect();
    drag={id:event.pointerId,x:event.clientX,y:event.clientY,width:rect.width,height:rect.height};
    grip.setPointerCapture(event.pointerId);dialog.setAttribute('data-size-dragging','');
  }
  function moveDrag(event) {
    if(!drag||event.pointerId!==drag.id)return;
    event.preventDefault();
    const v=viewport();
    settings.width=clamp((drag.width+2*(event.clientX-drag.x))/v.width*100,Math.max(45,Number(widthRange.min)),100);
    settings.height=clamp((drag.height+2*(event.clientY-drag.y))/v.height*100,Math.max(50,Number(heightRange.min)),100);
    settings.maximized=false;apply();
  }
  function finishDrag(event) {
    if(!drag || (event && event.pointerId!==drag.id))return;
    const pointer=drag.id;drag=null;dialog.removeAttribute('data-size-dragging');
    if(grip.hasPointerCapture(pointer))grip.releasePointerCapture(pointer);
    persist();announce('ウィンドウのサイズを変更しました。');
  }
  grip.addEventListener('pointerdown',startDrag);
  grip.addEventListener('pointermove',moveDrag);
  grip.addEventListener('pointerup',finishDrag);
  grip.addEventListener('pointercancel',finishDrag);
  grip.addEventListener('lostpointercapture',finishDrag);
  grip.addEventListener('dblclick',()=>maxButton.click());
  grip.addEventListener('keydown',event=>{
    if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End'].includes(event.key))return;
    event.preventDefault();event.stopPropagation();
    if(event.key==='Home'){settings={...defaults};}
    else if(event.key==='End'){settings.maximized=true;}
    else{
      if(settings.maximized){settings={width:100,height:100,maximized:false};}
      const amount=event.shiftKey?5:1;
      if(event.key==='ArrowLeft')settings.width=clamp(Number(widthRange.value)-amount,Number(widthRange.min),100);
      if(event.key==='ArrowRight')settings.width=clamp(Number(widthRange.value)+amount,Number(widthRange.min),100);
      if(event.key==='ArrowUp')settings.height=clamp(Number(heightRange.value)-amount,Number(heightRange.min),100);
      if(event.key==='ArrowDown')settings.height=clamp(Number(heightRange.value)+amount,Number(heightRange.min),100);
    }
    apply();persist();announce('ウィンドウのサイズを変更しました。');
  });
  function scheduleApply(){if(viewport().width<760 || viewport().height<720)setExpanded(false);cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(apply);}
  window.addEventListener('resize',scheduleApply);
  if(window.visualViewport)window.visualViewport.addEventListener('resize',scheduleApply);
  new MutationObserver(()=>{if(dialog.open)apply();}).observe(dialog,{attributes:true,attributeFilter:['open']});
  dialog.addEventListener('close',()=>finishDrag());
  apply();
  setExpanded(viewport().width>=760 && viewport().height>=720);
  if(!storageAvailable)hint.textContent='設定はページを閉じるまでの間だけ適用します。このブラウザでは保存できません。';
  window.JourneyDialogSize=Object.freeze({version:'2026-09-25-v1',getState:()=>({...settings}),storageKey:KEY});
})();
