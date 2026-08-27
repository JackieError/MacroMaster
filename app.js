const leaders = {
  kr: [
    { rank: '01', name: '한빛반도체', ticker: 'DEMO 001', sector: '반도체 장비', rs: '94', note: '거래대금 2.1배' },
    { rank: '02', name: '코리아파워', ticker: 'DEMO 002', sector: '전력 인프라', rs: '91', note: '20일선 지지' },
    { rank: '03', name: '넥스트바이오', ticker: 'DEMO 003', sector: '바이오', rs: '87', note: '실적 추정치 ↑' },
    { rank: '04', name: '모션로보틱스', ticker: 'DEMO 004', sector: '로봇', rs: '84', note: '신고가 -3%' }
  ],
  us: [
    { rank: '01', name: 'Northstar AI', ticker: 'DEMO·NST', sector: 'AI 인프라', rs: '96', note: '주간 신고가' },
    { rank: '02', name: 'Vector Grid', ticker: 'DEMO·VGR', sector: '전력망', rs: '92', note: '거래량 증가' },
    { rank: '03', name: 'Orbit Systems', ticker: 'DEMO·OBS', sector: '우주·방산', rs: '89', note: '50일선 상승' },
    { rank: '04', name: 'Helix Health', ticker: 'DEMO·HLX', sector: '헬스케어', rs: '85', note: '실적 발표 D-6' }
  ]
};

const date = new Intl.DateTimeFormat('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }).format(new Date());
document.querySelector('#todayLabel').textContent = `${date} · DAILY BRIEF`;

function renderLeaders(market = 'kr') {
  document.querySelector('#leaderRows').innerHTML = leaders[market].map(item => `
    <tr><td><div class="stock"><strong><span class="rank">${item.rank}</span>${item.name}</strong><small>${item.ticker}</small></div></td>
    <td>${item.sector}</td><td class="rs">${item.rs}</td>
    <td><span class="trend-bars" aria-label="상승 추세"><i></i><i></i><i></i><i></i><i></i></span></td><td>${item.note}</td></tr>`).join('');
}
renderLeaders();

document.querySelectorAll('.tabs button').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('.tabs button').forEach(tab => tab.classList.remove('active'));
  button.classList.add('active');
  renderLeaders(button.dataset.market);
}));

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
    const response = await fetch('/api/predictions', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ thesis: marketNote.value, invalidation: invalidNote.value, probability: Number(probability.value) }) });
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
    const response = await fetch('/api/status'); if (!response.ok) throw new Error();
    const data = await response.json();
    document.querySelector('#apiUpdated').textContent = `마지막 확인 ${new Date(data.updated_at).toLocaleTimeString('ko-KR')}`;
    document.querySelectorAll('#sourceChips span').forEach(chip => {
      const key = Object.keys(names).find(k => names[k] === chip.textContent); const source = data.sources[key];
      chip.className = source?.connected ? 'live' : 'error'; chip.title = source?.connected ? `${source.mode} 데이터` : (source?.reason || source?.error || '연결 안 됨');
    });
    const fred = data.sources.fred;
    if (fred?.connected && fred.series?.length) {
      const ten = fred.series.find(x => x.id === 'DGS10'), vix = fred.series.find(x => x.id === 'VIXCLS');
      const values = document.querySelectorAll('.metric-card>strong');
      if (ten && values[0]) values[0].innerHTML = `${ten.value.toFixed(2)}<small>%</small>`;
      if (vix && values[2]) values[2].textContent = vix.value.toFixed(1);
    }
  } catch { document.querySelector('#apiUpdated').textContent = '정적 모드 · server.py로 실행하면 연결됩니다.'; }
}
loadLiveSources();

const sections = [...document.querySelectorAll('main section')];
const links = [...document.querySelectorAll('.nav-link')];
const observer = new IntersectionObserver(entries => entries.forEach(entry => {
  if (!entry.isIntersecting) return;
  links.forEach(link => link.classList.toggle('active', link.getAttribute('href') === `#${entry.target.id}`));
}), { rootMargin: '-30% 0px -60% 0px' });
sections.forEach(section => observer.observe(section));
