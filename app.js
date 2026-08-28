const API_BASE = window.MARKET_NOTE_API_BASE || '';

const date = new Intl.DateTimeFormat('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }).format(new Date());
document.querySelector('#todayLabel').textContent = `${date} · DAILY BRIEF`;

const tasks = [...document.querySelectorAll('[data-task]')];
const savedTasks = JSON.parse(localStorage.getItem('market-note-tasks') || '{}');
tasks.forEach(task => {
  task.checked = Boolean(savedTasks[task.dataset.task]);
  task.addEventListener('change', updateProgress);
});

let quizDone = localStorage.getItem('market-note-quiz') === 'done';
function updateProgress() {
  const state = {};
  tasks.forEach(task => state[task.dataset.task] = task.checked);
  localStorage.setItem('market-note-tasks', JSON.stringify(state));
  const total = tasks.length + 1;
  const completed = tasks.filter(task => task.checked).length + (quizDone ? 1 : 0);
  document.querySelector('#progressText').textContent = `${completed} / ${total}`;
  document.querySelector('#progressBar').style.width = `${completed / total * 100}%`;
}
updateProgress();

document.querySelectorAll('[data-answer]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-answer]').forEach(option => option.classList.remove('correct', 'wrong'));
  const isRight = button.dataset.answer === 'right';
  button.classList.add(isRight ? 'correct' : 'wrong');
  document.querySelector('#quizFeedback').textContent = isRight
    ? '정답입니다. 가격 하나가 아니라 위험자산 전반으로 약세가 퍼지는지 먼저 확인해야 합니다.'
    : '다시 생각해보세요. 한 종목보다 시장 전체의 위험 선호가 약해지는지 확인하는 게 먼저입니다.';
  if (isRight) {
    quizDone = true;
    localStorage.setItem('market-note-quiz', 'done');
    updateProgress();
  }
}));

const marketNote = document.querySelector('#marketNote');
const invalidNote = document.querySelector('#invalidNote');
marketNote.value = localStorage.getItem('market-note-market') || '';
invalidNote.value = localStorage.getItem('market-note-invalid') || '';
document.querySelector('#saveJournal').addEventListener('click', async () => {
  localStorage.setItem('market-note-market', marketNote.value.trim());
  localStorage.setItem('market-note-invalid', invalidNote.value.trim());
  const status = document.querySelector('#saveStatus');
  try {
    const response = await fetch(`${API_BASE}/api/predictions`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ thesis: marketNote.value, invalidation: invalidNote.value, probability: Number(probability.value) }) });
    if (!response.ok) throw new Error();
    status.textContent = '서버에 저장되었습니다. 결과가 나온 뒤 복기해보세요.';
  } catch { status.textContent = '브라우저에 저장했습니다. 서버 실행 시 예측표에도 저장됩니다.'; }
  setTimeout(() => status.textContent = '내용은 이 브라우저에만 저장됩니다.', 3000);
});

const probability = document.querySelector('#probability');
probability.addEventListener('input', () => document.querySelector('#probabilityValue').textContent = `${probability.value}%`);
document.querySelector('[data-chart-answer]').addEventListener('click', () => {
  document.querySelector('#chartAnswer').textContent = '좋습니다. 상승 추세는 유지될 수 있지만 참여 강도가 약해지는지 후속 거래량과 지지선을 확인해야 합니다.';
});
document.querySelectorAll('[data-definition]').forEach(button => button.addEventListener('click', () => document.querySelector('#definitionBox').textContent = button.dataset.definition));
const chainNotes = { '전력망':'핵심 지표: 변압기 수주잔고·전력 인허가. 병목: 계통 연결 대기.', '데이터센터':'핵심 지표: 착공·임대율·PUE. 병목: 부지와 전력.', '가속기':'핵심 지표: 출하량·ASP. 병목: 첨단 패키징.', 'HBM':'핵심 지표: 가격·수율·CAPA. 병목: 인증과 수율.', 'AI 소프트웨어':'핵심 지표: 유료 사용자·추론 비용. 병목: 수익화.' };
document.querySelectorAll('[data-term]').forEach(button => button.addEventListener('click', () => document.querySelector('#chainInfo').textContent = chainNotes[button.dataset.term]));

async function loadLiveSources() {
  const names = {fred:'FRED',dart:'DART',korea:'공공데이터',sec:'SEC',telegram:'Telegram'};
  try {
    const response = await fetch(`${API_BASE}/api/status`); if (!response.ok) throw new Error();
    const data = await response.json();
    const connectedCount = Object.values(data.sources).filter(source => source?.connected).length;
    document.querySelector('#dataModeLabel').textContent = 'LIVE DATA';
    document.querySelector('#dataModeDetail').textContent = `실데이터 ${connectedCount}개 소스 연결`;
    document.querySelector('#apiUpdated').textContent = `마지막 확인 ${new Date(data.updated_at).toLocaleTimeString('ko-KR')}`;
    document.querySelectorAll('#sourceChips span').forEach(chip => {
      const key = Object.keys(names).find(k => names[k] === chip.textContent); const source = data.sources[key];
      chip.className = source?.connected ? 'live' : 'error'; chip.title = source?.connected ? `${source.mode} 데이터` : (source?.reason || source?.error || '연결 안 됨');
    });
    const fred = data.sources.fred;
    if (fred?.connected && fred.series?.length) {
      const ten = fred.series.find(x => x.id === 'DGS10'), dollar = fred.series.find(x => x.id === 'DTWEXBGS'), vix = fred.series.find(x => x.id === 'VIXCLS');
      const values = document.querySelectorAll('.metric-card>strong');
      const changes = document.querySelectorAll('.metric-card>.change');
      if (ten && values[0]) values[0].innerHTML = `${ten.value.toFixed(2)}<small>%</small>`;
      if (dollar && values[1]) values[1].textContent = dollar.value.toFixed(2);
      if (vix && values[2]) values[2].textContent = vix.value.toFixed(1);
      if (ten?.history?.length > 1 && changes[0]) {
        const diff = ten.history.at(-1) - ten.history.at(-2); changes[0].textContent = `${diff >= 0 ? '▲' : '▼'} ${Math.abs(diff).toFixed(2)}%p`; changes[0].className = `change ${diff <= 0 ? 'up' : 'down'}`;
      }
      [[dollar, changes[1]], [vix, changes[2]]].forEach(([series, element]) => {
        if (!series?.history?.length || series.history.length < 2 || !element) return;
        const before = series.history.at(-2), diff = (series.history.at(-1) / before - 1) * 100; element.textContent = `${diff >= 0 ? '▲' : '▼'} ${Math.abs(diff).toFixed(2)}%`; element.className = `change ${diff <= 0 ? 'up' : 'down'}`;
      });
      const direction = series => series.history.at(-1) - series.history.at(-2);
      const rateMove = direction(ten), dollarMove = direction(dollar), vixMove = direction(vix);
      const score = 50 + (rateMove <= 0 ? 12 : -12) + (dollarMove <= 0 ? 10 : -10) + (vix.value < 20 ? 14 : vix.value > 25 ? -14 : 0);
      const bounded = Math.max(0, Math.min(100, score));
      document.querySelector('#regimeScore').textContent = bounded;
      document.querySelector('.gauge').style.background = `conic-gradient(var(--lime) 0 ${bounded}%, #38443e ${bounded}%)`;
      document.querySelector('#regimeDate').textContent = `${ten.date} 기준`;
      document.querySelector('#regimeTitle').textContent = bounded >= 65 ? '매크로 위험 환경 우호' : bounded <= 35 ? '매크로 위험 환경 경계' : '매크로 위험 환경 중립';
      document.querySelector('#regimeText').textContent = `미 10년물 ${ten.value.toFixed(2)}%, 달러지수 ${dollar.value.toFixed(2)}, VIX ${vix.value.toFixed(2)}의 최신값과 직전 관측치 방향으로 계산한 규칙 기반 점수입니다.`;
      document.querySelector('#regimeSignals').innerHTML = `<span>금리 <b>${rateMove > 0 ? '상승' : rateMove < 0 ? '하락' : '보합'}</b></span><span>달러 <b>${dollarMove > 0 ? '상승' : dollarMove < 0 ? '하락' : '보합'}</b></span><span>VIX <b>${vixMove > 0 ? '상승' : vixMove < 0 ? '하락' : '보합'}</b></span>`;
      document.querySelector('#macroConnection').textContent = `금리 ${rateMove > 0 ? '↑' : '↓'} · 달러 ${dollarMove > 0 ? '↑' : '↓'} · VIX ${vixMove > 0 ? '↑' : '↓'}`;
      document.querySelector('#macroNarrative').textContent = `직전 관측치 대비 미 10년물 ${rateMove >= 0 ? '+' : ''}${rateMove.toFixed(2)}%p, 달러 ${dollarMove >= 0 ? '+' : ''}${dollarMove.toFixed(2)}, VIX ${vixMove >= 0 ? '+' : ''}${vixMove.toFixed(2)}입니다. 이 문장은 방향만 기술하며 주가 원인을 단정하지 않습니다.`;
    }
    const telegram = data.sources.telegram;
    const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));
    if (telegram?.connected) {
      const items = telegram.items || [];
      document.querySelector('#pulseContent').innerHTML = `<article class="pulse-score dark-card"><div class="card-top"><span>BOT RECEIVED</span><span class="pill positive">실제 ${items.length}건</span></div><strong>${items.length}<small>건</small></strong><h3>${items.length < 10 ? '분위기 판정 보류' : '수집 표본 확인 필요'}</h3><p>${items.length < 10 ? '현재 표본이 10건 미만이므로 감성·급상승 주제를 계산하지 않습니다.' : '중복 제거와 출처 다양성 검사를 거친 뒤에만 분위기를 판정합니다.'}</p></article><article class="theme-radar"><div class="radar-head"><span>최근 실제 메시지</span><small>${telegram.mode}</small></div>${items.slice(-5).reverse().map((item,index) => `<div class="theme-item"><b>0${index+1}</b><div><strong>${escapeHtml(item.chat)}</strong><small>${escapeHtml(item.text)}</small></div></div>`).join('') || '<p>봇이 받은 메시지가 없습니다.</p>'}</article><article class="counter-card"><span class="mini-label">DATA QUALITY</span><h3>현재 가능한 결론</h3><p>${items.length < 10 ? `수신 ${items.length}건으로 시장 분위기를 대표할 수 없습니다. 채널과 출처가 다양해질 때까지 원문 열람만 제공합니다.` : '메시지 수보다 독립 출처 수와 가격·공시 교차검증을 우선합니다.'}</p></article>`;
    }
    const dartItems = (data.sources.dart?.items || []).filter(item => item.stock_code).slice(0,2);
    const secItems = (data.sources.sec?.items || []).slice(0,2);
    const reports = [...dartItems.map(item => ({kind:'DART',date:item.rcept_dt,title:`${item.corp_name} · ${item.report_nm.trim()}`,url:`https://dart.fss.or.kr/dsaf001/main.do?rcpNo=${item.rcept_no}`})), ...secItems.map(item => ({kind:'SEC',date:item.date,title:`${item.company} · ${item.form}`,url:`https://www.sec.gov/edgar/browse/?CIK=${item.ticker}`}))];
    document.querySelector('#liveReports').innerHTML = reports.map((item,index) => `<article><span>0${index+1} · ${item.kind}</span><h3>${escapeHtml(item.title)}</h3><p>공시일 ${escapeHtml(item.date)}</p><small><a href="${item.url}" target="_blank" rel="noopener">공식 원문 확인 ↗</a></small></article>`).join('') || '<article>현재 수신된 실제 공시가 없습니다.</article>';
  } catch {
    document.querySelector('#apiUpdated').textContent = 'API 연결 실패 · 실데이터를 표시할 수 없습니다.';
    document.querySelector('#dataModeLabel').textContent = 'DATA UNAVAILABLE';
    document.querySelector('#dataModeDetail').textContent = '실데이터 API에 연결할 수 없음';
  }
}
loadLiveSources();

let semiconductorData;
let selectedHorizon = '2y';
const signed = value => value == null ? '—' : `${value > 0 ? '+' : ''}${Number(value).toFixed(1)}%`;
const dateLabel = value => value && value.length === 8 ? `${value.slice(0,4)}.${value.slice(4,6)}.${value.slice(6)}` : value;

function renderCompanies() {
  if (!semiconductorData?.companies) return;
  document.querySelector('#companyCycles').innerHTML = semiconductorData.companies.map(company => {
    const focus = company.returns[selectedHorizon];
    return `<article class="company-cycle">
      <div class="company-top"><div><small>${company.code} · ${company.sessions}거래일</small><h3>${company.name}</h3></div><span class="phase-badge">${company.phase}</span></div>
      <div class="return-focus ${focus >= 0 ? 'positive' : 'negative'}"><strong>${signed(focus)}</strong><span>${selectedHorizon.toUpperCase()} 누적 변화</span></div>
      <div class="return-grid">${['1m','3m','1y','2y'].map(h => `<div><span>${h.toUpperCase()}</span><b>${signed(company.returns[h])}</b></div>`).join('')}</div>
      <div class="trend-facts"><span>고점 대비 <b>${signed(company.drawdown)}</b></span><span>50일선 <b>${company.above_ma50 ? '위' : '아래'}</b></span><span>200일선 <b>${company.above_ma200 ? '위' : '아래'}</b></span><span>변동성 <b>${company.annualized_volatility}%</b></span></div>
    </article>`;
  }).join('');
  const ranked = [...semiconductorData.companies].sort((a,b) => (b.returns['1y'] ?? -999) - (a.returns['1y'] ?? -999));
  document.querySelector('#leaderRows').innerHTML = ranked.map((company,index) => `<tr><td><div class="stock"><strong><span class="rank">0${index+1}</span>${company.name}</strong><small>${company.code}</small></div></td><td>반도체 대형주</td><td class="rs">${signed(company.returns['1y'])}</td><td>${company.phase}</td><td>고점 대비 ${signed(company.drawdown)} · 200일선 ${company.above_ma200 ? '위' : '아래'}</td></tr>`).join('');
}

function renderEvents(name) {
  const company = semiconductorData?.companies?.find(x => x.name === name);
  if (!company) return;
  const events = [...company.sell_events].sort((a,b) => b.date.localeCompare(a.date)).slice(0,4);
  document.querySelector('#eventTimeline').innerHTML = events.map(event => {
    const filing = event.disclosures?.[0];
    const macro = event.macro?.map(x => `${x.label} ${x.change_5obs >= 0 ? '+' : ''}${x.change_5obs}`).join(' · ') || '인접 매크로 관측치 없음';
    const telegram = event.telegram?.length ? ` · Telegram ${event.telegram.length}건` : '';
    return `<article class="sell-event"><time>${dateLabel(event.date)}</time><strong>${signed(event.return)}</strong><b>${event.classification}</b><p>거래대금 ${event.turnover_multiple}배${telegram}<br>${macro}</p><details><summary>해석과 반대 근거</summary><p>${event.interpretation}</p><p><b>대안:</b> ${event.alternative}</p><p><b>무효화:</b> ${event.invalidation}</p></details>${filing ? `<a href="https://dart.fss.or.kr/dsaf001/main.do?rcpNo=${filing.receipt}" target="_blank" rel="noopener">${filing.title} ↗</a>` : '<p>±5일 중요 공시 없음</p>'}</article>`;
  }).join('') || '<p>조건에 해당하는 강한 매도 사건이 없습니다.</p>';
}

async function loadSemiconductorAnalysis(force = false) {
  const target = document.querySelector('#cycleAsOf');
  try {
    if (force) target.textContent = '근거 다시 계산 중…';
    const response = await fetch(`${API_BASE}/api/analysis/semiconductor${force ? `?t=${Date.now()}` : ''}`); if (!response.ok) throw new Error();
    semiconductorData = await response.json(); if (!semiconductorData.connected) throw new Error();
    target.textContent = `${dateLabel(semiconductorData.companies[0]?.as_of)} 기준 · ${semiconductorData.mode}`;
    document.querySelector('#semiconductorConclusion').textContent = semiconductorData.conclusion;
    document.querySelector('#semiconductorMethod').textContent = semiconductorData.method;
    renderCompanies(); renderEvents(document.querySelector('#eventCompany').value);
  } catch { target.textContent = '로컬 API 서버에서만 실데이터 분석이 제공됩니다.'; }
}
document.querySelectorAll('[data-horizon]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-horizon]').forEach(x => x.classList.remove('active')); button.classList.add('active'); selectedHorizon = button.dataset.horizon; renderCompanies();
}));
document.querySelector('#eventCompany').addEventListener('change', event => renderEvents(event.target.value));
loadSemiconductorAnalysis();

const sections = [...document.querySelectorAll('main section')];
const links = [...document.querySelectorAll('.nav-link')];
const observer = new IntersectionObserver(entries => entries.forEach(entry => {
  if (!entry.isIntersecting) return;
  links.forEach(link => link.classList.toggle('active', link.getAttribute('href') === `#${entry.target.id}`));
}), { rootMargin: '-30% 0px -60% 0px' });
sections.forEach(section => observer.observe(section));
