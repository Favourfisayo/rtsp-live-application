---
applyTo: '**'
---

# Project / Feature Context & Specifications

## Metadata

* **Project Name:** RTSP Livestream Overlay Web Application
* **Version:** v1.0.0
* **Timeline:**

  * Start Date: 2026-01-15
  * Expected Completion: 2026-01-16 (before 1:00 PM)
* **Development Methodology:** Waterfall (Requirements → Design → Implementation → Demo)
* **Priority Level:** Medium

---

## Project Overview

### Description

The system is a web-based RTSP livestream player with real-time overlay management.

At its core, the application allows a user to:

* Play a livestream sourced from a user-provided RTSP URL
* Convert RTSP streams into a browser-compatible format (HLS or WebRTC)
* Add, move, resize, and manage overlays (text or image) on top of the video
* Persist overlay configurations using backend APIs and MongoDB
* Modify overlays in real time while the livestream is playing

This is a **single-user, interactive web application** intended for local execution and demonstration purposes. It is **not** a broadcast or multi-user streaming platform.

---

### Goals & Objectives

**Primary Goals**

* Enable RTSP livestream playback inside a web browser
* Allow users to create and manage real-time overlays on top of the livestream

**Secondary Goals**

* Persist overlay configurations via backend APIs
* Maintain a clean, modular architecture that is easy to reason about and document

---

### Scope

**In Scope**

* RTSP stream ingestion and conversion to a browser-supported protocol
* Embedded video player with basic controls (play, pause, volume)
* Overlay creation, update, deletion, and persistence
* Drag-and-drop and resizable overlays
* REST APIs for overlay management
* Local development setup with documentation and demo video

**Out of Scope**

* User authentication or authorization
* Multi-user or collaborative editing
* Production-grade streaming infrastructure
* Overlay animations or transitions
* Advanced video editing features

---

## Target Users

### Primary Users

* **User Type:** Single end user (developer / evaluator)

  * Technical proficiency: Medium
  * Goals:

    * Play an RTSP livestream
    * Add and manage overlays visually
  * Pain Points:

    * RTSP streams not natively supported by browsers
    * Need for real-time overlay interaction

### Secondary Users

* None (single-user system)

---

## Technical Specifications

### Tech Stack

**Frontend**

* Framework: React 18.x
* Language: JavaScript (ES2023)
* State Management: React local state (no global store required)
* Styling: Tailwind CSS (simple, utility-based styling)
* Build Tool: Vite
* Additional Libraries:

  * Drag & resize utility (e.g. react-draggable / react-resizable)

**Backend**

* Runtime / Language: Python 3.12.7
* Framework: Flask
* Database: MongoDB
* ODM: PyMongo
* Authentication: None
* Additional Services:

  * RTSP conversion tool (figure out the best one to use)

**Infrastructure**

* Hosting: Localhost (development only)
* CI/CD: Not required
* Containerization: Optional (Docker not required)
* Monitoring: Not required

---

### Architecture Pattern

* **Modular Monolith**

  * Single Flask application
  * Internally divided into feature-based modules:

    * RTSP module
    * Overlay module

This structure balances simplicity with clear separation of concerns.

---

### Database Schema

**Overlay (MongoDB Collection)**
Fields:

* `_id` (ObjectId)
* `type` (string: "text" | "image")
* `content` (string: text value or image URL)
* `position`:

  * `x` (number)
  * `y` (number)
* `size`:

  * `width` (number)
  * `height` (number)
* `created_at` (timestamp)
* `updated_at` (timestamp)

RTSP stream data does not require persistent storage.

---

### API Specifications

* **API Type:** REST
* **API Version:** v1
* **Base URL:** `http://localhost:5000/api`
* **Authentication:** None

**Key Endpoints**

**RTSP**

* `POST /rtsp/start`
  Purpose: Accept RTSP URL and return a browser-compatible stream URL

**Overlay**

* `POST /overlays` – Create overlay
* `GET /overlays` – Fetch all overlays
* `PUT /overlays/{id}` – Update overlay
* `DELETE /overlays/{id}` – Delete overlay

---

### Third-Party Integrations

* Figure out some tool for RTSP to WebRTC stream conversion

---

## Functional Requirements

### Core Features

1. **RTSP Livestream Playback**

   * Description: Play a livestream from a user-provided RTSP URL
   * User Story:
     As a user, I want to provide an RTSP URL so that I can watch the livestream in my browser.
   * Acceptance Criteria:

     * RTSP URL can be submitted from the UI
     * Stream plays using a browser-supported protocol
     * Play, pause, and volume controls work

2. **Overlay Management**

   * Description: Create and manage text and image overlays on top of the livestream
   * User Story:
     As a user, I want to add overlays so that information appears on top of the video.
   * Acceptance Criteria:

     * Overlays can be created, moved, resized, and deleted
     * Overlay changes appear immediately
     * Overlay state persists across reloads

---

### Business Rules

* Overlays are independent of RTSP stream lifecycle
* No authentication or user accounts are required
* Only one active stream is required at a time

---

## Non-Functional Requirements

### Performance

* UI interactions (drag/resize) must feel responsive
* API response time should be under 500ms locally

### Scalability

* Not required beyond single-user usage

### Availability

* Local development availability only

### Security

* No sensitive data stored
* RTSP URLs handled server-side only

### Accessibility

* Basic keyboard navigation
* Proper alt text for images
* Semantic HTML usage

### Internationalization

* Not required

---

## User Experience & Behavior

### User Flows

**Livestream + Overlay Flow**

1. User opens application
2. User enters RTSP URL
3. User starts livestream
4. User adds overlay
5. User moves/resizes overlay
6. Overlay updates persist in database

---

### UI / UX Considerations

* Video player as the base layer
* Overlays rendered above video using absolute positioning
* Simple, minimal controls
* Desktop-first layout

---

## Dependencies & Constraints

### External Dependencies

* Use some external tool/dependency to convert RTSP stream to webRTC that the web browser can natively handle..

### Technical Constraints

* Browsers do not natively support RTSP
* Must run locally
* Must be completed within one day

### Resource Constraints

* Team size: 1 developer
* Hard submission deadline

---

## Success Metrics

* RTSP stream plays successfully in browser
* Overlays can be created, updated, and deleted
* Demo video clearly shows real-time behavior
* Code is structured and documented


---

## Change Log

| Date       | Version | Changes               | Author |
| ---------- | ------- | --------------------- | ------ |
| 2026-01-15 | v1.0.0  | Initial specification | Favour |

---

## Notes & Assumptions

* Application is single-user
* RTSP stream is assumed to be valid
* Simplicity is prioritized over extensibility

---

## 2. General Project Instructions

### 2a. Frontend General Instructions (Project-Specific Additions)

**Additional Project-Specific Rules**

* Overlays must be rendered in a separate overlay layer above the video
* Overlay UI state must sync with backend on create/update/delete
* Avoid global state unless strictly necessary
* Favor clarity over abstraction due to time constraints

---

### Notes for AI Agent

* Follow the modular structure: RTSP feature and Overlay feature
* Do not introduce unnecessary complexity
* Prefer simple, readable solutions
* Flag browser RTSP limitations clearly when relevant
* Keep everything demo-ready and explainable
* Always check for errors, and fix if any, before requesting me to review your changes.
* Only add high-level comments, that describes the code block, what it does and how it's used, and prevent verbose nested comments.

---
