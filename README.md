# 알비온 제작 계산기 (한국어)

Nendys 계산기와 같은 기능을 게임 공개 데이터로 새로 구현한 한국어 버전입니다.
정제 · 제작 · 음식 · 물약 전부를 다루며, 파일 하나로 브라우저에서 바로 실행됩니다.

## 사용법

`index.html` 을 브라우저로 열면 끝입니다. 설치·서버 불필요.

* 시세는 열 때마다 [Albion Online Data Project](https://www.albion-online-data.com/) 에서 자동으로 받아옵니다.
* 설정(도시·집중·프리미엄 등)과 직접 입력한 가격은 브라우저에 저장됩니다.

## 기능

| | |
|---|---|
| 아이템 | 9,254종 — 한글 이름 검색 (정제품·무기·방어구·가방/망토·음식·물약·탈것·채집도구) |
| 반환율 | `B/(1+B)` · 도시 18% + 정제특화 40% / 제작특화 15% + 집중 59% + 일일·추가 보너스 |
| 연쇄 제작 | 하위 재료를 "직접 제작"으로 바꾸면 원광까지 재귀 전개 (체인 정제 포함) |
| 원가 | 재료비 + 제작소 사용료(`아이템가치 × 0.1125 × 사용료/100`) |
| 수익 | 판매세 4%(프리미엄)/8% + 판매주문 등록비 2.5% 반영, 이익률·집중 1당 이익 |
| 시세 | 아시아/아메리카/유럽 서버, 도시별 판매주문·구매주문 가격, 데이터 나이 표시 |
| 수동 입력 | 시세가 없거나 실제 거래가와 다를 때 재료·판매가를 직접 덮어쓰기 |

## 게임 패치 후 데이터 갱신

아이템·레시피가 바뀌면 이 폴더에서 아래 3줄만 실행하면 됩니다.

```bash
curl -sL https://raw.githubusercontent.com/ao-data/ao-bin-dumps/master/items.json -o items_raw.json
curl -sL https://raw.githubusercontent.com/ao-data/ao-bin-dumps/master/formatted/items.json -o items_formatted.json
python3 build_data.py && python3 build_app.py
```

* `build_data.py` — 게임 덤프에서 레시피·한글명·아이템가치를 뽑아 `albion_data.json` 생성
* `build_app.py` — `app_template.html` 에 데이터를 넣어 완성본 HTML 빌드
* 반환율·세금 수치는 `app_template.html` 상단 `bonusSum()` / `salesTax()` 에 있습니다

## 배포

`main` 브랜치 루트를 GitHub Pages 가 그대로 서빙합니다. 푸시하면 1~2분 뒤 반영됩니다.

    https://jeonghun-project.github.io/albion-calculator-ko/

시세 API 는 `Access-Control-Allow-Origin: *` 라 브라우저에서 직접 호출합니다 —
서버나 프록시가 필요 없어 정적 호스팅(Pages, Netlify, S3) 어디서든 동작합니다.
외부 네트워크 요청을 막는 샌드박스 환경에서만 시세가 비어 보입니다.

## 출처

* 아이템·레시피 데이터 — [ao-data/ao-bin-dumps](https://github.com/ao-data/ao-bin-dumps) (한국어 이름은 게임 공식 로컬라이제이션)
* 시세 — [Albion Online Data Project](https://www.albion-online-data.com/)
* 아이콘 — `render.albiononline.com` 공식 렌더 API

Sandbox Interactive GmbH 와 무관한 비공식 도구입니다.
