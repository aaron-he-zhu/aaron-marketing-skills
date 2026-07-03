# Feed Title Patterns

Front-loaded product-title formulas by vertical, an attribute-priority checklist, GTIN/availability/disapproval hygiene rules, and one before/after title example. Used by step 4 (rewrite titles) and step 3 (attribute completeness) of [../SKILL.md](../SKILL.md). All numbers below are **Estimated** starter defaults — confirm each against the live feed and the destination landing page before shipping.

## Character limits (Estimated)

| Platform | Title field | Hard max | Front-load budget |
|---|---|---|---|
| Google Shopping / PMax | `title` | ~150 chars | first ~70 chars carry the match |
| Meta Commerce / Advantage+ Catalog | `title` | ~150 chars | first ~65 chars |
| Microsoft Shopping | `title` | ~150 chars | first ~70 chars |

Rule: the buyer decides in the visible prefix. Put brand + product type + top spec in the first ~70 chars; the tail is for secondary variants and long-tail terms. Never pad to the limit — a truthful 60-char title beats a stuffed 150.

## Title formula by vertical

Order = highest-intent attribute first. Drop any slot the item does not have; do not invent one.

| Vertical | Formula (front → back) | Example shape |
|---|---|---|
| Apparel / footwear | Brand + Product type + Key attribute + Color + Material + Size + Gender/Age | `Nike Air Zoom Pegasus 40 Running Shoe Black Mesh Men's US 10` |
| Electronics | Brand + Model + Product type + Key spec + Capacity/Size + Color | `Sony WH-1000XM5 Wireless Headphones Noise-Canceling Black` |
| Home / furniture | Brand + Product type + Key feature + Material + Dimensions + Color | `IKEA Kallax Shelf Unit 4-Cube Particleboard 30x30 White` |
| Health / beauty | Brand + Product type + Key attribute + Quantity/Volume + Skin/Hair type | `CeraVe Moisturizing Cream Fragrance-Free 19 oz Dry Skin` |
| Consumable / grocery | Brand + Product type + Flavor/Variant + Count + Size/Weight | `Nespresso Vertuo Coffee Pods Melozio 30-Count Medium Roast` |
| Auto / parts | Brand + Part type + Fitment (make/model/year) + Spec + OEM/MPN | `Bosch Brake Pads Front Ceramic Fits Honda Civic 2016-2021` |
| Generic default | Brand + Product type + Key attribute + Variant (color/size) | `<Brand> <Product type> <Key spec> <Variant>` |

Attribute-ordering rules:
- Brand first **only if** it drives demand; for unbranded/generic goods lead with product type.
- One key spec, not three — pick the attribute a buyer searches on (capacity, size, fitment).
- Match variant terms (color/size) to the actual `color`/`size` attributes; a title/attribute mismatch is a common disapproval.
- No promo text in the title: no `Free Shipping`, `Sale`, `Best`, `%`, ALL-CAPS words, or emoji. Promotions live in `promotion_id` / `sale_price`, not the title.

## Attribute-priority checklist

Required — a missing one limits or disapproves the item. Flag per item as `[needs source]`; never fabricate.

- [ ] `id` — stable, unique per item
- [ ] `title` — front-loaded per the vertical formula
- [ ] `description` — secondary detail; truthful to the landing page
- [ ] `link` — destination URL, resolves, matches the item
- [ ] `image_link` — resolves; meets the platform's image rules
- [ ] `availability` — reflects real stock (`in_stock` / `out_of_stock` / `preorder`)
- [ ] `price` — matches the landing-page price (see hygiene below)
- [ ] `brand` — real brand; required unless a recognized exemption
- [ ] `gtin` **or** `mpn` — GTIN where the product carries one; `mpn`+`brand` when it does not
- [ ] `condition` — `new` / `refurbished` / `used`
- [ ] `google_product_category` — mapped to the taxonomy, not guessed

Recommended — improves match and coverage (prospecting leans harder on these):

- [ ] `product_type` — your own taxonomy string; drives listing-group trees
- [ ] `product_highlight` — short benefit bullets
- [ ] `sale_price` + `sale_price_effective_date` — for live promos
- [ ] `color`, `size`, `material`, `pattern`
- [ ] `gender`, `age_group` — required for apparel; recommended elsewhere
- [ ] `item_group_id` — ties variants of one product together
- [ ] custom labels (`custom_label_0`–`4`) — for bid/budget segmentation

## GTIN / availability / disapproval hygiene

GTIN:
- Present where the product has a manufacturer GTIN; use `mpn` + `brand` only for genuinely GTIN-exempt items (custom, handmade, some bundles).
- Valid check digit and correct length (UPC-12, EAN-13, etc.); a bad check digit is a frequent disapproval cause.
- Unique per distinct product; one GTIN reused across unrelated items triggers limited serving.

Availability:
- `availability` must match real stock; an `in_stock` item that is sold out on the landing page is a mismatch disapproval.
- Use `preorder` / `backorder` with `availability_date` rather than mislabeling as in stock.

Price:
- Feed `price` must equal the landing-page price the buyer sees at that URL (currency and amount).
- On a mismatch, flag it against the landing-page truth — do **not** silently rewrite the feed price to match (per SKILL.md step 5).
- Put discounts in `sale_price`; keep `price` as the regular price.

Disapproval triage (item → cause → fix), highest-value work first:

| Common cause | Fix |
|---|---|
| Missing / invalid GTIN | Supply the real GTIN or set the correct exemption; fix the check digit |
| Price mismatch (feed vs landing page) | Reconcile to landing-page truth; flag, don't auto-overwrite |
| `availability` vs real stock | Set to actual stock state; add `availability_date` for preorder/backorder |
| Image issue (missing / placeholder / promo overlay / too small) | Point `image_link` at a clean product image meeting the platform's rules |
| Title/attribute mismatch (color/size in title ≠ attributes) | Align the title variant terms to the real `color`/`size` |
| Restricted / prohibited content (O2 risk) | Flag to [ad-account-auditor](../../../activate/ad-account-auditor/SKILL.md); do not ship |
| Unsubstantiated claim in title/description (O1 risk) | Flag; use registered wording from `memory/claims/claims-ledger.md` if it exists |
| Missing required attribute (`brand`, `condition`, category) | Mark `[needs source]` per item; do not fabricate |

A rewritten title on a disapproved item still does not serve — clear the disapproval before polishing the title.

## Before / after example (Estimated, illustrative)

Item: a men's running shoe, US size 10, black.

**Before** — generic, no front-loaded attributes, promo text, variant not in attributes:
```
title: SALE!! Best Running Shoes - Free Shipping - Great Deal
brand: (empty)
gtin: (empty)
color: (empty)
availability: in_stock   (landing page shows sold out)
price: 89.00             (landing page shows 79.00)
```
Problems: no brand/GTIN, promo text and ALL-CAPS in the title, variant terms absent from attributes, availability and price both mismatched (two disapproval causes).

**After** — front-loaded per the apparel formula, promo removed, attributes filled, hygiene reconciled:
```
title: Nike Air Zoom Pegasus 40 Running Shoe Black Mesh Men's US 10
brand: Nike
gtin: 0195869XXXXXX        [needs source — confirm real GTIN + check digit]
color: Black
size: US 10
availability: out_of_stock  (matched to landing page)
price: 79.00                (matched to landing-page price)
```
The GTIN stays flagged, not invented; price and availability are reconciled to the landing page, not silently overwritten.

## Related

- [../SKILL.md](../SKILL.md) — the product-feed-optimizer skill (steps 3–5 use this pack)
- [roas-benchmark.md](../../../../references/roas-benchmark.md) — the O (Offer) dimension this feed data feeds
- [ad-account-auditor](../../../activate/ad-account-auditor/SKILL.md) — runs the O1 (claim) / O2 (policy) vetoes
- [humanizer-slop.md](../../../../references/humanizer-slop.md) — de-slop pass over rewritten titles/descriptions
