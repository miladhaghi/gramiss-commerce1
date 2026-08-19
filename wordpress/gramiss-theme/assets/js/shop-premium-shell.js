/* GRAMISS_SHOP_PREMIUM_SHELL_JS_V2 */
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
    return r>=105&&r<=205&&g>=92&&g<=195&&b>=78&&b<=185&&r>=g&&g>=b&&Math.max(r,g,b)-Math.min(r,g,b)<=62;
  }
  function taupeStyle(style){
    if(!style)return false;
    if(taupe(style.backgroundColor)||taupe(style.borderTopColor)||taupe(style.borderBottomColor))return true;
    var bg=String(style.backgroundImage||'');
    var matches=bg.match(/rgba?\([^)]*\)/g)||[];
    return matches.some(taupe);
  }
  function ensurePseudoKillStyle(){
    if(qs('#gramiss-shop-top-cleanup-style'))return;
    var style=document.createElement('style');
    style.id='gramiss-shop-top-cleanup-style';
    style.textContent='body.gse-shop-ready .gramiss-strip-pseudo-kill::before,body.gse-shop-ready .gramiss-strip-pseudo-kill::after{display:none!important;content:none!important;height:0!important;min-height:0!important;margin:0!important;padding:0!important;border:0!important;background:none!important;box-shadow:none!important}';
    document.head.appendChild(style);
  }

  function cleanLegacyTitle(){
    var hero=qs('.gramiss-shop-premium-hero');
    if(!hero)return;
    var heroTop=hero.getBoundingClientRect().top;
    var currentTitle=(qs('h1',hero)||{}).textContent||'فروشگاه';
    currentTitle=String(currentTitle).trim();
    qsa('h1,h2,.page-title,.woocommerce-products-header__title,.entry-title').forEach(function(el){
      if(el.closest('.gramiss-shop-premium-hero'))return;
      var text=String(el.textContent||'').trim();
      if(text!==currentTitle&&text!=='فروشگاه')return;
      var rect=el.getBoundingClientRect();
      if(rect.bottom>heroTop+8)return;
      var parent=el.closest('.woocommerce-products-header,.page-header,.entry-header');
      var target=parent||el;
      target.style.setProperty('display','none','important');
      target.style.setProperty('margin','0','important');
      target.style.setProperty('padding','0','important');
      target.style.setProperty('min-height','0','important');
      target.setAttribute('aria-hidden','true');
    });
  }

  function cleanLegacyBand(){
    ensurePseudoKillStyle();
    var header=qs('.site-header,#masthead,header');
    var bottom=header?header.getBoundingClientRect().bottom:190;
    var hero=qs('.gramiss-shop-premium-hero');
    var heroTop=hero?hero.getBoundingClientRect().top:bottom+180;
    qsa('body *').forEach(function(el){
      if(el===header||el.closest('.gramiss-shop-premium-hero,.gramiss-shop-control-shell,.gramiss-shop-filter-overlay'))return;
      var rect=el.getBoundingClientRect();
      if(rect.width<innerWidth*.72||rect.top<bottom-8||rect.top>Math.min(heroTop+12,bottom+170)||rect.height<3||rect.height>70)return;
      var text=String(el.textContent||'').trim();
      var s=getComputedStyle(el);
      if(text.length<=4&&taupeStyle(s)){
        el.style.setProperty('display','none','important');
        el.style.setProperty('height','0','important');
        el.style.setProperty('min-height','0','important');
        el.style.setProperty('margin','0','important');
        el.style.setProperty('padding','0','important');
        return;
      }
      var before=getComputedStyle(el,'::before');
      var after=getComputedStyle(el,'::after');
      var pseudoTaupe=(before&&before.content!=='none'&&taupeStyle(before))||(after&&after.content!=='none'&&taupeStyle(after));
      if(pseudoTaupe){el.classList.add('gramiss-strip-pseudo-kill');}
    });
  }

  function cleanTop(){cleanLegacyTitle();cleanLegacyBand();}

  function init(){
    moveFilterTrigger();
    addStyleTip();
    bindDrawer();
    cleanTop();
    setTimeout(cleanTop,120);
    setTimeout(cleanTop,420);
    setTimeout(cleanTop,1100);
  }

  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',init,{once:true});}
  else{init();}
  window.addEventListener('pageshow',init);
})();
