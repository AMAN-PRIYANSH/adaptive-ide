/* quiz.js v2.2 — Adaptive Learning IDE */
'use strict';

let currentQ      = null;
let hintUsed      = false;
let hintText      = '';
let timerSec      = 0;
let timerInterval = null;
let submitLocked  = false;

const $ = id => document.getElementById(id);

const loadingState   = $('loadingState');
const questionCard   = $('questionCard');
const feedbackCard   = $('feedbackCard');
const optionsGrid    = $('optionsGrid');
const questionText   = $('questionText');
const hintBtn        = $('hintBtn');
const hintMsg        = $('hintMsg');
const nextBtn        = $('nextBtn');
const progressFill   = $('progressFill');
const progressLabel  = $('progressLabel');
const abilityDisplay = $('abilityDisplay');
const sigmaDisplay   = $('sigmaDisplay');
const timerDisplay   = $('timerDisplay');
const timerBadge     = $('timerBadge');
const qTypeBadge     = $('qTypeBadge');
const qDiffBadge     = $('qDiffBadge');
const devPanel       = $('devPanel');

$('devToggleBtn').addEventListener('click', () => devPanel.classList.toggle('hidden'));
$('devCloseBtn').addEventListener('click',  () => devPanel.classList.add('hidden'));

// ── Security ──────────────────────────────────────────────────────────
document.addEventListener('paste', e => e.preventDefault());
document.addEventListener('copy',  e => e.preventDefault());
document.addEventListener('keydown', e => {
  if (e.key === 'F12') e.preventDefault();
  if ((e.ctrlKey||e.metaKey) && e.key === 'u') e.preventDefault();
  if ((e.ctrlKey||e.metaKey) && e.shiftKey && ['I','i'].includes(e.key)) e.preventDefault();
});

// ── Fullscreen ────────────────────────────────────────────────────────
async function tryFullscreen() {
  try { await document.documentElement.requestFullscreen(); } catch(_) {}
}
document.addEventListener('fullscreenchange', () => {
  if (!document.fullscreenElement) showToast('Fullscreen exited.', 'warn');
});

function showToast(msg, type = 'info') {
  // Remove existing toasts first
  document.querySelectorAll('.quiz-toast').forEach(t => t.remove());
  const t = document.createElement('div');
  t.className = 'quiz-toast';
  t.textContent = msg;
  t.style.cssText = `
    position:fixed; bottom:1.5rem; left:50%; transform:translateX(-50%);
    background:${type === 'warn' ? '#2e2000' : '#1e1e2e'};
    border:1px solid ${type === 'warn' ? '#ffb86c' : '#6c63ff'};
    color:${type === 'warn' ? '#ffb86c' : '#cdd6f4'};
    padding:.6rem 1.2rem; border-radius:8px; font-size:.85rem;
    z-index:9999; white-space:nowrap; pointer-events:none;
  `;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

// ── Timer ─────────────────────────────────────────────────────────────
function startTimer(estimatedTime) {
  timerSec = 0;
  timerDisplay.textContent = '0s';
  timerBadge.classList.remove('warn', 'over');
  clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    timerSec++;
    timerDisplay.textContent = timerSec + 's';
    const r = timerSec / estimatedTime;
    timerBadge.classList.toggle('warn', r >= 1.0 && r < 2.0);
    timerBadge.classList.toggle('over', r >= 2.0);
  }, 1000);
}
function stopTimer() { clearInterval(timerInterval); }

// ── Dev panel ─────────────────────────────────────────────────────────
function dvSet(id, val) { const el = $(id); if (el) el.textContent = val; }

// ── THE CORE FIX: clean render question ──────────────────────────────
// Problem was: code questions inserted NEW <p> and <pre> elements into
// questionCard on every call but never removed the ones from last time.
// Fix: questionCard has ONE fixed container div (#questionBody).
// We always REPLACE its innerHTML — never append to the DOM.

function renderQuestion(data) {
  const body = $('questionBody');

  // Split on first double-newline — text before it is the question,
  // everything after is the code block.
  const splitIdx = data.question.indexOf('\n\n');
  const hasCode  = splitIdx !== -1;

  if (hasCode) {
    const qText  = data.question.slice(0, splitIdx).trim();
    const cBlock = data.question.slice(splitIdx + 2).trim();
    body.innerHTML = `
      <p class="question-text">${escHtml(qText)}</p>
      <pre class="code-block">${escHtml(cBlock)}</pre>
    `;
  } else {
    body.innerHTML = `<p class="question-text">${escHtml(data.question)}</p>`;
  }
}

function escHtml(s) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Load next question ─────────────────────────────────────────────────
async function loadNextQuestion() {
  // Always show loading, hide both cards — clean slate every time
  show(loadingState);
  hide(questionCard);
  hide(feedbackCard);

  submitLocked = false;
  hintUsed     = false;
  hintText     = '';
  hintMsg.textContent  = '';
  hintBtn.disabled     = false;
  hintBtn.style.opacity = '1';

  const res  = await fetch('/api/next');
  const data = await res.json();

  if (data.done) { window.location.href = '/result'; return; }

  currentQ = data;

  // Progress bar
  const pct = ((data.question_number - 1) / data.total_questions * 100).toFixed(1);
  progressFill.style.width  = pct + '%';
  progressLabel.textContent = `${data.question_number} / ${data.total_questions}`;

  // Type / difficulty badges
  qTypeBadge.textContent = data.type.toUpperCase();
  qDiffBadge.textContent = 'B=' + (data.difficulty * 100).toFixed(0) + '%';

  // Topic badge
  const topicBadge = $('qTopicBadge');
  if (topicBadge) {
    if (data.topic) {
      topicBadge.textContent  = data.topic;
      topicBadge.style.display = '';
    } else {
      topicBadge.style.display = 'none';
    }
  }

  // ── Render question text + optional code block ──
  renderQuestion(data);

  // ── Render options ──────────────────────────────
  // Always clear and rebuild — never append
  optionsGrid.innerHTML = '';
  data.options.forEach(opt => {
    const btn = document.createElement('button');
    btn.className   = 'option-btn';
    btn.textContent = opt;
    btn.addEventListener('click', () => selectOption(btn, opt));
    optionsGrid.appendChild(btn);
  });

  // Store hint text for this question
  hintText = data.hint || '💡 You can do it! 🔥';

  // Dev panel — pre-answer state
  dvSet('dv-qid',  data.id);
  dvSet('dv-type', data.type);
  dvSet('dv-diff', (data.difficulty * 100).toFixed(1) + '%');
  dvSet('dv-disc', data.discrimination != null ? data.discrimination : 'default (2.0)');
  dvSet('dv-gues', '0.20 (default)');
  dvSet('dv-est',  data.estimated_time + 's');
  ['dv-ab','dv-aa','dv-delta','dv-sigma','dv-ep',
   'dv-surp','dv-surpa','dv-guess','dv-hm','dv-tm',
   'dv-tr','dv-sm','dv-lr','dv-cs','dv-ws'].forEach(id => dvSet(id, '—'));

  startTimer(data.estimated_time);

  // Show question, hide loading
  hide(loadingState);
  show(questionCard);
}

// ── Option selection ───────────────────────────────────────────────────
function selectOption(clickedBtn, answer) {
  if (submitLocked) return;
  submitLocked = true;
  stopTimer();

  document.querySelectorAll('.option-btn').forEach(b => {
    b.classList.remove('selected');
    b.disabled = true;
  });
  clickedBtn.classList.add('selected');
  hintBtn.disabled = true;

  submitAnswer(answer);
}

// ── Hint ───────────────────────────────────────────────────────────────
hintBtn.addEventListener('click', () => {
  if (hintUsed) return;
  hintUsed              = true;
  hintBtn.disabled      = true;
  hintBtn.style.opacity = '0.5';
  hintMsg.textContent   = hintText;
});

// ── Submit ─────────────────────────────────────────────────────────────
async function submitAnswer(answer) {
  const res = await fetch('/api/submit', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ answer, hint_used: hintUsed, time_taken: timerSec }),
  });
  showFeedback(await res.json(), answer);
}

// ── Feedback ───────────────────────────────────────────────────────────
function showFeedback(result, givenAnswer) {
  // Colour options — correct green, chosen-wrong red
  document.querySelectorAll('.option-btn').forEach(btn => {
    const text = btn.textContent.trim();
    if (text === result.correct_answer.trim())              btn.classList.add('correct');
    else if (text === givenAnswer.trim() && !result.correct) btn.classList.add('wrong');
  });

  // Header ability / sigma
  abilityDisplay.textContent = (result.ability_after * 100).toFixed(1) + '%';
  sigmaDisplay.textContent   = (result.uncertainty  * 100).toFixed(1) + '%';

  // Verdict
  const verdict = $('feedbackVerdict');
  verdict.textContent = result.correct ? '✓ Correct!' : '✗ Incorrect';
  verdict.className   = 'feedback-verdict ' + (result.correct ? 'correct-v' : 'wrong-v');

  $('feedbackExplanation').textContent = result.explanation;

  // Ability change row
  $('fbAbilityBefore').textContent = (result.ability_before * 100).toFixed(1) + '%';
  $('fbAbilityAfter').textContent  = (result.ability_after  * 100).toFixed(1) + '%';
  const delta   = result.delta;
  const deltaEl = $('fbDelta');
  deltaEl.textContent = (delta >= 0 ? '▲ +' : '▼ ') + (delta * 100).toFixed(2) + '%';
  deltaEl.className   = 'ability-delta ' + (delta >= 0 ? 'pos' : 'neg');
  $('fbSigma').textContent = `σ=${(result.uncertainty * 100).toFixed(1)}%`;

  // Progress
  const pct = (result.questions_done / result.total_questions * 100).toFixed(1);
  progressFill.style.width  = pct + '%';
  progressLabel.textContent = `${result.questions_done} / ${result.total_questions}`;

  // Dev panel — post-answer
  if (result.dev) {
    const d = result.dev;
    dvSet('dv-ab',    (result.ability_before * 100).toFixed(2) + '%');
    dvSet('dv-aa',    (result.ability_after  * 100).toFixed(2) + '%');
    dvSet('dv-delta', (result.delta * 100).toFixed(3) + '%');
    dvSet('dv-sigma', (d.uncertainty_after  * 100).toFixed(1) + '%');
    dvSet('dv-ep',    (result.expected_p     * 100).toFixed(1) + '%');
    dvSet('dv-surp',  d.surprise.toFixed(4));
    dvSet('dv-surpa', d.surprise_adj.toFixed(4));
    dvSet('dv-guess', d.guess_detected ? '⚠ YES' : 'no');
    dvSet('dv-hm',    d.hint_modifier.toFixed(2));
    dvSet('dv-tm',    d.time_modifier.toFixed(2));
    dvSet('dv-tr',    d.time_ratio.toFixed(2) + 'x');
    dvSet('dv-sm',    d.streak_modifier.toFixed(2));
    dvSet('dv-lr',    d.learning_rate.toFixed(4));
    dvSet('dv-cs',    d.correct_streak);
    dvSet('dv-ws',    d.wrong_streak);
    dvSet('dv-disc',  d.discrimination);
    dvSet('dv-gues',  d.guessing_param);
    if (d.guess_detected) showToast('⚠ Fast guess on hard question — boost discounted', 'warn');
  }

  // Switch cards
  hide(questionCard);
  show(feedbackCard);
}

// ── Next ────────────────────────────────────────────────────────────────
nextBtn.addEventListener('click', loadNextQuestion);

// ── Helpers ─────────────────────────────────────────────────────────────
function show(el) { el.classList.remove('hidden'); }
function hide(el) { el.classList.add('hidden'); }

// ── Init ─────────────────────────────────────────────────────────────────
(async () => {
  await tryFullscreen();
  await loadNextQuestion();
})();
