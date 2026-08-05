
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
    const res=await fetch('assets/social-data.json',{cache:'no-store'});
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

// V0.18: looped background music with autoplay fallback and a visible pause/play control.
(() => {
  const audio = document.getElementById('siteBgm');
  const toggle = document.getElementById('musicToggle');
  const state = document.getElementById('musicState');
  const action = document.getElementById('musicAction');
  if (!audio || !toggle || !state || !action) return;

  audio.volume = 0.55;
  let userPaused = false;
  let autoplayBlocked = false;

  const render = () => {
    const playing = !audio.paused && !audio.ended;
    toggle.classList.toggle('is-playing', playing);
    toggle.setAttribute('aria-pressed', String(playing));
    action.textContent = playing ? 'Ⅱ' : '▶';
    state.textContent = playing
      ? '循环播放中 · 点击暂停'
      : (autoplayBlocked ? '浏览器已拦截自动播放 · 点击播放' : '已暂停 · 点击播放');
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
    state.textContent = '音频加载失败，请检查文件路径';
    action.textContent = '▶';
  });

  // Most mobile/desktop browsers block audible autoplay. The first ordinary tap
  // on the page is therefore used as a compliant fallback, unless the user has paused it.
  const unlockOnFirstInteraction = async (event) => {
    if (event.target.closest?.('#musicToggle')) return;
    if (audio.paused && !userPaused) await tryPlay();
    if (!audio.paused) {
      document.removeEventListener('pointerdown', unlockOnFirstInteraction);
      document.removeEventListener('keydown', unlockOnFirstInteraction);
    }
  };
  document.addEventListener('pointerdown', unlockOnFirstInteraction);
  document.addEventListener('keydown', unlockOnFirstInteraction);

  render();
  tryPlay();
})();
