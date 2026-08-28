# Delivery harness

## 로컬

`./scripts/harness serve` 후 `http://127.0.0.1:4173/`에서 확인한다.

## Git

- 기본 원격 `origin`: `JackieError/market-study-dashboard`
- 보조 원격 `macromaster`: `JackieError/MacroMaster`
- `.env`, DB, 캐시는 절대 커밋하지 않는다.

## 배포

Pages 링크:

- `https://jackieerror.github.io/market-study-dashboard/`
- `https://jackieerror.github.io/MacroMaster/`
- `https://jackieerror.github.io/MacroMaster/investmaster/` — InvestMaster 투자학교

정적 배포에서는 API가 작동하지 않는다. 백엔드 배포 전에는 정적 데이터가 실시간인 것처럼 표시되지 않게 한다.
