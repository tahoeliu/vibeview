# Optional composition techniques

Read only when a concrete design need goes beyond the main guide. Do not load this file to start every page, and do not read the underlying stylesheets just to discover class names.

## Lead with attraction and subject-led art direction

Make the subject visually compelling before optimizing production effort. Choose cutaway, editorial illustration, photo collage, or data story according to what the subject needs to reveal, not a preset or fixed style rotation.

The hero visual should depict the actual subject, mechanism, or evidence; a big heading above three cards is not a substitute. Give the opening a clear focal point and a reason to keep reading.

## Build beats around object, change, and insight

Each beat should establish an object, reveal a meaningful change, and make an insight legible. Preserve the object's identity across beats through stable labels, visual traits, and spatial continuity, so readers follow the same thing rather than relearn each scene.

## Extend the background, not the text

Write ordinary headings and sections directly in the fragment. For an edge-to-edge background, use a top-level `<section class="vv-full-bleed">`; its padding aligns the text with ordinary content. Avoid a second outer wrapper. Existing top-level `.vv-wrap` elements do not receive another width deduction. `vv-section` adds vertical space only.

For a fully authored layout, use `--layout custom`. A single wrapped component does not prove that the whole page has safe reading boundaries. `--bare` removes the visual kit, not the reading boundaries; combine it with custom layout only when replacing both deliberately.

## Reuse only the primitives that help

| Need | Available classes |
| --- | --- |
| Text and spacing | `vv-wrap`, `vv-section`, `vv-kicker`, `vv-lead`, `vv-note`, `vv-display`, `vv-serif`, `vv-stack` |
| Layout | `vv-grid` with `--cols`; `vv-split` with `--left`, `--right`, `--vv-gap`; `vv-gap` with `--space`; `vv-inset` with `--pad` |
| Visual surfaces | `vv-stage`, `vv-halo`, `vv-sheet`, `vv-glass`, `vv-tilt`, `vv-orbit`, `vv-dotgrid`, `vv-caption-card`, `vv-sticker`, `vv-orb` |
| Information graphics | `vv-track` / `vv-segment`, `vv-donut` / `vv-donut-core`, `vv-timeline`, `vv-route`, `vv-proof`, `vv-source`, `vv-callout` |

Use `--value` and `--color` for track segments and `--portion` for a donut. Calculate proportions from real data; label the denominator and units. These classes are ingredients, not a page template. Add CSS only for elements actually used.

## Keep visuals explanatory

Choose the representation before the component: do not equate visual explanation with box-and-arrow diagrams. Use subject imagery, spatial grouping, juxtaposition, layers, proportion or typography when they express the idea more elegantly. Do not promote large arrows to a default visual motif. Add an arrow only when its direction conveys necessary information; then label its relationship and keep its visual weight subordinate to the subject. Do not invent a flow to showcase animation or reuse a recipe. Keep annotations clear of prose and graphic edges. Use consistent semantic color, but make distinctions understandable without color alone. Choose a concrete visual analogy only when it preserves the actual relationship.

Allow long English labels to wrap; avoid squeezing them into smaller type. For Chinese, allow adequate character width and line height, and break labels at meaningful phrase boundaries. Do not letter-space Chinese text to imitate an English display heading. Keep mixed-language identifiers readable without forcing the entire page into bilingual text.

Basic shared grids stack on narrow screens. Supply equivalent treatment for custom diagrams, and keep intentionally wide charts or tables in local scroll containers. Do not hide explanations on small screens. Respect reduced-motion preferences and avoid continuous decorative animation.

## Mix precise graphics with approved art

Use SVG for precise geometry, relationships, labels, and data; combine it with approved, embedded real or generated raster art when that improves recognition or explanation. Label factual evidence versus illustration explicitly, including generated or reconstructed imagery, and never present illustrative detail as observed fact.

Asset searches and image-generation calls are not obligatory. Work with available approved material or authored graphics; do not introduce heavy 3D dependencies just to achieve visual appeal.

## Default to effortless normal scrolling

Let ordinary scrolling carry the complete explanation. Do not nudge readers with buttons, dropdowns, or menus to uncover essential content. Add optional interaction only when it has a demonstrable understanding benefit, such as comparing states or testing a relationship; retain a complete static reading path.

## Make motion carry the explanation

Use motion to explain flow, state transition, assembly, or focus: readers should learn what moves, changes, joins, or matters. Avoid decorative loops and motion that merely delays access to information.

Provide explicit static keyframes and captions for the meaningful states, including a reduced-motion presentation. Keep transitions faithful to the underlying facts; identify schematic timing, preserve truthful quantities, and state units wherever measurements appear. Captions must explain the change without requiring playback.

## Review the rendered result with a bounded pass

For complex visuals, review the actual rendered page at desktop and narrow widths; source inspection alone is not sufficient. Check subject recognition, beat continuity, factual labels and units, annotation collisions, clipping, reading order, static states, and reduced-motion behavior. If rendering cannot be reviewed, state that limitation rather than claiming visual QA.

Use a concise, targeted pass to fix observed comprehension and layout defects, then recheck the affected views. Effort is a secondary constraint, not a reason to replace the subject with generic cards; stop when the explanation and rendering hold up, without infinite polishing.
