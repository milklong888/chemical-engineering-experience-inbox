---
name: aspen-dynamics-toolpack
description: Inspect an Aspen Dynamics file package, locate existing local MCP and CLI tools, verify listed file hashes or exported CSV time grids, and organize an explicitly requested local case archive. Native modeling remains with aspen-plus-operations.
---

# Aspen Dynamics 本地工具包

使用 `toolpack.py catalog --settings local_settings.json` 查本机入口；`plan` 只打印调用方案，不启动服务。已连接 MCP 优先；Aspen Plus MCP 不代表 Dynamics 自动化接口。

文件任务使用 `manifest` 和 `grid`。历史文本检查通过 `history --operations-root <installed operations skill>` 调用现有 `aspen_evidence.py`，保留唯一解析 owner。完整命令和参数见 [README.md](README.md)。这些离线检查不证明原生计算、精度锁、产品或工程验收。

需要导出、初始化、控制或扰动试验时进入当前安装的 `aspen-plus-operations`，读取其 `references/aspen_dynamics_workflow.md` 与当前项目合同，核对安装版本。不得从本包继承设备尺寸、流量、控制器增益、误差容差或文献参数。

本地 `case_audit/` 是显式访问的项目档案；每案先读 `LEARNING_ELIGIBILITY.json`。有放宽谱系的案例和历史脚本不能进入默认检索、通用技能、公开经验候选或自动执行。只有客户项目原件保存在本地完整包；公开工具副本不含该目录及机器路径。
