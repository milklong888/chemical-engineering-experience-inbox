# 规范化与主库同步

2026-11-12：按用户直接维护要求完成三遍规划复核，已同步到
[主工作库0.4.14](https://github.com/milklong888/chemical-engineering-skills/commit/6850a082c190caf2b121c3bd066a289b486ff908)。

12个维护单元和23份提案分别绑定专业owner与处置。完整映射见本目录的
`normalized_proposals.json`、主库`runtime/module_catalog.json`及
[主库整理记录](https://github.com/milklong888/chemical-engineering-skills/blob/6850a082c190caf2b121c3bd066a289b486ff908/docs/MODULE_NORMALIZATION_0.4.14.md)。

- Dynamics、布局、边界及文件辅助归operations；EDR四检查归EDR；收敛观测归error-repair。
- 主库已有双效方法补入专门入口后共有20个Skill；12维护单元与20专业Skill是不同目录范围。
- 专家CLI/MCP的`module_catalog`、`module_check`调用九项允许的离线操作，复用同一专业实现。
- 两组隔离归档保持资格限制，默认工具与安装均排除；归档来源没有升级为成功案例。
- 操作图位置、原生Dynamics控制、自动告警诊断、完整原生依赖解析和预算执行器继续标明未实现。
- 规则编号使用`proposal_id#local_rule_id`；旧固定模型条款服从当前任务授权和分工要求。

代码测试、真实stdio及异目录安装分别验证。主库提交前801项测试通过；这些证据支持
代码、组织和安装，不证明Aspen/EDR运行或工程验收。主库纳入经审查的通用机制不等于
本箱投稿准入；`canonical_admitted`、原提案及来源链身份均不因本次整理自动改变。
