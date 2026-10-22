#!/usr/bin/env python3
"""Run composer regression tests with Python's standard library."""
import concurrent.futures
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from compose import compose, LIMIT
from render import write_new, render

ROOT = Path(__file__).resolve().parent.parent
SIMPLE = '<h1>Reading boundaries</h1><p>Keep the explanation readable.</p>'


class ComposerTests(unittest.TestCase):
    def test_default_reading_layout(self):
        page, warnings = compose(SIMPLE, 'A & B')
        self.assertIn('<main id="main" class="vv-reading-layout">', page)
        self.assertIn('A &amp; B', page)
        self.assertIn('--vv-gutter:', page)
        self.assertEqual(warnings, [])
        self.assertEqual(page.count(SIMPLE), 1)

    def test_theme_kit_layout_matrix(self):
        for theme in ('blue', 'sage', 'amber', 'violet'):
            for kit in (True, False):
                for layout in ('reading', 'custom'):
                    with self.subTest(theme=theme, kit=kit, layout=layout):
                        page, warnings = compose(SIMPLE, 'Matrix', theme, kit, layout)
                        self.assertIn('data-theme="' + theme + '"', page)
                        self.assertEqual('class="vv-reading-layout"' in page, layout == 'reading')
                        self.assertEqual(bool(warnings), layout == 'custom')
                        self.assertEqual('--vv-gutter:' in page, layout == 'reading')

    def test_invalid_layout(self):
        for value in ('', 'auto', None, 'reading" onload="bad'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                compose(SIMPLE, 'Invalid', layout=value)

    def test_no_implicit_custom_detection(self):
        fragment = '<div class="vv-wrap"><h1>Wrapped title</h1></div><p>Unwrapped text</p>'
        self.assertIn('class="vv-reading-layout"', compose(fragment, 'Mixed')[0])

    def test_loose_text(self):
        for fragment in ('Loose ' + SIMPLE, SIMPLE + ' &amp; trailing', '&#65;' + SIMPLE):
            with self.subTest(fragment=fragment), self.assertRaisesRegex(ValueError, 'top-level text'):
                compose(fragment, 'Loose')
        self.assertIn('Loose ', compose('Loose ' + SIMPLE, 'Loose', layout='custom')[0])
        compose('\n<!-- comment -->' + SIMPLE + '\n', 'Whitespace')

    def test_full_bleed_preserves_authored_markup(self):
        fragment = SIMPLE + '<section class="vv-full-bleed vv-callout"><h2>Edge-to-edge background</h2><p>Inset text</p></section>'
        self.assertIn(fragment, compose(fragment, 'Full bleed')[0])

    def test_security_rejections(self):
        invalid = [
            '<script>alert(1)</script>', '<img src="https://example.com/a.png" alt="Image">',
            '<p onclick="bad()">Bad</p>', '<div hidden>Hidden</div>',
            '<style>@import "https://example.com/a.css";</style>',
            '<style>p{background:url(https://example.com/a.png)}</style>',
            '<div id="main">Duplicate</div>', '<div><p>Unclosed</div>',
            '<a href="#missing">Missing</a>', '<details><summary>Hidden</summary></details>',
            '<p class="a" class="b">Duplicate attributes</p>', '<main>Wrapper</main>',
            '<svg><path fill="url(#missing)"/></svg>',
        ]
        for value in invalid:
            for layout in ('reading', 'custom'):
                with self.subTest(value=value, layout=layout), self.assertRaises(ValueError):
                    compose(SIMPLE + value, 'Rejected', layout=layout)

    def test_heading_and_local_references(self):
        for fragment in ('<p>No heading</p>', '<!-- <h1>Fake</h1> --><p>Text</p>', '<svg><h1>Fake</h1></svg>'):
            with self.subTest(fragment=fragment), self.assertRaises(ValueError):
                compose(fragment, 'Missing heading')
        compose(SIMPLE + '<a href="#target">Jump</a><p id="target">Target</p>', 'References')

    def test_existing_example_custom_layout(self):
        fragment = (ROOT / 'examples/reading-map.fragment.html').read_text()
        page, warnings = compose(fragment, 'Example', layout='custom')
        self.assertIn(fragment, page)
        self.assertNotIn('class="vv-reading-layout"', page)
        self.assertEqual(len(warnings), 1)

    def test_legacy_json_renderer(self):
        page = render({'title': 'Legacy', 'blocks': [{'type': 'prose', 'text': 'Readable content'}]})
        self.assertIn('class="wrap"', page)
        self.assertNotIn('vv-reading-layout', page)

    def test_cli_bom_language_and_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / 'result.html'
            command = [sys.executable, '-B', str(ROOT / 'scripts/compose.py'), '-', str(dest), '--title', 'CLI', '--bare', '--lang', 'zh-CN']
            result = subprocess.run(command, input=b'\xef\xbb\xbf' + SIMPLE.encode(), capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn('<html lang="zh-CN">', dest.read_text())
            self.assertIn('vv-reading-layout', dest.read_text())
            original = dest.read_bytes()
            result = subprocess.run(command, input=SIMPLE.encode(), capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(dest.read_bytes(), original)
            result = subprocess.run(command, input=b'x' * (LIMIT + 1), capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn(b'Input exceeds', result.stdout)
            result = subprocess.run(command, input=b'\xff', capture_output=True)
            self.assertEqual(result.returncode, 1)

    def test_exclusive_publication_under_concurrency(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / 'race.html'
            def publish(index):
                try:
                    write_new(dest, str(index))
                    return index
                except (ValueError, FileExistsError):
                    return None
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
                winners = [i for i in pool.map(publish, range(4)) if i is not None]
            self.assertEqual(len(winners), 1)
            self.assertEqual(dest.read_text(), str(winners[0]))
            self.assertEqual(list(Path(directory).iterdir()), [dest])

    def test_symlink_and_existing_output_protection(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'target.html'
            target.write_text('Original')
            link = Path(directory) / 'link.html'
            link.symlink_to(target)
            for path in (target, link):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    write_new(path, 'Replacement')
            self.assertEqual(target.read_text(), 'Original')
            with self.assertRaises(ValueError):
                write_new(Path(directory) / 'missing' / 'page.html', SIMPLE)

    def test_failure_before_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / 'failure.html'
            for operation in ('fsync', 'link'):
                with self.subTest(operation=operation), patch('render.os.' + operation, side_effect=OSError('Injected failure')):
                    with self.assertRaises(OSError):
                        write_new(dest, SIMPLE)
                self.assertFalse(dest.exists())
                self.assertEqual(list(Path(directory).iterdir()), [])

    def test_cancellation_before_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / 'cancelled.html'
            with patch('render.os.fsync', side_effect=KeyboardInterrupt):
                with self.assertRaises(KeyboardInterrupt):
                    write_new(dest, SIMPLE)
            self.assertFalse(dest.exists())
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_missing_layout_asset_fails_closed(self):
        original = Path.read_text
        def read(path, *args, **kwargs):
            if path.name == 'layout.css':
                raise FileNotFoundError('Missing reading layout asset')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', read):
            with self.assertRaises(FileNotFoundError):
                compose(SIMPLE, 'Incomplete installation')
            compose(SIMPLE, 'Custom without layout asset', layout='custom')

    def test_cleanup_failure_after_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / 'success.html'
            warnings = []
            with patch('render.os.unlink', side_effect=OSError('Injected cleanup failure')):
                self.assertEqual(write_new(dest, SIMPLE, warnings), dest)
            self.assertEqual(dest.read_text(), SIMPLE)
            self.assertIn('Output created successfully', warnings[0])
            self.assertEqual(len(list(Path(directory).glob('.vibepreview-*'))), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
