#!/usr/bin/env python3
"""员工离职挽留诊断。

输入一份脱敏的信号 JSON（见 references/input-schema.md），输出：
风险读数、最可能的状态、下次 1:1 要核实的问题、行动计划、谈话脚本、不要做的事。
含身份或敏感个人信息的输入一律拒绝。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 注：re 仅用于 score_states 的信号切词

STATES_PATH = Path(__file__).resolve().parent.parent / "references" / "five-states.json"

# 身份 / 敏感字段：作为 key 出现即拒绝
FORBIDDEN_KEYS = {
    "姓名", "工号", "邮箱", "手机号", "身份证", "花名",
    "name", "employee_id", "email", "phone", "id_card",
    "salary", "薪酬", "薪资", "工资", "健康", "health",
    "家庭", "family", "年龄", "age", "性别", "gender",
    "民族", "宗教", "religion",
}

STAGE_RISK = {
    "signals": "low",
    "expressed": "medium",
    "has_offer": "high",
    "resigned": "high",
}


def load_states() -> dict:
    with STATES_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def scan_forbidden(obj, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN_KEYS:
                hits.append(f"{path}.{k}" if path else k)
            hits.extend(scan_forbidden(v, f"{path}.{k}" if path else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits.extend(scan_forbidden(v, f"{path}[{i}]"))
    return hits


def score_states(signals: list[str], states: dict) -> list[tuple[str, dict, int]]:
    """把观察信号和各状态的信号库做关键词重叠打分。"""
    text = " ".join(signals)
    scored = []
    for key, st in states["states"].items():
        score = 0
        for sig in st["signals"]:
            # 取信号里的关键词做宽松包含匹配
            for token in re.split(r"[，、/：:；;（(]|的|了|和", sig):
                token = token.strip()
                if len(token) >= 2 and token in text:
                    score += 1
        scored.append((key, st, score))
    scored.sort(key=lambda x: -x[2])
    return scored


def match_warning_signs(signals: list[str], warning: list[str]) -> list[str]:
    text = " ".join(signals)
    # 每条预警信号的核心关键词，用于宽松匹配观察信号
    keywords = {
        "不再在方案/架构讨论中发言": ["架构", "方案", "评审", "不发言", "没发言", "不说话"],
        "不再推动更好的实践与标准": ["推动", "实践", "标准", "最佳实践"],
        "文档、复盘这类『额外投入』消失": ["文档", "复盘", "额外投入"],
        "长期问题/技术债被默默降级、不作解释": ["技术债", "降级", "长期问题", "ticket"],
        "汇报/站会更新越来越短、越来越机械": ["站会", "汇报", "更新", "机械", "越来越短"],
    }
    hits = []
    for w in warning:
        for token in keywords.get(w, [w]):
            if token in text:
                hits.append(w)
                break
    return hits


def build_report(data: dict, states: dict) -> dict:
    ctx = data.get("context", {})
    stage = ctx.get("stage", "signals")
    signals = data.get("signals", [])

    risk = STAGE_RISK.get(stage, "low")
    # 多个预警信号叠加会抬高风险
    warn_hits = match_warning_signs(signals, states["warning_signs"])
    if risk == "low" and len(warn_hits) >= 3:
        risk = "medium"

    scored = score_states(signals, states)
    top = [s for s in scored if s[2] > 0][:2]
    if not top:
        top = []

    return {
        "stage": stage,
        "risk": risk,
        "risk_desc": states["risk_levels"][risk],
        "warning_hits": warn_hits,
        "top_states": top,
        "manager_can_change": data.get("manager_can_change"),
        "context": ctx,
        "has_offer": stage in ("has_offer", "resigned"),
    }


def standard_plan(states: dict) -> list[str]:
    """无论诊断结果如何，都先给一套标准挽留方案（五状态全覆盖）。"""
    L = ["## 标准挽留方案（先看这个）", ""]
    L.append("在还没锁定具体原因前，这套方案覆盖五种最常见的离职状态。逐条对照，看哪几条最贴合你观察到的情况：")
    L.append("")
    for key, st in states["states"].items():
        first = st["interventions"][0]
        L.append(f"- **{st['label']} → {st['needs']}**：{first}")
    L.append("")
    L.append("通用动作：约一次 1:1，先听再判断；给具体而非泛泛的认可；不承诺你控制不了的时间线。")
    return L


def resolve_reason(reason: str, states: dict):
    """把用户给的核心原因（状态 key 或自由文）映射到某个状态。"""
    if not reason:
        return None
    if reason in states["states"]:
        return reason, states["states"][reason]
    # 自由文：按状态标签、需要、信号做关键词匹配
    best, best_score = None, 0
    for key, st in states["states"].items():
        score = 0
        pool = [st["label"], st["needs"]] + st["signals"]
        for p in pool:
            for token in re.split(r"[，、/：:；;（(]|的|了|和", p):
                token = token.strip()
                if len(token) >= 2 and token in reason:
                    score += 1
        # 一些常见词直接归类
        if key == "unappreciated" and any(w in reason for w in ["钱", "薪", "涨薪", "报酬", "认可", "赏识"]):
            score += 2
        if key == "bored" and any(w in reason for w in ["无聊", "没意思", "重复", "挑战"]):
            score += 2
        if key == "stuck" and any(w in reason for w in ["晋升", "成长", "瓶颈", "看不到", "发展"]):
            score += 2
        if key == "lonely" and any(w in reason for w in ["孤独", "融不进", "氛围", "关系"]):
            score += 2
        if key == "apathetic" and any(w in reason for w in ["没意义", "麻木", "热情", "价值感"]):
            score += 2
        if score > best_score:
            best, best_score = key, score
    if best and best_score > 0:
        return best, states["states"][best]
    return None


def personalized_plan(reason: str, states: dict) -> list[str]:
    """基于用户给出的核心原因，生成个性化挽留内容。"""
    L = ["## 个性化挽留方案", ""]
    L.append(f"你判断的核心原因：**{reason}**")
    L.append("")
    resolved = resolve_reason(reason, states)
    if not resolved:
        L.append("这个原因没有清晰落到五状态里。建议在 1:1 里先厘清：是认可、连接、挑战、成长还是意义出了问题？确认后再定干预。")
        L.append("如果根因不在你可改变范围内（换赛道、搬家、家庭原因等），把重点放在体面告别和保护关系上，别硬留。")
        return L
    key, st = resolved
    L.append(f"最贴合的状态是「**{st['label']}**」，他需要的是「**{st['needs']}**」。")
    L.append("")
    L.append("**针对性干预：**")
    for a in st["interventions"]:
        L.append(f"- {a}")
    L.append("")
    L.append("**下次 1:1 先核实：**")
    for q in st["verify_questions"]:
        L.append(f"- {q}")
    return L


def to_markdown(r: dict, states: dict, reason: str = "") -> str:
    ctx = r["context"]
    L = ["# 离职挽留诊断", ""]
    who = " · ".join(x for x in [ctx.get("role"), ctx.get("tenure")] if x)
    if who:
        L.append(f"对象背景：{who}")
    L.append(f"**风险等级：{r['risk'].upper()}** — {r['risk_desc']}")
    L.append("")

    # 一、标准挽留方案：无论信号多少都先给
    L.extend(standard_plan(states))
    L.append("")

    if r["warning_hits"]:
        L.append("## 命中的脱离预警信号")
        for w in r["warning_hits"]:
            L.append(f"- {w}")
        L.append("")

    if r["top_states"]:
        L.append("## 从现有信号看，最可能的状态")
        for key, st, score in r["top_states"]:
            L.append(f"### {st['label']} → 需要「{st['needs']}」")
            L.append("**下次 1:1 要核实：**")
            for q in st["verify_questions"]:
                L.append(f"- {q}")
            L.append("**干预方向：**")
            for a in st["interventions"]:
                L.append(f"- {a}")
            L.append("")

    L.append("## 行动计划")
    if r["risk"] == "high":
        L.append("- 立即处理，不要等年度评估周期。")
    L.append("- 本周：约一次 1:1，用上面的问题核实状态，先听再判断。")
    L.append("- 本月：针对确认的状态，落一个具体、你能兑现的干预。")
    L.append("- 结构性：把这次暴露的问题（认可机制、成长路径、业务连接等）补进日常管理。")
    L.append("")

    if r["has_offer"]:
        L.append("## 对方已有 offer / 已递辞呈")
        L.append("放慢，别先问「要什么才留下」。顺序：理解为什么开始看 → 判断你能否真正改变根因 → 只在修复真实/快速/公平时 counter → 无论去留都保护关系。详见 references/has-another-offer.md。")
        if r["manager_can_change"] is False:
            L.append("")
            L.append("> 你标记了根因不在你可改变范围内。这种情况下 counter 往往只是推迟辞职；把重点放在体面告别和保护关系上。")
        L.append("")

    # 二、个性化：用户给了核心原因就生成，否则抛出追问
    if reason:
        L.extend(personalized_plan(reason, states))
        L.append("")
    else:
        L.append("## 下一步：请你判断核心原因")
        L.append("以上是标准方案。要生成更贴合的个性化挽留内容，请回答一个问题：")
        L.append("")
        L.append("> **你认为这位员工要走的核心原因是什么？**（可以是：不被赏识 / 孤独 / 无聊 / 卡住 / 麻木，也可以用你自己的话描述，比如「觉得晋升没希望」「拿到了翻倍的 offer」「家在外地想回去」）")
        L.append("")
        L.append("拿到你的判断后，我会据此生成针对性的干预、谈话脚本和核实问题。")

    L.append("")
    L.append("> 提醒：保留的前提是对方相信你因为在意他而行动，而不是怕失去他。有些人留不住是正常的，好聚好散。")
    return "\n".join(L).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="员工离职挽留诊断")
    parser.add_argument("--input", required=True, help="脱敏信号 JSON 路径")
    parser.add_argument("--reason", default="", help="用户判断的核心离职原因（状态 key 或自由文），给了就生成个性化方案")
    parser.add_argument("--format", default="markdown", choices=["markdown", "json"])
    args = parser.parse_args(argv)

    with open(args.input, encoding="utf-8") as fh:
        data = json.load(fh)

    hits = scan_forbidden(data)
    if hits:
        print("错误：输入包含身份或敏感字段，拒绝诊断（隐私边界）。命中：" + "; ".join(hits[:8]),
              file=sys.stderr)
        return 2

    states = load_states()
    report = build_report(data, states)
    if args.format == "json":
        # 精简 JSON，去掉不可序列化的嵌套
        out = {k: v for k, v in report.items() if k != "top_states"}
        out["top_states"] = [{"key": k, "label": st["label"], "needs": st["needs"], "score": sc}
                             for k, st, sc in report["top_states"]]
        sys.stdout.write(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(to_markdown(report, states, args.reason))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
