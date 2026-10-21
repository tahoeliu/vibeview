# 条件适用的JSON组件路径

仅在内容规整、组件完整准确、版式不单调且品质不降低时使用。不要因为能够塞入字段就使用模板；不必先尝试模板。非适配内容走自主compose.py或完整HTML。

`python <技能目录>/scripts/render.py <内容.json> <新的输出.html>`

顶层title、可选subtitle/meta/theme（blue/sage/amber/violet）、blocks数组。块通用type、title、text（字符串或段落数组）、note、variant（plain/tinted）、columns（1–4）。所有普通字段都是纯文本。

- prose/callout：text。
- compare：items中title/text，可选label。
- metrics：items中value/title/text。
- flow/timeline：items中title/text，可选label。
- findings：items中title/text，可选label/action/source。
- bars：items中title/非负value，可选unit；只支持零基准线性条，不支持负数或堆叠。
- sources：items中title/text/url；url为无凭据http(s)。
- custom：html为受限静态HTML/SVG，不允许style、脚本、事件或外部资源；SVG id以custom-开头且全页唯一。

例：{"title":"两种选择","theme":"blue","blocks":[{"type":"compare","items":[{"title":"A","text":"依据"},{"title":"B","text":"代价"}]}]}

脚本只负责机械组装，不推导数据含义、不验证业务结论。输出父目录需已存在且文件不存在；组装已检查，不再启动独立检查流程。
