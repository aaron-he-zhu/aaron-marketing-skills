# Meta Tag Code Templates

HTML code templates for Open Graph, Twitter cards, and complete meta tag blocks.

---

## Open Graph Tags

```html
<meta property="og:type" content="[article/website/product]">
<meta property="og:url" content="[Full canonical URL]">
<meta property="og:title" content="[Title - up to 60 chars]">
<meta property="og:description" content="[Description - up to 200 chars]">
<meta property="og:image" content="[Image URL - 1200x630px]">
<meta property="og:site_name" content="[Website Name]">
<meta property="og:locale" content="en_US">
```

**OG Type**: article (blog), website (homepage), product, video.other, profile

**OG Image**: 1200x630px recommended, 600x315px minimum, JPG/PNG, text <20% of image

---

## Twitter Card Tags

```html
<meta name="twitter:card" content="[summary_large_image/summary]">
<meta name="twitter:site" content="@[YourHandle]">
<meta name="twitter:title" content="[Title - 70 chars max]">
<meta name="twitter:description" content="[Description - 200 chars max]">
<meta name="twitter:image" content="[Image URL]">
<meta name="twitter:image:alt" content="[Image description]">
```

**Card types**: summary (144x144 min), summary_large_image (300x157 min), player (640x360 min), app (800x418)

---

## Additional Meta Tags

```html
<link rel="canonical" href="[Preferred URL]">
<meta name="robots" content="index, follow">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="author" content="[Author Name]">
<html lang="en">
```

**Article-specific**:
```html
<meta property="article:published_time" content="[ISO 8601 date]">
<meta property="article:modified_time" content="[ISO 8601 date]">
<meta property="article:author" content="[Author URL]">
<meta property="article:section" content="[Category]">
<meta property="article:tag" content="[Tag]">
```

---

## Complete Meta Tag Block

```html
<!-- Primary -->
<title>[Optimized Title]</title>
<meta name="description" content="[Optimized Description]">
<link rel="canonical" href="[Canonical URL]">

<!-- Open Graph -->
<meta property="og:type" content="[type]">
<meta property="og:url" content="[URL]">
<meta property="og:title" content="[OG Title]">
<meta property="og:description" content="[OG Description]">
<meta property="og:image" content="[Image URL]">
<meta property="og:site_name" content="[Site Name]">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="[Twitter Title]">
<meta name="twitter:description" content="[Twitter Description]">
<meta name="twitter:image" content="[Image URL]">

<!-- Additional -->
<meta name="robots" content="index, follow">
<meta name="author" content="[Author]">
```
