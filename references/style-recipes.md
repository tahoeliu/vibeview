# Material skins and composable recipes

Read this interface first; inspect only relevant selectors, not every CSS file.
Let the composer embed `assets/design.css` and the existing reading shell; do not read or copy the CSS.
Use default `--theme morandi`; explicit violet, blue, sage and amber preserve their old palettes. Never put a body wrapper in a fragment.
Material skins are reusable. The main visual's meaning, evidence and composition still require original design.
These fragments are optional combinations, not mandatory page templates.
Morandi means muted hues, not automatic sophistication and never low contrast.

## Tokens and local parameters
- Theme: `--vv-bg/ink/muted/accent/soft/secondary/tint/line/shadow` (each expands to a full `--vv-*` name).
- Surfaces: `--vv-surface`, `--vv-sage`, `--vv-clay`, `--vv-slate`, `--vv-oat`.
- Graphics: `--vv-graph-ink`, `--vv-graph-line`; captions: `--vv-caption-ink`.
- `vv-editorial`: two columns; `--editorial-copy/art` (track sizes), `--editorial-gap/align`.
- `vv-mosaic`: auto-fit grid; `--mosaic-min/gap`. No implicit spanning or visual reordering.
- `vv-panel`: `--panel-pad/bg/radius/shadow`; `vv-paper`: `--paper-base/wash`, a light CSS gradient.
- `vv-frame`: `--frame-bg/pad/radius/ratio`; ratio defaults to auto and never clips content.
- `vv-figure`: use on a figure or root SVG; SVG width is 100%, height auto. Supply a viewBox.
- `vv-beat`: explicit index plus content; `--beat-index-width/gap/space`; `vv-beat-index`: `--beat-index-size`.
- `vv-rule`: `--rule-space/color`; decorative separator, not a data boundary.
- `vv-metric`: `--metric-gap`; `vv-metric-value`: `--metric-size/color`; `vv-metric-label`: dark caption.
- `vv-bar-row`: `--bar-label-width/gap`; `vv-bar-label`: visible name and value.
- `vv-bar-track`: `--bar-height/track-color`; `vv-bar-fill`: `--value` (unitless 0..100), `--bar-color`.
- Bar fill uses `width: calc(var(--value, 0) * 1%)`, not flex; put `--value` on each fill.
- `vv-palette`: `--palette-min/gap`; `vv-swatch`: `--color`, `--swatch-height/radius`; text stays outside the chip.
- SVG: `vv-svg-label/note/line/node/flow`; `--svg-text/font-size/stroke/stroke-width/fill`.
- SVG label/note defaults: 20px/18px, minimum 18px in SVG units; flow dashes: `12 12`, no animation.
- `vv-space-before/after`: `--space-before/after`; `vv-pad-block`: `--pad-block`.
Set complete variable names on the component that consumes them, e.g. `--panel-pad:24px`.
SVG variables may inherit from a containing group; use local overrides for individual marks.
At <=760px editorial, mosaic, beat and bar rows stack in DOM order; palette remains auto-fit.
All compositions stay inside their parent; no viewport-width breakout or reading-shell overrides.
Allow long Chinese text to wrap. SVG text needs authored tspan lines and sufficient viewBox space.
An 18-unit SVG font can render smaller when scaled: check the actual mobile size and simplify the visual.

## 1. Editorial material and an authored illustration
```html
<section class="vv-editorial">
  <div class="vv-stack"><h2>Explain one relationship</h2><p>Supply the claim and evidence.</p></div>
  <figure class="vv-frame vv-paper vv-figure">
    <svg viewBox="0 0 300 160" role="img" aria-labelledby="recipe-art-title">
      <title id="recipe-art-title">Placeholder for an original relationship diagram</title>
      <rect class="vv-svg-node" x="12" y="12" width="276" height="136" rx="12"/>
      <text class="vv-svg-label" x="30" y="86">Author the visual here</text>
    </svg>
    <figcaption>Replace the placeholder with a meaningful illustration.</figcaption>
  </figure>
</section>
```

## 2. Variable mosaic and metrics
```html
<div class="vv-mosaic" style="--mosaic-min:220px">
  <article class="vv-panel vv-metric"><strong class="vv-metric-value">42</strong><p class="vv-metric-label">Illustrative count, not research data</p></article>
  <article class="vv-panel vv-paper"><h3>Context</h3><p>Explain the unit, scope and source.</p></article>
</div>
```

## 3. Numbered section and a non-flex bar
```html
<section class="vv-beat">
  <span class="vv-beat-index">01</span>
  <div><h2>Compare a stated measure</h2>
    <div class="vv-bar-row vv-space-before">
      <span class="vv-bar-label">Example completion: 64%</span>
      <div class="vv-bar-track" aria-hidden="true"><span class="vv-bar-fill" style="--value:64"></span></div>
    </div>
    <hr class="vv-rule"><p class="vv-metric-label">Illustrative only; provide a source for real values.</p>
  </div>
</section>
```

## 4. Palette with readable external labels
```html
<div class="vv-panel vv-palette" style="--palette-min:110px">
  <div class="vv-swatch" style="--color:var(--vv-sage)">Sage</div>
  <div class="vv-swatch" style="--color:var(--vv-clay)">Clay</div>
  <div class="vv-swatch" style="--color:var(--vv-slate)">Slate</div>
  <div class="vv-swatch" style="--color:var(--vv-oat)">Oat</div>
</div>
```

## Contrast contract
Morandi ink, muted, accent and secondary must meet WCAG AA 4.5:1 on the eight supplied light backgrounds:
`bg`, `surface`, `soft`, `tint`, `sage`, `clay`, `slate`, `oat`. Never fade body text or notes with opacity.
The paper gradient stays between surface and oat; custom washes and color overrides require a fresh check.
Use graph-line for meaningful boundaries (3:1 minimum); theme line is decorative only.
Keep graph-ink text on light node fills; do not use pastel swatches as text or assume color alone carries meaning.
Legacy palettes are preserved, not retroactively certified. Recheck their custom combinations separately.
