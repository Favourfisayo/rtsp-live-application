# Backend Security Instructions

**RTSP Livestream Overlay Backend**

## Security Context

This is a **single-user internal tool**, not a public SaaS.

Security goals:

* Prevent command injection
* Prevent arbitrary network access abuse
* Protect system resources
* Fail safely on malformed inputs

We prioritize **process safety and input control** over user auth complexity.

---

## 1. Authentication & Access

* If exposed beyond localhost:

  * Use a single shared access token
* No password systems unless explicitly required
* No user accounts by default

Security through clarity, not ceremony.

---

## 2. RTSP-Specific Threat Model (Critical)

### Command Injection Prevention

* **NEVER** interpolate RTSP URLs into shell commands
* Use argument arrays when invoking ffmpeg/gstreamer
* Validate RTSP URLs strictly before use
* Disallow:

  * `;`
  * `|`
  * backticks
  * `$()`

RTSP URLs are attacker-controlled input. Treat them as hostile.

---

## 3. Network Security

* Prevent SSRF-style abuse:

  * Allow RTSP only
  * Optional allowlist for IP ranges
* Do not allow arbitrary protocol forwarding
* Enforce connection timeouts

---

## 4. Input Validation (Security-Focused)

* Validate:

  * RTSP URLs
  * Overlay text length
  * Image URLs (protocol + length)
* Enforce max payload sizes
* Reject oversized overlay content

---

## 5. Process & Resource Protection

* Limit concurrent ffmpeg processes to 1
* Enforce CPU/memory limits if containerized
* Kill child processes on server shutdown
* Watchdog streaming processes

---

## 6. API Security

* Rate limit:

  * Stream start/stop endpoints
  * Overlay creation
* Reject invalid content types
* Enforce JSON schema strictly

---

## 7. Logging (Minimal & Safe)

* Log:

  * Stream state changes
  * Errors
* Never log:

  * Full RTSP URLs (mask credentials)
  * Command arguments
* Logs must not expose system paths

---

## 8. File & Image Security

* If loading external images:

  * Validate URL scheme
  * Enforce size limits
  * Disallow local file paths
* Never proxy arbitrary files to the client

---

## 9. Deployment Safety

* Run backend as non-root
* Use minimal container images
* Disable unused ports
* Enforce HTTPS if exposed externally

---

## 10. Security Red Flags (Immediate Stop)

🚨 Shell interpolation with user input
🚨 Arbitrary protocol support (`file://`, `http://` for streams)
🚨 Multiple unmanaged ffmpeg processes
🚨 Unbounded overlay payload sizes

---

## Notes for AI Agent

* RTSP input is the primary attack vector
* Streaming processes are the primary risk surface
* When unsure, reject input and log
* Stability beats features every time
* Only add high-level comments, that describes the code block, what it does and how it's used, and prevent verbose nested comments.