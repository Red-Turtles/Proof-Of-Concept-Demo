// Simplified Animal Identifier App JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('Animal Identifier App loaded');
    
    // Get elements
    const fileInput = document.getElementById('file-input');
    const uploadArea = document.querySelector('.upload-area');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const removeFileBtn = document.getElementById('remove-file');
    const submitBtn = document.getElementById('submit-btn');
    
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
        if (fileInfo) {
            fileInfo.style.display = 'flex';
        }
        if (submitBtn) {
            submitBtn.disabled = false;
            console.log('Submit button enabled');
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
        if (submitBtn) {
            submitBtn.disabled = true;
            console.log('Submit button disabled');
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
    
    console.log('Animal Identifier App initialized successfully');
});