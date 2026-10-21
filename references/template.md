# Optional JSON renderer

Use this renderer for regular, structured content that the supplied components can represent faithfully. For a custom explanation, use `compose.py` instead. Choose based on the content; a template trial is not required.

```bash
python3 <skill-directory>/scripts/render.py <content.json> <new-page.html>
```

The output directory must exist, and the destination file must be new. All fields contain plain text unless explicitly marked as HTML. The renderer assembles the page; it does not interpret the data or check the conclusions.

## Page fields

- `title`: required, non-empty page title.
- `blocks`: required array of content blocks.
- `subtitle`, `meta`: optional text.
- `language`: `en` (default) or `zh-CN`.
- `theme`: `blue`, `sage`, `amber`, or `violet`.

## Blocks

Blocks share the fields `type`, `title`, `text` (a string or an array of paragraphs), `note`, `variant` (`plain` or `tinted`), and `columns` (1–4).

| Type | Content |
| --- | --- |
| `prose`, `callout` | `text` |
| `compare` | `items` with `title`, `text`, and an optional `label` |
| `metrics` | `items` with `value`, `title`, and `text` |
| `flow`, `timeline` | `items` with `title`, `text`, and an optional `label` |
| `findings` | `items` with `title` and `text`; optional `label`, `action`, and `source` |
| `bars` | `items` with `title` and a nonnegative `value`; optional `unit`. Bars use a zero-based linear scale. Negative values and stacking are unsupported. |
| `sources` | `items` with `title`, `text`, and `url`. Use HTTP(S) URLs without embedded credentials. |
| `custom` | `html` containing the supported static HTML/SVG subset. No styles, scripts, event handlers, or external resources. SVG IDs must begin with `custom-` and be unique across the page. |

```json
{
  "title": "Two options, different trade-offs",
  "theme": "blue",
  "blocks": [
    {
      "type": "compare",
      "items": [
        {"title": "Option A", "text": "Explain its strengths and constraints."},
        {"title": "Option B", "text": "Explain when the alternative fits better."}
      ]
    }
  ]
}
```

The renderer performs its own assembly checks. Follow any checks required by the host or user, without adding another review workflow by default.
