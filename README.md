# dsh-soe-decision-check — State-owned enterprise “三重一大” (three important and one large) decision register procedural-trail check

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-soe-decision-check` reads one “三重一大” decision register — the enterprise header plus one row per matter — and checks that register's own procedural trail: that each matter records its proposal or its basis, that a matter marked as pre-studied records a study date, that the pre-study date is not later than the meeting date, that a decision is recorded and a decided matter records its vote, that the matter category comes from the vocabulary you configure, that the register names the enterprise and the deciding body, and that matter numbers are unique.

## What it looks like

![Terminal demo of dsh-soe-decision-check: real output over its SD-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-soe-decision-check/main/docs/assets/dsh-soe-decision-check-demo.png)

Real output from this plugin over its own `SD-001` test fixture — not a mock-up. The rule pack ships no invented quotations, so a finding names both the clause it applied and the fact that the clause text was not obtained.

## What it answers

| You ask | What it answers |
|---|---|
| A matter has neither its proposal nor its basis filled in. Does the check say anything? | Yes. `SD-001` requires at least one of those two columns on every row that carries either one, and reports the row when both are blank. It checks that at least one is filled, not whether the matter belongs to the “三重一大” scope, and not whether the decision procedure or the authority behind it was appropriate. |
| The register marks a matter as pre-studied, but the study date is empty. | `SD-002` reads the register's own 前置研究 column and reports the row when its value counts as pre-studied while the study date (`consultedAt`) is blank. Which values count is set by the rule's `conditionValues` (是, Y, yes, true, 已研究, √ by default). It checks that the date is filled, not whether the pre-study was substantive or whether its conclusion was adopted. When no row carries such a value, the rule reports itself in `skipped` instead of passing. |
| The study date is later than the meeting date — or cannot be read as a date at all. | `SD-003` compares the study date (`consultedAt`) with the meeting date (`meetingAt`) and reports a study date later than the meeting; the same day counts as not later. A date it cannot parse is reported as its own finding rather than skipped. It compares those two dates only — it does not judge whether the procedure was really carried out. |
| One row records no decision; another records a decision but no vote result. | `SD-004` requires the decision column (`decision`) on every row that carries it, and `SD-005` then requires the vote column (`voteResult`) only on rows where a decision is recorded. Neither checks whether the votes reached a required proportion: that proportion comes from your enterprise's implementing measures, and the rule does not compute it. |
| `SD-006` never reports anything on my register. | Its category vocabulary ships empty, so with no `values` configured `SD-006` reports itself in `skipped` rather than passing silently. Configure your own matter categories and it checks only that a filled category (`category`, 事项类别) is one of them; it does not decide whether the matter belongs to the “三重一大” scope. |
| The same 序号 appears on two rows. | `SD-008` reports the repeated `matterNo`, ignoring whitespace, because a repeat makes the matter impossible to point at in the minutes. Deliberating one matter at several meetings is normal: distinguish those rows by meeting number instead of reusing the sequence number. The rule checks uniqueness only. |

## Standards it follows

| Document | Number | Cited by rules |
|---|---|---|
| 《关于进一步推进国有企业贯彻落实"三重一大"决策制度的意见》 | 中办发〔2010〕17号（中共中央办公厅、国务院办公厅印发；⚠️ 党内文件，非法律、行政法规或部门规章；全文分三部分，按（一）至（二十三）编号，不设"第X条"） | SD-001, SD-002, SD-003, SD-004, SD-005, SD-006, SD-007, SD-008 |

**Boundary:** this plugin checks a **三重一大决策事项台账** for the procedural trail a register can be held to —
that each matter records its proposal and its basis, that a matter marked as pre-studied records a study date,
that the pre-study date is not later than the meeting date, that a decision and a vote record exist, that the
matter category comes from your vocabulary, that the register names the enterprise and the deciding body, and
that numbers are unique. It does **not** decide whether a decision was compliant, whether authority was
exceeded, whether an amount reaches the "large fund operation" threshold, or who is accountable.

> ### ⚠️ What this plugin deliberately does not know
>
> **What counts as a "三重一大" matter, and at what amount, is set by each enterprise's own implementing
> measures** — and the thresholds differ by industry, level and scale. So this plugin **hard-codes no amount
> threshold and no matter list.** Instead:
>
> - `SD-002` reads the register's **own 前置研究 column** to decide whether a matter needed pre-study, and the
>   values that count as "pre-studied" are configurable.
> - `SD-005` requires a vote record **only when a decision is recorded**, and it **does not check whether the
>   votes meet a required proportion** — that proportion comes from the implementing measures, and a register
>   rarely records the quorum and voting rule needed to compute it.
> - `SD-006`'s category vocabulary ships **empty**; with nothing configured it reports itself in `skipped`.
>
> **Every `excerpt` in the rule pack says, in so many words, that the clause text was not obtained.** The
> regime lives in 《关于进一步推进国有企业贯彻落实"三重一大"决策制度的意见》(中办发〔2010〕17号) and each
> enterprise's implementing measures. The verification pass could not retrieve verbatim clause text, so the
> pack states the gap in the `excerpt` field itself and keeps every rule at `warn` or `info`. **When the texts
> are in hand, replace each `excerpt` with the real clause and raise `kind` to `direct`.**
>
> A further limit worth stating: this checks that the **trail** exists. A study recorded on the right date does
> not prove the pre-study was substantive, and the plugin makes no finding about that.

## Compatibility

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a year of meetings use `ptc` |

## What it does

Registers the `soe_decision_check` tool. It reads one decision register — the enterprise header plus one row per
matter — applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `SD-001` | a matter records its proposal or its basis | warn | principle |
| `SD-002` | a pre-studied matter records the study date | warn | principle |
| `SD-003` | the pre-study date is not later than the meeting | warn | principle |
| `SD-004` | a decision is recorded | warn | principle |
| `SD-005` | a decided matter records the vote | warn | principle |
| `SD-006` | the category comes from your vocabulary (off by default) | info | principle |
| `SD-007` | the register names the enterprise and deciding body | warn | principle |
| `SD-008` | matter numbers are unique | warn | principle |
## Install

```sh
dsh plugin --profile <name> add dsh-soe-decision-check
dsh --profile <name> --dump-config | grep 'dsh-soe-decision-check'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/soe-decision-check.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `SD-002` `conditionValues` — the values in your 前置研究 column that mark a matter as pre-studied, by
  default `[是, Y, yes, true, 已研究, √]`.
- `SD-005` `conditionField` / `requiredFields` — what triggers the vote requirement; the decision column by
  default, requiring the vote column.
- `SD-006` `values` — your matter categories, e.g.
  `[重大决策, 重要人事任免, 重大项目安排, 大额度资金运作]`. Empty means no check.
- `SD-007` `fields` — the header fields that must be present; enterprise and deciding body by default. Add
  `meetingNo` if your register records the meeting number in the header.

## Material format

The tool accepts JSON or YAML:

```yaml
company: 某某集团有限公司
body: 党委会
meetingNo: 2026 年第 3 次
rows:
  - { 序号: '1', 决策事项: 某某技改项目立项, 事项类别: 重大项目安排,
      议题内容: 提请审议某某技改项目立项及投资概算,
      决策依据: 公司"三重一大"决策制度实施办法第 12 条, 涉及金额: 4800万元,
      前置研究: 是, 前置研究日期: 2026-02-20, 会议日期: 2026-03-05,
      决议结论: 同意立项，投资概算控制在 4800 万元以内,
      表决结果: 应到 9 人，实到 9 人，同意 9 票, 承办部门: 发展策划部 }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the register's own
column names are kept, so a finding names the column it read. Dates may be `2026-03-05` or
`2026-03-05 09:30`.

## Rule sources

Rule data lives in `rules/soe-decision-check.yaml`. The pack's header states the citation gap in full, and each
rule's `note` repeats the part that matters for that rule. The load-time guard that normally enforces "an
excerpt must be a real quotation of at least eight characters" cannot tell a quotation from a description —
so this pack leans on the header, the per-rule notes and a test that asserts every `excerpt` admits the gap.

## Troubleshooting

- **`SD-006` never runs.** Its vocabulary is empty. What counts as a "三重一大" matter is your implementing
  measures' business, and the plugin will not impose a list.
- **`SD-002` reports itself as skipped.** No row is marked as pre-studied. If your register uses different
  wording for that column, widen `conditionValues`.
- **`SD-003` fires on a pre-study I know happened.** The two dates disagree. Either the study date or the
  meeting date is wrong, or the row belongs to a later meeting.
- **`SD-005` fires although the vote passed easily.** It checks that a vote is *recorded*, not that it reached
  a proportion. Whether the proportion was met needs the quorum and the voting rule.
- **`SD-008` fires on one matter twice.** Deliberating the same matter at several meetings is normal;
  distinguish the rows by meeting number rather than reusing the sequence number.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-soe-decision-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-soe-decision-check   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and
the check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-soe-decision-check contributors.
