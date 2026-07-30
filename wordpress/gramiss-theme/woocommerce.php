<?php
/**
 * WooCommerce fallback template.
 *
 * @package Gramiss
 */

defined( 'ABSPATH' ) || exit;

get_header();
?>
<main id="primary" class="gramiss-main gramiss-commerce-main">
    <?php woocommerce_content(); ?>
</main>
<?php
get_footer();
