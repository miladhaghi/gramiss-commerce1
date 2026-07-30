<?php
defined( 'ABSPATH' ) || exit;
get_header();
?>
<main id="primary" class="content-area">
<?php while ( have_posts() ) : the_post(); ?><?php wc_get_template_part( 'content', 'single-product' ); ?><?php endwhile; ?>
</main>
<?php get_footer(); ?>
