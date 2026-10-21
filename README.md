<div align="center">

# VibeView

### Turn long AI answers into visual explanations people want to read.

An open-source Agent Skill that transforms the context and results already in your conversation into a polished, standalone HTML page.

**One Skill · `vv` in your conversation · One portable HTML file**

[See the real output](#see-it-in-action) · [Install the skill](#install) · [Build the example](#build-the-example-without-an-agent) · [Understand the limits](#scope-and-limitations) · [Chinese](README.zh-CN.md)

</div>

![VibeView 1.5.2 output: a request sequence diagram explains timeouts, retries, and idempotency keys](docs/preview.png)

> This is a screenshot of output built with this repository's 1.5.2 composer, not a mockup. The engineering scenario is fictional. An Agent authored the visual content; Python assembled the page. Results vary by model, source material, and prompt.

## From “answered” to “understood”

AI can produce a long answer. The hard part is often not missing text; it is the relationships buried inside it. Which option fits which situation? What does one failure affect? Which assumptions support the conclusion?

VibeView gives an Agent visual storytelling guidance and a lightweight HTML builder. **Start with the relationship the reader most needs to understand, then design the visual around the content.** It does not put every paragraph in a generic card or hide important details behind tabs.

```text
vv summarize the analysis so far and make the key conclusion and evidence clear

vv show how these two options differ, when each fits, and what each costs

vv explain the retry mechanism we discussed, including failure paths and limits
```

Type `vv` in a conversation with an Agent that supports local Skills. **It is a natural-language convention, not a terminal command.**

## See it in action

The example answers one question: **After a client timeout, why shouldn’t you retry with a new key?**

| What was buried in prose | How VibeView makes it visible |
| --- | --- |
| A request succeeded, but its receipt never arrived | A sequence diagram separates server state from what the client knows |
| A retry of the same operation versus a genuinely new operation | Side-by-side relationship diagrams show when requests converge and when they stay separate |
| A key reused with different parameters, an in-progress request, and an expired record | The complete rules table keeps the edge cases visible |
| Idempotency is not an unconditional promise to execute only once | Concurrency, atomicity, and retention are explained as separate requirements |

**[Read the source material](examples/reading-map.input.md) → [Explore the visual page](examples/reading-map.fragment.html) → [Download the standalone HTML](docs/index.html)**

GitHub renders the HTML file as source. Download it and open it in a browser, or build it locally with the command below. There is no hosted live demo advertised here.

## Why an Agent Skill?

You are already discussing the problem with an Agent, and the answer is already in the conversation. VibeView helps make that answer easier to understand without moving it to another editor and laying it out again.

- **Continue the current conversation.** Use the existing instructions, context, and results; do not repeat research or write a second report by default.
- **Make relationships visible.** The Agent creates subject-specific diagrams, comparisons, and reading hierarchy. The design primitives do not impose a page layout.
- **Emphasize the key idea while keeping details in view.** Explanations, tables, and relevant sources can appear together on one page.
- **Deliver one portable file.** The composer embeds styles. The default output needs no JavaScript, remote fonts, or server.
- **Spend effort on the content.** Reuse the brand shell, typography, and visual primitives so design effort goes into the explanation itself.

**Good for:** explaining technical mechanisms, comparing options, reviewing a process, and presenting analysis already completed.

**Not intended for:** live business systems, interactive dashboards, rigid pixel-perfect templates, or research that requires automatic fact-checking. Short answers do not need a webpage.

## Install

### Requirements

- An Agent host that can load a local `SKILL.md` and run local scripts. This project was built for **WorkBuddy**.
- Python 3. The validation environment for this release was Python 3.13.12 on macOS. The scripts use only the standard library; no `pip install` is needed.
- Git for the command below. You can also download the ZIP and copy it into the Skills directory manually.

### Install in WorkBuddy

Run this in a macOS or Linux terminal:

```bash
git clone https://github.com/tahoeliu/vibeview.git "$HOME/.workbuddy/skills/vibeview"
```

The destination directory must not already exist; do not overwrite an existing installation. If SSH is configured, you can use the repository's SSH clone URL instead.

> **Already using VibeView, VibePreview, or TahoeView?** First locate the old Skill in your host. The author's former installation directory was named `tahoeview`, while the Skill itself was already named `vibeview`. Do not load both copies at once. Back up and disable the old copy before installing this one. The command above does not migrate or remove an older version.

Ask WorkBuddy to reload local Skills. If it does not recognize the Skill, restart the app or start a new session. Then try:

```text
vv explain how a timeout retry can create a duplicate operation, including concurrency and expiration limits
```

The Agent authors HTML/SVG from the available material and invokes the local builder. The host and task determine where the result is saved and how it is previewed.

Other hosts that support local Skills may be able to load this folder, but compatibility has not been verified host by host. Copying `SKILL.md` alone is not sufficient; keep `scripts/`, `assets/`, and `references/` alongside it.

## Build the example without an Agent

Clone the project into a new directory, then run:

```bash
git clone https://github.com/tahoeliu/vibeview.git
cd vibeview
python3 -B scripts/compose.py examples/reading-map.fragment.html preview.html \
  --title "After a timeout, don't do the same thing twice" --theme violet
```

Open `preview.html` in a browser. On macOS:

```bash
open preview.html
```

**Choose a new output filename each time.** The tool refuses to overwrite an existing file, and the output directory must already exist.

This reproduces the pre-authored example; **Python does not turn Markdown into diagrams.** To create new visual content, use an Agent or write an HTML fragment yourself.

## How it works

```text
Your instruction + material already in the conversation
                         ↓
Agent identifies the point and authors HTML / SVG plus optional CSS
                         ↓
compose.py checks the fragment, embeds base styles, and adds the brand shell
                         ↓
One new HTML file → read it in a browser
```

The default path does not prescribe a page template. Four base themes are available: `violet`, `blue`, `sage`, and `amber`. You can override styles or use `--bare` to keep only the brand shell.

```bash
python3 -B scripts/compose.py your-fragment.html your-page.html \
  --title "Your topic" --theme sage
```

The fragment must include its own `<h1>` and must not include full-page `html/head/body/main/header/footer` wrappers. Use it only for trusted content you or an Agent have newly authored.

Regular, structured comparisons can also use the [JSON component path](references/template.md). It is an option, not the default way to compose a page.

## Scope and limitations

| Boundary | What it means |
| --- | --- |
| Desktop-first reading | The example includes a narrow-screen layout; that does not mean the Skill is fully adapted to every mobile device. |
| Not a Markdown parser | In version 1.5.2, `compose.py` accepts an HTML fragment. Markdown may be input material for the Agent. |
| Not an HTML sanitizer | Static checks cannot make arbitrary external HTML safe. Do not pass untrusted webpages directly to the composer. |
| Local build does not mean the whole workflow is offline | Model requests depend on the Agent host. Handle sensitive material according to your model and privacy settings. |
| Diagrams are not fact-checking | Check data, sources, assumptions, and conclusions. A diagram must not be used to manufacture evidence. |
| A file is not a deployment | This tool creates a local HTML file. Uploading or hosting it requires a separate action; check for sensitive content before sharing. |
| Results depend on authorship | There is no guarantee that every page will look equally good and no unmeasured speedup claim. |

## Release and feedback

Current release: **1.5.2**, a minimal fix on the author's installed 1.5.1 stable version. It does **not** include 1.7.0 or experimental Next code.

This release uses the actual HTML title instead of text matching, checks local CSS/SVG references, and reports success with a clear warning if the output was created but temporary-file cleanup failed. An exception may still leave a temporary file; inspect the path in the warning and do not modify a staging file that shares content with the finished output.

The release completed 100 isolated regression cases on Python 3.13.12 / macOS, covering theme combinations, input boundaries, concurrent conflicts, and fault injection. This is not a guarantee of cross-platform behavior, long-running reliability, or safety for arbitrary untrusted HTML.

If you encounter an output error, open an [issue](https://github.com/tahoeliu/vibeview/issues) with the version, Python and OS versions, command, error message, and a minimal reproducible example you can share publicly. Do not upload keys, tokens, or business-confidential material.

Contributions that improve diagram examples, documentation, or reproducible bug reports are welcome. If VibeView helped you explain a difficult topic, consider starring the project or sharing a sanitized example.

## License

[MIT](LICENSE) © 2026 tahoeliu.
