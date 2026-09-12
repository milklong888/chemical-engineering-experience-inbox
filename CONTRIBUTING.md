# 投稿 / Contributing an experience

中文使用者可直接按 [中文投稿指南](docs/USER_SUBMISSION_GUIDE.zh-CN.md) 操作：
让助手先在本地整理，本人授权准确的公开内容，再通过 GitHub Fork + PR 提交
`proposals/<条目ID>.md` 脱敏候选摘要。完整 `submission.json` 及私人证据不提交。
当前没有一键上传、后台投稿或已配置的私人证据安全提交渠道；需要私人证据时，
先留本地并由维护者安排核验。`inbox/` 由维护者在独立核验后写入，CI 绿色不自动准入。

支持提醒机制的 Skill 应在有证据且值得复用的成功经验，或已确认并审核的原则
出现时，主动展示精确拟公开摘要、适用边界和投稿入口。首次公开须本人 opt-in；
可使用明确范围、可撤回的持续授权，但仍须核对本条内容在范围内。不要每回合
提醒，也不要在使用者拒绝后反复催促。此机制是否可用，以实际安装版本为准。

Submit only a method summary you have authority to publish. This repository is
public. Creating a PR or issue must be a deliberate action by the contributor;
installation or use of a Skill does not opt anyone into uploads.

1. Choose `executed_success` or `thought_principle` using
   [the admission protocol](docs/ADMISSION_PROTOCOL.md).
2. Prepare the evidence and admission record locally. The JSON files in
   [`examples/`](examples/) are synthetic governance demonstrations, not public
   submission forms. Do not publish the complete `submission.json`, which may
   contain private records. Changing `synthetic` to false does not supply evidence.
3. Keep raw project files, logs, private messages, credentials and licensed
   source pages local. A maintainer must review the sanitized public content,
   the actual contributor's sharing authority and its evidence scope before
   admitting it. Do not post sensitive evidence in a public PR to request review.
4. Bind opt-in to the final item/content digest. For thoughts, user confirmation
   must precede assistant review; changing the content requires fresh events.
   For successful executions, maintainers check the actual relevant run and
   tested version. A Git commit or green badge alone cannot establish success.
   A contributor may give a revocable standing grant with explicit repository,
   content and validity scope; independently verify that this exact item is
   covered before publication. A reminder itself never supplies opt-in.
5. Fork this repository, add only the authorized sanitized candidate summary at
   `proposals/<item-id>.md`, and open a PR to this repository. Do not write an
   admission claim into `inbox/`; maintainers own those entries. A public PR is
   already publication of its text, even while review is pending: review the
   exact export first. CI tests the repository code; a green result or a merged
   PR does not by itself admit the experience. Report pending status honestly.

There is currently no configured secure channel for sending private evidence.
Keep it local until a maintainer arranges an appropriate verification method;
do not put it in a public PR or issue. Already-public source code and execution
evidence may be cited with their actual public links. There is no automatic
upload service, and installing this or the main Skill repository does not
silently upgrade every user's installed workflow or authorize their uploads.
Skills supporting contribution reminders should show the exact proposed public
summary, applicability limits and entry point when supported reusable experience
is found, rather than prompt every turn or repeatedly after a refusal. Availability
depends on the user's actual installed version.

By deliberately submitting original experience text with an explicit
CC-BY-4.0 declaration and opt-in, you offer that text under the
[Creative Commons Attribution 4.0 International license](https://creativecommons.org/licenses/by/4.0/).
The local admission record binds that declaration as `publish.license`; the
complete record must not be added to the public PR.
Code contributions use the repository's MIT license. Do not submit material
whose rights you cannot grant. Attribution uses your chosen public contributor
identifier; no private identity information is required.

Maintainers keep confirmation/evidence observations outside the public
submission repository and add only approved allowlisted summaries to the inbox.
No PR automatically changes canonical Skills, knowledge graphs, default
retrieval or model weights. The owner periodically requests a separate
consolidation review; candidates can merge, specialize, replace, remain local,
or be rejected with an evidence-bound reason.

To withdraw consent before admission, tell the maintainer the item ID and
revision; the next publication check must observe that revocation. For content
already made public, request a withdrawal record/removal; deleting a file cannot
guarantee removal from historical clones or other recipients.
