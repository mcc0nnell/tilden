const MEDIA_TYPE = "application/tilden+json";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "GET" && url.pathname === "/health") {
      return json({ ok: true, service: "tilden-reference-resolver" }, 200);
    }

    if (request.method !== "POST" || url.pathname !== "/tilden/v1/resolve") {
      return tildenError("not-found", "No such Tilden resolver resource.", 404);
    }

    if (!env.TILDEN_SIGNING_SECRET) {
      return tildenError(
        "resolver-misconfigured",
        "Resolver signing material is not configured.",
        503,
      );
    }

    let input;
    try {
      input = await request.json();
    } catch {
      return tildenError("invalid-request", "Request body must be JSON.", 400);
    }

    const validationError = validateRequest(input);
    if (validationError) {
      return tildenError("invalid-request", validationError, 400);
    }

    let routes;
    try {
      routes = JSON.parse(env.TILDEN_ROUTES || "{}");
    } catch {
      return tildenError(
        "resolver-misconfigured",
        "TILDEN_ROUTES is not valid JSON.",
        503,
      );
    }

    const record = routes[input.identifier];
    if (!record) {
      return tildenError(
        "not-found",
        "No routable Tilden record is available for this identifier.",
        404,
      );
    }

    const now = new Date();
    const expires = new Date(now.getTime() + 5 * 60 * 1000);

    const unsigned = {
      version: "0.1",
      identifier: input.identifier,
      requestId: input.requestId || null,
      issuedAt: now.toISOString(),
      expiresAt: expires.toISOString(),
      endpoints: selectCompatibleEndpoints(record.endpoints || [], input.capabilities),
      authority: {
        delegationSequence: Number(record.delegationSequence || 0),
        verificationMethod:
          record.verificationMethod || "urn:tilden:demo:hmac-sha256",
      },
    };

    if (unsigned.endpoints.length === 0) {
      return tildenError(
        "unsupported-capability",
        "The identifier has routes, but none match the supplied capabilities.",
        406,
      );
    }

    const proofValue = await sign(unsigned, env.TILDEN_SIGNING_SECRET);

    return json(
      {
        ...unsigned,
        proof: {
          type: "TildenDemoHmacSha256",
          verificationMethod: unsigned.authority.verificationMethod,
          created: now.toISOString(),
          proofValue,
        },
      },
      200,
      { "Cache-Control": "private, max-age=60" },
    );
  },
};

function validateRequest(input) {
  if (!input || typeof input !== "object" || Array.isArray(input)) {
    return "Request body must be an object.";
  }

  if (input.version !== "0.1") {
    return "Only Tilden request version 0.1 is supported by this reference resolver.";
  }

  if (typeof input.identifier !== "string") {
    return "identifier is required.";
  }

  if (!/^tel:\+[1-9][0-9]{6,14}$/.test(input.identifier)) {
    return "identifier must be a normalized tel:+ E.164-style identifier.";
  }

  return null;
}

function selectCompatibleEndpoints(endpoints, capabilities) {
  if (!capabilities || typeof capabilities !== "object") {
    return [...endpoints].sort(byPriority);
  }

  const requestedProtocols = new Set(capabilities.protocols || []);
  const requestedMedia = new Set(capabilities.media || []);
  const requestedFeatures = new Set(capabilities.features || []);

  return endpoints
    .filter((endpoint) => {
      if (
        requestedProtocols.size > 0 &&
        !requestedProtocols.has(endpoint.protocol)
      ) {
        return false;
      }

      const offered = new Set(endpoint.capabilities || []);

      if (
        requestedMedia.size > 0 &&
        ![...requestedMedia].some((capability) => offered.has(capability))
      ) {
        return false;
      }

      if (
        requestedFeatures.size > 0 &&
        ![...requestedFeatures].every((capability) => offered.has(capability))
      ) {
        return false;
      }

      return true;
    })
    .sort(byPriority);
}

function byPriority(a, b) {
  return Number(a.priority || 100) - Number(b.priority || 100);
}

async function sign(value, secret) {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"],
  );

  const bytes = encoder.encode(stableStringify(value));
  const signature = await crypto.subtle.sign("HMAC", key, bytes);
  return base64url(new Uint8Array(signature));
}

function stableStringify(value) {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }

  if (Array.isArray(value)) {
    return `[${value.map(stableStringify).join(",")}]`;
  }

  return `{${Object.keys(value)
    .sort()
    .map((key) => `${JSON.stringify(key)}:${stableStringify(value[key])}`)
    .join(",")}}`;
}

function base64url(bytes) {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/g, "");
}

function tildenError(error, message, status) {
  return json({ version: "0.1", error, message }, status);
}

function json(body, status = 200, headers = {}) {
  return new Response(JSON.stringify(body, null, 2), {
    status,
    headers: {
      "Content-Type": MEDIA_TYPE,
      "X-Content-Type-Options": "nosniff",
      ...headers,
    },
  });
}
