document.addEventListener('DOMContentLoaded', function() {
    console.log('Turtle Identifier App loaded');

    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    const csrfToken = csrfMeta ? csrfMeta.getAttribute('content') : null;
    window.csrfToken = csrfToken;

    function fetchWithCsrf(url, options = {}) {
        const config = { ...options };
        config.headers = config.headers ? { ...config.headers } : {};
        const activeToken = window.csrfToken || csrfToken;
        if (activeToken) {
            config.headers['X-CSRF-Token'] = activeToken;
        }
        return fetch(url, config);
    }

    // Security state management
    let securityStatus = null;
    let currentCaptcha = null;

    const securityStatusDiv = document.getElementById('security-status');
    const securityMessageEl = document.getElementById('security-message');
    const captchaContainer = document.getElementById('captcha-challenge');
    const captchaQuestionEl = document.getElementById('captcha-question');
    const captchaAnswerInput = document.getElementById('captcha-answer');
    const captchaSubmitBtn = document.getElementById('captcha-submit-btn');
    const captchaRefreshBtn = document.getElementById('captcha-refresh-btn');
    const captchaFeedback = document.getElementById('captcha-feedback');

    function setCaptchaFeedback(message, type) {
        if (!captchaFeedback) {
            return;
        }
        captchaFeedback.textContent = message || '';
        captchaFeedback.classList.remove('success', 'error');
        if (type) {
            captchaFeedback.classList.add(type);
        }
    }

    function enforceSubmissionState() {
        if (!submitBtn) {
            return;
        }
        const hasFile = fileInput && fileInput.files && fileInput.files[0];
        const blocked = securityStatus && !securityStatus.is_trusted && securityStatus.rate_limited;
        submitBtn.disabled = !hasFile || !!blocked;
    }

    function applySecurityStatus(status) {
        if (status) {
            securityStatus = status;
            if (status.csrf_token) {
                window.csrfToken = status.csrf_token;
            }
        }
        updateSecurityUI();
    }

    async function loadCaptcha(force = false) {
        if (!captchaContainer) {
            return;
        }

        if (!force && currentCaptcha) {
            captchaContainer.style.display = 'block';
            return;
        }

        try {
            const response = await fetchWithCsrf('/api/security/captcha', { method: 'POST' });
            if (!response.ok) {
                throw new Error(`Failed to load CAPTCHA: ${response.status}`);
            }
            currentCaptcha = await response.json();
            captchaContainer.style.display = 'block';
            if (captchaQuestionEl) {
                captchaQuestionEl.textContent = currentCaptcha.question;
            }
            if (captchaAnswerInput) {
                captchaAnswerInput.value = '';
                captchaAnswerInput.focus();
            }
            setCaptchaFeedback('', null);
            if (captchaSubmitBtn) {
                captchaSubmitBtn.disabled = false;
                captchaSubmitBtn.textContent = 'Verify';
            }
        } catch (error) {
            console.error('Failed to load CAPTCHA challenge:', error);
            setCaptchaFeedback('Unable to load security challenge. Please try again.', 'error');
        }
    }

    async function submitCaptchaAnswer() {
        if (!captchaSubmitBtn) {
            return;
        }

        if (!currentCaptcha) {
            await loadCaptcha(true);
            return;
        }

        if (!captchaAnswerInput || !captchaAnswerInput.value.trim()) {
            setCaptchaFeedback('Please enter your answer before verifying.', 'error');
            return;
        }

        try {
            captchaSubmitBtn.disabled = true;
            captchaSubmitBtn.textContent = 'Verifying...';
            setCaptchaFeedback('', null);

            const response = await fetchWithCsrf('/api/security/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    captcha_id: currentCaptcha.captcha_id,
                    answer: captchaAnswerInput.value.trim()
                })
            });

            const result = await response.json();

            if (response.ok && result.success) {
                setCaptchaFeedback('Verification successful! You can continue identifying animals.', 'success');
                currentCaptcha = null;
                if (captchaAnswerInput) {
                    captchaAnswerInput.value = '';
                }
                applySecurityStatus(result.status);
            } else {
                const feedback = result.error || 'Verification failed. Please try again.';
                setCaptchaFeedback(feedback, 'error');
                if (result.status) {
                    applySecurityStatus(result.status);
                }
                if (result.code === 'too_many_attempts' || result.code === 'invalid_captcha' || result.code === 'expired_captcha') {
                    currentCaptcha = null;
                    await loadCaptcha(true);
                }
            }
        } catch (error) {
            console.error('Failed to verify CAPTCHA:', error);
            setCaptchaFeedback('Unable to verify the challenge. Please try again.', 'error');
        } finally {
            if (captchaSubmitBtn) {
                captchaSubmitBtn.disabled = false;
                captchaSubmitBtn.textContent = 'Verify';
            }
            enforceSubmissionState();
        }
    }

    if (captchaRefreshBtn) {
        captchaRefreshBtn.addEventListener('click', (event) => {
            event.preventDefault();
            loadCaptcha(true);
        });
    }

    if (captchaSubmitBtn) {
        captchaSubmitBtn.addEventListener('click', (event) => {
            event.preventDefault();
            submitCaptchaAnswer();
        });
    }

    // Initialize security features
    initializeSecurity();

    // Modern upload area handling
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const removeFileBtn = document.getElementById('remove-file');
    const submitBtn = document.getElementById('submit-btn');

    // Debug: Check if elements are found
    console.log('Elements found:', {
        uploadArea: !!uploadArea,
        fileInput: !!fileInput,
        fileInfo: !!fileInfo,
        fileName: !!fileName,
        removeFileBtn: !!removeFileBtn,
        submitBtn: !!submitBtn
    });

    // Handle file selection - simplified approach
    if (fileInput) {
        console.log('Setting up file input listener');
        fileInput.addEventListener('change', function(e) {
            console.log('File input change event triggered');
            const file = e.target.files[0];
            if (file) {
                console.log('File found:', file.name);
                processFile(file);
            } else {
                console.log('No file selected');
            }
        });
    }

    if (uploadArea) {
        // Handle drag and drop
        uploadArea.addEventListener('dragover', handleDragOver);
        uploadArea.addEventListener('dragleave', handleDragLeave);
        uploadArea.addEventListener('drop', handleDrop);

        // Handle remove file
        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', removeFile);
        }

        // Click to select file
        uploadArea.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Upload area clicked, triggering file input');
            if (fileInput) {
                fileInput.click();
            }
        });
    }


    function handleDragOver(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    }

    function handleDragLeave(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    }

    function handleDrop(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            fileInput.files = files;
            processFile(file);
        }
    }

    function processFile(file) {
        console.log('File selected for analysis:', file.name);
        console.log('File details:', {
            name: file.name,
            size: file.size,
            type: file.type
        });

        // Validate file size
        if (file.size > 16 * 1024 * 1024) { // 16MB
            console.log('File too large:', file.size);
            showMessage('File size must be less than 16MB', 'error');
            clearFile();
            return;
        }

        // Validate file type (additional security layer)
        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            console.log('Invalid file type:', file.type);
            showMessage('Please select a valid image file (PNG, JPG, JPEG, GIF, BMP, or WEBP)', 'error');
            clearFile();
            return;
        }

        console.log('File validation passed, updating UI...');

        // Show file info
        if (fileName) fileName.textContent = file.name;
        if (fileInfo) fileInfo.style.display = 'flex';
        enforceSubmissionState();

        // Check if CAPTCHA is required
        checkSecurityRequirements();
    }

    function removeFile() {
        clearFile();
        showMessage('File removed', 'info');
    }

    function clearFile() {
        console.log('Clearing file...');
        if (fileInput) fileInput.value = '';
        if (fileInfo) fileInfo.style.display = 'none';
        enforceSubmissionState();
    }

    // Initialize submit button state
    enforceSubmissionState();


    // Form submission handling - simplified
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // Let the server handle CAPTCHA validation
            // Just check if file is selected
            if (!fileInput.files[0]) {
                e.preventDefault();
                showMessage('Please select a file first', 'error');
                return;
            }
        });
    }

    async function initializeSecurity() {
        try {
            const response = await fetchWithCsrf('/api/security/status');
            const status = await response.json();
            applySecurityStatus(status);
        } catch (error) {
            console.error('Failed to load security status:', error);
        }
    }

    async function checkSecurityRequirements() {
        try {
            const response = await fetchWithCsrf('/api/security/status');
            const status = await response.json();
            applySecurityStatus(status);

            const threshold = securityStatus.rate_limit_threshold || 2;

            if (!securityStatus.is_trusted && securityStatus.rate_limited) {
                const plural = threshold === 1 ? '' : 's';
                showMessage(`Security verification required after ${threshold} image identification${plural}`, 'error');
                await loadCaptcha();
            } else if (!securityStatus.is_trusted) {
                const remainingRequests = threshold - securityStatus.request_count;
                if (remainingRequests > 0) {
                    showMessage(`${remainingRequests} identification${remainingRequests > 1 ? 's' : ''} remaining before security verification`, 'info');
                }
            }
        } catch (error) {
            console.error('Failed to check security requirements:', error);
        }
    }


    function updateSecurityUI() {
        if (!securityStatusDiv || !securityMessageEl) {
            enforceSubmissionState();
            return;
        }

        if (securityStatus && !securityStatus.is_trusted) {
            securityStatusDiv.style.display = 'block';
            const threshold = securityStatus.rate_limit_threshold || 2;
            const remaining = Math.max(0, threshold - securityStatus.request_count);

            if (securityStatus.rate_limited) {
                securityMessageEl.textContent = 'Rate limit reached - Security verification required';
                if (captchaContainer) {
                    captchaContainer.style.display = 'block';
                    if (!currentCaptcha) {
                        loadCaptcha();
                    }
                }
            } else {
                const message = remaining > 0
                    ? `${remaining} identification${remaining === 1 ? '' : 's'} remaining before verification`
                    : 'Security verification pending';
                securityMessageEl.textContent = message;
                if (captchaContainer) {
                    captchaContainer.style.display = 'none';
                }
            }
        } else {
            securityStatusDiv.style.display = 'none';
            if (captchaContainer) {
                captchaContainer.style.display = 'none';
            }
            currentCaptcha = null;
            setCaptchaFeedback('', null);
        }

        enforceSubmissionState();
    }

    function showMessage(message, type = 'info') {
        // Remove existing messages
        const existingMessages = document.querySelectorAll('.security-message');
        existingMessages.forEach(msg => msg.remove());

        // Create new message
        const messageDiv = document.createElement('div');
        messageDiv.className = `security-message ${type}`;
        messageDiv.textContent = message;

        // Insert after security status
        if (securityStatusDiv && securityStatusDiv.style.display !== 'none') {
            securityStatusDiv.insertAdjacentElement('afterend', messageDiv);
        } else {
            // Insert at the beginning of the discovery card container if available
            const discoveryCard = document.querySelector('.discovery-card');
            if (discoveryCard) {
                discoveryCard.insertAdjacentElement('afterbegin', messageDiv);
            }
        }

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }



    console.log('Client-side security and validation initialized');
});
