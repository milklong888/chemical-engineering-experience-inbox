条目ID：EXP-20261020-aspen-small-patterns
类型：improvement_proposal / 零碎操作素材卡
priority：normal
状态：待审目的到模块映射；不是已运行案例或上线数据库
公开署名：milklong888
内容许可：CC BY 4.0（本原创提案；引用资料保留原许可）

# 目的到模块：purge等小结构先作为素材

以下用于决定应查哪个专业方法，不是可直接执行的默认建模脚本。模块次序中“必要”均须由当前相态、温压、职责和来源决定，不给固定比例或工况。

| 目的 | 候选模块结构 | harness：不要做 |
|---|---|---|
| 循环排出一部分 | 回收流→FSplit→purge终端＋recycle返回 | 不用SEP凭空只排杂质而零损失保留有价物；不把split叫选择性分离 |
| 冷凝回收后气相purge | Heater/HeatX冷却→Flash2；气相FSplit后排放/返回，液相按真实去向 | 不把全流分流当仅排未凝气；不由总汽化率猜杂质回收 |
| 溶剂补液 | 贫液返回＋新鲜补液→Mixer→必要泵/冷却→接收端 | 不把总循环量当持续新鲜补液；不混淆净损失与gross |
| 气液/两液相分离 | Flash2 / Flash3 / Decanter，按所需相态和物性选择 | 不用FSplit分相，不忽略第二液相 |
| 返回高压节点 | 液体Pump、气体Compr；需要时多级与级间冷却/分液 | 不用Heater无功升压，也不默认任意压缩机可处理任意含液量 |
| 降压后分相 | Valve→需要时Flash2/Flash3 | 不把节流算轴功回收，不忽略出口相态 |
| 单股稳温或真实回热 | Heater表示热边界；HeatX表示两侧实际换热 | 不由两台相反Q的Heater声称已有实体换热器/面积/EDR |
| 吸收与再生 | 吸收配置RadFrac→富液→再生配置RadFrac→贫液返回 | 不把平衡级塔当内件/传质能力已经核实；不强套不适用DSTWU |
| 隐式质量目标 | Design Spec＋合法独立Vary | 不由Calculator每轮同时写同一操纵量 |
| 显式联动/循环数值 | Calculator/适用Balance＋真实返回流与tear安排 | 不把tear当物理排污或切断返回后声称闭合 |

purge比例由组分去向、累积限制与有价物损失衡算，不给默认1%等数值。气相purge与全流purge的控制体不同；所有出口、反应源汇及返回都须纳入当前组分衡算。

## 结构卡应带的最小内容

目的/适用前提；候选变体；每股产消端；补料/循环/净采出/终端；热功和压力服务；唯一控制写入者；来源与证据边界；触发harness；需要的专业owner。细节没有足够依据时保留待核，先不派生独立Skill。

## 来源与待核

- Aspen原厂[Version 10.1 User Guide大学镜像](https://terpconnect.umd.edu/~nsw/chbe446/AspenPlusV10UserGuide1.pdf)，印刷10-4提供FSplit分流/purge语义；旧版本字段不当现代语法保证。
- AspenTech [Distillation Modeling](https://www.aspentech.com/en/products/pages/distillation-modeling-in-aspen-plus/)提供现行严格/速率模型入口；具体版本、进料方向、端器与接触结构另核。
- 现有专业owner负责换热、压力设备与原生控制工具；本卡是它们的检索/交接提案，不取代实现规则。

尚未完成这组映射的跨版本软件执行、设备核验或独立行为测试，不写executed_success，不把原案例的放宽结果用作本卡依据。
