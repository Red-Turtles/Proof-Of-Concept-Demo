### Cursor AI Tutorial: Implementing CAPTCHA Protection in Your Web App

#### Overview
This case study-style tutorial walks through planning, integrating, and hardening CAPTCHA in a modern web application. It covers selecting a provider, implementing both frontend and backend verification, accessibility/UX considerations, common pitfalls, and production-readiness guidance. Examples include Google reCAPTCHA, hCaptcha, Cloudflare Turnstile, and a simple self-hosted fallback.

#### The Task
- **User Request**: “Add a CAPTCHA to my contact, signup, and login forms with minimal friction.”
- **Follow-up**: “How do I verify it on the server?”
- **Final Request**: “Can I avoid Google and keep it privacy-friendly? Also provide a fallback.”

---

### Step-by-Step Process

#### 1) Initial Planning and Threat Model
- **Identify abuse vectors**: credential stuffing, signup spam, contact form abuse, scraping, brute-force attempts.
- **Define constraints**:
  - Privacy and compliance needs (GDPR/CCPA).
  - Accessibility requirements (keyboard-only, screen readers).
  - Regions and blocklists (China, Iran restrictions).
  - UX tolerance (checkbox vs. invisible vs. passive score).
- **Choose a strategy**:
  - Low friction: Cloudflare Turnstile.
  - Balanced: reCAPTCHA v2 Invisible or hCaptcha checkbox.
  - No third-party: lightweight self-hosted math/text fallback (paired with rate limiting).

#### 2) Provider Selection (quick comparison)
- **reCAPTCHA**: ubiquitous, robust, Google dependency, privacy concerns in some orgs.
- **hCaptcha**: privacy-focused, free tier, robust, similar integration to reCAPTCHA.
- **Cloudflare Turnstile**: privacy-first, very low friction, easy integration, generous free tier.
- **Self-hosted fallback**: full control, lowest friction possible, less bot-resilient alone—pair with rate limiting and heuristics.

#### 3) Frontend Integration

- **Google reCAPTCHA v2 (checkbox)**:
```html
<script src="https://www.google.com/recaptcha/api.js" async defer></script>
<form action="/contact" method="POST">
  <!-- your form fields -->
  <div class="g-recaptcha" data-sitekey="YOUR_SITE_KEY"></div>
  <button type="submit">Send</button>
</form>
```
- Token field name: `g-recaptcha-response`

- **hCaptcha (checkbox)**:
```html
<script src="https://js.hcaptcha.com/1/api.js" async defer></script>
<form action="/contact" method="POST">
  <!-- your form fields -->
  <div class="h-captcha" data-sitekey="YOUR_SITE_KEY"></div>
  <button type="submit">Send</button>
</form>
```
- Token field name: `h-captcha-response`

- **Cloudflare Turnstile**:
```html
<script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
<form action="/contact" method="POST">
  <!-- your form fields -->
  <div class="cf-challenge" data-sitekey="YOUR_SITE_KEY"></div>
  <button type="submit">Send</button>
</form>
```
- Token field name: `cf-turnstile-response`

**Tips**:
- Place widgets near the submit button.
- Use one widget per form submission (refresh/reset on errors).
- Localize with provider attributes where available.

#### 4) Backend Verification

- **Flask (Python) – reCAPTCHA example**:
```python
import os
import requests
from flask import Flask, request, abort

app = Flask(__name__)
RECAPTCHA_SECRET = os.environ["RECAPTCHA_SECRET"]

def verify_recaptcha(token: str, remote_ip: str | None = None) -> bool:
    payload = {"secret": RECAPTCHA_SECRET, "response": token}
    if remote_ip:
        payload["remoteip"] = remote_ip
    resp = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload, timeout=5)
    data = resp.json()
    return bool(data.get("success"))

@app.post("/contact")
def contact():
    token = request.form.get("g-recaptcha-response")
    if not token or not verify_recaptcha(token, request.remote_addr):
        abort(400, "Captcha validation failed")
    # proceed with processing
    return "OK"
```

- **Express (Node) – reCAPTCHA example**:
```javascript
import express from 'express';
import fetch from 'node-fetch';

const app = express();
app.use(express.urlencoded({ extended: true }));
const SECRET = process.env.RECAPTCHA_SECRET;

app.post('/contact', async (req, res) => {
  const token = req.body['g-recaptcha-response'];
  if (!token) return res.status(400).send('Captcha missing');

  const response = await fetch('https://www.google.com/recaptcha/api/siteverify', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ secret: SECRET, response: token })
  });
  const data = await response.json();
  if (!data.success) return res.status(400).send('Captcha failed');

  // proceed with processing
  res.send('OK');
});
```

- **Adjust endpoints for other providers**:
  - hCaptcha verify: `https://hcaptcha.com/siteverify`
  - Turnstile verify: `https://challenges.cloudflare.com/turnstile/v0/siteverify`
- Always send the server-side secret; never expose it on the client.

#### 5) Self-Hosted Fallback (simple, lightweight)
- **HTML**:
```html
<form action="/contact" method="POST">
  <!-- your fields -->
  <label for="captcha">What is 7 + 5?</label>
  <input id="captcha" name="captcha_answer" required>
  <input type="hidden" name="captcha_expected" value="12">
  <button type="submit">Send</button>
</form>
```
- **Flask example (session-backed is better than hidden fields)**:
```python
import os, secrets
from flask import Flask, session, request, abort

app = Flask(__name__)
app.secret_key = os.environ["APP_SECRET_KEY"]

@app.get("/contact")
def contact_form():
    # generate and store expected answer in session
    a, b = 7, 5  # replace with random
    session["captcha_expected"] = str(a + b)
    # render template showing the question
    return f"""
      <form method="POST">
        <label>What is {a} + {b}?</label>
        <input name="captcha_answer" required>
        <button type="submit">Send</button>
      </form>
    """

@app.post("/contact")
def contact_submit():
    expected = session.pop("captcha_expected", None)
    if not expected or request.form.get("captcha_answer") != expected:
        abort(400, "Captcha incorrect")
    return "OK"
```
- Pair with rate limiting, IP heuristics, and honeypots for meaningful protection.

#### 6) UX, Accessibility, and Localization
- Ensure keyboard navigability and proper focus states.
- Provide ARIA labels and descriptive instructions.
- Offer audio challenge or alternative where supported.
- Localize widget text using provider attributes.
- Avoid blocking when provider scripts fail—graceful fallbacks.

#### 7) Security Hardening
- Verify on the server only; never trust client claims.
- Rate limit endpoints (e.g., IP + account + user-agent tuples).
- Bind CAPTCHA to a session or nonce; reject replayed tokens.
- Enforce token freshness and one-time-use semantics.
- Add honeypot fields and submission time checks (too-fast submissions).
- Protect with CSRF tokens; deny on mismatch.
- Log failures with context (no secrets), alert on spikes.
- Rotate secrets regularly; store in a vault or env vars.

#### 8) Testing and Monitoring
- Unit test: valid token, missing token, invalid token, replay attempts.
- Integration test: full form flow including error rendering and retry.
- Manual test with script failures, ad blockers, slow networks.
- Observability: track pass/fail rates, latency to verification endpoints, and CAPTCHAs per endpoint.

---

### Pros of Using Cursor AI for This Task
- **Structured Execution**: Broke down selection, integration, and hardening into clear steps.
- **Provider-Agnostic Guidance**: Reusable patterns for reCAPTCHA, hCaptcha, and Turnstile.
- **Production Focus**: Emphasis on server-side verification, rate limiting, and monitoring.
- **Developer Experience**: Copy-paste examples for Flask and Express.

### Cons and Limitations
- **Third-Party Dependence**: External verification endpoints can fail or be blocked.
- **Accessibility Trade-offs**: Some challenges remain difficult for assistive tech.
- **Regional Constraints**: Certain providers may not work in all regions.
- **Self-Hosted Weakness**: Simple captchas alone are easier to bypass—must be layered.

### Key Learnings for Cursor AI Users
- **Start with Requirements**: Privacy, region, accessibility, friction.
- **Always Verify Server-Side**: Client-side checks are insufficient.
- **Layer Defenses**: CAPTCHA + rate limiting + CSRF + heuristics.
- **Design for Failure**: Graceful degradation and clear user errors.
- **Monitor in Production**: Alert on anomaly spikes and token errors.

### Technical Recommendations
- **Providers**: Prefer Turnstile for privacy/UX, hCaptcha for privacy balance, reCAPTCHA for ubiquity.
- **Secrets**: Keep in env vars; rotate periodically.
- **Networking**: Add timeouts and retries to verification calls; cache short-lived provider public keys if needed.
- **Framework Add-ons**:
  - Flask: `Flask-Limiter` for rate limiting, CSRF via `flask-wtf` or `itsdangerous`.
  - Express: `express-rate-limit`, `helmet`, CSRF via `csurf`.
- **Fallback**: Implement a self-hosted math challenge for script-blocked environments, but keep it behind rate limiting.

### Overall Assessment
- **Success Rate**: 90%
- **What Worked Well**: Clear provider-agnostic flow, concise integration snippets, strong hardening guidance.
- **What Could Improve**: Region-specific caveats, richer a11y patterns, more SPA examples.

### Conclusion
Implementing CAPTCHA effectively is about thoughtful provider choice, strict server-side verification, layered defenses, and good UX. Use the snippets above to integrate your chosen provider, add a self-hosted fallback for resiliency, and harden with rate limiting and CSRF. With monitoring in place, you’ll significantly reduce automated abuse without burdening legitimate users.
