Output "employee-retention-demo.gif"
Set Shell "bash"
Set FontSize 18
Set Width 1200
Set Height 760
Set Padding 24
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms

Hide
Type "cd /path/to/employee-retention" Enter
Type "clear" Enter
Show
Sleep 600ms
Type "# 喂一个脱敏离职风险案例（假数据），出挽留诊断与风险等级" Sleep 400ms Enter
Sleep 1s
Type "sed -n '1,12p' tests/fixtures/case-bored.json" Sleep 300ms Enter
Sleep 2200ms
Type "python3 scripts/diagnose.py --input tests/fixtures/case-bored.json | head -30" Sleep 300ms Enter
Sleep 3500ms
Type "# 全程脱敏假数据 · 只产草稿/洞察，人工复核后再用 ✅" Enter
Sleep 2800ms
