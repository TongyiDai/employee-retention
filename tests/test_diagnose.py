#!/usr/bin/env python3
"""diagnose.py 的单元测试。"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "diagnose.py"
FIX = ROOT / "tests" / "fixtures"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


def test_bored_case_detects_state():
    r = run("--input", str(FIX / "case-bored.json"), "--format", "json")
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    labels = [s["label"] for s in out["top_states"]]
    assert "无聊" in labels


def test_warning_signs_raise_risk():
    # 三个预警信号叠加，风险从 low 抬到 medium
    r = run("--input", str(FIX / "case-bored.json"), "--format", "json")
    out = json.loads(r.stdout)
    assert len(out["warning_hits"]) >= 3
    assert out["risk"] == "medium"


def test_has_offer_is_high_risk():
    r = run("--input", str(FIX / "case-has-offer.json"), "--format", "json")
    out = json.loads(r.stdout)
    assert out["risk"] == "high"
    assert out["has_offer"] is True


def test_has_offer_markdown_has_counter_guidance():
    r = run("--input", str(FIX / "case-has-offer.json"), "--format", "markdown")
    assert "别先问" in r.stdout or "放慢" in r.stdout
    # manager_can_change=false 应给出「counter 只是推迟」的提示
    assert "推迟辞职" in r.stdout


def test_reject_pii():
    r = run("--input", str(FIX / "invalid-pii.json"))
    assert r.returncode == 2
    assert "隐私边界" in r.stderr


def test_reject_salary_field():
    r = run("--input", str(FIX / "invalid-pii.json"))
    assert "salary" in r.stderr or "姓名" in r.stderr


def test_standard_plan_always_present():
    # 无论有没有 reason，都先给标准挽留方案
    r = run("--input", str(FIX / "case-bored.json"), "--format", "markdown")
    assert "标准挽留方案" in r.stdout


def test_asks_core_reason_when_no_reason():
    r = run("--input", str(FIX / "case-bored.json"), "--format", "markdown")
    assert "核心原因" in r.stdout
    assert "个性化挽留方案" not in r.stdout


def test_personalized_when_reason_given():
    r = run("--input", str(FIX / "case-bored.json"), "--reason", "觉得晋升没希望，看不到成长", "--format", "markdown")
    assert "个性化挽留方案" in r.stdout
    assert "卡住" in r.stdout  # 自由文应映射到「卡住」


def test_reason_state_key_direct():
    r = run("--input", str(FIX / "case-bored.json"), "--reason", "unappreciated", "--format", "markdown")
    assert "不被赏识" in r.stdout


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"\n{len(fns)} passed")
