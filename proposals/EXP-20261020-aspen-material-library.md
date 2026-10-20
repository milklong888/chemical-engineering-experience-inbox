条目ID：EXP-20261020-aspen-material-library
类型：improvement_proposal / 架构改进卡
priority：normal
状态：待审设计提案；未实现数据库、未安装Skill、未接入活动图谱或默认检索
公开署名：milklong888
内容许可：CC BY 4.0（本原创提案；引用资料保留原许可）

# 大任务切片为素材，小任务关联专业方法

## 改进目标

用户描述一个目的时，能找到该目的通常对应的工段、Aspen模块和边界；不用每次从一段长对话重新猜结构。宏大案例先简单切片，保留检索所需材料，不把整厂工程流程塞进最高层Skill。细节方法只有确有独立触发和检查价值时才提议独立Skill。

## 分层方案

| 层 | 内容 | 拟放置方式 |
|---|---|---|
| system_slice | 整体系的功能分段、先后关系、工段进出、回收/再生/公用工程边界 | 素材库中的粗粒度卡；不复制项目参数 |
| operation_pattern | purge、补液、降压闪蒸、外置冷凝/再沸等目的到模块链 | 小结构卡，关联变体、接口与harness |
| skill_method | 双效、热泵等需要详细决策和审查的方法 | 未来专业Skill；本轮只提交改进卡，不安装 |
| source_record | 原文位置、版本/身份、可支持范围与未核条件 | 来源记录；不搬运受限全文 |
| case_pointer | 历史案例的精确位置和验收/谱系状态 | 私有审计索引；不自动成为公共样例或默认检索证据 |

拟用稳定ID把“system_slice→operation_pattern→skill_method→source_record”关联起来。Skill提供怎么判断与执行，数据库提供如何找到结构和出处；两者不维护第二份相互冲突的正文。

## 拟定卡片字段

`id, revision, level, goal, aliases, applicable_when, excluded_when, boundary_inputs, boundary_outputs, module_roles, material_edges, heat_edges, work_edges, variants, recycle_returns, legitimate_terminals, control_writer_ownership, harness_ids, source_ids, owner_ref, evidence_scope, lineage_status, review_state, supersedes`

缺项保留未知，不为了填卡发明物料边。历史案例的私有标记和出处不放公开卡。每条来源分别决定可用性；不能因某条已验证就把相邻候选一起提升。

## 初始整理方向

大任务仅做分段骨架：反应及未反应物回收、精馏/萃取及溶剂回收、吸收/再生闭环、热量回收和压力配套。再把purge、补液、分相、换热、升降压和目标控制挂到实际工段。

先核现有Skill和图谱归属，优先复用已有任务路由、节点/流股账、控制体和连接检查。未来数据库可用现成JSON记录作为受审源、SQLite作为可重建查询层；只有现有能力确有缺口才开发。当前卡片没有选定或上线新数据库程序。

## 不做与验收

不从放宽/未知谱系复制数值、修法、反思或成功标签；不把案例摘要当真实运行；不把该素材库变成自动建模授权。候选、准入、检索资格、正式晋升分别记录。

未来实现须用实际任务验证：能检索到适用变体及owner，排除不适用案例，回到原始依据；资料缺失时准确限制依赖结论。文件存在、相似度高和数据库查询成功都不证明工艺成立。

本轮进展：已盘点架构入口并形成提案。数据库建设、活动入口修改、实际Aspen验证均未执行。
