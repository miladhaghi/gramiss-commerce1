/* GRAMISS_PDP_PREMIUM_V1 */
(function(){
  'use strict';

  function qs(sel,root){ return (root||document).querySelector(sel); }
  function qsa(sel,root){ return Array.prototype.slice.call((root||document).querySelectorAll(sel)); }

  function categoryLabel(summary){
    var a=qs('.product_meta .posted_in a, .g2-pdp-meta .posted_in a',summary);
    var text=a?a.textContent.trim():'';
    var map=[
      [/پیراهن|shirt/i,'SHIRT'],[/تیشرت|تی.?شرت|t.?shirt/i,'T-SHIRT'],[/شلوار|jean|pants|trouser/i,'PANTS'],
      [/کتونی|کفش|sneaker|shoe/i,'SNEAKERS'],[/کلاه|cap|hat/i,'CAP'],[/کیف|bag/i,'BAG'],
      [/جوراب|sock/i,'SOCKS'],[/کمربند|belt/i,'BELT'],[/لباس زیر|underwear/i,'UNDERWEAR'],[/جاکلیدی|keychain/i,'KEYCHAIN']
    ];
    for(var i=0;i<map.length;i++){ if(map[i][0].test(text)) return map[i][1]; }
    return 'PRODUCT';
  }

  function makeEyebrow(summary){
    if(qs('.g3-product-eyebrow',summary)) return;
    var title=qs('.product_title, .g2-pdp-title',summary);
    if(!title) return;
    var el=document.createElement('span');
    el.className='g3-product-eyebrow';
    el.textContent='GRAMISS / '+categoryLabel(summary);
    title.parentNode.insertBefore(el,title);
  }

  function makeHelperRow(form){
    if(!form || qs('.g3-product-helper-row',form)) return;
    var anchor=form.querySelector('table.variations') || form.firstElementChild;
    if(!anchor) return;
    var row=document.createElement('div');
    row.className='g3-product-helper-row';
    var items=[['راهنمای سایز','size'],['جزئیات پارچه','fabric'],['فرم تن‌خور','fit']];
    items.forEach(function(item){
      var a=document.createElement('a');
      a.href='#g3-details-zone';
      a.textContent=item[0];
      a.dataset.helper=item[1];
      a.addEventListener('click',function(e){
        var target=qs('#g3-details-zone, .g3-details-zone');
        if(target){ e.preventDefault(); target.scrollIntoView({behavior:'smooth',block:'start'}); }
      });
      row.appendChild(a);
    });
    anchor.insertAdjacentElement('afterend',row);
  }

  function enhanceQuantity(summary){
    qsa('.quantity',summary).forEach(function(quantity){
      if(quantity.classList.contains('g3-premium-quantity')) return;
      var input=qs('input.qty',quantity);
      if(!input) return;
      quantity.classList.add('g3-premium-quantity');
      var minus=document.createElement('button');
      minus.type='button'; minus.className='g3-qty-step g3-qty-minus'; minus.setAttribute('aria-label','کاهش تعداد'); minus.textContent='−';
      var plus=document.createElement('button');
      plus.type='button'; plus.className='g3-qty-step g3-qty-plus'; plus.setAttribute('aria-label','افزایش تعداد'); plus.textContent='+';
      quantity.insertBefore(minus,input);
      quantity.appendChild(plus);
      function step(delta){
        var val=parseFloat(input.value||'0');
        var min=parseFloat(input.getAttribute('min')); if(isNaN(min)) min=1;
        var max=parseFloat(input.getAttribute('max')); if(isNaN(max)) max=Infinity;
        var inc=parseFloat(input.getAttribute('step')); if(isNaN(inc)||inc<=0) inc=1;
        var next=val+(delta*inc); next=Math.max(min,Math.min(max,next));
        input.value=String(next);
        input.dispatchEvent(new Event('change',{bubbles:true}));
      }
      minus.addEventListener('click',function(){ step(-1); });
      plus.addEventListener('click',function(){ step(1); });
    });
  }

  function priceText(summary){
    var amount=qs('.woocommerce-variation-price .amount:last-child',summary) || qs(':scope > .price .amount:last-child',summary) || qs('.price .amount:last-child',summary);
    if(!amount) return '';
    var t=(amount.textContent||'').replace(/\u00a0/g,' ').replace(/\s+/g,' ').trim();
    if(/تومان/.test(t)){
      t=t.replace(/تومان/g,'').trim();
      if(t) t=t+' تومان';
    }
    return t;
  }

  function syncCTA(summary){
    var p=priceText(summary);
    qsa('.single_add_to_cart_button',summary).forEach(function(btn){
      if(!btn.dataset.g3OriginalLabel) btn.dataset.g3OriginalLabel=(btn.textContent||'افزودن به سبد').trim();
      btn.textContent=p?('افزودن به سبد — '+p):'افزودن به سبد';
    });
  }

  function makeTrustRow(summary){
    if(qs('.g3-product-trust-row',summary)) return;
    var form=qs('form.cart',summary);
    if(!form) return;
    var row=document.createElement('div');
    row.className='g3-product-trust-row';
    [['پرداخت امن','✓'],['ارسال سریع','→'],['تعویض سایز','↻']].forEach(function(item){
      var box=document.createElement('div'); box.className='g3-product-trust-item';
      var icon=document.createElement('span'); icon.className='g3-product-trust-icon'; icon.setAttribute('aria-hidden','true'); icon.textContent=item[1];
      var text=document.createElement('span'); text.textContent=item[0];
      box.appendChild(icon); box.appendChild(text); row.appendChild(box);
    });
    form.insertAdjacentElement('afterend',row);
  }

  function clickNativeTab(tabClass){
    var link=qs('.woocommerce-tabs ul.tabs li.'+tabClass+' a');
    if(link){ link.click(); return true; }
    return false;
  }

  function makeInfoNav(shell){
    if(qs('.g3-premium-info-nav',shell)) return;
    var details=qs('.g3-details-zone',shell);
    var related=qs('.g3-related-zone',shell);
    if(!details && !related) return;
    if(details) details.id='g3-details-zone';
    if(related) related.id='g3-related-zone';
    var nav=document.createElement('div'); nav.className='g3-premium-info-nav';
    var cards=[
      {label:'درباره این محصول',tab:'description_tab',target:details},
      {label:'جزئیات و نگهداری',tab:'additional_information_tab',target:details},
      {label:'استایل پیشنهادی',tab:null,target:related}
    ];
    cards.forEach(function(cfg,idx){
      var b=document.createElement('button'); b.type='button'; b.className='g3-premium-info-card'; b.textContent=cfg.label;
      var exists=cfg.tab?!!qs('.woocommerce-tabs ul.tabs li.'+cfg.tab+' a'):!!cfg.target;
      if(!exists){ b.classList.add('is-disabled'); b.disabled=true; }
      if(idx===0 && exists) b.classList.add('is-active');
      b.addEventListener('click',function(){
        if(b.disabled) return;
        qsa('.g3-premium-info-card',nav).forEach(function(x){ x.classList.remove('is-active'); }); b.classList.add('is-active');
        if(cfg.tab) clickNativeTab(cfg.tab);
        if(cfg.target) cfg.target.scrollIntoView({behavior:'smooth',block:'start'});
      });
      nav.appendChild(b);
    });
    var insertion=details||related;
    insertion.parentNode.insertBefore(nav,insertion);
    if(related){
      var h2=qs('.related.products > h2',related);
      if(h2) h2.textContent='استایل پیشنهادی';
    }
  }

  function bindPriceSync(summary){
    if(summary.dataset.g3PriceSync==='1') return;
    summary.dataset.g3PriceSync='1';
    var form=qs('form.variations_form',summary);
    if(form){
      form.addEventListener('change',function(){ setTimeout(function(){ syncCTA(summary); },20); });
      var wrap=qs('.single_variation_wrap',form);
      if(wrap && window.MutationObserver){
        new MutationObserver(function(){ syncCTA(summary); }).observe(wrap,{subtree:true,childList:true,characterData:true,attributes:true});
      }
    }
  }

  function enhance(){
    var shell=qs('.gramiss-pdp-runtime-v3');
    if(!shell || shell.dataset.g3PremiumReady==='1') return false;
    var summary=qs('.g3-summary-slot > .summary, .g3-summary-slot > .g2-pdp-buy',shell);
    if(!summary) return false;
    shell.dataset.g3PremiumReady='1';
    document.body.classList.add('gramiss-pdp-premium-v1');
    document.documentElement.classList.add('gramiss-pdp-premium-ready');
    makeEyebrow(summary);
    var form=qs('form.variations_form, form.cart',summary);
    if(form && form.classList.contains('variations_form')) makeHelperRow(form);
    enhanceQuantity(summary);
    makeTrustRow(summary);
    makeInfoNav(shell);
    syncCTA(summary);
    bindPriceSync(summary);
    document.dispatchEvent(new CustomEvent('gramiss:pdp-premium-ready'));
    return true;
  }

  if(!enhance()){
    if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',enhance,{once:true});
    else setTimeout(enhance,0);
  }
  window.addEventListener('load',function(){ enhance(); setTimeout(function(){ var s=qs('.g3-summary-slot > .summary, .g3-summary-slot > .g2-pdp-buy'); if(s){ enhanceQuantity(s); syncCTA(s); } },80); },{once:true});
})();
