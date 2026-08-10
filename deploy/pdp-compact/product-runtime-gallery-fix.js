/* GRAMISS_PDP_GALLERY_SWITCH_V2 */
(function(){
  'use strict';

  function initGallery(){
    var shell=document.querySelector('.gramiss-pdp-runtime-v3');
    if(!shell) return;

    var gallery=shell.querySelector('.woocommerce-product-gallery');
    if(!gallery || gallery.dataset.g3DualStageReady==='1') return;

    var rawSlides=Array.prototype.slice.call(gallery.querySelectorAll('.woocommerce-product-gallery__wrapper > .woocommerce-product-gallery__image'));
    var slides=rawSlides.filter(function(slide){ return !slide.classList.contains('clone'); });
    var thumbs=Array.prototype.slice.call(gallery.querySelectorAll('ol.flex-control-thumbs img'));
    if(!slides.length || !thumbs.length) return;

    var sources=slides.map(function(slide){
      var img=slide.querySelector('img');
      if(!img) return null;
      return {
        src: img.getAttribute('data-large_image') || img.getAttribute('data-src') || img.currentSrc || img.src,
        srcset: img.getAttribute('data-srcset') || img.getAttribute('srcset') || '',
        sizes: img.getAttribute('sizes') || '',
        alt: img.getAttribute('alt') || ''
      };
    }).filter(Boolean);
    if(!sources.length) return;

    gallery.dataset.g3DualStageReady='1';

    var viewport=gallery.querySelector('.flex-viewport');
    var wrapper=gallery.querySelector('.woocommerce-product-gallery__wrapper');
    var nativeStage=viewport || (wrapper && wrapper.parentElement===gallery ? wrapper : null);

    var stage=document.createElement('div');
    stage.className='g3-dual-stage';
    stage.setAttribute('aria-live','polite');

    var secondary=document.createElement('img');
    secondary.className='g3-dual-image g3-dual-image-secondary';
    secondary.alt='';
    secondary.setAttribute('aria-hidden','true');

    var primary=document.createElement('img');
    primary.className='g3-dual-image g3-dual-image-primary';

    stage.appendChild(secondary);
    stage.appendChild(primary);

    if(nativeStage && nativeStage.parentNode===gallery){
      nativeStage.insertAdjacentElement('afterend',stage);
      nativeStage.style.setProperty('display','none','important');
    }else{
      var thumbsList=gallery.querySelector('ol.flex-control-thumbs');
      if(thumbsList) gallery.insertBefore(stage,thumbsList);
      else gallery.appendChild(stage);
      if(wrapper) wrapper.style.setProperty('display','none','important');
    }

    function applyImage(node,data){
      if(!node || !data) return;
      node.src=data.src;
      if(data.srcset) node.srcset=data.srcset; else node.removeAttribute('srcset');
      if(data.sizes) node.sizes=data.sizes; else node.removeAttribute('sizes');
      node.alt=data.alt || '';
    }

    function secondaryIndexFor(primaryIndex){
      if(sources.length<2) return -1;
      return primaryIndex===1 ? 0 : 1;
    }

    function show(index){
      if(index<0 || index>=sources.length) return;

      applyImage(primary,sources[index]);
      primary.setAttribute('aria-label',(sources[index].alt || 'تصویر محصول'));

      var secondaryIndex=secondaryIndexFor(index);
      if(secondaryIndex>=0 && sources[secondaryIndex]){
        applyImage(secondary,sources[secondaryIndex]);
        secondary.style.setProperty('display','block','important');
      }else{
        secondary.style.setProperty('display','none','important');
      }

      thumbs.forEach(function(thumb,i){
        var active=i===index;
        thumb.classList.toggle('flex-active',active);
        thumb.setAttribute('aria-current',active?'true':'false');
        thumb.style.setProperty('opacity',active?'1':'.62','important');
        thumb.style.setProperty('border-color',active?'#111318':'rgba(17,19,24,.10)','important');
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
      };
      thumb.addEventListener('click',activate,true);
      thumb.addEventListener('keydown',function(event){
        if(event.key==='Enter' || event.key===' '){ activate(event); }
      },true);
    });

    /* Block all legacy pointer-driven gallery movement while keeping thumbnail clicks available. */
    ['mousemove','pointermove','mouseover','mouseenter','mouseleave'].forEach(function(type){
      gallery.addEventListener(type,function(event){
        if(event.target && event.target.closest && event.target.closest('ol.flex-control-thumbs')) return;
        event.stopPropagation();
        if(event.stopImmediatePropagation) event.stopImmediatePropagation();
      },true);
    });

    gallery.querySelectorAll('.woocommerce-product-gallery__trigger').forEach(function(node){ node.remove(); });
    gallery.querySelectorAll('.woocommerce-product-gallery__wrapper, .woocommerce-product-gallery__image, .woocommerce-product-gallery__image img').forEach(function(node){
      node.style.setProperty('transform','none','important');
      node.style.setProperty('transition','none','important');
      node.style.setProperty('animation','none','important');
    });

    var initial=thumbs.findIndex(function(t){ return t.classList.contains('flex-active'); });
    show(initial>=0?initial:0);
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
