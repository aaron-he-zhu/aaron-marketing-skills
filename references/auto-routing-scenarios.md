<!-- Generated routing projection; do not edit directly. -->
# Auto Routing Scenario Index

Small runtime index for `/aaron-marketing:auto`. The full case corpus is split so a host can load only the routing evidence needed for the current goal. Read the [routing boundary contract](aaron-product-api-contract.md) first.

## Shard selection contract

1. Choose exactly one primary discipline shard from the table after lightweight goal triage.
2. Add [cross-discipline](auto-routing/cross-discipline.md) only when the goal crosses a discipline boundary or a listed word sense is unresolved.
3. Load at most **3 shards total**. A third shard is allowed only when the selected route has a concrete two-discipline handoff; never load every shard speculatively.
4. If the available object and outcome still do not identify a primary shard, ask one concise blocking question before loading case data.

## Primary shards

| Command discipline | Runtime shard | Cases |
|---|---|---:|
| `narrative` | [Narrative routing scenarios (TALE)](auto-routing/narrative.md) | 6 |
| `seo-geo` | [SEO/GEO](auto-routing/seo-geo.md) | 48 |
| `social` | [Social routing scenarios (ECHO)](auto-routing/social.md) | 7 |
| `email` | [Email routing scenarios (SEND)](auto-routing/email.md) | 6 |
| `ad` | [Paid routing scenarios (ROAS)](auto-routing/ad.md) | 6 |
| `influencer` | [Influencer](auto-routing/influencer.md) | 4 |
| `launch` | [Launch routing scenarios (RAMP)](auto-routing/launch.md) | 6 |

The cross-discipline shard contains 5 boundary cases and is never the sole primary shard.
