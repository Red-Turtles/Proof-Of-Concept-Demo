document.addEventListener('DOMContentLoaded', function() {
    console.log('Turtle Identifier App loaded');

    // Security state management
    let securityStatus = null;

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
        if (submitBtn) {
            submitBtn.disabled = false;
            console.log('Submit button enabled:', submitBtn.disabled);
        } else {
            console.error('Submit button not found!');
        }

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
        if (submitBtn) {
            submitBtn.disabled = true;
            console.log('Submit button disabled:', submitBtn.disabled);
        }
    }

    // Initialize submit button state
    if (submitBtn) {
        submitBtn.disabled = true;
        console.log('Initial submit button state - disabled:', submitBtn.disabled);
    }

    // Test: Add a simple test button to verify file input works
    if (fileInput) {
        const testBtn = document.createElement('button');
        testBtn.textContent = 'Test File Input';
        testBtn.style.cssText = 'position: fixed; top: 10px; right: 10px; z-index: 9999; background: red; color: white; padding: 10px;';
        testBtn.onclick = () => {
            console.log('Test button clicked');
            fileInput.click();
        };
        document.body.appendChild(testBtn);
        
        // Remove test button after 10 seconds
        setTimeout(() => {
            if (testBtn.parentNode) {
                testBtn.parentNode.removeChild(testBtn);
            }
        }, 10000);
    }


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
