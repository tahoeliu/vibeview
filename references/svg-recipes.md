# SVG parts: small geometry, free composition

Use only after choosing a subject-led composition. Treat these parts as implementation utilities, not an art-direction recommendation. Do not default to box-and-arrow diagrams, oversized arrows, or animated routes because they are available. Prefer the representation that is both appealing and faithful to the subject; keep original SVG whenever the parts would constrain it. Output stays plain SVG, offline and inspectable. No browser-side framework, DSL parsing or extra composer mode.

## Minimal use

Add `<skill-directory>/scripts` to Python's module path, then:

```python
from svg_parts import Canvas
c = Canvas('boundary', width=360, height=240, title='设备内的数据边界示意')
c.add(c.region(24, 20, 312, 196, '设备内', tone='oat'))
c.add(c.node(64, 88, 232, 80, '本地副本', tone='surface', note='仅示意存放位置'))
svg = c.render()
# Minimal API demonstration, not a recommended hero composition.
# Put svg inside a trusted body fragment with h1; no motion flag is needed.
```

When directional routes are genuinely needed, draw regions first, routes next, nodes/labels last. The current `route()` helper always adds an arrowhead; do not use it for non-directional relationships. Use grouping, alignment or an authored unheaded line instead. Avoid enlarged arrowheads and long dominant connectors; keep direction marks subordinate to the subject. Keep the route endpoint just outside the target node. A route starts at its first point and has an arrow at its last point. Flow uses the same static arrow plus a literal `12 12` dash pattern, loops by default, and requires `--motion`. Labels never move. Do not put labels directly over a route; supply `label_at` when needed.

## Small API

All methods return strings, except `add` returns the Canvas. Explicitly add each returned component. Repeated `render()` is deterministic and does not mutate the canvas.

| Method | Use |
| --- | --- |
| `Canvas(prefix, width=360, height=360, title='图解')` | One unique ASCII prefix per SVG in the final page; mandatory meaningful title. |
| `node(x,y,w,h,label,tone='sage',note=None)` | Rounded surface with centered text; label and note may contain explicit newlines. |
| `label(x,y,text,anchor='middle',note=False)` | x/y anchor the text block center vertically, not its first baseline. |
| `route(points,tone='ink',flow=False,repeat='loop',label=None,label_at=None)` | 2–32 points; straight/orthogonal/polygonal route, not auto obstacle avoidance. |
| `region(x,y,w,h,label,tone='oat')` | Background grouping or boundary, not a security guarantee. |
| `stack(x,y,w,h,labels,tone='slate',gap=10)` | 1–4 vertically expanded layers; h is per layer; adds a non-proportional disclaimer. |
| `badge(x,y,text,tone='oat')` | Radius-16 sequence marker; use one or two short characters. |
| `dot(x,y,tone='sage',r=6)` | Junction or status mark; add a textual meaning where needed. |
| `bracket(x1,x2,y,label)` | Upward-open bracket with caption below; no arrow. |
| `add(*parts)` / `render()` | Up to 512 trusted strings; output goes through the normal composer. |

Surface tones: `sage/clay/slate/oat/surface`. Route tones: `ink/accent/secondary`. Dot accepts all eight. Theme colors use existing variables, not semantic red/green meanings. Mark data categories with text as well as color.

Coordinates are finite numbers in -4096..4096; sizes are positive and at most 4096. Reject bool, non-numeric strings, NaN and infinity. Text fields are escaped and limited to 500 characters; no silent truncation. This is not auto-fit: manually wrap labels and choose sufficient dimensions. A long legal string can still overflow a small box. The composer catches duplicate IDs and missing references but cannot prove visual fit. `add` is only for trusted authored SVG, not external HTML.

## Reuse a local composition

`examples/svg-recipes.py` provides `branch`, `cycle`, `layers`, `boundary`, `before_after`, and `fan_in`, each with a unique-prefix parameter. Use their source as editable geometry, not as factual content. Change labels, route points and captions to match evidence. Two instances of the same function need different prefixes.

To inspect all six once:

```bash
python3 -B <skill-directory>/examples/svg-recipes.py NEW.fragment.html
python3 -B <skill-directory>/scripts/compose.py NEW.fragment.html NEW.html --title 'SVG 样板' --lang zh-CN --motion
```

Both output files must be new, in an existing authorized directory. Do not emit the six-example catalog for ordinary reader requests.

## Shared optional styles

Normal composition embeds the CSS. Do not read/copy the stylesheet. Builder shapes include explicit fills/strokes; the kit adds consistent label typography, region boundaries and wrappers.

- `vv-diagram`, `vv-diagram-frame`: fluid SVG; frame caps desktop width at 480px.
- `vv-part-node/label/note/line/region/badge/dot`: builder classes, scoped without changing old SVG classes.
- `vv-part-outline`: unfilled meaningful boundary; `vv-part-guide`: dashed guide, not a data series.
- `vv-part-halo`: light outline behind text for local line crossings; not an excuse to overlap labels.
- `vv-part-number`: tabular large value; supply units and factual denominator nearby.

Keep literal dasharray on animated paths. No CSS animation, arbitrary script or transform override on motion nodes. Arrow markers are namespaced per SVG and per tone, avoiding `context-stroke` compatibility dependence. Narrow scaling still shrinks text: start from a 360-unit diagram, inspect at 390px and optionally 320px; simplify before shrinking labels. Keep diagrams and captions visible under reduced motion and without JavaScript. Existing page checks suffice unless code changes require full regression.
