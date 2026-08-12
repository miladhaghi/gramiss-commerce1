/* GRAMISS_PDP_RUNTIME_V4 */
(function(){
  'use strict';

  function first(sel){ return document.querySelector(sel); }
  function releaseBoot(){
    document.documentElement.classList.remove('gramiss-pdp-booting');
    document.documentElement.classList.add('gramiss-pdp-booted');
  }

  function init(){
    var body=document.body;
    if(!body || !body.classList.contains('single-product')){ releaseBoot(); return; }
    if(first('.gramiss-pdp-runtime-v3')){ releaseBoot(); return; }

    var g2Root=first('.gramiss-pdp-v2');
    var product=first('main .product.type-product, .site-main .product.type-product, div.product.type-product, div.product');
    var gallery=first('.g2-pdp-gallery, .woocommerce-product-gallery');
    var summary=first('.g2-pdp-buy, .summary.entry-summary, .summary');
    var tabs=first('.g2-pdp-details .woocommerce-tabs, .woocommerce-tabs');
    var related=first('.g2-pdp-related .related.products, section.related.products, .related.products');

    if(!summary || !gallery){
      body.classList.add('gramiss-pdp-runtime-missing-core');
      releaseBoot();
      return;
    }

    var sourceRoot=g2Root || product || summary.parentElement;
    if(!sourceRoot || !sourceRoot.parentNode){ releaseBoot(); return; }

    var shell=document.createElement('div');
    shell.className='gramiss-pdp-runtime-v3';
    shell.setAttribute('data-runtime-version','4');

    var purchase=document.createElement('section');
    purchase.className='g3-purchase-zone';
    purchase.setAttribute('aria-label','مشاهده و خرید محصول');

    var summarySlot=document.createElement('div');
    summarySlot.className='g3-summary-slot';

    var gallerySlot=document.createElement('div');
    gallerySlot.className='g3-gallery-slot';

    var detailsZone=document.createElement('section');
    detailsZone.className='g3-details-zone';
    detailsZone.setAttribute('aria-label','اطلاعات کامل محصول');

    var relatedZone=document.createElement('section');
    relatedZone.className='g3-related-zone';
    relatedZone.setAttribute('aria-label','محصولات مرتبط');

    sourceRoot.parentNode.insertBefore(shell,sourceRoot);
    shell.appendChild(purchase);
    purchase.appendChild(summarySlot);
    purchase.appendChild(gallerySlot);
    summarySlot.appendChild(summary);
    gallerySlot.appendChild(gallery);

    if(tabs){ detailsZone.appendChild(tabs); shell.appendChild(detailsZone); }
    if(related){ relatedZone.appendChild(related); shell.appendChild(relatedZone); }

    shell.querySelectorAll('.woocommerce-product-gallery__trigger').forEach(function(node){ node.remove(); });
    shell.querySelectorAll('[data-parallax],[data-tilt],[data-magnetic]').forEach(function(node){
      node.removeAttribute('data-parallax');
      node.removeAttribute('data-tilt');
      node.removeAttribute('data-magnetic');
    });

    var customMain=shell.querySelector('#g2-pdp-main-image');
    if(customMain){
      shell.addEventListener('click',function(event){
        var thumb=event.target.closest('[data-g2-pdp-thumb]');
        if(!thumb || !shell.contains(thumb)) return;
        var src=thumb.getAttribute('data-src');
        var srcset=thumb.getAttribute('data-srcset');
        var alt=thumb.getAttribute('data-alt');
        if(src) customMain.src=src;
        if(srcset) customMain.srcset=srcset; else customMain.removeAttribute('srcset');
        if(alt) customMain.alt=alt;
        shell.querySelectorAll('[data-g2-pdp-thumb]').forEach(function(btn){
          var active=btn===thumb;
          btn.classList.toggle('is-active',active);
          btn.setAttribute('aria-pressed',active?'true':'false');
        });
      });
    }

    if(sourceRoot && sourceRoot!==shell){
      sourceRoot.setAttribute('data-gramiss-pdp-legacy-hidden','true');
      sourceRoot.style.setProperty('display','none','important');
      sourceRoot.style.setProperty('height','0','important');
      sourceRoot.style.setProperty('min-height','0','important');
      sourceRoot.style.setProperty('margin','0','important');
      sourceRoot.style.setProperty('padding','0','important');
      sourceRoot.style.setProperty('overflow','hidden','important');
    }

    body.classList.add('gramiss-pdp-runtime-ready');

    var stableNodes=shell.querySelectorAll('.woocommerce-product-gallery, .woocommerce-product-gallery *, .g2-pdp-gallery, .g2-pdp-gallery *, .g3-related-zone li.product, .g3-related-zone li.product *');
    stableNodes.forEach(function(node){
      node.style.setProperty('transform','none','important');
      node.style.setProperty('animation','none','important');
    });

    /* Release the first-paint gate immediately after the final DOM is in place. */
    releaseBoot();
  }

  /* This file is loaded with defer. Run synchronously as soon as the parsed DOM is available;
     do not defer another animation frame, because that caused the visible legacy-layout flash. */
  if(document.body){
    init();
  }else{
    document.addEventListener('DOMContentLoaded',init,{once:true});
  }

  window.addEventListener('load',function(){
    if(!document.body || !document.body.classList.contains('gramiss-pdp-runtime-ready')) init();
    releaseBoot();
  },{once:true});

  /* Never leave the storefront hidden if an unrelated third-party script fails. */
  window.setTimeout(releaseBoot,3500);
})();
