/* GRAMISS_CARD_TRANSFER_V1 */
(function(){
  'use strict';
  function copyText(value, button){
    var done=function(){
      if(!button)return;
      var label=button.querySelector('span');
      if(label){label.dataset.old=label.dataset.old||label.textContent;label.textContent='کپی شد';}
      button.classList.add('is-copied');
      window.setTimeout(function(){
        button.classList.remove('is-copied');
        if(label&&label.dataset.old)label.textContent=label.dataset.old;
      },1500);
    };
    if(navigator.clipboard&&window.isSecureContext){
      navigator.clipboard.writeText(value).then(done).catch(function(){fallback(value);done();});
      return;
    }
    fallback(value);done();
  }
  function fallback(value){
    var input=document.createElement('textarea');
    input.value=value;input.setAttribute('readonly','');input.style.position='fixed';input.style.opacity='0';
    document.body.appendChild(input);input.select();
    try{document.execCommand('copy');}catch(e){}
    document.body.removeChild(input);
  }
  document.addEventListener('click',function(e){
    var btn=e.target.closest&&e.target.closest('.gct-copy[data-copy]');
    if(!btn)return;
    e.preventDefault();copyText(btn.getAttribute('data-copy')||'',btn);
  });
  document.addEventListener('change',function(e){
    if(!e.target.matches||!e.target.matches('.gct-upload input[type="file"]'))return;
    var wrap=e.target.closest('.gct-upload');
    var label=wrap&&wrap.querySelector('[data-gct-file-name]');
    var file=e.target.files&&e.target.files[0];
    if(label)label.textContent=file?file.name:'JPG، PNG، WEBP یا PDF تا ۵MB';
  });
})();
