import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const readJson = (name) => JSON.parse(readFileSync(resolve(here, name), 'utf8'));

const resolution = readJson('resolution.json');
const descriptor = readJson('baudot-service.json');

function invariant(condition, message) {
  if (!condition) throw new Error(message);
}

function setIntersection(a = [], b = []) {
  const right = new Set(b);
  return a.filter((value) => right.has(value));
}

function validateBinding(parent, service, now = new Date('2026-09-05T21:02:00Z')) {
  const baudot = parent.capabilities.find((capability) => capability.type === 'baudot');
  invariant(baudot, 'baudot capability is required');
  invariant(new URL(baudot.uri).protocol === 'https:', 'baudot capability URI must use HTTPS');
  invariant(service.subject === parent.subject, 'descriptor subject must match parent Tilden subject');
  invariant(service.service_uri === baudot.uri, 'descriptor service_uri must match signed baudot capability URI');
  invariant(new URL(service.service_uri).origin === new URL(baudot.uri).origin, 'descriptor origin must remain bound to the signed service origin');

  const issued = new Date(service.issued_at);
  const expires = new Date(service.expires_at);
  invariant(Number.isFinite(issued.valueOf()) && Number.isFinite(expires.valueOf()), 'descriptor timestamps must parse');
  invariant(now >= issued, 'descriptor must not be used before issued_at');
  invariant(now < expires, 'descriptor must not be expired');
  invariant(expires <= new Date(parent.expires_at), 'descriptor must not outlive the parent resolution vector');

  const effective = service.transports.map((transport) => ({
    ...transport,
    effective_media: setIntersection(baudot.media, transport.media),
    effective_features: setIntersection(baudot.features, transport.features),
  }));

  return { baudot, effective };
}

function satisfies(transport, requiredMedia, requiredFeatures) {
  return requiredMedia.every((item) => transport.effective_media.includes(item))
    && requiredFeatures.every((item) => transport.effective_features.includes(item));
}

function selectTransport(parent, service, requirements) {
  const { effective } = validateBinding(parent, service);
  return effective
    .filter((transport) => satisfies(transport, requirements.media, requirements.features))
    .sort((a, b) => a.priority - b.priority)[0] ?? null;
}

function rttReady(observation) {
  return observation.rttNegotiated === true
    && observation.firstT140CharacterObserved === true;
}

const requirements = {
  media: ['video', 'rtt'],
  features: ['asl', 't140'],
};

const selected = selectTransport(resolution, descriptor, requirements);
invariant(selected?.id === 'sip-total-conversation', 'lowest-priority compatible transport should be selected');
invariant(selected.profiles.includes('t140-rfc4103'), 'selected SIP vector should advertise RFC 4103 T.140');

const expanded = structuredClone(descriptor);
expanded.transports[0].media.push('message');
expanded.transports[0].features.push('untrusted-extra-feature');
const expandedSelection = selectTransport(resolution, expanded, requirements);
invariant(!expandedSelection.effective_media.includes('message'), 'descriptor must not expand signed media');
invariant(!expandedSelection.effective_features.includes('untrusted-extra-feature'), 'descriptor must not expand signed features');

const wrongSubject = structuredClone(descriptor);
wrongSubject.subject = 'tel:+12025550999';
let subjectRejected = false;
try {
  validateBinding(resolution, wrongSubject);
} catch (error) {
  subjectRejected = /subject/.test(error.message);
}
invariant(subjectRejected, 'subject-mismatch vector must be rejected');

const signalingOnly = {
  rttNegotiated: true,
  firstT140CharacterObserved: false,
};
invariant(rttReady(signalingOnly) === false, 'RTT negotiation alone must not produce rttReady');

const observedRtt = {
  rttNegotiated: true,
  firstT140CharacterObserved: true,
};
invariant(rttReady(observedRtt) === true, 'observed T.140 after negotiation should satisfy reference RTT readiness');

const pstn = resolution.capabilities.find((capability) => capability.type === 'pstn');
invariant(pstn, 'reference resolution must contain PSTN fallback');
invariant(!pstn.media.includes('rtt'), 'reference PSTN fallback intentionally lacks RTT');
const silentDowngradeAllowed = requirements.media.every((required) => pstn.media.includes(required));
invariant(silentDowngradeAllowed === false, 'audio-only PSTN must not silently satisfy video+RTT requirements');

console.log('PASS parent Baudot capability -> descriptor binding');
console.log(`PASS compatible transport selection -> ${selected.id}`);
console.log('PASS dynamic descriptor cannot expand signed media/features');
console.log('PASS subject mismatch rejected');
console.log('PASS signaling-only RTT remains not ready');
console.log('PASS negotiated + observed T.140 satisfies reference RTT readiness');
console.log('PASS video+RTT policy blocks silent audio-only PSTN downgrade');
