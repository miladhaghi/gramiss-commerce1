/* GRAMISS HOME FLOATING HEADER V1 — progressive enhancement only. */
(function(){
  'use strict';
  var header=document.querySelector('.site-header--home-float');
  if(!header)return;

  var ticking=false;
  function sync(){
    header.classList.toggle('is-compact',window.scrollY>54);
    ticking=false;
  }
  function onScroll(){
    if(ticking)return;
    ticking=true;
    window.requestAnimationFrame(sync);
  }
  sync();
  window.addEventListener('scroll',onScroll,{passive:true});

  var count=header.querySelector('.gramiss-cart-count');
  if(count&&window.MutationObserver){
    var observer=new MutationObserver(function(){
      count.classList.remove('gramiss-count-pop');
      void count.offsetWidth;
      count.classList.add('gramiss-count-pop');
    });
    observer.observe(count,{childList:true,characterData:true,subtree:true});
  }
})();
