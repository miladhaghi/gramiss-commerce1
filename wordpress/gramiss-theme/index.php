<?php
/**
 * Main template.
 *
 * @package Gramiss
 */

defined( 'ABSPATH' ) || exit;

get_header();
?>
<main id="primary" class="gramiss-main">
    <?php if ( have_posts() ) : ?>
        <?php while ( have_posts() ) : ?>
            <?php the_post(); ?>
            <article id="post-<?php the_ID(); ?>" <?php post_class( 'gramiss-entry' ); ?>>
                <?php the_content(); ?>
            </article>
        <?php endwhile; ?>

        <?php the_posts_pagination(); ?>
    <?php else : ?>
        <p><?php esc_html_e( 'محتوایی پیدا نشد.', 'gramiss' ); ?></p>
    <?php endif; ?>
</main>
<?php
get_footer();
