/* GRAMISS_PDP_GALLERY_SWITCH_V3 */
(function(){
  'use strict';

  function cleanUrl(value){
    try{
      return decodeURIComponent(String(value||'').split('?')[0]).toLowerCase();
    }catch(e){
      return String(value||'').split('?')[0].toLowerCase();
    }
  }

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
      var src=data.full_src || data.src || data.url || '';
      if(src) node.src=src;
      var srcset=data.srcset || data.src_set || '';
      if(srcset) node.srcset=srcset; else node.removeAttribute('srcset');
      if(data.sizes) node.sizes=data.sizes; else node.removeAttribute('sizes');
      node.alt=data.alt || '';
    }

    function sourceIndexForImage(data){
      if(!data) return -1;
      var target=cleanUrl(data.full_src || data.src || data.url || '');
      if(!target) return -1;
      return sources.findIndex(function(source){
        var src=cleanUrl(source.src);
        return src===target || src.indexOf(target)!==-1 || target.indexOf(src)!==-1;
      });
    }

    function tokensFor(meta){
      var tokens=[];
      if(meta){
        [meta.value,meta.label].forEach(function(value){
          var token=cleanUrl(value).replace(/[-_]+/g,' ').trim();
          if(token && token.length>1) tokens.push(token);
        });
      }
      return tokens;
    }

    function semanticSecondary(primaryIndex,meta){
      if(sources.length<2) return -1;
      var tokens=tokensFor(meta);
      if(tokens.length){
        var match=sources.findIndex(function(source,index){
          if(index===primaryIndex) return false;
          var hay=cleanUrl((source.src||'')+' '+(source.alt||'')).replace(/[-_]+/g,' ');
          return tokens.some(function(token){ return hay.indexOf(token)!==-1; });
        });
        if(match>=0) return match;
      }
      if(primaryIndex>=0){
        if(primaryIndex+1<sources.length) return primaryIndex+1;
        if(primaryIndex-1>=0) return primaryIndex-1;
      }
      return sources.length>1 ? 1 : -1;
    }

    function secondaryIndexFor(primaryIndex){
      if(sources.length<2) return -1;
      return primaryIndex===1 ? 0 : 1;
    }

    function markThumb(index){
      thumbs.forEach(function(thumb,i){
        var active=i===index;
        thumb.classList.toggle('flex-active',active);
        thumb.setAttribute('aria-current',active?'true':'false');
        thumb.style.setProperty('opacity',active?'1':'.62','important');
        thumb.style.setProperty('border-color',active?'#111318':'rgba(17,19,24,.10)','important');
      });
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

      markThumb(index);
      gallery.dataset.g3ActiveSlide=String(index);
      gallery.dataset.g3VariationImage='0';
    }

    gallery.g3ApplyVariationImage=function(image,meta){
      if(!image) return;
      applyImage(primary,image);
      primary.setAttribute('aria-label',image.alt || 'تصویر محصول');

      var primaryIndex=sourceIndexForImage(image);
      var secondaryIndex=semanticSecondary(primaryIndex,meta||{});
      if(secondaryIndex>=0 && sources[secondaryIndex]){
        applyImage(secondary,sources[secondaryIndex]);
        secondary.style.setProperty('display','block','important');
      }

      if(primaryIndex>=0){
        markThumb(primaryIndex);
        gallery.dataset.g3ActiveSlide=String(primaryIndex);
      }
      gallery.dataset.g3VariationImage='1';
    };

    gallery.g3ResetVariationImage=function(){
      var index=parseInt(gallery.dataset.g3BaseSlide||gallery.dataset.g3ActiveSlide||'0',10);
      show(isNaN(index)?0:index);
    };

    gallery.g3ShowSource=show;

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
    initial=initial>=0?initial:0;
    gallery.dataset.g3BaseSlide=String(initial);
    show(initial);
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
