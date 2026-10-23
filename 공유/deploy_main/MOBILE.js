/* MOBILE.js — 배포본(deploy_main) 전용. MOBILE.css 와 짝.
   1) 세로 안내 오버레이 #mbRotate 생성. 문구는 앱 언어(localStorage noriLang, 없으면 <html lang>)를 큰 글씨로,
      다른 언어를 작은 글씨로 함께 보여준다. 세로로 바뀔 때마다 언어를 다시 읽는다.
   2) 첫 터치에서 screen.orientation.lock('landscape') 를 한 번 시도한다. 전체화면은 요청하지 않으므로
      대부분의 브라우저에서 거절되며, 실패는 조용히 무시하고 오버레이가 대신한다.
   3) DESIGN.css 의 종이 질감 변수(--pp-tx-* · --pp-star-*-img)를 절대 URL 로 다시 지정한다.
      변수 속 url() 은 그 변수를 "쓰는" 스타일시트 기준으로 풀린다 — DESIGN.css 안의 원판 버튼 등은
      DESIGN.css 기준, B-2 게임·A-3·A-4 의 인라인 스타일은 페이지 기준이라 상대경로 하나로는 양쪽이 맞지 않는다.
      절대 URL 이면 file:// · 하위 경로 호스팅 어디서든 같다. 질감이 첫 화면부터 보이도록 이 파일은 defer 없이 <head> 에서 로드. */
(function(){
  var me = document.currentScript && document.currentScript.src;
  if(!me) return;
  var TX = {
    '--pp-tx-grain':'tx-paper-grain.webp', '--pp-tx-sheet':'tx-paper-sheet.webp', '--pp-tx-felt':'tx-felt.webp',
    '--pp-tx-btn':'tx-btn-grain.webp', '--pp-tx-card':'card-felt-teal.webp', '--pp-tx-grass':'cell-grass.webp',
    '--pp-tx-disc':'disc.webp', '--pp-tx-pill':'pill-wood.webp',
    '--pp-star-off-img':'star-off.svg', '--pp-star-on-img':'star-on.svg'
  };
  var st = document.documentElement.style;
  for(var k in TX) st.setProperty(k, 'url("' + new URL('img_png/paper/' + TX[k], me).href + '")');
})();
(function(){
  var TXT = {
    ko:{main:'기기를 가로로 돌려주세요', label:'가로 화면 안내'},
    en:{main:'Please turn your device sideways', label:'Rotate your device'}
  };
  function lang(){
    var l = null;
    try{ l = localStorage.getItem('noriLang') }catch(e){}
    if(l !== 'ko' && l !== 'en') l = (document.documentElement.lang || '').slice(0,2) === 'ko' ? 'ko' : 'en';
    return l;
  }
  var box, mainEl, subEl;
  function paint(){
    if(!box) return;
    var l = lang(), o = l === 'ko' ? 'en' : 'ko';
    mainEl.textContent = TXT[l].main; mainEl.lang = l;
    subEl.textContent = TXT[o].main; subEl.lang = o;
    box.setAttribute('aria-label', TXT[l].label);
  }
  function build(){
    if(document.getElementById('mbRotate')) return;
    box = document.createElement('div');
    box.id = 'mbRotate'; box.setAttribute('role','alertdialog');
    box.innerHTML =
      '<div class="mb-card">' +
        '<svg class="mb-icon" viewBox="0 0 96 96" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">' +
          '<rect x="30" y="12" width="36" height="72" rx="8"/><path d="M44 72h8"/></svg>' +
        '<p class="mb-main"></p><p class="mb-sub"></p>' +
      '</div>';
    mainEl = box.querySelector('.mb-main'); subEl = box.querySelector('.mb-sub');
    paint();
    document.body.appendChild(box);
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build); else build();

  var mq = window.matchMedia ? matchMedia('(orientation:portrait) and (max-width:900px)') : null;
  if(mq){ var on = function(){ if(mq.matches) paint() };
    if(mq.addEventListener) mq.addEventListener('change', on); else if(mq.addListener) mq.addListener(on); }
  window.addEventListener('storage', function(e){ if(e.key === 'noriLang') paint() });

  function tryLock(){
    window.removeEventListener('pointerdown', tryLock, true);
    try{
      var so = screen.orientation;
      if(so && typeof so.lock === 'function'){ var p = so.lock('landscape'); if(p && p.catch) p.catch(function(){}) }
    }catch(e){}
  }
  window.addEventListener('pointerdown', tryLock, true);
})();
