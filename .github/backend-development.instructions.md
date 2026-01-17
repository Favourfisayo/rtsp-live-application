# Backend Development Instructions

**RTSP Livestream Overlay Backend**

## System Context (Read First)

This backend powers a **single-user RTSP livestream overlay tool**.

Core responsibilities:

* Accept and validate RTSP stream URLs
* Control stream lifecycle (connect, disconnect, status)
* Manage overlay entities (text/image overlays, position, size)
* Expose APIs for real-time overlay updates
* Maintain low latency and predictable behavior

This is a **modular monolith**, not microservices.

---

## Core Principles (Non-Negotiable)

### 1. Architecture & Boundaries

* Use **modular monolith architecture**
* Separate modules clearly:

  * `rtsp` → stream lifecycle & status
  * `overlays` → CRUD + positioning
  * `api` → HTTP/WebSocket handlers
* No cross-module access except via explicit interfaces
* No business logic in controllers

**Allowed architectures:**

* Clean Architecture
* Hexagonal Architecture
* Layered Architecture

---

### 2. Project-Specific Folder Structure

```
src/
├── api/
│   ├── http/               # REST controllers
│   ├── ws/                 # WebSocket handlers (if used)
│   └── middleware/
├── modules/
│   ├── rtsp/
│   │   ├── rtsp.controller.ts
│   │   ├── rtsp.service.ts
│   │   ├── rtsp.manager.ts     # stream lifecycle control
│   │   └── rtsp.types.ts
│   ├── overlays/
│   │   ├── overlay.controller.ts
│   │   ├── overlay.service.ts
│   │   ├── overlay.model.ts
│   │   └── overlay.types.ts
├── infrastructure/
│   ├── persistence/        # DB access
│   ├── cache/              # Redis / in-memory
│   └── streaming/          # RTSP -> webRTC adapter
├── utils/
├── validators/
```

**Rules**

* No shared “utils” that hide business logic
* Streaming logic must live under `infrastructure/streaming`
* Controllers are thin. Services decide.

---

### 3. Data Model (Overlay-First)

Overlays are **stateful UI objects**, not static content.

Overlay entity must minimally include:

* `id`
* `type` (`text | image`)
* `content` (text or image URL)
* `x`, `y` (normalized or pixel coordinates)
* `width`, `height`
* `zIndex`
* `visible`
* `createdAt`, `updatedAt`

RTSP stream state must include:

* `status` (`idle | connecting | live | error`)
* `lastError`
* `startedAt`

---

### 4. API Design (Low-Latency Bias)

#### REST for:

* Overlay CRUD
* Stream control (start / stop)
* State retrieval

#### WebSocket (or SSE) for:

* Live overlay updates
* Stream status updates

**Never poll for real-time state if push is feasible.**

---

### 5. Input Validation (Strict)

* Validate **all** external input
* RTSP URLs:

  * Must start with `rtsp://`
  * Length capped
  * No shell-interpolated usage
* Overlay positions:

  * Enforce numeric bounds
  * Reject NaN, Infinity
* Use schema validation at **API boundary only**

Fail fast. No silent coercion.

---

### 6. Error Handling Rules

* RTSP failures must return:

  * Clear message
  * Stream status updated internally
* Never crash the process on stream failure
* Streaming errors are **expected**, not exceptional

Example:

```json
{
  "success": false,
  "error": {
    "code": "RTSP_CONNECTION_FAILED",
    "message": "Unable to connect to RTSP stream"
  }
}
```

---

### 7. Streaming Lifecycle Rules

* Only one active RTSP stream at a time
* Starting a new stream **must stop the previous one**
* Stream state must be centralized (single source of truth)
* ffmpeg/gstreamer processes must:

  * Be tracked
  * Be killable
  * Never orphaned

No zombie processes. Ever.

---

### 8. Persistence Strategy

* Overlays: persistent (DB or file-based storage)
* Stream state: ephemeral (memory)
* Never persist transient stream errors
* DB is not in the hot path for frame rendering

---

### 9. Performance Rules

* Overlay updates must be lightweight
* No DB writes on every drag event
* Use debouncing or explicit “save” semantics
* Streaming thread/process must not block API threads

Latency > abstraction purity. Always.

---

### 10. Testing (Practical)

* Unit test:

  * Overlay services
  * Stream state transitions
* Integration test:

  * API endpoints
* Do NOT attempt to fully test RTSP streams in CI
* Mock streaming adapters

---

### 11. Explicit Anti-Patterns

❌ Treating overlays as static CMS data
❌ Writing overlay updates on every mouse move
❌ Streaming logic inside controllers
❌ Restarting ffmpeg on every API call
❌ Multi-tenant assumptions

---

### Notes for AI Agent

* This is a **tool**, not a platform
* Optimize for predictability, not scale theater
* If something increases latency or complexity, question it
* Streaming failures are normal; crashes are not
* Only add high-level comments, that describes the code block, what it does and how it's used, and prevent verbose nested comments.