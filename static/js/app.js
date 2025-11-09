// Simplified Animal Identifier App JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Animal Identifier App loaded');

    const csrfMeta = document.querySelector('meta[name="csrf-token"]');
    if (csrfMeta && !window.csrfToken) {
        window.csrfToken = csrfMeta.getAttribute('content');
    }

    const TRANSITION_DURATION = 650;
    let transitionOverlay = document.querySelector('.page-transition');

    if (!transitionOverlay) {
        transitionOverlay = document.createElement('div');
        transitionOverlay.className = 'page-transition';
        transitionOverlay.setAttribute('aria-hidden', 'true');
        transitionOverlay.innerHTML = `
            <div class="fade-layer"></div>
            <svg class="leaf" viewBox="0 0 120 120" role="presentation">
                <defs>
                    <linearGradient id="leafGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#d4ff6a" />
                        <stop offset="45%" stop-color="#52c41a" />
                        <stop offset="100%" stop-color="#1a4d3a" />
                    </linearGradient>
                </defs>
                <path d="M60 6c22 12 48 36 48 66 0 30-22 48-48 48S12 102 12 72C12 36 38 20 60 6z" fill="url(#leafGradient)" />
                <path d="M60 22C40 38 32 56 32 76c0 14 8 28 28 34 20-6 28-20 28-34 0-20-8-38-28-54z" fill="rgba(255, 255, 255, 0.18)" />
                <path d="M60 20v72" stroke="rgba(255,255,255,0.7)" stroke-width="4" stroke-linecap="round" />
                <path d="M60 52c-8 6-14 14-14 28" stroke="rgba(255,255,255,0.5)" stroke-width="4" stroke-linecap="round" fill="none" />
                <path d="M60 44c8 6 14 14 14 28" stroke="rgba(255,255,255,0.4)" stroke-width="4" stroke-linecap="round" fill="none" />
            </svg>
        `;
        document.body.appendChild(transitionOverlay);
    }

    function startTransition(callback) {
        if (!transitionOverlay) {
            callback();
            return;
        }

        transitionOverlay.classList.remove('is-active');
        // Force reflow to restart animation
        void transitionOverlay.offsetWidth;

        transitionOverlay.classList.add('is-active');
        document.body.classList.add('is-transitioning');

        setTimeout(() => {
            callback();
        }, TRANSITION_DURATION);

        setTimeout(() => {
            document.body.classList.remove('is-transitioning');
            transitionOverlay.classList.remove('is-active');
        }, TRANSITION_DURATION + 800);
    }

    function bindLinkTransition(link) {
        link.addEventListener('click', (event) => {
            const href = link.getAttribute('href');
            if (!href || href.startsWith('#')) {
                return;
            }

            if (link.target && link.target !== '_self') {
                return;
            }

            const targetUrl = new URL(link.href, window.location.href);
            if (targetUrl.origin !== window.location.origin) {
                return;
            }

            if (targetUrl.href === window.location.href) {
                event.preventDefault();
                return;
            }

            event.preventDefault();
            startTransition(() => {
                window.location.href = targetUrl.href;
            });
        });
    }

    document.querySelectorAll('a.nav-link, a[data-transition="true"]').forEach((link) => {
        bindLinkTransition(link);
    });

    document.querySelectorAll('.logout-form').forEach((form) => {
        form.addEventListener('submit', (event) => {
            event.preventDefault();
            startTransition(() => {
                form.submit();
            });
        });
    });

    window.addEventListener('pageshow', () => {
        document.body.classList.remove('is-transitioning');
        if (transitionOverlay) {
            transitionOverlay.classList.remove('is-active');
        }
    });
    
    // Get elements
    const fileInput = document.getElementById('file-input');
    const uploadArea = document.querySelector('.upload-area');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const removeFileBtn = document.getElementById('remove-file');
    const submitBtn = document.getElementById('submit-btn');
    const communityUploadName = document.getElementById('upload-filename');
    
    console.log('Elements found:', {
        fileInput: !!fileInput,
        uploadArea: !!uploadArea,
        fileInfo: !!fileInfo,
        fileName: !!fileName,
        removeFileBtn: !!removeFileBtn,
        submitBtn: !!submitBtn
    });
    
    // Initialize submit button as disabled
    if (submitBtn) {
        submitBtn.disabled = true;
        console.log('Submit button initialized as disabled');
    }
    
    // Handle file input change
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            console.log('File input changed');
            const file = e.target.files[0];
            if (file) {
                console.log('File selected:', file.name, 'Size:', file.size, 'Type:', file.type);
                handleFileSelection(file);
            } else {
                console.log('No file selected');
                clearFileSelection();
            }
        });
    }
    
    // Handle upload area click
    if (uploadArea) {
        uploadArea.addEventListener('click', function(e) {
            console.log('Upload area clicked');
            if (fileInput) {
                fileInput.click();
            }
        });
    }
    
    // Handle remove file button
    if (removeFileBtn) {
        removeFileBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('Remove file clicked');
            clearFileSelection();
        });
    }
    
    // Handle drag and drop
    if (uploadArea) {
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                console.log('File dropped:', file.name);
                if (fileInput) {
                    fileInput.files = files;
                    handleFileSelection(file);
                }
            }
        });
    }
    
    function handleFileSelection(file) {
        // Validate file size (16MB max)
        if (file.size > 16 * 1024 * 1024) {
            console.log('File too large:', file.size);
            alert('File size must be less than 16MB');
            clearFileSelection();
            return;
        }
        
        // Validate file type
        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            console.log('Invalid file type:', file.type);
            alert('Please select a valid image file (PNG, JPG, JPEG, GIF, BMP, or WEBP)');
            clearFileSelection();
            return;
        }
        
        console.log('File validation passed');
        
        // Show file info
        if (fileName) {
            fileName.textContent = file.name;
        }
        if (communityUploadName) {
            communityUploadName.textContent = file.name;
        }
        if (fileInfo) {
            fileInfo.style.display = 'flex';
        }
        if (submitBtn) {
            submitBtn.disabled = false;
            console.log('Submit button enabled');
        }
        if (uploadArea && uploadArea.classList) {
            uploadArea.classList.add('has-file');
        }
        
        console.log('File selection completed successfully');
    }
    
    function clearFileSelection() {
        console.log('Clearing file selection');
        if (fileInput) {
            fileInput.value = '';
        }
        if (fileInfo) {
            fileInfo.style.display = 'none';
        }
        if (communityUploadName) {
            communityUploadName.textContent = 'No file selected';
        }
        if (submitBtn) {
            submitBtn.disabled = true;
            console.log('Submit button disabled');
        }
        if (uploadArea && uploadArea.classList) {
            uploadArea.classList.remove('has-file');
        }
    }
    
    // Form submission handling
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            console.log('Form submitted');
            if (!fileInput || !fileInput.files[0]) {
                e.preventDefault();
                alert('Please select a file first');
                return;
            }
            console.log('Form submission proceeding...');
        });
    }
    
    function updateCountsForSelector(selector, value) {
        document.querySelectorAll(selector).forEach((element) => {
            element.textContent = value;
        });
    }

    function handleCommunityAction(button, url, actionType) {
        if (!url) {
            return;
        }

        const csrfToken = window.csrfToken || csrfMeta?.getAttribute('content');
        button.disabled = true;

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-Token': csrfToken || ''
            },
            body: JSON.stringify({})
        })
        .then((response) => response.json())
        .then((data) => {
            if (!data.success) {
                window.alert(data.message || 'Unable to process request.');
                return;
            }

            const counts = data.counts || data;

            if (counts.likes !== undefined) {
                document.querySelectorAll(`[data-action="toggle-like"][data-url="${url}"] .count`).forEach((el) => {
                    el.textContent = counts.likes;
                });
                updateCountsForSelector('.like-count', counts.likes);
            }

            if (counts.saves !== undefined) {
                document.querySelectorAll(`[data-action="toggle-bookmark"][data-url="${url}"] .count`).forEach((el) => {
                    el.textContent = counts.saves;
                });
                updateCountsForSelector('.save-count', counts.saves);
            }

            if (counts.comments !== undefined) {
                updateCountsForSelector('.comment-count', counts.comments);
            }

            const buttons = document.querySelectorAll(`[data-url="${url}"]`);
            buttons.forEach((btn) => {
                if (actionType === 'like') {
                    if (data.action === 'liked') {
                        btn.classList.add('is-active');
                    } else {
                        btn.classList.remove('is-active');
                    }
                } else if (actionType === 'bookmark') {
                    if (data.action === 'saved') {
                        btn.classList.add('is-active');
                    } else {
                        btn.classList.remove('is-active');
                    }
                }
            });
        })
        .catch((error) => {
            console.error('Community action failed', error);
            window.alert('Something went wrong. Please try again.');
        })
        .finally(() => {
            button.disabled = false;
        });
    }

    document.querySelectorAll('[data-action="toggle-like"]').forEach((button) => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            const url = button.getAttribute('data-url');
            handleCommunityAction(button, url, 'like');
        });
    });

    document.querySelectorAll('[data-action="toggle-bookmark"]').forEach((button) => {
        button.addEventListener('click', (event) => {
            event.preventDefault();
            const url = button.getAttribute('data-url');
            handleCommunityAction(button, url, 'bookmark');
        });
    });

    document.querySelectorAll('[data-share-url]').forEach((button) => {
        button.addEventListener('click', async (event) => {
            event.preventDefault();
            const shareUrl = button.getAttribute('data-share-url');
            if (!shareUrl) {
                return;
            }

            try {
                if (navigator.share) {
                    await navigator.share({
                        title: 'WildID Community Sighting',
                        url: shareUrl
                    });
                } else if (navigator.clipboard) {
                    await navigator.clipboard.writeText(shareUrl);
                    window.alert('Link copied to clipboard!');
                } else {
                    window.prompt('Copy this link', shareUrl);
                }
            } catch (error) {
                console.error('Share failed', error);
                window.alert('Unable to share at the moment.');
            }
        });
    });

    document.querySelectorAll('.badge-progress-fill[data-progress]').forEach((bar) => {
        const progress = bar.getAttribute('data-progress');
        if (progress !== null) {
            bar.style.width = `${progress}%`;
        }
    });

    console.log('Animal Identifier App initialized successfully');
});