#!/usr/bin/env python3
"""渲染员工离职挽留的四张 Geometry Blue 画板。

风格：白底、黑线、单一蓝色强调（#2F6BFF）、几何极简、16:9。
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

W, H = 1200, 675
BLACK = "#111111"
LINE = "#222222"
GRAY = "#666666"
GUIDE = "#B8B8B8"
LIGHT = "#E8E8E8"
FILL = "#F5F5F5"
BLUE = "#2F6BFF"
FONT = "-apple-system,BlinkMacSystemFont,'PingFang SC','Noto Sans CJK SC',sans-serif"


def esc(v: object) -> str:
    return html.escape(str(v), quote=True)


def txt(x, y, v, size=16, fill=BLACK, anchor="middle", weight=400, letter=0):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
            f'font-size="{size}px" font-weight="{weight}" letter-spacing="{letter}px" fill="{fill}">{esc(v)}</text>')


def two_lines(x, y, a, b, size=16, fill=BLACK, gap=20, weight=600):
    return txt(x, y - gap / 2 + 5, a, size, fill, weight=weight) + txt(x, y + gap / 2 + 5, b, size, fill, weight=weight)


def line(x1, y1, x2, y2, color=LINE, width=1.5, arrow=False, dashed=False):
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    dash = ' stroke-dasharray="5 7"' if dashed else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{dash}{marker} />'


def path(d, color=LINE, width=1.5, arrow=False, dashed=False):
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    dash = ' stroke-dasharray="5 7"' if dashed else ""
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash}{marker} />'


def rect(x, y, w, h, fill="none", stroke=LINE, width=1.5):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" />'


def circle(cx, cy, r, fill="none", stroke=LINE, width=1.5):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" />'


def title(scene):
    intent = scene["intent"]
    sub = intent.get("subtitle", "员工离职挽留")
    return "".join([
        txt(96, 78, intent["core_message"], 32, BLACK, "start", 650),
        txt(96, 108, sub, 14, GRAY, "start"),
        line(96, 136, 1104, 136, LIGHT, 1),
    ])


# ---------- 画板 1：两段式工作流 ----------
def render_twostage(scene):
    body = [title(scene)]
    y = 340
    # 左：信息来源两条汇入
    body.append(rect(96, 250, 150, 60, "#FFFFFF", LINE, 1.4))
    body.append(txt(171, 285, "用户提供的信息", 14, BLACK, weight=600))
    body.append(rect(96, 372, 150, 60, "#FFFFFF", LINE, 1.4))
    body.append(txt(171, 400, "飞书证据（可选）", 14, BLACK, weight=600))
    body.append(txt(171, 420, "1:1 · 纪要 · OKR", 11, GRAY))
    body.append(path("M 246 280 C 300 280 300 330 348 335", LINE, 1.4, True))
    body.append(path("M 246 402 C 300 402 300 350 348 345", LINE, 1.4, True))
    # 中：标准方案
    body.append(rect(360, 292, 150, 96, FILL, LINE, 1.5))
    body.append(two_lines(435, 330, "标准", "挽留方案", 17, BLACK, 22, 650))
    body.append(txt(435, 372, "五状态全覆盖", 12, GRAY))
    # 追问
    body.append(line(510, 340, 566, 340, LINE, 1.5, arrow=True))
    body.append(circle(628, 340, 50, BLUE))
    body.append(two_lines(628, 337, "追问", "核心原因", 15, "#FFFFFF", 20, 650))
    # 个性化
    body.append(line(690, 340, 746, 340, LINE, 1.5, arrow=True))
    body.append(rect(758, 292, 150, 96, "#FFFFFF", LINE, 1.5))
    body.append(two_lines(833, 330, "个性化", "挽留内容", 17, BLACK, 22, 650))
    body.append(txt(833, 372, "针对性干预与脚本", 12, GRAY))
    # 谈话
    body.append(line(908, 340, 964, 340, LINE, 1.5, arrow=True))
    body.append(circle(1030, 340, 40, "#FFFFFF", LINE, 1.5))
    body.append(two_lines(1030, 338, "一次", "谈话", 15, BLACK, 19, 600))
    # 底注
    body.append(txt(600, 500, "先给可动手的标准方案，再按你判断的核心原因个性化", 13, GRAY))
    return "".join(body)


# ---------- 画板 2：五状态诊断 ----------
def render_states(scene):
    body = [title(scene)]
    items = [
        ("不被赏识", "被重视"),
        ("孤独", "被连接"),
        ("无聊", "被挑战"),
        ("卡住", "在成长"),
        ("麻木", "有热情"),
    ]
    top, gap = 200, 74
    lx, rx = 300, 640
    body.append(txt(300, 174, "他感到", 13, GRAY, weight=600))
    body.append(txt(640, 174, "他需要", 13, GRAY, weight=600))
    for i, (feel, need) in enumerate(items):
        y = top + i * gap
        body.append(rect(180, y, 240, 52, "#FFFFFF", LINE, 1.4))
        body.append(txt(300, y + 32, feel, 18, BLACK, weight=600))
        body.append(line(424, y + 26, 516, y + 26, LINE, 1.5, arrow=True))
        body.append(rect(520, y, 240, 52, "#FFFFFF", LINE, 1.4))
        body.append(f'<rect x="520" y="{y}" width="6" height="52" fill="{BLUE}" />')
        body.append(txt(640, y + 32, need, 18, BLUE, weight=600))
    body.append(txt(872, 300, "先判断状态", 15, BLACK, weight=600))
    body.append(txt(872, 328, "再对症干预", 15, BLACK, weight=600))
    body.append(txt(872, 372, "同样是想走", 13, GRAY))
    body.append(txt(872, 394, "无聊和卡住", 13, GRAY))
    body.append(txt(872, 416, "需要的完全不同", 13, GRAY))
    return "".join(body)


# ---------- 画板 3：已有 offer 的应对顺序 ----------
def render_offer(scene):
    body = [title(scene)]
    y = 330
    steps = [
        (200, "理解", "为什么开始看"),
        (450, "判断可信度", "能否改根因"),
        (700, "决定 counter", "真实·快速·公平"),
        (960, "保护关系", "好聚好散"),
    ]
    for x0, x1 in ((280, 350), (560, 618), (820, 870)):
        body.append(line(x0, y, x1, y, LINE, 1.5, arrow=True))
    # 起点：警示——别先问「要什么才留下」
    body.append(rect(96, y - 46, 184, 92, FILL, LINE, 1.5))
    body.append(txt(188, y - 4, "对方已有 offer", 17, BLACK, weight=650))
    body.append(txt(188, y + 28, "先放慢", 12, GRAY))
    body.append(circle(450, y, 46, "#FFFFFF", LINE, 1.5))
    body.append(txt(450, y + 6, "?", 34, GRAY, weight=700))
    body.append(circle(700, y, 46, BLUE))
    body.append(txt(700, y + 6, "counter", 15, "#FFFFFF", weight=650))
    body.append(circle(960, y, 46, "#FFFFFF", LINE, 1.5))
    body.append(f'<circle cx="960" cy="{y}" r="8" fill="{BLUE}" />')
    for x, label, sub in steps:
        body.append(txt(x, y + 92, label, 16, BLACK, weight=600))
        body.append(txt(x, y + 116, sub, 12, GRAY))
    body.append(txt(600, 520, "别一上来就问「要什么才能留下你」——那会让关系显得纯交易", 13, GRAY))
    return "".join(body)


# ---------- 画板 4：隐私边界 ----------
def render_boundary(scene):
    body = [title(scene)]
    body.append(rect(112, 196, 476, 340, FILL, "none", 0))
    body.append(rect(706, 196, 382, 340, "#FFFFFF", LIGHT, 1))
    body.append(line(647, 190, 647, 548, GUIDE, 1, dashed=True))
    body.append(txt(350, 228, "这枚 Skill 用来", 15, GRAY, weight=600))
    body.append(txt(897, 228, "明确拒绝", 15, GRAY, weight=600))
    # 左：帮管理者在意人
    body.append(circle(250, 320, 40, "#FFFFFF", LINE, 1.5))
    body.append(f'<circle cx="250" cy="320" r="8" fill="{BLUE}" />')
    body.append(txt(250, 388, "帮你更好地", 14, BLACK, weight=600))
    body.append(txt(250, 410, "在意一个人", 14, BLACK, weight=600))
    body.append(line(330, 320, 420, 320, LINE, 1.5, arrow=True))
    body.append(rect(432, 288, 120, 64, "#FFFFFF", LINE, 1.4))
    body.append(txt(492, 316, "准备一次", 13, BLACK, weight=600))
    body.append(txt(492, 338, "真诚的谈话", 13, BLACK, weight=600))
    # 右：拒绝清单
    rejects = ["离职预测打分", "人员排序", "背对背画像", "背后监控"]
    for i, rj in enumerate(rejects):
        yy = 280 + i * 46
        body.append(txt(760, yy, "✕", 16, BLUE, "start", 700))
        body.append(txt(792, yy, rj, 16, GRAY, "start"))
    body.append(txt(350, 500, "只对自己直属成员、判断可被本人复核", 12, GRAY))
    body.append(txt(897, 500, "匿名数据不反向识别到个人", 12, GRAY))
    return "".join(body)


RENDERERS = {
    "twostage": render_twostage,
    "states": render_states,
    "offer": render_offer,
    "boundary": render_boundary,
}


def render(scene):
    kind = scene["intent"]["composition"]
    fn = RENDERERS.get(kind)
    if fn is None:
        raise ValueError(f"unsupported composition: {kind}")
    body = fn(scene)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <title>{esc(scene["intent"]["core_message"])}</title>
  <desc>Geometry Board for the 员工离职挽留 skill.</desc>
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth">
      <path d="M 0 0 L 8 4 L 0 8 z" fill="{LINE}" />
    </marker>
  </defs>
  <rect width="{W}" height="{H}" fill="#FFFFFF" />
  {body}
</svg>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for scene_path in sorted(args.scene_dir.glob("*.json")):
        scene = json.loads(scene_path.read_text(encoding="utf-8"))
        out = args.output_dir / f"{scene_path.stem}.svg"
        out.write_text(render(scene), encoding="utf-8")
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
