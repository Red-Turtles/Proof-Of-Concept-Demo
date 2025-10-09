document.addEventListener('DOMContentLoaded', function() {
    console.log('Turtle Identifier App loaded');

    let securityStatus = null;
    let submittingWithCaptcha = false;

    initializeSecurity();

    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                console.log('File selected for analysis');

                if (file.size > 16 * 1024 * 1024) {
                    showMessage('File size must be less than 16MB', 'error');
                    this.value = '';
                    return;
                }

                const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];
                if (!allowedTypes.includes(file.type)) {
                    showMessage('Please select a valid image file (PNG, JPG, JPEG, GIF, BMP, or WEBP)', 'error');
                    this.value = '';
                    return;
                }

                checkSecurityRequirements();
            }
        });
    }

    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            const fileInput = uploadForm.querySelector('input[type="file"]');
            if (!fileInput || !fileInput.files[0]) {
                e.preventDefault();
                showMessage('Please select a file first', 'error');
                return;
            }

            const siteKey = uploadForm.dataset ? uploadForm.dataset.sitekey : '';
            if (!siteKey) {
                return; // No reCAPTCHA configured; let server handle math CAPTCHA if needed
            }

            if (submittingWithCaptcha) {
                return; // Already obtained token, allow natural submit
            }

            try {
                e.preventDefault();
                const statusRes = await fetch('/api/security/status');
                const status = await statusRes.json();

                if (!status.is_trusted && status.rate_limited) {
                    const token = await getRecaptchaToken(siteKey);
                    if (!token) {
                        showMessage('Security verification failed. Please try again.', 'error');
                        return;
                    }
                    attachHiddenToken(uploadForm, token);
                    submittingWithCaptcha = true;
                    uploadForm.submit();
                } else {
                    // Not rate-limited yet; proceed
                    uploadForm.submit();
                }
            } catch (err) {
                console.error('Error obtaining security status or token:', err);
                showMessage('Could not verify security. Please try again.', 'error');
            }
        });
    }

    const captchaForm = document.getElementById('captcha-form');
    if (captchaForm) {
        captchaForm.addEventListener('submit', function(e) {
            const submitBtn = captchaForm.querySelector('.captcha-submit-btn');
            const answerInput = captchaForm.querySelector('input[name="captcha_answer"]');
            
            if (!answerInput.value) {
                e.preventDefault();
                showMessage('Please enter your answer', 'error');
                return;
            }
            
            submitBtn.disabled = true;
            submitBtn.textContent = 'Verifying...';
        });
    }

    async function initializeSecurity() {
        try {
            const response = await fetch('/api/security/status');
            securityStatus = await response.json();
            updateSecurityUI();
        } catch (error) {
            console.error('Failed to load security status:', error);
        }
    }

    async function checkSecurityRequirements() {
        try {
            const response = await fetch('/api/security/status');
            securityStatus = await response.json();
            
            if (!securityStatus.is_trusted && securityStatus.rate_limited) {
                showMessage('Security verification required after 2 image identifications', 'error');
            } else if (!securityStatus.is_trusted) {
                const remainingRequests = 2 - securityStatus.request_count;
                if (remainingRequests > 0) {
                    showMessage(`${remainingRequests} identification${remainingRequests > 1 ? 's' : ''} remaining before security verification`, 'info');
                }
            }
        } catch (error) {
            console.error('Failed to check security requirements:', error);
        }
    }

    function updateSecurityUI() {
        const securityStatusDiv = document.getElementById('security-status');
        const securityMessage = document.getElementById('security-message');

        if (securityStatus && !securityStatus.is_trusted) {
            securityStatusDiv.style.display = 'block';
            
            if (securityStatus.rate_limited) {
                securityMessage.textContent = 'Rate limit reached - Security verification required';
            } else {
                const remaining = 2 - securityStatus.request_count;
                securityMessage.textContent = `${remaining} identification${remaining > 1 ? 's' : ''} remaining before verification`;
            }
        } else {
            securityStatusDiv.style.display = 'none';
        }
    }

    function showMessage(message, type = 'info') {
        const existingMessages = document.querySelectorAll('.security-message');
        existingMessages.forEach(msg => msg.remove());

        const messageDiv = document.createElement('div');
        messageDiv.className = `security-message ${type}`;
        messageDiv.textContent = message;

        const securityStatus = document.getElementById('security-status');
        if (securityStatus && securityStatus.style.display !== 'none') {
            securityStatus.insertAdjacentElement('afterend', messageDiv);
        } else {
            const card = document.querySelector('.card');
            const firstChild = card.firstElementChild;
            card.insertBefore(messageDiv, firstChild);
        }

        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }

    function attachHiddenToken(form, token) {
        let input = form.querySelector('input[name="recaptcha_token"]');
        if (!input) {
            input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'recaptcha_token';
            form.appendChild(input);
        }
        input.value = token;
    }

    async function getRecaptchaToken(siteKey) {
        if (!window.grecaptcha || !window.grecaptcha.execute) {
            await loadRecaptcha(siteKey);
        }
        try {
            const token = await window.grecaptcha.execute(siteKey, { action: 'submit' });
            return token;
        } catch (e) {
            console.error('grecaptcha.execute failed:', e);
            return '';
        }
    }

    function loadRecaptcha(siteKey) {
        return new Promise((resolve) => {
            if (window.grecaptcha && window.grecaptcha.execute) {
                resolve();
                return;
            }
            const script = document.createElement('script');
            script.src = `https://www.google.com/recaptcha/api.js?render=${siteKey}`;
            script.async = true;
            script.onload = resolve;
            document.head.appendChild(script);
        });
    }

    console.log('Client-side security and validation initialized');
});

