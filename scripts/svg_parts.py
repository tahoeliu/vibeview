"""可复用 SVG 几何小组件，仅使用 Python 标准库，不负责生成整页。

每个嵌入同一页面的 Canvas 必须由调用者提供唯一 prefix；重复 render
不会自动生成新命名空间。组件只返回字符串，须显式 add，按添加顺序绘制。
add 接受可信调用者的 SVG 字符串，不是 sanitizer。结果仍须重新经过
compose.py 检查；flow 需要 compose(..., motion=True) 或 CLI --motion。
颜色依赖现有 --vv-* CSS 变量。字体固定为 20/18px，不计算汉字宽度、
不自动换行或缩小；显式换行使用 tspan。字体、溢出、缩放和最终布局仍要
浏览器校验。作者自行安排分区、节点和连线，不自动布置整页。

数值接受有限实数（含 Decimal/Fraction），拒绝 bool、复数和数字字符串。
坐标及计算出的文本坐标限定于 [-4096, 4096]；尺寸为 (0, 4096]。
文本每字段最多 500 字符，超限报错。非法类型抛 TypeError，非法值抛
ValueError。stack 的 h 是每层高度，层间距 gap 可为零；各层标签必须
留有上下各 8 单位空间，并附“示意堆叠，非比例”注释。
"""

import html
import math
import re
from decimal import Decimal
from numbers import Real


_COLORS = {
    'sage': 'var(--vv-sage)',
    'clay': 'var(--vv-clay)',
    'slate': 'var(--vv-slate)',
    'oat': 'var(--vv-oat)',
    'surface': 'var(--vv-surface)',
    'ink': 'var(--vv-graph-ink)',
    'accent': 'var(--vv-accent)',
    'secondary': 'var(--vv-secondary)',
}
_SURFACES = ('sage', 'clay', 'slate', 'oat', 'surface')
_LINES = ('ink', 'accent', 'secondary')


def _number(value, name, lower=-4096, upper=4096, positive=False):
    if isinstance(value, bool) or not isinstance(value, (Real, Decimal)):
        raise TypeError(f'{name} 必须为实数，不能是 bool')
    try:
        result = float(value)
    except (OverflowError, ValueError):
        raise ValueError(f'{name} 必须为有限且在范围内的实数') from None
    if not math.isfinite(result) or not lower <= value <= upper:
        raise ValueError(f'{name} 必须在 [{lower}, {upper}] 内且有限')
    if positive and (value <= 0 or result <= 0):
        raise ValueError(f'{name} 必须大于零')
    return result


def _size(value, name):
    return _number(value, name, lower=0, positive=True)


def _fmt(value):
    return '0' if value == 0 else format(value, '.15g')


def _text(value, name='text', nonempty=False):
    if not isinstance(value, str):
        raise TypeError(f'{name} 必须为字符串')
    if len(value) > 500:
        raise ValueError(f'{name} 不得超过 500 字符')
    if nonempty and not value.strip():
        raise ValueError(f'{name} 不能为空')
    return value


def _choice(value, allowed, name):
    if not isinstance(value, str):
        raise TypeError(f'{name} 必须为字符串')
    if value not in allowed:
        raise ValueError(f'{name} 必须为 {", ".join(allowed)} 之一')
    return value


def _color(tone, allowed):
    return _COLORS[_choice(tone, allowed, 'tone')]


def _boolean(value, name):
    if not isinstance(value, bool):
        raise TypeError(f'{name} 必须为 bool')
    return value


def _point(value, name):
    if not isinstance(value, (list, tuple)):
        raise TypeError(f'{name} 必须为二维 list 或 tuple')
    if len(value) != 2:
        raise ValueError(f'{name} 必须包含两个坐标')
    return tuple(_number(v, f'{name}[{i}]') for i, v in enumerate(value))


def _box(x, y, w, h):
    return (_number(x, 'x'), _number(y, 'y'), _size(w, 'w'), _size(h, 'h'))


def _rows(text):
    return text.replace('\r\n', '\n').replace('\r', '\n').split('\n')


def _text_height(text, note=False):
    return (18 if note else 20) + (len(_rows(text)) - 1) * (24 if note else 26)


def _label(x, y, text, anchor='middle', note=False):
    x, y = _number(x, 'x'), _number(y, 'y')
    text = _text(text)
    _choice(anchor, ('start', 'middle', 'end'), 'anchor')
    _boolean(note, 'note')
    rows = _rows(text)
    step = 24 if note else 26
    top = y - (len(rows) - 1) * step / 2
    spans = []
    for i, row in enumerate(rows):
        cy = _number(top + i * step, '文本行 y')
        spans.append(f'<tspan x="{_fmt(x)}" y="{_fmt(cy)}">{html.escape(row)}</tspan>')
    cls = 'vv-part-note' if note else 'vv-part-label'
    size = 18 if note else 20
    weight = 400 if note else 600
    return (
        f'<text class="{cls}" x="{_fmt(x)}" y="{_fmt(y)}" '
        f'text-anchor="{anchor}" dominant-baseline="central" '
        f'fill="{_COLORS["ink"]}" stroke="none" '
        f'style="font-family:system-ui,sans-serif;font-size:{size}px;font-weight:{weight}">'
        + ''.join(spans) + '</text>'
    )


class Canvas:
    """保留作者布局自由的 SVG 容器；prefix 必须在最终页面中唯一。"""

    def __init__(self, prefix, width=360, height=360, title='图解'):
        if not isinstance(prefix, str):
            raise TypeError('prefix 必须为字符串')
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,47}', prefix, flags=re.ASCII):
            raise ValueError('prefix 必须以 ASCII 字母开头，且仅含字母、数字、_、-，长度 1..48')
        self._prefix = prefix
        self._width = _size(width, 'width')
        self._height = _size(height, 'height')
        self._title = _text(title, 'title', nonempty=True)
        self._fragments = []

    def add(self, *fragments):
        """按顺序加入可信字符串，最多 512 段；不解析、不清洗，返回 self。"""
        if any(not isinstance(fragment, str) for fragment in fragments):
            raise TypeError('add 只接受字符串')
        if len(self._fragments) + len(fragments) > 512:
            raise ValueError('Canvas 最多允许 512 个片段')
        self._fragments.extend(fragments)
        return self

    def render(self):
        """返回含标题及三种本地箭头的根 SVG；不修改已添加片段。"""
        markers = ''.join(
            f'<marker id="{self._prefix}-arrow-{tone}" viewBox="0 0 10 10" '
            f'refX="9" refY="5" markerWidth="7" markerHeight="7" '
            f'orient="auto" markerUnits="strokeWidth">'
            f'<path d="M 0 0 L 10 5 L 0 10 Z" fill="{_COLORS[tone]}" '
            f'stroke="none"/></marker>'
            for tone in _LINES
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" class="vv-figure vv-diagram" '
            f'width="{_fmt(self._width)}" height="{_fmt(self._height)}" '
            f'viewBox="0 0 {_fmt(self._width)} {_fmt(self._height)}" '
            f'role="img" aria-labelledby="{self._prefix}-title" fill="none">'
            f'<title id="{self._prefix}-title">{html.escape(self._title)}</title>'
            f'<defs>{markers}</defs>' + ''.join(self._fragments) + '</svg>'
        )

    def node(self, x, y, w, h, label, tone='sage', note=None):
        """返回圆角节点；主标签和可选注释作为一个文本块垂直居中。"""
        x, y, w, h = _box(x, y, w, h)
        fill = _color(tone, _SURFACES)
        label = _text(label, 'label')
        label_h = _text_height(label)
        cy = y + h / 2
        if note is not None:
            note = _text(note, 'note')
            note_h = _text_height(note, note=True)
            cy -= (note_h + 8) / 2
            text = _label(x + w / 2, cy, label)
            text += _label(x + w / 2, cy + label_h / 2 + 8 + note_h / 2, note, note=True)
        else:
            text = _label(x + w / 2, cy, label)
        return (
            f'<g class="vv-part-node"><rect x="{_fmt(x)}" y="{_fmt(y)}" '
            f'width="{_fmt(w)}" height="{_fmt(h)}" rx="12" '
            f'fill="{fill}" stroke="var(--vv-graph-line)" stroke-width="1.5"/>'
            + text + '</g>'
        )

    def label(self, x, y, text, anchor='middle', note=False):
        """x/y 是整个多行文本块的锚点/垂直中心，不是首行基线。"""
        return _label(x, y, text, anchor, note)

    def route(self, points, tone='ink', flow=False, repeat='loop', label=None, label_at=None):
        """按给定点连接折线并保留末端箭头，不自动避障。

        label_at 为显式 (x, y)；省略时标签放在路径长度中点上方 16 单位。
        repeat 仅允许 loop/once；非 flow 忽略默认 loop，但拒绝 once。
        """
        color = _color(tone, _LINES)
        _boolean(flow, 'flow')
        _choice(repeat, ('loop', 'once'), 'repeat')
        if not flow and repeat != 'loop':
            raise ValueError('非 flow 不允许 repeat=once')
        if not isinstance(points, (list, tuple)):
            raise TypeError('points 必须为 list 或 tuple')
        if not 2 <= len(points) <= 32:
            raise ValueError('points 必须包含 2..32 个点')
        points = [_point(point, f'points[{i}]') for i, point in enumerate(points)]
        if label_at is not None:
            label_at = _point(label_at, 'label_at')
            if label is None:
                raise ValueError('label_at 需要同时提供 label')
        caption = ''
        if label is not None:
            label = _text(label, 'label')
            if label_at is None:
                lengths = [math.hypot(b[0] - a[0], b[1] - a[1])
                           for a, b in zip(points, points[1:])]
                remaining = sum(lengths) / 2
                lx, ly = points[0]
                for a, b, length in zip(points, points[1:], lengths):
                    if length and remaining <= length:
                        ratio = remaining / length
                        lx, ly = a[0] + (b[0] - a[0]) * ratio, a[1] + (b[1] - a[1]) * ratio
                        break
                    remaining -= length
                label_at = (lx, ly - 16)
            caption = _label(*label_at, label)
        d = 'M ' + ' L '.join(f'{_fmt(x)} {_fmt(y)}' for x, y in points)
        motion = f' stroke-dasharray="12 12" data-vv-motion="flow" data-vv-repeat="{repeat}"' if flow else ''
        path = (
            f'<path class="vv-part-line" d="{d}" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'marker-end="url(#{self._prefix}-arrow-{tone})"{motion}/>'
        )
        return '<g>' + path + caption + '</g>'

    def badge(self, x, y, text, tone='oat'):
        """固定半径 16 的序号圆；文本不会自动缩小或裁剪。"""
        x, y = _number(x, 'x'), _number(y, 'y')
        fill = _color(tone, _SURFACES)
        caption = _label(x, y, text)
        return (
            f'<g class="vv-part-badge"><circle cx="{_fmt(x)}" cy="{_fmt(y)}" '
            f'r="16" fill="{fill}" stroke="var(--vv-graph-line)" stroke-width="1.5"/>'
            + caption + '</g>'
        )

    def stack(self, x, y, w, h, labels, tone='slate', gap=10):
        """1..4 层等尺寸节点垂直展开，避免后层几何覆盖前层标签；非比例。"""
        x, y, w, h = _box(x, y, w, h)
        _color(tone, _SURFACES)
        gap = _number(gap, 'gap', lower=0)
        if not isinstance(labels, (list, tuple)):
            raise TypeError('labels 必须为 list 或 tuple')
        if not 1 <= len(labels) <= 4:
            raise ValueError('labels 必须包含 1..4 个标签')
        parts = []
        for i, label in enumerate(labels):
            label = _text(label, f'labels[{i}]')
            if _text_height(label) + 16 > h:
                raise ValueError('stack 每层 h 必须容纳标签行高及上下各 8 单位留白')
            parts.append(self.node(x, y + i * (h + gap), w, h, label, tone))
        bottom = y + len(labels) * h + (len(labels) - 1) * gap
        parts.append(_label(x + w / 2, bottom + 21, '示意堆叠，非比例', note=True))
        return '<g>' + ''.join(parts) + '</g>'

    def bracket(self, x1, x2, y, label):
        """开口向上的横向括号；注释在横线下方，不带箭头。"""
        x1, x2, y = _number(x1, 'x1'), _number(x2, 'x2'), _number(y, 'y')
        if x2 <= x1:
            raise ValueError('bracket 要求 x2 > x1')
        label = _text(label, 'label')
        top = _number(y - 8, '括号顶端 y')
        caption = _label((x1 + x2) / 2, y + 12 + _text_height(label, note=True) / 2, label, note=True)
        return (
            f'<g><path class="vv-part-line" d="M {_fmt(x1)} {_fmt(top)} '
            f'L {_fmt(x1)} {_fmt(y)} L {_fmt(x2)} {_fmt(y)} L {_fmt(x2)} {_fmt(top)}" '
            f'fill="none" stroke="{_COLORS["ink"]}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round"/>' + caption + '</g>'
        )

    def dot(self, x, y, tone='sage', r=6):
        """返回实心圆点；作为标记允许全部八种颜色，半径为正数。"""
        x, y, r = _number(x, 'x'), _number(y, 'y'), _size(r, 'r')
        fill = _color(tone, _COLORS)
        return (
            f'<circle class="vv-part-dot" cx="{_fmt(x)}" cy="{_fmt(y)}" '
            f'r="{_fmt(r)}" fill="{fill}" stroke="none"/>'
        )

    def region(self, x, y, w, h, label, tone='oat'):
        """返回背景分区及左上标签；应先 add 分区，再 add 前景组件。"""
        x, y, w, h = _box(x, y, w, h)
        fill = _color(tone, _SURFACES)
        label = _text(label, 'label')
        caption = _label(x + 12, y + 12 + _text_height(label) / 2, label, anchor='start')
        return (
            f'<g class="vv-part-region"><rect x="{_fmt(x)}" y="{_fmt(y)}" '
            f'width="{_fmt(w)}" height="{_fmt(h)}" rx="12" '
            f'fill="{fill}" stroke="none"/>' + caption + '</g>'
        )
