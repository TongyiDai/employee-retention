# 输入格式规范

`diagnose.py` 的输入是一份**脱敏**的信号 JSON，描述一名成员近期的观察信号。所有内容应由管理者对自己成员的观察或用户明确授权的材料整理而来，不含敏感个人信息。

## 结构

```json
{
  "context": {
    "role": "高级工程师",
    "tenure": "2 年",
    "stage": "signals",
    "note": "阶段：signals（信号微弱）/ expressed（已表达想走）/ has_offer（已有 offer）/ resigned（已递辞呈）"
  },
  "signals": [
    "最近两次架构评审都没怎么发言",
    "站会更新越来越短",
    "私下说过『没什么新东西可学了』",
    "OKR 进展停滞但能力没问题"
  ],
  "manager_can_change": true,
  "trust_note": "关系还不错，平时沟通顺畅"
}
```

字段说明：

- `context.role` / `tenure`：岗位与任期，用于给建议加上下文（不含姓名、工号等身份标识）。
- `context.stage`：所处阶段，影响风险等级与应对方式。
  - `signals`：只有微弱信号
  - `expressed`：已口头表达想走
  - `has_offer`：已拿到别家 offer
  - `resigned`：已递辞呈
- `signals`：观察到的具体信号列表。脚本会和 `five-states.json` 里各状态的 `signals` 做匹配，判断最可能的状态。
- `manager_can_change`：管理者是否能真正改变根因（影响 counter 建议）。
- `trust_note`：信任现状的简短说明（可选，帮助判断补救会不会显得功利）。

## 禁止字段

输入不应包含姓名、工号、邮箱、手机号等身份标识，也不应包含薪酬历史、健康、家庭、年龄、性别、民族、宗教等敏感信息。脚本检测到这类字段会拒绝运行。

`role`、`tenure` 这类岗位上下文不受影响。
