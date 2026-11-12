# 模块目录与一次性完整性核对

2026-11-12：本库按12个维护单元组织。一次性核查范围与剩余外部条件见[审查记录](AUDIT_20261112.md)。由独立公开分支归并候选源码与规则，并补齐Dynamics、EDR的真实离线MCP入口；未自动安装客户端、启动商业软件或提升正式准入状态。

|模块|可调用入口|规则与测试|范围|
|---|---|---|---|
|[经验准入与事实核对](../scripts/validate_experience.py)|cli|2规则入口 / 1测试目录|Offline or document scope only; no engineering acceptance|
|[Aspen证据解析](../pool/scripts/aspen-evidence/aspen_evidence.py)|library|1规则入口 / 1测试目录|Offline or document scope only; no engineering acceptance|
|[本地文件交付](../pool/scripts/local-artifact-delivery/artifact_bridge.py)|cli|1规则入口 / 1测试目录|Offline or document scope only; no engineering acceptance|
|[收敛诊断](../pool/scripts/convergence-diagnostics/audit_precision_trials.py)|cli|1规则入口 / 1测试目录|Offline or document scope only; no engineering acceptance|
|[原生流程布局](../pool/scripts/aspen-native-layout/pfs_layout.py)|cli|1规则入口 / 1测试目录|Offline or document scope only; no engineering acceptance|
|[流程边界与受控回调](../pool/scripts/flowsheet-boundary-tools/boundary_compare.py)|cli|1规则入口 / 1测试目录|Offline or document scope only; no engineering acceptance|
|[导出流股审计参考](../archive/2026-10-22/smr-psa-audit-tools/scripts/compare_exported_streams.py)|cli|1规则入口 / 1测试目录|Offline or document scope only; no engineering acceptance|
|[碱性电解方法](../archive/2026-10-30/alkaline-electrolyzer-methods/scripts/acm_parallel_contract_audit.py)|cli|1规则入口 / 1测试目录|Offline or document scope only; no engineering acceptance|
|[Dynamics离线工具](../pool/scripts/aspen-dynamics-tools/toolpack.py)|mcp_cli|2规则入口 / 1测试目录|5 offline MCP tools; not native Dynamics control; catalog/plan never starts external services|
|[EDR与水力学检查](../pool/scripts/edr-hydraulics-checks/scripts/engineering_checks.py)|mcp_cli|2规则入口 / 1测试目录|4 read-only checks; operating-plot position not implemented; not EDR/native or manufacturing acceptance|
|[双效精馏结构规则](../skill_candidates/aspen-double-effect-distillation/SKILL.md)|rules|2规则入口 / 0测试目录|Text and figure candidate; no executable flowsheet or native simulation claim|
|[其它拟定规则与方法](../proposals/EXP-20261012-operating-techniques.md)|rules|23规则入口 / 0测试目录|Contains P0, ACM/membrane, heat-pump boundaries, method persistence, verifiable acceptance and EDR six-item maintenance plan; no MCP needed for text-only rules|

## 重点补齐

- Dynamic原来仅在PR12分支。现在同时包含目录/计划、CSV时间网格、文件清单、历史文本检查、5个实际stdio MCP工具、规则、依赖、示例和测试。它不提供原生Dynamics控制；旧目录中的Plus MCP、专家后台和原生审核器仍是明确的外部依赖。未取得完整许可/依赖闭包的私人源快照没有搬入。
- EDR新增4个只读工具的CLI与MCP封装，附API、规则、4组合成输入、来源身份、依赖、测试及文件manifest。操作图位置诊断仍未实现；FC检查不等于图形居中。
- 原生布局、流程边界、双效结构规则，以及工作方法/方法持久化候选已从其公开分支归并。来源提交和文件身份见[导入记录](imported_sources.json)。旧来源元数据仍只证明原始快照，当前核对以本次回归及文件身份为准。

## 使用与验证

核心离线工具按各README运行，通常只需Python标准库。需要两个MCP入口时，在独立环境安装根目录requirements-mcp.txt；测试使用Python3.14.3、mcp1.28.1、pydantic2.13.4、pydantic-settings2.14.2。配置示例仅供复制修改，不写入本机配置。

```text
python -B -X utf8 scripts/check_module_catalog.py
python -B -X utf8 -m unittest discover -s tests -v
python -B -X utf8 pool/scripts/aspen-dynamics-tools/mcp_server.py
python -B -X utf8 pool/scripts/edr-hydraulics-checks/scripts/checks_mcp.py
```

后两条启动的是供客户端连接的stdio离线服务，不会连接Aspen。原生商业接口需要对应合法安装、许可证、版本核查和自有会话，不能由依赖文件存在推断可用。

文本规则/图件包按完整引用路径打包，不为纯文本规则制造空MCP接口。已有CLI和库的未声明接口仍不承诺存在。生成器为文档维护工具，不是工艺计算或建模器。

## 仍属拟定/外部条件的内容

六项EDR改进中的位置证据分支、诊断回执/消费端范围完善仍按[原提案](../proposals/EXP-20261112-edr-hydraulics-maintenance-plan.md)区分状态；本次补齐的是模块和接口封装，未把未实现算法改写为完成。原生审计、第三方后台和制造认证仍有各自的外部依赖。所有候选继续按准入协议审核，文件齐全、离线测试或MCP调用成功都不是工程验收。
