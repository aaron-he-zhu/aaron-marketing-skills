# On-Page SEO Auditor - Compact Output Templates

Use one shape: evidence -> checks -> issues -> fix -> score. Keep only sections that match page type.

## Shared Conventions

| Item | Rule |
|------|------|
| Status | `✅` pass, `⚠️` partial risk, `❌` fail |
| Severity | `P0` blocks ranking/indexing, `P1` suppresses performance, `P2` hygiene |
| Evidence | Page state, crawl date, competitor set, inferred keyword |
| Scores | `/10` sections; final roll-up `/100` |

## Step Map

| Step | Focus | Must Capture |
|------|-------|--------------|
| 1 | Setup | URL, keyword, page type, goal |
| 2 | Title | length, keyword position, clickability |
| 3 | Meta description | length, CTA, intent match |
| 4 | Headers | single H1, hierarchy, keyword coverage |
| 5 | Content quality | depth, proof, freshness, readability |
| 6 | Keyword usage | placement, related terms, overuse |
| 7 | Internal links | count, anchor quality, gaps |
| 8 | Images | alt text, file names, size, format, lazy load |
| 9 | Technical on-page | URL, canonical, speed, mobile, schema |
| 10 | CORE-EEAT quick scan | 17 page-level checks |
| 11 | Summary | priorities, quick wins, checklist |

## Setup

Page URL, target keyword, secondary keywords, page type, business goal, competitor set.

## Title Tag

Current title, character count, length 50-60 chars, primary keyword, front-loaded wording, intent/clickability, recommended title, score.

## Meta Description

Current description, character count, length 150-160 chars, natural keyword, CTA, promise match, recommended description, score.

## Headers

Current H1/H2/H3 hierarchy, single H1, H1 keyword coverage, logical nesting, subtopic coverage, score.

## Content Quality

Word count, read time, depth vs competitors, unique proof, freshness, readability, E-E-A-T signals, intro answer, chunking, examples/stats, FAQ/conclusion/CTA, score.

## Keyword Usage

Primary keyword, density, title/meta/H1/first 100 words/H2-H3/URL/image alt status, related terms, missing terms, overuse risk, score.

## Internal Links

Total internal links, descriptive anchors, topical depth, broken/misdirected links, recommended additions, score.

## Images

| Image | Alt Text | File Name | Size/Format | Lazy Load | Status | Fix |
|-------|----------|-----------|-------------|-----------|--------|-----|
| [image] | [alt or missing] | [filename] | [KB/WebP/JPG] | [yes/no] | ✅/⚠️/❌ | [fix] |

| Image check | Status | Notes | Fix |
|-------------|--------|-------|-----|
| File names are descriptive | ✅/⚠️/❌ | [notes] | [fix] |
| Lazy loading enabled where appropriate | ✅/⚠️/❌ | [notes] | [fix] |

Score: [X]/10.

## Technical On-Page

URL/slug, canonical, mobile, page speed, HTTPS, schema markup, score.

## CORE-EEAT Quick Scan

| ID | Check | Status | Notes |
|----|-------|--------|-------|
| C01 | Intent alignment | ✅/⚠️/❌ | [notes] |
| C02 | Direct answer early | ✅/⚠️/❌ | [notes] |
| C09 | FAQ coverage | ✅/⚠️/❌ | [notes] |
| C10 | Semantic closure | ✅/⚠️/❌ | [notes] |
| O01 | Heading hierarchy | ✅/⚠️/❌ | [notes] |
| O02 | Summary/takeaways | ✅/⚠️/❌ | [notes] |
| O03 | Tables where needed | ✅/⚠️/❌ | [notes] |
| O05 | Schema markup | ✅/⚠️/❌ | [notes] |
| O06 | Section chunking | ✅/⚠️/❌ | [notes] |
| R01 | Data precision | ✅/⚠️/❌ | [notes] |
| R02 | Citation density | ✅/⚠️/❌ | [notes] |
| R06 | Timestamp freshness | ✅/⚠️/❌ | [notes] |
| R08 | Internal link graph | ✅/⚠️/❌ | [notes] |
| R10 | Content consistency | ✅/⚠️/❌ | [notes] |
| Exp01 | First-person experience | ✅/⚠️/❌ | [notes] |
| Ept01 | Author identity | ✅/⚠️/❌ | [notes] |
| T04 | Disclosure statements | ✅/⚠️/❌ | [notes] |

**Quick Score**: [X]/17 passing

## Step 11: Generate Audit Summary

| Area | Score | Top Issue | First Fix |
|------|:-----:|-----------|-----------|
| Title | [X]/10 | [issue] | [fix] |
| Meta | [X]/10 | [issue] | [fix] |
| Headers | [X]/10 | [issue] | [fix] |
| Content | [X]/10 | [issue] | [fix] |
| Keywords | [X]/10 | [issue] | [fix] |
| Links | [X]/10 | [issue] | [fix] |
| Images | [X]/10 | [issue] | [fix] |
| Technical | [X]/10 | [issue] | [fix] |
| CORE-EEAT quick scan (scaled) | [scaled score]/20 | [issue] | [fix] |

Scaling rule: `scaled score = round(passed_checks / 17 * 20)`. Finish with P0/P1/P2 issues, quick wins, competitor gap snapshot, and action checklist.
