# Data harness

## 연결 소스

- FRED: 금리·달러·변동성·경기 시계열
- OpenDART: 국내 공시·재무정보
- 금융위원회 공공데이터: 국내 주식 일봉
- SEC EDGAR: 미국 공시·XBRL
- Telegram Bot API: 봇 수신 메시지

## 데이터 계약

모든 관측치는 `source`, `observed_at`, `effective_date`, `value`, `unit`, `url`, `quality`를 갖는다. 자연어 분석은 사용한 관측치 ID를 보존한다.

## 품질 규칙

- 수정치와 발표 당시 값을 가능한 한 구분한다.
- 휴장일·결측치·0 거래량을 보간해 사실처럼 만들지 않는다.
- API 오류 시 최신 캐시를 `stale`로 표시하며 실시간이라고 쓰지 않는다.
- 종목·지수·ETF를 같은 종류로 혼합하지 않는다.
- 별도 API 활용신청이 필요한 소스는 연결 완료 전까지 숫자를 생성하지 않는다.

## 다음 스키마

`observations`, `instruments`, `events`, `price_bars`, `documents`, `claims`, `analysis_runs` 테이블로 확장한다. 원문과 파생값을 분리한다.

