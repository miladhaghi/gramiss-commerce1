/* GRAMISS_PDP_GALLERY_SWITCH_V1 */
(function(){
  'use strict';

  function initGallery(){
    var shell=document.querySelector('.gramiss-pdp-runtime-v3');
    if(!shell) return;

    var gallery=shell.querySelector('.woocommerce-product-gallery');
    if(!gallery || gallery.dataset.g3StaticSwitchReady==='1') return;

    var slides=Array.prototype.slice.call(gallery.querySelectorAll('.woocommerce-product-gallery__wrapper > .woocommerce-product-gallery__image'));
    var thumbs=Array.prototype.slice.call(gallery.querySelectorAll('ol.flex-control-thumbs img'));
    if(!slides.length || !thumbs.length) return;

    gallery.dataset.g3StaticSwitchReady='1';

    function show(index){
      if(index<0 || index>=slides.length) return;
      slides.forEach(function(slide,i){
        slide.style.setProperty('display', i===index ? 'flex' : 'none', 'important');
        slide.style.setProperty('opacity', i===index ? '1' : '0', 'important');
        slide.style.setProperty('visibility', i===index ? 'visible' : 'hidden', 'important');
        slide.style.setProperty('position', i===index ? 'relative' : 'absolute', 'important');
        slide.style.setProperty('inset', i===index ? 'auto' : '0', 'important');
        slide.setAttribute('aria-hidden', i===index ? 'false' : 'true');
      });
      thumbs.forEach(function(thumb,i){
        var active=i===index;
        thumb.classList.toggle('flex-active',active);
        thumb.setAttribute('aria-current',active?'true':'false');
        thumb.style.setProperty('opacity',active?'1':'.6','important');
        thumb.style.setProperty('border-color',active?'#111318':'rgba(17,19,24,.1)','important');
      });
      gallery.dataset.g3ActiveSlide=String(index);
    }

    thumbs.forEach(function(thumb,index){
      thumb.setAttribute('role','button');
      thumb.setAttribute('tabindex','0');
      var activate=function(event){
        if(event){
          event.preventDefault();
          event.stopPropagation();
          if(event.stopImmediatePropagation) event.stopImmediatePropagation();
        }
        show(index);
        requestAnimationFrame(function(){ show(index); });
        setTimeout(function(){ show(index); },30);
      };
      thumb.addEventListener('click',activate,true);
      thumb.addEventListener('keydown',function(event){
        if(event.key==='Enter' || event.key===' '){ activate(event); }
      },true);
    });

    var initial=thumbs.findIndex(function(t){ return t.classList.contains('flex-active'); });
    show(initial>=0?initial:0);

    /* Woo/FlexSlider may try to restore transforms/classes later. Keep our static gallery authoritative. */
    var observer=new MutationObserver(function(){
      var current=parseInt(gallery.dataset.g3ActiveSlide||'0',10);
      show(isNaN(current)?0:current);
    });
    var wrapper=gallery.querySelector('.woocommerce-product-gallery__wrapper');
    if(wrapper) observer.observe(wrapper,{attributes:true,attributeFilter:['style','class']});
  }

  function boot(){
    initGallery();
    setTimeout(initGallery,120);
    setTimeout(initGallery,500);
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot);
  else boot();
  window.addEventListener('load',boot);
})();
