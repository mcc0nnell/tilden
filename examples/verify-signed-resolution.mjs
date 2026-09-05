import { readFile } from "node:fs/promises";
import { webcrypto } from "node:crypto";

const { subtle } = webcrypto;

const decodeBase64url = (value) =>
  Buffer.from(value.replace(/-/g, "+").replace(/_/g, "/"), "base64");

const [delegation, signed, expectedResolution] = await Promise.all([
  readFile(new URL("./authority-delegation.json", import.meta.url), "utf8").then(JSON.parse),
  readFile(new URL("./signed-resolution.jws.json", import.meta.url), "utf8").then(JSON.parse),
  readFile(new URL("./resolution.json", import.meta.url), "utf8").then(JSON.parse),
]);

const protectedHeader = JSON.parse(decodeBase64url(signed.protected).toString("utf8"));

if (protectedHeader.alg !== "Ed25519") {
  throw new Error(`unexpected alg: ${protectedHeader.alg}`);
}
if (protectedHeader.typ !== "tilden-resolution+jws") {
  throw new Error(`unexpected typ: ${protectedHeader.typ}`);
}
if (protectedHeader.cty !== "application/tilden+json") {
  throw new Error(`unexpected cty: ${protectedHeader.cty}`);
}

const key = delegation.signing_keys.find(({ kid }) => kid === protectedHeader.kid);
if (!key) {
  throw new Error(`delegation does not authorize kid ${protectedHeader.kid}`);
}
if (key.alg !== "Ed25519" || key.kty !== "OKP" || key.crv !== "Ed25519") {
  throw new Error("delegated key is not compatible with the SIGN-004 Ed25519 profile");
}

const publicKey = await subtle.importKey(
  "jwk",
  { kty: key.kty, crv: key.crv, x: key.x },
  { name: "Ed25519" },
  false,
  ["verify"],
);

const signingInput = Buffer.from(`${signed.protected}.${signed.payload}`, "ascii");
const signature = decodeBase64url(signed.signature);

const valid = await subtle.verify("Ed25519", publicKey, signature, signingInput);
if (!valid) {
  throw new Error("SIGN-004 reference signature did not verify");
}

const decodedResolution = JSON.parse(decodeBase64url(signed.payload).toString("utf8"));
if (JSON.stringify(decodedResolution) !== JSON.stringify(expectedResolution)) {
  throw new Error("signed payload does not match examples/resolution.json");
}

if (decodedResolution.subject !== `tel:${delegation.scope.prefix}`) {
  throw new Error("signed subject is outside the example delegation scope");
}
if (decodedResolution.authority !== delegation.resolver) {
  throw new Error("signed authority does not match the delegated resolver");
}

const tamperedInput = Buffer.from(signingInput);
tamperedInput[tamperedInput.length - 1] ^= 1;
const tamperedValid = await subtle.verify("Ed25519", publicKey, signature, tamperedInput);
if (tamperedValid) {
  throw new Error("tampered signing input unexpectedly verified");
}

console.log("SIGN-004 reference vector verified");
console.log(`subject: ${decodedResolution.subject}`);
console.log(`authority: ${decodedResolution.authority}`);
console.log(`kid: ${protectedHeader.kid}`);
console.log("tamper check: rejected as expected");
