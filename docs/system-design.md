## WildID System Design Document

### 1. Overview
WildID is a Flask-based web application that identifies animal species from uploaded images using a hosted vision-LMM (Together.ai Qwen2.5-VL). It provides a modern UI, a results page with confidence indicators, and an interactive habitat map using Leaflet. Security includes rate limiting, a simple math CAPTCHA, browser fingerprinting/trust, and strict security headers.

### 2. Architecture
- **Frontend**: Server-rendered templates (`Jinja2`) with static assets under `static/` and `templates/`. Leaflet is loaded from CDN on the map page.
- **Backend**: `Flask` app in `app.py`, with routes for pages and JSON APIs. Security logic isolated in `security.py` as `SecurityManager`.
- **External Services**: Together.ai chat completions API for image understanding; optional OpenAI path present but unused by default.
- **State**: File-based Flask sessions; in-memory security stores for demo (request counts, CAPTCHAs, trusted browsers). Uploaded files are persisted only temporarily, then removed.
- **Containerization/Orchestration**: Dockerfile and Compose definitions for dev and prod; generated Kubernetes manifests under `bridge/` for a proof-of-concept deployment.

High-level component diagram
- Client browser
  - Upload form and drag/drop (`templates/discovery.html`, `static/js/app.js`)
  - Results view (`templates/results.html`)
  - Map view (`templates/map.html` + Leaflet)
- Flask server (`app.py`)
  - Routes: `/`, `/discovery`, `/identify`, `/map`, `/api/*`, `/health`
  - Security: `SecurityManager` hooks and endpoints
  - Together.ai integration for vision
- Filesystem
  - `uploads/` for temp images (cleaned immediately after processing)

### 3. Request Lifecycle and Data Flow
1. User navigates to `/discovery` and uploads an image via POST `/identify`.
2. Server enforces security checks (rate limit + CAPTCHA gate if required), records request, and validates file type/size.
3. File is written to a randomized temporary path via `tempfile.mkstemp`; image validity is verified with `Pillow`.
4. Image is base64-encoded and sent to Together.ai `chat/completions` with a structured JSON response prompt.
5. Response is parsed as JSON (with fallback for code-fenced content). If parsing fails, a conservative "Unknown" payload is returned.
6. Temp file is deleted. The results page is rendered with the response and an inline preview (base64 data URL) for UX.
7. If the user clicks "View Habitat Map", `/map` renders Leaflet markers using static habitat data returned by `get_animal_habitat_data`.

### 4. Modules and Responsibilities
- `app.py`
  - App bootstrapping, CORS, session config, security headers
  - Upload handling, temporary file lifecycle, image validation
  - AI provider integration (Together.ai; OpenAI path present but not active)
  - Template rendering and JSON API routes
  - Habitat datasource (`get_animal_habitat_data`) with a curated set of species/habitats
- `security.py`
  - `SecurityManager` encapsulating:
    - Browser fingerprinting and trust window
    - IP+fingerprint rate limiting with sliding window
    - Simple math CAPTCHA generation/verification
    - Security status aggregation endpoint support

### 5. API Surface
- Page routes
  - `GET /` → `templates/index.html`
  - `GET /discovery` → `templates/discovery.html` (conditionally renders CAPTCHA block)
  - `POST /verify-captcha` → redirects to `/` on success; re-renders discovery page with error on failure
  - `POST /identify` → performs analysis and renders `results.html`
  - `GET /map?species&common_name&animal_type` → renders map page with Leaflet and markers
  - `GET /test-map` → debugging page for coordinates
- JSON APIs
  - `GET /api/habitat/<species>?common_name&animal_type` → habitat JSON used by `test-map.html`
  - `GET /api/security/status` → `{ is_trusted, rate_limited, browser_fingerprint, request_count }`
  - `POST /api/security/captcha` → `{ captcha_id, question, timeout }`
  - `POST /api/security/verify` body: `{ captcha_id, answer }` → `{ success: boolean, ... }`
- Health
  - `GET /health` → `{ status: 'healthy', message: 'WildID API is running' }`

### 6. Security Design
- **Headers** (`@app.after_request`):
  - `X-Content-Type-Options=nosniff`, `X-Frame-Options=DENY`, `X-XSS-Protection=1; mode=block`, `Referrer-Policy=strict-origin-when-cross-origin`
  - `Content-Security-Policy` restricting sources to self (+ Leaflet CDN on map page via `unpkg.com`)
- **Sessions**: File-based via `Flask-Session`, persistent for 30 days, `SECRET_KEY` configurable via env.
- **Rate limiting**: In-memory sliding window keyed by `IP:fingerprint`, `max_requests_per_window=2`, `window=3600s`. Exceeded users must solve CAPTCHA.
- **CAPTCHA**: Simple arithmetic with timeout and binding to the generated browser fingerprint; success trusts browser for 30 days.
- **File handling**: `secure_filename`, temp file creation via `mkstemp`, `Pillow` verification, deletion after processing. Max content length 16MB.
- **Trust model**: Post-CAPTCHA success marks the browser as trusted; trusted browsers bypass rate-limit CAPTCHA until trust expires.
- **Notes/Prod Hardening**:
  - Replace in-memory stores with Redis for shared-state deployments
  - Consider CSRF protection for form endpoints; add SameSite/secure cookie enforcement in prod
  - Validate/meter external API error cases; add circuit breakers/retries with backoff
  - Extend CSP to pin Leaflet subresources; consider subresource integrity

### 7. Configuration
Environment variables (see `env.example`):
- `TOGETHER_API_KEY` (required)
- `PORT` (default 3000)
- `UPLOAD_FOLDER` (default `uploads`)
- `MAX_CONTENT_LENGTH` (default `16777216`)
- `SECRET_KEY` and session cookie flags (set secure flags in production)
- Security tunables: `RATE_LIMIT_WINDOW`, `MAX_REQUESTS_PER_WINDOW`, `CAPTCHA_TIMEOUT`, `BROWSER_TRUST_DURATION`

### 8. Error Handling and Logging
- Centralized logging via `logging` to both file `app.log` and stdout.
- External API failures return a friendly `Service temporarily unavailable` error displayed on `results.html`.
- Image parsing and temp file errors produce 400s or result error rendering; temp files cleaned in `finally` path where possible.

### 9. Frontend/UI
- `templates/index.html`: marketing-style landing page with CTA to discovery.
- `templates/discovery.html`: upload flow, security status banner, conditional CAPTCHA block, drag-drop area, client-side validation in `static/js/app.js`.
- `templates/results.html`: displays animal label, confidence badge, and image preview; deep links to map when species is known.
- `templates/map.html`: Leaflet map with custom colored markers by habitat type; utilities for fit/reset/toggle, and download summary.
- Styling in `static/css/style.css` emphasizes dark-green/yellow theme with responsive layouts.

### 10. External Integrations
- **Together.ai**: `POST https://api.together.xyz/v1/chat/completions` with model `Qwen/Qwen2.5-VL-72B-Instruct`, temperature 0.1, and instructions to return strict JSON (handles code-fenced responses). Timeout 30s.
- (Optional) **OpenAI** path exists targeting `gpt-4o` with base64 image data but is not used by default.

### 11. Deployment
- Dockerfile: Python 3.12-slim, installs deps, non-root user, exposes 3000, runs `python app.py`, with a healthcheck on `/health`.
- Compose:
  - `docker-compose.yml` (prod): maps `3000:3000`, mounts `./uploads`, passes `TOGETHER_API_KEY`, healthcheck.
  - `docker-compose.dev.yml` (dev): live-reload via mounting `.` and `uploads/`, runs `python app.py`.
- Kubernetes (generated POC under `bridge/`):
  - Namespace, NetworkPolicy, Deployment (1 replica), Services (cluster and published), PVC for uploads.
  - NOTE: The manifests include Windows path artifacts and a hardcoded `TOGETHER_API_KEY` value; treat as placeholder POC and sanitize before real use.

### 12. Testing and Quality
- `test_security.py`: functional smoke test hitting security endpoints (status, CAPTCHA create/verify) and main page; run while the app is running.
- Python test deps in `requirements.txt`: `pytest`, `pytest-cov`, `pytest-mock` present but no unit tests included beyond the script.
- Suggested additions:
  - Unit tests for `SecurityManager` rate limiting and CAPTCHA lifecycles
  - Integration tests for `/identify` mocking Together.ai responses
  - Frontend e2e smoke via Playwright or Cypress

### 13. Scalability and Future Work
- Externalize state to Redis for rate limiting, CAPTCHA sessions, and trusted browsers (already listed as a prod note).
- Introduce queue-based async analysis for large workloads; pre-sign upload URLs and serve via object storage if needed.
- Add cached/normalized taxonomy backend and real habitat datasets.
- Implement standardized JSON API for `/identify` response alongside HTML rendering.
- Observability: structured logs, request IDs, metrics (latency, error rates), and tracing.

### 14. Operational Considerations
- Secure secrets: never hardcode API keys in manifests; use secrets managers/K8s Secrets.
- Ensure CSP/SRI cover all third-party assets.
- Set `SESSION_COOKIE_SECURE=true` and `SameSite=Strict` in production behind HTTPS.
- Configure reverse proxy (e.g., Nginx) for TLS termination and static asset caching.
