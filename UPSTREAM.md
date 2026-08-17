# 上游与先例

## 上游来源

- 上游项目：[manager-dot-dev/manager-skills](https://github.com/manager-dot-dev/manager-skills)
- 上游 Skill：[skills/retaining-developers](https://github.com/manager-dot-dev/manager-skills/tree/c47ebc7adc3ef84056f059e2a426077cfe12de8c/skills/retaining-developers)
- 固定版本：`c47ebc7adc3ef84056f059e2a426077cfe12de8c`
- 上游许可证：MIT
- 核验时间：2026-08-17（Asia/Shanghai）

## 保留与扩展

上游 Skill 面向工程管理者，核心是五状态保留框架、脱离预警信号、股权沟通、零预算认可和「对方已有 offer」的应对。本包保留这些方法，并做了实质扩展：

- **场景泛化**：从「工程管理者带工程师」泛化为任意团队管理者挽留任意核心成员，工程例子保留但不独占。
- **中文语境重写**：五状态、谈话脚本、股权与认可、应对 offer 全部按中文职场语境改写，不是逐字翻译。
- **二段式工作流**：先给覆盖五状态的标准挽留方案，再追问「核心原因」，据用户判断或飞书证据生成个性化内容。
- **本地诊断脚本**：把脱敏信号整理成风险读数、状态判断、行动计划、谈话脚本；支持 `--reason` 做原因映射与个性化。
- **飞书证据集成**：从 1:1 记录、会议纪要、OKR、交流内容中只读、脱敏地梳理某成员的信号与成长轨迹。
- **隐私硬约束**：只对自己直属成员用、不做离职预测打分、不做背对背画像、不做监控；诊断脚本拒绝含身份或敏感字段的输入。
- **与员工敬业度匿名调研联动**：群体匿名信号提示关注方向，但不反向识别到个人。
- **假数据回放与单元测试**：10 项测试覆盖状态识别、预警抬升、二段式、原因映射、隐私拒绝。

## 公开先例

- [5 reasons why your best developers will quit](https://newsletter.manager.dev/p/why-developers-quit)：五状态保留框架（不被赏识/孤独/无聊/卡住/麻木）。
- [The Guide to Stock Options conversations](https://newsletter.manager.dev/p/the-guide-to-stock-options-conversations)：入职/在职/离职三时点的股权沟通。
- [How to WOW your engineers without budget](https://newsletter.manager.dev/p/how-to-wow-your-engineers-without-budget)：零预算认可做法。
- 脱离预警信号为 manager.dev 课程的原创材料。

方法为中文语境重写与再组织，非上游文本的逐字复制。
