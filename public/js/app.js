document.addEventListener('DOMContentLoaded', function() {
    console.log('Turtle Identifier App loaded');

    // Security state management
    let securityStatus = null;

    // Initialize security features
    initializeSecurity();

    // File input handling
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                console.log('File selected for analysis');

                // Validate file size
                if (file.size > 16 * 1024 * 1024) { // 16MB
                    showMessage('File size must be less than 16MB', 'error');
                    this.value = '';
                    return;
                }

                // Validate file type (additional security layer)
                const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];
                if (!allowedTypes.includes(file.type)) {
                    showMessage('Please select a valid image file (PNG, JPG, JPEG, GIF, BMP, or WEBP)', 'error');
                    this.value = '';
                    return;
                }

                // Check if CAPTCHA is required
                checkSecurityRequirements();
            }
        });
    }

    // Form submission handling - simplified
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            // Let the server handle CAPTCHA validation
            // Just check if file is selected
            const fileInput = uploadForm.querySelector('input[type="file"]');
            if (!fileInput.files[0]) {
                e.preventDefault();
                showMessage('Please select a file first', 'error');
                return;
            }
        });
    }

    // CAPTCHA form handling
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
            
            // Show loading state
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
                loadCaptcha();
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
        // Remove existing messages
        const existingMessages = document.querySelectorAll('.security-message');
        existingMessages.forEach(msg => msg.remove());

        // Create new message
        const messageDiv = document.createElement('div');
        messageDiv.className = `security-message ${type}`;
        messageDiv.textContent = message;

        // Insert after security status
        const securityStatus = document.getElementById('security-status');
        if (securityStatus && securityStatus.style.display !== 'none') {
            securityStatus.insertAdjacentElement('afterend', messageDiv);
        } else {
            // Insert at the beginning of the card
            const card = document.querySelector('.card');
            const firstChild = card.firstElementChild;
            card.insertBefore(messageDiv, firstChild);
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
