#!/usr/bin/env python3
"""VibeView JSON -> standalone desktop HTML. Standard library; no network/browser."""
import argparse
import html
import json
import math
import os
import re
import sys
import tempfile
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

LIMIT = 2 * 1024 * 1024
THEMES = {'blue', 'sage', 'amber', 'violet'}

def text(value, label='text'):
    if not isinstance(value, str):
        raise ValueError(label + ' must be a string')
    return value

def esc(value):
    return html.escape(text(value), quote=True)

def paragraphs(value):
    if value is None or value == '' or value == []:
        return ''
    values = [value] if isinstance(value, str) else value
    if not isinstance(values, list):
        raise ValueError('text must be a string or list of strings')
    return ''.join('<p>' + esc(v) + '</p>' for v in values)

def fields(obj, allowed, label):
    if not isinstance(obj, dict) or set(obj) - set(allowed.split()):
        raise ValueError(label + ': unknown field or not an object')

def url(value):
    value = text(value, 'url')
    p = urlsplit(value)
    if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password or any(ord(c) < 33 for c in value):
        raise ValueError('Source URL must be http(s), without credentials or whitespace')
    return html.escape(value, quote=True)

class Fragment(HTMLParser):
    """Strict small markup subset, not a general HTML/CSS sanitizer."""
    tags = set('div span p strong em b i small br h3 h4 ul ol li figure figcaption pre code svg g path rect circle ellipse line polyline polygon text tspan title desc defs marker lineargradient radialgradient stop'.split())
    attrs = set('class id role aria-label aria-labelledby viewbox width height x y x1 x2 y1 y2 cx cy r rx ry d points fill stroke stroke-width stroke-dasharray stroke-linecap stroke-linejoin opacity fill-opacity stroke-opacity transform text-anchor dominant-baseline font-size font-weight offset stop-color stop-opacity gradientunits gradienttransform markerwidth markerheight refx refy orient marker-end marker-start'.split())
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.stack = []
        self.ids = set()
        self.refs = []
    def handle_starttag(self, tag, attrs):
        if tag not in self.tags:
            raise ValueError('custom: disallowed tag ' + tag)
        if tag != 'br':
            self.stack.append(tag)
        self.depth = len(self.stack)
        if self.depth > 64:
            raise ValueError('custom: nesting limit')
        for k, v in attrs:
            if k not in self.attrs or v is None:
                raise ValueError('custom: disallowed attribute ' + k)
            if k == 'class' and (not re.fullmatch(r'[a-zA-Z0-9 _-]*', v) or any(x in v.split() for x in ('hero', 'section', 'wrap'))):
                raise ValueError('custom: invalid class')
            if k == 'id':
                if not re.fullmatch(r'custom-[A-Za-z0-9_-]+', v) or v in self.ids:
                    raise ValueError('custom ids must be unique and start custom-')
                self.ids.add(v)
            if k in ('fill', 'stroke', 'marker-end', 'marker-start') and 'url' in v.lower():
                if not re.fullmatch(r'url\(#custom-[A-Za-z0-9_-]+\)', v):
                    raise ValueError('custom: only local SVG references allowed')
                self.refs.append(v[5:-1])
            if any(x in v.lower() for x in ('javascript:', 'data:', 'http:', 'https:', 'expression(', 'var(')):
                raise ValueError('custom: external or dynamic value')
    def handle_endtag(self, tag):
        if tag not in self.tags:
            raise ValueError('custom: disallowed end tag')
        if tag != 'br':
            if not self.stack or self.stack.pop() != tag:
                raise ValueError('custom: mismatched tags')
            self.depth = len(self.stack)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)
    def handle_decl(self, decl):
        raise ValueError('custom: declarations forbidden')

def custom(value):
    value = text(value, 'html')
    p = Fragment()
    p.feed(value)
    p.close()
    if p.depth != 0 or any(x not in p.ids for x in p.refs):
        raise ValueError('custom: unbalanced markup or missing SVG reference')
    return value

def items_of(block):
    items = block.get('items', [])
    if not isinstance(items, list) or not 1 <= len(items) <= 100:
        raise ValueError('items must contain 1..100 entries')
    return items

def render_block(b, index):
    fields(b, 'type title text items note variant columns html unit', 'block')
    kind = b.get('type')
    types = {'prose', 'compare', 'metrics', 'flow', 'timeline', 'findings', 'bars', 'callout', 'custom', 'sources'}
    if kind not in types:
        raise ValueError('Unknown block type: ' + str(kind))
    cols = b.get('columns', 3 if kind in ('metrics', 'flow') else 2)
    if type(cols) is not int or not 1 <= cols <= 4:
        raise ValueError('columns must be 1..4')
    variant = b.get('variant', 'plain')
    if variant not in ('plain', 'tinted'):
        raise ValueError('variant must be plain or tinted')
    heading = '<h2>' + esc(b['title']) + '</h2>' if b.get('title') else ''
    intro = '<div class="intro">' + paragraphs(b.get('text')) + '</div>' if kind not in ('prose', 'callout') else ''
    body = ''
    if kind == 'prose':
        body = '<div class="prose">' + paragraphs(b.get('text')) + '</div>'
    elif kind == 'callout':
        body = '<div class="callout">' + paragraphs(b.get('text')) + '</div>'
    elif kind == 'custom':
        body = '<div class="custom">' + custom(b.get('html', '')) + '</div>'
    else:
        items = items_of(b)
        for item in items:
            fields(item, 'title text value label action source url', 'item')
        if kind in ('compare', 'metrics', 'findings', 'flow', 'timeline'):
            css = {'compare': 'grid compare', 'metrics': 'grid metrics', 'findings': 'findings', 'flow': 'path', 'timeline': 'timeline'}[kind]
            parts = []
            for n, i in enumerate(items):
                title = '<h3>' + esc(i.get('title', '')) + '</h3>'
                desc = paragraphs(i.get('text'))
                label = '<div class="badge">' + esc(i['label']) + '</div>' if i.get('label') else ''
                if kind == 'metrics':
                    value = i.get('value', '')
                    if type(value) not in (str, int, float) or (type(value) is float and not math.isfinite(value)):
                        raise ValueError('metric value must be text or finite number')
                    part = '<article class="tile"><div class="metric">' + esc(str(value)) + '</div>' + title + desc + '</article>'
                elif kind in ('flow', 'timeline'):
                    part = '<article class="step"><span class="number">' + esc(i.get('label', str(n + 1).zfill(2))) + '</span><div>' + title + desc + '</div></article>'
                elif kind == 'findings':
                    action = '<div class="action">' + paragraphs(i['action']) + '</div>' if i.get('action') else ''
                    source = '<div class="source">' + esc(i['source']) + '</div>' if i.get('source') else ''
                    part = '<article class="finding">' + label + title + desc + action + source + '</article>'
                else:
                    part = '<article class="tile">' + label + title + desc + '</article>'
                parts.append(part)
            body = '<div class="' + css + '" style="--cols:' + str(cols) + '">' + ''.join(parts) + '</div>'
        elif kind == 'bars':
            values = [i.get('value') for i in items]
            if any(type(v) not in (float, int) or not math.isfinite(v) or v < 0 or v > 1e100 for v in values):
                raise ValueError('bars require finite nonnegative values <= 1e100')
            maximum = max(values) or 1
            unit = esc(b.get('unit', ''))
            rows = ['<div class="bar-row"><span class="bar-label">' + esc(i.get('title', '')) + '</span><div class="track"><div class="fill" style="width:' + str(round(v / maximum * 100, 4)) + '%"></div></div><span class="bar-value">' + esc(str(v)) + unit + '</span></div>' for i, v in zip(items, values)]
            body = '<div class="bars">' + ''.join(rows) + '<p class="caption">线性零基准；最长条对应本组最大值。' + esc(b.get('note', '')) + '</p></div>'
        else:
            rows = []
            for i in items:
                label = esc(i.get('title', '来源'))
                link = '<a href="' + url(i['url']) + '" target="_blank" rel="noopener noreferrer">' + label + '</a>' if i.get('url') else label
                rows.append('<li>' + link + paragraphs(i.get('text')) + '</li>')
            body = '<ul class="sources">' + ''.join(rows) + '</ul>'
    note = '<p class="caption">' + esc(b['note']) + '</p>' if b.get('note') and kind != 'bars' else ''
    return '<section id="section-' + str(index) + '" class="section ' + variant + '"><div class="wrap">' + heading + intro + '<div class="content">' + body + '</div>' + note + '</div></section>'

class FinalCheck(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            if a['id'] in self.ids:
                raise ValueError('Duplicate final id: ' + a['id'])
            self.ids.add(a['id'])

def render(data):
    fields(data, 'title subtitle meta theme blocks', 'page')
    title = text(data.get('title'), 'title')
    if not title.strip():
        raise ValueError('title must not be empty')
    theme = data.get('theme', 'blue')
    if theme not in THEMES:
        raise ValueError('theme: blue/sage/amber/violet')
    blocks = data.get('blocks')
    if not isinstance(blocks, list) or not 1 <= len(blocks) <= 80:
        raise ValueError('blocks must contain 1..80 entries')
    css = (Path(__file__).resolve().parent.parent / 'assets/preview.css').read_text(encoding='utf-8')
    body = ''.join(render_block(b, n) for n, b in enumerate(blocks, 1))
    page = '<!doctype html>\n<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src data:; base-uri \'none\'"><title>VibeView · ' + esc(title) + '</title><style>' + css + '</style></head><body data-theme="' + theme + '"><header><div class="wrap"><a data-vibe-brand href="#main">VibeView.</a></div></header><main id="main"><section class="hero"><div class="wrap"><h1>' + esc(title) + '</h1><div class="lead">' + paragraphs(data.get('subtitle')) + '</div><p class="meta">' + esc(data.get('meta', '')) + '</p></div></section>' + body + '</main><footer><div class="wrap">VibeView · 单页可视化阅读</div></footer></body></html>'
    checker = FinalCheck()
    checker.feed(page)
    if len(page.encode()) > 8 * 1024 * 1024:
        raise ValueError('Output exceeds 8 MiB limit')
    return page

def write_new(destination, page, warnings=None):
    dest = Path(destination).absolute()
    if dest.suffix.lower() not in ('.html', '.htm') or not dest.parent.is_dir():
        raise ValueError('Output must be .html in an existing directory')
    if os.path.lexists(dest):
        raise ValueError('Output already exists; choose a new filename')
    temp = None
    published = False
    try:
        fd, temp = tempfile.mkstemp(prefix='.vibepreview-', suffix='.tmp', dir=dest.parent)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(page)
            f.flush()
            os.fsync(f.fileno())
        # 排他发布；提交后清理失败不能把成功误报为失败。
        os.link(temp, dest)
        published = True
    finally:
        if temp:
            try:
                os.unlink(temp)
            except FileNotFoundError:
                pass
            except OSError as exc:
                message = ('输出已成功生成' if published else '输出未生成') + f'；临时文件清理失败：{temp}（{exc}）'
                if warnings is not None:
                    warnings.append(message)
                else:
                    print(message, file=sys.stderr)
    return dest

def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('input', help='JSON file or - for stdin')
    cli.add_argument('output', help='New HTML file; never overwrite')
    args = cli.parse_args()
    started = time.perf_counter()
    try:
        if args.input == '-':
            raw = sys.stdin.buffer.read(LIMIT + 1)
        else:
            with open(args.input, 'rb') as f:
                raw = f.read(LIMIT + 1)
        if len(raw) > LIMIT:
            raise ValueError('Input exceeds 2 MiB limit')
        data = json.loads(raw.decode('utf-8-sig'))
        page = render(data)
        warnings = []
        out = write_new(args.output, page, warnings)
        print(json.dumps({'status': 'ok', 'warnings': warnings, 'file': str(out), 'input_bytes': len(raw), 'output_bytes': len(page.encode()), 'elapsed_ms': round((time.perf_counter() - started) * 1000, 2), 'checks': 'schema, escaping, fragment whitelist, ids, no-overwrite; no browser'}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError, RecursionError, OverflowError) as e:
        print(json.dumps({'status': 'error', 'error': str(e)}, ensure_ascii=False))
        return 1

if __name__ == '__main__':
    sys.exit(main())
