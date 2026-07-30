<?php
defined( 'ABSPATH' ) || exit;
get_header();
?>
<main id="primary" class="content-area" style="min-height:55vh;display:grid;place-items:center;text-align:center;"><div><p class="latin-label">404</p><h1>این صفحه پیدا نشد</h1><p>آدرس ممکن است تغییر کرده باشد یا صفحه حذف شده باشد.</p><a class="button button-primary" href="<?php echo esc_url( home_url( '/' ) ); ?>">بازگشت به صفحه اصلی</a></div></main>
<?php get_footer(); ?>
