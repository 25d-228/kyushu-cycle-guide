"""Apply idempotent usability fixes before building the review bundle."""
from pathlib import Path
p=Path('assets/main-settings.js')
s=p.read_text(encoding='utf-8')
s=s.replace("let readingKey='',renderToken=0;", "let readingKey='';")
s=s.replace("originalRender();improveDialog();readingKey=contentKey();const position=readingPositions.get(readingKey)||0,token=++renderToken;\n    requestAnimationFrame(()=>{if(token===renderToken&&placeDialog.open)q('dialogBody').scrollTop=position;});", "originalRender();improveDialog();readingKey=contentKey();\n    if(placeDialog.open)q('dialogBody').scrollTop=readingPositions.get(readingKey)||0;")
s=s.replace("const result=originalOpen(...args);improveDialog();return result;", "const result=originalOpen(...args);improveDialog();readingKey=contentKey();q('dialogBody').scrollTop=readingPositions.get(readingKey)||0;return result;")
s=s.replace("readingKey='';renderToken++;", "readingKey='';")
s=s.replace("try{localStorage.setItem(KEY,JSON.stringify(saved));localStorage.setItem(LEGACY,JSON.stringify({width:saved.width,height:saved.height,maximized:saved.maximized}));storageOK=true;}", "try{localStorage.setItem(KEY,JSON.stringify(saved));storageOK=true;}")
s=s.replace("catch(_){storageOK=false;}\n    apply();closeSettings();", "catch(_){storageOK=false;}\n    try{localStorage.setItem(LEGACY,JSON.stringify({width:saved.width,height:saved.height,maximized:saved.maximized}));}catch(_){}\n    apply();closeSettings();")
s=s.replace("const body=q('dialogBody'),gallery=body.querySelector('.journey-gallery');", "q('dialogDayBtn').textContent='地図に戻る';\n    const body=q('dialogBody'),gallery=body.querySelector('.journey-gallery');")
old="window.addEventListener('storage',event=>{if(event.key===KEY){try{saved=normalize(JSON.parse(event.newValue||'null'));apply();if(modal.open){draft={...saved};refreshDraft();}}catch(_){}}});"
new="window.addEventListener('storage',event=>{if(event.key===KEY){try{const dirty=modal.open&&JSON.stringify(draft)!==JSON.stringify(saved);saved=normalize(JSON.parse(event.newValue||'null'));apply();if(modal.open&&!dirty){draft={...saved};refreshDraft();}else if(dirty)q('uxSaveInfo').textContent='別のタブで表示設定が更新されました。編集中の内容は保持しています。保存すると、この内容が適用されます。';}catch(_){}}});"
s=s.replace(old,new)
marker="  apply();improveDialog();\n  window.JourneySettings="
if 'selectedTabObserver' not in s:
    s=s.replace(marker, "  const selectedTabObserver=new MutationObserver(()=>{document.querySelectorAll('[role=tablist]').forEach(list=>list.querySelectorAll('[role=tab]').forEach(t=>t.tabIndex=t.getAttribute('aria-selected')==='true'?0:-1));});\n  document.querySelectorAll('[role=tablist]').forEach(list=>selectedTabObserver.observe(list,{subtree:true,attributes:true,attributeFilter:['aria-selected']}));\n"+marker)
if 'function containDialogFocus' not in s:
    s=s.replace(marker, '''  function containDialogFocus(event) {
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
''' + marker)
p.write_text(s,encoding='utf-8')
