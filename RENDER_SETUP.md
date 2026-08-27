# Render 배포 안내

## 1. Blueprint 열기

[Deploy to Render](https://render.com/deploy?repo=https%3A%2F%2Fgithub.com%2FJackieError%2Fmarket-study-dashboard)를 연다.

Render 계정을 만들거나 로그인한 뒤 GitHub 계정 `JackieError`를 연결한다. 저장소 접근 권한에서 `market-study-dashboard`를 허용한다.

## 2. 비밀 환경변수 입력

Blueprint 화면의 `market-note-api` 서비스에 다음 값을 입력한다.

- `FRED_API_KEY`
- `DART_API_KEY`
- `DATA_GO_KR_KEY`
- `TELEGRAM_BOT_TOKEN`
- `MARKET_NOTE_USER_AGENT`: `MarketNote/0.1 본인이메일`

로컬 `/Users/error/market-study-dashboard/.env`에 있는 값과 같다. 키는 GitHub 파일이나 Render 서비스 이름에 넣지 않는다.

`MARKET_NOTE_HOST=0.0.0.0`과 `MARKET_NOTE_PORT=10000`은 Blueprint가 자동으로 설정한다.

## 3. 배포

`Deploy Blueprint`를 누르고 로그에서 다음 단계를 확인한다.

1. `pip install -r requirements.txt`
2. `python3 server.py`
3. `Market Note: http://0.0.0.0:10000`
4. 서비스 상태 `Live`

완료되면 `https://market-note-api-....onrender.com` 형식의 URL이 생긴다.

## 4. 상태 확인

생성된 URL 뒤에 `/api/status`를 붙여 브라우저에서 연다.

```text
https://생성된주소.onrender.com/api/status
```

응답의 `fred`, `dart`, `korea`, `sec`, `telegram` 연결 상태를 확인한다. API 키 값 자체는 응답에 나오지 않는다.

## 5. Pages와 연결

생성된 Render URL을 `config.js`의 값으로 설정한다.

```js
window.MARKET_NOTE_API_BASE = 'https://생성된주소.onrender.com';
```

그 뒤 `main`에 푸시하면 GitHub Pages에서도 실데이터 분석을 사용한다.

## 주의

- Render 무료 인스턴스는 사용하지 않으면 잠들 수 있어 첫 요청이 느릴 수 있다.
- SQLite 파일은 영구 저장소가 아니다. 예측 기록을 영구 보존하려면 PostgreSQL로 이전한다.
- 환경변수를 바꾼 뒤에는 `Save, rebuild, and deploy`를 선택한다.
- 키가 노출됐다고 의심되면 해당 제공처에서 즉시 재발급한다.
