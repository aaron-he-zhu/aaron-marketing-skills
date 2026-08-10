# Agent Plugins v1 portable package

This repository publishes an additional **Portable Lite** projection that follows
the published Agent Plugins 1.0.0 package contract. Portable Lite is this
project's capability label, not a conformance tier defined by Agent Plugins.
The portable archive is additive: the repository's existing Claude, `npx skills`,
SkillHub, ClawHub, OpenClaw, Hermes, Lite, Pro, and Governed surfaces remain
separate compatibility channels.

The implementation baseline is the versioned, published
[Agent Plugins Specification 1.0.0](https://github.com/agentplugins/agent-plugins-spec/blob/f24daf829224fd7fb685ae117c518ea27cbe7b9e/spec/1.0.0.md),
not an unversioned client-native plugin format. The unmodified canonical manifest
schema and its machine-verifiable source record are committed as
[`plugin.schema.json`](../references/standards/agent-plugins/1.0.0/plugin.schema.json)
and
[`PROVENANCE.json`](../references/standards/agent-plugins/1.0.0/PROVENANCE.json).

## Generated package

Build the release-only projection with:

```bash
python3 scripts/build-distribution.py \
  --agent-plugin --profile portable-lite \
  --output /private/path/aaron-agent-plugin
python3 scripts/validate-agent-plugin.py \
  /private/path/aaron-agent-plugin
python3 scripts/build-distribution.py \
  --verify-manifest /private/path/aaron-agent-plugin \
  --profile portable-lite
```

The dedicated validator checks the Agent Plugins manifest, all 120 strict
Skills and contained links, forbidden runtime/MCP surfaces, the projection, and
the complete file manifest. The final command is an independent read-only
manifest/profile check; add `--source-repository owner/repo` and
`--source-commit <40-or-64-hex-object-id>` when the output must match exact
provenance.

The output is one self-contained Agent Plugins directory:

```text
aaron-agent-plugin/
├── plugin.json
├── PORTABILITY.md
├── agent-plugin-projection.json
├── distribution-manifest.json
├── <reachable-root-static-file>  # for example CONNECTORS.md or SECURITY.md
├── docs/
│   └── ...                   # only reachable, contained static docs
├── skills/
│   ├── <skill-name>/
│   │   ├── SKILL.md
│   │   ├── references/       # only reachable skill-local static files
│   │   ├── assets/           # only reachable skill-local static files
│   │   └── ...               # other reachable static skill resources
│   └── ...                   # exactly 120 immediate skill directories
└── references/
    └── ...                   # reachable, contained shared static references
```

The exact root static closure can change when canonical Skill links change; it
is enumerated and hash-bound by the two manifests. Root Markdown/JSON files in
that closure remain inert reference material, not commands or executable
runtime.

`plugin.json` uses the canonical schema identifier
`https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`. Agent Plugins
discovers skills by convention from the immediate children of `skills/`;
`plugin.json` does not enumerate skill paths and needs no `extensions` pointer.
The projection flattens the canonical discipline/phase source tree without
changing the 120 skill identities. The source tree remains authoritative, and
the generated archive is never a second committed Skill inventory.

`agent-plugin-projection.json` binds every generated `SKILL.md` to its canonical
source path and records both source and projected hashes.
`distribution-manifest.json` binds every output file, including all copied
static dependencies, and their hashes. `PORTABILITY.md` is the in-package
capability boundary and the fallback target for links whose source behavior is
deliberately unavailable in Portable Lite. Every packaged path must resolve
inside the generated plugin root; the projection does not use escaping symlinks
or external file references.

## Portable Lite boundary

The portable projection preserves useful static Agent Skills while avoiding
claims that Agent Plugins v1 does not make.

| Surface | Portable Lite behavior |
|---|---|
| Agent Plugins manifest | Included as closed root `plugin.json` targeting 1.0.0. |
| Agent Skills | Exactly 120 immediate `skills/<name>/SKILL.md` children with strict portable frontmatter and contained static dependencies. |
| Shared knowledge | Only the statically reachable reference closure is copied and hash-bound. |
| MCP | No `mcp.json` is generated. The documented connector catalog remains opt-in client configuration. |
| Commands and hooks | Not included. Agent Plugins v1 does not define them as portable component types. |
| Executable repository runtime | Scripts, hooks, commands, controllers, and other root runtime code are not copied. Affected links resolve to the explicit `PORTABILITY.md` fallback. |
| Connectors and credentials | No connector is registered and no credential authority is implied by installation. |
| Host tools | Source `allowed-tools` declarations are omitted, so Portable Lite grants no host-tool preapproval; any tool use remains a separate client/user decision. |
| Persistence and governed loops | No audit/state persistence, run controller, or workflow-loop capability is claimed. A workflow that requires an excluded deterministic runtime must degrade explicitly rather than report a result it did not compute. |
| Client listing metadata | Client- and registry-specific frontmatter is omitted from the portable copy; the existing publication channels retain it. |

The absence of `mcp.json` is intentional. Agent Plugins permits a skills-only
plugin, and a missing optional component location is not an error. This project
does not turn its documented MCP endpoints into automatic process execution or
remote connections merely by adding a portable package.

## Compatibility ownership

The Portable Lite archive does not replace client-specific behavior:

- `.claude-plugin/plugin.json`, the eight commands, and Claude hooks remain in
  the existing Claude compatibility surface.
- `npx skills`, SkillHub, ClawHub, OpenClaw, and Hermes continue to consume their
  established source or generated metadata rather than the strict portable
  frontmatter projection.
- Existing Lite, Pro, and Governed packages keep their current physical and
  runtime ceilings. Portable Lite is an additional package with a narrower,
  static capability contract.
- No reverse-domain client extension is invented. Use `plugin.json.extensions`
  or a namespaced top-level directory only when the namespace-owning client has
  documented its exact fields, files, and runtime behavior.

Agent Plugins standardizes a directory manifest and the fixed discovery
locations for Agent Skills and MCP servers. Distribution, marketplace catalogs,
installation, enablement, updates, signing, permissions, authentication, and
client UI are outside the v1 portable contract. Publishing the archive through
an existing release channel is therefore a repository release decision, not an
Agent Plugins conformance guarantee about that channel.

## Pinned upstream baseline

| Upstream | Pinned identity |
|---|---|
| Agent Plugins specification | `1.0.0`, published by commit `f24daf829224fd7fb685ae117c518ea27cbe7b9e` on 2026-07-27 |
| Canonical manifest schema | `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` |
| Vendored schema SHA-256 | `0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883` over exactly 1,805 bytes |
| Agent Skills baseline | commit `217be548739f21d6008915c29aefe320ea1a90af` on 2026-08-04 |

The Agent Skills baseline is separately pinned because Agent Plugins delegates
`SKILL.md` validity to the Agent Skills specification. At that baseline, the
portable frontmatter fields are `name`, `description`, `license`,
`compatibility`, `metadata`, and experimental `allowed-tools`, and `metadata`
is a string-to-string mapping. Repository-specific listing fields remain in the
canonical compatibility sources instead of being presented as portable fields.
Portable Lite uses the stricter subset `name`, `description`, `license`, and
`metadata`: it omits source host-compatibility text, host-tool preapprovals, and
the Hermes/OpenClaw metadata objects. The canonical source remains the SSOT for
those client-specific behaviors.

## Upstream recheck procedure

Perform this review before changing the projection contract, accepting a new
Agent Plugins version, or cutting a release after either upstream has changed.

1. Read the versioned Agent Plugins specification and the pinned Agent Skills
   specification. Treat their normative text as authoritative when it is more
   restrictive than the JSON Schema.
2. Verify that the canonical URL and release-commit source still produce the
   recorded 1.0.0 bytes:

   ```bash
   curl -fsSL \
     https://agent-plugins.org/schemas/1.0.0/plugin.schema.json \
     | shasum -a 256

   curl -fsSL \
     https://raw.githubusercontent.com/agentplugins/agent-plugins-spec/f24daf829224fd7fb685ae117c518ea27cbe7b9e/schemas/1.0.0/plugin.schema.json \
     | shasum -a 256

   curl -fsSL \
     https://agent-plugins.org/schemas/1.0.0/plugin.schema.json \
     | cmp - references/standards/agent-plugins/1.0.0/plugin.schema.json
   ```

   All three checks must resolve to the recorded bytes and SHA-256. A mismatch
   is an upstream-review stop, not permission to silently refresh the vendored
   file. Published canonical schema identifiers are immutable under the v1
   versioning contract.
3. Review upstream changes after Agent Skills commit
   `217be548739f21d6008915c29aefe320ea1a90af`, especially frontmatter fields,
   metadata types, directory naming, file discovery, and validation behavior.
   Record a new full commit and timestamp only after reviewing its diff.
4. If Agent Plugins publishes a new specification version, add a new versioned
   standards directory and provenance record. Do not rewrite the pinned 1.0.0
   artifact in place.
5. Run the offline provenance guard:

   ```bash
   python3 -m unittest tests.test_agent_plugins_provenance
   ```

6. Rebuild Portable Lite twice into new output directories, run
   `python3 scripts/validate-agent-plugin.py <output>` on both, and require
   identical projection and distribution manifests before release. Then run the
   complete repository validation. Run every available candidate-client smoke
   and record its evidence; an unavailable client remains a non-blocking
   client-verification backlog entry marked `Pending`. A `Pending` row forbids a
   client-verified claim but does not block release of the schema- and
   repository-validator-conformant archive. Schema validation alone does not
   prove path containment or preserved client behavior.
