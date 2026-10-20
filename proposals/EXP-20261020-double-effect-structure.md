条目ID：EXP-20261020-double-effect-structure
类型：improvement_proposal / 专业模块结构改进卡
priority：normal
状态：来源支持的待审结构方案；无Aspen执行成功或准入声明
公开署名：milklong888
内容许可：CC BY 4.0（本原创提案；引用资料保留原许可）

# 双效精馏：构型、抽象层级与独立方法边界

## 拟解决的缺口

“双效”不足以唯一决定物料连接。拟建立与热泵专业模块同层的独立方法入口，但本轮仅存改进卡，不安装、不改活动Skill。卡片关联[分构型harness](EXP-20261020-double-effect-harness.md)。

## 候选结构，而非固定配方

| 结构维度 | 模块与接口表达 | 选择前必须明确 |
|---|---|---|
| 平行进料 | 原料分配到两座RadFrac，各自承担明确分离任务 | 分料授权、各自产物指标、产品混合前温压兼容 |
| 顺流/逆流串联 | 原料先入一塔，来源指定的中间物流去另一塔 | 哪股净/循环物流跨塔，第一/第二塔不自动等于高/低压 |
| 端器热流抽象 | 较热塔冷凝端器通过明确热服务耦合较冷塔再沸端器 | 同次Q来源与接收、残余热冷负荷及规格自由度 |
| 显式过程HeatX | HP塔顶gross蒸汽进热侧，凝液分清回流/净采出；LP底部受热液进冷侧，是否形成外部循环及返汽/两相返回按再沸器型式决定 | 真实两侧端口、对应端器职责替换、回流/返汽及净采出 |
| 部分热集成 | 回收热＋有据补热；未利用放热另有冷却 | 实际源汇能力和温焓曲线，不强迫热负荷全部相等 |

此处HP/LP为压力角色，温位仍须由物性与当前温压确认。不同分离任务的塔间热集成可使用相同热原则，但应说明与同一任务多效的边界。

显式LP侧有至少两类需分开：釜式平衡近似可以“加热→汽液分离→气返塔、液作净底产品”；热虹吸/强制循环可“两相返塔内集液区、净底产品另采”。不能一律添加FLASH2，也不能重复采出。

外部Heater若只处理蒸汽/热油并以热流供内部端器，保留端器可以是合法抽象；只有外置设备替代了同一过程物料相变服务，才处理对应内置职责。正式实现优先核目标版本Reboiler Wizard与帮助，不在提案中编造COM路径或卡片。

## 拟定专业方法交接

双效入口负责构型、热服务和端口闭合；塔优化负责初始化、产品目标与SPEC/VARY；operations负责真实建卡、导出与文件证据；设备专业负责同工况物理能力。复用原节点/流股检查器，另核其不能证明的冷热侧隔离、端器等价和热力学。

未来每个方案需交物料/热/功连接表、gross/net、端器热服务账、控制唯一写入者、温焓/压降条件、启动/备用及未知项。结构声明不替代真实端口导出，过程HeatX不替代EDR。

## 独立公开依据及范围

- He等，2023，[DOI 10.1039/D3RA06235J](https://doi.org/10.1039/D3RA06235J)，§3.3/Fig.7支持多种进料构型；不迁移其体系和参数。
- AspenTech，[Distillation Modeling Study Guide](https://www.aspentech.com/en/-/media/aspentech/home/cst-certification/aspen-plus-certification/at-05198_aspen-plus-dm-study-guide)，PDF p11提供端器热曲线、thermosiphon及Reboiler Wizard外置HeatX入口；不证明跨版本卡片。
- Luyben，2022，[DOI 10.1016/j.cep.2022.109068](https://doi.org/10.1016/j.cep.2022.109068)，Heat transfer issues / Aspen simulation implementation / Fig.3支持区别外置过程实现和公用工程热流近似；不把其具体流程当双效唯一通式。
- Luyben，2023，[DOI 10.1016/j.compchemeng.2023.108284](https://doi.org/10.1016/j.compchemeng.2023.108284)，Abstract/Introduction讨论相变温度分布与换热建模；不据此给通用温差或U值。
- HTRI，[thermosiphon operation](https://www.htri.net/news/demystifying-thermosiphon-operation)，Fig.1支持自然循环与回路热水力需独立核验。

公开主张仅为有条件的方法提案；未取得现代官方具体端口/COM语法，也未在当前版本搭建验证。详细源读记录私下保留，论文访问限制不伪装成已由所有审核者复核。
