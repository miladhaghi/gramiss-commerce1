<?php
/** Site footer. @package Gramiss */
defined( 'ABSPATH' ) || exit;
?>
<footer class="site-footer" id="about">
    <div class="gramiss-container">
        <div class="footer-grid">
            <div class="footer-brand"><div class="footer-wordmark">GRAMISS</div><p class="footer-copy">فروشگاهی برای انتخاب پوشاک با اطلاعات واقعی، مسیر کوتاه و تجربه‌ای بدون فشار.</p></div>
            <div class="footer-column"><h3>فروشگاه</h3><ul><li><a href="<?php echo esc_url( function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' ) ); ?>">همه محصولات</a></li><li><a href="<?php echo esc_url( home_url( '/product-category/caps/' ) ); ?>">کلاه</a></li><li><a href="<?php echo esc_url( home_url( '/product-category/bags/' ) ); ?>">کیف</a></li></ul></div>
            <div class="footer-column"><h3>حساب</h3><ul><li><a href="<?php echo esc_url( function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'myaccount' ) : home_url( '/my-account/' ) ); ?>">حساب من</a></li><li><a href="<?php echo esc_url( function_exists( 'wc_get_cart_url' ) ? wc_get_cart_url() : home_url( '/cart/' ) ); ?>">سبد خرید</a></li><li><a href="<?php echo esc_url( function_exists( 'wc_get_checkout_url' ) ? wc_get_checkout_url() : home_url( '/checkout/' ) ); ?>">تسویه حساب</a></li></ul></div>
            <div class="footer-column"><h3>راهنما</h3><ul><li><a href="<?php echo esc_url( home_url( '/contact/' ) ); ?>">تماس با ما</a></li><li><a href="<?php echo esc_url( home_url( '/shipping/' ) ); ?>">ارسال سفارش</a></li><li><a href="<?php echo esc_url( home_url( '/returns/' ) ); ?>">تعویض و مرجوعی</a></li></ul></div>
        </div>
        <div class="footer-bottom"><span>© <?php echo esc_html( wp_date( 'Y' ) ); ?> Gramiss</span><span>طراحی و توسعه اختصاصی</span></div>
    </div>
</footer>
<?php wp_footer(); ?>
</body>
</html>
