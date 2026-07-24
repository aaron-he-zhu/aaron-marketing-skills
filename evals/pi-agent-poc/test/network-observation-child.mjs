const adapterUrl = new URL("../src/session-tree-poc.mjs", import.meta.url);
const { CAPABILITY_BOUNDARY, PiSessionRuntimeAdapter } = await import(adapterUrl);

const adapter = await PiSessionRuntimeAdapter.create({ id: "isolated-runtime" });
await adapter.accept({ type: "turn_start", turnId: "turn-isolated" });
await adapter.accept({ type: "turn_end", turnId: "turn-isolated" });
await adapter.accept({ type: "save_point", hadPendingMutations: true });

process.stdout.write(`${JSON.stringify({
  attempts: globalThis.__piPocObservedAttempts,
  boundary: CAPABILITY_BOUNDARY,
})}\n`);
