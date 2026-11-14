# adr-skills

[English](README_EN.md)

面向软件项目的架构决策工作流：从受影响代码检查、ADR（架构决策记录）撰写，到独立方案审查和分阶段实施。你可以使用总入口衔接流程，也可以只调用需要的阶段。

## 技能一览

| Skill | 用途 |
| --- | --- |
| `adr-workflow` | 根据请求和授权组织各阶段。 |
| `adr-check` | 检查受影响的代码职责、依赖和新职责落点。 |
| `adr-writing` | 讨论并撰写 ADR、阶段计划和验收合同。 |
| `adr-review` | 独立审查方案并给出可核对的结论。 |
| `adr-implementation` | 按已确定的 ADR 分阶段实施、测试和验收。 |

五个目录组成一个套件。**请把整套安装在同一个 Skills 父目录中**：总入口会用到其他组件，实施组件也引用审查组件的指纹规则。各阶段可以单独调用，但仅安装一个目录可能缺少依赖。

## 安装

### 使用 Skills CLI

在要使用的项目目录中运行；需要 Node.js 22.20 或更高版本。下面的命令安装到当前项目，不会全局安装。

```sh
# 查看套件中的技能
npx skills add DOIT-Ben/adr-skills --list

# 安装整套到 Codex
npx skills add DOIT-Ben/adr-skills --skill '*' --agent codex --copy --yes

# 安装整套到 Claude Code
npx skills add DOIT-Ben/adr-skills --skill '*' --agent claude-code --copy --yes
```

如需全局安装，可在选定目标后加入 `--global`；安装前先核对已有同名技能。Skills CLI 是可选的第三方工具，有关联网和遥测选项见其[官方说明](https://github.com/vercel-labs/skills#telemetry)。

### 手动安装

克隆或下载本仓库，将 `skills/` 下的五个完整目录复制到目标智能体的 Skills 父目录，保留同级结构。Codex 和 Claude Code 的具体目录取决于个人或项目安装范围；若已有同名目录，请先检查再更新。不要只复制 `SKILL.md`，因为模板和参考资料也是流程的一部分。

安装后开始新会话，并检查客户端是否发现所需技能。技能正文主要使用中文；所用模型需要能够理解中文指令。

## 使用示例

```text
使用 adr-workflow，检查这个项目中增加笔记导出功能会影响哪些模块，
撰写 ADR 并做独立方案审查。本次不实施代码。
```

也可以要求 `adr-check` 只检查代码影响，要求 `adr-writing` 只写草案，或要求 `adr-review` 审查现有方案。执行已审查的方案时使用 `adr-implementation`，并提供 ADR、阶段计划与获准范围。

独立审查可由未参与撰写的人员或具有独立上下文的代理完成。无法获得独立审查时，方案保持待审，不以自查代替通过。实施、提交和发布均以用户实际授权为准。

## 验证和维护

使用 Python 3.9 或更新版本，在仓库根目录运行：

```sh
python -m unittest discover -s tests -v
python scripts/audit_privacy.py
```

测试覆盖技能入口、依赖引用和安装布局；隐私筛查检查未忽略的工作区文件与本地可达 Git 历史，只输出类别和位置。筛查不能识别所有隐私，公开前仍需人工检查内容与历史。真实智能体的识别与执行也需在目标客户端中验证。

本仓库维护可分发版本。若另有个人化副本，更新时应逐项对照并选择性合并，保留通用行为，避免直接复制私有配置、机器路径或个人验证记录；同步后重新运行检查。

## 许可证

[MIT](LICENSE)
