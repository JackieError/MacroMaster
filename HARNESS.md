# Harness map

하네스는 새 터미널이나 에이전트가 동일한 기준으로 작업하도록 만드는 실행·맥락 단위다.

| 하네스 | 파일 | 담당 |
|---|---|---|
| Research | `harnesses/research.md` | 장기 섹터·기업·매크로 해석 |
| Data | `harnesses/data.md` | API, 캐시, 스키마, 품질 검사 |
| Telegram | `harnesses/telegram.md` | 메시지 수집·중복 제거·분위기 |
| Learning | `harnesses/learning.md` | 초보 학습 흐름과 복기 UX |
| Delivery | `harnesses/delivery.md` | 테스트, GitHub, Pages, 운영 |

## 명령

```bash
./scripts/harness status    # 비밀값 없이 연결·Git 상태 확인
./scripts/harness check     # Python/JS/필수 파일 검사
./scripts/harness serve     # .env를 읽는 로컬 서버 실행
./scripts/harness research  # 오늘 분석 작업용 안내 출력
./scripts/harness deploy    # 검사 후 origin main에 푸시
```

다른 에이전트를 시작할 때는 다음 문장을 전달한다.

> AGENTS.md와 PROJECT_STATE.md를 먼저 읽고, 작업에 해당하는 harnesses 문서를 따른 뒤 ./scripts/harness check를 실행하라. 비밀값은 출력하지 마라.

