# 普通脚本池：Aspen错误证据纯解析模块

条目ID：EXP-20261012-aspen-evidence-parser  
优先级：normal  
类型：script / bounded offline code behavior  
状态：已保存原版公开工具与回归测试；不是inbox准入记录或工程验收证明。

本包复用已有 aspen-plus-operations 的原版 aspen_evidence.py，不另造解析规则。输入是调用者已取得的文本或字节；依赖Python标准库，不启动COM、不改模型、不写文件。调用者仍须取得当前版本/格式及同次运行的真实证据。

## 来源与许可

代码及测试固定来源提交：
https://github.com/milklong888/chemical-engineering-skills/commit/fdd6a1e6d56279e6376dada934a230aea3be85ab

原始文件路径：
- plugins/chemical-engineering-skills/skills/aspen-plus-operations/scripts/aspen_evidence.py
- plugins/chemical-engineering-skills/skills/aspen-plus-operations/scripts/tests/test_aspen_evidence.py

代码SHA256：7465D04FC8D1114D65A9F64C94ABDA32FA885B7A6C8E493AEC4B90034E9A3F31  
测试SHA256：D830F107E1E47EFB7C9423D1DCB2B52EAF90F515C5885C1E8DBCC54BB1514279

随包保留MIT LICENSE及THIRD_PARTY_NOTICES.md，许可文件来源固定到：
https://github.com/milklong888/chemical-engineering-skills/commit/98a2ea53a127cad7e2fecd0df447a89f5ca014a0

该代码提交当时未有LICENSE文件；当前公开MIT声明下的代码与本包固定代码字节一致。代码不改为投稿摘要的CC BY许可。公开版本、摘要和源码身份见 SOURCE_METADATA.json。

THIRD_PARTY_NOTICES.md保留上游整包声明原文，其中其他目录的相对链接指上游仓库，不表示本脚本副本附带这些第三方组件、知识库或原始资料。上游原声明见 https://github.com/milklong888/chemical-engineering-skills/blob/98a2ea53a127cad7e2fecd0df447a89f5ca014a0/THIRD_PARTY_NOTICES.md 。

## 接口与边界

- parse_summary_counts(text, *, profile=...)：解析汇总表；缺失或未支持的证据不得补零。
- inspect_history_text(text, *, source='history', source_sha256=None)：检查取得的完整历史文本。
- evaluate_clean_gate(...)：对调用者传入的运行身份、汇总/消息/历史等检查严格求解证据。

函数签名和返回字段以原文件为准。本包不会取得Aspen界面，不覆盖所有未知表格格式，不处理产品/设备设计证明，也不自行决定接受项目的豁免。求解证据通过不等于完整工程交付。

## 离线回归

从经验仓库根目录执行：

    python -B -m unittest discover -s pool/scripts/aspen-evidence/tests -v

测试保持源版原样，使用合成文本。已观察到27项通过，支持这些测试覆盖的解析行为；不证明任何实际Aspen模型通过。此包不附模型、真实history、客户信息或私人运行回执。合并后的CI只按其实际检查范围表述。

普通技巧见 [工作方法候选](../../../proposals/EXP-20261012-operating-techniques.md)，优先级规则见 [分级说明](../../../docs/PRIORITY_POLICY.md)。

