# -*- coding: utf-8 -*-
"""아이템 아이콘을 로컬로 미러링한다.

render.albiononline.com 은 동시 요청이 몰리면 502 로 죽으므로 4개씩만 받는다.
이미 받아둔 파일은 건너뛰므로 중단 후 다시 실행해도 이어서 진행된다.
"""
import json, os, ssl, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

def make_ctx():
    """프록시가 TLS 를 가로채는 환경에서도 되도록 시스템 인증서를 먼저 쓴다."""
    for path in (os.environ.get('SSL_CERT_FILE'), '/etc/ssl/cert.pem',
                 '/etc/ssl/certs/ca-certificates.crt'):
        if path and os.path.exists(path):
            try:
                return ssl.create_default_context(cafile=path)
            except Exception:
                pass
    return ssl.create_default_context()

CTX = make_ctx()

SIZE     = 64
OUT      = 'icons'
WORKERS  = 4
TRIES    = 5
BASE     = 'https://render.albiononline.com/v1/item/'

os.makedirs(OUT, exist_ok=True)
ids = [r['id'] for r in json.load(open('albion_data.json'))['items']]
todo = [i for i in ids if not os.path.exists(os.path.join(OUT, i + '.png'))]
print(f"전체 {len(ids)}종 / 받을 것 {len(todo)}종", flush=True)

done = fail = 0
t0 = time.time()

def get(item_id):
    url = BASE + urllib.parse.quote(item_id) + f'.png?size={SIZE}'
    path = os.path.join(OUT, item_id + '.png')
    for n in range(TRIES):
        try:
            # PNG 응답에는 no-transform 이 붙어 압축되지 않으므로 그대로 받는다
            req = urllib.request.Request(url, headers={
                'User-Agent': 'albion-calculator-ko/1.0 (icon mirror, one-time)',
            })
            with urllib.request.urlopen(req, timeout=30, context=CTX) as r:
                data = r.read()
            if len(data) < 100:
                raise ValueError('too small')
            tmp = path + '.part'
            with open(tmp, 'wb') as f:
                f.write(data)
            os.replace(tmp, path)
            return True
        except Exception:
            time.sleep(0.7 * (2 ** n))
    return False

with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    for ok in ex.map(get, todo):
        if ok: done += 1
        else:  fail += 1
        n = done + fail
        if n % 250 == 0 or n == len(todo):
            el = time.time() - t0
            rate = n / el if el else 0
            left = (len(todo) - n) / rate / 60 if rate else 0
            print(f"  {n}/{len(todo)}  성공 {done} 실패 {fail}  "
                  f"{rate:.1f}건/초  남은 시간 약 {left:.0f}분", flush=True)

sz = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT) if f.endswith('.png'))
print(f"완료 — 성공 {done}, 실패 {fail}, 총 {sz/1024/1024:.0f} MB", flush=True)
if fail:
    print("실패한 것은 다시 실행하면 이어서 받습니다.", flush=True)
