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
      const v=getPath(data,path);
      if(v!==undefined)el.textContent=displayValue(v,el);
    });
    const note=document.getElementById('socialUpdated');
    if(note&&data.updated){const [y,m,d]=data.updated.split('-'); note.textContent=`数据截至 ${y}年${Number(m)}月${Number(d)}日；粉丝数为平台公开数据，跨平台未去重。`;}
  }catch(_){/* file:// 预览时保留 HTML 内置数值 */}
}
hydrateSocialData();
