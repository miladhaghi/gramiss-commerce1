<?php
defined( 'ABSPATH' ) || exit;
get_header();
?>
<main id="primary" class="content-area">
<?php while ( have_posts() ) : the_post(); ?>
    <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>><h1><?php the_title(); ?></h1><?php the_content(); ?></article>
<?php endwhile; ?>
</main>
<?php get_footer(); ?>
