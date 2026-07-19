import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdir, mkdtemp, readFile, readdir, rm, stat, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";
import test from "node:test";
import { promisify } from "node:util";

import { InMemorySessionRepo, Session } from "@earendil-works/pi-agent-core";

import {
  CAPABILITY_BOUNDARY,
  CUSTOM_ENTRY_TYPES,
  PI_AGENT_CORE_VERSION,
  PI_TO_RUNTIME_EVENT,
  PiSessionRuntimeAdapter,
} from "../src/session-tree-poc.mjs";

const require = createRequire(import.meta.url);
const POC_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const execFileAsync = promisify(execFile);

function entriesOfType(entries, customType) {
  return entries.filter((entry) => entry.type === "custom" && entry.customType === customType);
}

async function finishTurn(adapter, turnId) {
  await adapter.accept({ type: "turn_start", turnId });
  await adapter.accept({ type: "turn_end", turnId });
  return adapter.accept({ type: "save_point", hadPendingMutations: true });
}

async function treeFingerprint(root) {
  const output = [];
  async function visit(current, relative) {
    const info = await stat(current);
    if (info.isDirectory()) {
      output.push(`d:${relative}`);
      for (const name of (await readdir(current)).sort()) {
        await visit(path.join(current, name), path.join(relative, name));
      }
      return;
    }
    const content = await readFile(current);
    output.push(`f:${relative}:${createHash("sha256").update(content).digest("hex")}`);
  }
  await visit(root, ".");
  return output;
}

function stableValue(value) {
  if (Array.isArray(value)) return value.map(stableValue);
  if (value && typeof value === "object") {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stableValue(value[key])]));
  }
  return value;
}

function withProjectionHash(value) {
  return {
    ...value,
    projection_sha256: createHash("sha256").update(JSON.stringify(stableValue(value))).digest("hex"),
  };
}

async function withPatchedRepoCreate(seed, operation) {
  const originalCreate = InMemorySessionRepo.prototype.create;
  InMemorySessionRepo.prototype.create = async function patchedCreate(options) {
    const session = await originalCreate.call(this, options);
    await seed(session);
    return session;
  };
  try {
    return await operation();
  } finally {
    InMemorySessionRepo.prototype.create = originalCreate;
  }
}

function projectedEvent(sequence, sourceType, runtimeType, turnId = null, oldLeafId = null, newLeafId = null) {
  return {
    sequence,
    source_type: sourceType,
    runtime_type: runtimeType,
    turn_id: turnId,
    old_leaf_id: oldLeafId,
    new_leaf_id: newLeafId,
  };
}

async function appendPreloadedTurn(session, mutate = () => {}) {
  const snapshotProjection = {
    schema_version: 1,
    ordinal: 1,
    turn_id: "preloaded-turn",
    parent_turn_id: null,
    source_event_types: ["turn_start", "turn_end"],
    runtime_event_types: ["turn_started", "turn_finished"],
  };
  const batchProjection = {
    schema_version: 1,
    events: [
      projectedEvent(1, "turn_start", "turn_started", "preloaded-turn"),
      projectedEvent(2, "turn_end", "turn_finished", "preloaded-turn"),
      projectedEvent(3, "turn_end", "turn_snapshot_created", "preloaded-turn"),
      projectedEvent(4, "save_point", "save_point_created"),
    ],
  };
  mutate({ stage: "projection", snapshot: snapshotProjection, batch: batchProjection });
  const snapshot = withProjectionHash(snapshotProjection);
  const batch = withProjectionHash(batchProjection);
  mutate({ stage: "hashed", snapshot, batch });
  const snapshotId = await session.appendCustomEntry(CUSTOM_ENTRY_TYPES.turnSnapshot, snapshot);
  const batchId = await session.appendCustomEntry(CUSTOM_ENTRY_TYPES.runtimeEventBatch, batch);
  const savePointProjection = {
    schema_version: 1,
    ordinal: 1,
    event_batch_entry_id: batchId,
    snapshot_entry_ids: [snapshotId],
    flushed_event_count: batch.events.length,
    flushed_snapshot_count: 1,
  };
  mutate({ stage: "save-point-projection", snapshot, batch, savePoint: savePointProjection, snapshotId, batchId });
  const savePoint = withProjectionHash(savePointProjection);
  mutate({ stage: "save-point-hashed", snapshot, batch, savePoint, snapshotId, batchId });
  await session.appendCustomEntry(CUSTOM_ENTRY_TYPES.savePoint, savePoint);
}

async function appendBatchWithoutSnapshots(session, events) {
  const batch = withProjectionHash({ schema_version: 1, events });
  const batchId = await session.appendCustomEntry(CUSTOM_ENTRY_TYPES.runtimeEventBatch, batch);
  await session.appendCustomEntry(CUSTOM_ENTRY_TYPES.savePoint, withProjectionHash({
    schema_version: 1,
    ordinal: 1,
    event_batch_entry_id: batchId,
    snapshot_entry_ids: [],
    flushed_event_count: events.length,
    flushed_snapshot_count: 0,
  }));
}

function snapshotProjection(ordinal, turnId, parentTurnId) {
  return withProjectionHash({
    schema_version: 1,
    ordinal,
    turn_id: turnId,
    parent_turn_id: parentTurnId,
    source_event_types: ["turn_start", "turn_end"],
    runtime_event_types: ["turn_started", "turn_finished"],
  });
}

async function appendReorderedTurnHistory(session) {
  const firstId = await session.appendCustomEntry(
    CUSTOM_ENTRY_TYPES.turnSnapshot,
    snapshotProjection(1, "ordered-a", null),
  );
  const secondId = await session.appendCustomEntry(
    CUSTOM_ENTRY_TYPES.turnSnapshot,
    snapshotProjection(2, "ordered-b", "ordered-a"),
  );
  const events = [
    projectedEvent(1, "turn_start", "turn_started", "ordered-b"),
    projectedEvent(2, "turn_end", "turn_finished", "ordered-b"),
    projectedEvent(3, "turn_end", "turn_snapshot_created", "ordered-b"),
    projectedEvent(4, "turn_start", "turn_started", "ordered-a"),
    projectedEvent(5, "turn_end", "turn_finished", "ordered-a"),
    projectedEvent(6, "turn_end", "turn_snapshot_created", "ordered-a"),
    projectedEvent(7, "save_point", "save_point_created"),
  ];
  const batchId = await session.appendCustomEntry(
    CUSTOM_ENTRY_TYPES.runtimeEventBatch,
    withProjectionHash({ schema_version: 1, events }),
  );
  await session.appendCustomEntry(CUSTOM_ENTRY_TYPES.savePoint, withProjectionHash({
    schema_version: 1,
    ordinal: 1,
    event_batch_entry_id: batchId,
    snapshot_entry_ids: [firstId, secondId],
    flushed_event_count: events.length,
    flushed_snapshot_count: 2,
  }));
}

test("pins the verified Pi release and disables every install lifecycle script", async () => {
  const piPackage = require("@earendil-works/pi-agent-core/package.json");
  assert.equal(piPackage.version, PI_AGENT_CORE_VERSION);
  assert.equal(piPackage.engines.node, ">=22.19.0");
  assert.equal(piPackage.scripts.preinstall, undefined);
  assert.equal(piPackage.scripts.install, undefined);
  assert.equal(piPackage.scripts.postinstall, undefined);

  const packageJson = JSON.parse(await readFile(path.join(POC_ROOT, "package.json"), "utf8"));
  const packageLock = JSON.parse(await readFile(path.join(POC_ROOT, "package-lock.json"), "utf8"));
  const npmrc = await readFile(path.join(POC_ROOT, ".npmrc"), "utf8");
  assert.equal(packageJson.dependencies["@earendil-works/pi-agent-core"], PI_AGENT_CORE_VERSION);
  assert.equal(packageJson.overrides["@earendil-works/pi-ai"], PI_AGENT_CORE_VERSION);
  assert.equal(packageLock.lockfileVersion, 3);
  assert.equal(packageLock.packages["node_modules/@earendil-works/pi-agent-core"].version, PI_AGENT_CORE_VERSION);
  assert.equal(packageLock.packages["node_modules/@earendil-works/pi-ai"].version, PI_AGENT_CORE_VERSION);
  assert.equal(
    packageLock.packages["node_modules/@earendil-works/pi-agent-core"].integrity,
    "sha512-nwnOR3SuLYGRFfyQm8ri4Nj5VGVAvAM9GuqQd3u7BUQj0d6hmD2F8w7OHAAjThE3CuySIdM+v8E22QJG6/RfCg==",
  );
  assert.equal(
    packageLock.packages["node_modules/@earendil-works/pi-ai"].integrity,
    "sha512-Moe/H8c87yacDGK9dPbWphZNjVsrb3nTrIHycOQJAkFEnY9PYxOOd74+ny44kATfPU9Dm7aTHefar3pZF+UKUA==",
  );
  assert.match(npmrc, /^ignore-scripts=true$/m);

  const installScriptPackages = Object.entries(packageLock.packages)
    .filter(([, value]) => value.hasInstallScript === true)
    .map(([name]) => name)
    .sort();
  assert.deepEqual(installScriptPackages, [
    "node_modules/@google/genai",
    "node_modules/protobufjs",
  ]);
});

test("uses Pi branch, moveTo, and fork without losing alternate history", async () => {
  const adapter = await PiSessionRuntimeAdapter.create({ id: "branch-source" });
  const first = await finishTurn(adapter, "turn-1");
  await finishTurn(adapter, "turn-2");

  await adapter.moveTo(first.savePointEntryId);
  await adapter.accept({ type: "save_point", hadPendingMutations: true });
  await finishTurn(adapter, "turn-3");

  const selectedTurns = entriesOfType(await adapter.branch(), CUSTOM_ENTRY_TYPES.turnSnapshot)
    .map((entry) => entry.data.turn_id);
  assert.deepEqual(selectedTurns, ["turn-1", "turn-3"]);
  const selectedSnapshots = entriesOfType(await adapter.branch(), CUSTOM_ENTRY_TYPES.turnSnapshot);
  assert.equal(selectedSnapshots.at(-1).data.parent_turn_id, "turn-1");

  const allTurns = entriesOfType(await adapter.entries(), CUSTOM_ENTRY_TYPES.turnSnapshot)
    .map((entry) => entry.data.turn_id);
  assert.deepEqual(allTurns, ["turn-1", "turn-2", "turn-3"]);

  const fork = await adapter.forkAt(first.savePointEntryId, { id: "branch-fork" });
  await finishTurn(fork, "turn-4");
  const forkTurns = entriesOfType(await fork.branch(), CUSTOM_ENTRY_TYPES.turnSnapshot)
    .map((entry) => entry.data.turn_id);
  assert.deepEqual(forkTurns, ["turn-1", "turn-4"]);
  assert.equal((await fork.metadata()).id, "branch-fork");
  assert.deepEqual(
    entriesOfType(await adapter.branch(), CUSTOM_ENTRY_TYPES.turnSnapshot).map((entry) => entry.data.turn_id),
    ["turn-1", "turn-3"],
  );
});

test("creates exactly one snapshot per turn and flushes only at save points", async () => {
  const adapter = await PiSessionRuntimeAdapter.create({ id: "snapshot-session" });
  await adapter.accept({ type: "turn_start", turnId: "turn-a" });
  await adapter.accept({ type: "turn_end", turnId: "turn-a" });
  assert.equal((await adapter.entries()).length, 0);
  assert.equal(adapter.pendingMutationCount, 4);

  const first = await adapter.accept({ type: "save_point", hadPendingMutations: true });
  assert.equal(first.savePoint.flushed_snapshot_count, 1);
  assert.equal(first.savePoint.flushed_event_count, 4);
  assert.equal(adapter.pendingMutationCount, 0);
  await assert.rejects(
    adapter.accept({ type: "turn_start", turnId: "turn-a" }),
    /already snapshotted/,
  );

  await finishTurn(adapter, "turn-b");
  const entries = await adapter.entries();
  const snapshots = entriesOfType(entries, CUSTOM_ENTRY_TYPES.turnSnapshot);
  assert.equal(snapshots.length, 2);
  assert.deepEqual(snapshots.map((entry) => entry.data.turn_id), ["turn-a", "turn-b"]);
  assert.deepEqual(snapshots.map((entry) => entry.data.parent_turn_id), [null, "turn-a"]);
  assert.ok(snapshots.every((entry) => /^[0-9a-f]{64}$/.test(entry.data.projection_sha256)));
  assert.equal(entriesOfType(entries, CUSTOM_ENTRY_TYPES.runtimeEventBatch).length, 2);
  assert.equal(entriesOfType(entries, CUSTOM_ENTRY_TYPES.savePoint).length, 2);
});

test("fails closed for unknown, provider, tool, payload-bearing, and malformed events", async () => {
  const adapter = await PiSessionRuntimeAdapter.create({ id: "fail-closed" });
  for (const event of [
    { type: "future_event" },
    { type: "__proto__" },
    { type: "constructor" },
    { type: "before_provider_request" },
    { type: "tool_call" },
    { type: "message_end", message: { role: "assistant", content: "secret" } },
    { type: "turn_start", turnId: "turn-1", prompt: "must-not-persist" },
  ]) {
    await assert.rejects(adapter.accept(event), /not allowlisted|exactly/);
  }
  assert.equal(adapter.pendingMutationCount, 0);
  assert.equal((await adapter.entries()).length, 0);
  assert.equal(PI_TO_RUNTIME_EVENT.tool_call, undefined);
});

test("keeps construction internal and never calls injected repo or session objects", async () => {
  let methodCalls = 0;
  const fake = {
    create() { methodCalls += 1; },
    open() { methodCalls += 1; },
    getMetadata() { methodCalls += 1; },
  };
  assert.throws(
    () => new PiSessionRuntimeAdapter(fake, fake, fake),
    /constructor is internal/,
  );
  await assert.rejects(
    PiSessionRuntimeAdapter.create({ repo: fake }),
    /non-data value|unsupported key/,
  );
  const prototypeOption = {};
  Object.defineProperty(prototypeOption, "__proto__", {
    configurable: true,
    enumerable: true,
    writable: true,
    value: null,
  });
  await assert.rejects(PiSessionRuntimeAdapter.create(prototypeOption), /unsupported key/);
  assert.equal(methodCalls, 0);
  assert.equal(PiSessionRuntimeAdapter.fromSession, undefined);
  assert.equal(Object.getOwnPropertyDescriptor(PiSessionRuntimeAdapter.prototype, "session"), undefined);
});

test("copies event envelopes without invoking accessors or Proxy traps", async () => {
  const adapter = await PiSessionRuntimeAdapter.create({ id: "descriptor-boundary" });
  let getterCalls = 0;
  const accessorEvent = {};
  Object.defineProperty(accessorEvent, "type", {
    configurable: true,
    enumerable: true,
    get() {
      getterCalls += 1;
      return "agent_start";
    },
  });
  await assert.rejects(adapter.accept(accessorEvent), /data property/);
  assert.equal(getterCalls, 0);

  let proxyTrapCalls = 0;
  const proxyEvent = new Proxy({ type: "agent_start" }, {
    get() { proxyTrapCalls += 1; return "agent_start"; },
    getOwnPropertyDescriptor() { proxyTrapCalls += 1; return undefined; },
    getPrototypeOf() { proxyTrapCalls += 1; return Object.prototype; },
    ownKeys() { proxyTrapCalls += 1; return ["type"]; },
  });
  await assert.rejects(adapter.accept(proxyEvent), /must not be a Proxy/);
  assert.equal(proxyTrapCalls, 0);

  const symbolEvent = { type: "agent_start" };
  symbolEvent[Symbol("hidden")] = "payload";
  await assert.rejects(adapter.accept(symbolEvent), /only string keys/);

  const nonEnumerableEvent = { type: "agent_start" };
  Object.defineProperty(nonEnumerableEvent, "hidden", { value: "payload" });
  await assert.rejects(adapter.accept(nonEnumerableEvent), /normal data property/);

  const prototypeEvent = { type: "agent_start" };
  Object.defineProperty(prototypeEvent, "__proto__", {
    configurable: true,
    enumerable: true,
    writable: true,
    value: null,
  });
  assert.ok(Reflect.ownKeys(prototypeEvent).includes("__proto__"));
  await assert.rejects(adapter.accept(prototypeEvent), /must contain exactly/);
  assert.equal(adapter.pendingMutationCount, 0);
});

test("isolates caller inputs, return values, entries, branches, and metadata", async () => {
  const adapter = await PiSessionRuntimeAdapter.create({ id: "isolated-views" });
  const start = { type: "turn_start", turnId: "turn-safe" };
  const accepted = adapter.accept(start);
  start.turnId = "turn-mutated";
  await accepted;
  const ended = await adapter.accept({ type: "turn_end", turnId: "turn-safe" });
  assert.ok(Object.isFrozen(ended));
  assert.ok(Object.isFrozen(ended.snapshot));
  assert.throws(() => { ended.snapshot.turn_id = "tampered"; }, TypeError);

  const flushed = await adapter.accept({ type: "save_point", hadPendingMutations: true });
  assert.ok(Object.isFrozen(flushed.savePoint));
  const entries = await adapter.entries();
  const snapshots = entriesOfType(entries, CUSTOM_ENTRY_TYPES.turnSnapshot);
  const originalHash = snapshots[0].data.projection_sha256;
  assert.ok(Object.isFrozen(entries));
  assert.ok(Object.isFrozen(snapshots[0].data));
  assert.throws(() => { snapshots[0].data.turn_id = "tampered"; }, TypeError);
  assert.throws(() => { entries.push({}); }, TypeError);

  const branch = await adapter.branch();
  const metadata = await adapter.metadata();
  assert.ok(Object.isFrozen(branch));
  assert.ok(Object.isFrozen(metadata));
  assert.throws(() => { metadata.id = "tampered"; }, TypeError);
  const reread = entriesOfType(await adapter.entries(), CUSTOM_ENTRY_TYPES.turnSnapshot)[0];
  assert.equal(reread.data.turn_id, "turn-safe");
  assert.equal(reread.data.projection_sha256, originalHash);
});

test("hydrates valid custom history and rejects malformed adapter-owned history", async () => {
  await withPatchedRepoCreate(
    (session) => appendPreloadedTurn(session),
    async () => {
      const adapter = await PiSessionRuntimeAdapter.create({ id: "valid-preload" });
      await finishTurn(adapter, "next-turn");
      const snapshots = entriesOfType(await adapter.entries(), CUSTOM_ENTRY_TYPES.turnSnapshot);
      assert.deepEqual(snapshots.map((entry) => entry.data.ordinal), [1, 2]);
      assert.equal(snapshots[1].data.parent_turn_id, "preloaded-turn");
    },
  );

  const malformedCases = [
    {
      name: "projection hash",
      pattern: /projection hash mismatch/,
      mutate({ stage, snapshot }) {
        if (stage === "hashed") snapshot.projection_sha256 = "0".repeat(64);
      },
    },
    {
      name: "sequence",
      pattern: /event sequence/,
      mutate({ stage, batch }) {
        if (stage === "projection") batch.events[1].sequence = 1;
      },
    },
    {
      name: "ordinal",
      pattern: /positive integer/,
      mutate({ stage, snapshot }) {
        if (stage === "projection") snapshot.ordinal = 0;
      },
    },
    {
      name: "snapshot parent",
      pattern: /snapshot parent mismatch/,
      mutate({ stage, snapshot }) {
        if (stage === "projection") snapshot.parent_turn_id = "wrong-parent";
      },
    },
    {
      name: "save-point cross-reference",
      pattern: /cross-reference mismatch/,
      mutate({ stage, savePoint }) {
        if (stage === "save-point-projection") savePoint.snapshot_entry_ids = ["wrong-id"];
      },
    },
  ];
  for (const malformed of malformedCases) {
    await withPatchedRepoCreate(
      (session) => appendPreloadedTurn(session, malformed.mutate),
      () => assert.rejects(
        PiSessionRuntimeAdapter.create({ id: `malformed-${malformed.name.replaceAll(" ", "-")}` }),
        malformed.pattern,
      ),
    );
  }

  await withPatchedRepoCreate(
    (session) => appendBatchWithoutSnapshots(session, [
      projectedEvent(1, "turn_start", "turn_started", "ghost-turn"),
      projectedEvent(2, "turn_end", "turn_finished", "ghost-turn"),
      projectedEvent(3, "turn_end", "turn_snapshot_created", "ghost-turn"),
      projectedEvent(4, "save_point", "save_point_created"),
    ]),
    () => assert.rejects(PiSessionRuntimeAdapter.create({ id: "ghost-turn" }), /snapshot projections/),
  );
  await withPatchedRepoCreate(
    appendReorderedTurnHistory,
    () => assert.rejects(PiSessionRuntimeAdapter.create({ id: "reordered-turns" }), /snapshot projections/),
  );
  await withPatchedRepoCreate(
    (session) => appendBatchWithoutSnapshots(session, [
      projectedEvent(1, "save_point", "save_point_created"),
      projectedEvent(2, "agent_start", "run_started"),
      projectedEvent(3, "save_point", "save_point_created"),
    ]),
    () => assert.rejects(PiSessionRuntimeAdapter.create({ id: "duplicate-save" }), /exactly one final save_point/),
  );

  await withPatchedRepoCreate(
    (session) => session.appendCustomEntry("aaron.future_entry.v1", { preserved: true }),
    () => assert.rejects(PiSessionRuntimeAdapter.create({ id: "unknown-owned" }), /unrecognized adapter-owned/),
  );
  await withPatchedRepoCreate(
    (session) => session.appendCustomEntry("third-party.note.v1", { preserved: true }),
    async () => {
      const adapter = await PiSessionRuntimeAdapter.create({ id: "unknown-third-party" });
      assert.equal((await adapter.entries())[0].customType, "third-party.note.v1");
    },
  );
});

test("fails fast when mutations race and never double-flushes a save point", async () => {
  const adapter = await PiSessionRuntimeAdapter.create({ id: "single-flight-save" });
  await adapter.accept({ type: "turn_start", turnId: "race-turn" });
  await adapter.accept({ type: "turn_end", turnId: "race-turn" });
  const firstSave = adapter.accept({ type: "save_point", hadPendingMutations: true });
  assert.throws(() => adapter.pendingMutationCount, /in progress/);
  const saveResults = await Promise.allSettled([
    firstSave,
    adapter.accept({ type: "save_point", hadPendingMutations: true }),
  ]);
  assert.equal(saveResults.filter((result) => result.status === "fulfilled").length, 1);
  assert.equal(saveResults.filter((result) => result.status === "rejected").length, 1);
  assert.match(saveResults.find((result) => result.status === "rejected").reason.message, /in progress/);
  const entries = await adapter.entries();
  assert.equal(entriesOfType(entries, CUSTOM_ENTRY_TYPES.turnSnapshot).length, 1);
  assert.equal(entriesOfType(entries, CUSTOM_ENTRY_TYPES.runtimeEventBatch).length, 1);
  assert.equal(entriesOfType(entries, CUSTOM_ENTRY_TYPES.savePoint).length, 1);
  assert.equal(adapter.pendingMutationCount, 0);
});

test("serializes public reads with mutations and pendingMutationCount", async () => {
  const adapter = await PiSessionRuntimeAdapter.create({ id: "read-operation-guard" });
  const originalGetEntries = Session.prototype.getEntries;
  let signalEntered;
  let releaseRead;
  const entered = new Promise((resolve) => { signalEntered = resolve; });
  const gate = new Promise((resolve) => { releaseRead = resolve; });
  Session.prototype.getEntries = async function delayedGetEntries() {
    signalEntered();
    await gate;
    return originalGetEntries.call(this);
  };

  let readPromise;
  try {
    readPromise = adapter.entries();
    await entered;
    await assert.rejects(adapter.accept({ type: "agent_start" }), /entries is in progress/);
    assert.throws(() => adapter.pendingMutationCount, /entries is in progress/);
    releaseRead();
    assert.deepEqual(await readPromise, []);
    await adapter.accept({ type: "agent_start" });
    assert.equal(adapter.pendingMutationCount, 1);
  } finally {
    releaseRead();
    Session.prototype.getEntries = originalGetEntries;
    if (readPromise) await readPromise.catch(() => {});
  }
});

test("fails fast when moveTo or forkAt races another mutation", async () => {
  const moveAdapter = await PiSessionRuntimeAdapter.create({ id: "single-flight-move" });
  const first = await finishTurn(moveAdapter, "move-turn");
  const moveRace = await Promise.allSettled([
    moveAdapter.moveTo(first.savePointEntryId),
    moveAdapter.accept({ type: "turn_start", turnId: "must-not-start" }),
  ]);
  assert.deepEqual(moveRace.map((result) => result.status), ["fulfilled", "rejected"]);
  assert.match(moveRace[1].reason.message, /in progress/);
  await moveAdapter.accept({ type: "save_point", hadPendingMutations: true });
  const latestBatch = entriesOfType(await moveAdapter.branch(), CUSTOM_ENTRY_TYPES.runtimeEventBatch).at(-1);
  const treeEvent = latestBatch.data.events.find((event) => event.source_type === "session_tree");
  assert.equal(treeEvent.new_leaf_id, first.savePointEntryId);
  assert.equal(typeof treeEvent.old_leaf_id, "string");

  const forkAdapter = await PiSessionRuntimeAdapter.create({ id: "single-flight-fork" });
  const forkPoint = await finishTurn(forkAdapter, "fork-turn");
  const forkRace = await Promise.allSettled([
    forkAdapter.forkAt(forkPoint.savePointEntryId, { id: "single-flight-child" }),
    forkAdapter.accept({ type: "turn_start", turnId: "must-not-start" }),
  ]);
  assert.deepEqual(forkRace.map((result) => result.status), ["fulfilled", "rejected"]);
  assert.match(forkRace[1].reason.message, /in progress/);
  assert.equal((await forkRace[0].value.metadata()).id, "single-flight-child");
  assert.equal(forkAdapter.pendingMutationCount, 0);
});

test("allows moveTo and forkAt only at fully validated adapter save-point boundaries", async () => {
  const adapter = await PiSessionRuntimeAdapter.create({ id: "boundary-targets" });
  const first = await finishTurn(adapter, "boundary-turn");
  const entriesBefore = await adapter.entries();
  const branchBefore = await adapter.branch();

  for (const [label, target] of [
    ["snapshot", first.snapshotEntryIds[0]],
    ["event-batch", first.eventBatchEntryId],
  ]) {
    await assert.rejects(adapter.moveTo(target), /save-point boundary/);
    await assert.rejects(
      adapter.forkAt(target, { id: `invalid-${label}-fork` }),
      /save-point boundary/,
    );
    assert.deepEqual(await adapter.entries(), entriesBefore);
    assert.deepEqual(await adapter.branch(), branchBefore);
    assert.equal(adapter.pendingMutationCount, 0);
  }

  const fork = await adapter.forkAt(first.savePointEntryId, { id: "valid-boundary-fork" });
  assert.equal((await fork.metadata()).id, "valid-boundary-fork");
  await finishTurn(fork, "fork-after-rejection");
});

test("rejects sequential and cross-adapter fork-id collisions before Pi can overwrite the repo map", async () => {
  const source = await PiSessionRuntimeAdapter.create({ id: "collision-source" });
  const first = await finishTurn(source, "collision-turn-1");
  const second = await finishTurn(source, "collision-turn-2");

  await assert.rejects(
    source.forkAt(first.savePointEntryId, { id: "collision-source" }),
    /fork id already exists/,
  );
  const healthyChild = await source.forkAt(second.savePointEntryId, { id: "healthy-child" });
  assert.equal((await healthyChild.metadata()).id, "healthy-child");

  await source.forkAt(first.savePointEntryId, { id: "one-child" });
  await assert.rejects(
    source.forkAt(second.savePointEntryId, { id: "one-child" }),
    /fork id already exists/,
  );

  let optionGetterCalls = 0;
  const accessorOptions = {};
  Object.defineProperty(accessorOptions, "id", {
    configurable: true,
    enumerable: true,
    get() {
      optionGetterCalls += 1;
      return "must-not-be-read";
    },
  });
  await assert.rejects(source.forkAt(first.savePointEntryId, accessorOptions), /data property/);
  assert.equal(optionGetterCalls, 0);

  const sharedRepoAdapter = await source.forkAt(first.savePointEntryId, { id: "race-parent" });
  const race = await Promise.allSettled([
    source.forkAt(first.savePointEntryId, { id: "same-race-child" }),
    sharedRepoAdapter.forkAt(first.savePointEntryId, { id: "same-race-child" }),
  ]);
  assert.equal(race.filter((result) => result.status === "fulfilled").length, 1);
  assert.equal(race.filter((result) => result.status === "rejected").length, 1);
  assert.match(race.find((result) => result.status === "rejected").reason.message, /reserved|already exists/);

  await assert.rejects(
    source.forkAt(first.savePointEntryId, { id: "same-race-child" }),
    /fork id already exists/,
  );
  const postRace = await source.forkAt(second.savePointEntryId, { id: "post-race-child" });
  assert.equal((await postRace.metadata()).id, "post-race-child");
});

test("observes no network or subprocess invocation and leaves sentinels untouched", async () => {
  const fixture = await mkdtemp(path.join(os.tmpdir(), "pi-agent-poc-"));
  const memoryRoot = path.join(fixture, "memory");
  const registryRoot = path.join(fixture, "registries");
  await mkdir(path.join(memoryRoot, "claims"), { recursive: true });
  await mkdir(registryRoot, { recursive: true });
  await writeFile(path.join(memoryRoot, "claims", "sentinel.json"), "{\"unchanged\":true}\n");
  await writeFile(path.join(registryRoot, "sentinel.json"), "{\"unchanged\":true}\n");
  const before = await treeFingerprint(fixture);

  try {
    const { stdout, stderr } = await execFileAsync(process.execPath, [
      "--import",
      path.join(POC_ROOT, "test", "network-observation-preload.mjs"),
      path.join(POC_ROOT, "test", "network-observation-child.mjs"),
    ], { cwd: fixture, encoding: "utf8" });
    assert.equal(stderr, "");
    const observation = JSON.parse(stdout);
    assert.deepEqual(observation.attempts, []);
    assert.deepEqual(observation.boundary, {
      providerModulesLoaded: true,
      providerInvocation: false,
      modelInvocation: false,
      network: false,
      tools: false,
      persistentFilesystem: false,
    });
  } finally {
    assert.deepEqual(await treeFingerprint(fixture), before);
    await rm(fixture, { recursive: true, force: true });
  }
});
