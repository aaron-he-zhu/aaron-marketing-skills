# Update Triggers & Cross-Skill Integration

## Update Triggers

### After Ranking Check
1. Update memory/hot-cache.md -> Hero Keywords table
2. Save snapshot to memory/monitoring/rank-history/YYYY-MM-DD-ranks.csv
3. Note significant movement keywords
4. Update "Last Metrics Update" date
5. If hero keyword moves +/-5 positions, create alert note

### After Competitor Analysis
1. Update memory/hot-cache.md -> Primary Competitors section
2. Save report to memory/research/competitors/YYYY-MM-DD-analysis.md
3. Update competitor overview notes
4. Note new strategies in hot cache

### After Audit (Technical/Content/Backlink)
1. Save report to memory/audits/[type]/YYYY-MM-DD-[audit-name].md
2. Extract top 3-5 action items -> hot cache Current Optimization Priorities
3. Update Key Metrics Snapshot if audit includes metrics
4. Create campaign entry if audit spawns new initiative

### After Monthly/Quarterly Report
1. Save report to memory/monitoring/reports/[period]/YYYY-MM-report.md
2. Update all metrics in hot cache Key Metrics Snapshot
3. Demote stale hot cache items
4. Update campaign statuses
5. Archive completed campaigns

### After Influencer Campaign Close
1. Save final analysis to memory/influencer/performance-analyzer/YYYY-MM-DD-[campaign].md
2. Update hot cache campaign status; promote renew/drop calls and winning formats
3. Closed-cycle creator facts (final rate, response history, new baselines) land in memory/creators/candidates.md; recommend creator-registry at 3+ pending updates per creator

### After Paid Readback / Attribution Pass
1. Save the snapshot or workbook to memory/paid-ads/[skill]/YYYY-MM-DD-[topic].md
2. Update hot cache Key Metrics (ROAS/CPA deltas, de-duped conversion counts)
3. Roll gated ad-account-auditor handoffs (ROAS blocks) and attribution-reconciler standing workbooks into the monthly memory/audits/YYYY-MM.md aggregate
4. Route lapsed offers and unresolved claim flags to offer-claims-registry via memory/claims/candidates.md

## Archive Management

### Monthly
1. Review hot cache for items not referenced in 30 days
2. Move stale items to cold storage
3. Create snapshot: memory/monitoring/snapshots/YYYY-MM-hot-cache-snapshot.md
4. Compress old rank-history exports
5. Update glossary with new terms

### Quarterly
1. Review entire cold storage structure
2. Compress files older than 6 months
3. Create quarterly summary report
4. Audit active campaigns -> archive completed ones

## Cross-Skill Memory Integration

| Skill | Memory Actions |
|-------|---------------|
| **keyword-research** | Add to memory/research/keywords/; promote high-value to hot cache; update glossary |
| **rank-tracker** | Update rank-history/; refresh hot cache Hero Keywords; flag significant movements |
| **competitor-analysis** | Update memory/research/competitors/; refresh hot cache Competitors; add new competitors if they outrank top 5 |
| **content-gap-analysis** | Store in memory/research/content-gaps/; promote opportunities to hot cache; update content calendar |
| **content-writer** | Log to memory/content/published/YYYY-MM-DD-[slug].md; track keyword + publish date; set 30-day performance check |
| **content-quality-auditor** | Save to memory/audits/content/; update hot cache Key Metrics; flag score < 60 in Active Campaigns |
| **domain-authority-auditor** | Save to memory/audits/domain/; update CITE Score in hot cache; note veto status; compare against previous |
| **influencer skills (IMPACT)** | Save dated outputs to memory/influencer/[skill]/; promote confirmed partners, agreed rates, campaign facts to hot cache; creator facts go to memory/creators/candidates.md |
| **content-reviewer** | Save gated ART verdict to memory/audits/influencer/; log dated compliance events as creator-registry candidates; flag T1/T2 vetoes in hot cache |
| **creator-registry** | Sole writer of memory/creators/[handle-slug].md; reconciles memory/creators/candidates.md; promotes expiring exclusivity windows + rate ceilings to hot cache |
| **paid skills (ROAS)** | Save dated outputs to memory/paid-ads/[skill]/; promote chosen structures/angles and readback deltas to hot cache; claim candidates go to memory/claims/candidates.md |
| **ad-account-auditor** | Save gated RQS verdict to memory/audits/paid/; promote verdict + vetoes to hot cache; rolled into the monthly memory/audits/YYYY-MM.md aggregate |
| **offer-claims-registry** | Sole writer of memory/claims/claims-ledger.md + offers.md; sweeps memory/claims/candidates.md; promotes live offers + none-on-file claims to hot cache |
