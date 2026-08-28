# InvestMaster

기업 분석부터 가치평가, 거시경제, 포트폴리오까지 자기만의 투자 시스템으로 연결하는 인터랙티브 투자학교입니다.

**Live site:** https://jackieerror.github.io/MacroMaster/investmaster/

- 80개 주제를 12개 Part로 재구성한 다층 커리큘럼
- 개념 → 사례 → 계산/실습 → 내 규칙의 학습 루프
- 복리·DCF·ROIC·매출 동인 인터랙티브 실험
- 투자 거장 18명의 전략을 같은 8개 질문으로 비교하는 연구실
- 투자철학·기업분석·가치평가·포트폴리오·일지·Playbook 빌더
- 브라우저 `localStorage` 기반 진도, 사례 답변, 투자 규칙 자동 저장

실습 차트의 2022년 10월~2023년 8월 데이터는 MacroMaster가 수집한 Yahoo Finance 종가와 FRED 환율·VIX 관측치에서 월말 값을 추출해 기준일 100으로 정규화했습니다. 합성 시계열은 사용하지 않습니다.

## 페이지 구조

- `index.html` — 학교 소개와 전체 학습 여정
- `curriculum.html?part=1` — Part별 학습 워크스페이스
- `practice.html` — 매크로 Case Study 차트 실습 워크스페이스
- `masters.html` — 거장 비교와 개인 Playbook
- `system.html` — 최종 투자 시스템 산출물 작성

별도 빌드 과정 없이 `index.html`을 열 수 있습니다. MacroMaster 저장소의 `investmaster/` 하위 경로에서 GitHub Pages로 함께 배포됩니다.
