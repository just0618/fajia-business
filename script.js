const menuBtn=document.querySelector('.menu-btn');
const nav=document.querySelector('.main-nav');
menuBtn?.addEventListener('click',()=>{const open=nav.classList.toggle('open');menuBtn.setAttribute('aria-expanded',String(open));});
nav?.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{nav.classList.remove('open');menuBtn?.setAttribute('aria-expanded','false');}));
const toast=document.getElementById('toast');
function showToast(msg){toast.textContent=msg;toast.classList.add('show');setTimeout(()=>toast.classList.remove('show'),2400)}
document.getElementById('copyEmail')?.addEventListener('click',async()=>{try{await navigator.clipboard.writeText('mejoymedia@foxmail.com');showToast('商务邮箱已复制');}catch{showToast('请手动复制：mejoymedia@foxmail.com')}});
['pdfBtn','pdfBtn2'].forEach(id=>document.getElementById(id)?.addEventListener('click',()=>showToast('PDF版正在制作中；上线后按钮将始终下载最新版')));
document.getElementById('materialBtn')?.addEventListener('click',()=>showToast('商务素材包尚在整理，将根据授权范围提供'));
