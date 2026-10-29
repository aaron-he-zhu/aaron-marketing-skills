# AaronMarketing 优化方案 v3：以最少机制保持完整质量

日期：2026-10-27（Asia/Shanghai）。状态：用户已于2026-10-27批准全部分阶段实施；实施结果见[验收记录](optimization-v3-validation.md)。
本版完整替代v2。目标从“增加能力时顺便减负”改为：**先删除不必要的机制，再用已有能力完成MetaFlywheel闭环、Bench改进和可靠恢复。**

## 1. 简化的硬边界

项目收敛为三个原则：**每类事实只有一个权威来源；每次操作只有一条必要执行路径；展示状态随时可从事实重建。** 不要求所有事实放一个文件，也不把不同权限的模块塞成一个引擎。

必须保持：

- 120个技能的官网URL、slug、GitHub公开SKILL.md路径及独立安装/发现能力。
- 7个专业领域、8个审计入口、8套Bench的320个条目和37个profile的专业判断能力。已有ID、历史版本与审计证据继续可追溯。
- 权限、隐私、事实所有权、来源/hash、适用性、100%适用项覆盖、Unknown/N/A、veto、舍入、选定分支、nonce/receipt单次消费、并发与停止预算。
- Lite/Pro/Governed与宿主差异的实际边界；新项目默认Lite。安装内容和先前批准不自动授予本次外部执行权限。
- 独立检查器、人工冻结golden、专业反例及既有发布来源门禁。简化执行次数不减少验证命题。

本轮不新增生产服务、第三方依赖、数据库、记忆schema、自动经验匹配、重放引擎、顶层事件类型、生产模式或用户日常命令。可以增加少量替代重复逻辑的内部函数/作者工具；必须同时删除旧实现和重复编排，不能只加包壳。

## 2. 已核对的基线及真正的复杂度

| 维护面 | 当前实测/证据 | v3决定 |
|---|---|---|
| 核心 | `cac58547bc84ed2af865b68b90c5cfbb79b63978`，bundle20.1.0 | 保持stdlib运行时与现有公开入口 |
| 官网 | `fe778e70a48f9441066052786ef2045eae0be542`；120份vendor与核心一致 | 无现存版本漂移，不以修复虚构漂移立项 |
| 官网源快照 | 120文件、1,510,416字节 | 保留唯一离线内容输入，不为减少文件数同时删掉源与产物 |
| 官网中间投影 | skillBodies 1,138,693B；QuickStarts 79,833B | 删除合计1,218,526B已提交中间数据，构建直接读源 |
| compact研究载荷 | 121个capsule JSON、1,032,169B；certified_bindings为空 | 从正式发行与默认作者链退役，正式执行只保留explicit |
| Bench | 320项、37profile；80条criterion存在双份手维护 | 删除80条重复人工定义，保留完整编译投影 |
| 同次完整CI | discovery覆盖65模块；36个conformance suite又覆盖其中34个唯一模块；完整behavior在S2/S3中跑两次 | 按实际test ID/命令语义去重，独立oracle仍各执行一次 |
| 运行投影 | run每次写session.json；workflow每次写state.json，恢复再从events重算 | 取消强制写出与“先修复缓存才算有效”的流程 |
| 拟新增经验提示 | v2仍提分类器、匹配字段、Hook适配、独立测试 | 全部撤销；不计作已删除的现有源码 |

MetaFlywheel参考固定提交`4f59cf874dd979a95006f4ae8d7305159656ccce`。Pi Durable参考官方`earendil-works/pi/packages/durable`固定提交`6c384aa30f619d7b28963f2bab24d8dacbe73cb6`，包1.4.0，实验API。两者均只借鉴原则，不引入依赖。

前轮检查是既有基线：核心架构/生成文档检查通过；官网27项测试通过，Astro检查0错误。本次是只读审计及方案修订；这些结果不能当成v3实现验收。

## 3. MetaFlywheel只作为做事方法，零新增运行机制

沿用“发现 → 界定 → 最小解决 → 独立验收 → 必要时沉淀 → 相关时复用”，直接落在现有对象：

```text
用户任务 / 已有finding
→ 目标、约束、验收条件
→ 原skill / 已有workflow执行
→ 原validator或auditor核验
→ 有复用价值且获授权才更新decisions
→ 后续由现有context按任务读取
```

普通任务不要求填写六阶段记录；无需复用的结果不强制写经验。一次审计不默认跑八套Bench。已有任务、工件和引用足够时，不再创建总结、经验卡、曝光记录或额外复盘表。

项目只保留原`memory/decisions.md`及其现有批准/退役语义；WARM保留证据。不加`trigger/scope/advice`匹配字段，不加自动错误分类与召回Hook，不加检索索引、交付账本、采纳状态、经验Dashboard、off/shadow/hint模式或新评测runner。现有decisions增长仍受预算与记忆生命周期约束。

这会撤销v2的E及专用提示测试，消除一整条尚未证明收益的生产路径。以后只有真实使用证明既有上下文无法满足关键复用，才另行评估自动召回。

## 4. 核心运行时：减少状态、重复解析和实验分支

### 4.1 正式上下文只保留已能部署的explicit

当前三个host都默认explicit，certified_bindings为空；发布器还明确拒绝任何非空binding，因为可信签名认证链尚未实现。这比“默认没人用”提供了更明确的退役依据。

执行顺序：

1. 从正式Governed分发清单移除capsule树与compact专用认证schema。
2. 去掉生产assembly/profile/distribution中的balanced/lean选择、认证与回退分支。非explicit部署请求明确拒绝，不静默换成未经认证的表示。
3. 保留explicit实际依赖的host/module解析、来源校验与controller/model/tool分离；不能整份删除context-profile-resolver。
4. 先解除explicit blind-routing评测对capsule index的无条件绑定，迁移adapter、schema、来源验证及历史结果读取，保持真实provider smoke、金标隔离和显式评测可运行；再删除capsule树并结束每次技能修改必须生成120胶囊的要求。研究成果、来源与边界保留在简短结论及Git历史；专用研究命令明确退役，不伪装成仍可运行。
5. 删除仅服务该研究的默认CI/ablation/certificate维护；真实provider smoke、基础语义检查和独立发布验证继续保留。协议v3中与compact无关的blind routing/来源隔离能力按实际消费者保留。

直接收益：生产代码中为三种表示维护的选择/认证分支收敛为explicit一路；当前真正可部署的表示本来就只有explicit。正式包不再携带上述约1.03MB胶囊。仓库中删除胶囊/研究代码的最终数量以完整消费者迁移后的diff为准，不能把分发减重冒充全仓库减重。未来若重新研究compact，从固定历史提交启动，不在生产树常驻半套认证平台。

这是退役尚不能发布的研究能力，不是已经证明模型质量等价的内容压缩；不据此宣称模型token、成本或质量改善。

### 4.2 事件保留持久事实，取消强制落盘的运行缓存

run的session.json、workflow的state.json已是重放结果，正常控制路径从事件计算状态。当前每次append还必须写缓存，造成“事件已提交、缓存失败、调用报错、再执行repair”的额外故障窗口。

目标路径：

```text
当前：验证 → 提交事件 → 强制写派生文件 → 返回；缓存异常另走修复
目标：验证 → 提交事件 → 返回同次内存视图；需要文件时显式导出
```

- run普通append、幂等返回、loop-step恢复等所有隐含投影写点一并收敛，不能只改1655行而遗漏2057/2189等路径。
- workflow verify验证plan、run anchor、事件、证据、approval/nonce/receipt及重放状态；缓存缺失/过期不再否定真实事件。
- 原project/repair-projection入口在兼容期成为显式导出；旧plan的state_ref保留读取，不迁移历史plan、不重写历史事件。导出路径仍由已验证run/loop身份推导，检查旧字段与规范路径一致；不能按plan中的任意字符串写盘。
- 旧投影存在时不能变成权威输入；保留必要的安全路径拒绝。导出失败仅说明导出失败，不能反推事件未提交。
- 先核对内部、文档及分发消费者，移除依赖后再删强制写和相关错误路径。若发现真实外部文件消费，提供明确的兼容导出方式与发布说明，不能悄悄破坏。

**不删除**不可变plan/snapshot/savepoint/envelope、registry的规范事实、动作意图/回执、audit-loop的lease/fencing/step证据。它们不是同一种缓存。取消派生文件不需要新的通用commit-result层；保留已有事件身份、幂等与提交事实即可。

### 4.3 一次操作只解析与验证一次，保留跨边界重验

当前controller先调用planner验证，内部完成resolve后丢掉结果，随后再次resolve；resume也先load/project，再在resume_summary里重复load/project与savepoint核验。

改成：

- 候选request → 一次来源闭包验证与resolve → 使用同一已验证manifest。
- resume一次取得已验证events/head/state，summary、binding、savepoint结果由同一视图派生；并发时返回一致视图或明确重试。
- 内部传递已验证对象，不公开skip_validation参数；外部CLI、跨调用、写入或副作用前仍做各自必要验证。缓存不能跨调用延长信任。
- AUTHORITY_RANK只保留resolver原定义；作者生成器共用小型catalog读取接口，替代至少四处手写遍历。独立架构checker不共享生成oracle。

以同输入manifest等价、关键反例保留、目录扫描/文件读取次数减少验收，不承诺未经测量的性能百分比。

### 4.4 修正waiting，而不新增调度器

已用本地临时fixture复现：`waiting → hook_observed → active`。状态应由显式生命周期及既有合法推进事件决定；session-start、读取、resume和看板观察不自动唤醒。保留原来合法的context/turn推进，不强行规定只准turn_started。

恢复继续只读；结果未知保留未决。Pi的稳定key不等于外部exactly-once，本轮不自动重放模型、发送或推送。Resend跨调用需原稳定key及供应商窗口；无可靠幂等保证的mutation不自动重试。

## 5. Bench：一份公共实现，八个专业适配器

### 5.1 先减少作者规则来源与重复操作

| 内容 | 唯一作者归属 | 删除/派生 |
|---|---|---|
| 条目构念、criterion、边界与专业例子 | 各benchmark的明确item锚点 | 核对后删除catalog中80条重复criterion；禁止新补240条手写副本 |
| profile、权重、适用性、veto、公共数值政策 | framework-catalog + scorer | runbook/bench/skill需要展示的表由现有生成器投影，不再手抄 |
| 激活、报告头、Unknown/N/A、保存与降级流程 | auditor-runbook | 八auditor原SKILL中的公共段生成或引用；保留其领域触发/证据/例子/修复去向 |
| 评分与覆盖运算 | 现有rubric-score | 不再增加第二个评分器或领域总分 |
| 工件结构与归属 | 原schema/validator | 不另建Bench状态、证据数据库或修复映射registry |

八份auditor SKILL仍是完整公开入口。需要自包含的安装渠道继续获得生成内容，不能为节省正文而变成失效指针。共享的是实现与规则来源，专业判断、sink及权限仍独立。

保留已有8个standalone auditor-runtime：它们有实际安装消费者，root/standalone已通过XOR互斥，不能当作重复加载删除。公共规则生成可直接扩展现有auditor生成流程，不新建模板DSL、Bench编译服务或持久中间item库。编译接口遇到同ID多个权威锚点应失败，不继续first occurrence静默选取。

一次任务的相同来源只采集一次，用已有引用/hash/日期供多个item分别判断；同源多次引用不是多份独立证据。复审先处理变化及依赖，最终仍完整交原scorer计算，不能把局部检查冒充完整覆盖。

### 5.2 Bench本身：定义、锚点、诊断与校准

Bench既是六步的验收工具，也应作为被优化的对象。首轮围绕定义去重、锚点消歧、采证复用和诊断输出，复用现有catalog/scorer/runbook/golden及校准协议，不增加第九套bench或另一个评测平台。

**已确认的首批问题与修订要求：**

| 问题 | 实际证据 | 处理与验收 |
|---|---|---|
| N/A规则自相矛盾 | standalone生成器要求所有non-unknown状态附evidence；scorer又拒绝na携带evidence | 从生成器源修正为pass/partial/fail附证据，unknown附缺口原因，na须目录许可和reason；重生成八份runtime并做交叉负控 |
| Unknown被写成Fail | CORE-EEAT-A05的Fail锚点是Unknown | 区分未观察到认可证据与有充分观察支持认可不足；缺数据案例必须unknown，不能打0分 |
| 状态边界重叠/留空 | CORE-C03的1–2variants与single exact query重叠；R01没有明确恰好1个数据点；R02未说明密度/来源类型组合冲突如何裁决 | 明确计数对象、边界及组合判定顺序，建立事实→状态的独立反例；会改变历史案例分类时记录rubric revision |
| 详细规则与例子评不同东西 | CORE-O04一处按每500词列表密度，一处按并列信息组织判断 | 固定单一构念，避免凑列表数量；语义修改经版本化及边界回归，不靠改措辞掩盖含义变化 |
| cohort原则与表内固定阈值脱节 | CITE要求peer-relative，但C01详细段仍直接按500/50划状态 | 将默认示例、本次冻结cohort/日期/判据同位呈现；缺比较依据仍unknown，不将体量小直接判fail |
| 同一条目文字两处人工维护 | 80条catalog item_definitions与Markdown编译items并存，其他240条又采用另一形态 | Markdown保留criterion权威，catalog保留identity/profile/政策；逐条核对后去除80条重复criterion，旧可选字段读兼容按现有schema保留 |

定义归属只保留两类必要职责：人文benchmark拥有构念、条目锚点、边界例子；catalog/scorer拥有profile、权重、适用性、veto与计算政策。政策细化的item_policies.definition不能当重复文案顺手删除。Standalone仍保留完整编译定义，生成物的存在满足宿主需要，不代表需要第二个人工作者入口。

公共状态、舍入、coverage和veto说明集中维护。runbook保留操作/权限/工件要求，benchmark保留领域判断。确需重复展示的profile/veto/输入表由现有生成器投影，替换手抄；不再新建manifest。自然语言condition与机器可求值applicable_when分别标明，不能把自然语言解释包装成已机器验证的适用性。

**八套框架的具体优化重点：**

| Bench | 首轮优化内容 | 继续保留的边界 |
|---|---|---|
| CORE-EEAT | 先修A05/C03/R01/R02/O04；核对C/R维度名称与目录一致；复核FAQ/数据点/格式阈值的适用性 | 内容、作者/组织信誉各自归属；不能为高分堆数字、引用、FAQ或列表；条件项调整先有案例和版本 |
| CITE | peer cohort/市场/阶段与表内锚点一体展示，区分规模、可信度、可见性证据，最小补证批次 | 保留peer-relative现有原则；不按年龄或体量直接判不可信；未知私有控制台证据不作veto |
| STAR | 先给高分歧的创意/匹配项补证据和边界；核对披露相关项各检验什么命题，复用一份素材采证 | forecast/actual、creator/deliverable/return分开；不把关联条目未经分析直接合并 |
| ROAS | 强化R3增量/R4业务约束/R5边际、A5饱和/S4疲劳的判别例子；finding映射到既有修复技能 | RQS与平台ROAS比率分开，真实利润/增量证据不由归因自报替代 |
| SEND | 按program复用采证批次，补MPP/open、N/A与抑制/退订反例，明确D2各program真值来源 | 不把newsletter强套电商流程；opens代理不升级成真实转化或增量证据 |
| RAMP | 给P6反馈闭环等短锚点补最小证据和完成条件，明确每阶段复审依赖 | preflight/execution/outcome分开，计划不算结果，跨阶段不合总分 |
| ECHO | 给C3平台原生适配等项补可判例子；区分平台习惯、合规和质量；复用素材/许可/分母证据 | asset/program分开；UGC权限、反操纵与真实观测仍独立判断 |
| TALE | 给A9具体性等短锚点补正反例；明确canon→surface→实验结果的引用与修复顺序 | truth/system/effectiveness分开；一致性、真实与有效性不能互相替代 |

先处理确认冲突、全部veto的关键边界和10–20个实际高分歧条目，不一次为320项扩写成长篇。每个修订锚点只补必要的对象、最低证据、适用/排除条件、状态顺序、边界例子和下一步。是否合并、条件化或退役条目由重叠/可靠性证据决定，不为缩减数量而删控制；确需变更时保留旧ID/锚点映射和历史解析。

**让诊断可执行，同时减少采证与复审：**

- 继续用现有coverage、score_interval、gaps。NOT_SCORED也应输出已验证问题、最小补证批次、建议修复技能及完成条件；不降低100%适用项覆盖门槛。score_interval是数学上下界，不是概率置信区间，不取中点当暂定分数。
- 同一claims、页面、身份、许可或统计导出只采集一次，在现有WARM证据中留引用。不同条目分别判断自己的命题；三次引用同源材料不是三份独立佐证，不提高confidence或跨框架累计veto。
- 对source/canon/claims/平台政策/数据窗口变更，优先复核受影响条目，复用仍适用的未变证据，最终完整typed run仍交原scorer重算。新日期、context或版本产生新run；不修改历史证据日期或沿用旧总分。
- 闭环输出以qualified item ID连接finding→动作→证据→复审。复用现有Skill Ownership和工作流，不另手维护320条修复映射或建立新调度状态机。

**验收和发布分两类：**

1. 结构与一致性修复：320个qualified ID及37个profile的membership/政策可追溯；相同frozen run计算结果保持；删除重复定义后完整运行包仍含全部项。复用test_rubric_score、test_auditor_runtime、test_auditor_prompt_contracts、golden math及现有生成物检查，保留独立人工golden。
2. 锚点语义修订：记录旧事实→旧状态、新事实→新状态和理由；双盲评分先探索20–30个争议item-cases，检查分歧及严重pass/fail或veto分歧。Unknown/N/A适用性一致性单独统计；ICC只用于可比较且覆盖完整总分。小样本不能宣称八套框架已校准。

已有scoring-semantics§8就是正式可靠性/outcome校准协议，后续执行它，不再复制一套制度。修正明确矛盾不需要等待业务研究完成；但权重、veto、阈值或条目语义的实质修改都须版本化、回归并限定新结论。业务预测或ROI声明仍需独立真实数据校准，所有未校准结果继续advisory。

发布时由统一刷新入口同步catalog、相关benchmark/auditor文档、生成runtime/prompt contracts、source hash、machine contracts、版本和下游公开标准；正式退役的研究胶囊不再列为每次修改的必经链。不改120个技能URL。Bench减负单独报告：人工规则来源、重复criterion数、同任务采集次数、补证问答次数、评分分歧和复审工作量。未测量值写待测，不用条目数少或数学测试全绿冒充质量提高。


## 6. 官网：保留一份源快照，删除整个正文生成层

**推翻v2“删vendor、再保留skills.generated”的选择。** 当前更简单的目标是源快照直读：

```text
package.json：唯一repository + commit锁
                 ↓ 一次同步/独立比对
vendor：锁定的system-catalog.json + 原120份SKILL.md
                 ↓ Astro构建直接读取
catalog.ts薄适配 + 现有Markdown渲染器
                 ↓
原页面、原120个技能URL
```

- 从同一固定提交同步catalog与120份MD，package只维护repository/commit；版本、成员、数量、phase和路径从catalog派生。
- 以构建期loader/现有Markdown管线替代skillBodies.ts和skillQuickStarts.ts；删除Python正文生成器，不建立skills.generated和额外manifest。
- 保留catalog.ts兼容exports及精炼人工文案；override只决定表达，不决定成员。现112条purpose不强制用description覆盖，避免文案质量倒退。
- 保留普通离线dev/build。快照更新/CI完整来源比对需要固定checkout；不能同时声称删掉所有快照又保留无输入离线构建。
- package源锁是唯一新增的少量来源元数据，不是“零成本”。CI用独立固定checkout逐字比catalog和全部MD，不信任快照自报hash。
- Python→TS的摘录策略迁移是真实成本。保持12k字符策略、完整block截断、Quick Start/Instructions、GFM表格、代码围栏、相对链接、安全HTML策略、h1降级、可访问表格与截断提示。逐技能比较旧输出后才删旧链。
- source链接统一由锁定SHA与path计算；不能继续链接可变main。

其余可落地减法：

| 当前 | 收敛方式 | 验收 |
|---|---|---|
| 无消费者renderer/别名、WHY/ALL_ROUTES等 | 删除，不保留空兼容壳 | 无dangling import；Astro实际路由不变 |
| marketingPeers按Sep7/8/9/10/11分批函数及页面日期分支 | 每个既有peer集中维护compare/review发布属性、demand与显式link scope；少量普通查询 | 全部URL、每页链接集合/顺序、日期和需求来源一致；已发布不等于全站都可链接 |
| 三份matrix页的共同模板 | 一个普通组件，保留SEO/GEO与Email专业数据和特殊段落 | DOM/SEO/FAQ/CTA与analytics、链接集合等价；不建通用PSEO DSL |

既有engineering文档是内部设计事实；无runtime import不等于可删。已归档ops材料不反复同步，不将删历史资料或压缩文件算作运行架构简化。Gateway/Worker未实现的状态继续准确表述。

## 7. 作者与CI：少一次操作，而不只是少一份代码

### 7.1 作者只改权威输入，不记十个生成器顺序

已有10个tracking surfaces中大量内容已经生成，不能把它们误报成十处全手写。本轮删除CONTRIBUTING中要求手改generated skills.sh.json等矛盾指令，明确输入、派生面与独立检查。

普通技能、框架或目录修改统一使用一个薄的刷新入口，固定列出既有生成器依赖顺序；默认不提升版本、不访问网络、不发布。发布继续调用已有bump-release事务，再走同一刷新链。实现可复用已有作者脚本；若必须增加一个入口，必须同时移除分散的手写编排，不增加任务DSL、通用DAG或状态库。

保留各生成器独立--check。历史changelog、schema版本、旧release支持记录依其语义维护，不做全库字符串替换。第二次刷新零diff；故意省略一个已知生成依赖，验证独立检查能发现，不能让刷新入口和检查共用一份漏项清单。退役compact后不再维护其默认生成顺序。

### 7.2 同一不可变输入的同一检查只执行一次

S2/S3当前完整run-behavior在209/263重复；architecture、生成检查也重复；discovery之后manifest再运行34个已覆盖Python模块，Hook shell在同路径最多重复四次。

处理：

1. 先删除同job、同参数/环境、同一checkout的确定重复调用。
2. 全量路径采用“一次unittest discovery + 一次非discovery conformance”。保留现有runner及单suite使用能力；仅对能证明test ID等价的标准调用去重。
3. shell runtime、golden、负控、架构与生成漂移等不同验证命题各执行一次。特殊参数、执行环境或自定义main不凭文件名去重。
4. PR、nightly、release各自独立执行，不跨运行复用“之前通过”。
5. 优先复用现有deterministic-suites清单，避免再维护一份CI清单。只在确实减少维护处时抽小公共阶段；不把八workflow合成大workflow。

test ID/命令覆盖等价针对保留的功能范围。PoC/compact专属测试的退役，以及waiting/缓存语义修正所替换的测试，单列删除理由、有意差异和仍保留的通用反例；不能把退役专用测试混入CI去重收益。

工程成熟度checker目前检查YAML字符串。抽取调用时必须检查真实可达执行关系；不得用注释保留命令名来假装已执行。实现解析成本若超过删减收益，先只去重复调用，保留清晰YAML。发布权限、可信来源、线上标准检查及owner门禁不下放到通用工具。

## 8. Pi研究退役与可靠恢复的最小测试

旧`evals/pi-agent-poc/`是0.80.10内存session研究，结论production NO-GO；不是本次Pi Durable，也没有生产消费者。v3默认结束它的持续维护：保留简短固定来源/结论于现有eval说明，删除9个PoC文件和专用workflow，同步移除仅服务该目录的checker例外；通用依赖隔离/Markdown扫描反例继续保留。若确认仍有独立研究消费者，将其固定归档而不计入当前持续CI。

实施前核对GitHub required status是否引用专用job；有绑定时先完成对应迁移，不能只凭源码搜索认定无消费者。本地若残留ignored node_modules，先移出退役目录，再移除扫描例外。

Pi借鉴集中在已有事件语义、只读恢复与外部副作用边界，不移植Harness、SQLite/JSONL后端、scheduler或工具replay。它的deferred进度可丢窗口、单storage owner没有跨进程锁，不能拿其文档证明本项目任意故障无损或exactly-once。

复用现有unittest/mock/TemporaryDirectory补以下缺口，不另建runner：

| 场景 | 必须保留的结果 |
|---|---|
| 工件写完、事件未提交 | 孤立文件不算成功 |
| 事件fsync、响应丢失 | 同key返回原事件；换payload拒绝；不重做外部动作 |
| 取消强制投影写 | 删除/篡改旧缓存不改变事件结论；真正事件/证据损坏仍失败 |
| 显式导出失败 | 单独报告导出失败，原事件与业务状态不回滚 |
| tool_requested无结果/外部成功而receipt未知 | 保持未决；resume不调模型、不重发，不伪造receipt |
| waiting后session-start/查看 | 保持waiting，合法显式推进才改变 |
| resume期间并发append | summary/head/binding来自同一验证视图或明确重试 |
| nonce/receipt复用、兄弟分支证据、过期lease、预算耗尽 | 原拒绝/停止条件仍成立 |
| Bench恢复/复审 | 原版本和同证据可重算；换时间/口径/证据生成新run |

状态故障使用test_run_events、test_runtime_controller、test_workflow_loop、test_audit_loop；动作边界用test_connectors_local。测试可以增加，但不写仅镜像函数的测试，也不因为删研究功能而删基础安全反例。

## 9. 四批实施，每批替换后立即删旧路径

批次是评审边界，不要求四个大PR。代码所有权和风险不同可拆小提交，不以PR数减少充当架构简化。

| 批次 | 具体交付 | 同批必须删除 | 放行证据 |
|---|---|---|---|
| A：直接减负 | CI确定重复去重；作者输入指令修正；官网死入口清理；旧Pi PoC退役 | 同job重复调用、误导手改步骤、无消费者兼容壳、PoC专用持续维护 | test ID/独立命令覆盖不减、通用隔离反例保留、正常构建 |
| B：正式运行主路径收敛 | explicit-only；一次resolve/read view；取消强制投影写；修正waiting | capsule默认生成/分发、compact生产分支、二次resolve、派生缓存故障/强制修复流程 | 原explicit输出与全部安全边界；恢复故障矩阵；旧plan与显式导出兼容 |
| C：来源与呈现收敛 | 官网源快照直读；catalog共享作者接口/固定ceilings派生；统一刷新入口；peer/matrix局部归并 | skillBodies、QuickStarts、正文Python生成链、重复遍历/常量、历史分批判断/重复模板 | 120URL与来源逐项一致；输出/SEO/导航等价；离线构建；二次刷新零diff |
| D：Bench质量与维护面收敛 | 公共流程/规则生成；80定义去重；确认矛盾和少量高分歧锚点修订；补证/复审减负 | 八份共同手写流程、重复政策表/criterion、已被替代解释 | 320项/37profile完整；冻结run等价；语义修订版本化与独立事实→状态反例 |

A先做；B可与C/D并行，C/D公共生成文件应划清所有权。每批完成即删除原路径，不长期双轨。原13.5–25人日估算覆盖了已撤销功能，也未覆盖本轮更深退役，现撤销；按A的实际变更与B/C消费者清单重新估算，不用更小数字装作已更简单。

### 9.1 兼容与回滚必须随替换一并验证

实施前固定该批源码提交、可用发行包和输入基线，使用现有Git与发布工件记录，不增加回滚数据库。结构替换通过独立验收后删除旧路径；只有需要撤销时才恢复对应固定版本，不长期维护两套生产实现。

| 改动 | 兼容验收与回滚单位 |
|---|---|
| 运行缓存、单次解析与waiting | 固定时钟/ID比较事件字节、内存状态、nonce/receipt消费、分支和终态；导出文件差异及waiting纠错单列。回滚前暂停相关写入并固定head，在同一隔离快照验证原版本对期间事件/plan/工件的verify、只读resume及同key幂等重试；旧版需要投影时先用匹配版本显式导出。不能安全接管则停止推进并只读保全证据，不降级猜测、不重发外部动作、不重写历史。不可回滚到已知会破坏权限或状态正确性的版本 |
| compact退役 | explicit正文、host/权限结论与blind-routing金标隔离保持；来源元数据差异单列。恢复时以代码、schema、胶囊、分发清单为同一版本单位，默认仍explicit，不把回滚当作认证或启用compact的依据 |
| 官网快照直读及模板归并 | 比较完整120个(slug,公开路径,路由)集合，逐技能内容/链接及离线构建；独立安装包和standalone降级另验，不能只检查120这个总数。回滚源码锁、catalog/MD快照、loader/renderer及页面适配为一致版本，不混用新快照与旧摘录规则 |
| Bench定义去重与锚点修订 | 比较320个qualified ID、37个profile的完整成员与政策，冻结run结果等价；专业锚点变化有意版本化。回滚catalog、benchmark、生成runtime/contracts及版本为一致单位；旧审计仍绑定原版本，新口径重审生成新run，不覆盖历史分数或判决 |
| 作者与CI去重 | 对保留功能比较展开后的test ID、参数、环境和独立验证命题；缺一项即恢复对应调用后再评审。required status迁移与workflow退役协调验证；不擅自降低外部门禁或改权限 |

任何失败都先保留已提交事实和证据。代码回滚不撤销外部已经发生的效果，回滚方案也不授予新的发送、发布、部署或外部配置权限。

## 10. 验收账本：质量不退、机制和操作确实减少

不设无法证明的“删30%代码”目标。每批报告实际前后值和证据，以下不同维度不互相抵消：

| 指标 | v3验收目标 |
|---|---|
| 生产运行新机制 | 0个新服务/依赖/事件类型/持久库/自动经验路径 |
| 正式prompt表示 | 3种声明及实验分支 → 1种explicit；权限与host能力照常核验 |
| 默认胶囊维护与载荷 | 不再每次改skill生成120份；正式包移除121份JSON的现有树 |
| 非权威运行缓存 | 两类默认强制写 → 0；只保留必要显式导出；不涉及registry真值或lease证据 |
| 单次resolve/resume | 去掉重复完整解析与多head混读；关键来源跨边界仍重验 |
| 官网正文链 | 原MD→QuickStarts路径副本→Python→TS正文→renderer，收敛为锁定原MD/catalog→构建renderer |
| Bench人工criterion副本 | 80条 → 0；320个专业项与37profile完整可用 |
| 同次CI重复 | 完全相同检查不重复；实际test ID与独立oracle覆盖等价；耗时另测 |
| 作者操作 | 编辑各权威输入→一次刷新→独立检查；不手改生成面、不记依赖顺序 |
| 对用户的操作 | 原命令与URL可用；六步不变六张表；不增加profile/经验系统配置 |

结构去重必须在冻结输入下证明行为/输出等价；错误修正与锚点变更列出有意差异及版本，不能混成“全部零diff”。来源hash、分发清单和声明元数据随改版的预期变化单列，模型实际explicit正文、权限结论和业务判定分别比较。新版本保留必要的旧合同读取；必须按旧源码重验时使用对应固定版本运行包，不重写历史hash，也不承诺新runtime能重验所有已退役的旧来源。无法证明质量等价的删减不进入默认实施：保留最小必要旧机制并说明原因，不通过删反例、减证据、弱化阈值让检查变绿。

测试通过只支持受测性质。Bench可靠性/业务有效性、模型上下文压缩质量与真实ROI不因源码更少自动成立；当前尚未验证的收益继续准确标注。

### 10.1 本轮方案最终验收记录

2026-10-27复核两仓库HEAD与本方案基线一致，跟踪文件无改动；实际交付仅为本计划文件，所在docs/plans目录按现有规则被Git忽略，尚未提交或发布。核心架构、生成system文档、8份standalone auditor runtime的只读检查通过；独立临时脚本确认核心/plugin/官网目录与正文/QuickStarts的120个成员及路径一致、120份vendor字节一致，Bench实测320项/37profile/80条重复定义，coverage与veto数值未改。

这些是现状和方案依据核验，不是v3实现、线上URL可访问性、所有宿主安装或业务效果验证。实施阶段仍须完成上述完整路径集合、离线构建、独立安装、故障与回滚验收。方案交付无阻塞；required status等外部消费者、真实业务校准属于实施前核对或后续验证。以上为实施授权前的验收状态。用户随后明确批准“分阶段全部实施”，覆盖本地代码修改与测试；本地验收完成后又批准“推送pr，但是不合并。”，覆盖提交、推送和草稿PR。合并、部署及外部权限变更仍不在范围内。

## 11. 关键依据与参考

- [作者与生成面的现行边界](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/CONTRIBUTING.md#L140)
- [当前重复CI调用](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/.github/workflows/validate-skill.yml#L196)
- [已存在的conformance命令清单](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/evals/deterministic-suites.json)
- [compact部署绑定为空](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/references/prompt-profiles.json#L25)
- [发布器拒绝非空认证绑定](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/scripts/build-distribution.py#L1333)
- [现有生产context链](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/scripts/runtime-controller.py#L344)
- [planner内部resolve](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/scripts/context-plan.py#L1001)
- [resume重复读取](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/scripts/runtime-controller.py#L669)
- [强制session投影写入](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/scripts/run-events.py#L1655)
- [强制workflow投影写入](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/scripts/workflow_loop.py#L2239)
- [workflow将缓存过期当失败](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/scripts/workflow_loop.py#L2389)
- [waiting当前投影逻辑](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/scripts/run-events.py#L735)
- [公共审计runbook](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/references/auditor-runbook.md#L1)
- [N/A生成器矛盾](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/scripts/generate-auditor-runtime.py#L231)
- [N/A实际评分合同](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/scripts/rubric-score.py#L624)
- [CORE-A05 Unknown/Fail冲突](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/references/core-eeat-benchmark.md#L603)
- [CITE默认阈值与cohort](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/references/cite-domain-rating.md#L231)
- [现有校准协议](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/references/scoring-semantics.md#L101)
- [官网反向生成输入](https://github.com/aaron-he-zhu/aaronmarketing-site/blob/fe778e70a48f9441066052786ef2045eae0be542/scripts/generate-skill-bodies.py#L238)
- [现有Markdown渲染器](https://github.com/aaron-he-zhu/aaronmarketing-site/blob/fe778e70a48f9441066052786ef2045eae0be542/src/lib/renderSkillMd.ts#L1)
- [官网详情页正文消费者](https://github.com/aaron-he-zhu/aaronmarketing-site/blob/fe778e70a48f9441066052786ef2045eae0be542/src/pages/skills/s/[slug].astro#L5)
- [peer现有导航范围](https://github.com/aaron-he-zhu/aaronmarketing-site/blob/fe778e70a48f9441066052786ef2045eae0be542/src/data/marketingPeers.ts#L326)
- [旧Pi PoC的NO-GO结论](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/cac58547bc84ed2af865b68b90c5cfbb79b63978/evals/pi-agent-poc/README.md#L7)
- [MetaFlywheel固定参考](https://github.com/NBagent-dev/metaflywheel/tree/4f59cf874dd979a95006f4ae8d7305159656ccce)
- [Pi Durable官方实验边界](https://github.com/earendil-works/pi/blob/6c384aa30f619d7b28963f2bab24d8dacbe73cb6/packages/durable/README.md#L1)
- [Pi意图提交及双重replay-safe要求](https://github.com/earendil-works/pi/blob/6c384aa30f619d7b28963f2bab24d8dacbe73cb6/packages/durable/src/harness/tool.ts#L169)
- [Pi稳定key与exactly-once边界](https://github.com/earendil-works/pi/blob/6c384aa30f619d7b28963f2bab24d8dacbe73cb6/packages/durable/src/harness/types.ts#L275)
- [Pi deferred progress边界](https://github.com/earendil-works/pi/blob/6c384aa30f619d7b28963f2bab24d8dacbe73cb6/packages/durable/README.md#L497)
