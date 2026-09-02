# -*- coding: utf-8 -*-
"""ao-bin-dumps -> 한국어 알비온 계산기용 압축 데이터셋"""
import json, datetime, collections

RAW = json.load(open('items_raw.json'))['items']
FMT = json.load(open('items_formatted.json'))

LOC = {}
for e in FMT:
    un = e.get('UniqueName')
    ln = e.get('LocalizedNames') or {}
    if un:
        LOC[un] = (ln.get('KO-KR'), ln.get('EN-US'))

# 다룰 아이템 종류
KINDS = ['simpleitem', 'consumableitem', 'equipmentitem', 'weapon',
         'mount', 'transformationweapon', 'journalitem', 'farmableitem',
         'consumablefrominventoryitem', 'furnitureitem', 'trackingitem']

def as_list(x):
    if x is None: return []
    return x if isinstance(x, list) else [x]

def mid(uniquename, ench):
    ench = int(ench or 0)
    return f"{uniquename}@{ench}" if ench > 0 else uniquename

def parse_reqs(node, uniquename):
    """craftingrequirements -> [{f,a,s,m:[[id,cnt],..]}]"""
    out = []
    for req in as_list(node):
        mats = []
        for r in as_list(req.get('craftresource')):
            u = r.get('@uniquename')
            if not u: continue
            mats.append([mid(u, r.get('@enchantmentlevel', 0)), float(r.get('@count', 1))])
        if not mats: continue
        out.append({
            'f': float(req.get('@craftingfocus', 0) or 0),
            'a': float(req.get('@amountcrafted', 1) or 1),
            's': float(req.get('@silver', 0) or 0),
            'm': mats,
        })
    return out

# ---- 1차 수집 --------------------------------------------------------------
items = {}   # marketId -> record

def add(uniquename, ench, kind, base, node_over=None):
    src = node_over if node_over is not None else base
    i = mid(uniquename, ench)
    ko, en = LOC.get(i) or LOC.get(uniquename) or (None, None)
    rec = {
        'id': i,
        'ko': ko or en or uniquename,
        'en': en or uniquename,
        't': int(base.get('@tier', 0) or 0),
        'e': int(ench or 0),
        'k': kind,
        'sc': base.get('@shopcategory', ''),
        's1': base.get('@shopsubcategory1', ''),
        's2': base.get('@shopsubcategory2', ''),
        'cc': base.get('@craftingcategory', ''),
    }
    iv = src.get('@itemvalue') or base.get('@itemvalue')
    if iv: rec['iv'] = float(iv)
    nut = src.get('@nutrition') or base.get('@nutrition')
    if nut: rec['nu'] = float(nut)
    fame = base.get('@famevalue')
    if fame: rec['fv'] = float(fame)
    r = parse_reqs(src.get('craftingrequirements'), uniquename)
    if r: rec['r'] = r
    items[i] = rec

for kind in KINDS:
    for it in as_list(RAW.get(kind)):
        if not isinstance(it, dict): continue
        un = it.get('@uniquename')
        if not un: continue
        add(un, it.get('@enchantmentlevel', 0), kind, it)
        ench_node = it.get('enchantments')
        if ench_node:
            for en_ in as_list(ench_node.get('enchantment')):
                add(un, en_.get('@enchantmentlevel', 0), kind, it, node_over=en_)

# ---- 아이템 가치(itemvalue) 재귀 계산 -------------------------------------
# 제작 수수료(nutrition) 계산용. 명시값 없으면 재료 가치 합에서 유도.
_cache = {}
def item_value(i, depth=0):
    if i in _cache: return _cache[i]
    rec = items.get(i)
    if rec is None or depth > 12:
        return 0.0
    if 'iv' in rec:
        _cache[i] = rec['iv']; return rec['iv']
    _cache[i] = 0.0  # 순환 방지
    best = 0.0
    for r in rec.get('r', []):
        tot = sum(item_value(m, depth + 1) * c for m, c in r['m'])
        v = tot / (r['a'] or 1)
        best = max(best, v)
    _cache[i] = best
    return best

for i in list(items):
    v = item_value(i)
    if v: items[i]['iv'] = round(v, 2)

# ---- 필요한 것만 남기기 ----------------------------------------------------
CRAFT_KINDS = {'simpleitem', 'consumableitem', 'equipmentitem', 'weapon',
               'mount', 'transformationweapon', 'journalitem'}
keep = set()
for i, rec in items.items():
    if rec.get('r') and rec['k'] in CRAFT_KINDS:
        keep.add(i)
# 재료로 쓰이는 것도 모두 포함
frontier = list(keep)
while frontier:
    i = frontier.pop()
    for r in items.get(i, {}).get('r', []):
        for m, _ in r['m']:
            if m in items and m not in keep:
                keep.add(m); frontier.append(m)

out_items = []
for i in sorted(keep):
    rec = dict(items[i])
    if rec['k'] not in CRAFT_KINDS:
        rec.pop('r', None)           # 재료 전용 아이템의 레시피는 버림
    for k in ('sc', 's1', 's2', 'cc', 'ko', 'en'):
        if rec.get(k) == '': rec.pop(k)
    for k in ('e', 't'):
        if rec.get(k) == 0: rec.pop(k)
    out_items.append(rec)

data = {
    'meta': {
        'source': 'ao-data/ao-bin-dumps',
        'generated': datetime.date.today().isoformat(),
        'count': len(out_items),
    },
    'items': out_items,
}
json.dump(data, open('albion_data.json', 'w'), ensure_ascii=False, separators=(',', ':'))

# ---- 통계 -----------------------------------------------------------------
c = collections.Counter(r['k'] for r in out_items)
cr = collections.Counter(r['k'] for r in out_items if r.get('r'))
print("총", len(out_items), "종")
for k in c: print(f"  {k:28} {c[k]:6}  (제작가능 {cr[k]})")
import os; print("파일 크기:", round(os.path.getsize('albion_data.json')/1024/1024, 2), "MB")
