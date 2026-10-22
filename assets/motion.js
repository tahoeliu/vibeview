/* VibeView fixed runtime: visible-only flow loops, offline progressive enhancement. */
(() => {
  "use strict";
  const nodes = Array.from(document.querySelectorAll("[data-vv-motion]"));
  if (!nodes.length) return;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  const states = nodes.map(node => ({node, animation: null, visible: false, done: false}));
  let observer;
  const finish = state => {
    state.done = true;
    if (state.animation) state.animation.cancel();
    state.animation = null;
    state.node.dataset.vvState = "static";
    if (observer) observer.unobserve(state.node);
  };
  const update = state => {
    if (state.done) return;
    if (reduced.matches) { finish(state); return; }
    if (!state.visible || document.hidden) {
      if (state.animation) state.animation.pause();
      state.node.dataset.vvState = "paused";
      return;
    }
    try {
      if (!state.animation) {
        const node = state.node;
        const kind = node.dataset.vvMotion;
        let frames;
        if (kind === "flow") {
          const dash = node.getAttribute("stroke-dasharray").trim().split(/[ ,]+/).map(Number);
          const period = dash.reduce((a, b) => a + b, 0) * (dash.length % 2 ? 2 : 1);
          if (!Number.isFinite(period) || period <= 0 || period > 4096 || dash.some(x => x <= 0)) { finish(state); return; }
          frames = [{strokeDashoffset: period}, {strokeDashoffset: 0}];
        }
        else if (kind === "assemble") {
          const x = Number(node.dataset.vvDx || 0);
          const y = Number(node.dataset.vvDy || 0);
          frames = [{transform: `translate(${x}px, ${y}px)`}, {transform: "translate(0px, 0px)"}];
        } else frames = [{transform: "scale(0.94)"}, {transform: "scale(1)"}];
        state.animation = node.animate(frames, {
          duration: Number(node.dataset.vvDuration || 1600),
          delay: Number(node.dataset.vvDelay || 0),
          iterations: kind === "flow" && node.dataset.vvRepeat !== "once" ? Infinity : 1,
          fill: "none", easing: kind === "flow" ? "linear" : "ease-out"
        });
        state.animation.onfinish = () => finish(state);
      } else state.animation.play();
      state.node.dataset.vvState = "running";
    } catch (_) { finish(state); }
  };
  if (!window.IntersectionObserver || !Element.prototype.animate || reduced.matches) {
    states.forEach(finish);
    return;
  }
  const byNode = new Map(states.map(state => [state.node, state]));
  observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      const state = byNode.get(entry.target);
      state.visible = entry.isIntersecting && entry.intersectionRatio >= 0.15;
      update(state);
    });
  }, {threshold: [0, 0.15]});
  states.forEach(state => observer.observe(state.node));
  document.addEventListener("visibilitychange", () => states.forEach(update));
  const onReduce = () => { if (reduced.matches) states.forEach(finish); };
  if (reduced.addEventListener) reduced.addEventListener("change", onReduce);
  else if (reduced.addListener) reduced.addListener(onReduce);
  window.addEventListener("pagehide", event => {
    if (event.persisted) {
      states.forEach(state => {
        if (state.animation) { state.animation.pause(); state.node.dataset.vvState = "paused"; }
      });
    } else { states.forEach(finish); observer.disconnect(); }
  });
  window.addEventListener("pageshow", event => { if (event.persisted) states.forEach(update); });
})();
