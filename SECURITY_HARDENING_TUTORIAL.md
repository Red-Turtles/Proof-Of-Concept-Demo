## WildID Security Hardening Tutorial

This tutorial translates the recent WildID security assessment into a practical remediation plan. Work through the sections in order; each builds on the last to close critical gaps and align the implementation with the documented security architecture.

### Prerequisites

- Development environment with WildID running locally.
- Access to environment configuration (`.env`, deployment secrets, mail provider settings).
- Familiarity with Flask, SQLAlchemy, and basic web security controls.

> **Tip:** Keep tests running (`pytest`, `flask test`, etc.) as you iterate so regressions surface quickly.

---

### 1. Neutralize Host Header Injection in Magic Links

**Goal:** Ensure magic-link URLs cannot be poisoned by attacker-supplied hosts and always use HTTPS in production.

1. **Configure a canonical base URL.** In `config.py` (or `app.py` if config lives there), load a `BASE_URL`/`SERVER_NAME` from the environment, defaulting to the official domain for production and `http://localhost:5000` for development.
2. **Generate external URLs safely.** Replace manual string concatenation (`magic_link = f"http://{request_host}/auth/verify?token={token}"`) with Flask’s `url_for("auth.verify", token=token, _external=True, _scheme=base_url.scheme)` while forcing the hostname from configuration.
3. **Reject mismatched hosts.** Add a before-request hook that checks `request.host` against the allowed host list and aborts with `400` if it differs.
4. **Document deployment expectations.** Update ops runbooks to require the environment variable (e.g., `WILDID_BASE_URL=https://wildid.org`).

> **Verification:** Trigger a login locally and confirm the email contains the canonical domain. Attempt to spoof the `Host` header with a tool like `curl -H "Host: attacker.com"` and check that the request is rejected.

---

### 2. Enforce Authentication for Feedback and Other Privileged Routes

**Goal:** Block anonymous users from mutating sensitive data.

1. **Wrap feedback routes with an auth requirement.** Use a decorator or explicit guard that returns `401` when `current_user` is missing before any ownership checks run.
2. **Keep authorization intact.** After ensuring the user is authenticated, retain the ownership validation (`identification.user_id != current_user.id`) to prevent cross-account edits.
3. **Audit other routes.** Review `/identify`, `/api/history`, `/api/habitat`, etc., ensuring they either allow anonymous access by design or enforce `login_required`.

> **Verification:** Hit the feedback endpoint without cookies—expect `401`. Repeat as a different logged-in user—expect `403`.

---

### 3. Add CSRF Protection Across State-Changing Endpoints

**Goal:** Prevent forged POST/PUT/DELETE requests.

1. **Integrate Flask-WTF or similar.** Enable `WTF_CSRF_ENABLED` and initialize `CSRFProtect(app)`.
2. **Protect JSON APIs.** For REST endpoints, validate a header token (e.g., `X-CSRF-Token`) against the session’s CSRF token. Expose the token to the frontend by embedding it in the login response or a `/api/session` helper.
3. **Convert logout to POST.** Replace the GET logout route with a POST endpoint that requires a CSRF token.
4. **Update frontend calls.** Modify `public/js/app.js` to fetch and attach the CSRF token for each mutating request.

> **Verification:** Use browser dev tools or `curl` to replay a POST without the token—expect `400`/`403`. Ensure legitimate requests succeed.

---

### 4. Implement the Promised CAPTCHA and Rate-Limiting APIs

**Goal:** Deliver `/api/security/status` and `/api/security/captcha` and throttle abusive traffic.

1. **Add rate limiting.** Integrate `Flask-Limiter` with per-IP guardrails on login, token verification, and feedback submissions.
2. **Expose status endpoint.** Implement `/api/security/status` to report whether rate limiting or CAPTCHA is active, matching the frontend contract in `public/js/app.js`.
3. **Provide CAPTCHA challenges.** Use a service like hCaptcha/ReCAPTCHA or a self-hosted challenge. The `/api/security/captcha` route should issue tokens for the client to solve and verify solutions on submission.
4. **Add honeypots/logging.** Record failed CAPTCHA attempts, throttle IPs after repeated failures, and surface metrics to monitoring.

> **Verification:** Trigger throttling by sending bursts of requests. Confirm the frontend reacts to CAPTCHA activation as expected.

---

### 5. Secure Secrets, Sessions, and Cookies

**Goal:** Eliminate insecure defaults and harden session handling.

1. **Rotate `SECRET_KEY`.** Remove the development fallback (`dev-secret-key...`). Require `SECRET_KEY` via environment variables and automate rotation per environment.
2. **Set strict cookie flags.** Configure `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`, and `SESSION_COOKIE_SAMESITE='Lax'` (or `Strict` if UX allows). For subdomain sharing, document alternatives.
3. **Shorten session lifetime.** Consider reducing `PERMANENT_SESSION_LIFETIME` and adding idle timeouts.
4. **Hash magic-link tokens.** Store a hashed token (`sha256(token)`) in the database and compare hashes on verification. Store only the hash, never plaintext.
5. **Add token cleanup.** Schedule a background job or cron to purge expired tokens and stale filesystem sessions.

> **Verification:** Inspect cookies in the browser developer tools; flags should reflect the new configuration. Attempt to verify a login using only the stored hash—should fail.

---

### 6. Tighten Frontend Security Headers and Content Policy

**Goal:** Reduce XSS and clickjacking risk while preserving necessary functionality.

1. **Refine CSP.** Move inline scripts/styles into static files or add nonce-based loading. Update CSP to remove `'unsafe-inline'` and scope third-party domains to the minimum required for Leaflet and map tiles.
2. **Add HSTS.** Set `Strict-Transport-Security` (e.g., `max-age=31536000; includeSubDomains; preload`) when behind HTTPS.
3. **Review other headers.** Ensure `X-Frame-Options='DENY'`, `Referrer-Policy='strict-origin-when-cross-origin'`, and `Permissions-Policy` cover camera/mic/geolocation as appropriate.

> **Verification:** Use browser security tools or `curl -I` to inspect headers. Run Mozilla Observatory or securityheaders.com scans to confirm improvements.

---

### 7. Harden File Upload and AI Pipeline Handling

**Goal:** Minimize risk from hostile uploads and AI misuse.

1. **Re-encode uploads.** After validating with Pillow, re-save images to a safe format (e.g., JPEG/PNG) with size bounds to neutralize embedded payloads.
2. **Enforce pixel limits.** Reject images exceeding reasonable dimensions to prevent decompression bombs.
3. **Integrate malware scanning.** Use ClamAV or a cloud scanning API for additional protection.
4. **Avoid storing base64 blobs.** Instead, store resized images on disk/object storage and keep metadata in the database. Apply retention policies to clean up old uploads.
5. **Guard AI credentials.** Keep API keys in a secrets manager, restrict scopes, and monitor usage for anomalies. Consider proxying requests to strip sensitive payloads when possible.

> **Verification:** Attempt to upload oversized or malformed files; confirm graceful rejection. Monitor storage growth after repeated uploads.

---

### 8. Lock Down Deployment, Logging, and Monitoring

**Goal:** Ensure production runs without debug artifacts and that security signals are observable.

1. **Disable debug in production.** Run WildID via Gunicorn/Uvicorn with `debug=False`. Update `Dockerfile`/`docker-compose` accordingly.
2. **Serve via HTTPS.** Terminate TLS at a reverse proxy (nginx, Traefik) with automatic certificate renewal (e.g., certbot) and redirect all HTTP traffic to HTTPS.
3. **Harden health checks.** Limit information disclosed; return minimal status text without stack traces.
4. **Instrument logging.** Emit structured logs for login token generation, verification, feedback edits, rate-limit triggers, and CAPTCHA failures. Feed logs into a SIEM or alerting system.
5. **Add automated security tests.** Expand `test_security.py` to cover CSRF, auth, and rate-limiting behavior. Consider integrating dynamic scanners (OWASP ZAP) in CI/CD.

> **Verification:** Deploy to a staging environment and run the security test suite plus manual smoke tests. Confirm that no debug UI is reachable and TLS is enforced.

---

### Next Steps and Maintenance

- Track remediation progress with issues or tickets for each section above.
- Schedule periodic security reviews—especially after introducing new routes or integrations.
- Keep dependencies updated (`pip-audit`, `pip-tools`) and monitor advisories for Flask, Pillow, and third-party libraries.
- Revisit the threat model quarterly or after significant feature additions.

By following this tutorial, the team will close the high-severity vulnerabilities, restore parity between documentation and implementation, and establish a foundation for continuous hardening of the WildID platform.
