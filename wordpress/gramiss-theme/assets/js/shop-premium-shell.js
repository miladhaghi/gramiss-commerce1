/* GRAMISS_SHOP_PREMIUM_SHELL_JS_V1 */
(function(){
  'use strict';

  function qs(sel,root){return (root||document).querySelector(sel);}
  function qsa(sel,root){return Array.prototype.slice.call((root||document).querySelectorAll(sel));}

  function moveFilterTrigger(){
    var trigger=qs('.gramiss-shop-filter-trigger');
    var toolbar=qs('.gramiss-shop-control-shell .gse-catalog-toolbar');
    if(trigger&&toolbar&&trigger.parentNode!==toolbar){toolbar.appendChild(trigger);}
  }

  function addStyleTip(){
    var grid=qs('ul.products.gse-products');
    if(!grid||qs('.gramiss-shop-style-tip',grid))return;
    var products=qsa(':scope > li.product',grid);
    if(products.length<4)return;
    var li=document.createElement('li');
    li.className='gramiss-shop-style-tip';
    li.innerHTML='<div class="gramiss-shop-style-tip__inner"><span class="gramiss-shop-style-tip__spark" aria-hidden="true">✦</span><div class="gramiss-shop-style-tip__copy" dir="rtl"><strong>نکته استایل گرامیس</strong><span>برای یک استایل تمیز و امروزی، رنگ اصلی لباس را ساده نگه دار و با یک اکسسوری یا بافت متفاوت به استایل عمق بده.</span></div><a class="gramiss-shop-style-tip__link" href="/#journal">مشاهده راهنمای استایل <span aria-hidden="true">←</span></a></div>';
    products[3].insertAdjacentElement('afterend',li);
  }

  function bindDrawer(){
    var trigger=qs('.gramiss-shop-filter-trigger');
    var overlay=qs('.gramiss-shop-filter-overlay');
    var close=qs('.gramiss-shop-filter-close');
    if(!trigger||!overlay||trigger.dataset.gramissBound==='1')return;
    trigger.dataset.gramissBound='1';
    function open(){overlay.classList.add('is-open');overlay.setAttribute('aria-hidden','false');trigger.setAttribute('aria-expanded','true');document.body.classList.add('gramiss-shop-filter-open');}
    function shut(){overlay.classList.remove('is-open');overlay.setAttribute('aria-hidden','true');trigger.setAttribute('aria-expanded','false');document.body.classList.remove('gramiss-shop-filter-open');}
    trigger.addEventListener('click',open);
    if(close)close.addEventListener('click',shut);
    overlay.addEventListener('click',function(e){if(e.target===overlay)shut();});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&overlay.classList.contains('is-open'))shut();});
  }

  function rgb(value){
    var m=String(value||'').match(/rgba?\((\d+)[, ]+(\d+)[, ]+(\d+)/i);
    return m?[+m[1],+m[2],+m[3]]:null;
  }
  function taupe(value){
    var c=rgb(value);if(!c)return false;
    var r=c[0],g=c[1],b=c[2];
    return r>=105&&r<=205&&g>=92&&g<=190&&b>=78&&b<=176&&r>=g&&g>=b&&Math.max(r,g,b)-Math.min(r,g,b)<=58;
  }
  function cleanLegacyBand(){
    var header=qs('.site-header,#masthead,header');
    var bottom=header?header.getBoundingClientRect().bottom:190;
    qsa('div,section,aside').forEach(function(el){
      if(el.closest('.gramiss-shop-premium-hero,.gramiss-shop-control-shell'))return;
      var rect=el.getBoundingClientRect();
      if(rect.width<innerWidth*.78||rect.top<bottom-4||rect.top>bottom+120||rect.height<5||rect.height>48)return;
      if(String(el.textContent||'').trim().length>2)return;
      var s=getComputedStyle(el);
      if(taupe(s.backgroundColor)){el.style.setProperty('display','none','important');}
    });
  }

  function init(){
    moveFilterTrigger();
    addStyleTip();
    bindDrawer();
    cleanLegacyBand();
    setTimeout(cleanLegacyBand,250);
    setTimeout(cleanLegacyBand,900);
  }

  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',init,{once:true});}
  else{init();}
  window.addEventListener('pageshow',init);
})();
