# dsh-soe-decision-check — राज्य उद्यम के «三重一大» (तीन महत्वपूर्ण और एक बड़ा) निर्णय रजिस्टर की प्रक्रियात्मक रिकॉर्ड जाँच

`dsh-soe-decision-check` «三重一大» निर्णय रजिस्टर को पढ़ता है — उद्यम का हेडर और प्रत्येक विषय की एक पंक्ति — और उसी रजिस्टर की प्रक्रियात्मक रिकॉर्ड-शृंखला की जाँच करता है: क्या प्रत्येक विषय अपनी प्रस्ताव-सामग्री या निर्णय-आधार दर्ज करता है, क्या पूर्व-अध्ययन किया हुआ चिह्नित विषय अध्ययन की तिथि दर्ज करता है, क्या अध्ययन की तिथि बैठक की तिथि के बाद नहीं है, क्या निर्णय दर्ज है और निर्णीत विषय मतदान परिणाम दर्ज करता है, क्या विषय-श्रेणी आपके द्वारा कॉन्फ़िगर किए गए मानों में से है, क्या रजिस्टर उद्यम और निर्णय लेने वाला निकाय घोषित करता है, और क्या विषय-क्रमांक अद्वितीय हैं।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| किसी विषय में न प्रस्ताव-सामग्री भरी है न निर्णय-आधार। क्या कुछ बताया जाता है? | हाँ। `SD-001` उन दोनों में से कोई स्तंभ रखने वाली हर पंक्ति में कम से कम एक भरा होने की अपेक्षा करता है और दोनों खाली होने पर वह पंक्ति दर्ज करता है। यह केवल यह देखता है कि कम से कम एक भरा है, यह नहीं कि विषय «三重一大» के दायरे में है, और यह भी नहीं कि प्रक्रिया या अधिकार उपयुक्त थे। |
| रजिस्टर किसी विषय को पूर्व-अध्ययन किया हुआ बताता है, पर अध्ययन की तिथि खाली है। | `SD-002` रजिस्टर के अपने 前置研究 स्तंभ को पढ़ता है और तब वह पंक्ति दर्ज करता है जब उसका मान पूर्व-अध्ययन माना जाता हो और तिथि (`consultedAt`) खाली हो। कौन-से मान गिने जाएँ, यह नियम का `conditionValues` तय करता है (डिफ़ॉल्ट 是, Y, yes, true, 已研究, √)। यह देखता है कि तिथि भरी है, यह नहीं कि पूर्व-अध्ययन सारवान था या उसका निष्कर्ष अपनाया गया। ऐसा कोई मान किसी पंक्ति में न हो तो यह नियम चुपचाप पास होने के बजाय स्वयं को `skipped` में बताता है। |
| अध्ययन की तिथि बैठक की तिथि के बाद है, या तिथि के रूप में पढ़ी ही नहीं जा सकती। | `SD-003` अध्ययन की तिथि (`consultedAt`) की तुलना बैठक की तिथि (`meetingAt`) से करता है और अध्ययन की तिथि बाद की होने पर दर्ज करता है; एक ही दिन बाद का नहीं माना जाता। जो तिथि पढ़ी न जा सके, वह अलग से दर्ज होती है, चुपचाप छोड़ी नहीं जाती। यह केवल उन दो तिथियों की तुलना करता है, यह नहीं आँकता कि प्रक्रिया वास्तव में निभाई गई। |
| एक पंक्ति में निर्णय दर्ज नहीं है; दूसरी में निर्णय है पर मतदान परिणाम नहीं। | `SD-004` निर्णय स्तंभ (`decision`) को उन सभी पंक्तियों में अपेक्षित करता है जो वह स्तंभ रखती हैं, और `SD-005` तब मतदान स्तंभ (`voteResult`) केवल उन पंक्तियों में अपेक्षित करता है जहाँ निर्णय दर्ज है। इनमें से कोई यह नहीं जाँचता कि मत आवश्यक अनुपात तक पहुँचे; वह अनुपात आपके उद्यम के कार्यान्वयन नियमों में है और इस नियम में उसकी गणना नहीं होती। |
| मेरे रजिस्टर पर `SD-006` कभी कुछ नहीं बताता। | उसकी श्रेणी-सूची खाली मिलती है, इसलिए `values` कॉन्फ़िगर न होने पर `SD-006` चुपचाप पास होने के बजाय स्वयं को `skipped` में बताता है। अपनी विषय-श्रेणियाँ कॉन्फ़िगर करें तो यह केवल यह देखता है कि भरी हुई श्रेणी (`category`, 事项类别) सूची में है; यह नहीं तय करता कि विषय «三重一大» के दायरे में है। |
| एक ही 序号 दो पंक्तियों में आया है। | `SD-008` दोहराया गया `matterNo` दर्ज करता है (तुलना में रिक्त स्थान छोड़ दिए जाते हैं), क्योंकि दोहराव से कार्यवृत्त में विषय की सही पहचान नहीं हो पाती। एक ही विषय का कई बैठकों में विचार किया जाना सामान्य है: ऐसी पंक्तियों को क्रमांक दोहराने के बजाय बैठक क्रमांक से अलग दिखाएँ। यह नियम केवल अद्वितीयता देखता है। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
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

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-soe-decision-check
dsh --profile <name> --dump-config | grep 'dsh-soe-decision-check'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/soe-decision-check.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-soe-decision-check
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-soe-decision-check contributors.
