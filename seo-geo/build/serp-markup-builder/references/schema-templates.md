# Schema.org JSON-LD Templates

Compact starter blocks. Replace placeholders, remove unused fields, and validate before ship.

## Shared Rules

- Match visible page content exactly; omit fields that are not visible or verified.
- Use absolute canonical URLs.
- Use ISO 8601 for dates and durations.
- Remove placeholders before publishing.
- Only emit `aggregateRating` or `review` when visible, verifiable user reviews support the exact values.

## FAQPage

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Question text 1]",
      "acceptedAnswer": { "@type": "Answer", "text": "[Answer text 1]" }
    },
    {
      "@type": "Question",
      "name": "[Question text 2]",
      "acceptedAnswer": { "@type": "Answer", "text": "[Answer text 2]" }
    }
  ]
}
```

## HowTo

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "[How-to title]",
  "description": "[Brief description]",
  "totalTime": "PT[hours]H[minutes]M",
  "supply": [{ "@type": "HowToSupply", "name": "[Supply item]" }],
  "tool": [{ "@type": "HowToTool", "name": "[Tool]" }],
  "step": [{ "@type": "HowToStep", "position": 1, "name": "[Step title]", "text": "[Instructions]", "url": "[Page URL]#step1" }]
}
```

## Article / BlogPosting

Use `Article`, `BlogPosting`, `NewsArticle`, or `TechArticle` as `@type`.

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "[Title]",
  "description": "[Summary]",
  "image": ["[Image URL]"],
  "datePublished": "[ISO 8601 publish date-time]",
  "dateModified": "[ISO 8601 modified date-time]",
  "author": { "@type": "Person", "name": "[Author Name]" },
  "publisher": { "@type": "Organization", "name": "[Publisher Name]", "logo": { "@type": "ImageObject", "url": "[Logo URL]" } },
  "mainEntityOfPage": { "@type": "WebPage", "@id": "[Canonical URL]" }
}
```

## Product

Use `aggregateRating` and `review` only when counts and values match visible, verified user reviews.
Use `price`, `priceCurrency`, and `availability` only when the page shows current purchasable offer details.

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "[Product Name]",
  "image": ["[Image URL]"],
  "description": "[Product description]",
  "sku": "[SKU]",
  "brand": { "@type": "Brand", "name": "[Brand Name]" },
  "offers": {
    "@type": "Offer",
    "url": "[Product page URL]",
    "priceCurrency": "[ISO 4217 currency code]",
    "price": "[price]",
    "availability": "https://schema.org/[InStock/OutOfStock/PreOrder]"
  }
}
```

**Optional review extension**: add only when the page shows visible, verifiable user reviews that match the numbers.

```json
"aggregateRating": {
  "@type": "AggregateRating",
  "ratingValue": "[rating value]",
  "reviewCount": "[review count]",
  "bestRating": "5",
  "worstRating": "1"
},
"review": [{
  "@type": "Review",
  "author": { "@type": "Person", "name": "[Reviewer Name]" },
  "reviewRating": { "@type": "Rating", "ratingValue": "[rating value]", "bestRating": "5" },
  "reviewBody": "[Review text]",
  "datePublished": "[ISO 8601 review date]"
}]
```

## LocalBusiness

Use a specific subtype when possible, such as `Restaurant`, `Store`, `LegalService`, `Dentist`, or `AutoRepair`. Include `@id`, name, URL, phone, address, opening hours, and price range only when visible. **Optional review extension**: reuse the Product review fragment only when local-business reviews are visible, verifiable, and policy-eligible.

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "@id": "[Business canonical URL]#localbusiness",
  "name": "[Business Name]",
  "url": "[Business canonical URL]",
  "image": ["[Business image URL]"],
  "telephone": "[Phone]",
  "priceRange": "[Visible price range]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[Street address]",
    "addressLocality": "[City]",
    "addressRegion": "[Region]",
    "postalCode": "[Postal code]",
    "addressCountry": "[Country code]"
  },
  "geo": { "@type": "GeoCoordinates", "latitude": "[latitude]", "longitude": "[longitude]" },
  "openingHoursSpecification": [{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["[DayOfWeek]"],
    "opens": "[HH:MM]",
    "closes": "[HH:MM]"
  }],
  "sameAs": ["[Profile URL]"]
}
```

## Organization

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "[Organization Name]",
  "url": "[Website URL]",
  "logo": "[Logo URL]",
  "description": "[Company description]",
  "sameAs": ["[LinkedIn URL]", "[YouTube URL]"],
  "contactPoint": { "@type": "ContactPoint", "telephone": "[Phone]", "contactType": "[contact type]" }
}
```

## BreadcrumbList

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "[Homepage URL]" },
    { "@type": "ListItem", "position": 2, "name": "[Category]", "item": "[Category URL]" },
    { "@type": "ListItem", "position": 3, "name": "[Current Page]", "item": "[Page URL]" }
  ]
}
```

## Other Types Matrix

| Type | Required starter fields | Notes |
|------|-------------------------|-------|
| VideoObject | name, description, thumbnailUrl, uploadDate, duration, embedUrl | Use visible video metadata |
| PodcastEpisode | name, description, url, datePublished, partOfSeries | Align with RSS/episode source-of-truth |
| Event | name, description, startDate, status, attendance mode, location, organizer | Keep status current |
| Course | name, description, provider, course instance | Use CourseInstance for mode/workload |
| Recipe | name, image, author, description, times, yield, ingredients, instructions | Optional review extension only when visible |
| SoftwareApplication | name, operatingSystem, applicationCategory, offers, version, downloadUrl | Price can be `[price or 0]` only when visible |

## Combined Array

Place multiple complete objects inside one array in a single `<script type="application/ld+json">` block when the page needs more than one schema type.

## Preflight Checklist

- Validate with `validator.schema.org` and Google Rich Results Test.
- Use truthful review data only; if unsure, omit review properties.
- Keep URLs canonical and accessible.
- Remove trailing commas and placeholder text before publishing.
