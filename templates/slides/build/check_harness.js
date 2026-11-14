(async function(){
  function sleep(ms){return new Promise(r=>setTimeout(r,ms));}
  while(!(window.Reveal && Reveal.isReady && Reveal.isReady())) await sleep(50);
  while(!(window.MathJax && MathJax.startup && MathJax.startup.promise)) await sleep(50);
  await MathJax.startup.promise;
  await document.fonts.ready;
  Reveal.configure({transition:'none', backgroundTransition:'none'});
  const n = Reveal.getTotalSlides();
  const rep = [];
  for (let i=0;i<n;i++){
    Reveal.slide(i);
    await sleep(80);
    const s = Reveal.getCurrentSlide();
    const sc = Reveal.getScale();
    const sr = s.getBoundingClientRect();
    let maxBottom = 0, worst = '';
    const walk = (el) => {
      for (const c of el.children){
        const cs = getComputedStyle(c);
        if (cs.position === 'absolute' || c.tagName === 'ASIDE' || cs.display === 'none') continue;
        const r = c.getBoundingClientRect();
        const b = (r.bottom - sr.top)/sc;
        if (b > maxBottom){maxBottom = b; worst = c.tagName + '.' + (c.className||'').toString().slice(0,40);}
      }
    };
    walk(s);
    const vc = s.querySelector('.vc'); if (vc) walk(vc);
    const wide = [];
    s.querySelectorAll('mjx-container').forEach(m=>{
      let p = m.parentElement;
      while (p && p !== s && getComputedStyle(p).display.indexOf('inline') === 0) p = p.parentElement;
      if (m.getAttribute('display') === 'true') p = m.parentElement.closest('div,li,p,td') || p;
      const inner = m.querySelector('mjx-math') || m;
      const pr = p.getBoundingClientRect(); const r = inner.getBoundingClientRect();
      if (r.right > pr.right + 3*sc) wide.push(Math.round((r.right-pr.right)/sc));
      if (r.right > sr.right - 30*sc) wide.push('edge');
    });
    // text elements (not code) that are wider than their container
    const hov = [];
    s.querySelectorAll('p, li, div.theorem-box, div.definition-box, div.insight-box, div.warning-box, div.danger-box, div.board-box, table').forEach(e=>{
      if (e.closest('pre')) return;
      if (e.scrollWidth > e.clientWidth + 2) hov.push(e.tagName + '.' + (e.className||'').toString().slice(0,25) + ':' + (e.scrollWidth - e.clientWidth));
    });
    rep.push({i: i+1, sh: s.scrollHeight, maxBottom: Math.round(maxBottom), worst, wide, hov: hov.slice(0,4)});
  }
  const pre = document.createElement('pre'); pre.id='overflow-report'; pre.textContent = JSON.stringify(rep);
  document.body.appendChild(pre);
  document.title = 'DONE';
})();
