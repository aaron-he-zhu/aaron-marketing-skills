import { createHash } from "node:crypto";
import { isProxy } from "node:util/types";

import { InMemorySessionRepo } from "@earendil-works/pi-agent-core";

export const PI_AGENT_CORE_VERSION = "0.80.10";

export const CAPABILITY_BOUNDARY = Object.freeze({
  providerModulesLoaded: true,
  providerInvocation: false,
  modelInvocation: false,
  network: false,
  tools: false,
  persistentFilesystem: false,
});

export const CUSTOM_ENTRY_TYPES = Object.freeze({
  turnSnapshot: "aaron.turn_snapshot.v1",
  runtimeEventBatch: "aaron.runtime_event_batch.v1",
  savePoint: "aaron.save_point.v1",
});

// These are adapter-owned synthetic facsimiles, not raw AgentHarness events.
export const PI_TO_RUNTIME_EVENT = Object.freeze({
  agent_start: "run_started",
  turn_start: "turn_started",
  turn_end: "turn_finished",
  save_point: "save_point_created",
  session_tree: "branch_created",
  agent_end: "run_finished",
});

const EVENT_KEYS = Object.freeze({
  agent_start: ["type"],
  turn_start: ["type", "turnId"],
  turn_end: ["type", "turnId"],
  save_point: ["type", "hadPendingMutations"],
  session_tree: ["type", "oldLeafId", "newLeafId"],
  agent_end: ["type"],
});

const INTERNAL_CONSTRUCTION_TOKEN = Symbol("PiSessionRuntimeAdapter.internal");
const OWNED_CUSTOM_TYPES = new Set(Object.values(CUSTOM_ENTRY_TYPES));
const PROJECTION_HASH = /^[0-9a-f]{64}$/;
const REPO_FORK_ID_RESERVATIONS = new WeakMap();

function isPlainObject(value) {
  if (value === null || typeof value !== "object" || Array.isArray(value) || isProxy(value)) return false;
  const prototype = Object.getPrototypeOf(value);
  return prototype === Object.prototype || prototype === null;
}

function clonePlainData(value, label, { requireNormalDescriptors = false } = {}) {
  const seen = new Set();

  function clone(current, path) {
    if (
      current === null ||
      current === undefined ||
      typeof current === "string" ||
      typeof current === "boolean"
    ) {
      return current;
    }
    if (typeof current === "number" && Number.isFinite(current)) return current;
    if (typeof current !== "object") throw new TypeError(`${path} contains non-data value`);
    if (isProxy(current)) throw new TypeError(`${path} must not be a Proxy`);
    if (seen.has(current)) throw new TypeError(`${path} must not be cyclic`);
    seen.add(current);

    try {
      if (Array.isArray(current)) {
        if (Object.getPrototypeOf(current) !== Array.prototype) {
          throw new TypeError(`${path} must use the standard Array prototype`);
        }
        const keys = Reflect.ownKeys(current);
        const descriptors = Object.getOwnPropertyDescriptors(current);
        const expected = new Set(["length", ...Array.from({ length: current.length }, (_, index) => String(index))]);
        if (keys.some((key) => typeof key !== "string" || !expected.has(key)) || keys.length !== expected.size) {
          throw new TypeError(`${path} must be a dense data-only array`);
        }
        const output = [];
        for (let index = 0; index < current.length; index += 1) {
          const descriptor = descriptors[String(index)];
          if (!descriptor || !("value" in descriptor) || descriptor.get || descriptor.set) {
            throw new TypeError(`${path}[${index}] must be a data property`);
          }
          if (
            requireNormalDescriptors &&
            (!descriptor.enumerable || !descriptor.writable || !descriptor.configurable)
          ) {
            throw new TypeError(`${path}[${index}] must be a normal data property`);
          }
          output.push(clone(descriptor.value, `${path}[${index}]`));
        }
        return output;
      }

      if (!isPlainObject(current)) throw new TypeError(`${path} must be a plain object`);
      const keys = Reflect.ownKeys(current);
      if (keys.some((key) => typeof key !== "string")) {
        throw new TypeError(`${path} must contain only string keys`);
      }
      const descriptors = Object.getOwnPropertyDescriptors(current);
      const output = {};
      for (const key of keys) {
        const descriptor = descriptors[key];
        if (!descriptor || !("value" in descriptor) || descriptor.get || descriptor.set) {
          throw new TypeError(`${path}.${key} must be a data property`);
        }
        if (
          requireNormalDescriptors &&
          (!descriptor.enumerable || !descriptor.writable || !descriptor.configurable)
        ) {
          throw new TypeError(`${path}.${key} must be a normal data property`);
        }
        Object.defineProperty(output, key, {
          configurable: true,
          enumerable: true,
          writable: true,
          value: clone(descriptor.value, `${path}.${key}`),
        });
      }
      return output;
    } finally {
      seen.delete(current);
    }
  }

  return clone(value, label);
}

function deepFreeze(value) {
  if (value && typeof value === "object" && !Object.isFrozen(value)) {
    for (const item of Array.isArray(value) ? value : Object.values(value)) deepFreeze(item);
    Object.freeze(value);
  }
  return value;
}

function expose(value, label = "result") {
  return deepFreeze(clonePlainData(value, label));
}

function immutableCopy(value, label) {
  return deepFreeze(clonePlainData(value, label));
}

function assertExactKeys(value, expected, label) {
  const actual = Reflect.ownKeys(value).sort();
  const wanted = [...expected].sort();
  if (actual.length !== wanted.length || actual.some((key, index) => key !== wanted[index])) {
    throw new TypeError(`${label} must contain exactly: ${wanted.join(", ")}`);
  }
}

function assertSafeId(value, label, { nullable = false } = {}) {
  if (nullable && value === null) return;
  if (typeof value !== "string" || !/^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/.test(value)) {
    throw new TypeError(`${label} must be a safe identifier`);
  }
}

function assertPositiveInteger(value, label) {
  if (!Number.isSafeInteger(value) || value < 1) throw new TypeError(`${label} must be a positive integer`);
}

function stableValue(value) {
  if (Array.isArray(value)) return value.map(stableValue);
  if (isPlainObject(value)) {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stableValue(value[key])]));
  }
  if (value === null || ["string", "boolean"].includes(typeof value)) return value;
  if (typeof value === "number" && Number.isSafeInteger(value)) return value;
  throw new TypeError("projection contains a non-canonical value");
}

function digest(value) {
  return createHash("sha256").update(JSON.stringify(stableValue(value))).digest("hex");
}

function withProjectionHash(value) {
  const projection = clonePlainData(value, "projection");
  return { ...projection, projection_sha256: digest(projection) };
}

function verifyProjectionHash(value, label) {
  if (typeof value.projection_sha256 !== "string" || !PROJECTION_HASH.test(value.projection_sha256)) {
    throw new TypeError(`${label}.projection_sha256 must be a SHA-256 digest`);
  }
  const { projection_sha256: actual, ...projection } = value;
  if (digest(projection) !== actual) throw new Error(`${label} projection hash mismatch`);
}

function copyAllowedOptions(value, allowed, label) {
  const source = value === undefined ? {} : value;
  const copied = clonePlainData(source, label, { requireNormalDescriptors: true });
  if (!isPlainObject(copied)) throw new TypeError(`${label} must be a plain object`);
  const unknown = Reflect.ownKeys(copied).filter((key) => !allowed.includes(key));
  if (unknown.length) throw new TypeError(`${label} contains unsupported key: ${unknown[0]}`);
  return copied;
}

function validateSyntheticPiEvent(input) {
  const event = clonePlainData(input, "event", { requireNormalDescriptors: true });
  if (!isPlainObject(event) || typeof event.type !== "string") {
    throw new TypeError("event must be a plain object with a string type");
  }
  if (!Object.hasOwn(EVENT_KEYS, event.type)) {
    throw new TypeError(`synthetic event type is not allowlisted: ${event.type}`);
  }
  const expectedKeys = EVENT_KEYS[event.type];
  assertExactKeys(event, expectedKeys, event.type);

  if (event.type === "turn_start" || event.type === "turn_end") {
    assertSafeId(event.turnId, "turnId");
  } else if (event.type === "save_point") {
    if (typeof event.hadPendingMutations !== "boolean") {
      throw new TypeError("hadPendingMutations must be boolean");
    }
  } else if (event.type === "session_tree") {
    assertSafeId(event.oldLeafId, "oldLeafId", { nullable: true });
    assertSafeId(event.newLeafId, "newLeafId", { nullable: true });
  }
  return event;
}

function validateOuterBranch(branchInput) {
  if (isProxy(branchInput) || !Array.isArray(branchInput)) throw new TypeError("Pi branch must be an array");
  const branch = clonePlainData(branchInput, "Pi branch");
  const ids = new Set();
  let previousId = null;
  for (const [index, entry] of branch.entries()) {
    if (!isPlainObject(entry)) throw new TypeError(`Pi branch[${index}] must be a plain object`);
    assertSafeId(entry.id, `Pi branch[${index}].id`);
    assertSafeId(entry.parentId, `Pi branch[${index}].parentId`, { nullable: true });
    if (ids.has(entry.id)) throw new Error(`Pi branch contains duplicate entry id: ${entry.id}`);
    if (entry.parentId !== previousId) throw new Error(`Pi branch parent mismatch at entry ${entry.id}`);
    if (typeof entry.type !== "string") throw new TypeError(`Pi branch[${index}].type must be a string`);
    ids.add(entry.id);
    previousId = entry.id;
  }
  return branch;
}

function validateSnapshot(data, label) {
  assertExactKeys(data, [
    "schema_version", "ordinal", "turn_id", "parent_turn_id", "source_event_types",
    "runtime_event_types", "projection_sha256",
  ], label);
  if (data.schema_version !== 1) throw new TypeError(`${label}.schema_version must be 1`);
  assertPositiveInteger(data.ordinal, `${label}.ordinal`);
  assertSafeId(data.turn_id, `${label}.turn_id`);
  assertSafeId(data.parent_turn_id, `${label}.parent_turn_id`, { nullable: true });
  if (
    !Array.isArray(data.source_event_types) ||
    data.source_event_types.length !== 2 ||
    data.source_event_types[0] !== "turn_start" ||
    data.source_event_types[1] !== "turn_end"
  ) throw new TypeError(`${label}.source_event_types is invalid`);
  if (
    !Array.isArray(data.runtime_event_types) ||
    data.runtime_event_types.length !== 2 ||
    data.runtime_event_types[0] !== "turn_started" ||
    data.runtime_event_types[1] !== "turn_finished"
  ) throw new TypeError(`${label}.runtime_event_types is invalid`);
  verifyProjectionHash(data, label);
}

function validateProjectedEvent(event, label) {
  assertExactKeys(event, [
    "sequence", "source_type", "runtime_type", "turn_id", "old_leaf_id", "new_leaf_id",
  ], label);
  assertPositiveInteger(event.sequence, `${label}.sequence`);
  if (!Object.hasOwn(PI_TO_RUNTIME_EVENT, event.source_type)) {
    throw new TypeError(`${label}.source_type is not allowlisted`);
  }
  const normalRuntime = PI_TO_RUNTIME_EVENT[event.source_type];
  if (event.runtime_type !== normalRuntime && !(event.source_type === "turn_end" && event.runtime_type === "turn_snapshot_created")) {
    throw new TypeError(`${label}.runtime_type does not match its source`);
  }
  if (event.source_type === "turn_start" || event.source_type === "turn_end") {
    assertSafeId(event.turn_id, `${label}.turn_id`);
  } else if (event.turn_id !== null) {
    throw new TypeError(`${label}.turn_id must be null`);
  }
  if (event.source_type === "session_tree") {
    assertSafeId(event.old_leaf_id, `${label}.old_leaf_id`, { nullable: true });
    assertSafeId(event.new_leaf_id, `${label}.new_leaf_id`, { nullable: true });
  } else if (event.old_leaf_id !== null || event.new_leaf_id !== null) {
    throw new TypeError(`${label} leaf identifiers must be null`);
  }
}

function validateEventBatch(data, label, previousSequence) {
  assertExactKeys(data, ["schema_version", "events", "projection_sha256"], label);
  if (data.schema_version !== 1) throw new TypeError(`${label}.schema_version must be 1`);
  if (!Array.isArray(data.events) || data.events.length < 1) throw new TypeError(`${label}.events must not be empty`);
  let sequence = previousSequence;
  for (const [index, event] of data.events.entries()) {
    if (!isPlainObject(event)) throw new TypeError(`${label}.events[${index}] must be a plain object`);
    validateProjectedEvent(event, `${label}.events[${index}]`);
    if (index === 0 ? event.sequence <= sequence : event.sequence !== sequence + 1) {
      throw new Error(`${label} event sequence is not strictly ordered`);
    }
    sequence = event.sequence;
  }
  const last = data.events.at(-1);
  if (last.source_type !== "save_point" || last.runtime_type !== "save_point_created") {
    throw new Error(`${label} must terminate in save_point_created`);
  }
  if (data.events.slice(0, -1).some((event) => event.source_type === "save_point")) {
    throw new Error(`${label} may contain exactly one final save_point`);
  }
  verifyProjectionHash(data, label);
  return sequence;
}

function validateSavePoint(data, label) {
  assertExactKeys(data, [
    "schema_version", "ordinal", "event_batch_entry_id", "snapshot_entry_ids",
    "flushed_event_count", "flushed_snapshot_count", "projection_sha256",
  ], label);
  if (data.schema_version !== 1) throw new TypeError(`${label}.schema_version must be 1`);
  assertPositiveInteger(data.ordinal, `${label}.ordinal`);
  assertSafeId(data.event_batch_entry_id, `${label}.event_batch_entry_id`);
  if (!Array.isArray(data.snapshot_entry_ids)) throw new TypeError(`${label}.snapshot_entry_ids must be an array`);
  for (const [index, id] of data.snapshot_entry_ids.entries()) {
    assertSafeId(id, `${label}.snapshot_entry_ids[${index}]`);
  }
  if (!Number.isSafeInteger(data.flushed_event_count) || data.flushed_event_count < 1) {
    throw new TypeError(`${label}.flushed_event_count must be positive`);
  }
  if (!Number.isSafeInteger(data.flushed_snapshot_count) || data.flushed_snapshot_count < 0) {
    throw new TypeError(`${label}.flushed_snapshot_count must be non-negative`);
  }
  verifyProjectionHash(data, label);
}

function deriveProjectedSnapshotTurns(events, label) {
  const turnIds = [];
  for (let index = 0; index < events.length; index += 1) {
    const event = events[index];
    if (event.source_type === "turn_start") {
      const turnEnd = events[index + 1];
      const snapshotCreated = events[index + 2];
      if (
        event.runtime_type !== "turn_started" ||
        !turnEnd || turnEnd.source_type !== "turn_end" || turnEnd.runtime_type !== "turn_finished" ||
        turnEnd.turn_id !== event.turn_id ||
        !snapshotCreated || snapshotCreated.source_type !== "turn_end" ||
        snapshotCreated.runtime_type !== "turn_snapshot_created" ||
        snapshotCreated.turn_id !== event.turn_id
      ) throw new Error(`${label} contains an incomplete or reordered turn projection`);
      turnIds.push(event.turn_id);
      index += 2;
    } else if (event.source_type === "turn_end") {
      throw new Error(`${label} contains an orphan turn projection`);
    }
  }
  return turnIds;
}

function customEntries(entries, customType) {
  return entries.filter((entry) => entry.type === "custom" && entry.customType === customType);
}

function reserveRepoForkId(repo, id) {
  if (id === undefined) return () => {};
  let reservations = REPO_FORK_ID_RESERVATIONS.get(repo);
  if (!reservations) {
    reservations = new Set();
    REPO_FORK_ID_RESERVATIONS.set(repo, reservations);
  }
  if (reservations.has(id)) throw new Error(`fork id is already reserved: ${id}`);
  reservations.add(id);
  let released = false;
  return () => {
    if (released) return;
    released = true;
    reservations.delete(id);
    if (reservations.size === 0) REPO_FORK_ID_RESERVATIONS.delete(repo);
  };
}

function validateAdapterHistory(branchInput) {
  const branch = validateOuterBranch(branchInput);
  const seenTurnIds = new Set();
  let previousSnapshotOrdinal = 0;
  let previousSavePointOrdinal = 0;
  let previousEventSequence = 0;
  let previousTurnId = null;
  let pendingSnapshots = [];
  let pendingBatch = null;

  for (const entry of branch) {
    if (entry.type !== "custom") continue;
    if (typeof entry.customType !== "string") throw new TypeError(`custom entry ${entry.id} has no customType`);
    if (!OWNED_CUSTOM_TYPES.has(entry.customType)) {
      if (entry.customType.startsWith("aaron.")) {
        throw new Error(`unrecognized adapter-owned custom entry type: ${entry.customType}`);
      }
      continue;
    }
    assertExactKeys(entry, ["type", "id", "parentId", "timestamp", "customType", "data"], `custom entry ${entry.id}`);
    if (!isPlainObject(entry.data)) throw new TypeError(`custom entry ${entry.id}.data must be a plain object`);

    if (entry.customType === CUSTOM_ENTRY_TYPES.turnSnapshot) {
      if (pendingBatch !== null) throw new Error("turn snapshot cannot follow an unsealed event batch");
      validateSnapshot(entry.data, `turn snapshot ${entry.id}`);
      if (entry.data.ordinal <= previousSnapshotOrdinal) throw new Error("snapshot ordinals must increase");
      if (seenTurnIds.has(entry.data.turn_id)) throw new Error(`duplicate snapshot turn: ${entry.data.turn_id}`);
      if (entry.data.parent_turn_id !== previousTurnId) throw new Error(`snapshot parent mismatch: ${entry.data.turn_id}`);
      previousSnapshotOrdinal = entry.data.ordinal;
      previousTurnId = entry.data.turn_id;
      seenTurnIds.add(entry.data.turn_id);
      pendingSnapshots.push(entry);
      continue;
    }

    if (entry.customType === CUSTOM_ENTRY_TYPES.runtimeEventBatch) {
      if (pendingBatch !== null) throw new Error("event batch must be sealed by one save point");
      previousEventSequence = validateEventBatch(entry.data, `event batch ${entry.id}`, previousEventSequence);
      pendingBatch = entry;
      continue;
    }

    if (pendingBatch === null) throw new Error("save point is missing its event batch");
    validateSavePoint(entry.data, `save point ${entry.id}`);
    if (entry.data.ordinal <= previousSavePointOrdinal) throw new Error("save-point ordinals must increase");
    const snapshotIds = pendingSnapshots.map((snapshot) => snapshot.id);
    if (
      entry.data.event_batch_entry_id !== pendingBatch.id ||
      entry.data.flushed_event_count !== pendingBatch.data.events.length ||
      entry.data.flushed_snapshot_count !== snapshotIds.length ||
      entry.data.snapshot_entry_ids.length !== snapshotIds.length ||
      entry.data.snapshot_entry_ids.some((id, index) => id !== snapshotIds[index])
    ) throw new Error(`save point ${entry.id} cross-reference mismatch`);

    const projectedTurnIds = deriveProjectedSnapshotTurns(
      pendingBatch.data.events,
      `event batch ${pendingBatch.id}`,
    );
    const snapshotTurnIds = pendingSnapshots.map((snapshot) => snapshot.data.turn_id);
    if (
      projectedTurnIds.length !== snapshotTurnIds.length ||
      projectedTurnIds.some((turnId, index) => turnId !== snapshotTurnIds[index])
    ) throw new Error(`save point ${entry.id} snapshot projections do not match stored snapshots`);
    previousSavePointOrdinal = entry.data.ordinal;
    pendingSnapshots = [];
    pendingBatch = null;
  }

  if (pendingSnapshots.length || pendingBatch !== null) throw new Error("adapter-owned history ends with an incomplete flush");
  return {
    branch,
    seenTurnIds,
    lastTurnId: previousTurnId,
    snapshotOrdinal: previousSnapshotOrdinal,
    eventSequence: previousEventSequence,
    savePointOrdinal: previousSavePointOrdinal,
  };
}

export class PiSessionRuntimeAdapter {
  #repo;
  #session;
  #activeTurn = null;
  #pendingEvents = [];
  #pendingSnapshots = [];
  #seenTurnIds = new Set();
  #lastTurnId = null;
  #eventSequence = 0;
  #snapshotOrdinal = 0;
  #savePointOrdinal = 0;
  #busyOperation = null;

  constructor(token, repo, session) {
    if (token !== INTERNAL_CONSTRUCTION_TOKEN) {
      throw new TypeError("PiSessionRuntimeAdapter constructor is internal; use create()");
    }
    if (Object.getPrototypeOf(repo) !== InMemorySessionRepo.prototype) {
      throw new TypeError("adapter requires its internally owned exact InMemorySessionRepo");
    }
    this.#repo = repo;
    this.#session = session;
  }

  static async create(options) {
    const { id = "pi-poc-session" } = copyAllowedOptions(options, ["id"], "create options");
    assertSafeId(id, "session id");
    const repo = new InMemorySessionRepo();
    const session = await repo.create({ id });
    return PiSessionRuntimeAdapter.#fromSession(repo, session);
  }

  static async #fromSession(repo, session) {
    if (Object.getPrototypeOf(repo) !== InMemorySessionRepo.prototype) {
      throw new TypeError("adapter requires its internally owned exact InMemorySessionRepo");
    }
    const metadata = clonePlainData(await session.getMetadata(), "Pi session metadata");
    const opened = await repo.open(metadata);
    if (opened !== session) throw new Error("Pi repo/session identity mismatch");
    const adapter = new PiSessionRuntimeAdapter(INTERNAL_CONSTRUCTION_TOKEN, repo, session);
    await adapter.#hydrateFromBranch();
    return adapter;
  }

  async #withOperation(operation, callback) {
    if (this.#busyOperation !== null) {
      throw new Error(`${operation} rejected while ${this.#busyOperation} is in progress`);
    }
    this.#busyOperation = operation;
    try {
      return await callback();
    } finally {
      this.#busyOperation = null;
    }
  }

  #assertReadable(operation) {
    if (this.#busyOperation !== null) {
      throw new Error(`${operation} rejected while ${this.#busyOperation} is in progress`);
    }
  }

  async #hydrateFromBranch() {
    const state = validateAdapterHistory(await this.#session.getBranch());
    this.#seenTurnIds = state.seenTurnIds;
    this.#lastTurnId = state.lastTurnId;
    this.#snapshotOrdinal = state.snapshotOrdinal;
    this.#eventSequence = state.eventSequence;
    this.#savePointOrdinal = state.savePointOrdinal;
  }

  async #validateSavePointBoundary(entryId, operation) {
    let state;
    try {
      state = validateAdapterHistory(await this.#session.getBranch(entryId));
    } catch (error) {
      throw new Error(`${operation} target must be a fully validated adapter save-point boundary`, {
        cause: error,
      });
    }
    const target = state.branch.at(-1);
    if (
      !target || target.id !== entryId || target.type !== "custom" ||
      target.customType !== CUSTOM_ENTRY_TYPES.savePoint
    ) throw new Error(`${operation} target must be a fully validated adapter save-point boundary`);
    return state;
  }

  #stageRuntimeEvent(sourceType, { turnId = null, oldLeafId = null, newLeafId = null, runtimeType } = {}) {
    this.#eventSequence += 1;
    const projected = immutableCopy({
      sequence: this.#eventSequence,
      source_type: sourceType,
      runtime_type: runtimeType ?? PI_TO_RUNTIME_EVENT[sourceType],
      turn_id: turnId,
      old_leaf_id: oldLeafId,
      new_leaf_id: newLeafId,
    }, "runtime event");
    validateProjectedEvent(projected, "runtime event");
    this.#pendingEvents.push(projected);
    return projected;
  }

  #assertCleanBoundary(operation) {
    if (this.#activeTurn !== null || this.#pendingEvents.length || this.#pendingSnapshots.length) {
      throw new Error(`${operation} requires a completed save_point flush`);
    }
  }

  async accept(input) {
    const event = validateSyntheticPiEvent(input);
    return this.#withOperation("accept", () => this.#acceptCanonical(event));
  }

  async #acceptCanonical(event) {
    if (event.type === "turn_start") {
      if (this.#activeTurn !== null) throw new Error("a turn is already active");
      if (this.#seenTurnIds.has(event.turnId)) throw new Error(`turn already snapshotted: ${event.turnId}`);
      this.#activeTurn = {
        turnId: event.turnId,
        parentTurnId: this.#lastTurnId,
        firstEventIndex: this.#pendingEvents.length,
      };
      this.#stageRuntimeEvent(event.type, { turnId: event.turnId });
      return expose({ staged: true });
    }

    if (event.type === "turn_end") {
      if (this.#activeTurn === null || this.#activeTurn.turnId !== event.turnId) {
        throw new Error("turn_end must match the active turn");
      }
      this.#stageRuntimeEvent(event.type, { turnId: event.turnId });
      const turnEvents = this.#pendingEvents.slice(this.#activeTurn.firstEventIndex);
      this.#snapshotOrdinal += 1;
      const snapshot = immutableCopy(withProjectionHash({
        schema_version: 1,
        ordinal: this.#snapshotOrdinal,
        turn_id: event.turnId,
        parent_turn_id: this.#activeTurn.parentTurnId,
        source_event_types: turnEvents.map((item) => item.source_type),
        runtime_event_types: turnEvents.map((item) => item.runtime_type),
      }), "turn snapshot");
      validateSnapshot(snapshot, "turn snapshot");
      this.#pendingSnapshots.push(snapshot);
      this.#stageRuntimeEvent("turn_end", { turnId: event.turnId, runtimeType: "turn_snapshot_created" });
      this.#seenTurnIds.add(event.turnId);
      this.#lastTurnId = event.turnId;
      this.#activeTurn = null;
      return expose({ staged: true, snapshot });
    }

    if (event.type === "save_point") {
      if (this.#activeTurn !== null) throw new Error("save_point cannot split an active turn");
      const hadPendingMutations = this.#pendingEvents.length > 0 || this.#pendingSnapshots.length > 0;
      if (event.hadPendingMutations !== hadPendingMutations) {
        throw new Error(
          `save_point hadPendingMutations mismatch: expected ${hadPendingMutations}, got ${event.hadPendingMutations}`,
        );
      }
      this.#stageRuntimeEvent(event.type);
      return this.#flush();
    }

    if (event.type === "session_tree") {
      if (this.#activeTurn !== null) throw new Error("session_tree cannot split an active turn");
      this.#stageRuntimeEvent(event.type, { oldLeafId: event.oldLeafId, newLeafId: event.newLeafId });
      return expose({ staged: true });
    }

    if (this.#activeTurn !== null) {
      throw new Error(`${event.type} cannot occur during an active turn in this PoC`);
    }
    this.#stageRuntimeEvent(event.type);
    return expose({ staged: true });
  }

  async #flush() {
    const snapshotEntryIds = [];
    for (const snapshot of this.#pendingSnapshots) {
      snapshotEntryIds.push(await this.#session.appendCustomEntry(
        CUSTOM_ENTRY_TYPES.turnSnapshot,
        immutableCopy(snapshot, "stored turn snapshot"),
      ));
    }

    const eventBatch = immutableCopy(withProjectionHash({
      schema_version: 1,
      events: this.#pendingEvents.map((event) => clonePlainData(event, "pending event")),
    }), "runtime event batch");
    const eventBatchEntryId = await this.#session.appendCustomEntry(
      CUSTOM_ENTRY_TYPES.runtimeEventBatch,
      immutableCopy(eventBatch, "stored runtime event batch"),
    );

    this.#savePointOrdinal += 1;
    const savePoint = immutableCopy(withProjectionHash({
      schema_version: 1,
      ordinal: this.#savePointOrdinal,
      event_batch_entry_id: eventBatchEntryId,
      snapshot_entry_ids: [...snapshotEntryIds],
      flushed_event_count: this.#pendingEvents.length,
      flushed_snapshot_count: this.#pendingSnapshots.length,
    }), "save point");
    const savePointEntryId = await this.#session.appendCustomEntry(
      CUSTOM_ENTRY_TYPES.savePoint,
      immutableCopy(savePoint, "stored save point"),
    );

    this.#pendingEvents = [];
    this.#pendingSnapshots = [];
    return expose({
      flushed: true,
      eventBatchEntryId,
      savePointEntryId,
      snapshotEntryIds,
      savePoint,
    });
  }

  async moveTo(entryId) {
    assertSafeId(entryId, "entryId");
    return this.#withOperation("moveTo", async () => {
      this.#assertCleanBoundary("moveTo");
      const targetState = await this.#validateSavePointBoundary(entryId, "moveTo");
      const oldLeafId = await this.#session.getLeafId();
      await this.#session.moveTo(entryId);
      this.#lastTurnId = targetState.lastTurnId;
      await this.#acceptCanonical({ type: "session_tree", oldLeafId, newLeafId: entryId });
      return expose({ oldLeafId, newLeafId: entryId });
    });
  }

  async forkAt(entryId, options) {
    assertSafeId(entryId, "entryId");
    const copiedOptions = copyAllowedOptions(options, ["id"], "fork options");
    if (copiedOptions.id !== undefined) assertSafeId(copiedOptions.id, "fork id");
    return this.#withOperation("forkAt", async () => {
      this.#assertCleanBoundary("forkAt");
      await this.#validateSavePointBoundary(entryId, "forkAt");
      const releaseForkId = reserveRepoForkId(this.#repo, copiedOptions.id);
      try {
        if (copiedOptions.id !== undefined) {
          const listed = clonePlainData(await this.#repo.list(), "Pi repo metadata list");
          if (!Array.isArray(listed)) throw new TypeError("Pi repo metadata list must be an array");
          for (const [index, item] of listed.entries()) {
            if (!isPlainObject(item)) throw new TypeError(`Pi repo metadata[${index}] must be a plain object`);
            assertSafeId(item.id, `Pi repo metadata[${index}].id`);
            if (item.id === copiedOptions.id) throw new Error(`fork id already exists: ${copiedOptions.id}`);
          }
        }
        const metadata = clonePlainData(await this.#session.getMetadata(), "Pi session metadata");
        const forked = await this.#repo.fork(metadata, { entryId, position: "at", id: copiedOptions.id });
        return PiSessionRuntimeAdapter.#fromSession(this.#repo, forked);
      } finally {
        releaseForkId();
      }
    });
  }

  get pendingMutationCount() {
    this.#assertReadable("pendingMutationCount");
    return this.#pendingEvents.length + this.#pendingSnapshots.length;
  }

  async metadata() {
    return this.#withOperation(
      "metadata",
      async () => expose(await this.#session.getMetadata(), "Pi session metadata"),
    );
  }

  async entries() {
    return this.#withOperation(
      "entries",
      async () => expose(await this.#session.getEntries(), "Pi session entries"),
    );
  }

  async branch() {
    return this.#withOperation(
      "branch",
      async () => expose(await this.#session.getBranch(), "Pi session branch"),
    );
  }
}
