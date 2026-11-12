---
name: aspen-native-layout
description: Reorder or repair the native Aspen Plus flowsheet canvas through Export18 text and owned COM/file roundtrips. Use for PFD module positions, icon rotation or reflection, stream routes, graphical connection points, and layout persistence after reopening or packaging. Process design and solver acceptance remain with their existing owners.
---

# Aspen原生排布子技能候选

当前是experience中的可安装候选，未自动接入任何活动安装。用户要求保留/修正Aspen内部排布时，父级aspen-plus-operations应路由到本能力；不需要用户再描述实现提示词。自动发现元数据见`agents/openai.yaml`，实际安装仍须核对父级路由和脚本依赖。

先读取当前模型、已接受说明书/PFD和允许修改范围。实际FLOWSHEET/端口角色决定连线，参考图只决定表达；只修图面时冻结全部物理输入与已有求解精度。原生原件在保护副本上处理，不编辑APW/BKP二进制、不以重画外部PNG替代原生排布。

读取[tools接口](references/tools-interface.md)，用本包`pfs_layout.py`的inspect取得当前图元、方向与真实端点，再形成显式layout plan。布局依实际拓扑决定层次和水/物料路由，不能把五级图当所有流程的通用模板。旋转/镜像、缩放和图形附着点都必须记录，不保留全Modifier0再靠长折线绕行。

应用计划并检查全部真实Export4输入卡不变；检查图元集合、图标、At/Scale/Modifier/Label、流股端点/折点、方向和$D。未知格式或图元保留原件并报告具体缺口，不能默默丢掉。检查共线重叠、穿设备与标签压线；普通几何跨线不擅加物理接点。

复用已有operations runtime/supervisor完成原生导入、保存和复开，逐项确认输出确实存在且非空。重开精确APW/BKP再Export18，核同一布局和全部物理卡；如需交付运行模型，再交既有严格审核owner无编辑运行。本包不另造错误计数解析器，也不把布局成功升级为完整工程通过。

先提供单独文件让使用者核图；用户要求打包后，按其明确文件清单打包，独立解压核身份并按所宣称范围复开。程序预览不冒充Aspen截图，未产生的DXF/PDF不当作验收证据。当前用户禁用Computer Use时，全程只走允许的COM/文件方式。

本包代码和测试支持的范围以README与SOURCE_METADATA为准；外部商业帮助主题只作来源定位，不随包附原文。热泵连接素材另见[结构卡](../../materials/five-stage-water-source-heat-pump.md)，其数值、物性、效率与设备能力不得自动成为新案默认。
