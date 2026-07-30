<?php
/**
 * Gramiss WooCommerce shop and product-category archive.
 *
 * @package Gramiss
 */

defined( 'ABSPATH' ) || exit;

get_header();

$shop_url        = function_exists( 'wc_get_page_permalink' ) ? wc_get_page_permalink( 'shop' ) : home_url( '/shop/' );
$current_orderby = isset( $_GET['orderby'] ) ? wc_clean( wp_unslash( $_GET['orderby'] ) ) : 'date';
$current_cat     = isset( $_GET['product_cat'] ) ? sanitize_title( wp_unslash( $_GET['product_cat'] ) ) : '';
$categories      = get_terms(
    array(
        'taxonomy'   => 'product_cat',
        'hide_empty' => true,
        'parent'     => 0,
        'number'     => 12,
    )
);
if ( is_wp_error( $categories ) ) {
    $categories = array();
}

$filter_taxonomies = array(
    'color'    => array( 'taxonomy' => 'pa_color', 'title' => 'رنگ', 'summary' => 'رنگ‌های موجود' ),
    'size'     => array( 'taxonomy' => 'pa_size', 'title' => 'سایز', 'summary' => 'S، M، L، XL' ),
    'material' => array( 'taxonomy' => 'pa_material', 'title' => 'جنس', 'summary' => 'جنس و بافت محصول' ),
);

$active_filter_count = 0;
foreach ( array( 'product_cat', 'min_price', 'max_price', 'filter_color', 'filter_size', 'filter_material', 'in_stock', 'on_sale' ) as $filter_key ) {
    if ( ! empty( $_GET[ $filter_key ] ) ) {
        ++$active_filter_count;
    }
}

function gramiss_render_shop_filters( string $instance, array $categories, array $filter_taxonomies, string $shop_url ): void {
    $selected_cat = isset( $_GET['product_cat'] ) ? sanitize_title( wp_unslash( $_GET['product_cat'] ) ) : '';
    $min_price    = isset( $_GET['min_price'] ) ? absint( $_GET['min_price'] ) : '';
    $max_price    = isset( $_GET['max_price'] ) ? absint( $_GET['max_price'] ) : '';
    $orderby      = isset( $_GET['orderby'] ) ? wc_clean( wp_unslash( $_GET['orderby'] ) ) : 'date';
    ?>
    <form class="shop-filter-panel <?php echo 'mobile' === $instance ? 'is-mobile' : ''; ?>" method="get" action="<?php echo esc_url( $shop_url ); ?>" dir="rtl">
        <div class="shop-filter-title">
            <h2><?php echo 'mobile' === $instance ? esc_html__( 'فیلتر محصولات', 'gramiss' ) : esc_html__( 'فیلترها', 'gramiss' ); ?></h2>
            <a href="<?php echo esc_url( $shop_url ); ?>"><?php esc_html_e( 'پاک کردن همه', 'gramiss' ); ?></a>
        </div>

        <section class="shop-filter-section is-open">
            <button type="button" class="shop-filter-heading" aria-expanded="true"><span><?php esc_html_e( 'دسته‌بندی', 'gramiss' ); ?></span><span aria-hidden="true">⌄</span></button>
            <p class="shop-filter-summary"><?php esc_html_e( 'محصولات را براساس دسته محدود کن', 'gramiss' ); ?></p>
            <div class="shop-filter-options"><div class="shop-filter-choice-list">
                <?php foreach ( $categories as $category ) : ?>
                    <label><input type="radio" name="product_cat" value="<?php echo esc_attr( $category->slug ); ?>" <?php checked( $selected_cat, $category->slug ); ?>><span><?php echo esc_html( $category->name ); ?></span></label>
                <?php endforeach; ?>
            </div></div>
        </section>

        <section class="shop-filter-section is-open">
            <button type="button" class="shop-filter-heading" aria-expanded="true"><span><?php esc_html_e( 'محدوده قیمت', 'gramiss' ); ?></span><span aria-hidden="true">⌄</span></button>
            <p class="shop-filter-summary"><?php esc_html_e( 'قیمت را به تومان وارد کن', 'gramiss' ); ?></p>
            <div class="shop-filter-options"><div class="shop-price-fields">
                <label><span><?php esc_html_e( 'از', 'gramiss' ); ?></span><input type="number" name="min_price" min="0" step="10000" value="<?php echo esc_attr( $min_price ); ?>" placeholder="۵۰۰۰۰۰"></label>
                <label><span><?php esc_html_e( 'تا', 'gramiss' ); ?></span><input type="number" name="max_price" min="0" step="10000" value="<?php echo esc_attr( $max_price ); ?>" placeholder="۵۰۰۰۰۰۰"></label>
            </div></div>
        </section>

        <?php foreach ( $filter_taxonomies as $filter_key => $config ) : ?>
            <?php
            if ( ! taxonomy_exists( $config['taxonomy'] ) ) { continue; }
            $terms = get_terms( array( 'taxonomy' => $config['taxonomy'], 'hide_empty' => true, 'number' => 16 ) );
            if ( is_wp_error( $terms ) || empty( $terms ) ) { continue; }
            $query_key = 'filter_' . $filter_key;
            $selected  = isset( $_GET[ $query_key ] ) ? array_map( 'sanitize_title', (array) wp_unslash( $_GET[ $query_key ] ) ) : array();
            ?>
            <section class="shop-filter-section">
                <button type="button" class="shop-filter-heading" aria-expanded="false"><span><?php echo esc_html( $config['title'] ); ?></span><span aria-hidden="true">⌄</span></button>
                <p class="shop-filter-summary"><?php echo esc_html( $config['summary'] ); ?></p>
                <div class="shop-filter-options" hidden><div class="<?php echo 'size' === $filter_key ? 'shop-size-choices' : 'shop-filter-choice-list'; ?>">
                    <?php foreach ( $terms as $term ) : ?>
                        <label><input type="checkbox" name="<?php echo esc_attr( $query_key ); ?>[]" value="<?php echo esc_attr( $term->slug ); ?>" <?php checked( in_array( $term->slug, $selected, true ) ); ?>><span><?php echo esc_html( $term->name ); ?></span></label>
                    <?php endforeach; ?>
                </div></div>
            </section>
        <?php endforeach; ?>

        <section class="shop-filter-section is-open">
            <button type="button" class="shop-filter-heading" aria-expanded="true"><span><?php esc_html_e( 'وضعیت', 'gramiss' ); ?></span><span aria-hidden="true">⌄</span></button>
            <p class="shop-filter-summary"><?php esc_html_e( 'موجودی و تخفیف', 'gramiss' ); ?></p>
            <div class="shop-filter-options">
                <label class="shop-filter-switch"><input type="checkbox" name="in_stock" value="1" <?php checked( ! empty( $_GET['in_stock'] ) ); ?>><span><?php esc_html_e( 'فقط کالاهای موجود', 'gramiss' ); ?></span></label>
                <label class="shop-filter-switch"><input type="checkbox" name="on_sale" value="1" <?php checked( ! empty( $_GET['on_sale'] ) ); ?>><span><?php esc_html_e( 'فقط محصولات تخفیف‌دار', 'gramiss' ); ?></span></label>
            </div>
        </section>

        <input type="hidden" name="orderby" value="<?php echo esc_attr( $orderby ); ?>">
        <button class="shop-filter-apply" type="submit"><?php esc_html_e( 'اعمال فیلترها', 'gramiss' ); ?></button>
    </form>
    <?php
}

function gramiss_render_shop_product_card( WC_Product $product ): void {
    $product_id = $product->get_id();
    $categories = wc_get_product_category_list( $product_id, '، ' );
    $english    = $product->get_sku() ? $product->get_sku() : strtoupper( str_replace( '-', ' ', $product->get_slug() ) );
    $is_new     = strtotime( $product->get_date_created() ? $product->get_date_created()->date( 'Y-m-d' ) : '2000-01-01' ) > strtotime( '-30 days' );
    $badge      = $product->is_on_sale() ? 'تخفیف' : ( $is_new ? 'جدید' : '' );
    $ajax       = $product->supports( 'ajax_add_to_cart' ) && $product->is_purchasable() && $product->is_in_stock();
    $add_url    = $ajax ? $product->add_to_cart_url() : $product->get_permalink();
    $add_label  = $ajax ? 'افزودن' : 'انتخاب';
    ?>
    <article class="shop-product-card" data-product-id="<?php echo esc_attr( $product_id ); ?>" dir="rtl">
        <a class="shop-product-media" href="<?php echo esc_url( $product->get_permalink() ); ?>" aria-label="<?php echo esc_attr( sprintf( 'مشاهده %s', $product->get_name() ) ); ?>">
            <?php if ( $badge ) : ?><span class="shop-product-badge"><?php echo esc_html( $badge ); ?></span><?php endif; ?>
            <span class="shop-artwork shop-artwork-cap"><?php echo wp_kses_post( $product->get_image( 'woocommerce_thumbnail', array( 'loading' => 'lazy' ) ) ); ?></span>
        </a>
        <button class="shop-wishlist" type="button" data-gramiss-wishlist="<?php echo esc_attr( $product_id ); ?>" aria-label="افزودن به علاقه‌مندی‌ها" aria-pressed="false"><svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8Z"/></svg></button>
        <button class="shop-compare" type="button" data-gramiss-compare="<?php echo esc_attr( $product_id ); ?>" aria-label="افزودن به مقایسه" aria-pressed="false"><svg aria-hidden="true" width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M4 7h11M4 17h16M15 4l3 3-3 3M9 14l-3 3 3 3"/></svg></button>
        <a class="shop-product-copy" href="<?php echo esc_url( $product->get_permalink() ); ?>"><span><?php echo $categories ? wp_kses_post( $categories ) : esc_html__( 'محصول Gramiss', 'gramiss' ); ?></span><strong><?php echo esc_html( $product->get_name() ); ?></strong><small dir="ltr"><?php echo esc_html( $english ); ?></small></a>
        <div class="shop-product-buy"><b><?php echo wp_kses_post( $product->get_price_html() ); ?></b><a class="shop-add-button <?php echo $ajax ? 'add_to_cart_button ajax_add_to_cart' : ''; ?>" href="<?php echo esc_url( $add_url ); ?>" data-quantity="1" data-product_id="<?php echo esc_attr( $product_id ); ?>" data-product_sku="<?php echo esc_attr( $product->get_sku() ); ?>" rel="nofollow"><?php echo esc_html( $add_label ); ?></a></div>
    </article>
    <?php
}

function gramiss_render_shop_sample_cards(): void {
    $samples = array(
        array( 'product-shoe.png', 'کتونی روزمره', 'DAILY SNEAKER', 'کتونی', '۲٬۹۸۰٬۰۰۰ تومان', 'جدید' ),
        array( 'product-shirt.png', 'تیشرت اسنشال', 'ESSENTIAL T-SHIRT', 'تیشرت', '۱٬۲۸۰٬۰۰۰ تومان', '' ),
        array( 'product-cap.png', 'کلاه آبی آسمانی', 'SKY BLUE CAP', 'کلاه', '۹۸۰٬۰۰۰ تومان', 'منتخب' ),
        array( 'product-bag.png', 'کیف کراس‌بادی', 'CROSSBODY BAG', 'کیف', '۲٬۴۸۰٬۰۰۰ تومان', '' ),
        array( 'product-shirt.png', 'تیشرت مینیمال مشکی', 'BLACK MINIMAL TEE', 'تیشرت', '۱٬۳۹۰٬۰۰۰ تومان', '' ),
        array( 'product-shoe.png', 'کتونی شهری خاکستری', 'URBAN GREY SNEAKER', 'کتونی', '۳٬۲۸۰٬۰۰۰ تومان', 'جدید' ),
    );
    foreach ( $samples as $index => $sample ) : ?>
        <article class="shop-product-card is-demo" dir="rtl"><span class="shop-product-media"><?php if ( $sample[5] ) : ?><span class="shop-product-badge"><?php echo esc_html( $sample[5] ); ?></span><?php endif; ?><span class="shop-artwork shop-artwork-cap"><img src="<?php echo esc_url( gramiss_asset( $sample[0] ) ); ?>" alt="<?php echo esc_attr( $sample[1] ); ?>" loading="lazy"></span></span><button class="shop-wishlist" type="button" data-gramiss-wishlist="demo-<?php echo esc_attr( $index ); ?>" aria-label="افزودن به علاقه‌مندی‌ها" aria-pressed="false">♡</button><button class="shop-compare" type="button" data-gramiss-compare="demo-<?php echo esc_attr( $index ); ?>" aria-label="افزودن به مقایسه" aria-pressed="false">⇄</button><span class="shop-product-copy"><span><?php echo esc_html( $sample[3] ); ?></span><strong><?php echo esc_html( $sample[1] ); ?></strong><small dir="ltr"><?php echo esc_html( $sample[2] ); ?></small></span><div class="shop-product-buy"><b><?php echo esc_html( $sample[4] ); ?></b><span class="shop-add-button is-disabled">نمونه</span></div></article>
    <?php endforeach;
}
?>
<main class="shop-page" id="top" data-node-id="30:2">
<section class="shop-intro" aria-labelledby="shop-title"><div class="shop-intro-copy" dir="rtl"><p class="shop-kicker" dir="ltr">SHOP / COLLECTION</p><h1 id="shop-title"><?php woocommerce_page_title(); ?></h1><p>محصولات منتخب <bdi dir="ltr">Gramiss</bdi> با تمرکز بر کیفیت، دوام و استایل روزمره.</p></div><nav class="shop-breadcrumb" aria-label="مسیر صفحه" dir="rtl"><a href="<?php echo esc_url( home_url( '/' ) ); ?>">خانه</a><span aria-hidden="true">/</span><span aria-current="page">فروشگاه</span></nav></section>
<section class="shop-quick-categories" aria-labelledby="quick-title"><h2 id="quick-title">دسته‌بندی سریع</h2><div class="shop-quick-scroll" aria-label="فیلتر سریع دسته‌بندی‌ها"><a class="<?php echo '' === $current_cat ? 'is-active' : ''; ?>" href="<?php echo esc_url( $shop_url ); ?>">همه</a><?php foreach ( array_slice( $categories, 0, 7 ) as $category ) : ?><a class="<?php echo $current_cat === $category->slug ? 'is-active' : ''; ?>" href="<?php echo esc_url( add_query_arg( 'product_cat', $category->slug, $shop_url ) ); ?>"><?php echo esc_html( $category->name ); ?></a><?php endforeach; ?><?php if ( empty( $categories ) ) : foreach ( array( 'کتونی', 'تیشرت', 'کلاه', 'کیف', 'جوراب' ) as $label ) : ?><span><?php echo esc_html( $label ); ?></span><?php endforeach; endif; ?></div></section>
<section class="shop-catalog" aria-label="محصولات فروشگاه"><div class="shop-catalog-toolbar"><p class="shop-product-count" role="status" dir="rtl"><?php echo esc_html( sprintf( '%s محصول', number_format_i18n( (int) wc_get_loop_prop( 'total' ) ) ) ); ?></p><div class="shop-desktop-controls"><form class="shop-sort" method="get" action="<?php echo esc_url( $shop_url ); ?>"><select name="orderby" aria-label="مرتب‌سازی محصولات" onchange="this.form.submit()"><option value="date" <?php selected( $current_orderby, 'date' ); ?>>مرتب‌سازی: جدیدترین</option><option value="price" <?php selected( $current_orderby, 'price' ); ?>>قیمت: کم به زیاد</option><option value="price-desc" <?php selected( $current_orderby, 'price-desc' ); ?>>قیمت: زیاد به کم</option><option value="popularity" <?php selected( $current_orderby, 'popularity' ); ?>>محبوب‌ترین</option></select><span aria-hidden="true">⌄</span></form><div class="shop-grid-toggle" aria-label="تعداد ستون‌های محصولات"><button type="button" class="is-active" data-grid="3" aria-label="نمای سه ستونه" aria-pressed="true">▦</button><button type="button" data-grid="4" aria-label="نمای چهار ستونه" aria-pressed="false">▦</button></div></div><div class="shop-mobile-controls"><form class="shop-sort is-mobile" method="get" action="<?php echo esc_url( $shop_url ); ?>"><select name="orderby" aria-label="مرتب‌سازی محصولات" onchange="this.form.submit()"><option value="date">جدیدترین</option><option value="price">ارزان‌ترین</option><option value="price-desc">گران‌ترین</option></select><span aria-hidden="true">⌄</span></form><button type="button" class="shop-mobile-filter-trigger" aria-haspopup="dialog" aria-expanded="false"><span aria-hidden="true">☷</span><span>فیلتر<?php echo $active_filter_count ? ' (' . esc_html( $active_filter_count ) . ')' : ''; ?></span></button></div></div><div class="shop-catalog-layout"><aside class="shop-desktop-filter" aria-label="فیلتر محصولات"><?php gramiss_render_shop_filters( 'desktop', $categories, $filter_taxonomies, $shop_url ); ?></aside><div class="shop-results"><div class="shop-active-filters" dir="rtl"><h2>فیلترهای فعال</h2><div class="shop-active-filter-list"><?php if ( $active_filter_count ) : ?><span class="shop-active-filter-chip is-primary"><?php echo esc_html( sprintf( '%d فیلتر فعال', $active_filter_count ) ); ?></span><a class="shop-active-filter-chip clear-all" href="<?php echo esc_url( $shop_url ); ?>">حذف همه</a><?php else : ?><span class="shop-no-active-filter">بدون فیلتر فعال</span><?php endif; ?></div></div><div class="shop-product-grid columns-3" aria-live="polite"><?php if ( woocommerce_product_loop() ) : while ( have_posts() ) : the_post(); $product = wc_get_product( get_the_ID() ); if ( $product ) { gramiss_render_shop_product_card( $product ); } endwhile; else : gramiss_render_shop_sample_cards(); endif; ?></div></div></div></section>
<section class="shop-smart-cta" aria-labelledby="smart-cta-title"><div dir="rtl"><h2 id="smart-cta-title">هنوز مطمئن نیستی؟</h2><p>به چند سؤال کوتاه پاسخ بده تا <bdi dir="ltr">Gramiss</bdi> مناسب‌ترین گزینه را براساس استایل و نیازت پیشنهاد دهد.</p></div><a class="button button-secondary" href="<?php echo esc_url( home_url( '/#journal' ) ); ?>">شروع راهنمای هوشمند</a></section>
<nav class="shop-pagination" aria-label="صفحه‌بندی محصولات"><?php echo wp_kses_post( paginate_links( array( 'total' => max( 1, (int) wc_get_loop_prop( 'total_pages' ) ), 'current' => max( 1, (int) wc_get_loop_prop( 'current_page' ) ), 'prev_text' => '←', 'next_text' => '→', 'type' => 'plain' ) ) ); ?></nav>
<section class="shop-buying-guide" aria-labelledby="guide-cta-title"><div dir="rtl"><h2 id="guide-cta-title">نمی‌دانی چه انتخابی برایت مناسب‌تر است؟</h2><p>راهنماهای خرید <bdi dir="ltr">Gramiss</bdi> درباره جنس، سایز، دوام و استایل به تو کمک می‌کنند مطمئن‌تر انتخاب کنی.</p></div><a class="button button-primary" href="<?php echo esc_url( home_url( '/#journal' ) ); ?>">مشاهده راهنمای خرید</a></section>
<section class="shop-newsletter" id="newsletter"><div class="shop-newsletter-copy" dir="rtl"><h2>به خانواده <bdi dir="ltr">Gramiss</bdi> بپیوند.</h2><p>جدیدترین کالکشن‌ها و راهنماهای استایل را قبل از همه دریافت کن.</p></div><div class="newsletter-form-wrap"><form class="newsletter-form" action="" method="post"><label class="screen-reader-text" for="shop-newsletter-email">ایمیل</label><input id="shop-newsletter-email" name="email" type="email" placeholder="example@email.com" dir="ltr"><button type="submit">عضویت</button></form><p class="newsletter-status">بدون اسپم • لغو اشتراک در هر زمان</p></div></section>
</main>
<div class="shop-filter-overlay" aria-hidden="true"><aside class="filter-drawer" role="dialog" aria-modal="true" aria-labelledby="mobile-filter-title"><div class="filter-drawer-heading"><h2 id="mobile-filter-title">فیلتر محصولات</h2><button class="filter-drawer-close" type="button" aria-label="بستن">×</button></div><?php gramiss_render_shop_filters( 'mobile', $categories, $filter_taxonomies, $shop_url ); ?></aside></div><div class="gramiss-shop-toast" role="status" aria-live="polite"></div>
<?php get_footer(); ?>
