/* GRAMISS_PDP_TROUSER_SIZE_UI_V1 */
(function(){
  'use strict';

  function norm(v){ return String(v||'').trim().toLowerCase(); }

  function rowLabel(select){
    var row=select.closest('tr');
    var label=row && row.querySelector('th.label label, .label label');
    return norm(label ? label.textContent : '');
  }

  function isTrouserSizeSelect(select){
    var key=norm((select.name||'')+' '+(select.id||'')+' '+rowLabel(select));
    return key.indexOf('سایز شلوار')!==-1 ||
      key.indexOf('trouser-size')!==-1 || key.indexOf('trouser_size')!==-1 ||
      key.indexOf('pants-size')!==-1 || key.indexOf('pants_size')!==-1 ||
      key.indexOf('jeans-size')!==-1 || key.indexOf('jeans_size')!==-1 ||
      key.indexOf('shalvar')!==-1 || key.indexOf('شلوار')!==-1;
  }

  function triggerChange(select){
    if(window.jQuery){ window.jQuery(select).trigger('change'); }
    else { select.dispatchEvent(new Event('change',{bubbles:true})); }
  }

  function optionFor(select,value){
    return Array.prototype.find.call(select.options,function(o){ return o.value===value; });
  }

  function updateLabel(select){
    var row=select.closest('tr');
    var label=row && row.querySelector('th.label label, .label label');
    if(!label) return;
    var current=label.querySelector('.g3-current-variation-value');
    if(!current){
      current=document.createElement('span');
      current.className='g3-current-variation-value';
      label.appendChild(current);
    }
    var option=optionFor(select,select.value);
    current.textContent=option && select.value ? ' — '+option.textContent.trim() : '';
  }

  function findGroup(select){
    var parent=select.parentElement;
    if(!parent) return null;
    return parent.querySelector('.g3-trouser-size-options[data-select-name="'+CSS.escape(select.name)+'"]');
  }

  function sync(select){
    var group=findGroup(select);
    if(!group) return;
    Array.prototype.forEach.call(group.querySelectorAll('button[data-value]'),function(button){
      var option=optionFor(select,button.dataset.value);
      var disabled=!option || option.disabled || option.classList.contains('disabled');
      var selected=select.value===button.dataset.value;
      button.disabled=disabled;
      button.classList.toggle('is-disabled',disabled);
      button.classList.toggle('is-selected',selected);
      button.setAttribute('aria-pressed',selected?'true':'false');
      button.setAttribute('aria-disabled',disabled?'true':'false');
    });
    updateLabel(select);
  }

  function build(select){
    if(!isTrouserSizeSelect(select)) return;
    if(findGroup(select)){ sync(select); return; }

    var options=Array.prototype.slice.call(select.options).filter(function(o){ return o.value!==''; });
    if(!options.length || !select.parentElement) return;

    var group=document.createElement('div');
    group.className='g3-variation-options g3-size-options g3-trouser-size-options';
    group.dataset.selectName=select.name;
    group.setAttribute('role','group');
    group.setAttribute('aria-label','انتخاب سایز شلوار');

    options.forEach(function(option){
      var button=document.createElement('button');
      button.type='button';
      button.className='g3-variation-option g3-size-option';
      button.dataset.value=option.value;
      button.textContent=option.textContent.trim();
      button.title=option.textContent.trim();
      button.setAttribute('aria-label','سایز شلوار '+option.textContent.trim());
      button.setAttribute('aria-pressed','false');
      button.addEventListener('click',function(){
        if(button.disabled) return;
        select.value=button.dataset.value;
        triggerChange(select);
        requestAnimationFrame(function(){ sync(select); });
      });
      group.appendChild(button);
    });

    select.insertAdjacentElement('afterend',group);
    select.classList.add('g3-native-variation-select');
    select.dataset.g3TrouserSizeUiReady='1';
    sync(select);
  }

  function initForm(form){
    if(!form) return;
    var selects=Array.prototype.slice.call(form.querySelectorAll('select[name^="attribute_"]')).filter(isTrouserSizeSelect);
    if(!selects.length) return;

    selects.forEach(function(select){
      build(select);
      if(select.dataset.g3TrouserSizeEvents!=='1'){
        select.dataset.g3TrouserSizeEvents='1';
        select.addEventListener('change',function(){
          setTimeout(function(){ sync(select); },0);
          setTimeout(function(){ sync(select); },80);
        });
        var observer=new MutationObserver(function(){ sync(select); });
        observer.observe(select,{subtree:true,attributes:true,attributeFilter:['disabled','class','selected']});
      }
    });

    if(window.jQuery && form.dataset.g3TrouserSizeJq!=='1'){
      form.dataset.g3TrouserSizeJq='1';
      window.jQuery(form).on('woocommerce_update_variation_values woocommerce_variation_select_change check_variations found_variation reset_data hide_variation',function(){
        setTimeout(function(){ selects.forEach(function(s){ build(s); sync(s); }); },0);
        setTimeout(function(){ selects.forEach(sync); },80);
      });
    }
  }

  function boot(){
    var scope=document.querySelector('.gramiss-pdp-runtime-v3') || document;
    Array.prototype.forEach.call(scope.querySelectorAll('form.variations_form'),initForm);
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot,{once:true});
  else boot();
  window.addEventListener('load',function(){ setTimeout(boot,60); },{once:true});
})();
