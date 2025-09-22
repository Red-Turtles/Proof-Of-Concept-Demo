document.addEventListener('DOMContentLoaded', function() {
    console.log('Turtle Identifier App loaded');

    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Security: Don't log sensitive filename information
                console.log('File selected for analysis');

                // Validate file size
                if (file.size > 16 * 1024 * 1024) { // 16MB
                    alert('File size must be less than 16MB');
                    this.value = '';
                    return;
                }

                // Validate file type (additional security layer)
                const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];
                if (!allowedTypes.includes(file.type)) {
                    alert('Please select a valid image file (PNG, JPG, JPEG, GIF, BMP, or WEBP)');
                    this.value = '';
                    return;
                }
            }
        });
    }

    // Add any other client-side functionality here
    console.log('Client-side validation initialized');
});
