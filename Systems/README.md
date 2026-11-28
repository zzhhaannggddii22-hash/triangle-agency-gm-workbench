# 规则系统目录

本目录保存每套 TRPG 规则系统的独立知识环境。每个 system_id 有唯一规范入口。按下列登记表提供的精确路径加载。目录名与 ID 独立。

## 当前系统

- [Triangle Agency / 三角机构](./Triangle_Agency/README.md) — `system_id: triangle_agency`；当前正式实战规则版本为用户指定的中文 v22。
- [Cairn /《石冢》](./Cairn/README.md) — `system_id: cairn`；Cairn Second Edition；第二套系统接入准备中，当前为 candidate，尚未开放正式运行。
- [Blades in the Dark /《暗影之刃》（中文 SRD 译名：《暗夜冷锋》）](./Blades_in_the_Dark/README.md) — `system_id: blades_in_the_dark`；中文 SRD 修订号待核；独立研究中，当前为 candidate，尚未开放正式运行。

- [Daggerheart™ Compatible /《匕首心》](./Daggerheart/README.md) — `system_id: daggerheart`；默认规则集 Daggerheart Core Set；SRD 2.0 混合收录 Core 与 Hope & Fear，已分库并默认关闭扩展；当前为 candidate。
- [Worlds Without Number（WWN）](./Worlds_Without_Number/README.md) — `system_id: worlds_without_number`；英文核心规则与 SRD 1.0 作为研究基线；独立研究中，当前为 candidate，尚未开放正式运行。
- [Mothership / 母舰](./Mothership/README.md) — `system_id: mothership`；Mothership 1E；规则与模组运行准备中，当前为 candidate。

```yaml
systems:
  - system_id: triangle_agency
    system_entry: Systems/Triangle_Agency/README.md
    ruleset_versions: ["中文 v22"]
    status: active
  - system_id: cairn
    system_entry: Systems/Cairn/README.md
    ruleset_versions: ["Cairn Second Edition"]
    status: candidate
  - system_id: blades_in_the_dark
    system_entry: Systems/Blades_in_the_Dark/README.md
    ruleset_versions: ["Blades in the Dark SRD / 中文《暗夜冷锋》译本（修订号待核）"]
    status: candidate
  - system_id: daggerheart
    system_entry: Systems/Daggerheart/README.md
    ruleset_versions: ["Daggerheart Core Set", "Official SRD v2.0 (2026-08-25; mixed Core + Hope & Fear reference)"]
    default_expansion_scope: CORE_ONLY
    status: candidate
  - system_id: worlds_without_number
    system_entry: Systems/Worlds_Without_Number/README.md
    ruleset_versions: ["Worlds Without Number Core Rulebook", "SRD 1.0 (mechanics reference)"]
    status: candidate
  - system_id: mothership
    system_entry: Systems/Mothership/README.md
    ruleset_versions: ["Mothership 1E"]
    status: candidate
```

## 跨系统规则运行集成

- [System Rule Runtime Integration Protocol](./SYSTEM_RULE_RUNTIME_INTEGRATION_PROTOCOL.md)：跨系统共享的规则运行集成契约。它只规定系统规则如何按触发进入运行、如何连接资源与世界状态，不包含任何具体游戏机制。

## 接入约定

每个系统目录必须有 README，记录正式名称、system_id、规则版本、权威来源、状态、规则索引、专属 Skill 与适配边界。

系统之间完全隔离。研究或 Candidate 验证某系统不代表它已被正式 Campaign 采用；正式 Campaign 以 SYSTEM_BINDING 为准。Candidate 验证必须使用 TEST_ONLY_NON_CANON Validation Manifest，禁止继承/写入正式战役状态。不要仅凭仓库默认系统、用户过去玩过的系统或常见 TRPG 习惯推断当前系统。

通用 GM 能力统一维护在 `GM_Training/`。系统规则、术语、裁定和专属研究只维护在登记的对应系统目录，不复制到通用 Skill。

## Cairn 接入状态

Cairn 已建立独立系统入口、规则索引、专属 GM Skill、Preflight、规范化运行手册与测试夹具。状态继续保持 candidate。允许独立合成回归及用户明确授权的 TEST_ONLY_NON_CANON 短团验证；正式 Campaign 裁定仍须等官方来源核验、正反例与跨系统隔离测试、Preflight 和 1–2 次真实短团复盘后再评估。详见 [Cairn 接入研究](./Cairn/Research/INITIAL_RESEARCH.md)。
