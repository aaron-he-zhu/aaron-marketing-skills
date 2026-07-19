import childProcess from "node:child_process";
import dgram from "node:dgram";
import dns from "node:dns";
import http from "node:http";
import https from "node:https";
import { syncBuiltinESMExports } from "node:module";
import net from "node:net";
import tls from "node:tls";
import workerThreads from "node:worker_threads";

const attempts = [];
const block = (surface) => (..._args) => {
  attempts.push(surface);
  throw new Error(`network/process observation blocked ${surface}`);
};

Object.defineProperty(globalThis, "__piPocObservedAttempts", {
  configurable: false,
  enumerable: false,
  writable: false,
  value: attempts,
});
Object.defineProperty(globalThis, "fetch", {
  configurable: true,
  enumerable: true,
  writable: true,
  value: block("fetch"),
});
http.request = block("http.request");
http.get = block("http.get");
https.request = block("https.request");
https.get = block("https.get");
net.connect = block("net.connect");
net.createConnection = block("net.createConnection");
tls.connect = block("tls.connect");
dgram.createSocket = block("dgram.createSocket");
dns.lookup = block("dns.lookup");
dns.resolve = block("dns.resolve");
dns.resolve4 = block("dns.resolve4");
dns.resolve6 = block("dns.resolve6");
childProcess.exec = block("child_process.exec");
childProcess.execFile = block("child_process.execFile");
childProcess.execSync = block("child_process.execSync");
childProcess.execFileSync = block("child_process.execFileSync");
childProcess.spawn = block("child_process.spawn");
childProcess.spawnSync = block("child_process.spawnSync");
childProcess.fork = block("child_process.fork");
workerThreads.Worker = block("worker_threads.Worker");
syncBuiltinESMExports();
