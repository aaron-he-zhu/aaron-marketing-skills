# E-commerce Platform SEO Patterns

Referenced from [SKILL.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/technical-seo-checker/SKILL.md). Use alongside [bulk-audit-playbook.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/technical-seo-checker/references/bulk-audit-playbook.md) when the site runs on a recognizable e-commerce platform. Platform-specific defaults save 60-80% of the time vs. diagnosing from scratch.

---

## How to use this reference

1. Identify the platform from signals: HTML comments, JS bundles, cookies, URL patterns, or asking the user.
2. Jump to the relevant section.
3. Run the "Diagnostic signals" checks — these are platform-specific pitfalls.
4. Apply the "Fix locations" to resolve issues at the template level (not per-URL).

---

## Shopify

**How to identify**: `cdn.shopify.com` in assets, `Shopify.shop` in HTML, `/products/`, `/collections/`, `/cart` URL patterns.

### Diagnostic signals

| Symptom | Likely root cause |
|---------|-------------------|
| Products with variants not indexed | Canonical pointing to parent SKU; variant query strings (`?variant=12345`) dropped |
| Collection pagination loop | Default Shopify pagination has no `rel="prev/next"` in newer themes |
| Filter URLs indexed | Faceted collection URLs (`/collections/shoes?filter.p.vendor=Nike`) leaking |
| `?view=json` URLs indexed | Accidental indexing of Shopify JSON endpoints |
| Tag URLs cannibalizing categories | `/collections/<tag>` duplicates `/collections/<category>` |

### Fix locations

- `sections/product-template.liquid` — variant canonical logic
- `sections/collection-template.liquid` — pagination + filter canonical
- `layout/theme.liquid` — global canonical, robots meta
- `templates/page.liquid` — page-type overrides
- `robots.txt.liquid` — custom robots (Shopify exposes this on Shopify Plus)
- Shopify Admin → Online Store → Preferences → search engine listing defaults

### Red-flag Shopify defaults

- **Tag pages (`/collections/<tag>`)**: should `noindex` unless you have a content-led tag strategy
- **`/collections/vendors`, `/collections/types`**: `noindex`
- **`/cart`, `/checkout`, `/account`**: `noindex`
- **Variant query URLs**: canonical should point to base product URL (parent)

---

## WooCommerce (WordPress)

**How to identify**: `/wp-content/plugins/woocommerce/`, `/product-category/`, `/shop/` URL patterns, `woocommerce` class on body.

### Diagnostic signals

| Symptom | Likely root cause |
|---------|-------------------|
| Attribute filter URLs indexed | WooCommerce attribute archives (`/pa_color/red/`) |
| Tag + category cannibalization | Both `/product-tag/<slug>/` and `/product-category/<slug>/` ranking |
| Pagination indexed individually | `/shop/page/2/` etc. without canonical strategy |
| Product variations lost | Custom theme stripping variation meta |
| Duplicate meta across products | Default Yoast / Rank Math templates not customized |

### Fix locations

- `functions.php` or child theme — filter URL `noindex`
- `wp-config.php` — disable pagination indexing via `WP_DISABLE_FATAL_ERROR_HANDLER` area
- Yoast / Rank Math / All-in-One SEO plugin settings — per-post-type + taxonomy defaults
- `robots.txt` (via plugin or file) — wildcard `Disallow: /*add-to-cart=*`, `Disallow: /*?orderby=*`
- Theme `single-product.php` — canonical override for variable products

### Red-flag WooCommerce defaults

- **`?add-to-cart=<id>` URLs** appear in crawls — block in robots
- **`?orderby=`, `?min_price=`** — noindex or cloak from crawlers
- **Attribute archives** — `noindex,follow` by default; only expose if they have unique content
- **Product tags** — often duplicate category landing intent; default `noindex`

---

## Headless (Next.js / Remix / Astro / Gatsby) backed by CMS

**How to identify**: source maps pointing to `_next/`, `_astro/`, `_remix/`, or framework-specific class names. CMS backend may be Contentful / Sanity / Strapi / WordPress headless.

### Diagnostic signals

| Symptom | Likely root cause |
|---------|-------------------|
| Content not indexed | Client-side rendering only; no SSR / no prerender |
| Meta tags missing or generic | Rendered by JS after initial HTML delivery |
| Hreflang tags wrong | Static generation misses locale-per-URL rendering |
| Stale content served | Cached at edge; ISR / revalidation not firing |
| Canonical tags all point to `/` | Template using hardcoded canonical |
| Schema missing or malformed | JSON-LD generated client-side instead of server-side |

### Fix locations

- `app/(routes)/[slug]/page.tsx` or equivalent — ensure SSR or SSG, not CSR
- `next.config.js` → `experimental.serverActions` / `generateStaticParams`
- `getStaticProps` / `getServerSideProps` — return canonical, meta, schema in initial render
- `middleware.ts` — redirect rules, locale routing
- CMS query → ensure publish-ready content is fetched at build / request, not post-hydration
- Edge cache config (Vercel / Cloudflare / Netlify) — revalidation policy for product updates

### Red-flag Headless defaults

- **React hooks rendering meta tags** — search engines often miss these if not SSR'd
- **No `<link rel="canonical">`** in initial HTML — check `view-source:` not DevTools
- **`next/image` without width/height** — CLS issues on product listing pages
- **Cache-Control headers** — `public, max-age=31536000` on HTML is wrong (only for assets)

---

## BigCommerce

**How to identify**: `stencil-themes` in page source, `cdn11.bigcommerce.com` assets.

### Diagnostic signals

| Symptom | Likely root cause |
|---------|-------------------|
| Facet URL bloat | BigCommerce default exposes `?Facet=` URLs |
| Brand + category overlap | `/brands/<name>/` + `/categories/` duplicates |
| Product images 301 loop | Auto-generated image optimization paths |
| Stencil theme meta issues | Handlebars templates don't escape variant data |

### Fix locations

- Stencil theme `templates/components/products/*.html` — canonical per view
- `config.json` → `settings.urls.*` customization
- BigCommerce Control Panel → Storefront → SEO settings → Search Engine Options

---

## Magento 2 (Adobe Commerce)

**How to identify**: `/static/version*/frontend/` in assets, `Mage_Core` references.

### Diagnostic signals

| Symptom | Likely root cause |
|---------|-------------------|
| `.html` extension + non-`.html` duplicates | URL rewrite table conflicts |
| Layered nav facet URLs indexed | Default Magento layered navigation exposed |
| Session ID in URLs | Legacy Magento 1 setting still live post-migration |
| Multi-store content duplication | Different store views use same canonical base |

### Fix locations

- `app/design/frontend/<vendor>/<theme>/Magento_Catalog/templates/product/*.phtml`
- Admin → Stores → Configuration → Catalog → SEO
- `app/etc/config.php` — use `Magento_CatalogUrlRewrite` correctly
- `composer.json` — ensure Magento 2.4.5+ for built-in structured data

---

## Universal e-commerce checklist

Regardless of platform, verify:

- [ ] Product pages have `Product` schema with `offers.price`, `offers.priceCurrency`, `offers.availability`, and `review`/`aggregateRating` if reviews exist
- [ ] Collection / category pages have unique meta descriptions (not auto-generated "Shop our X selection")
- [ ] Faceted navigation has a clear rule: `noindex,follow` OR `Disallow` in robots.txt OR canonical to parent
- [ ] Pagination has `rel="next/prev"` OR consistent canonical OR self-canonical per page with clear content differentiation
- [ ] Out-of-stock products: 301 redirect to category, keep with "notify me" form, or 410 if permanently removed
- [ ] Product variations: one primary variant canonical, others `noindex` OR hash-based URLs (`#variant-red`)
- [ ] Structured data for `BreadcrumbList` on all category / product / blog pages
- [ ] International stores: `hreflang` alternates + self-referential; x-default for global fallback
