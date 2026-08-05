
function renderTMinusOne(){
  const date=new Date();
  date.setHours(12,0,0,0);
  date.setDate(date.getDate()-1);
  const zh=`${date.getFullYear()}年${date.getMonth()+1}月${date.getDate()}日`;
  const dot=`${date.getFullYear()}.${String(date.getMonth()+1).padStart(2,'0')}.${String(date.getDate()).padStart(2,'0')}`;
  document.querySelectorAll('[data-tminus-one]').forEach(el=>{
    el.textContent=el.closest?.('.preview-chip')?dot:zh;
  });
}
renderTMinusOne();
const menuBtn=document.querySelector('.menu-btn');
const nav=document.querySelector('.main-nav');
menuBtn?.addEventListener('click',()=>{const open=nav.classList.toggle('open');menuBtn.setAttribute('aria-expanded',String(open));});
nav?.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{nav.classList.remove('open');menuBtn?.setAttribute('aria-expanded','false');}));
const toast=document.getElementById('toast');
function showToast(msg){if(!toast)return;toast.textContent=msg;toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),2400)}
document.getElementById('copyEmail')?.addEventListener('click',async()=>{try{await navigator.clipboard.writeText('mejoymedia@foxmail.com');showToast('商务邮箱已复制');}catch{showToast('请手动复制：mejoymedia@foxmail.com')}});
function getPath(obj,path){return path.split('.').reduce((v,k)=>v===undefined||v===null?null:v[k],obj)}
function sumKnown(values){
  const known=values.filter(v=>typeof v==='number'&&Number.isFinite(v));
  return known.length?known.reduce((a,b)=>a+b,0):null;
}
function compactNumber(value){
  if(value===null||value===undefined||value==='')return '—';
  if(typeof value==='string')return value;
  const n=Number(value); if(!Number.isFinite(n))return '—';
  const trim=x=>String(Number(x.toFixed(1)));
  if(Math.abs(n)>=100000000)return `${trim(n/100000000)}亿`;
  if(Math.abs(n)>=10000)return `${trim(n/10000)}万`;
  return n.toLocaleString('zh-CN');
}
function displayValue(value,el){
  let text=el.dataset.format==='raw' ? (value??'—') : compactNumber(value);
  if(value!==null&&value!==undefined&&value!==''&&el.dataset.suffix)text+=el.dataset.suffix;
  return text;
}
function computeSummary(data){
  const p=data.platforms||{};
  const artistFollowers=sumKnown([
    p.douyin?.faxuange?.followers,p.douyin?.hejiashu?.followers,
    p.weibo?.faxuange?.followers,p.weibo?.hejiashu?.followers,
    p.xhs?.faxuange?.followers,p.xhs?.hejiashu?.followers
  ]);
  const douyinArtistLikes=sumKnown([p.douyin?.faxuange?.engagement,p.douyin?.hejiashu?.engagement]);
  const d=Object.values(data.content?.douyin||{});
  const w=Object.values(data.content?.weibo||{});
  const visibleDouyinComments=sumKnown(d.map(x=>x.comments));
  const visibleWeiboReposts=sumKnown(w.map(x=>x.reposts));
  const visibleWeiboInteractions=sumKnown(w.flatMap(x=>[x.likes,x.comments,x.reposts]));
  data.summary={...(data.summary||{}),threePlatformArtistFollowers:artistFollowers,douyinArtistLikes,visibleDouyinComments,visibleWeiboReposts,visibleWeiboInteractions};
  return data;
}
async function hydrateSocialData(){
  try{
    const res=await fetch(`assets/social-data.json?v=${Date.now()}`,{cache:'no-store'});
    if(!res.ok)return;
    const data=computeSummary(await res.json());
    document.querySelectorAll('[data-social-path],[data-metric-path],[data-summary-path]').forEach(el=>{
      const path=el.dataset.socialPath||el.dataset.metricPath||el.dataset.summaryPath;
      let v=getPath(data,path);
      // The third Douyin card changed from a video URL to a new note URL in V0.20.
      // Do not show the former post's cached metrics while the scheduled scraper is
      // still waiting to refresh social-data.json.
      if(path.startsWith('content.douyin.item03.') && data.content?.douyin?.item03?.url!=='https://www.douyin.com/note/7670451363546191754')v=null;
      if(v!==undefined)el.textContent=displayValue(v,el);
    });
    renderTMinusOne();
  }catch(_){/* file:// 预览时保留 HTML 内置数值 */}
}
hydrateSocialData();

// V0.24: compact left-side, draggable, collapsible background music player.
(() => {
  const player = document.getElementById('musicPlayer');
  const audio = document.getElementById('siteBgm');
  const toggle = document.getElementById('musicToggle');
  const state = document.getElementById('musicState');
  const action = document.getElementById('musicAction');
  const handle = document.getElementById('musicDockHandle');
  if (!player || !audio || !toggle || !state || !action || !handle) return;

  audio.volume = 0.5;
  let userPaused = false;
  let autoplayBlocked = false;
  let dragging = false;
  let moved = false;
  let pointerId = null;
  let startPointerX = 0;
  let startPointerY = 0;
  let startLeft = 0;
  let startTop = 0;

  const positionKey = 'fajiaMusicPositionV24';
  const collapsedKey = 'fajiaMusicCollapsedV24';
  const storedCollapsed = localStorage.getItem(collapsedKey);
  const shouldCollapse = storedCollapsed === null ? true : storedCollapsed === 'true';

  const clamp = (value, min, max) => Math.min(Math.max(value, min), Math.max(min, max));

  const savePosition = () => {
    const rect = player.getBoundingClientRect();
    localStorage.setItem(positionKey, JSON.stringify({ left: rect.left, top: rect.top }));
  };

  const placeAt = (left, top) => {
    const margin = 6;
    const maxLeft = window.innerWidth - player.offsetWidth - margin;
    const maxTop = window.innerHeight - player.offsetHeight - margin;
    player.style.left = `${clamp(left, margin, maxLeft)}px`;
    player.style.top = `${clamp(top, margin, maxTop)}px`;
    player.style.right = 'auto';
    player.style.bottom = 'auto';
    player.classList.add('has-custom-position');
  };

  const restorePosition = () => {
    try {
      const saved = JSON.parse(localStorage.getItem(positionKey) || 'null');
      if (saved && Number.isFinite(saved.left) && Number.isFinite(saved.top)) {
        requestAnimationFrame(() => placeAt(saved.left, saved.top));
      }
    } catch (_) {}
  };

  const keepInsideViewport = () => {
    if (!player.classList.contains('has-custom-position')) return;
    const rect = player.getBoundingClientRect();
    placeAt(rect.left, rect.top);
    savePosition();
  };

  const setCollapsed = (collapsed) => {
    player.classList.toggle('is-collapsed', collapsed);
    handle.setAttribute('aria-expanded', String(!collapsed));
    handle.setAttribute('aria-label', collapsed ? '拖动或展开侧边音乐播放器' : '拖动或收起侧边音乐播放器');
    handle.querySelector('span').textContent = collapsed ? '›' : '‹';
    localStorage.setItem(collapsedKey, String(collapsed));
    requestAnimationFrame(keepInsideViewport);
  };

  const render = () => {
    const playing = !audio.paused && !audio.ended;
    toggle.classList.toggle('is-playing', playing);
    toggle.setAttribute('aria-pressed', String(playing));
    action.textContent = playing ? 'Ⅱ' : '▶';
    state.textContent = playing
      ? '循环播放中'
      : (autoplayBlocked ? '点击播放' : '已暂停');
  };

  const tryPlay = async () => {
    if (userPaused) return false;
    try {
      await audio.play();
      autoplayBlocked = false;
      render();
      return true;
    } catch (_) {
      autoplayBlocked = true;
      render();
      return false;
    }
  };

  handle.addEventListener('pointerdown', (event) => {
    if (event.button !== undefined && event.button !== 0) return;
    const rect = player.getBoundingClientRect();
    dragging = true;
    moved = false;
    pointerId = event.pointerId;
    startPointerX = event.clientX;
    startPointerY = event.clientY;
    startLeft = rect.left;
    startTop = rect.top;
    handle.setPointerCapture?.(pointerId);
    player.classList.add('is-dragging');
    event.preventDefault();
  });

  handle.addEventListener('pointermove', (event) => {
    if (!dragging || event.pointerId !== pointerId) return;
    const dx = event.clientX - startPointerX;
    const dy = event.clientY - startPointerY;
    if (Math.hypot(dx, dy) > 5) moved = true;
    if (!moved) return;
    placeAt(startLeft + dx, startTop + dy);
    event.preventDefault();
  });

  const finishDrag = (event) => {
    if (!dragging || (event.pointerId !== undefined && event.pointerId !== pointerId)) return;
    dragging = false;
    player.classList.remove('is-dragging');
    try { handle.releasePointerCapture?.(pointerId); } catch (_) {}
    pointerId = null;
    if (moved) {
      savePosition();
    } else {
      setCollapsed(!player.classList.contains('is-collapsed'));
    }
  };

  handle.addEventListener('pointerup', finishDrag);
  handle.addEventListener('pointercancel', finishDrag);

  toggle.addEventListener('click', async () => {
    if (audio.paused) {
      userPaused = false;
      await tryPlay();
    } else {
      userPaused = true;
      audio.pause();
      render();
    }
  });

  audio.addEventListener('play', render);
  audio.addEventListener('pause', render);
  audio.addEventListener('error', () => {
    autoplayBlocked = true;
    state.textContent = '音频不可用';
    action.textContent = '▶';
  });

  const unlockOnFirstInteraction = async (event) => {
    if (event.target.closest?.('#musicPlayer')) return;
    if (audio.paused && !userPaused) await tryPlay();
    if (!audio.paused) {
      document.removeEventListener('pointerdown', unlockOnFirstInteraction);
      document.removeEventListener('keydown', unlockOnFirstInteraction);
    }
  };

  document.addEventListener('pointerdown', unlockOnFirstInteraction);
  document.addEventListener('keydown', unlockOnFirstInteraction);
  window.addEventListener('resize', keepInsideViewport);

  setCollapsed(shouldCollapse);
  restorePosition();
  render();
  tryPlay();
})();
