# Mermaid Templates — site hierarchy & link graph

Copy-paste `mermaid` diagrams for architecture Step 7 (Draw the Site Map) and linking-mode site maps in [SKILL.md](../SKILL.md). Paste any block into a Mermaid renderer. Swap the bracketed labels for real pages. Convention: one subgraph per nav zone; orphans in their own subgraph with no inbound edges; islands are clusters that link among themselves but never back to a pillar.

## 1. Hierarchy tree (L0 → L1 → L2/L3)

```mermaid
graph TD
  H[Home /] --> S1[Section /features]
  H --> S2[Section /use-cases]
  H --> S3[Blog /blog]
  S1 --> F1[Reporting /features/reporting]
  S1 --> F2[Automation /features/automation]
  S3 --> P1[Post /blog/subject-lines]
  S3 --> P2[Post /blog/segmentation]
```

## 2. Nav zones (header / footer / sidebar)

```mermaid
graph TD
  subgraph Header
    H[Home] --> Feat[Features]
    H --> Price[Pricing]
    H --> CTA[Start free]
  end
  subgraph Footer
    H --> About[About]
    H --> Docs[Docs]
    H --> Legal[Privacy]
  end
```

## 3. Hub/spoke topic cluster

```mermaid
graph TD
  P[Pillar: Email marketing] --> A[List building]
  P --> B[Subject lines]
  P --> C[Segmentation]
  A --> P
  B --> P
  C --> P
  A --- B
  style P fill:#9C27B0,color:#fff
```

Solid = hub↔spoke links; `---` = cross-links between spokes. Purple = the hub/pillar.

## 4. Orphan & island highlighting

Orphans have no inbound edge; islands cross-link internally but never to a pillar.

```mermaid
graph TD
  subgraph Pillars
    H[Home] --> P[Pillar: Email]
  end
  subgraph Cluster
    P --> A[List building]
    P --> B[Subject lines]
  end
  subgraph Island
    X[Glossary A] --- Y[Glossary B]
  end
  subgraph Orphans
    O[Old promo page]
  end
  style X fill:#f44336,color:#fff
  style Y fill:#f44336,color:#fff
  style O fill:#FFC107
```

Color key: **red** (#f44336) = island (reconnect to a pillar or retire); **yellow** (#FFC107) = orphan (add inbound links, noindex, or 301).

## 5. Before / after (linking mode)

```mermaid
graph TD
  subgraph Before
    Hb[Home] --> Bb[Pillar]
    SEGb[Segmentation]
    AUTb[Automation]
  end
  subgraph After
    Ha[Home] --> Ba[Pillar]
    Ba --> SEGa[Segmentation]
    Ba --> AUTa[Automation]
    SEGa --> Ba
    AUTa --> Ba
  end
```

Use `-.301.->` for a planned redirect edge (dotted): `OP[Old promo] -.301.-> B[Pillar]`.

## 6. Color-coding conventions

Apply `style` fills to make the diagnostic view readable at a glance.

```mermaid
graph TD
  H[Home] --> F[Features]
  H --> N[New section]
  H --> R[Deprecated page]
  H --> O[Orphan page]
  style H fill:#4CAF50,color:#fff
  style F fill:#4CAF50,color:#fff
  style N fill:#2196F3,color:#fff
  style R fill:#f44336,color:#fff
  style O fill:#FFC107
```

Key: **green** (#4CAF50) = existing, no change; **blue** (#2196F3) = new page to create; **red** (#f44336) = remove/redirect or island; **yellow** (#FFC107) = orphan/restructure; **purple** (#9C27B0) = hub or CTA.

## Rendering notes

- `graph TD` = top-down; use `graph LR` for wide, shallow sites.
- Keep node labels short (`page name /url`) so the diagram stays readable.
- One subgraph per nav zone keeps orphans and islands visually separate — the point of the map.
