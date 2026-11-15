# Aspen 项目复盘与图文工作流同步

日期 2026-11-15。本文记录公开工作库的维护更新及脱敏的方法摘要。

## Aspen 方法更新

- 核对当前模型、化学身份和目标 Aspen 版本。跨版本复开需读回数据库和有效输入，并以实算结果同步交付文档。
- 修复既有模型前冻结拓扑及原有控制。分别记录稳态、Dynamics 与 HYSYS 文件身份。在动态试验中绑定时间零和工程依赖，比较纯度响应、合格产量及能耗。
- 用原生 Sensitivity 在固定基准下开展板数或回流比试验。分别记录可行点、有限逼近和未覆盖工况。回收塔设计规定采用明确组分和衡算边界。
- 液液分相以化学身份和实际相组成为依据，检查两相有效区间，逐组分闭合。静态换热与季节性水力结论分别核验。
- 按输入、SM、EO 同步和求解阶段记录诊断。定位最早有因果证据的失败与最终未闭合问题，区分上游反应器失败和下游零流量旁路。

[工作库项目方法复盘](https://github.com/milklong888/chemical-engineering-skills/blob/0774d2d59f9b32a8bedec26165181c78bc5890bd/plugins/chemical-engineering-skills/skills/chemical-engineering-expert/references/ASPEN_CASE_REVIEW.md)

## 图文工作流更新

把化工模拟服务写作、案例与短教程、平台表达、配图核验、草稿交付与内容台账并入可按需调用的专家参考。软件原生截图、计算证据和示意图使用不同的来源标记。账号资料及原样图留在本地。

[工作库图文草稿参考](https://github.com/milklong888/chemical-engineering-skills/blob/0774d2d59f9b32a8bedec26165181c78bc5890bd/plugins/chemical-engineering-skills/skills/chemical-engineering-expert/references/CONTENT_DRAFTING.md)

## 维护与证据范围

对应[主库源码提交](https://github.com/milklong888/chemical-engineering-skills/commit/0774d2d59f9b32a8bedec26165181c78bc5890bd)。工作库技能结构、引用、署名、发布完整性及目录合同测试已本地核验。Aspen 项目方法依据已有记录提炼。本轮没有重跑商业软件。诊断、方案研究、历史复算和工程验收各有适用范围；学习排除项目及其派生材料仅留本地审计。本记录归入维护同步，不改变原有投稿、准入与学习状态。
