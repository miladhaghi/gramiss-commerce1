/* GRAMISS_SHOP_SCULPTED_V1 */
(function(){
  'use strict';
  function $(s,r){return (r||document).querySelector(s)}
  function $all(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))}
  function releaseBoot(){document.documentElement.classList.remove('gramiss-shop-booting')}

  function buildToolbar(products){
    if($('.gse-catalog-toolbar'))return;
    var nativeOrdering=$('.woocommerce-ordering');
    var nativeSelect=nativeOrdering?$('select.orderby',nativeOrdering):null;
    var resultCount=$('.woocommerce-result-count');
    var toolbar=document.createElement('section');toolbar.className='gse-catalog-toolbar';toolbar.setAttribute('aria-label','کنترل فروشگاه');
    var count=document.createElement('div');count.className='gse-count';
    var txt=resultCount?resultCount.textContent.trim():'';var nums=txt.match(/[۰-۹0-9]+/g);count.textContent=nums&&nums.length?nums[nums.length-1]+' محصول':'محصولات';
    var wrap=document.createElement('div');wrap.className='gse-search-wrap';
    var search=document.createElement('input');search.type='search';search.className='gse-search-input';search.placeholder='جست‌وجو در محصولات…';search.setAttribute('aria-label','جست‌وجو در محصولات');
    var params=new URLSearchParams(location.search);if(params.get('s'))search.value=params.get('s');
    search.addEventListener('keydown',function(e){if(e.key!=='Enter')return;e.preventDefault();var p=new URLSearchParams(location.search),q=search.value.trim();if(q)p.set('s',q);else p.delete('s');p.set('post_type','product');p.delete('paged');p.delete('product-page');location.href=location.pathname+'?'+p.toString()});
    wrap.appendChild(search);
    var tabs=document.createElement('div');tabs.className='gse-sort-tabs';tabs.setAttribute('role','group');tabs.setAttribute('aria-label','مرتب‌سازی محصولات');
    var choices=[['menu_order','پیش‌فرض'],['date','جدیدترین'],['price','ارزان‌ترین'],['price-desc','گران‌ترین'],['popularity','پرفروش‌ترین']];
    var active=nativeSelect&&nativeSelect.value?nativeSelect.value:(params.get('orderby')||'menu_order');
    choices.forEach(function(c){var value=c[0],label=c[1];if(nativeSelect&&!nativeSelect.querySelector('option[value="'+value+'"]'))return;var b=document.createElement('button');b.type='button';b.className='gse-sort-button'+(active===value?' is-active':'');b.dataset.orderby=value;b.textContent=label;b.addEventListener('click',function(){if(nativeSelect){nativeSelect.value=value;nativeSelect.dispatchEvent(new Event('change',{bubbles:true}));var f=nativeSelect.closest('form');if(f){if(typeof f.requestSubmit==='function')f.requestSubmit();else f.submit();return}}var p=new URLSearchParams(location.search);if(value==='menu_order')p.delete('orderby');else p.set('orderby',value);p.delete('paged');p.delete('product-page');location.href=location.pathname+(p.toString()?'?'+p.toString():'')});tabs.appendChild(b)});
    toolbar.appendChild(count);toolbar.appendChild(wrap);toolbar.appendChild(tabs);products.parentNode.insertBefore(toolbar,products);
  }

  function ensureSurface(item){
    var surface=$('.gse-card-surface',item);if(surface)return surface;
    surface=document.createElement('div');surface.className='gse-card-surface';
    item.insertBefore(surface,item.firstChild);
    Array.prototype.slice.call(item.childNodes).forEach(function(node){if(node!==surface)surface.appendChild(node)});
    return surface;
  }
  function ensureMediaFrame(surface){
    var link=$('.woocommerce-loop-product__link',surface);if(!link)return;
    var existing=$('.gse-media-frame',link);if(existing)return;
    var img=$('img',link);if(!img)return;
    var media=img.closest('picture')||img,frame=document.createElement('div');frame.className='gse-media-frame';media.parentNode.insertBefore(frame,media);frame.appendChild(media);
  }
  function ensureInfoPanel(surface){
    if($('.gse-info-panel',surface))return;
    var productLink=$('.woocommerce-loop-product__link',surface);var title=$('.woocommerce-loop-product__title',surface)||$('h2',surface)||$('h3',surface);var price=$('.price',surface);
    if(!title&&!price)return;
    var panel=document.createElement('div');panel.className='gse-info-panel';
    if(title){var a=document.createElement('a');a.className='gse-title-link';a.href=productLink&&productLink.href?productLink.href:'#';title.parentNode.removeChild(title);a.appendChild(title);panel.appendChild(a)}
    if(price){price.parentNode.removeChild(price);panel.appendChild(price)}
    surface.appendChild(panel);
  }
  function ensureActionOrb(surface){
    if($('.gse-action-orb',surface))return;
    var button=$('a.button,button.button,.button',surface);if(!button)return;
    var orb=document.createElement('div');orb.className='gse-action-orb';button.parentNode.insertBefore(orb,button);orb.appendChild(button);
  }
  function markProducts(products){
    $all(':scope > li.product',products).forEach(function(item,index){
      item.classList.remove('gse-large-right','gse-large-left','gse-small','gse-corner-card');item.classList.add('gse-sculpted-card');
      var cycle=index%8;if(cycle===0)item.classList.add('gse-large-right');else if(cycle===4)item.classList.add('gse-large-left');else item.classList.add('gse-small');
      var surface=ensureSurface(item);ensureMediaFrame(surface);ensureInfoPanel(surface);ensureActionOrb(surface);
    });
  }
  function init(){
    try{var products=$('ul.products');if(!products)return;document.body.classList.add('gse-shop-ready');products.classList.add('gse-products');markProducts(products);buildToolbar(products)}finally{releaseBoot()}
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
  window.addEventListener('pageshow',releaseBoot,{once:true});
})();
