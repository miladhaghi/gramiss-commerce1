import argparse
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

CTX = ssl._create_unverified_context()
BASE = 'https://gramiss.ir'


def validate(filename, content):
    filename = (filename or '').strip()
    content = (content or '').strip()
    if not re.fullmatch(r'google[A-Za-z0-9_-]{8,200}\.html', filename):
        raise ValueError('invalid Google verification filename')
    expected = 'google-site-verification: ' + filename
    if content != expected:
        raise ValueError('verification content must exactly match Google filename')
    if len(content.encode('utf-8')) > 512:
        raise ValueError('verification content unexpectedly large')
    return filename, content


def api(fn, params, post=False):
    host = os.environ['CPANEL_HOST']
    user = os.environ['CPANEL_USER']
    token = os.environ['CPANEL_TOKEN']
    url = f'https://{host}:2083/execute/Fileman/{fn}'
    encoded = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(
        url if post else url + '?' + encoded.decode(),
        data=encoded if post else None,
        method='POST' if post else 'GET',
    )
    req.add_header('Authorization', f'cpanel {user}:{token}')
    if post:
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(req, context=CTX, timeout=90) as r:
        payload = json.loads(r.read().decode('utf-8', 'replace'))
    result = payload.get('result') if isinstance(payload.get('result'), dict) else payload
    if not isinstance(result, dict) or result.get('status') != 1:
        raise RuntimeError(str(result))
    return result.get('data')


def save(filename, content):
    return api('save_file_content', {
        'dir': 'public_html',
        'file': filename,
        'content': content,
        'from_charset': 'UTF-8',
        'to_charset': 'UTF-8',
        'fallback': '0',
    }, True)


def extract_content(data):
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        for key in ('content', 'file_content', 'data'):
            if isinstance(data.get(key), str):
                return data[key]
    return None


def read_server_file(filename):
    try:
        data = api('get_file_content', {
            'dir': 'public_html',
            'file': filename,
            'from_charset': '_DETECT_',
            'to_charset': 'utf-8',
        })
        return extract_content(data)
    except Exception as exc:
        text = str(exc).lower()
        if any(x in text for x in ('no such file', 'does not exist', 'not found', 'failed to open')):
            return None
        raise


def http_get(filename):
    url = BASE + '/' + urllib.parse.quote(filename, safe='') + '?gsc=' + str(int(time.time()))
    req = urllib.request.Request(url, headers={
        'User-Agent': 'GramissGSCVerificationPublisher/1.0',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    })
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=120) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', 'replace')


def rollback_new_file(filename):
    nonce = str(int(time.time()))
    helper = 'gramiss-gsc-rollback-' + nonce + '.php'
    php = "<?php $f=__DIR__.'/" + filename + "'; $ok=!file_exists($f)||@unlink($f); @unlink(__FILE__); header('Content-Type:text/plain'); echo $ok?'OK':'FAIL'; ?>"
    save(helper, php)
    status, body = http_get(helper)
    if status != 200 or body.strip() != 'OK':
        raise RuntimeError('rollback helper failed: HTTP %s body=%r' % (status, body[:80]))
    after = read_server_file(filename)
    if after is not None:
        raise RuntimeError('rollback did not remove verification file')


def publish(filename, content):
    filename, content = validate(filename, content)
    existing = read_server_file(filename)
    if existing is not None:
        if existing.strip() == content:
            status, body = http_get(filename)
            if status == 200 and body.strip() == content:
                print('GSC_VERIFICATION_ALREADY_PRESENT', filename)
                print('PASS GSC VERIFICATION FILE PUBLISHER V1 IDEMPOTENT')
                return
        raise SystemExit('REFUSE existing Google verification filename with different/unverified content')

    save(filename, content + '\n')
    errors = []
    try:
        stored = read_server_file(filename)
        if stored is None or stored.strip() != content:
            errors.append('cPanel stored content mismatch')
        status, body = http_get(filename)
        print('GSC_VERIFICATION_HTTP', json.dumps({'filename': filename, 'status': status}, sort_keys=True))
        if status != 200:
            errors.append('public HTTP ' + str(status))
        elif body.strip() != content:
            errors.append('public content mismatch')
        if errors:
            raise RuntimeError('; '.join(errors))
    except Exception:
        rollback_new_file(filename)
        print('ROLLBACK GSC VERIFICATION FILE COMPLETE', filename)
        raise

    print('PASS GSC VERIFICATION FILE PUBLISHER V1', filename)


def self_test():
    good = 'google12345678abcdef.html'
    validate(good, 'google-site-verification: ' + good)
    bad = 0
    for filename, content in [
        ('index.html', 'google-site-verification: index.html'),
        (good, 'google-site-verification: googleDIFFERENT.html'),
        ('googlex.html', 'google-site-verification: googlex.html'),
    ]:
        try:
            validate(filename, content)
        except ValueError:
            bad += 1
    assert bad == 3
    print('PASS GSC VERIFICATION FILE PUBLISHER V1 SELFTEST')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--filename')
    p.add_argument('--content')
    p.add_argument('--self-test', action='store_true')
    a = p.parse_args()
    if a.self_test:
        self_test()
    else:
        if not a.filename or not a.content:
            p.error('--filename and --content are required')
        publish(a.filename, a.content)
