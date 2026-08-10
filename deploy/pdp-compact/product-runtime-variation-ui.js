/* GRAMISS_PDP_VARIATION_UI_V1 */
(function(){
  'use strict';

  var COLOR_MAP={
    'blue':'#1d4f91','آبی':'#1d4f91',
    'charcoal':'#373331','ذغالی':'#373331',
    'sky-blue':'#69b7e6','آبی آسمانی':'#69b7e6',
    'beige':'#d8c4a5','بژ':'#d8c4a5',
    'purple':'#6d4d88','بنفش':'#6d4d88',
    'yellow':'#e2c33e','زرد':'#e2c33e',
    'olive':'#707546','زیتونی':'#707546',
    'green':'#2d7351','سبز':'#2d7351',
    'red':'#b43e3e','قرمز':'#b43e3e',
    'navy':'#202d45','سرمه‌ای':'#202d45','سرمه ای':'#202d45',
    'white':'#f7f6f2','سفید':'#f7f6f2',
    'black':'#171819','مشکی':'#171819',
    'gray':'#797977','grey':'#797977','طوسی':'#797977','خاکستری':'#797977',
    'brown':'#6c4c3d','قهوه‌ای':'#6c4c3d','قهوه ای':'#6c4c3d',
    'cream':'#eee5d2','کرم':'#eee5d2',
    'orange':'#d77a31','نارنجی':'#d77a31'
  };

  function norm(value){
    return String(value||'').trim().toLowerCase();
  }

  function triggerChange(select){
    if(window.jQuery){
      window.jQuery(select).trigger('change');
    }else{
      select.dispatchEvent(new Event('change',{bubbles:true}));
    }
  }

  function optionLabel(select,value){
    var option=Array.prototype.find.call(select.options,function(item){ return item.value===value; });
    return option ? option.textContent.trim() : '';
  }

  function colorFor(value,label){
    return COLOR_MAP[norm(value)] || COLOR_MAP[norm(label)] || '#c9c4bb';
  }

  function isColorSelect(select){
    var key=norm(select.name+' '+select.id);
    return key.indexOf('pa_color')!==-1 || key.indexOf('attribute_color')!==-1 || key.indexOf('رنگ')!==-1;
  }

  function isSizeSelect(select){
    var key=norm(select.name+' '+select.id);
    return key.indexOf('clothing-size')!==-1 || key.indexOf('pa_size')!==-1 || key.indexOf('attribute_size')!==-1 || key.indexOf('سایز')!==-1;
  }

  function updateCurrentLabel(select){
    var row=select.closest('tr');
    if(!row) return;
    var label=row.querySelector('th.label label, .label label');
    if(!label) return;
    var current=label.querySelector('.g3-current-variation-value');
    if(!current){
      current=document.createElement('span');
      current.className='g3-current-variation-value';
      label.appendChild(current);
    }
    var text=select.value ? optionLabel(select,select.value) : '';
    current.textContent=text ? ' — '+text : '';
  }

  function syncGroup(select){
    var group=select.parentElement && select.parentElement.querySelector('.g3-variation-options[data-select-name="'+CSS.escape(select.name)+'"]');
    if(!group) return;

    Array.prototype.forEach.call(group.querySelectorAll('button[data-value]'),function(button){
      var option=Array.prototype.find.call(select.options,function(item){ return item.value===button.dataset.value; });
      var disabled=!option || option.disabled || option.classList.contains('disabled');
      var selected=select.value===button.dataset.value;
      button.disabled=disabled;
      button.classList.toggle('is-disabled',disabled);
      button.classList.toggle('is-selected',selected);
      button.setAttribute('aria-pressed',selected?'true':'false');
      button.setAttribute('aria-disabled',disabled?'true':'false');
    });
    updateCurrentLabel(select);
  }

  function buildGroup(select){
    if(select.dataset.g3VariationUiReady==='1'){
      syncGroup(select);
      return;
    }
    if(!isColorSelect(select) && !isSizeSelect(select)) return;

    var parent=select.parentElement;
    if(!parent) return;
    var options=Array.prototype.slice.call(select.options).filter(function(option){ return option.value!==''; });
    if(!options.length) return;

    var group=document.createElement('div');
    group.className='g3-variation-options '+(isColorSelect(select)?'g3-color-options':'g3-size-options');
    group.dataset.selectName=select.name;
    group.setAttribute('role','group');

    options.forEach(function(option){
      var button=document.createElement('button');
      button.type='button';
      button.dataset.value=option.value;
      button.className=isColorSelect(select)?'g3-variation-option g3-color-option':'g3-variation-option g3-size-option';
      button.setAttribute('aria-pressed','false');
      button.title=option.textContent.trim();

      if(isColorSelect(select)){
        button.style.setProperty('--g3-swatch-color',colorFor(option.value,option.textContent));
        var dot=document.createElement('span');
        dot.className='g3-color-dot';
        dot.setAttribute('aria-hidden','true');
        button.appendChild(dot);
        button.setAttribute('aria-label','رنگ '+option.textContent.trim());
      }else{
        button.textContent=option.textContent.trim();
        button.setAttribute('aria-label','سایز '+option.textContent.trim());
      }

      button.addEventListener('click',function(){
        if(button.disabled) return;
        select.value=button.dataset.value;
        triggerChange(select);
        requestAnimationFrame(function(){ syncGroup(select); });
      });
      group.appendChild(button);
    });

    select.insertAdjacentElement('afterend',group);
    select.classList.add('g3-native-variation-select');
    select.dataset.g3VariationUiReady='1';
    syncGroup(select);
  }

  function syncAll(form){
    Array.prototype.forEach.call(form.querySelectorAll('select[name^="attribute_"]'),function(select){
      buildGroup(select);
      syncGroup(select);
    });
  }

  function gallery(){
    return document.querySelector('.gramiss-pdp-runtime-v3 .woocommerce-product-gallery');
  }

  function selectedColorMeta(form){
    var select=form.querySelector('select[name="attribute_pa_color"], select[name*="color"]');
    if(!select || !select.value) return {value:'',label:''};
    return {value:select.value,label:optionLabel(select,select.value)};
  }

  function productVariations(form){
    if(window.jQuery){
      var data=window.jQuery(form).data('product_variations');
      if(Array.isArray(data)) return data;
    }
    var raw=form.getAttribute('data-product_variations');
    if(!raw) return [];
    try{ return JSON.parse(raw); }catch(e){ return []; }
  }

  function variationMatchesColor(variation,value){
    var attrs=(variation && variation.attributes) || {};
    return Object.keys(attrs).some(function(key){
      return norm(key).indexOf('color')!==-1 && attrs[key]===value;
    });
  }

  function applyVariationImage(form,variation){
    if(!variation || !variation.image) return;
    var g=gallery();
    var meta=selectedColorMeta(form);
    if(g && typeof g.g3ApplyVariationImage==='function'){
      g.g3ApplyVariationImage(variation.image,meta);
      return;
    }
    var primary=document.querySelector('.gramiss-pdp-runtime-v3 .g3-dual-image-primary');
    if(primary){
      var src=variation.image.full_src || variation.image.src;
      if(src) primary.src=src;
      if(variation.image.srcset) primary.srcset=variation.image.srcset; else primary.removeAttribute('srcset');
      if(variation.image.sizes) primary.sizes=variation.image.sizes; else primary.removeAttribute('sizes');
      if(variation.image.alt) primary.alt=variation.image.alt;
    }
  }

  function previewSelectedColor(form){
    var meta=selectedColorMeta(form);
    if(!meta.value) return false;
    var variations=productVariations(form);
    var match=variations.find(function(variation){
      if(!variationMatchesColor(variation,meta.value)) return false;
      if(variation.variation_is_active===false) return false;
      if(!variation.image) return false;
      return !!(variation.image.full_src || variation.image.src);
    });
    if(!match) return false;
    applyVariationImage(form,match);
    return true;
  }

  function resetGallery(){
    var g=gallery();
    if(g && typeof g.g3ResetVariationImage==='function') g.g3ResetVariationImage();
  }

  function resetOrPreview(form){
    if(!previewSelectedColor(form)) resetGallery();
  }

  function initForm(form){
    if(!form || form.dataset.g3VariationUiReady==='1') return;
    var selects=form.querySelectorAll('select[name^="attribute_"]');
    if(!selects.length) return;

    form.dataset.g3VariationUiReady='1';
    syncAll(form);

    Array.prototype.forEach.call(selects,function(select){
      select.addEventListener('change',function(){
        setTimeout(function(){ syncAll(form); },0);
        setTimeout(function(){ syncAll(form); },80);
        if(isColorSelect(select)){
          setTimeout(function(){ previewSelectedColor(form); },20);
          setTimeout(function(){ previewSelectedColor(form); },100);
        }
      });
    });

    var reset=form.querySelector('.reset_variations');
    if(reset){
      reset.addEventListener('click',function(){
        setTimeout(function(){ syncAll(form); resetGallery(); },20);
      });
    }

    if(window.jQuery){
      var $form=window.jQuery(form);
      $form.on('woocommerce_update_variation_values woocommerce_variation_select_change check_variations',function(){
        setTimeout(function(){ syncAll(form); },0);
      });
      $form.on('found_variation',function(event,variation){
        syncAll(form);
        applyVariationImage(form,variation);
      });
      $form.on('reset_data hide_variation',function(){
        setTimeout(function(){ syncAll(form); },0);
        setTimeout(function(){ resetOrPreview(form); },30);
      });
    }

    var observer=new MutationObserver(function(){ syncAll(form); });
    Array.prototype.forEach.call(selects,function(select){
      observer.observe(select,{subtree:true,attributes:true,attributeFilter:['disabled','class','selected']});
    });
  }

  function boot(){
    var shell=document.querySelector('.gramiss-pdp-runtime-v3');
    if(!shell) return;
    Array.prototype.forEach.call(shell.querySelectorAll('form.variations_form'),initForm);
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot);
  else boot();
  window.addEventListener('load',function(){ setTimeout(boot,60); });
})();
