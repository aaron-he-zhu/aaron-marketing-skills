# E-commerce Platform SEO Patterns

Identify the platform, jump to its section, run diagnostic checks, apply fixes at template level.

## Shopify

**Identify**: `cdn.shopify.com`, `/products/`, `/collections/`, `/cart` URLs.

| Symptom | Root Cause |
|---------|-----------|
| Variants not indexed | Canonical points to parent; `?variant=` dropped |
| Collection pagination loop | No `rel="prev/next"` in newer themes |
| Filter URLs indexed | Faceted URLs (`?filter.p.vendor=`) leaking |
| Tag URLs cannibalizing | `/collections/<tag>` duplicates category |

**Fix locations**: `sections/product-template.liquid`, `sections/collection-template.liquid`, `layout/theme.liquid`, `robots.txt.liquid` (Plus only).

**Noindex**: Tag pages, `/collections/vendors`, `/collections/types`, `/cart`, `/checkout`, `/account`. Variant URLs should canonical to parent.

## WooCommerce

**Identify**: `/wp-content/plugins/woocommerce/`, `/product-category/`, `woocommerce` body class.

| Symptom | Root Cause |
|---------|-----------|
| Attribute filter URLs indexed | WooCommerce attribute archives (`/pa_color/red/`) |
| Tag + category cannibalization | Both taxonomies ranking for same terms |
| Pagination indexed individually | `/shop/page/2/` without canonical strategy |
| Duplicate meta across products | Default SEO plugin templates not customized |

**Fix locations**: `functions.php` / child theme, Yoast/Rank Math plugin settings, `robots.txt`, `single-product.php`.

**Block/noindex**: `?add-to-cart=`, `?orderby=`, `?min_price=`, attribute archives, product tags.

## Headless (Next.js / Remix / Astro / Gatsby)

**Identify**: `_next/`, `_astro/`, `_remix/` in source. CMS: Contentful / Sanity / Strapi / WP headless.

| Symptom | Root Cause |
|---------|-----------|
| Content not indexed | Client-side rendering only, no SSR/prerender |
| Meta tags missing/generic | Rendered by JS after initial HTML |
| Canonical tags all point to `/` | Hardcoded canonical in template |
| Schema missing/malformed | JSON-LD generated client-side |

**Key fixes**: Ensure SSR/SSG (not CSR). Return canonical, meta, schema in initial HTML render. Check `view-source:` not DevTools. Set proper Cache-Control (no `max-age=31536000` on HTML). Fix `next/image` width/height for CLS.

## BigCommerce

**Identify**: `stencil-themes` in source, `cdn11.bigcommerce.com`.

| Symptom | Root Cause |
|---------|-----------|
| Facet URL bloat | Default `?Facet=` URLs exposed |
| Brand + category overlap | `/brands/` duplicates `/categories/` |
| Stencil theme meta issues | Handlebars templates don't escape variant data |

**Fix locations**: Stencil `templates/components/products/*.html`, `config.json`, Control Panel SEO settings.

## Magento 2

**Identify**: `/static/version*/frontend/` in assets, `Mage_Core`.

| Symptom | Root Cause |
|---------|-----------|
| `.html` + non-`.html` duplicates | URL rewrite table conflicts |
| Layered nav URLs indexed | Default layered navigation exposed |
| Session ID in URLs | Legacy Magento 1 setting post-migration |
| Multi-store duplication | Store views share canonical base |

**Fix locations**: Admin > Stores > Configuration > Catalog > SEO, `Magento_CatalogUrlRewrite`, theme templates.

## Universal Checklist

- [ ] Product pages: `Product` schema with `offers.price`, `availability`, `aggregateRating`
- [ ] Category pages: unique meta descriptions (not auto-generated)
- [ ] Faceted nav: `noindex,follow` OR `Disallow` OR canonical to parent
- [ ] Pagination: `rel="next/prev"` OR self-canonical with content differentiation
- [ ] Out-of-stock: 301 to category, "notify me" form, or 410 if permanent
- [ ] Variations: one canonical, others `noindex` or hash-based
- [ ] `BreadcrumbList` schema on all category/product/blog pages
- [ ] International: `hreflang` + self-referential + x-default
