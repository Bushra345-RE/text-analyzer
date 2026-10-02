const $ = id => document.getElementById(id);
const SAMPLE = `I recently built a small Python app to analyze text, and the experience was great. The interface is clean and the results are fast. Parsing sentences was a bit difficult at first, and a few bugs were annoying, but the final tool is useful and reliable. Text analysis makes it easy to spot patterns in writing. Good text analysis starts with clean text and clear goals.`;

const words = t => (t.match(/[A-Za-z][A-Za-z'’-]*/g) || []).length;
const esc = s => s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

function toast(msg){const t=$('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2200)}
function showError(msg){const e=$('error');e.textContent=msg||'';e.hidden=!msg}

$('text').addEventListener('input', e => { $('counter').textContent = `${words(e.target.value)} words`; });
$('sample').onclick = () => { $('text').value = SAMPLE; $('title').value = 'Sample review'; $('text').dispatchEvent(new Event('input')); };
$('clear').onclick = () => { $('text').value=''; $('title').value=''; $('text').dispatchEvent(new Event('input')); showError(''); };

$('go').onclick = async () => {
  showError('');
  const btn = $('go'); btn.disabled = true; btn.textContent = 'Analyzing…';
  try {
    const res = await fetch('/api/analyze', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({text:$('text').value, title:$('title').value})});
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Something went wrong.');
    render(data.result);
    toast('Analysis saved');
    loadHistory();
    if (window.innerWidth <= 860) $('results').scrollIntoView({behavior:'smooth'});
  } catch (err) {
    showError(err.message.includes('fetch') ? 'Can’t reach the server. Check that the backend is running.' : err.message);
  } finally { btn.disabled = false; btn.textContent = 'Analyze text'; }
};

function render(r){
  $('empty').hidden = true; $('output').hidden = false;
  const s = r.stats;
  const tiles = [[s.words,'words'],[s.sentences,'sentences'],[s.reading_time_min+' min','reading time'],
    [s.unique_words,'unique words'],[s.avg_sentence_length,'words per sentence'],[s.lexical_diversity,'variety score']];
  $('tiles').innerHTML = tiles.map(([v,l]) => `<div class="tile"><b>${v}</b><span>${l}</span></div>`).join('');
  const se = r.sentiment;
  $('sentLabel').textContent = se.label; $('sentLabel').className = 'pill ' + se.label;
  $('needle').style.left = ((se.score + 1) / 2 * 100) + '%';
  $('cloud').innerHTML = r.keywords.length
    ? r.keywords.map(k => `<span class="chip" style="font-size:${(0.85 + k.weight * 0.6).toFixed(2)}rem">${esc(k.term)}</span>`).join('')
    : '<span class="muted">Not enough text to find keywords.</span>';
  const max = r.top_words[0]?.count || 1;
  $('bars').innerHTML = r.top_words.map(w =>
    `<div class="bar"><span>${esc(w.word)}</span><div class="track"><div class="fill" data-w="${w.count/max*100}"></div></div><em>${w.count}</em></div>`).join('');
  requestAnimationFrame(() => document.querySelectorAll('.fill').forEach(f => f.style.width = f.dataset.w + '%'));
}

async function loadHistory(){
  const items = await (await fetch('/api/history')).json();
  $('hcount').textContent = items.length ? `${items.length} saved` : '';
  $('history').innerHTML = items.length ? items.map(i => `
    <li class="hitem" tabindex="0" data-id="${i.id}">
      <strong>${esc(i.title)}</strong><p>${esc(i.preview)}</p>
      <div class="hmeta"><span>${i.words} words · ${i.sentiment}</span>
      <button class="del" data-del="${i.id}" aria-label="Delete ${esc(i.title)}">Delete</button></div>
    </li>`).join('') : '<li class="muted">Nothing saved yet. Your analyses will show up here.</li>';
}

$('history').addEventListener('click', async e => {
  const del = e.target.closest('[data-del]');
  if (del) { await fetch('/api/history/' + del.dataset.del, {method:'DELETE'}); toast('Deleted'); return loadHistory(); }
  const li = e.target.closest('.hitem'); if (!li) return;
  const d = await (await fetch('/api/history/' + li.dataset.id)).json();
  $('title').value = d.title; $('text').value = d.text; $('text').dispatchEvent(new Event('input'));
  render(d.result); scrollTo({top:0, behavior:'smooth'});
});
$('history').addEventListener('keydown', e => { if (e.key === 'Enter' && e.target.classList.contains('hitem')) e.target.click(); });
loadHistory();
