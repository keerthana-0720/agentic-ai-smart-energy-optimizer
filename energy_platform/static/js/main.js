// ============================================================
// main.js - EnergyAI Platform Global JavaScript
// ============================================================

// ===== LIVE CLOCK IN FOOTER =====
function updateFooterTime() {
  const el = document.getElementById('footer-time');
  if (el) el.textContent = new Date().toLocaleTimeString('en-US');
}
setInterval(updateFooterTime, 1000);
updateFooterTime();

// ===== AI ASSISTANT POPUP =====
const aiBtn   = document.getElementById('aiAssistantBtn');
const aiPopup = document.getElementById('aiPopup');
const closeAi = document.getElementById('closeAiPopup');
const aiInput = document.getElementById('aiInput');
const aiSend  = document.getElementById('aiSendBtn');
const aiMsgs  = document.getElementById('aiMessages');

const aiResponses = [
  "Your current energy usage is 342.5 kWh. Consider shifting heavy loads to off-peak hours.",
  "I detected an anomaly in Sector B — 23% above baseline. Recommend immediate inspection.",
  "Based on weather forecasts, expect a 12% increase in consumption next week.",
  "Switching to LED lighting could save you up to 15% on your lighting costs.",
  "Your energy saving score is 78/100. Great job! Optimize HVAC to push it above 85.",
  "Peak consumption occurs between 2PM-5PM. Schedule industrial tasks before noon.",
  "Solar panel integration could offset 20% of your grid consumption.",
  "AI prediction: Next month consumption estimated at 389 kWh based on current trends."
];

if (aiBtn) {
  aiBtn.addEventListener('click', () => {
    aiPopup.classList.toggle('open');
  });
}
if (closeAi) {
  closeAi.addEventListener('click', () => aiPopup.classList.remove('open'));
}

function addAiMessage(text, type) {
  const div = document.createElement('div');
  div.className = 'ai-message ' + type;
  div.innerHTML = (type === 'bot' ? '<i class="fas fa-robot me-2 text-success"></i>' : '') + text;
  aiMsgs.appendChild(div);
  aiMsgs.scrollTop = aiMsgs.scrollHeight;
}

function handleAiSend() {
  if (!aiInput) return;
  const val = aiInput.value.trim();
  if (!val) return;
  addAiMessage(val, 'user');
  aiInput.value = '';
  setTimeout(() => {
    const resp = aiResponses[Math.floor(Math.random() * aiResponses.length)];
    addAiMessage(resp, 'bot');
  }, 600);
}

if (aiSend)  aiSend.addEventListener('click', handleAiSend);
if (aiInput) aiInput.addEventListener('keydown', e => { if (e.key === 'Enter') handleAiSend(); });

// ===== SIDEBAR TOGGLE (mobile) =====
const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar       = document.getElementById('sidebar');
if (sidebarToggle && sidebar) {
  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    sidebar.classList.toggle('open');
  });
}

// ===== NAVBAR SCROLL EFFECT =====
window.addEventListener('scroll', () => {
  const nav = document.querySelector('.glass-nav');
  if (nav) {
    nav.style.background = window.scrollY > 50
      ? 'rgba(10,10,26,0.98)'
      : 'rgba(10,10,26,0.85)';
  }
});

// ===== AUTO-DISMISS FLASH ALERTS =====
setTimeout(() => {
  document.querySelectorAll('.alert').forEach(a => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(a);
    if (bsAlert) bsAlert.close();
  });
}, 5000);

// ===== ANIMATE ELEMENTS ON SCROLL =====
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('fade-in-up');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.feature-card, .step-card, .kpi-card, .glass-card').forEach(el => {
  observer.observe(el);
});
