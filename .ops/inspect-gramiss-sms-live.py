#!/usr/bin/env python3
import json, time, importlib.util
from pathlib import Path

helper_path = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_cpanel_helper', helper_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def main():
    name = 'gramiss-sms-inspect-' + str(int(time.time())) + '.php'
    php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
require __DIR__ . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/plugin.php';

$settings = get_option('gramiss_sms_v1_settings', array());
$out = array(
  'plugin_active' => is_plugin_active('gramiss-sms/gramiss-sms.php'),
  'woocommerce' => class_exists('WooCommerce'),
  'settings' => array(
    'api_key_configured' => !empty($settings['api_key']),
    'template_id' => isset($settings['template_id']) ? (string)$settings['template_id'] : '',
    'parameter_name' => isset($settings['parameter_name']) ? (string)$settings['parameter_name'] : '',
    'gateway_id' => isset($settings['gateway_id']) ? (string)$settings['gateway_id'] : '',
    'auto_enabled' => isset($settings['auto_enabled']) ? (string)$settings['auto_enabled'] : '',
  ),
  'gateways' => array(),
  'orders' => array(),
);

if (function_exists('WC') && WC() && WC()->payment_gateways()) {
  foreach (WC()->payment_gateways()->payment_gateways() as $id => $gateway) {
    $out['gateways'][] = array(
      'id' => (string)$id,
      'title' => method_exists($gateway, 'get_title') ? wp_strip_all_tags((string)$gateway->get_title()) : (string)$id,
      'enabled' => isset($gateway->enabled) ? (string)$gateway->enabled : '',
    );
  }
}

if (function_exists('wc_get_orders')) {
  $orders = wc_get_orders(array('limit' => 8, 'orderby' => 'date', 'order' => 'DESC', 'return' => 'objects'));
  foreach ($orders as $order) {
    if (!$order instanceof WC_Order) continue;
    $notes = wc_get_order_notes(array('order_id' => $order->get_id(), 'limit' => 20));
    $sms_notes = array();
    foreach ($notes as $note) {
      $content = isset($note->content) ? (string)$note->content : '';
      if (stripos($content, 'Gramiss SMS') !== false) $sms_notes[] = wp_strip_all_tags($content);
    }
    $out['orders'][] = array(
      'id' => $order->get_id(),
      'status' => $order->get_status(),
      'created_via' => $order->get_created_via(),
      'payment_method' => $order->get_payment_method(),
      'payment_method_title' => $order->get_payment_method_title(),
      'sms_sent_meta' => (bool)$order->get_meta('_gramiss_sms_registration_sent_at', true),
      'sms_notes' => $sms_notes,
    );
  }
}

@unlink(__FILE__);
echo wp_json_encode($out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
?>'''
    mod.save_root(name, php)
    status, body = mod.get(mod.BASE + '/' + name + '?t=' + str(time.time()), 180)
    print('HTTP', status)
    data = json.loads(body)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    if status != 200:
        raise SystemExit('inspect endpoint failed')

if __name__ == '__main__':
    main()
