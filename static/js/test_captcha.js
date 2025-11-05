(() => {
  let currentCaptcha = null;
  let csrfToken = null;

  async function ensureCsrfToken() {
    if (csrfToken) {
      return csrfToken;
    }

    try {
      const response = await fetch('/api/security/status');
      if (response.ok) {
        const status = await response.json();
        csrfToken = status.csrf_token || null;
      }
    } catch (error) {
      console.error('Failed to fetch CSRF token:', error);
    }

    return csrfToken;
  }

  function renderResult(message, type = 'info') {
    const resultDiv = document.getElementById('result');
    if (!resultDiv) {
      return;
    }
    const colors = {
      success: '#166534',
      error: '#b91c1c',
      info: '#1f2937'
    };
    const color = colors[type] || colors.info;
    resultDiv.innerHTML = `<p style="color: ${color};">${message}</p>`;
  }

  window.testCaptcha = async function testCaptcha() {
    try {
      console.log('Testing CAPTCHA API...');
      const token = await ensureCsrfToken();
      const response = await fetch('/api/security/captcha', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'X-CSRF-Token': token } : {})
        }
      });

      if (response.ok) {
        currentCaptcha = await response.json();
        console.log('CAPTCHA received:', currentCaptcha);

        const questionEl = document.getElementById('captcha-question');
        if (questionEl) {
          questionEl.textContent = currentCaptcha.question;
        }

        renderResult('✅ CAPTCHA loaded successfully!', 'success');
      } else {
        console.error('CAPTCHA API failed:', response.status);
        renderResult(`❌ CAPTCHA API failed: ${response.status}`, 'error');
      }
    } catch (error) {
      console.error('Error:', error);
      renderResult(`❌ Error: ${error.message}`, 'error');
    }
  };

  window.verifyCaptcha = async function verifyCaptcha() {
    if (!currentCaptcha) {
      renderResult('❌ No CAPTCHA loaded', 'error');
      return;
    }

    const answerInput = document.getElementById('captcha-answer');
    if (!answerInput || !answerInput.value) {
      renderResult('❌ Please enter an answer', 'error');
      return;
    }

    try {
      const token = await ensureCsrfToken();
      const response = await fetch('/api/security/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { 'X-CSRF-Token': token } : {})
        },
        body: JSON.stringify({
          captcha_id: currentCaptcha.captcha_id,
          answer: answerInput.value
        })
      });

      const result = await response.json();
      if (result.status && result.status.csrf_token) {
        csrfToken = result.status.csrf_token;
      }

      if (response.ok && result.success) {
        renderResult('✅ CAPTCHA verified successfully!', 'success');
      } else {
        renderResult(`❌ CAPTCHA verification failed: ${result.error || 'Unknown error'}`, 'error');
      }
    } catch (error) {
      console.error('Verification error:', error);
      renderResult(`❌ Error: ${error.message}`, 'error');
    }
  };

  window.addEventListener('load', () => {
    testCaptcha().catch(error => console.error('Auto-load error:', error));
  });
})();
