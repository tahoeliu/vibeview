# Optional explanatory motion

Read only when movement makes a relationship easier to grasp. Keep normal scrolling sufficient; do not add buttons, dropdowns, or menus by default. Use a few subject-specific movements rather than animating the whole page. The small bundled runtime supports seamless route loops and finite illustration, not a simulation engine or a video player.

## Authoring contract

Add `--motion` to the usual composer command. Keep authored `<script>` tags, event handlers, controls, and external resources out of the fragment. The composer injects only its own runtime with a CSP content hash. No network, storage, evaluation, dependencies, or user input are used by that runtime. The static path still emits no script.

Place `data-vv-motion` on SVG graphic objects (`g`, `path`, `line`, `polyline`, `polygon`, `rect`, `circle`, `ellipse`), never prose or captions. Keep HTML captions, units, conclusions, and keyframes visible. The final static SVG must already be correct without JavaScript; do not author invisible initial states. Do not combine transforms/CSS animation and runtime motion on the same element: use a nested `g` for motion instead.

| Kind | Meaning | Authoring |
| --- | --- | --- |
| `flow` | Direction of movement along a route | Dashed `path`, `line`, or `polyline`; supply a literal positive numeric `stroke-dasharray` attribute (not CSS-only). Offset travels one complete dash period to 0; odd-length patterns double their sum. Loop by default; `data-vv-repeat="once"` opts out. Never override the dash pattern in CSS. Add static arrowheads and labels; this is not a measured speed. |
| `assemble` | Parts settle into an explained configuration | Start offset supplied by `data-vv-dx` / `data-vv-dy`; endpoint is the authored position. Useful for assembly or state transitions accompanied by explicit before/after keyframes. |
| `focus` | Briefly emphasize a subject or detail | Scale from 0.94 to 1. Use selectively, not as an entry effect on every object. |

Optional integer attributes: `data-vv-duration` 200..4000 milliseconds (default 1600); `data-vv-delay` 0..800 (default 0); assemble offsets -240..240 (default 0). Limits are per-effect comfort and resource guards, not limits on generation time. `data-vv-repeat` accepts `once` or `loop`; only flow permits looping. Dash periods must be <=4096 SVG units, without zero/negative lengths or units. Maximum 48 animated objects per page; usually 1–6 simultaneous loops suffice. Prefer fewer clear paths over particle fields. Unknown motion attributes or values fail before output publication.

```html
<h1>A route with a visible direction</h1>
<svg viewBox="0 0 480 120" role="img" aria-label="Items flow from source to destination">
  <path d="M40 60 H410" fill="none" stroke="#6366a5" stroke-width="5"
    stroke-dasharray="12 12" data-vv-motion="flow" data-vv-duration="1800"/>
  <path d="M400 48 L420 60 L400 72" fill="none" stroke="#6366a5" stroke-width="5"/>
  <text x="40" y="100">Source</text><text x="340" y="100">Destination</text>
</svg>
<p>Flow is illustrative; distance and animation speed do not represent measured throughput.</p>
```

## Playback and fallback

Start when at least 15% of the object enters view. Flow loops smoothly while visible by default; assembly/focus and explicit once effects release after completion. Pause offscreen or in a hidden tab, resume without restarting, and never hijack scrolling. On a persisted pagehide (back/forward cache), pause; resume on persisted pageshow. Other page exits release animations. No controls are injected. Keep loops subtle and limited to recurring mechanisms or direction cues; never loop accumulating numbers or flashing attention effects. Honor reduced motion and retain static arrows/captions. Do not claim that this control-free runtime alone guarantees accessibility compliance for every continuous animation; add a host-approved stop mechanism or use once/static if the audience or applicable requirements demand it.

With JavaScript disabled, missing browser features, reduced-motion preference, a runtime error, or a non-cached page exit, retain the static endpoint. Switching to reduced motion cancels existing animation immediately and does not restart it when the preference changes back. Printing resets runtime transforms and flow offset. Core content must not depend on seeing the transition; use before/after diagrams where the transition contains an important fact.

## Focused verification

For motion pages, inspect desktop and narrow rendering, run the effect once, and verify static/reduced-motion reading. Check that labels do not move with decorative objects, text does not overlap, and no essential state is absent. Verify no page resource requests or console errors; intentional loops must pause offscreen and under reduced motion. Reserve the complete lifecycle matrix for runtime changes; ordinary pages need only page-specific checks. Fix concrete defects, then stop; do not impose repeated browser cycles on simple static pages. Describe untested behavior honestly.
