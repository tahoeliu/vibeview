# Conditional JSON component path

Use this path only when the content is regular, the components can express it fully and accurately, and the resulting layout will not be monotonous or lower quality. Do not use a template just because the fields can contain the content; no template trial is required. For unsuitable material, compose freely with `compose.py` or write complete HTML.

`python <skill-directory>/scripts/render.py <content.json> <new-output.html>`

Top-level fields: `title`, optional `subtitle`, `meta`, `language` (`en` by default or `zh-CN`), `theme` (`blue` / `sage` / `amber` / `violet`), and a `blocks` array. Blocks share `type`, `title`, `text` (string or paragraph array), `note`, `variant` (`plain` / `tinted`), and `columns` (1–4). Ordinary fields are plain text.

- `prose` / `callout`: `text`.
- `compare`: `items` with `title` / `text`, optional `label`.
- `metrics`: `items` with `value` / `title` / `text`.
- `flow` / `timeline`: `items` with `title` / `text`, optional `label`.
- `findings`: `items` with `title` / `text`, optional `label` / `action` / `source`.
- `bars`: `items` with `title` / nonnegative `value`, optional `unit`; zero-based linear bars only, no negative values or stacking.
- `sources`: `items` with `title` / `text` / `url`; URLs must be credential-free HTTP(S).
- `custom`: `html` is a restricted static HTML/SVG subset; no `style`, scripts, events, or external resources. SVG ids must start with `custom-` and be unique on the page.

Example: `{"title":"Two options","theme":"blue","blocks":[{"type":"compare","items":[{"title":"A","text":"Evidence"},{"title":"B","text":"Trade-off"}]}]}`

The script mechanically assembles pages. It does not infer the meaning of data or validate business conclusions. The output directory must exist and the output file must not. Assembly checks are included; do not launch a separate check workflow.
