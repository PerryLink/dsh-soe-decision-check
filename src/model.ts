/**
 * dsh-soe-decision-check — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'soe_decision_check'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  matterNo: ['序号', '议题序号', '编号', 'matterNo'],
  matter: ['决策事项', '议题', '事项', 'matter'],
  category: ['事项类别', '类别', '决策类型', 'category'],
  proposal: ['议题内容', '方案', '提请内容', 'proposal'],
  basis: ['决策依据', '政策依据', '依据', 'basis'],
  amount: ['涉及金额', '金额', '标的金额', 'amount'],
  consulted: ['前置研究', '是否经前置研究', '前置程序', 'consulted'],
  consultedAt: ['前置研究日期', '研究日期', 'consultedAt'],
  meetingAt: ['会议日期', '决策日期', '审议日期', 'meetingAt'],
  decision: ['决议结论', '决策结论', '决议', 'decision'],
  voteResult: ['表决结果', '表决情况', '票数', 'voteResult'],
  owner: ['承办部门', '责任部门', '承办人', 'owner'],
  note: ['备注', '说明', 'note', 'remark'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'matters', '事项'],
  columns: COLUMNS,
  header: {
  company: ['company', '企业名称', '单位名称'],
  body: ['body', '决策机构', '会议名称', '党委会'],
  meetingNo: ['meetingNo', '会议届次', '会议编号'],
  meetingAt: ['meetingAt', '会议日期'],
  checkedAt: ['checkedAt', '核对日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '决策事项',
  'matter',
  '议题内容',
  'proposal',
  '决议结论',
  'decision',
  '决策依据',
  'basis',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
