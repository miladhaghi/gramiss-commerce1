<?php
/** GRAMISS_HOME_LOOKS_SURGICAL_V2 */
if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

$g1_theme_uri = get_stylesheet_directory_uri();
$g1_shop_url  = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );

$g1_product_data = static function ( $product_id, $reason ) {
    if ( ! function_exists( 'wc_get_product' ) ) {
        return null;
    }

    $product = wc_get_product( $product_id );
    if ( ! $product ) {
        return null;
    }

    return array(
        'id'     => $product_id,
        'name'   => $product->get_name(),
        'url'    => get_permalink( $product_id ),
        'price'  => $product->get_price_html(),
        'stock'  => $product->is_in_stock() ? 'موجود' : 'ناموجود',
        'sku'    => $product->get_sku() ? $product->get_sku() : 'GMS-' . $product_id,
        'reason' => $reason,
    );
};

$g1_look_2_spots = array(
    array( 'key' => 'cap',   'label' => 'کلاه فیت کپ', 'x' => '30%', 'y' => '10%', 'soon' => true ),
    array( 'key' => 'tee',   'label' => 'تیشرت',       'x' => '21%', 'y' => '34%', 'product' => $g1_product_data( 392, 'فرم باکسی + واش وینتیج؛ پایه‌ی اصلی استایل خیابانی.' ) ),
    array( 'key' => 'pants', 'label' => 'شلوار',       'x' => '24%', 'y' => '65%', 'product' => $g1_product_data( 284, 'فرم بگ کارگو + حجم کنترل‌شده؛ مناسب ترکیب با بالاتنه باکسی.' ) ),
    array( 'key' => 'shoes', 'label' => 'کتونی',       'x' => '23%', 'y' => '92%', 'product' => $g1_product_data( 435, 'فرم Chunky و حجیم؛ تعادل بصری مناسب برای شلوار بگ.' ) ),
);

$g1_look_1_spots = array(
    array( 'key' => 'shirt', 'label' => 'پیراهن', 'x' => '80%', 'y' => '29%', 'product' => $g1_product_data( 350, 'پارچه سیلکی + افت نرم؛ ظاهر تمیز و Relaxed بدون خشکی رسمی.' ) ),
    array( 'key' => 'pants', 'label' => 'شلوار',  'x' => '79%', 'y' => '64%', 'product' => $g1_product_data( 366, 'کرپ لَخت + فرم بگ و قد بلند؛ حجم نرم و مرتب روی کتونی.' ) ),
    array( 'key' => 'shoes', 'label' => 'کتونی',  'x' => '78%', 'y' => '92%', 'product' => $g1_product_data( 403, 'لژ ملایم + فرم تمیز؛ هماهنگ با شلوار روشن و استایل Old Money.' ) ),
);

$g1_render_spots = static function ( $spots, $look_key ) {
    foreach ( $spots as $index => $spot ) {
        $card_id = 'g1-look-card-' . $look_key . '-' . $spot['key'];
        $is_soon = ! empty( $spot['soon'] );
        $product = isset( $spot['product'] ) ? $spot['product'] : null;
        ?>
        <div class="g1-looks__spot g1-looks__spot--<?php echo esc_attr( $spot['key'] ); ?>" style="--spot-x:<?php echo esc_attr( $spot['x'] ); ?>;--spot-y:<?php echo esc_attr( $spot['y'] ); ?>;" data-g1-look-spot>
            <button class="g1-looks__hotspot" type="button" aria-expanded="false" aria-controls="<?php echo esc_attr( $card_id ); ?>" aria-label="<?php echo esc_attr( 'مشاهده ' . $spot['label'] ); ?>">
                <span aria-hidden="true"></span>
            </button>
            <div class="g1-looks__product-card product-card<?php echo $is_soon ? ' is-soon' : ''; ?>" id="<?php echo esc_attr( $card_id ); ?>" role="status">
                <?php if ( $is_soon || ! $product ) : ?>
                    <span class="g1-looks__card-kicker">SOON</span>
                    <strong><?php echo esc_html( $spot['label'] ); ?></strong>
                    <p>این آیتم به‌زودی به فروشگاه اضافه می‌شود.</p>
                <?php else : ?>
                    <div class="g1-looks__card-top">
                        <span class="g1-looks__card-kicker"><?php echo esc_html( $product['sku'] ); ?></span>
                        <span class="g1-looks__stock<?php echo 'موجود' === $product['stock'] ? ' is-in' : ' is-out'; ?>"><?php echo esc_html( $product['stock'] ); ?></span>
                    </div>
                    <strong><?php echo esc_html( $product['name'] ); ?></strong>
                    <div class="g1-looks__price"><?php echo wp_kses_post( $product['price'] ); ?></div>
                    <p><b>چرا این انتخاب؟</b> <?php echo esc_html( $product['reason'] ); ?></p>
                    <a href="<?php echo esc_url( $product['url'] ); ?>">مشاهده محصول <span aria-hidden="true">↗</span></a>
                <?php endif; ?>
            </div>
        </div>
        <?php
    }
};
?>

<link rel="stylesheet" href="<?php echo esc_url( $g1_theme_uri . '/assets/css/home-looks.css?v=2.0.0' ); ?>">

<section class="g1-looks g1-reveal" id="gramiss-looks" data-g1-looks aria-labelledby="g1-looks-title">
    <div class="g1-looks__ambient g1-looks__ambient--left" aria-hidden="true"></div>
    <div class="g1-looks__ambient g1-looks__ambient--right" aria-hidden="true"></div>

    <div class="g1-looks__scene">
        <article class="g1-looks__look g1-looks__look--street" aria-label="Look 02 — Street / Relaxed">
            <div class="g1-looks__look-label" dir="ltr">
                <span>LOOK 02</span>
                <b>STREET / RELAXED</b>
            </div>
            <div class="g1-looks__model-stage">
                <img src="<?php echo esc_url( $g1_theme_uri . '/assets/images/home/gramiss-look-02.webp?v=2.1.0' ); ?>" width="1024" height="1536" loading="lazy" decoding="async" alt="استایل خیابانی Gramiss با تیشرت باکسی، شلوار بگ، کتونی و کلاه">
                <?php $g1_render_spots( $g1_look_2_spots, 'street' ); ?>
            </div>
        </article>

        <div class="g1-looks__intro">
            <span class="g1-looks__eyebrow" dir="ltr">GRAMISS LOOKS / 01</span>
            <h2 id="g1-looks-title">استایل را لمس کن.</h2>
            <p>هر نقطه یک محصول واقعی از فروشگاه است. روی آیتم برو یا لمسش کن تا قیمت و موجودی را ببینی و مستقیم وارد همان محصول شوی.</p>
            <a class="g1-looks__cta" href="<?php echo esc_url( $g1_shop_url ); ?>">مشاهده فروشگاه <span aria-hidden="true">↗</span></a>
            <div class="g1-looks__legend" aria-hidden="true"><i></i><span>روی نقاط محصول برو</span></div>
        </div>

        <article class="g1-looks__look g1-looks__look--oldmoney" aria-label="Look 01 — Clean / Old Money">
            <div class="g1-looks__look-label" dir="ltr">
                <span>LOOK 01</span>
                <b>CLEAN / OLD MONEY</b>
            </div>
            <div class="g1-looks__model-stage">
                <img src="<?php echo esc_url( $g1_theme_uri . '/assets/images/home/gramiss-look-01.webp?v=2.1.0' ); ?>" width="1024" height="1536" loading="lazy" decoding="async" alt="استایل Old Money گرمیس با پیراهن آبی، شلوار کرم و کتونی سرمه‌ای">
                <?php $g1_render_spots( $g1_look_1_spots, 'oldmoney' ); ?>
            </div>
        </article>
    </div>
</section>

<script src="<?php echo esc_url( $g1_theme_uri . '/assets/js/home-looks.js?v=2.0.0' ); ?>" defer></script>
