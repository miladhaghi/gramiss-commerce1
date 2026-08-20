/* GRAMISS HOME FLOATING HEADER V3 — no scroll-time layout work. */
(function(){
  'use strict';
  var header=document.querySelector('.site-header--home-float');
  if(!header)return;

  /* No window scroll listener, no compact class, no layout mutation on scroll. */
  header.classList.remove('is-compact');

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
