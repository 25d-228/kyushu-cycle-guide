/* Main-page settings and usability improvements. */
(() => {
  'use strict';
  const placeDialog = document.getElementById('destinationDialog');
  if (!placeDialog || document.getElementById('siteSettingsDialog')) return;
  const KEY = 'orio-cycle-site-settings-v2', LEGACY = 'orio-cycle-dialog-size-v1';
  const defaults = {width:94, height:94, maximized:false, textSize:'normal', reduceMotion:false};
  const clamp = (n,a,b) => Math.min(b,Math.max(a,n));
  function normalize(value) {
    const s = value && typeof value === 'object' ? value : {};
    return {width:Number.isFinite(s.width)?clamp(s.width,45,100):94,
      height:Number.isFinite(s.height)?clamp(s.height,50,100):94,
      maximized:s.maximized===true, textSize:s.textSize==='large'?'large':'normal', reduceMotion:s.reduceMotion===true};
  }
  let saved={...defaults}, storageOK=true;
  try { saved=normalize(JSON.parse(localStorage.getItem(KEY)||localStorage.getItem(LEGACY)||'null')); }
  catch (_) { storageOK=false; }
  let draft={...saved}, returnFocus=null, resizeFrame=0;
  const reduced = () => saved.reduceMotion || matchMedia('(prefers-reduced-motion: reduce)').matches;
  const css = document.createElement('style');
  css.id='mainSettingsStyles';
  css.textContent=`
    .site-header{position:sticky;top:0;z-index:30;background:#fffefa}
    html{scroll-padding-top:120px}.header-right{gap:18px}#openSiteSettings{min-height:44px;white-space:nowrap}
    .ux-mobile-nav{display:none}.ux-skip{position:fixed;left:16px;top:-80px;z-index:100;background:#183f35;color:#fff;padding:12px 18px;border-radius:8px}.ux-skip:focus{top:10px}
    .ux-search{display:grid;grid-template-columns:auto minmax(0,1fr) auto;gap:10px 14px;align-items:center;padding:16px 20px;background:#fffefa;border:1px solid #dbe1d5;border-radius:14px;margin:0 0 18px}
    .ux-search label{font-weight:650;font-size:13px}.ux-search input{width:100%;min-width:0;height:44px;border:1px solid #a9b8a8;border-radius:8px;padding:9px 12px;background:#fff;color:#203b33;font-size:15px}
    .ux-search button,.ux-button{min-height:44px;border:1px solid #b0bfad;border-radius:8px;padding:9px 15px;background:#fffefa;color:#254937;font:inherit;font-size:13px;cursor:pointer}
    .ux-search button,.ux-button.primary{background:#1d513c;color:white;border-color:#1d513c}.ux-search button:hover,.ux-button.primary:hover{background:#153e2d}
    .ux-search p{grid-column:2/-1;margin:0;color:#5c6e5b;font-size:11px}.ux-search p[data-error]{color:#a32621}
    #siteSettingsDialog{position:fixed;inset:0;margin:auto;padding:0;width:min(870px,calc(100vw - 40px));height:min(860px,calc(100dvh - 40px));max-width:calc(100vw - 24px);max-height:calc(100dvh - 24px);border:1px solid #ced8c9;border-radius:20px;color:#203b33;background:#fffefa;box-shadow:0 20px 80px #162e3a35;overflow:hidden}
    #siteSettingsDialog:not([open]){display:none}#siteSettingsDialog[open]{display:flex;flex-direction:column}
    #siteSettingsDialog::backdrop{background:#14241b80;backdrop-filter:blur(3px)}
    .ux-settings-head{display:flex;align-items:flex-start;gap:14px;padding:23px 28px 20px;border-bottom:1px solid #e1e7db;background:#f2f5eb;flex-shrink:0}
    .ux-settings-symbol{width:42px;height:42px;display:grid;place-items:center;background:#dfe8d7;border-radius:12px;flex-shrink:0}
    .ux-settings-head h2{font-size:23px;margin:0 0 3px;line-height:1.4}.ux-settings-head p{margin:0;font-size:12px;color:#586950}
    .ux-close{margin-left:auto;width:44px;height:44px;border:1px solid #c5d0bf;border-radius:50%;background:#fffefa;color:#294934;font:inherit;font-size:25px;flex-shrink:0;cursor:pointer}
    .ux-settings-body{overflow:auto;min-height:0;padding:24px 28px;overscroll-behavior:contain;scrollbar-gutter:stable}
    .ux-settings-section+ .ux-settings-section{border-top:1px solid #e1e7db;margin-top:24px;padding-top:22px}
    .ux-settings-section h3{font-size:17px;line-height:1.5;margin:0 0 6px}.ux-settings-section>p{font-size:13px;color:#5b6d57;margin:0 0 17px;line-height:1.8}
    .ux-settings-grid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:24px;align-items:start}
    .ux-presets{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:18px}.ux-presets button{flex:1;padding:9px 10px;white-space:nowrap}
    .ux-presets button[aria-pressed=true]{background:#e3eeda;border-color:#527746;color:#224c30;box-shadow:inset 0 0 0 1px #527746}
    .ux-range{display:grid;grid-template-columns:1fr auto;gap:6px;margin:13px 0;font-size:13px}.ux-range label{font-weight:600}.ux-range output{font-variant-numeric:tabular-nums;color:#4d6448}
    .ux-range input{grid-column:1/-1;width:100%;min-width:0;height:32px;margin:0;accent-color:#247759;cursor:pointer}
    .ux-preview{background:#f0f3eb;border:1px solid #d9e0d1;border-radius:12px;padding:15px;text-align:center;min-width:0}.ux-preview h4{font-size:12px;margin:0 0 10px;color:#586951}
    .ux-preview-screen{height:160px;max-width:100%;margin:auto;position:relative;overflow:hidden;background:repeating-linear-gradient(25deg,#e5ede3 0px,#e5ede3 24px,#ebf0e6 24px,#ebf0e6 48px);border:1px solid #bacab6;border-radius:5px}
    .ux-preview-window{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);border-radius:5px;border:1px solid #769769;background:#fffefa;box-shadow:0 2px 10px #375a2926;overflow:hidden;text-align:left}
    .ux-preview-top{background:#e7efdf;padding:4px 6px;color:#375c2d;font-size:9px}.ux-preview-lines{padding:10px;display:grid;gap:7px}.ux-preview-lines i{height:5px;background:#e0e8d9;border-radius:3px}.ux-preview-lines i:nth-child(2){width:78%}.ux-preview-lines i:nth-child(3){width:90%}
    .ux-preview output{display:block;font-size:13px;font-weight:650;margin-top:10px;font-variant-numeric:tabular-nums}.ux-preview p{font-size:11px;color:#5b6e54;line-height:1.65;margin:6px 0 0}
    .ux-reading{display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:start}.ux-reading label{font-size:13px}.ux-reading select{display:block;width:100%;border:1px solid #aebdaa;border-radius:8px;background:#fffefa;font:inherit;padding:10px;margin-top:7px;min-height:44px;color:inherit}
    .ux-check{display:flex;gap:9px;align-items:flex-start;cursor:pointer;padding-top:4px;line-height:1.7}.ux-check input{width:19px;height:19px;accent-color:#247759;flex-shrink:0;margin:3px 0 0}.ux-check small{display:block;color:#61715b;font-size:11px}
    .ux-settings-help summary{cursor:pointer;font-weight:650;min-height:44px;padding:9px 0;font-size:14px}.ux-settings-help dl{margin:8px 0;font-size:13px;line-height:1.8}.ux-settings-help dt{font-weight:650;margin-top:12px}.ux-settings-help dd{margin:2px 0 0;color:#56664f}
    .ux-settings-foot{flex-shrink:0;padding:16px 28px;border-top:1px solid #e1e7db;background:#f8faf4;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
    .ux-save-info{width:100%;font-size:11px;color:#596d52;margin:0}.ux-foot-actions{display:flex;gap:8px;margin-left:auto}.ux-settings-foot button{min-height:44px}
    .ux-toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);z-index:40;max-width:calc(100vw - 30px);border-radius:10px;background:#1f4835;color:white;padding:12px 20px;box-shadow:0 4px 18px #152d2440;font-size:13px;pointer-events:none;opacity:0}.ux-toast.visible{opacity:1}
    .ux-map-disclosure{margin:6px 0}.ux-map-disclosure summary{min-height:32px;padding:4px 8px;cursor:pointer;color:#425f3d;font-size:11px}.ux-map-disclosure .journey-mini-map{margin-bottom:6px}
    .ux-content-links{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}.ux-content-links button{min-height:40px;font:inherit;font-size:12px;padding:7px 12px;border:1px solid #b6c4ad;background:#f6f9f0;color:#365b31;border-radius:8px;cursor:pointer}
    .ux-location-photos{margin-top:24px;border-top:1px solid #e0e7d8;padding-top:10px}.ux-location-photos summary{padding:10px 0;min-height:44px;cursor:pointer;font-size:13px;color:#496142}
    #destinationDialog.destination-dialog[data-user-size]{position:fixed;inset:0!important;margin:auto!important;width:var(--user-dialog-width)!important;height:var(--user-dialog-height)!important;max-width:100vw!important;max-height:100dvh!important;min-width:0;min-height:0;overflow:hidden;transition:none}
    #destinationDialog[data-size-maximized=true]{border-radius:0!important}
    #destinationDialog .dialog-footer{padding-right:24px}#destinationDialog .dialog-close{min-width:44px;min-height:44px}
    #destinationDialog .dialog-tabs button{min-height:44px;font-size:13px}#destinationDialog .journey-btn{min-height:40px}
    #destinationDialog .dialog-body{min-height:0;overflow:auto;overflow-wrap:break-word}
    #destinationDialog .dialog-body :is(p,.card-tip,.context-note,.rest-stop-body p){font-size:var(--ux-reading-size,14px);line-height:1.85}
    #destinationDialog .dialog-body :is(.source-checked,.photo-date-note,.rest-estimate-note,.journey-gallery-note){font-size:12px}
    #destinationDialog .journey-rest-gallery .journey-photo-grid{grid-template-columns:repeat(3,minmax(0,1fr))}
    #destinationDialog .journey-rest-gallery .journey-photo-grid>figure:first-child{grid-column:auto}
    #destinationDialog .journey-rest-gallery .journey-photo-grid>figure:first-child img{aspect-ratio:4/3}
    #destinationDialog[data-size-narrow] .dialog-shell-head{padding:12px 16px 10px}
    #destinationDialog[data-size-narrow] .dialog-title-row h2{font-size:24px}
    #destinationDialog[data-size-narrow] .dialog-body{padding:16px 14px 24px}
    #destinationDialog[data-size-narrow] .dialog-tabs{padding:0 12px}
    #destinationDialog[data-size-narrow] .journey-rest-gallery .journey-photo-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
    #destinationDialog[data-size-narrow] .journey-rest-gallery .journey-photo-grid>figure:first-child{grid-column:1/-1}
    #destinationDialog[data-size-narrow] .journey-rest-gallery .journey-photo-grid>figure:first-child img{aspect-ratio:16/8}
    #destinationDialog[data-size-compact] :is(.dialog-pref,.dialog-description,.dialog-context){display:none!important}
    #destinationDialog[data-size-compact] .dialog-shell-head{padding:8px 16px}
    #destinationDialog[data-size-compact] .dialog-title-row h2{font-size:22px}
    #destinationDialog[data-size-compact] .dialog-kicker{display:none}
    #destinationDialog[data-size-compact] .dialog-journey{padding:6px 14px}
    #destinationDialog[data-size-compact] .dialog-footer{padding-top:6px;padding-bottom:6px}
    #destinationDialog[data-size-tiny] .ux-map-disclosure{display:none}
    #destinationDialog[data-size-tiny] .dialog-journey .journey-stop-row{display:grid!important;margin-top:5px}
    #destinationDialog[data-size-tiny] .dialog-shell-head{padding-top:5px;padding-bottom:5px}
    #destinationDialog[data-size-tiny] .dialog-close{top:3px;right:10px}
    #destinationDialog[data-size-tiny] .dialog-tabs button{min-height:36px;padding:5px 8px}
    html[data-ux-reduced] *,html[data-ux-reduced]{scroll-behavior:auto!important;animation-duration:.01ms!important;transition-duration:.01ms!important}
    @media(prefers-reduced-motion:reduce){html,html *{scroll-behavior:auto!important;animation-duration:.01ms!important;transition-duration:.01ms!important}}
    @media(max-width:860px){.header-inner{gap:8px}.header-right{gap:6px}.header-right #printBtn{padding:10px;min-width:44px;min-height:44px}.ux-print-label{display:none}
      .ux-mobile-nav{display:flex;justify-content:space-around;border-top:1px solid #e6eadf;padding:0 8px;gap:4px}.ux-mobile-nav a{min-height:44px;display:flex;align-items:center;justify-content:center;font-size:12px;padding:8px;color:#445e3b;text-decoration:none}
    }
    @media(max-width:600px){#siteSettingsDialog{width:calc(100vw - 24px);height:calc(100dvh - 24px);border-radius:16px}.ux-settings-head{padding:16px;gap:10px}.ux-settings-head h2{font-size:21px}.ux-settings-head p{font-size:11px}.ux-settings-symbol{display:none}.ux-settings-body{padding:18px 16px}.ux-settings-grid{grid-template-columns:1fr;gap:14px}.ux-preview{display:none}.ux-reading{grid-template-columns:1fr;gap:12px}.ux-settings-foot{padding:12px 16px;gap:8px}.ux-settings-foot>.ux-button{font-size:11px;padding:8px}.ux-foot-actions{gap:6px}.ux-foot-actions .ux-button{font-size:12px;padding:8px 11px}.ux-settings-section h3{font-size:16px}.ux-search{padding:12px;grid-template-columns:minmax(0,1fr) auto;gap:7px}.ux-search label{grid-column:1/-1}.ux-search p{grid-column:1/-1;font-size:11px}.ux-search input{font-size:16px}.ux-preview output{font-size:12px}#destinationDialog .dialog-body :is(.source-checked,.photo-date-note){font-size:11px}}
    @media(max-width:370px){.header-inner .brand{gap:7px}.brand-symbol{width:30px;height:30px}.brand-text strong{font-size:9px;letter-spacing:.08em}.brand-text small{font-size:8px}#openSiteSettings{padding:8px;font-size:12px;gap:5px}.header-right{gap:4px}.ux-mobile-nav a{font-size:11px;padding:7px 5px}}
    @media(max-height:500px){.ux-settings-head{padding:8px 16px}.ux-settings-head p{display:none}.ux-settings-body{padding:14px 18px}.ux-settings-foot{padding:8px 16px}.ux-save-info{display:none}.ux-preview{display:none}.ux-settings-grid{grid-template-columns:1fr}.site-header{position:relative}}
    @media print{#siteSettingsDialog,.ux-mobile-nav,.ux-search,#openSiteSettings,.ux-toast,.ux-skip{display:none!important}.site-header{position:static}}
  `;
  document.head.append(css);
  const gear='<svg class="icon" aria-hidden="true" viewBox="0 0 24 24"><path d="m9 3-1 3-3 1-2 3 2 2-1 3 2 3 3-1 3 2 3-2 3 1 2-3-1-3 2-2-2-3-3-1-1-3z"/><circle cx="12" cy="12" r="3"/></svg>';
  const button=document.createElement('button');
  button.id='openSiteSettings';button.type='button';button.className='button-light';
  button.setAttribute('aria-haspopup','dialog');button.setAttribute('aria-controls','siteSettingsDialog');button.innerHTML=gear+'設定';
  document.querySelector('.header-right').append(button);
  const print=document.getElementById('printBtn');if(print){print.innerHTML=icon('print')+'<span class="ux-print-label">印刷</span>';print.setAttribute('aria-label','旅の計画を印刷');}
  const mobileNav=document.createElement('nav');mobileNav.className='ux-mobile-nav';mobileNav.setAttribute('aria-label','ページ内メニュー');
  mobileNav.innerHTML='<a href="#workspace">地図</a><a href="#schedule">日程</a><a href="#restDays">休養日</a><a href="#travelGuide">観光・宿</a>';
  document.querySelector('.site-header').append(mobileNav);
  const skip=document.createElement('a');skip.href='#workspace';skip.className='ux-skip';skip.textContent='地図と日程の操作へ';document.body.prepend(skip);
  const search=document.createElement('form');search.className='ux-search';search.setAttribute('role','search');
  search.innerHTML='<label for="uxPlaceSearch">地名を検索</label><input id="uxPlaceSearch" type="search" list="uxPlaceOptions" autocomplete="off" placeholder="例：日田、海響館、熊本" aria-describedby="uxSearchStatus"><button type="submit">詳細を開く</button><datalist id="uxPlaceOptions"></datalist><p id="uxSearchStatus" role="status" aria-live="polite">地図にある地名を入力するか、候補から選んでください。</p>';
  document.getElementById('workspace').before(search);
  for(const name of Object.keys(DATA.places)){const o=document.createElement('option');o.value=name;search.querySelector('datalist').append(o);}
  search.addEventListener('input',()=>{const s=search.querySelector('p');s.removeAttribute('data-error');s.textContent='地図にある地名を入力するか、候補から選んでください。';search.querySelector('input').removeAttribute('aria-invalid');});
  search.addEventListener('submit',event=>{
    event.preventDefault();const input=search.querySelector('input'),name=input.value.trim(),s=search.querySelector('p');
    if(!Object.hasOwn(DATA.places,name)){s.setAttribute('data-error','');s.textContent='その地名は見つかりませんでした。入力欄の候補から選んでください。';input.setAttribute('aria-invalid','true');input.focus();return;}
    const modes=['small','kaikyo','main'].filter(m=>DATA[m].some(d=>d.stops.includes(name)));
    const current=window.JourneyNavigator?.getState().mode;
    input.focus();openPlace(name,modes.includes(current)?current:modes[0]||'main');
  });
  const modal=document.createElement('dialog');modal.id='siteSettingsDialog';modal.setAttribute('aria-labelledby','uxSettingsTitle');
  modal.innerHTML=`
    <header class="ux-settings-head"><div class="ux-settings-symbol">${gear}</div><div><h2 id="uxSettingsTitle" tabindex="-1">サイト設定</h2><p>表示の好みはここでまとめて変更できます。</p></div><button type="button" class="ux-close" id="uxSettingsClose" aria-label="設定を閉じる。未保存の変更は破棄されます。">×</button></header>
    <div class="ux-settings-body">
      <section class="ux-settings-section"><h3>地名を開いたときの大きさ</h3><p>観光・ホテル・休養日プランの詳細画面に共通で適用します。設定画面自体の大きさは変わりません。</p>
        <div class="ux-settings-grid"><div><div class="ux-presets" role="group" aria-label="詳細画面のサイズを選ぶ"><button type="button" class="ux-button" data-size-preset="standard" aria-pressed="false">標準</button><button type="button" class="ux-button" data-size-preset="wide" aria-pressed="false">ゆったり</button><button type="button" class="ux-button" data-size-preset="full" aria-pressed="false">画面いっぱい</button></div>
          <div class="ux-range"><label for="uxWidth">横幅</label><output id="uxWidthValue" for="uxWidth"></output><input type="range" id="uxWidth" min="45" max="100" step="1" aria-describedby="uxSizeNote"></div>
          <div class="ux-range"><label for="uxHeight">高さ</label><output id="uxHeightValue" for="uxHeight"></output><input type="range" id="uxHeight" min="50" max="100" step="1" aria-describedby="uxSizeNote"></div>
          <p id="uxSizeNote" style="font-size:12px;color:#596d52;line-height:1.8;margin:10px 0 0">画面に対する割合です。小さい画面では操作できる大きさを確保します。</p>
        </div><aside class="ux-preview" aria-label="詳細画面の大きさのプレビュー"><h4>サイズのプレビュー</h4><div class="ux-preview-screen" aria-hidden="true"><div class="ux-preview-window"><div class="ux-preview-top">地名の詳細</div><div class="ux-preview-lines"><i></i><i></i><i></i><i></i></div></div></div><output id="uxSizeReadout"></output><p>保存後、次に地名を開くと<br>この大きさで表示されます。</p></aside></div>
      </section>
      <section class="ux-settings-section"><h3>読みやすさと動き</h3><div class="ux-reading"><label for="uxTextSize">詳細画面の説明文<select id="uxTextSize"><option value="normal">標準の文字</option><option value="large">大きめの文字</option></select></label><label class="ux-check"><input type="checkbox" id="uxReduceMotion"><span>地図の移動を控えめにする<small>移動アニメーションを省きます。端末の「視差効果を減らす」設定にも対応します。</small></span></label></div></section>
      <details class="ux-settings-section ux-settings-help"><summary>操作ガイドと保存について</summary><dl><dt>「前の日・次の日」と「前の地点・次の地点」</dt><dd>日付を変える操作と、同じ日の経由地をたどる操作を分けています。最後の地点からは翌日へ進み、休養日も飛ばしません。</dd><dt>地図と写真を見たいとき</dt><dd>詳細画面の「この日の地図」で概略図を開けます。ホテルのタブでは宿の情報を先に表示し、街の写真は下にまとめています。</dd><dt>キーボードでの操作</dt><dd>Tabで項目を移動し、Escで画面を閉じられます。観光・ホテルなどのタブは左右の矢印キーでも切り替えられます。</dd><dt>保存される場所</dt><dd>設定はこの端末の同じブラウザに保存します。他の端末とは同期しません。表示設定を初期値に戻しても、旅行の日付や保存した観光・ホテル候補は消えません。</dd></dl></details>
    </div>
    <footer class="ux-settings-foot"><p id="uxSaveInfo" class="ux-save-info" role="status" aria-live="polite"></p><button class="ux-button" id="uxResetSettings" type="button">表示設定を初期値に</button><div class="ux-foot-actions"><button class="ux-button" id="uxCancelSettings" type="button">キャンセル</button><button class="ux-button primary" id="uxSaveSettings" type="button">変更を保存</button></div></footer>`;
  document.body.append(modal);
  const toast=document.createElement('div');toast.className='ux-toast';toast.setAttribute('role','status');toast.setAttribute('aria-live','polite');document.body.append(toast);let toastTimer;
  const q=id=>document.getElementById(id);
  function notify(text){clearTimeout(toastTimer);toast.textContent=text;toast.classList.add('visible');toastTimer=setTimeout(()=>toast.classList.remove('visible'),5000);}
  function dimensions(s){const w=document.documentElement.clientWidth||innerWidth,h=innerHeight;return {width:Math.round(s.maximized?w:clamp(w*s.width/100,Math.min(w,320),w)),height:Math.round(s.maximized?h:clamp(h*s.height/100,Math.min(h,360),h)),w,h};}
  function apply(){
    const d=dimensions(saved);placeDialog.dataset.userSize='true';placeDialog.dataset.sizeMaximized=String(saved.maximized);
    placeDialog.toggleAttribute('data-size-narrow',d.width<760);placeDialog.toggleAttribute('data-size-compact',d.height<720);placeDialog.toggleAttribute('data-size-tiny',d.height<470);
    placeDialog.style.setProperty('--user-dialog-width',d.width+'px');placeDialog.style.setProperty('--user-dialog-height',d.height+'px');
    document.documentElement.style.setProperty('--ux-reading-size',saved.textSize==='large'?'16px':'14px');document.documentElement.toggleAttribute('data-ux-reduced',reduced());
  }
  function refreshDraft(){
    const d=dimensions(draft),w=draft.maximized?100:Math.round(draft.width),h=draft.maximized?100:Math.round(draft.height);
    q('uxWidth').value=w;q('uxHeight').value=h;q('uxWidthValue').textContent=w+'%';q('uxHeightValue').textContent=h+'%';
    q('uxWidth').setAttribute('aria-valuetext',`${w}%、表示幅は約${d.width}ピクセル`);q('uxHeight').setAttribute('aria-valuetext',`${h}%、表示高は約${d.height}ピクセル`);
    q('uxSizeReadout').textContent=`${d.width} × ${d.height} px`;q('uxSizeNote').textContent=`この端末での表示サイズ：${d.width} × ${d.height} px。小さい画面では、操作できる最小サイズを確保します。`;
    const p=modal.querySelector('.ux-preview-window');p.style.width=d.width/d.w*100+'%';p.style.height=d.height/d.h*100+'%';
    q('uxTextSize').value=draft.textSize;q('uxReduceMotion').checked=draft.reduceMotion;
    modal.querySelectorAll('[data-size-preset]').forEach(b=>{const s=b.dataset.sizePreset;const yes=s==='full'?draft.maximized:s==='wide'?!draft.maximized&&draft.width===94&&draft.height===94:!draft.maximized&&draft.width===80&&draft.height===86;b.setAttribute('aria-pressed',String(yes));});
    q('uxSaveInfo').textContent=JSON.stringify(draft)===JSON.stringify(saved)?'変更は「変更を保存」を押すまで適用されません。':'未保存の変更があります。「変更を保存」で適用します。';
    if(!storageOK)q('uxSaveInfo').textContent+=' このブラウザでは保存できないため、このページを開いている間だけ適用します。';
  }
  function openSettings(){
    if(placeDialog.open)return;
    returnFocus=document.activeElement;draft={...saved};refreshDraft();modal.showModal();document.body.classList.add('ux-settings-open');document.body.style.overflow='hidden';q('uxSettingsTitle').focus({preventScroll:true});
  }
  function closeSettings(){modal.close();}
  button.addEventListener('click',openSettings);
  q('uxSettingsClose').addEventListener('click',closeSettings);q('uxCancelSettings').addEventListener('click',closeSettings);
  modal.addEventListener('close',()=>{document.body.classList.remove('ux-settings-open');document.body.style.removeProperty('overflow');(returnFocus?.isConnected?returnFocus:button).focus({preventScroll:true});draft={...saved};});
  modal.addEventListener('cancel',event=>{event.preventDefault();closeSettings();});
  // Dismiss only if both the press and release were on the backdrop, not after dragging a slider.
  let backdrop=false;
  const outside=e=>{const r=modal.getBoundingClientRect();return e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom;};
  modal.addEventListener('pointerdown',e=>{backdrop=e.target===modal&&outside(e);});
  modal.addEventListener('click',e=>{if(backdrop&&e.target===modal&&outside(e))closeSettings();backdrop=false;});
  for(const id of ['uxWidth','uxHeight'])q(id).addEventListener('input',()=>{draft.width=Number(q('uxWidth').value);draft.height=Number(q('uxHeight').value);draft.maximized=false;refreshDraft();});
  q('uxTextSize').addEventListener('change',()=>{draft.textSize=q('uxTextSize').value;refreshDraft();});q('uxReduceMotion').addEventListener('change',()=>{draft.reduceMotion=q('uxReduceMotion').checked;refreshDraft();});
  modal.querySelectorAll('[data-size-preset]').forEach(b=>b.addEventListener('click',()=>{const p=b.dataset.sizePreset;if(p==='full')draft.maximized=true;else Object.assign(draft,p==='wide'?{width:94,height:94,maximized:false}:{width:80,height:86,maximized:false});refreshDraft();}));
  q('uxResetSettings').addEventListener('click',()=>{draft={...defaults};refreshDraft();q('uxSaveInfo').textContent='初期値を選びました。「変更を保存」で表示設定だけを初期化します。';});
  q('uxSaveSettings').addEventListener('click',()=>{
    saved=normalize(draft);
    try{localStorage.setItem(KEY,JSON.stringify(saved));storageOK=true;}
    catch(_){storageOK=false;}
    try{localStorage.setItem(LEGACY,JSON.stringify({width:saved.width,height:saved.height,maximized:saved.maximized}));}catch(_){}
    apply();closeSettings();notify(storageOK?'表示設定を保存しました。次に開く詳細画面に適用されます。':'表示設定を適用しました。ブラウザに保存できないため、再読み込みすると元に戻ります。');
  });
  if(typeof moveCamera==='function'){const original=moveCamera;moveCamera=function(camera,animate=true){return original(camera,reduced()?false:animate);};}
  let readingKey='';const readingPositions=new Map();const miniExpanded={wide:null,narrow:null};
  function contentKey(){const n=window.JourneyNavigator?.getState();return [explorer.mode,n?.day,explorer.requested,explorer.tab].join('|');}
  function improveDialog(){
    apply();const nav=q('dialogJourneyNav'),map=nav?.querySelector('.journey-mini-map');
    if(map&&!map.closest('details')){const d=document.createElement('details');d.className='ux-map-disclosure';const category=placeDialog.hasAttribute('data-size-narrow')||placeDialog.hasAttribute('data-size-compact')?'narrow':'wide';d.open=miniExpanded[category]??(category==='wide');const s=document.createElement('summary');s.textContent='この日の地図（概略図）';map.before(d);d.append(s,map);s.addEventListener('click',()=>{miniExpanded[category]=!d.open;});}
    q('dialogDayBtn').textContent='地図に戻る';
    const body=q('dialogBody'),gallery=body.querySelector('.journey-gallery');
    if(explorer.tab==='hotels'&&gallery&&!gallery.closest('.ux-location-photos')){const d=document.createElement('details');d.className='ux-location-photos';const s=document.createElement('summary');s.textContent='この街の写真を見る（ホテルの写真ではありません）';d.append(s,gallery);body.append(d);}
    if(explorer.tab==='rest'&&!body.querySelector('.ux-content-links')){const bar=document.createElement('nav');bar.className='ux-content-links';bar.setAttribute('aria-label','休養日の情報へ移動');for(const [label,selector] of [['過ごし方を選ぶ','.rest-plan-header'],['時間割を見る','.rest-timeline-head'],['写真を見る','.journey-gallery']]){const b=document.createElement('button');b.type='button';b.textContent=label;b.addEventListener('click',()=>{const t=body.querySelector(selector);if(t){t.setAttribute('tabindex','-1');body.scrollTo({top:t.getBoundingClientRect().top-body.getBoundingClientRect().top+body.scrollTop-12,behavior:'auto'});t.focus({preventScroll:true});}});bar.append(b);}body.prepend(bar);}
    // Roving tabindex and arrow-key behavior complement the existing click handlers.
    document.querySelectorAll('[role=tablist]').forEach(list=>{const tabs=[...list.querySelectorAll('[role=tab]')].filter(t=>!t.hidden);tabs.forEach(t=>t.tabIndex=t.getAttribute('aria-selected')==='true'?0:-1);});
  }
  const originalRender=renderDestination;
  renderDestination=function(){
    if(readingKey)readingPositions.set(readingKey,q('dialogBody').scrollTop);
    originalRender();improveDialog();readingKey=contentKey();
    if(placeDialog.open)q('dialogBody').scrollTop=readingPositions.get(readingKey)||0;
  };
  // Saving a candidate replaces the body without going through renderDestination.
  const originalRefresh=refreshSavedButtons;
  refreshSavedButtons=function(){const top=q('dialogBody').scrollTop;originalRefresh();improveDialog();q('dialogBody').scrollTop=top;};
  const originalOpen=openPlace;
  openPlace=function(...args){const result=originalOpen(...args);improveDialog();readingKey=contentKey();q('dialogBody').scrollTop=readingPositions.get(readingKey)||0;return result;};
  placeDialog.addEventListener('close',()=>{if(readingKey)readingPositions.set(readingKey,q('dialogBody').scrollTop);readingKey='';});
  document.addEventListener('keydown',event=>{
    const tab=event.target.closest?.('[role=tab]'),list=tab?.closest('[role=tablist]');if(!list||event.altKey||event.ctrlKey||event.metaKey)return;
    if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;
    const tabs=[...list.querySelectorAll('[role=tab]')].filter(t=>!t.hidden&&!t.disabled),i=tabs.indexOf(tab);
    const index=event.key==='Home'?0:event.key==='End'?tabs.length-1:(i+(event.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
    event.preventDefault();event.stopPropagation();tabs[index].click();tabs.forEach(t=>t.tabIndex=t===tabs[index]?0:-1);tabs[index].focus({preventScroll:true});
  });
  new MutationObserver(()=>{if(placeDialog.open)improveDialog();}).observe(q('dialogJourneyNav'),{childList:true});
  new MutationObserver(()=>{if(placeDialog.open)improveDialog();}).observe(placeDialog,{attributes:true,attributeFilter:['open']});
  window.addEventListener('resize',()=>{cancelAnimationFrame(resizeFrame);resizeFrame=requestAnimationFrame(()=>{apply();if(modal.open)refreshDraft();if(placeDialog.open)improveDialog();});});
  matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',apply);
  window.addEventListener('storage',event=>{if(event.key===KEY){try{const dirty=modal.open&&JSON.stringify(draft)!==JSON.stringify(saved);saved=normalize(JSON.parse(event.newValue||'null'));apply();if(modal.open&&!dirty){draft={...saved};refreshDraft();}else if(dirty)q('uxSaveInfo').textContent='別のタブで表示設定が更新されました。編集中の内容は保持しています。保存すると、この内容が適用されます。';}catch(_){}}});
  const selectedTabObserver=new MutationObserver(()=>{document.querySelectorAll('[role=tablist]').forEach(list=>list.querySelectorAll('[role=tab]').forEach(t=>t.tabIndex=t.getAttribute('aria-selected')==='true'?0:-1));});
  document.querySelectorAll('[role=tablist]').forEach(list=>selectedTabObserver.observe(list,{subtree:true,attributes:true,attributeFilter:['aria-selected']}));
  function containDialogFocus(event) {
    if(event.key!=='Tab'||event.altKey||event.ctrlKey||event.metaKey)return;
    const target=event.currentTarget;
    const items=[...target.querySelectorAll('button,input,select,textarea,a[href],summary,[tabindex]')].filter(el=>!el.disabled&&el.tabIndex>=0&&el.getClientRects().length&&getComputedStyle(el).visibility!=='hidden');
    if(!items.length){event.preventDefault();target.focus();return;}
    const current=items.indexOf(document.activeElement);
    if(current===-1||(!event.shiftKey&&current===items.length-1)||(event.shiftKey&&current===0)){
      event.preventDefault();items[event.shiftKey?items.length-1:0].focus();
    }
  }
  modal.addEventListener('keydown',containDialogFocus);
  placeDialog.addEventListener('keydown',containDialogFocus);
  apply();improveDialog();
  window.JourneySettings=Object.freeze({version:'2026-09-26-main-settings-v1',getState:()=>({...saved}),storageKey:KEY,open:openSettings});
  window.JourneyDialogSize=Object.freeze({version:'2026-09-26-settings',getState:()=>({width:saved.width,height:saved.height,maximized:saved.maximized}),storageKey:LEGACY});
})();
