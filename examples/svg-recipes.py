"""Six editable SVG recipes: execute once to emit a trusted HTML fragment.
Usage: python3 -B examples/svg-recipes.py NEW.fragment.html
Compose that fragment with --motion. No external dependencies or network.
Import individual functions to reuse a composition; geometry remains editable.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from svg_parts import Canvas
from render import write_new


def branch(prefix='branch'):
    c = Canvas(prefix, 360, 380, '读取缓存：命中返回，未命中查数据库')
    c.add(c.route([(180,74),(180,119)], flow=True),
          c.route([(114,190),(114,253),(85,253),(85,279)], tone='accent', flow=True),
          c.route([(246,190),(246,253),(275,253),(275,279)], tone='secondary', flow=True))
    c.add(c.node(100,16,160,58,'读取请求',tone='surface'),
          c.node(70,120,220,70,'查缓存',note='副本不是权威来源'),
          c.label(64,220,'命中',note=True),c.label(292,220,'未命中',note=True),
          c.node(15,280,140,66,'直接返回'),c.node(205,280,140,66,'查数据库',tone='clay'))
    return c.render()


def cycle(prefix='cycle'):
    c=Canvas(prefix,360,380,'观测、判断、行动、反馈构成循环，循环不是一次性进度')
    c.add(c.route([(180,85),(180,142)],flow=True,tone='accent'),
          c.route([(180,210),(180,266)],flow=True,tone='accent'),
          c.route([(280,303),(331,303),(331,51),(280,51)],flow=True,tone='secondary'))
    c.add(c.node(80,18,200,66,'观测',note='收集实际信号'),c.node(80,144,200,66,'判断',tone='slate',note='比较目标与现状'),
          c.node(80,268,200,66,'行动',tone='clay',note='调整后再次观测'),c.label(44,178,'反\n馈',note=True))
    return c.render()


def layers(prefix='layers'):
    c=Canvas(prefix,360,380,'三层结构：入口、服务、数据；排列示意，不代表规模')
    c.add(c.stack(80,26,240,68,['入口层','服务层','数据层'],gap=24))
    c.add(c.badge(39,60,'1'),c.badge(39,152,'2'),c.badge(39,244,'3'),c.bracket(80,320,326,'职责分层 ≠ 物理隔离'))
    return c.render()


def boundary(prefix='boundary'):
    c=Canvas(prefix,360,380,'设备边界：本地模型在设备内，云端模型在设备外，请求需跨越网络')
    c.add(c.region(14,14,332,194,'设备内部'),
          c.route([(91,134),(244,134)],label='本地',label_at=(180,113)),
          c.route([(86,162),(86,271)],tone='secondary',label='联网',label_at=(129,231)),
          c.node(26,92,120,70,'输入',tone='surface'),c.node(218,92,114,70,'本地模型',tone='sage'),
          c.node(26,274,120,70,'云端模型',tone='clay'),c.label(254,307,'设备外',note=True))
    return c.render()


def before_after(prefix='change'):
    c=Canvas(prefix,360,380,'库存写入后的两个时刻：数据库先更新，缓存失效后再读取')
    c.add(c.node(18,24,140,76,'数据库',tone='clay',note='库存 7'),c.node(202,24,140,76,'缓存',note='旧库存 8'),
          c.route([(272,103),(272,240)],tone='secondary',label='失效后再读',label_at=(179,173)),
          c.node(202,244,140,76,'缓存',note='新库存 7'),c.label(88,282,'稍后',note=True),c.bracket(18,342,343,'时序示意，不是强一致承诺'))
    return c.render()


def fan_in(prefix='fanin'):
    c=Canvas(prefix,360,380,'多个请求合并为一次回源，结果分发由正文说明')
    c.add(c.route([(67,84),(67,146),(180,146),(180,208)],tone='accent'),
          c.route([(180,84),(180,208)],tone='accent'),
          c.route([(293,84),(293,146),(180,146)],tone='accent'))
    c.add(c.node(15,20,104,64,'请求 A',tone='surface'),c.node(128,20,104,64,'请求 B',tone='surface'),
          c.node(241,20,104,64,'请求 C',tone='surface'),c.dot(180,146,tone='accent'),
          c.node(72,212,216,74,'合并回源',note='相同键的并发请求'),c.bracket(72,288,320,'回源结果再分发给等待者'))
    return c.render()


RECIPES=[
 ('branch','分支：走哪条路？','同一请求只走其中一条分支。命中与未命中不是连续步骤。',branch),
 ('cycle','回路：为什么还会回来？','只对持续发生的机制循环；不把完成进度、累计数量做成重复动画。',cycle),
 ('layers','分层：每层负责什么？','默认垂直展开，不用透视遮住文字；层高不是数据量。',layers),
 ('boundary','边界：什么跨出了设备？','先画背景分区，再画线路与节点。边框表示边界，不代表安全保证。',boundary),
 ('change','时序：哪里先变，哪里后变？','用明确的前后状态解释陈旧副本，不让动画承担唯一证据。',before_after),
 ('fanin','汇聚：多个怎样变成一个？','路由点由作者决定；组件不做自动避障，也不自动推断业务语义。',fan_in),
]

def fragment():
    result=['<p class="vv-kicker">SVG 可组合样板 / Lab.4</p><h1>复用几何，<br>不复用结论。</h1><p class="vv-lead">节点、箭头、多行标签、分区、层叠与括号，组合成六种不同关系。无需按钮，正常滚动即可阅读。</p>']
    for i,(name,title,caption,fn) in enumerate(RECIPES,1):
        result.append(f'<section class="vv-editorial vv-space-before"><div class="vv-stack"><p class="vv-kicker">0{i} / {name}</p><h2>{title}</h2><p>{caption}</p><p class="vv-note">这是可改写的局部构图，不是自动布局模板。文字、位置与业务边界仍由作者判断。</p></div><figure class="vv-frame vv-paper vv-figure vv-diagram-frame" style="--frame-pad:12px">{fn()}<figcaption>{caption}</figcaption></figure></section>')
    return '\n'.join(result)

if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('Usage: svg-recipes.py NEW.fragment.html')
    write_new(sys.argv[1],fragment(),[])
