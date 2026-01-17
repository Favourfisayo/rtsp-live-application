---
applyTo: 'apps/server/*'
---

# Backend Testing & QA Instructions

**RTSP Livestream Overlay Web Application (Flask Backend)**

---

## 1. Testing Philosophy

This backend controls two high-risk domains:

1. **RTSP stream lifecycle management**
2. **Real-time overlay configuration persistence**

RTSP streams are **inherently unreliable** (network drops, codec issues, bad URLs).
The backend must **fail safely**, never corrupt state, and never leave orphan processes.

Testing focuses on:

* Correct API behavior
* Valid state transitions
* Input validation
* Database correctness
* Graceful error handling

Frontend rendering and actual video decoding are **out of scope**.

---

## 2. Testing Strategy Overview

### Testing Pyramid (Adjusted for This Project)

* **65% Unit Tests**

  * Overlay business logic
  * RTSP state handling
  * Validators
  * Database repository logic

* **25% Integration Tests**

  * Flask API endpoints
  * MongoDB persistence
  * RTSP lifecycle coordination (mocked)

* **10% End-to-End Tests**

  * Start stream → create overlay → update overlay → stop stream

---

### Coverage Targets

| Layer           | Target |
| --------------- | ------ |
| Overall         | ≥ 80%  |
| Overlay module  | ≥ 90%  |
| RTSP module     | ≥ 90%  |
| API routes      | ≥ 85%  |
| Validators      | ≥ 95%  |
| DB repositories | ≥ 75%  |

---

## 3. Testing Framework & Tools (Python-Specific)

```json
{
  "testRunner": "PyTest",
  "assertion": "PyTest",
  "apiTesting": "pytest-flask",
  "database": "MongoDB test database",
  "mocking": "unittest.mock",
  "coverage": "coverage.py"
}
```

### Why This Works

* PyTest is lightweight and fast
* `pytest-flask` gives real request/response testing
* MongoDB test DB prevents production pollution
* `unittest.mock` cleanly replaces RTSP processes

---

## 4. Test File Organization

```
└── tests/
    ├── integration/
    │   ├── test_rtsp_api.py
    │   └── test_overlay_api.py
    └── e2e/
        └── test_stream_overlay_flow.py
```

---

## 5. Unit Testing

### 5.1 RTSP Module Unit Tests

**What to test**

* Valid RTSP URL handling
* Stream state transitions
* Single active stream enforcement
* Graceful failure on invalid streams
* Process cleanup logic

#### Example: RTSP Service Unit Test

```python
def test_start_stream_success(mocker, rtsp_service):
    mocker.patch.object(rtsp_service, "_start_ffmpeg", return_value=True)

    rtsp_service.start_stream("rtsp://valid-stream")

    assert rtsp_service.state["status"] == "live"
```

#### Error Path

```python
def test_start_stream_failure(mocker, rtsp_service):
    mocker.patch.object(
        rtsp_service,
        "_start_ffmpeg",
        side_effect=Exception("RTSP failed")
    )

    with pytest.raises(Exception):
        rtsp_service.start_stream("rtsp://bad-stream")

    assert rtsp_service.state["status"] == "error"
```

---

### 5.2 Overlay Module Unit Tests

**What to test**

* Overlay creation
* Update logic (partial vs full)
* Position bounds validation
* Overlay type enforcement
* Database mapping correctness

#### Example

```python
def test_create_text_overlay(overlay_service):
    overlay = overlay_service.create_overlay({
        "type": "text",
        "content": "Hello",
        "x": 50,
        "y": 100,
        "width": 200,
        "height": 50
    })

    assert overlay["type"] == "text"
    assert overlay["content"] == "Hello"
```

#### Validation Failure

```python
def test_invalid_overlay_position(overlay_service):
    with pytest.raises(ValueError):
        overlay_service.create_overlay({
            "type": "text",
            "content": "Bad",
            "x": -10,
            "y": 50
        })
```

---

### 5.3 Validator Unit Tests

Validators are cheap and critical.

```python
def test_valid_rtsp_url():
    assert is_valid_rtsp_url("rtsp://camera/stream") is True

def test_invalid_rtsp_url():
    assert is_valid_rtsp_url("http://youtube.com") is False
```

---

## 6. Integration Testing (Flask API)

### 6.1 RTSP API Integration Tests

#### Endpoints Tested

* `POST /api/rtsp/start`
* `POST /api/rtsp/stop`
* `GET /api/rtsp/status`

```python
def test_start_rtsp_stream(client, mocker):
    mocker.patch("app.rtsp.service.RTSPService.start_stream")

    response = client.post("/api/rtsp/start", json={
        "url": "rtsp://test-stream"
    })

    assert response.status_code == 200
```

#### Invalid Input

```python
def test_start_rtsp_invalid_url(client):
    response = client.post("/api/rtsp/start", json={
        "url": "invalid-url"
    })

    assert response.status_code == 400
```

---

### 6.2 Overlay API Integration Tests

#### CRUD Coverage

* Create
* Read
* Update
* Delete

```python
def test_create_overlay(client):
    response = client.post("/api/overlays", json={
        "type": "image",
        "content": "https://logo.png",
        "x": 10,
        "y": 10
    })

    assert response.status_code == 201
    assert response.json["type"] == "image"
```

---

## 7. Database Testing (MongoDB)

### Database Rules

* Use a **dedicated test database**
* Clear collections between tests
* Never reuse production URI

```python
@pytest.fixture(autouse=True)
def clear_db(mongo):
    mongo.db.overlays.delete_many({})
```

#### Repository Test

```python
def test_overlay_persistence(overlay_repository):
    overlay_id = overlay_repository.create({
        "type": "text",
        "content": "Persist me"
    })

    overlay = overlay_repository.get(overlay_id)
    assert overlay is not None
```

---

## 8. End-to-End Backend Flow Test

This validates the **entire backend contract**.

```python
def test_stream_overlay_flow(client, mocker):
    mocker.patch("app.rtsp.service.RTSPService.start_stream")

    client.post("/api/rtsp/start", json={"url": "rtsp://stream"})
    client.post("/api/overlays", json={
        "type": "text",
        "content": "LIVE"
    })

    overlays = client.get("/api/overlays").json
    assert len(overlays) == 1

    client.post("/api/rtsp/stop")
```

---

## 9. Error Handling & Stability Testing

### Required Error Scenarios

* Invalid RTSP URL
* Stream already running
* Overlay not found
* Database write failure
* Stream stop without active stream

```python
def test_stop_without_stream(client):
    response = client.post("/api/rtsp/stop")
    assert response.status_code == 400
```

---

## 10. Security Testing (Minimal but Realistic)

This is **not a user-auth system**, so we keep it sane.

### What We Test

* Input sanitization
* Payload size limits
* XSS prevention (stored text overlays)

```python
def test_xss_in_overlay_text(client):
    response = client.post("/api/overlays", json={
        "type": "text",
        "content": "<script>alert(1)</script>"
    })

    assert "<script>" not in response.json["content"]
```

---

## 11. Coverage Configuration

```bash
coverage run -m pytest
coverage report -m
```

Target:

* ≥ 80% overall
* No untested RTSP state logic
* No untested overlay mutations

---

## Final QA Assessment

✅ Backend APIs behave predictably
✅ RTSP failures are contained
✅ Overlay state is consistent
✅ Database integrity preserved
✅ System is safe to demo


* Only add high-level comments, that describes the code block, what it does and how it's used, and prevent verbose nested comments.
