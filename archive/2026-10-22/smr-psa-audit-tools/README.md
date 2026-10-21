# SMR+PSA建模复盘与离线审计参考脚本

record_kind：method_audit_reference；状态：待独立复用验证，不是executed_success。
learning_eligible=false；success_case_eligible=false；default_rule_eligible=false；default_retrieval_eligible=false。
代码MIT；说明CC BY 4.0。来源为用户明确要求的本次工作方式维护及离线工具整理。

## 先检查的两条bug

先执行[前置P0-016/017](../../../proposals/EXP-20261022-knowledge-escalation-p0.md)：原生图谱、官方知识库、最后websearch；未知warning立即同序取证。此前“完整反应参数/适用性先于方案”和“单位/量定义先换算再录入并原生读回、按需要实际使用Calculator/Design Spec”的原始bug记录也已随本次案例归入本地experience隔离审计，未改成无条件工艺默认。

## 这次建模经验支持到哪里

过程模型可用原生Design Spec控制明确产能目标，Calculator按真实上游值联动新鲜补水、燃烧需氧量与反应供热；依赖顺序和循环关系必须由当前模型实际验证。没有源数值和原生执行证据时，不能只凭外部脚本或工具路由名称宣称这些控制已运行。平衡反应模型与实际有限床层、理想分离包与多床吸附循环分别表述。

物热核查应逐叶区分容器、空值、实际零流和独立相组成；总循环水不等于新鲜水，流体焓功不等于全部轴功，内部换热不重复作为外部供热，附加分离/冷却负荷也要进入账本。反应净转化的分子、分母及碳基准须显式定义；参考平衡计算不是动力学或设备保证。这里没有发布任何该项目温压、物料、回收率或转化率作为推荐默认值。

详细诊断可以显示简略日志未显示的结果生成问题。具体故障文本消失与总warning消失分别检查；原生对象状态也不能覆盖完整Summary中的非零计数。重新初始化只能作为需验证的诊断动作。官方逐物流相态选项只能在当前真实相态证据支持时使用，不能推广为同类warning的一键修复。

BKP/INP交付须绑定各自真实路径、实际运行和关闭后文件组身份；不能根据文件名、保存成功或包内hash推断工程通过。同主干导入存在文件副作用时按本案证据隔离原件与恢复动作，不写成所有版本的必然机制。完整项目及原始实现只保留本地审计，不由此目录取得工程接受或自动复用资格。

## 可复用代码的明确接口

- `scripts/exported_phase_facts.py`：指定worker JSON、物流、组分与输出位置，严格读取已有原生叶子，区分总体zP与汽相分压，不执行新闪蒸或物性计算。
- `scripts/compare_exported_streams.py`：指定两个worker JSON，对照数值/单位/缺失与新增；相同数值不能推出相同警告或通过严格门。
- 只使用Python标准库；不调用Aspen、COM、网络或修改源文件。必须由调用者提供当前任务导出与明确参数，不携带项目数值或私人路径。
- 完整Summary/history的解释继续由原专业owner的唯一审查器处理；本目录不另写原生计数解析器，不把离线测试当Aspen运行。

```text
python -B -X utf8 scripts/exported_phase_facts.py --help
python -B -X utf8 scripts/compare_exported_streams.py --help
python -B -X utf8 -m unittest discover -s archive/2026-10-22/smr-psa-audit-tools/tests -v
```

CLI实际参数以脚本--help为准。SOURCE_METADATA.json绑定最终脚本/测试字节与验证范围；原项目证据、确认原文和运行日志不会随公共包上传。

## 原始权威入口

- AspenTech KB [000056985：对象PER_ERROR](https://esupport.aspentech.com/S_Article?id=000056985)
- AspenTech KB [000077076：逐对象运行消息](https://esupport.aspentech.com/S_Article?id=000077076)
- AspenTech KB [000083571：Run/Reinit控制](https://esupport.aspentech.com/apex/S_Article?id=000083571)

字段、状态位和相态选项仍需核当前安装版本帮助；这些链接支持方法查询，不是本次流程工程接受证书。公共内容仅为获授权的方法说明及代码审计参考；临时inbox准入、正式Skill/KG整合与设备/产品验收各自另行核验。
