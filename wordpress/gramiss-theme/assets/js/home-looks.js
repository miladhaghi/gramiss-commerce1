/* GRAMISS_HOME_LOOKS_V1 — interaction only; markup/data are server-rendered. */
(function(){
  'use strict';
  function init(root){
    var spots=Array.prototype.slice.call(root.querySelectorAll('.g1-look-hotspot'));
    if(!spots.length)return;
    var closeAll=function(except){spots.forEach(function(s){if(s!==except){s.classList.remove('is-active');var b=s.querySelector('.g1-look-hotspot-toggle');if(b)b.setAttribute('aria-expanded','false');}})};
    spots.forEach(function(spot){
      var button=spot.querySelector('.g1-look-hotspot-toggle');
      if(!button)return;
      button.addEventListener('click',function(ev){
        ev.preventDefault();ev.stopPropagation();
        var open=!spot.classList.contains('is-active');
        closeAll(spot);spot.classList.toggle('is-active',open);button.setAttribute('aria-expanded',open?'true':'false');
      });
      spot.addEventListener('mouseenter',function(){if(window.matchMedia('(hover:hover)').matches){closeAll(spot);spot.classList.add('is-active');button.setAttribute('aria-expanded','true');}});
      spot.addEventListener('mouseleave',function(){if(window.matchMedia('(hover:hover)').matches){spot.classList.remove('is-active');button.setAttribute('aria-expanded','false');}});
      spot.addEventListener('focusin',function(){closeAll(spot);spot.classList.add('is-active');button.setAttribute('aria-expanded','true');});
      spot.addEventListener('focusout',function(ev){if(!spot.contains(ev.relatedTarget)){spot.classList.remove('is-active');button.setAttribute('aria-expanded','false');}});
    });
    document.addEventListener('click',function(ev){if(!root.contains(ev.target)){closeAll();}});
    document.addEventListener('keydown',function(ev){if(ev.key==='Escape')closeAll();});
  }
  function boot(){document.querySelectorAll('[data-g1-looks]').forEach(init);}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
