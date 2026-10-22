#!/usr/bin/env python3
"""Build a standalone page from an authored HTML fragment using shared VibeView styles."""
import argparse
import html
import json
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from render import write_new

LIMIT = 4 * 1024 * 1024
VOID = set('area br col hr img input source track wbr'.split())
BANNED = set('html head body main header footer script iframe object embed link meta base form input button select textarea dialog details summary template audio video foreignobject animate animatetransform set'.split())

def css_check(css):
    if re.search(r'@import|expression\s*\(|behavior\s*:|-moz-binding|javascript\s*:|</style', css, re.I):
        raise ValueError('Active/external CSS or closing style tag is not allowed')
    targets = re.findall(r'url\(\s*[\"\']?([^\)\"\']+)', css, re.I)
    for target in targets:
        if not re.fullmatch(r'#[A-Za-z][\w-]*', target.strip()):
            raise ValueError('CSS url() must reference a local SVG id')
    if '\\' in css or '/*' in css:
        raise ValueError('Custom CSS escapes/comments are unsupported; use plain declarations')
    return [target.strip()[1:] for target in targets]

class AuthoredFragment(HTMLParser):
    """Basic checks for newly authored content, NOT a sanitizer for untrusted HTML."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.ids = {'main'}
        self.refs = []
        self.nodes = 0
        self.has_h1 = False
        self.in_style = False
        self.styles = []
        self.warnings = []
        self.has_loose_text = False
    def handle_starttag(self, tag, attrs):
        self.nodes += 1
        if self.nodes > 20000 or len(self.stack) > 128:
            raise ValueError('Markup safety limit exceeded')
        if tag in BANNED:
            raise ValueError('Unsupported content tag: ' + tag)
        if tag == 'h1' and not any(parent in ('svg', 'math') for parent in self.stack):
            self.has_h1 = True
        if tag not in VOID:
            self.stack.append(tag)
        if tag == 'style':
            self.in_style = True
        a = dict(attrs)
        if len(a) != len(attrs):
            raise ValueError('Duplicate attributes')
        for k, v in attrs:
            if k.startswith('on') or k in ('srcdoc', 'srcset', 'autofocus'):
                raise ValueError('Active attributes forbidden: ' + k)
            if k == 'hidden' or (k == 'role' and v in ('tab', 'tablist', 'tabpanel', 'slider')):
                raise ValueError('Hidden/switching content forbidden')
            if k == 'id':
                if not v or not re.fullmatch(r'[A-Za-z][\w-]*', v) or v in self.ids:
                    raise ValueError('Invalid/duplicate id')
                self.ids.add(v)
            if k in ('href', 'xlink:href', 'src'):
                if not v:
                    raise ValueError('Empty resource URL')
                if v.startswith('#'):
                    self.refs.append(v[1:])
                elif tag == 'a' and k == 'href':
                    p = urlsplit(v)
                    if p.scheme not in ('https', 'http') or not p.hostname or p.username or p.password or any(ord(c) < 33 for c in v):
                        raise ValueError('Links must be plain http(s) URLs')
                elif tag == 'img' and k == 'src' and re.fullmatch(r'data:image/(png|jpeg|webp);base64,[A-Za-z0-9+/=\s]+', v):
                    pass
                else:
                    raise ValueError('External resources forbidden; embed images explicitly')
            if k == 'style':
                self.refs.extend(css_check(v or ''))
                self.check_visibility(v or '')
            if k in ('fill', 'stroke', 'filter', 'clip-path', 'mask', 'marker-end', 'marker-start', 'marker-mid', 'cursor'):
                self.refs.extend(css_check(v or ''))
        if tag == 'img' and 'alt' not in a:
            raise ValueError('Image requires alt')
    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack.pop() != tag:
            raise ValueError('Unbalanced explicit tags: ' + tag)
        if tag == 'style':
            self.in_style = False
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)
    def handle_data(self, data):
        if self.in_style:
            self.styles.append(data)
        elif not self.stack and data.strip():
            self.has_loose_text = True
    def handle_decl(self, decl):
        raise ValueError('Supply content fragment, not document wrapper')
    def check_visibility(self, value):
        if re.search(r'display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0\s*[;}]|content-visibility\s*:\s*hidden', value, re.I):
            self.warnings.append('Possible hidden content; review before delivering')

def compose(fragment, title, theme='violet', kit=True, layout='reading'):
    if not isinstance(title, str) or not title.strip():
        raise ValueError('Title required')
    if theme not in ('violet', 'blue', 'sage', 'amber'):
        raise ValueError('Unknown theme')
    if layout not in ('reading', 'custom'):
        raise ValueError('Unknown layout; choose reading or custom')
    check = AuthoredFragment()
    check.feed(fragment)
    check.close()
    css = '\n'.join(check.styles)
    check.refs.extend(css_check(css))
    check.check_visibility(css)
    if check.stack or any(r not in check.ids for r in check.refs):
        raise ValueError('Unclosed tags or missing local reference')
    if not check.has_h1:
        raise ValueError('Authored content must contain its own h1; shell does not impose a hero')
    if layout == 'reading' and check.has_loose_text:
        raise ValueError('Wrap top-level text in an element such as p for the reading layout')
    if layout == 'custom':
        check.warnings.append('Custom layout: provide and verify text gutters, line lengths, and narrow-screen behavior')
    if kit:
        base = (Path(__file__).resolve().parent.parent / 'assets/design.css').read_text(encoding='utf-8')
    else:
        base = 'body{margin:0;color:#252535;background:#fafafa;font-family:system-ui,sans-serif}.vv-brandbar{padding:22px 40px;border-bottom:1px solid #ddd}.vv-brandbar a{color:inherit;text-decoration:none;font-size:25px;font-weight:700}.vv-footer{padding:24px 40px;font-size:12px;color:#667}'
    if layout == 'reading':
        base += '\n' + (Path(__file__).resolve().parent.parent / 'assets/layout.css').read_text(encoding='utf-8')
    main_class = ' class="vv-reading-layout"' if layout == 'reading' else ''
    page = '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src data:; base-uri \'none\'"><title>VibeView · ' + html.escape(title) + '</title><style>' + base + '</style></head><body data-theme="' + theme + '" data-vv-layout="' + layout + '"><header class="vv-brandbar"><div class="vv-wrap"><a data-vibe-brand href="#main">VibeView.</a></div></header><main id="main"' + main_class + '>' + fragment + '</main><footer class="vv-footer"><div class="vv-wrap">VibeView · Visual explanations</div></footer></body></html>'
    return page, list(dict.fromkeys(check.warnings))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='HTML fragment file, or - to read from stdin')
    parser.add_argument('output', help='New HTML file in an existing directory')
    parser.add_argument('--title', required=True)
    parser.add_argument('--theme', choices=('violet', 'blue', 'sage', 'amber'), default='violet')
    parser.add_argument('--bare', action='store_true', help='Omit visual primitives; retain reading boundaries unless --layout custom is set')
    parser.add_argument('--layout', choices=('reading', 'custom'), default='reading', help='Use safe reading boundaries (default), or preserve an authored layout with custom')
    parser.add_argument('--lang', choices=('en', 'zh-CN'), default='en', help='Document language metadata (default: en)')
    args = parser.parse_args()
    start = time.perf_counter()
    try:
        if args.input == '-':
            raw = sys.stdin.buffer.read(LIMIT + 1)
        else:
            with open(args.input, 'rb') as f:
                raw = f.read(LIMIT + 1)
        if len(raw) > LIMIT:
            raise ValueError('Input exceeds 4 MiB')
        page, warnings = compose(raw.decode('utf-8-sig'), args.title, args.theme, not args.bare, args.layout)
        if args.lang == 'zh-CN':
            page = page.replace('<html lang="en">', '<html lang="zh-CN">')
        out = write_new(args.output, page, warnings)
        print(json.dumps({'status': 'ok', 'file': str(out), 'input_bytes': len(raw), 'output_bytes': len(page.encode()), 'elapsed_ms': round((time.perf_counter()-start)*1000, 2), 'warnings': warnings, 'scope': 'Static checks for agent-authored fragments, not a sanitizer or visual review'}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError, RecursionError) as e:
        print(json.dumps({'status':'error','error':str(e)}, ensure_ascii=False))
        return 1

if __name__ == '__main__':
    sys.exit(main())
