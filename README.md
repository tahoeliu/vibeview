<div align="center">

<img src="assets/vibeview-mark.svg" alt="VibeView" width="64" height="64" />

# VibeView

### Make AI answers easier to understand—and more enjoyable to read.

An open-source **Agent Skill** that turns long AI answers into clear visual explanations, right from your conversation.

[**Get started**](#get-started) · [Live demo ↗](https://tahoeliu.github.io/vibeview/) · [Compare skills](#compare-visual-skills) · [简体中文](README.zh-CN.md)

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-7041b5?style=flat-square)](https://agentskills.io/home) [![Python 3](https://img.shields.io/badge/Python-3-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/) [![MIT](https://img.shields.io/badge/License-MIT-326f62?style=flat-square)](LICENSE)

</div>

![The same explanation in two forms: a dense paragraph about retries, and a visual showing two requests resolving to one saved result.](assets/readme-before-after.svg)

Your AI has the answer. You still have to make sense of it.

VibeView gives that answer a visual structure: show how a process works, put two options side by side, or connect a conclusion to its evidence. It uses the context and work already in the chat, with the important details still there to read.

```text
vv make the explanation above easier to understand
```

## See a real example

**Why can retrying after a timeout create duplicate work?** This example makes the request sequence visible, then walks through the rules and their limits.

[![An actual VibeView output: an English visual guide to API timeouts, retries, and idempotency keys, with a request sequence diagram.](https://tahoeliu.github.io/vibeview/)](https://tahoeliu.github.io/vibeview/)

<p align="center">
  <a href="https://tahoeliu.github.io/vibeview/"><strong>Open the live demo ↗</strong></a> ·
  <a href="examples/reading-map.fragment.html">Page source</a> ·
  <a href="examples/reading-map.input.md">Original question and answer</a>
</p>

This is a screenshot of a page built with the included composer. The scenario is fictional; the output is real. Explore the live demo or [build it locally](#build-the-example).

## What would you like to make clear?

![Three ways to use VibeView: explain a process with a sequence, compare options with a branching diagram, and connect evidence to a conclusion.](assets/readme-use-cases.svg)

```text
vv show how this works, including the failure paths
vv compare these options and make the trade-offs clear
vv turn our analysis into a visual guide, keeping the evidence and caveats
```

- **A layout that fits the idea.** The agent designs around the subject instead of filling a fixed page template.
- **The explanation stays intact.** Diagrams share the page with the details, tables, and sources. Readers can follow everything by scrolling.
- **Use the work you already have.** Start from the current conversation, without preparing a separate report or moving to another editor.

## Get started

VibeView uses the [open Agent Skills format](https://agentskills.io/home). It works with compatible harnesses that can load local skills, create files, and run **Python 3**. No Python packages are required.

```bash
git clone https://github.com/tahoeliu/vibeview.git
```

Move the complete `vibeview` folder into your harness’s skills directory, then reload skills as your harness requires. Keep `SKILL.md`, `scripts/`, `assets/`, and `references/` together.

Continue a conversation and ask:

```text
vv explain the analysis above visually. Keep the key points, evidence, and trade-offs.
```

`vv` is a prompt convention understood by the skill. Type it in your agent conversation. The agent writes the explanation and visuals, then uses the local builder to create the page. Short answers can stay as text.

<a name="build-the-example"></a>

<details>
<summary><strong>Build the example</strong></summary>

From the repository directory, run:

```bash
python3 -B scripts/compose.py examples/reading-map.fragment.html preview.html \
  --title "Retry the request. Reuse the result." --theme violet
```

Open `preview.html` in a browser. Choose a new output filename for each build: the composer refuses to overwrite files. It assembles an authored HTML fragment; the agent creates the explanation and diagrams.

</details>

## Compare visual skills

Several excellent skills cover this space. Their capabilities overlap; the main difference is which workflow they emphasize.

| Skill | Main focus |
| --- | --- |
| **VibeView** | Making an explanation already in your conversation easier to follow, with a custom visual structure and the supporting detail on one scrollable page. |
| [visual-explainer](https://github.com/nicobailon/visual-explainer) | Rich visual pages and slide decks, with dedicated workflows for architecture, diff reviews, plan audits, data tables, and project recaps. |
| [visualise](https://github.com/bentossell/visualise) | Interactive SVG diagrams, widgets, and charts displayed inline by a compatible chat renderer. |
| [visualize](https://github.com/careerhackeralex/visualize) | A broad range of HTML visualizations from a prompt, including dashboards, infographics, flowcharts, and slide decks. |
| [visualize by display.dev](https://github.com/display-dev/visualize) | Branded HTML artifacts, with a persistent brand profile and tools to explore, review, and refine a design. |

For VibeView, the starting point is simple: **“I have the answer. Help me see how it fits together.”**

<details>
<summary><strong>How it works, and what to expect</strong></summary>

The agent reads [SKILL.md](SKILL.md), chooses a visual approach, and writes the page content. The Python composer adds shared styles and the VibeView shell, checks the markup, and writes a new file.

- **Content comes first.** The default workflow supports custom HTML, SVG, and CSS. The [JSON renderer](references/template.md) is an optional path for regular, structured content.
- **Simple output.** The default page needs no JavaScript, remote fonts, or server. It can be saved and shared as a file. Hosting is a separate step.
- **Model-dependent results.** The agent authors the page, so visual quality and factual accuracy depend on the model, source material, and prompt. Review important claims before sharing.
- **Desktop-first reading.** The included example also adapts to narrower screens; the skill does not promise complete mobile support.
- **Trusted input only.** The composer checks newly authored fragments. It is not a sanitizer for arbitrary external HTML. The host’s model and network settings determine how source material is handled.
- **Version 1.5.2.** The runtime uses Python’s standard library. The release’s recorded regression run covered 100 isolated cases on Python 3.13.12 / macOS; it does not establish cross-platform support.

</details>

## Share something worth reading

Made a useful explainer? Share an example you can make public, contribute it here, or [star VibeView](https://github.com/tahoeliu/vibeview) to help others find it.

For bugs, [open an issue](https://github.com/tahoeliu/vibeview/issues) with your Python and OS versions, command, error message, and a minimal example that contains no private data.

[MIT](LICENSE) © 2026 tahoeliu
