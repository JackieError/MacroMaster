# Project state

최종 갱신: 2026-08-28

## 구현 완료

- 학습 중심 반응형 대시보드와 Pretendard 기반 리디자인
- 시장 체온, 주도주 후보, Telegram 분위기, 리포트 서재
- 6주 매크로 로드맵, 차트 퀴즈, 과거 사례, CPI 해설
- AI 밸류체인, 용어사전, 반대 논리, 확률 예측·복기
- Python 로컬 API 서버, SQLite 캐시·예측 저장
- `.env` 자동 로딩과 비밀정보 Git 제외
- FRED, OpenDART, 금융위원회 주가, SEC EDGAR, Telegram Bot API 연결
- FRED·DART·SEC·공공데이터 실제 응답 검증
- Telegram 봇 `@macroerrorbot` 연결 확인
- GitHub 저장소와 Pages 배포
- 삼성전자·SK하이닉스 490거래일 장기 분석 엔진
- 1개월·3개월·1년·2년 수익률, 50/200일 추세, 낙폭, 변동성 계산
- 고거래대금 매도 변곡일과 ±5일 DART 공시·FRED 관측치 결합
- 반도체 2년 사이클 및 기업별 사건 타임라인 화면
- `investmaster/` 하위 경로에 12개 Part 투자학교·거장 연구실·Case Study 실습실 통합

## 현재 배포

- `https://jackieerror.github.io/market-study-dashboard/` — Market Note 대시보드
- `https://jackieerror.github.io/MacroMaster/` — 같은 대시보드
- `https://jackieerror.github.io/MacroMaster/curriculum/` — 매크로 사례 학습 커리큘럼
- API: `https://market-note-api.onrender.com`

API 키와 `market_note.db`는 포함되지 않는다.

**두 저장소는 더 이상 동일하지 않다.** `curriculum/`은 MacroMaster에만 있으므로
`./scripts/harness deploy`(양쪽에 같은 main 푸시)를 쓰면 커리큘럼이 지워진다.
`harnesses/delivery.md`의 경고를 따른다.

## 매크로 커리큘럼 (`curriculum/`)

지표를 하나씩 설명하는 글로서리가 아니라, 실제로 있었던 국면을 실측 데이터로 다시 짚는 학습 페이지다.
자세한 규칙은 `harnesses/curriculum.md`, 사례·데이터 목록은 `curriculum/README.md` 참고.

- 카테고리별로 나뉜 사례들을 해시 라우팅 SPA로 제공 (사이드바 아코디언 + 용어사전 슬라이드오버)
- 각 사례 = 실측 차트 + 이벤트 마커 + 서술 + "실전에서 이렇게 읽는다"
  + 4단 심층 아코디언(메커니즘 / 패턴이 깨졌던 순간들 / 반론 / 지금 어떤 국면인가)
- 데이터 원본은 `curriculum/data/` (FRED 공개 CSV, Yahoo Finance, Stooq)
- 원본 작업본 Artifact: https://claude.ai/code/artifact/c421b29c-d3f0-4d98-8020-6240d7bf8ee0

## 진행해야 할 핵심 작업

1. 장기 섹터 사이클 확장
   - 반도체 외 전력·바이오·자동차 등 대표 기업 바스켓
   - KOSPI 및 섹터 지수 대비 상대강도
   - 수정주가/기업행사 보정
2. 사건 연구 고도화
   - Telegram·뉴스·실적 컨센서스 결합
   - 기대와 실제의 차이, 악재 둔감 구간 판별
3. 기업 분석 확장
   - 실적·가이던스·수주·증설·자금조달·내부자/지분 이벤트
   - 섹터 대비 상대강도와 매크로 민감도
4. 근거가 있는 자연어 브리핑
   - 사실/해석/가설/무효화 조건 분리
   - 문장별 출처와 데이터 기준일
5. 온라인 저장소를 SQLite에서 영구 PostgreSQL로 이전

## 알려진 제약

- 금융위원회 주식 시세 API는 작동하지만 섹터 지수 API는 별도 활용신청이 필요하다.
- Bot API는 봇이 받은 이후의 메시지만 수집한다. 공개 채널 과거 전체 수집은 별도 MTProto 사용자 인증이 필요하다.
- 무료 데이터만으로 애널리스트 컨센서스와 이익 추정치 변화 전체를 안정적으로 얻기 어렵다. 없으면 `확인 불가`로 표시한다.
- Pages 배포본에서 `/api/*`는 작동하지 않는다. 정적 폴백을 사용한다.
