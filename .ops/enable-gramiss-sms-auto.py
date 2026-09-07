#!/usr/bin/env python3
import json, time, importlib.util
from pathlib import Path

helper_path = Path(__file__).with_name('performance-pdp-image-request-fix-v4.py')
spec = importlib.util.spec_from_file_location('gramiss_cpanel_helper', helper_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def main():
    name = 'gramiss-sms-auto-enable-' + str(int(time.time())) + '.php'
    php = r'''<?php
header('Content-Type: application/json; charset=utf-8');
require __DIR__ . '/wp-load.php';

$key = 'gramiss_sms_v1_settings';
$settings = get_option($key, array());
$out = array('before' => array(), 'after' => array(), 'ok' => false);
$out['before'] = array(
  'api_key_configured' => !empty($settings['api_key']),
  'template_id' => isset($settings['template_id']) ? (string)$settings['template_id'] : '',
  'parameter_name' => isset($settings['parameter_name']) ? (string)$settings['parameter_name'] : '',
  'gateway_id' => isset($settings['gateway_id']) ? (string)$settings['gateway_id'] : '',
  'auto_enabled' => isset($settings['auto_enabled']) ? (string)$settings['auto_enabled'] : '',
);

if (empty($settings['api_key'])) { http_response_code(409); $out['error']='API key missing'; }
elseif ((string)($settings['template_id'] ?? '') !== '761339') { http_response_code(409); $out['error']='Unexpected template'; }
elseif ((string)($settings['parameter_name'] ?? '') !== 'ORDER_NUMBER') { http_response_code(409); $out['error']='Unexpected parameter'; }
elseif ((string)($settings['gateway_id'] ?? '') !== 'gramiss_card_transfer') { http_response_code(409); $out['error']='Unexpected gateway'; }
else {
  $settings['auto_enabled'] = '1';
  update_option($key, $settings, false);
  $check = get_option($key, array());
  $out['after'] = array(
    'api_key_configured' => !empty($check['api_key']),
    'template_id' => isset($check['template_id']) ? (string)$check['template_id'] : '',
    'parameter_name' => isset($check['parameter_name']) ? (string)$check['parameter_name'] : '',
    'gateway_id' => isset($check['gateway_id']) ? (string)$check['gateway_id'] : '',
    'auto_enabled' => isset($check['auto_enabled']) ? (string)$check['auto_enabled'] : '',
  );
  $out['ok'] = ($out['after']['auto_enabled'] === '1');
  if (!$out['ok']) http_response_code(500);
}
@unlink(__FILE__);
echo wp_json_encode($out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
?>'''
    mod.save_root(name, php)
    status, body = mod.get(mod.BASE + '/' + name + '?t=' + str(time.time()), 180)
    print('HTTP', status)
    print(body)
    data = json.loads(body)
    if status != 200 or not data.get('ok') or data.get('after', {}).get('auto_enabled') != '1':
        raise SystemExit('auto enable failed')

if __name__ == '__main__':
    main()
