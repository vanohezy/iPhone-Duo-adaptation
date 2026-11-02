# iPhone Duo Adaptation Skill · 折叠屏适配技能

[简体中文](README.md) | [English](README.en.md)

面向 Codex 等支持 `SKILL.md` 的编码助手，优化 iPhone Duo 各姿态下的布局、导航、工具栏、折叠保留区与任务连续性。

研究基线：2026-11-02。依据 Apple 官方 HIG、六场 Tech Talks、SDK 声明和七款 App 的原始发布资料。官方事实、厂商描述、设计推导与实际验收分别标记。内容以中文编写。

## 安装到 Codex

将仓库克隆到技能目录（已有同名目录时先检查，勿直接覆盖）：

```bash
git clone https://github.com/vanohezy/iphone-duo-adaptation.git ~/.codex/skills/iphone-duo-adaptation
```

如设置了 `CODEX_HOME`，使用该目录下的 `skills/iphone-duo-adaptation`。在新对话中调用：

```text
使用 $iphone-duo-adaptation 检查并优化这个 App 在外屏、展开、半折、左右分屏及折叠过程中的体验，完成验证并说明证据。
```

## 内容

- [技能入口](SKILL.md)：工作流程、任务范围和证据边界。
- [官方适配依据](references/official-guidance.md)：SDK 档位、六场讲解、API 与来源。
- [各状态布局](references/states-and-layout.md)：外屏、内屏两个方向、书本/桌面半折、帐篷、开合、左右分屏、PiP、键盘及相机。
- [优秀 App 案例](references/app-patterns.md)：Things、Fantastical、Cardhop、Bulletin、Structured、Detail、Prime Video。
- [代码实现](references/implementation.md)：SwiftUI、UIKit、Flutter、React Native 与 Web 的改造方法。
- [效果验收](references/validation.md)：布局、连续性、无障碍和分层验证。

## 只读布局检查

Python 3 标准库即可运行，无第三方依赖：

```bash
python3 scripts/audit_layout.py /absolute/path/to/app --format markdown
python3 scripts/audit_layout.py /absolute/path/to/app --format json --max-findings 200
```

输出是人工复核候选，可能误报和漏报，不替代编译、运行或真机测试。默认跳过隐藏目录、依赖、构建产物、符号链接、敏感命名文件及大于 2 MiB 的文件；不修改被检查项目。

## 测试

```bash
python3 -m unittest discover -s tests -v
```

覆盖跨平台候选发现、排除目录与符号链接、结果截断、命令行退出状态、文件只读及不可读输入。技能结构已校验，另以播客 App 的现实请求进行独立前测；这些验证不等于任何具体 App 已通过折叠屏真机验收。

## 来源与维护

本项目独立编写，不隶属于 Apple，也不是 Apple 官方 skill。官方文档及厂商内容归各自权利人所有；参考资料以归纳和链接呈现。Apple 原始入口：[Get ready for iPhone Duo](https://developer.apple.com/iphone-duo/)。API 与客户端行为可能更新，实际实施前核对当前官方资料和项目选用的 SDK。

欢迎通过 Issues 或 Pull Requests 提交附有原始来源或复现步骤的修正。请勿提交密钥、个人数据或未经授权的素材。

## 许可证

本仓库原创代码与文档采用 [MIT License](LICENSE)。所引用第三方资料保留其原有权利与条款。
