# 收敛定位与启动核查方法及离线脚本

条目ID：EXP-20261022-convergence-diagnostics
priority：normal；类型：method_and_code_reference。
状态：用户授权公开的工具与方法参考，不是工程executed_success或正式inbox准入。
公开署名：milklong888；方法文字CC BY 4.0，代码MIT。

本条目整理三项可复用操作：同源显式编辑生成二分隔离变体；按量定义核内外层精度试验；按实际观测与文件身份核冷启动和有界初值扰动。方法保留有效对照、失败分支、单位、物理冻结范围、目标响应和精确交付文件复开要求。

精度和移动阈值必须由当前项目给出。1e-6不作为通用默认值；相对tear准则与绝对产品容差不能直接比大小。脚本不运行Aspen，不自动解释残差平台原因，不读取模型二进制，不新增原生错误计数解析器。原生审核继续调用专业owner。

[完整方法](../pool/techniques/convergence-diagnostics.md) · [代码、接口与合成测试](../pool/scripts/convergence-diagnostics/README.md)

本次公开范围为上述方法及离线代码；不上传原项目、日志、运行结果或私人信息，不把原项目接受状态转换成共享严格成功经验。代码测试和CI仅支持离线工具行为，不构成Aspen求解或设备/产品验收。
