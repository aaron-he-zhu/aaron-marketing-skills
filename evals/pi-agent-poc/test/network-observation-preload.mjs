import childProcess from "node:child_process";
import http from "node:http";
import https from "node:https";
import { syncBuiltinESMExports } from "node:module";
import net from "node:net";

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
childProcess.exec = block("child_process.exec");
childProcess.execFile = block("child_process.execFile");
childProcess.spawn = block("child_process.spawn");
childProcess.fork = block("child_process.fork");
syncBuiltinESMExports();
