# dsh-soe-decision-check — 三重一大决策台账核对

[English](README.md) · [简体中文](README-zh.md) · [Español](README-es.md) · [Português](README-pt.md) · [हिन्दी](README-hi.md)

<!-- topblock:v1 -->
> **这是什么**　三重一大决策台账核对。输出一份「哪一行、哪一栏、差什么」的清单。
> **给谁用**　国企/事业单位办公室、纪检；不用懂命令行。
> **你交什么**　这项核对用到的原始材料（表格、清单或文书）；不改原件。Excel 可先转成 JSON/YAML，对话里也能代转。
> **它不做什么**　不判合规、不认定责任、不替代审核人；只列材料内部能逐条指认的差异。
> **怎么开始**　在 WorkBuddy / 扣子搜「文书与治理核对包」（本检查是其中一项；上架以商城为准）；或命令行：
> `dsh plugin --profile <name> add dsh-soe-decision-check`
<!-- /topblock:v1 -->

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)
[![dshfind](https://dshfind.com/api/badge/PerryLink/dsh-soe-decision-check?metric=downloads)](https://dshfind.com/en/plugins/PerryLink/dsh-soe-decision-check?ref=badge)

`dsh-soe-decision-check` 读取一份「三重一大」决策事项台账——企业表头加每个议题一行——核对这份台账自身的程序留痕：每个议题是否记录了议题内容或决策依据、标注为经前置研究的议题是否记录了研究日期、前置研究日期是否不晚于会议审议日期、是否记录了决议结论、已决议的议题是否记录了表决结果、事项类别是否出自你配置的取值口径、台账是否声明企业与决策机构、议题序号是否唯一。

## Install

```sh
dsh plugin --profile <name> add dsh-soe-decision-check
dsh --profile <name> --dump-config | grep 'dsh-soe-decision-check'
```

## 实际输出长什么样

![dsh-soe-decision-check 工作流图：文档 → 规则包 → 核对结果。](docs/assets/dsh-soe-decision-check-flow.svg)

*工作流概览：文档 → 规则包 → 核对结果。下面的示例使用实际命令面。*


本插件对自己 `SD-001` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

### 示例

下表是示例集：第一行是详细走查，其余行是简短案例。


#### 详细输出

**工具** `soe_decision_check`

**输入**

~~~json
{"meetingAt":"2026-03-05","rows":[{"前置研究":"是","前置研究日期":"2026-03-10","会议日期":"2026-03-05"}]}
~~~
 
**输出**

~~~json
{
  "id": "dsh-soe-decision-check.SD-003.de09b5a6",
  "ruleId": "SD-003",
  "severity": "warn",
  "locator": {
    "row": 1,
    "field": "consultedAt"
  },
  "found": "第 1 行「consultedAt」为 2026-03-10，晚于 「meetingAt」的 2026-03-05",
  "expected": "「consultedAt」不应晚于 2026-03-05",
  "fix": "前置研究日期不应晚于会议审议日期；核对两个日期的填写"
}
~~~

*来源 `dsh-soe-decision-check/tests/fixtures/SD-003/SD-003-unsafe.json`*

| 你会问 | 它怎么答 |
|---|---|
| 某个议题的议题内容与决策依据都没有填写，会被报出吗？ | 会。`SD-001` 要求携带这两栏中任一栏的行至少填写一项，两项皆空即报出该行。它只核对是否至少填了一项，不判断该事项是否属于「三重一大」范围，也不判断决策程序与权限是否适当。 |
| 台账标了「已经前置研究」，但前置研究日期空着。 | `SD-002` 读取台账自己的前置研究栏，取值属于「已研究」而研究日期（`consultedAt`）为空时逐行报出。哪些取值算「已研究」由本条的 `conditionValues` 规定（默认为 是、Y、yes、true、已研究、√）。它只核对日期栏是否填写，不判断前置研究是否实质开展、结论是否被采纳；没有任何一行取到这类值时，本条报告自己进入 `skipped`，而不是静默通过。 |
| 前置研究日期晚于会议日期，或者根本读不成日期。 | `SD-003` 比较研究日期（`consultedAt`）与会议日期（`meetingAt`），研究日期晚于会议即报出；同一天视为不晚于。无法解析的日期会单独报出，不会静默跳过。它只比较这两个日期，不判断该程序是否实质履行。 |
| 有一行没有决议结论，另有一行有决议结论却没有表决结果。 | `SD-004` 要求携带决议结论栏（`decision`）的行都填写，`SD-005` 只在已填写决议结论的行上要求表决结果栏（`voteResult`）。两条都不核对票数是否达到规定的通过比例——比例出自本企业实施办法，本条不作计算。 |
| `SD-006` 在我的台账上从来不报任何东西。 | 它的类别取值出厂为空，未配置 `values` 时 `SD-006` 报告自己进入 `skipped`，而不是静默通过。配置本机构的事项类别后，它只核对已填写的类别（`category`，事项类别）是否在册，不判断该事项是否属于「三重一大」范围。 |
| 序号在两行上重复出现。 | `SD-008` 会报出重复的 `matterNo`（比较时忽略空白字符），因为序号重复会让人无法在会议记录中准确指认议题。同一议题在多次会议中审议属于正常情形：请在会议届次上加以区分，不要复用序号。本条只核对唯一性。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
|---|---|---|
| 《关于进一步推进国有企业贯彻落实"三重一大"决策制度的意见》 | 中办发〔2010〕17号（中共中央办公厅、国务院办公厅印发；⚠️ 党内文件，非法律、行政法规或部门规章；全文分三部分，按（一）至（二十三）编号，不设"第X条"） | SD-001, SD-002, SD-003, SD-004, SD-005, SD-006, SD-007, SD-008 |

**边界（中文译文，以英文原文为准）：** 本插件核对一份 **三重一大决策事项台账** 在台账层面可以要求到的程序留痕——每个事项是否记录其提案与依据，标注为已前置研究的事项是否记录研究日期，前置研究日期是否不晚于会议日期，是否存在决定与表决记录，事项类别是否取自你的取值口径，台账是否写明企业与决策机构，以及编号是否唯一。它**不**判定决策是否合规、是否超越权限、金额是否达到“大额资金运作”标准，或应由谁承担责任。

> ### ⚠️ 本插件刻意不知道哪些事（以英文原文为准）
>
> **什么算「三重一大」事项、金额达到多少才算，由各企业自己的实施办法规定**——而阈值因行业、层级与规模而异。因此本插件**不硬编码任何金额阈值，也不硬编码任何事项清单。** 具体做法是：
>
> - `SD-002` 读取台账**自己的「前置研究」栏**来判断某事项是否需要前置研究，而哪些取值算作「已前置研究」是可配置的。
> - `SD-005` **只在记录了决定时**才要求有表决记录，而且它**不核对表决是否达到规定的比例**——该比例来自实施办法，而台账很少记录计算该比例所需的法定人数与表决规则。
> - `SD-006` 的事项类别取值清单出厂为**空**；在未配置任何取值时，它把自己记入 `skipped`。
>
> **规则库中的每一个 `excerpt` 都是它所引条款的逐字引文，且引文门会逐段回到 `rules/evidence/` 的记录里复核。**
> 条款怎么写，规则就怎么引；条款只是隐含，规则就停在 `warn`：由原则性条款推出的检查封顶在 `error` 之下，
> 并在自己的 `note` 里说明。规则库不会做的事是——转述一段条款，然后把转述当成引文。


## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-rc.2`。**已声明 `engines.dsh`**：0.2.1 起由宿主单独裁决，范围为 `>=0.2.1-0 <0.3.0` |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/soe-decision-check.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-soe-decision-check
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## PerryLink DSH Plugin Family

完整清单（62 个核查器 + 通用插件）见 [按材料选核查器](https://perrylink.github.io/zh/checkers/choose/)；本仓只是其中一个。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-soe-decision-check contributors.
