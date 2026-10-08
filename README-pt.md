# dsh-soe-decision-check — Registo de assuntos de decisão «三重一大» (três importantes e um grande) de uma empresa estatal e verificação do seu rasto procedimental

`dsh-soe-decision-check` lê um registo de assuntos de decisão «三重一大» —o cabeçalho da empresa mais uma linha por assunto— e verifica o rasto procedimental desse mesmo registo: se cada assunto regista a sua proposta ou o seu fundamento, se um assunto marcado como previamente estudado regista a data do estudo, se a data do estudo não é posterior à data da reunião, se está registada uma deliberação e se um assunto deliberado regista a votação, se a categoria do assunto vem da lista de valores que configurar, se o registo declara a empresa e o órgão decisor, e se os números de assunto não se repetem.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Um assunto não tem preenchidos nem a proposta nem o fundamento. Isso é reportado? | Sim. `SD-001` exige que cada linha que traga uma dessas duas colunas tenha pelo menos uma preenchida e reporta a linha quando ambas estão vazias. Verifica que exista pelo menos uma, não se o assunto pertence ao âmbito «三重一大», nem se o procedimento ou a competência foram adequados. |
| O registo marca um assunto como previamente estudado, mas a data do estudo está vazia. | `SD-002` lê a própria coluna 前置研究 do registo e reporta a linha quando o seu valor conta como previamente estudado e a data (`consultedAt`) está vazia. Que valores contam é fixado por `conditionValues` da regra (por defeito 是, Y, yes, true, 已研究, √). Verifica que a data está preenchida, não que o estudo prévio tenha sido substancial nem que a sua conclusão tenha sido adotada. Se nenhuma linha trouxer tal valor, a regra reporta-se a si mesma em `skipped` em vez de passar. |
| A data do estudo é posterior à da reunião, ou não é legível como data. | `SD-003` compara a data do estudo (`consultedAt`) com a da reunião (`meetingAt`) e reporta quando a primeira é posterior; o mesmo dia conta como não posterior. Uma data que não consegue analisar é reportada à parte, não é omitida em silêncio. Compara apenas as duas datas: não julga se o procedimento foi realmente cumprido. |
| Uma linha não regista deliberação; outra regista deliberação mas não votação. | `SD-004` exige a coluna da deliberação (`decision`) em cada linha que a traga, e `SD-005` exige depois a da votação (`voteResult`) apenas nas linhas com deliberação registada. Nenhuma verifica se os votos atingiram a proporção exigida: essa proporção consta das medidas de aplicação da sua empresa e a regra não a calcula. |
| O `SD-006` nunca reporta nada no meu registo. | O seu vocabulário de categorias vem vazio, por isso sem `values` configurado o `SD-006` reporta-se a si mesmo em `skipped` em vez de passar em silêncio. Configure as suas próprias categorias e ele verificará apenas que a categoria preenchida (`category`, 事项类别) consta da lista; não decide se o assunto pertence ao âmbito «三重一大». |
| O mesmo 序号 aparece em duas linhas. | `SD-008` reporta o `matterNo` repetido, ignorando espaços, porque a repetição impede apontar o assunto na ata. Que o mesmo assunto seja deliberado em várias reuniões é normal: distinga essas linhas pelo número da reunião em vez de reutilizar o número de ordem. A regra verifica apenas a unicidade. |

## Normas que segue

| Documento | Número | Regras que o citam |
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

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-soe-decision-check
dsh --profile <name> --dump-config | grep 'dsh-soe-decision-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/soe-decision-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-soe-decision-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-soe-decision-check contributors.
