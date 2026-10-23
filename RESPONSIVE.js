/* RESPONSIVE.js — 배경 거울 확장 타일 생성 (B-2_봄 공통). .stage__bg 하나를 8방향으로 뒤집어 복제한다. */
(function(){
  function build(){
    var bg = document.querySelector('.stage__bg'); if(!bg || bg.dataset.rx) return;
    bg.dataset.rx = '1';
    ['l','r','t','b','tl','tr','bl','br'].forEach(function(k){
      var c = bg.cloneNode(false);
      c.removeAttribute('id'); c.removeAttribute('onerror');
      c.className = 'stage__bg--x ' + k; c.alt = ''; c.setAttribute('aria-hidden','true');
      c.src = bg.currentSrc || bg.src;
      bg.parentNode.insertBefore(c, bg.nextSibling);
    });
    /* 원본이 onerror 폴백으로 src 가 바뀌면 타일도 따라간다 */
    bg.addEventListener('load', function(){
      document.querySelectorAll('.stage__bg--x').forEach(function(c){ c.src = bg.currentSrc || bg.src; });
    });
  }
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build); else build();
})();
