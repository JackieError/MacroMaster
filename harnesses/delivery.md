# Delivery harness

## 로컬

`./scripts/harness serve` 후 `http://127.0.0.1:4173/`에서 확인한다.

## Git

- 기본 원격 `origin`: `JackieError/market-study-dashboard`
- 보조 원격 `macromaster`: `JackieError/MacroMaster`
- `.env`, DB, 캐시는 절대 커밋하지 않는다.

### ⚠️ 두 저장소는 더 이상 동일하지 않다

`curriculum/`(매크로 사례 학습 페이지)과 `harnesses/curriculum.md`는 **MacroMaster에만** 있다.
따라서 `./scripts/harness deploy`처럼 **같은 main을 양쪽에 밀어넣는 방식은 더 이상 안전하지 않다** —
market-study-dashboard의 main을 MacroMaster로 푸시하면 `curriculum/`이 사라진다.

당분간 MacroMaster는 별도로 관리한다.

```bash
git push macromaster main    # MacroMaster만 갱신
git push origin main         # 대시보드만 갱신
```

`deploy` 명령을 다시 쓰려면 먼저 두 저장소의 관계를 정리해야 한다
(대시보드를 서브트리로 분리하거나, MacroMaster를 완전한 독립 저장소로 선언하거나).

## 배포

Pages 링크:

- `https://jackieerror.github.io/market-study-dashboard/`
- `https://jackieerror.github.io/MacroMaster/`
- `https://jackieerror.github.io/MacroMaster/investmaster/` — InvestMaster 투자학교

정적 배포에서는 API가 작동하지 않는다. 백엔드 배포 전에는 정적 데이터가 실시간인 것처럼 표시되지 않게 한다.
