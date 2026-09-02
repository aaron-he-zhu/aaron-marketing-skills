# Social Human Action and Rights Control

Use this control when a social package moves from drafting or gating to human posting, replying, moderating, pausing, unpausing, or removal. It does not add posting automation to any platform.

## Package and gate binding

Bind a package or batch with `package_ref`, `package_version`, `package_hash`, target channel/account reference, and claims/norm-card offsets. A pre-publish SHIP verdict applies only to that exact hash. Editing copy, media, disclosure, destination, or channel after the gate creates a new version and requires re-gating.

## Human action receipt

The human operator records one receipt per action: `action_ref`, action type (`post | reply | moderate | pause | unpause | remove`), channel/account reference, package/version/hash when applicable, actor reference, attempted/completed time, status (`succeeded | partial | failed | unknown`), an opaque post/operation ref, and a bound evidence record. The domain evidence may preserve a live URL, screenshot, or export; the shared locator-free envelope carries only its ref and digest. Label a manually supplied receipt `User-provided`; do not upgrade it to Measured.

A plan, queue row, draft, SHIP verdict, proposal marker, or requested action is not a receipt. Without a matching receipt, state remains `planned`, `queued`, or `open`—never `published`, `replied`, `paused`, `removed`, or `done`. Human posting remains the only publication path for closed and Chinese platforms; this control authorizes no automation anywhere.

## UGC rights

Track each asset with an opaque holder/subject reference, content reference, permitted use (`organic | paid`), exact channels and placements, start/expiry, territory if relevant, compensation, evidence reference, last-verified time, and status (`active | expired | revoked | disputed | unknown`). Only `active` rights covering the exact use allow publication. Public posting, tagging, a branded hashtag, or past organic permission never implies paid rights.

Re-check rights immediately before each use. Expired, revoked, disputed, unknown, or scope-mismatched rights fail closed. Removal requests create one removal action per live placement; the queue stays open until every placement has a matching removal receipt. A registry proposal records the fact for review but is not proof that removal occurred.
