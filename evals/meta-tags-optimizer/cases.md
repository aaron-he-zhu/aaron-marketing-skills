```yaml
{id: routing-command-publish-meta-001, type: eval-case, status: simulated, target_skill: meta-tags-optimizer, scenario: "User asks for title, meta description, and social previews.", input_summary: "Create title tags, meta descriptions, OG, and Twitter cards for this page.", expected_behavior: ["Route /aaron-seo-geo:create --meta to meta-tags-optimizer for metadata packages.", "Keep unsupported proof claims out of titles.", "Hand off schema needs to schema-markup-generator."], failure_modes: ["Routes only to seo-content-writer.", "Optimizes unsafe claims.", "Omits social tags."]}
```
