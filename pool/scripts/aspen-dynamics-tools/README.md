# Aspen Dynamics 本地工具包 1.0

把现有 MCP、命令行与文件检查入口归为一处。运行需要 Python 3.10+；工具本身只依赖标准库，不启动 Aspen、COM、MCP 或浏览器，不安装软件、不改 Codex 配置。

## 直接调用

在本目录执行：

```powershell
python -B -X utf8 toolpack.py catalog --settings local_settings.json
python -B -X utf8 toolpack.py plan aspenplus-mcp --settings local_settings.json
python -B -X utf8 toolpack.py plan chemical-expert-cli --settings local_settings.json
```

`catalog` 显示本地工具类别和文件是否存在。`plan` 输出 argv/cwd，仅供已授权任务调用；它不启动或验证服务。MCP 优先使用已连接的命名空间，避免为查询重复拉起服务。Plus MCP 的存在不证明有 Dynamics 接口。

移到另一台电脑时，复制 `local_settings.example.json` 为 `local_settings.json`，填本机路径和环境 Python；不复制旧机环境或许可证。`local_settings.json` 只在完整本地包中保存，公开副本排除它。没有配置的入口保持不可用。

## 文件检查

```powershell
python -B -X utf8 toolpack.py manifest <文件根目录> <manifest.json>
python -B -X utf8 toolpack.py grid <历史.csv> --time-column <列名> --interval <间隔> --start <开始> --end <结束> --time-abs-tol <时间列核对绝对容差>
python -B -X utf8 toolpack.py history <历史.his> --operations-root <aspen-plus-operations目录>
```

- `manifest` 输入 `{"files":[{"path":"relative/file","size":123,"sha256":"..."}]}`，核对清单所列字节；不声称清单完整或文件已被 Aspen 复开。拒绝越界、重复、链接和无效条目。
- `grid` 的间隔、起止和时间核对容差必须由调用者给定，单位与所选时间列一致。`--numeric-column` 可重复指定需要有限数值检查的列。这个容差只用于 CSV 时间列比较，绝不写入求解器。缺点、重复、非有限值和错列都会失败；不插值或补点。
- `history` 动态导入本机现有 `aspen_evidence.py`，不复制第二套汇总/警告规则。非 UTF 编码仅在调用者已有独立编码依据时传 `--verified-encoding`。输出始终限定为离线文本核查，不能证明运行身份、现场消息、精度锁、产品或正式交付。

返回码：0 为该命令声明的文件检查匹配或入口方案可用；2 为不匹配、输入无效或依赖不可用。所有结果中的 `strict_simulation_passed` 均不会因离线检查而变成 true。

## 复用与案例范围

动态建模、原生历史采集、初始化和控制方法沿用已安装 `aspen-plus-operations/references/aspen_dynamics_workflow.md`，接口按当前 Aspen 版本验证。工具包不携带通用设备尺寸、控制器整定值或流程数值。

完整本地发行版另有 `case_audit/`：模型交付压缩包、原始脚本快照、变更表、例外和案例复盘。这些只供显式审计与本案复现，不进入公开工具副本，也不因封装改为严格成功。原生验收仍绑定原来精确路径；换路径的文件身份匹配不能代替新路径的原生复开。

`SKILL.md` 是可显式交给助手读取的包入口；沿用已有操作技能，不另建一套工程判断或自动修改全局技能。脚本功能及本机配置见 `tool_catalog.json` 和本地来源账本。

## 离线验证

```powershell
python -B -X utf8 -m unittest discover -s tests -v
```

测试使用合成文件，验证 CSV、清单、配置和错误处理行为；不运行 Aspen，不产生工程成功证据。公共维护副本只包含通用工具、测试、调用说明与许可，不包含客户文件、路径、日志、参数或对话。

代码 MIT。说明文字 CC BY 4.0。Aspen 软件、手册、模型和第三方组件不随公开包分发；本包不授予其许可。
