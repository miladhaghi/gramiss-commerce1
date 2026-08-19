<?php
/**
 * Premium Gramiss cart experience.
 *
 * @package Gramiss
 */
defined( 'ABSPATH' ) || exit;

function gramiss_premium_cart_before(): void {
    if ( ! function_exists( 'is_cart' ) || ! is_cart() ) {
        return;
    }
    ?>
    <section class="gramiss-cart-perks gramiss-cart-perks--top" aria-label="مزایای خرید از گرامیس">
        <div class="gramiss-cart-perk"><span class="gramiss-cart-perk__icon" aria-hidden="true">⌁</span><span><strong>ارسال سریع و رایگان</strong><small>برای سفارش‌های واجد شرایط</small></span></div>
        <div class="gramiss-cart-perk"><span class="gramiss-cart-perk__icon" aria-hidden="true">↻</span><span><strong>بازگشت و تعویض آسان</strong><small>تا ۷ روز پس از دریافت کالا</small></span></div>
        <div class="gramiss-cart-perk"><span class="gramiss-cart-perk__icon" aria-hidden="true">♢</span><span><strong>پرداخت امن و مطمئن</strong><small>محافظت از اطلاعات پرداخت</small></span></div>
    </section>
    <?php
}
add_action( 'woocommerce_before_cart', 'gramiss_premium_cart_before', 4 );

function gramiss_premium_cart_after(): void {
    if ( ! function_exists( 'is_cart' ) || ! is_cart() ) {
        return;
    }
    ?>
    <section class="gramiss-cart-service-rail" aria-label="خدمات گرامیس">
        <div><span aria-hidden="true">▣</span><strong>ارسال سریع و رایگان</strong><small>ارسال مطمئن و پیگیری‌پذیر</small></div>
        <div><span aria-hidden="true">↻</span><strong>بازگشت و تعویض آسان</strong><small>تا ۷ روز پس از دریافت کالا</small></div>
        <div><span aria-hidden="true">✧</span><strong>تضمین اصالت کالا</strong><small>محصولات منتخب و کنترل‌شده</small></div>
        <div><span aria-hidden="true">◌</span><strong>پشتیبانی اختصاصی</strong><small>همراه شما در مسیر خرید</small></div>
    </section>
    <section class="gramiss-cart-safe">
        <span class="gramiss-cart-safe__badge" aria-hidden="true">✓</span>
        <span><strong>با خیال راحت خرید کنید</strong><small>اطلاعات شما با استانداردهای امنیتی محافظت می‌شود.</small></span>
    </section>
    <?php
}
add_action( 'woocommerce_after_cart', 'gramiss_premium_cart_after', 30 );

function gramiss_premium_cart_continue_link(): void {
    if ( ! function_exists( 'is_cart' ) || ! is_cart() ) {
        return;
    }
    $shop_url = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/' );
    ?>
    <a class="gramiss-cart-continue" href="<?php echo esc_url( $shop_url ); ?>">ادامه خرید <span aria-hidden="true">←</span></a>
    <?php
}
add_action( 'woocommerce_after_cart_totals', 'gramiss_premium_cart_continue_link', 25 );

function gramiss_premium_cart_item_name( $name, $cart_item, $cart_item_key ) {
    if ( ! function_exists( 'is_cart' ) || ! is_cart() ) {
        return $name;
    }
    $product = isset( $cart_item['data'] ) && $cart_item['data'] instanceof WC_Product ? $cart_item['data'] : null;
    if ( $product && $product->is_in_stock() ) {
        $name .= '<span class="gramiss-cart-stock"><span aria-hidden="true">✓</span> موجود در انبار</span>';
    }
    return $name;
}
add_filter( 'woocommerce_cart_item_name', 'gramiss_premium_cart_item_name', 20, 3 );

function gramiss_premium_free_shipping_label( $label, $method ) {
    if ( function_exists( 'is_cart' ) && is_cart() && is_object( $method ) && isset( $method->cost ) && (float) $method->cost <= 0 ) {
        return '<span class="gramiss-cart-free-shipping">رایگان</span>';
    }
    return $label;
}
add_filter( 'woocommerce_cart_shipping_method_full_label', 'gramiss_premium_free_shipping_label', 20, 2 );

function gramiss_premium_cart_assets(): void {
    if ( ! function_exists( 'is_cart' ) || ! is_cart() ) {
        return;
    }

    $css = <<<'CSS'
body.woocommerce-cart{background:linear-gradient(180deg,#f7f3ec 0,#fbfaf7 42%,#f4f1ea 100%);color:#11151a}
body.woocommerce-cart .content-area{width:min(calc(100% - 64px),1460px);margin:0 auto 110px}
body.woocommerce-cart article.page{padding-top:46px}
body.woocommerce-cart article.page>h1{margin:0 0 34px;text-align:right;font-size:clamp(36px,4vw,58px);line-height:1.2;letter-spacing:-.035em;font-weight:900;color:#11151a}
body.woocommerce-cart article.page>h1::after{content:"خانه  ‹  سبد خرید";display:block;margin-top:10px;color:#8b8f96;font-size:11px;font-weight:500;letter-spacing:0}
body.woocommerce-cart .woocommerce{display:grid;grid-template-columns:minmax(0,1fr) 385px;grid-template-areas:"notice notice" "perks perks" "form totals" "services totals" "safe totals";gap:24px 28px;align-items:start;direction:ltr}
body.woocommerce-cart .woocommerce>*{direction:rtl}
body.woocommerce-cart .woocommerce-notices-wrapper{grid-area:notice}
.gramiss-cart-perks--top{grid-area:perks}
body.woocommerce-cart .woocommerce-cart-form{grid-area:form;margin:0!important}
body.woocommerce-cart .cart-collaterals{grid-area:totals;width:100%!important;margin:0!important;float:none!important}
.gramiss-cart-service-rail{grid-area:services}
.gramiss-cart-safe{grid-area:safe}

.gramiss-cart-perks{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;padding:12px 18px;border:1px solid rgba(17,21,26,.08);border-radius:16px;background:rgba(255,255,255,.58);backdrop-filter:blur(12px);box-shadow:0 8px 24px rgba(17,21,26,.035)}
.gramiss-cart-perk{min-height:54px;display:flex;align-items:center;justify-content:center;gap:10px;color:#6f747d}
.gramiss-cart-perk__icon{width:30px;height:30px;border-radius:50%;display:grid;place-items:center;color:#a9825b;background:#f2e8dc;font-size:17px}
.gramiss-cart-perk strong,.gramiss-cart-perk small{display:block}.gramiss-cart-perk strong{font-size:11px;color:#363b42}.gramiss-cart-perk small{margin-top:2px;font-size:9px;color:#92969d}

body.woocommerce-cart table.shop_table{margin:0!important;border:1px solid rgba(17,21,26,.09)!important;border-radius:22px!important;background:rgba(255,255,255,.94)!important;box-shadow:0 18px 44px rgba(17,21,26,.055)!important;overflow:hidden;border-collapse:separate!important;border-spacing:0!important}
body.woocommerce-cart table.shop_table thead{background:rgba(248,246,241,.72)}
body.woocommerce-cart table.shop_table thead th{padding:20px 16px!important;border:0!important;border-bottom:1px solid rgba(17,21,26,.08)!important;color:#2c3137;font-size:11px!important;font-weight:800!important;text-align:center!important;white-space:nowrap}
body.woocommerce-cart table.shop_table td{padding:24px 16px!important;border:0!important;border-bottom:1px solid rgba(17,21,26,.08)!important;vertical-align:middle!important;color:#1a1f25;font-size:12px;text-align:center}
body.woocommerce-cart table.shop_table tbody tr.cart_item:last-of-type td{border-bottom:1px solid rgba(17,21,26,.08)!important}
body.woocommerce-cart td.product-thumbnail{width:126px;padding-left:8px!important;padding-right:18px!important}
body.woocommerce-cart td.product-thumbnail a{display:block;width:112px;height:128px;border-radius:18px;overflow:hidden;background:#eee9e1;border:1px solid rgba(17,21,26,.06)}
body.woocommerce-cart td.product-thumbnail img{width:100%!important;height:100%!important;max-width:none!important;object-fit:contain!important;padding:6px;filter:drop-shadow(0 10px 14px rgba(17,21,26,.10));transition:transform .3s ease}
body.woocommerce-cart td.product-thumbnail:hover img{transform:scale(1.035)}
body.woocommerce-cart td.product-name{min-width:240px;text-align:right!important;font-size:14px!important;line-height:1.9!important;font-weight:750!important}
body.woocommerce-cart td.product-name>a{color:#171b20!important;text-decoration:none!important}
body.woocommerce-cart td.product-name dl.variation{margin:8px 0 0!important;color:#737982;font-size:11px;font-weight:500}
body.woocommerce-cart td.product-name dl.variation dt,body.woocommerce-cart td.product-name dl.variation dd{margin:0 0 3px!important;padding:0!important;float:none!important;display:inline!important}
body.woocommerce-cart td.product-name dl.variation dd p{display:inline!important;margin:0!important}
.gramiss-cart-stock{width:max-content;margin-top:11px;padding:6px 10px;border:1px solid #e4d9cc;border-radius:10px;display:flex;align-items:center;gap:6px;color:#766557;background:#faf6f0;font-size:9px;font-weight:700}
.gramiss-cart-stock>span{width:16px;height:16px;border-radius:50%;display:grid;place-items:center;background:#e8efe7;color:#5c7d63;font-size:9px}
body.woocommerce-cart td.product-price,body.woocommerce-cart td.product-subtotal{font-size:13px!important;font-weight:800!important;white-space:nowrap}
body.woocommerce-cart td.product-remove{width:52px;padding-right:8px!important;padding-left:16px!important}
body.woocommerce-cart td.product-remove a.remove{width:36px!important;height:36px!important;border:1px solid rgba(17,21,26,.12)!important;border-radius:50%!important;display:grid!important;place-items:center!important;color:#191d22!important;background:#fff!important;font:400 20px/1 Arial,sans-serif!important;transition:.2s ease!important}
body.woocommerce-cart td.product-remove a.remove:hover{background:#161a1f!important;color:#fff!important;border-color:#161a1f!important;transform:rotate(7deg)}

body.woocommerce-cart .gramiss-qty{display:inline-grid;grid-template-columns:38px 50px 38px;align-items:center;border:1px solid rgba(17,21,26,.13);border-radius:12px;overflow:hidden;background:#fff;box-shadow:0 4px 12px rgba(17,21,26,.035)}
body.woocommerce-cart .gramiss-qty button{height:42px;border:0;background:#fff;color:#1b1f24;font-size:19px;cursor:pointer;transition:.18s ease}
body.woocommerce-cart .gramiss-qty button:hover{background:#f2eee7}
body.woocommerce-cart .gramiss-qty .quantity{margin:0!important}
body.woocommerce-cart .gramiss-qty .qty{width:50px!important;height:42px!important;padding:0!important;border:0!important;border-inline:1px solid rgba(17,21,26,.09)!important;border-radius:0!important;background:#fff!important;text-align:center!important;font-weight:800!important;-moz-appearance:textfield}
body.woocommerce-cart .gramiss-qty .qty::-webkit-outer-spin-button,body.woocommerce-cart .gramiss-qty .qty::-webkit-inner-spin-button{-webkit-appearance:none;margin:0}

body.woocommerce-cart table.shop_table td.actions{padding:18px 20px!important;background:#fff!important}
body.woocommerce-cart td.actions{position:relative}
body.woocommerce-cart td.actions .coupon{display:flex!important;align-items:center;gap:8px!important;float:right!important}
body.woocommerce-cart td.actions .coupon label{display:none!important}
body.woocommerce-cart td.actions .coupon #coupon_code{width:270px!important;height:50px!important;margin:0!important;padding:0 16px!important;border:1px solid rgba(17,21,26,.13)!important;border-radius:13px!important;background:#fbfaf7!important;color:#15191e!important;font-size:11px!important;box-shadow:none!important}
body.woocommerce-cart td.actions .coupon .button{height:50px!important;margin:0!important;padding:0 20px!important;border-radius:13px!important;background:#12161b!important;color:#fff!important;font-size:11px!important;box-shadow:0 8px 18px rgba(17,21,26,.12)!important}
body.woocommerce-cart td.actions>button[name="update_cart"]{float:left!important;min-height:48px!important;padding:0 18px!important;border-radius:999px!important;background:#eeece8!important;color:#535861!important;box-shadow:none!important;font-size:10px!important}
body.woocommerce-cart td.actions>button[name="update_cart"]:not(:disabled){background:#1a1e23!important;color:#fff!important}

body.woocommerce-cart .cart-collaterals .cart_totals{width:100%!important;float:none!important;position:sticky;top:126px;margin:0!important;padding:28px 28px 24px;border:1px solid rgba(17,21,26,.09);border-radius:24px;background:linear-gradient(180deg,rgba(255,255,255,.98),rgba(250,247,242,.98));box-shadow:0 22px 55px rgba(17,21,26,.075)}
body.woocommerce-cart .cart_totals h2{margin:0 0 18px!important;padding:0 0 18px!important;border-bottom:1px solid rgba(17,21,26,.08);font-size:0!important;text-align:right}
body.woocommerce-cart .cart_totals h2::after{content:"خلاصه سفارش";font-size:20px;line-height:1.5;font-weight:900;color:#15191e}
body.woocommerce-cart .cart_totals h2::before{content:"▱";width:34px;height:34px;margin-left:9px;border-radius:50%;display:inline-grid;place-items:center;vertical-align:middle;background:#efe5d9;color:#9b7654;font-size:18px}
body.woocommerce-cart .cart_totals table.shop_table{border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important}
body.woocommerce-cart .cart_totals table.shop_table th,body.woocommerce-cart .cart_totals table.shop_table td{padding:13px 0!important;border:0!important;background:transparent!important;font-size:11px!important}
body.woocommerce-cart .cart_totals table.shop_table th{text-align:right!important;font-weight:700!important;color:#41464d;width:48%}
body.woocommerce-cart .cart_totals table.shop_table td{text-align:left!important;font-weight:750!important;color:#15191e}
body.woocommerce-cart .cart_totals .order-total th,body.woocommerce-cart .cart_totals .order-total td{padding-top:20px!important;border-top:1px solid rgba(17,21,26,.10)!important;font-size:14px!important}
body.woocommerce-cart .cart_totals .order-total strong{font-weight:900!important}
.gramiss-cart-free-shipping{color:#28a96f;font-weight:900}
body.woocommerce-cart .wc-proceed-to-checkout{padding:20px 0 0!important;margin:0!important}
body.woocommerce-cart .wc-proceed-to-checkout a.checkout-button{min-height:62px!important;margin:0!important;border-radius:15px!important;display:flex!important;align-items:center;justify-content:center;background:linear-gradient(180deg,#1b1e23,#0e1115)!important;color:#fff!important;font-size:13px!important;font-weight:900!important;box-shadow:0 14px 26px rgba(17,21,26,.20)!important;transition:.25s ease!important}
body.woocommerce-cart .wc-proceed-to-checkout a.checkout-button:hover{transform:translateY(-2px)!important;box-shadow:0 18px 34px rgba(17,21,26,.24)!important}
.gramiss-cart-continue{height:54px;margin-top:12px;border:1px solid rgba(17,21,26,.12);border-radius:14px;display:flex;align-items:center;justify-content:center;gap:9px;color:#4e545d;text-decoration:none;font-size:11px;font-weight:750;background:rgba(255,255,255,.62);transition:.2s ease}
.gramiss-cart-continue:hover{background:#fff;color:#11151a;transform:translateY(-1px)}

.gramiss-cart-service-rail{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border:1px solid rgba(17,21,26,.08);border-radius:18px;background:rgba(255,255,255,.72);overflow:hidden}
.gramiss-cart-service-rail>div{min-height:92px;padding:18px 14px;display:grid;grid-template-columns:34px 1fr;column-gap:9px;align-content:center;border-left:1px solid rgba(17,21,26,.07)}
.gramiss-cart-service-rail>div:last-child{border-left:0}
.gramiss-cart-service-rail>div>span{grid-row:1/3;width:34px;height:34px;border-radius:50%;display:grid;place-items:center;background:#f1e8dc;color:#a27d59;font-size:16px}
.gramiss-cart-service-rail strong,.gramiss-cart-service-rail small{display:block}.gramiss-cart-service-rail strong{font-size:10px;color:#32373e}.gramiss-cart-service-rail small{margin-top:3px;color:#92969d;font-size:8px;line-height:1.7}
.gramiss-cart-safe{position:relative;min-height:104px;padding:22px 28px;border:1px solid #e4d5c5;border-radius:19px;display:flex;align-items:center;gap:16px;background:linear-gradient(105deg,#fbf4eb 0%,#f7ede1 58%,#fbf8f3 100%);overflow:hidden}
.gramiss-cart-safe::after{content:"";position:absolute;left:-3%;bottom:-40px;width:52%;height:100px;border-radius:50%;border:1px solid rgba(169,129,89,.13);box-shadow:0 -10px 0 rgba(169,129,89,.04),0 -20px 0 rgba(169,129,89,.025);transform:rotate(-5deg)}
.gramiss-cart-safe__badge{position:relative;z-index:1;flex:0 0 54px;width:54px;height:54px;border-radius:50%;display:grid;place-items:center;background:#171b20;color:#f2dfc8;font-size:22px;box-shadow:0 9px 20px rgba(17,21,26,.18)}
.gramiss-cart-safe>span:last-child{position:relative;z-index:1}.gramiss-cart-safe strong,.gramiss-cart-safe small{display:block}.gramiss-cart-safe strong{font-size:13px}.gramiss-cart-safe small{margin-top:6px;color:#777b82;font-size:9px}

body.woocommerce-cart .woocommerce-message,body.woocommerce-cart .woocommerce-info{grid-column:1/-1;border:1px solid rgba(17,21,26,.09)!important;border-radius:14px!important;background:#fff!important;box-shadow:0 10px 24px rgba(17,21,26,.04)!important}

@media(max-width:1120px){body.woocommerce-cart .woocommerce{grid-template-columns:1fr;grid-template-areas:"notice" "perks" "form" "totals" "services" "safe"}.gramiss-cart-perks{grid-template-columns:1fr 1fr 1fr}body.woocommerce-cart .cart-collaterals .cart_totals{position:static}.gramiss-cart-service-rail{grid-template-columns:1fr 1fr}}
@media(max-width:780px){body.woocommerce-cart .content-area{width:min(calc(100% - 28px),1460px);margin-bottom:70px}body.woocommerce-cart article.page{padding-top:28px}body.woocommerce-cart article.page>h1{margin-bottom:22px;font-size:34px}.gramiss-cart-perks{grid-template-columns:1fr;padding:10px 14px}.gramiss-cart-perk{justify-content:flex-start;min-height:46px}body.woocommerce-cart table.shop_table{display:block;border-radius:18px!important}body.woocommerce-cart table.shop_table thead{display:none}body.woocommerce-cart table.shop_table tbody,body.woocommerce-cart table.shop_table tr{display:block}body.woocommerce-cart table.shop_table tr.cart_item{position:relative;padding:16px 14px 18px;display:grid;grid-template-columns:92px 1fr;grid-template-areas:"thumb name" "thumb price" "qty subtotal";gap:10px 13px;border-bottom:1px solid rgba(17,21,26,.08)}body.woocommerce-cart table.shop_table tr.cart_item td{display:block!important;width:auto!important;min-width:0!important;padding:0!important;border:0!important;text-align:right!important}body.woocommerce-cart td.product-thumbnail{grid-area:thumb}body.woocommerce-cart td.product-thumbnail a{width:92px;height:110px;border-radius:14px}body.woocommerce-cart td.product-name{grid-area:name;font-size:13px!important;padding-left:34px!important}body.woocommerce-cart td.product-price{grid-area:price;color:#666d75!important}body.woocommerce-cart td.product-quantity{grid-area:qty}body.woocommerce-cart td.product-subtotal{grid-area:subtotal;text-align:left!important;align-self:center}body.woocommerce-cart td.product-remove{position:absolute!important;top:15px;left:14px}body.woocommerce-cart td.product-remove a.remove{width:30px!important;height:30px!important;font-size:17px!important}body.woocommerce-cart table.shop_table tr:not(.cart_item){display:block}body.woocommerce-cart table.shop_table td.actions{display:flex!important;flex-direction:column;gap:10px;padding:14px!important}body.woocommerce-cart td.actions .coupon{width:100%;display:grid!important;grid-template-columns:1fr auto;float:none!important}body.woocommerce-cart td.actions .coupon #coupon_code{width:100%!important}body.woocommerce-cart td.actions>button[name="update_cart"]{width:100%;float:none!important}.gramiss-cart-service-rail{grid-template-columns:1fr 1fr}.gramiss-cart-service-rail>div{border-bottom:1px solid rgba(17,21,26,.07)}.gramiss-cart-safe{padding:18px}.gramiss-cart-safe__badge{flex-basis:46px;width:46px;height:46px}body.woocommerce-cart .cart-collaterals .cart_totals{padding:22px 18px}}
@media(max-width:520px){.gramiss-cart-service-rail{grid-template-columns:1fr}.gramiss-cart-service-rail>div{border-left:0}.gramiss-cart-perk small,.gramiss-cart-service-rail small{display:none}}
CSS;

    $js = <<<'JS'
(function(){
  function enhanceCart(){
    document.querySelectorAll('body.woocommerce-cart td.product-quantity .quantity').forEach(function(quantity){
      if(quantity.parentElement && quantity.parentElement.classList.contains('gramiss-qty')) return;
      var input=quantity.querySelector('input.qty');
      if(!input) return;
      var wrap=document.createElement('div'); wrap.className='gramiss-qty';
      var minus=document.createElement('button'); minus.type='button'; minus.className='gramiss-qty-minus'; minus.setAttribute('aria-label','کاهش تعداد'); minus.textContent='−';
      var plus=document.createElement('button'); plus.type='button'; plus.className='gramiss-qty-plus'; plus.setAttribute('aria-label','افزایش تعداد'); plus.textContent='+';
      quantity.parentNode.insertBefore(wrap,quantity); wrap.appendChild(minus); wrap.appendChild(quantity); wrap.appendChild(plus);
      function change(delta){
        var step=parseFloat(input.step)||1, min=input.min!==''?parseFloat(input.min):0, max=input.max!==''?parseFloat(input.max):Infinity, value=parseFloat(input.value)||0;
        value=Math.min(max,Math.max(min,value+(delta*step)));
        input.value=value; input.dispatchEvent(new Event('change',{bubbles:true}));
        var update=document.querySelector('button[name="update_cart"]'); if(update){update.disabled=false; update.removeAttribute('disabled');}
      }
      minus.addEventListener('click',function(){change(-1)}); plus.addEventListener('click',function(){change(1)});
    });
    var coupon=document.getElementById('coupon_code'); if(coupon) coupon.setAttribute('placeholder','کد تخفیف خود را وارد کنید');
  }
  document.addEventListener('DOMContentLoaded',enhanceCart);
  if(window.jQuery){window.jQuery(document.body).on('updated_wc_div',enhanceCart);}
})();
JS;

    wp_add_inline_style( 'gramiss-v1', $css );
    wp_add_inline_script( 'gramiss-v1', $js, 'after' );
}
add_action( 'wp_enqueue_scripts', 'gramiss_premium_cart_assets', 40 );
