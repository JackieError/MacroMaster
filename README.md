# Market Note

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https%3A%2F%2Fgithub.com%2FJackieError%2Fmarket-study-dashboard)

매일 시장을 읽는 순서를 안내하는 투자 학습용 정적 웹페이지입니다.

## 실행

실데이터 API와 예측 기록을 사용하려면 아래 명령으로 로컬 서버를 실행합니다.

```bash
cd /Users/error/market-study-dashboard
python3 server.py
```

그다음 `http://127.0.0.1:4173/`로 접속합니다.

## API 키

`.env.example`을 `.env`로 복사한 뒤 발급받은 키를 `=` 오른쪽에 입력합니다. 서버는 시작할 때 `.env`를 자동으로 읽습니다. 키가 없는 소스는 연결 대기로 표시되며, SEC EDGAR는 키 없이 동작합니다.

```bash
cp .env.example .env
open -e .env
```

- `FRED_API_KEY`: 금리·달러·VIX
- `DART_API_KEY`: 국내 공시
- `DATA_GO_KR_KEY`: 국내 일별 주가
- `TELEGRAM_BOT_TOKEN`: 봇이 수신할 수 있는 채팅·채널 메시지

저장한 뒤 서버를 재시작합니다. Telegram Bot API는 봇이 추가된 대화와 봇에게 전달한 메시지만 읽을 수 있습니다.

현재 일부 카드는 UI 검증용 샘플이며, 로컬 API 서버 연결 시 실제 데이터 상태와 삼성전자·SK하이닉스 장기 분석이 표시됩니다. 체크리스트와 투자 기록은 브라우저 `localStorage`에도 저장됩니다.

## 온라인 API 배포

위의 **Deploy to Render** 버튼을 누르면 저장소의 `render.yaml`을 사용해 Python 분석 서버를 생성할 수 있습니다. 자세한 절차는 [RENDER_SETUP.md](RENDER_SETUP.md)에 있습니다.
