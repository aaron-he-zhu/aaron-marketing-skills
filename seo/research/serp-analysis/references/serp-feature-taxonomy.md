# SERP Feature Taxonomy

## Feature Categories

| Category | Features | Controlled By |
|----------|---------|--------------|
| **Knowledge** | Knowledge Panel, AI Overview, Featured Snippet | Content quality + structured data |
| **Engagement** | People Also Ask, Related Searches, Things to Know | Content relevance + question coverage |
| **Rich Results** | FAQ, How-To, Review Stars, Recipe, Event, Product | Schema markup + content format |
| **Media** | Image Pack, Video Carousel, Web Stories | Media optimization + hosting platform |
| **Commerce** | Shopping Results, Local Pack, Ads | Merchant feeds + Google Business Profile + ad spend |

---

## Feature Reference

### Featured Snippet (Position 0)

**Sub-types**: Paragraph (40-60 words, definitional queries) | Ordered List (how-to/process) | Unordered List (types/best/collections) | Table (comparison/data) | Video (visual how-to)

**Trigger**: Query has a direct-answer intent. Match existing snippet format, place answer immediately after H2/H3 heading, use proper HTML structure.

### People Also Ask (PAA)

**Trigger**: Almost all informational and commercial investigation queries.
**SEO value**: Each PAA question is a validated search query. Mine them for content ideas, answer within content using exact question as heading, keep answers 40-60 words.

### AI Overview

**Trigger**: Informational queries (highest rate), question-format, definitional. Lower for navigational/transactional.
**Formats**: Summary paragraph | Bulleted list | Step-by-step | Comparison | Table
**Citation drivers**: Clear citable sentences, front-loaded key information, structured data, topical authority, original data/statistics, comparison tables, recency.

### Knowledge Panel

**Trigger**: Brand/entity/person/place queries. Driven by Knowledge Graph presence, Wikipedia/Wikidata, consistent NAP, Organization schema.

### Image Pack

**Trigger**: Visual queries, product queries, design/inspiration. Use descriptive filenames, complete alt text, original images (not stock), WebP format, image sitemaps.

### Video Carousel

**Trigger**: How-to, tutorial, review queries. YouTube dominates. Optimize title, add chapters/timestamps, create transcripts, use VideoObject schema.

### Local Pack

**Trigger**: "[service] near me", "[service] in [location]", implicit local intent. Requires Google Business Profile, consistent local citations, reviews.

### Shopping Results

**Trigger**: Product purchase/comparison queries. Requires Google Merchant Center product feed, Product schema, accurate pricing.

### Sitelinks

**Trigger**: Brand/navigational queries for authoritative sites. Driven by clear site architecture, breadcrumb schema, strong internal linking.

### Rich Results (Schema-Dependent)

| Rich Result | Schema Required | Visual Impact |
|------------|----------------|--------------|
| FAQ | FAQPage | Expandable Q&A below listing |
| How-To | HowTo | Steps with optional images |
| Review Stars | AggregateRating | Star rating in snippet |
| Breadcrumb | BreadcrumbList | Path display replacing URL |
| Event | Event | Date, location, price |

### Related Searches / Things to Know

**SEO value**: Keyword discovery, content gap identification, topic cluster planning. Cover related topics to demonstrate comprehensiveness.

---

## Prioritization Matrix

| SERP Feature | Traffic Impact | Effort | Best For |
|-------------|---------------|--------|---------|
| Featured Snippet | Very High | Medium | Informational content |
| AI Overview citation | High (growing) | Medium-High | Authority/expertise sites |
| PAA | Medium-High | Low-Medium | FAQ-rich content |
| Video Carousel | High | High | Tutorial/how-to |
| Local Pack | Very High (local) | Medium | Local businesses |
| Rich Results (FAQ) | Medium | Low | Any content with Q&A |
| Rich Results (Review) | Medium-High | Low-Medium | Product/service reviews |
| Shopping Results | Very High (ecom) | Medium | Product sellers |
| Knowledge Panel | Medium (brand) | High | Established brands |

---

## SERP Feature Change Response

| Change | Action |
|--------|--------|
| Featured snippet lost | Check if snippet still exists for query; create better snippet-targeted content |
| AI Overview appeared | Optimize content for AI citation (structured, citable, authoritative) |
| AI Overview disappeared | Refocus on traditional SERP features |
| Video carousel appeared | Create video content for the keyword |
| Local Pack appeared | Consider local SEO if relevant |
| No features (blue links only) | Early-mover advantage for rich results |
| PAA but no snippet | Snippet opportunity not yet captured |

---

## AI Overview vs Traditional Strategy

- **Traditional SERP features** reward **format optimization** (structure content to match the feature)
- **AI Overviews** reward **authority and uniqueness** (be the source AI trusts for accurate, original information)
- Optimizing for both requires content that is structurally sound AND substantively authoritative
