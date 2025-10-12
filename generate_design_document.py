#!/usr/bin/env python3
"""
WildID Design Document Generator
Creates a comprehensive PNG design document for the WildID Wildlife Identification App
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Arrow
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import seaborn as sns

# Set up the figure with high DPI for crisp output
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'

# Color scheme from the CSS
colors = {
    'dark_green': '#1a4d3a',
    'medium_green': '#2d6a4f', 
    'light_green': '#52c41a',
    'yellow': '#ffd84d',
    'white': '#ffffff',
    'gray': '#6b7280',
    'dark_gray': '#374151',
    'black': '#0f172a',
    'slate': '#1e293b'
}

def create_design_document():
    """Create a comprehensive design document for WildID"""
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(20, 28))
    fig.patch.set_facecolor('white')
    
    # Main title
    fig.suptitle('WildID - Wildlife Identification App\nComprehensive Design Document', 
                 fontsize=24, fontweight='bold', color=colors['dark_green'], y=0.98)
    
    # 1. Application Overview
    ax1 = plt.subplot(4, 2, 1)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    
    # Header
    ax1.text(5, 9.5, 'Application Overview', fontsize=16, fontweight='bold', 
             ha='center', color=colors['dark_green'])
    
    # App description
    ax1.text(0.5, 8.5, 'WildID is an AI-powered wildlife identification application that uses', 
             fontsize=11, ha='left', va='top', wrap=True)
    ax1.text(0.5, 8.2, 'Together.ai\'s Qwen2.5-VL Vision model to identify animal species', 
             fontsize=11, ha='left', va='top')
    ax1.text(0.5, 7.9, 'from uploaded images. The app features interactive habitat mapping,', 
             fontsize=11, ha='left', va='top')
    ax1.text(0.5, 7.6, 'advanced security features, and a modern responsive UI.', 
             fontsize=11, ha='left', va='top')
    
    # Key features box
    features_box = FancyBboxPatch((0.5, 5.5), 9, 2, boxstyle="round,pad=0.1", 
                                 facecolor=colors['light_green'], alpha=0.2, 
                                 edgecolor=colors['medium_green'], linewidth=2)
    ax1.add_patch(features_box)
    ax1.text(5, 6.8, 'Key Features', fontsize=12, fontweight='bold', ha='center', 
             color=colors['dark_green'])
    ax1.text(1, 6.3, '• AI-Powered Species Identification', fontsize=10, ha='left')
    ax1.text(1, 6.0, '• Interactive Habitat Mapping', fontsize=10, ha='left')
    ax1.text(1, 5.7, '• Advanced Security & CAPTCHA System', fontsize=10, ha='left')
    ax1.text(5.5, 6.3, '• Modern Responsive UI', fontsize=10, ha='left')
    ax1.text(5.5, 6.0, '• Real-time File Processing', fontsize=10, ha='left')
    ax1.text(5.5, 5.7, '• Conservation Information', fontsize=10, ha='left')
    
    # 2. Technology Stack
    ax2 = plt.subplot(4, 2, 2)
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    
    ax2.text(5, 9.5, 'Technology Stack', fontsize=16, fontweight='bold', 
             ha='center', color=colors['dark_green'])
    
    # Backend
    backend_box = FancyBboxPatch((0.5, 7.5), 4, 1.5, boxstyle="round,pad=0.1", 
                                facecolor=colors['yellow'], alpha=0.3, 
                                edgecolor=colors['dark_green'], linewidth=2)
    ax2.add_patch(backend_box)
    ax2.text(2.5, 8.2, 'Backend', fontsize=12, fontweight='bold', ha='center', 
             color=colors['dark_green'])
    ax2.text(1, 7.8, '• Flask (Python)', fontsize=10, ha='left')
    ax2.text(1, 7.5, '• Together.ai API', fontsize=10, ha='left')
    
    # Frontend
    frontend_box = FancyBboxPatch((5.5, 7.5), 4, 1.5, boxstyle="round,pad=0.1", 
                                 facecolor=colors['light_green'], alpha=0.3, 
                                 edgecolor=colors['dark_green'], linewidth=2)
    ax2.add_patch(frontend_box)
    ax2.text(7.5, 8.2, 'Frontend', fontsize=12, fontweight='bold', ha='center', 
             color=colors['dark_green'])
    ax2.text(6, 7.8, '• HTML5/CSS3', fontsize=10, ha='left')
    ax2.text(6, 7.5, '• JavaScript', fontsize=10, ha='left')
    
    # AI/ML
    ai_box = FancyBboxPatch((0.5, 5.5), 4, 1.5, boxstyle="round,pad=0.1", 
                           facecolor=colors['medium_green'], alpha=0.3, 
                           edgecolor=colors['dark_green'], linewidth=2)
    ax2.add_patch(ai_box)
    ax2.text(2.5, 6.2, 'AI/ML', fontsize=12, fontweight='bold', ha='center', 
             color=colors['white'])
    ax2.text(1, 5.8, '• Qwen2.5-VL Vision', fontsize=10, ha='left', color=colors['white'])
    ax2.text(1, 5.5, '• Computer Vision', fontsize=10, ha='left', color=colors['white'])
    
    # Infrastructure
    infra_box = FancyBboxPatch((5.5, 5.5), 4, 1.5, boxstyle="round,pad=0.1", 
                              facecolor=colors['slate'], alpha=0.3, 
                              edgecolor=colors['dark_green'], linewidth=2)
    ax2.add_patch(infra_box)
    ax2.text(7.5, 6.2, 'Infrastructure', fontsize=12, fontweight='bold', ha='center', 
             color=colors['white'])
    ax2.text(6, 5.8, '• Docker', fontsize=10, ha='left', color=colors['white'])
    ax2.text(6, 5.5, '• Gunicorn', fontsize=10, ha='left', color=colors['white'])
    
    # 3. Architecture Diagram
    ax3 = plt.subplot(4, 2, 3)
    ax3.set_xlim(0, 12)
    ax3.set_ylim(0, 12)
    ax3.axis('off')
    
    ax3.text(6, 11.5, 'System Architecture', fontsize=16, fontweight='bold', 
             ha='center', color=colors['dark_green'])
    
    # User
    user_circle = Circle((2, 9.5), 0.8, facecolor=colors['yellow'], alpha=0.8, 
                        edgecolor=colors['dark_green'], linewidth=2)
    ax3.add_patch(user_circle)
    ax3.text(2, 9.5, 'User', fontsize=11, fontweight='bold', ha='center', va='center')
    
    # Web Interface
    web_rect = FancyBboxPatch((4.5, 8.5), 3, 1.5, boxstyle="round,pad=0.1", 
                             facecolor=colors['light_green'], alpha=0.8, 
                             edgecolor=colors['dark_green'], linewidth=2)
    ax3.add_patch(web_rect)
    ax3.text(6, 9.25, 'Web Interface', fontsize=11, fontweight='bold', ha='center', va='center')
    ax3.text(6, 8.8, 'HTML/CSS/JS', fontsize=9, ha='center', va='center', color=colors['dark_green'])
    
    # Flask App
    flask_rect = FancyBboxPatch((8.5, 8.5), 3, 1.5, boxstyle="round,pad=0.1", 
                               facecolor=colors['medium_green'], alpha=0.8, 
                               edgecolor=colors['dark_green'], linewidth=2)
    ax3.add_patch(flask_rect)
    ax3.text(10, 9.25, 'Flask App', fontsize=11, fontweight='bold', ha='center', va='center', color=colors['white'])
    ax3.text(10, 8.8, 'Python Backend', fontsize=9, ha='center', va='center', color=colors['white'])
    
    # AI API
    ai_rect = FancyBboxPatch((4.5, 6), 3, 1.5, boxstyle="round,pad=0.1", 
                            facecolor=colors['slate'], alpha=0.8, 
                            edgecolor=colors['dark_green'], linewidth=2)
    ax3.add_patch(ai_rect)
    ax3.text(6, 6.75, 'Together.ai API', fontsize=11, fontweight='bold', ha='center', va='center', 
             color=colors['white'])
    ax3.text(6, 6.3, 'Qwen2.5-VL Model', fontsize=9, ha='center', va='center', color=colors['white'])
    
    # File Storage
    db_rect = FancyBboxPatch((8.5, 6), 3, 1.5, boxstyle="round,pad=0.1", 
                            facecolor=colors['gray'], alpha=0.8, 
                            edgecolor=colors['dark_green'], linewidth=2)
    ax3.add_patch(db_rect)
    ax3.text(10, 6.75, 'File Storage', fontsize=11, fontweight='bold', ha='center', va='center', 
             color=colors['white'])
    ax3.text(10, 6.3, 'Temporary Files', fontsize=9, ha='center', va='center', color=colors['white'])
    
    # Security Layer
    security_rect = FancyBboxPatch((2, 4), 8, 1, boxstyle="round,pad=0.1", 
                                  facecolor=colors['yellow'], alpha=0.3, 
                                  edgecolor=colors['dark_green'], linewidth=2)
    ax3.add_patch(security_rect)
    ax3.text(6, 4.5, 'Security Layer (CAPTCHA, Rate Limiting, Browser Trust)', fontsize=10, fontweight='bold', ha='center', va='center', color=colors['dark_green'])
    
    # Improved Arrows with better positioning and styling
    # User to Web Interface
    ax3.annotate('', xy=(4.2, 9.5), xytext=(2.8, 9.5),
                arrowprops=dict(arrowstyle='->', lw=3, color=colors['dark_green'], 
                              connectionstyle="arc3,rad=0"))
    ax3.text(3.5, 10.2, '1. Upload Image', fontsize=9, ha='center', va='center', 
             bbox=dict(boxstyle="round,pad=0.3", facecolor=colors['white'], alpha=0.8))
    
    # Web Interface to Flask App
    ax3.annotate('', xy=(8.2, 9.25), xytext=(7.5, 9.25),
                arrowprops=dict(arrowstyle='->', lw=3, color=colors['dark_green'], 
                              connectionstyle="arc3,rad=0"))
    ax3.text(7.85, 10, '2. Process Request', fontsize=9, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.3", facecolor=colors['white'], alpha=0.8))
    
    # Flask App to AI API
    ax3.annotate('', xy=(6, 7.5), xytext=(8.5, 8.2),
                arrowprops=dict(arrowstyle='->', lw=3, color=colors['dark_green'], 
                              connectionstyle="arc3,rad=-0.2"))
    ax3.text(7.25, 7.8, '3. AI Analysis', fontsize=9, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.3", facecolor=colors['white'], alpha=0.8))
    
    # Flask App to File Storage
    ax3.annotate('', xy=(8.2, 6.75), xytext=(8.5, 8.2),
                arrowprops=dict(arrowstyle='->', lw=3, color=colors['dark_green'], 
                              connectionstyle="arc3,rad=0.2"))
    ax3.text(9.5, 7.5, '4. Store Temp File', fontsize=9, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.3", facecolor=colors['white'], alpha=0.8))
    
    # AI API to Flask App (response)
    ax3.annotate('', xy=(8.2, 6.75), xytext=(7.5, 6.75),
                arrowprops=dict(arrowstyle='->', lw=3, color=colors['medium_green'], 
                              connectionstyle="arc3,rad=0", linestyle='--'))
    ax3.text(7.85, 5.5, '5. Species Data', fontsize=9, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.3", facecolor=colors['white'], alpha=0.8))
    
    # Flask App to Web Interface (response)
    ax3.annotate('', xy=(7.5, 8.5), xytext=(8.2, 8.5),
                arrowprops=dict(arrowstyle='->', lw=3, color=colors['medium_green'], 
                              connectionstyle="arc3,rad=0", linestyle='--'))
    ax3.text(7.85, 7.8, '6. Results', fontsize=9, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.3", facecolor=colors['white'], alpha=0.8))
    
    # Web Interface to User (response)
    ax3.annotate('', xy=(2.8, 9.5), xytext=(4.2, 9.5),
                arrowprops=dict(arrowstyle='->', lw=3, color=colors['medium_green'], 
                              connectionstyle="arc3,rad=0", linestyle='--'))
    ax3.text(3.5, 8.8, '7. Display Results', fontsize=9, ha='center', va='center',
             bbox=dict(boxstyle="round,pad=0.3", facecolor=colors['white'], alpha=0.8))
    
    # Security layer connections
    ax3.annotate('', xy=(6, 5), xytext=(6, 7.5),
                arrowprops=dict(arrowstyle='->', lw=2, color=colors['yellow'], 
                              connectionstyle="arc3,rad=0", alpha=0.7))
    ax3.text(6.5, 6.2, 'Security Check', fontsize=8, ha='center', va='center', color=colors['dark_green'])
    
    # 4. Security Features
    ax4 = plt.subplot(4, 2, 4)
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 10)
    ax4.axis('off')
    
    ax4.text(5, 9.5, 'Security Features', fontsize=16, fontweight='bold', 
             ha='center', color=colors['dark_green'])
    
    # Security boxes
    security_features = [
        ('CAPTCHA System', 'Rate limiting with math challenges', 0.5, 8),
        ('Browser Trust', '30-day trusted browser tracking', 5.5, 8),
        ('File Security', 'Randomized filenames & auto-cleanup', 0.5, 6),
        ('Rate Limiting', '2 requests before verification', 5.5, 6),
        ('Security Headers', 'XSS, clickjacking protection', 0.5, 4),
        ('Session Management', 'Secure cookie configuration', 5.5, 4)
    ]
    
    for title, desc, x, y in security_features:
        box = FancyBboxPatch((x, y-0.8), 4, 1.5, boxstyle="round,pad=0.1", 
                           facecolor=colors['yellow'], alpha=0.2, 
                           edgecolor=colors['dark_green'], linewidth=1)
        ax4.add_patch(box)
        ax4.text(x+2, y+0.2, title, fontsize=11, fontweight='bold', ha='center', 
                color=colors['dark_green'])
        ax4.text(x+0.2, y-0.3, desc, fontsize=9, ha='left', va='top', wrap=True)
    
    # 5. UI Components
    ax5 = plt.subplot(4, 2, 5)
    ax5.set_xlim(0, 10)
    ax5.set_ylim(0, 10)
    ax5.axis('off')
    
    ax5.text(5, 9.5, 'UI Components & Design System', fontsize=16, fontweight='bold', 
             ha='center', color=colors['dark_green'])
    
    # Color palette
    ax5.text(0.5, 8.8, 'Color Palette:', fontsize=12, fontweight='bold', ha='left')
    color_boxes = [
        (colors['dark_green'], 'Dark Green', 0.5, 8.3),
        (colors['medium_green'], 'Medium Green', 2.5, 8.3),
        (colors['light_green'], 'Light Green', 4.5, 8.3),
        (colors['yellow'], 'Yellow Accent', 6.5, 8.3),
        (colors['slate'], 'Slate', 8.5, 8.3)
    ]
    
    for color, name, x, y in color_boxes:
        color_rect = Rectangle((x, y), 1.5, 0.4, facecolor=color, edgecolor=colors['black'], linewidth=1)
        ax5.add_patch(color_rect)
        ax5.text(x+0.75, y-0.2, name, fontsize=9, ha='center', va='top')
    
    # UI elements
    ax5.text(0.5, 7.5, 'Key UI Elements:', fontsize=12, fontweight='bold', ha='left')
    ax5.text(0.5, 7.2, '• Hero Section with gradient background', fontsize=10, ha='left')
    ax5.text(0.5, 6.9, '• Drag & drop file upload area', fontsize=10, ha='left')
    ax5.text(0.5, 6.6, '• Interactive habitat map (Leaflet)', fontsize=10, ha='left')
    ax5.text(0.5, 6.3, '• Results grid with species information', fontsize=10, ha='left')
    ax5.text(0.5, 6.0, '• Responsive design for mobile/desktop', fontsize=10, ha='left')
    
    # 6. Data Flow
    ax6 = plt.subplot(4, 2, 6)
    ax6.set_xlim(0, 12)
    ax6.set_ylim(0, 12)
    ax6.axis('off')
    
    ax6.text(6, 11.5, 'Data Flow & Processing', fontsize=16, fontweight='bold', 
             ha='center', color=colors['dark_green'])
    
    # Process steps with better spacing
    steps = [
        ('1. Image Upload', 'User uploads animal photo\n(PNG, JPG, WEBP, etc.)', 1, 10),
        ('2. Security Check', 'Rate limiting & CAPTCHA\nverification', 1, 8.2),
        ('3. File Processing', 'Secure temp file creation\nwith randomized names', 1, 6.4),
        ('4. AI Analysis', 'Together.ai species\nidentification', 1, 4.6),
        ('5. Results Display', 'Species info & habitat\nmap visualization', 1, 2.8),
        ('6. Cleanup', 'Automatic file deletion\nand cleanup', 1, 1)
    ]
    
    for i, (step, desc, x, y) in enumerate(steps):
        # Step box with better styling
        step_box = FancyBboxPatch((x, y-0.8), 4, 1.4, boxstyle="round,pad=0.1", 
                                facecolor=colors['light_green'], alpha=0.2, 
                                edgecolor=colors['dark_green'], linewidth=2)
        ax6.add_patch(step_box)
        ax6.text(x+2, y+0.2, step, fontsize=11, fontweight='bold', ha='center', 
                color=colors['dark_green'])
        ax6.text(x+0.2, y-0.4, desc, fontsize=9, ha='left', va='top', wrap=True, color=colors['gray'])
        
        # Improved arrow to next step
        if i < len(steps) - 1:
            ax6.annotate('', xy=(x+2, y-0.8), xytext=(x+2, y-0.1),
                        arrowprops=dict(arrowstyle='->', lw=2, color=colors['dark_green'], 
                                      connectionstyle="arc3,rad=0"))
    
    # Add parallel processing indicators
    ax6.text(6.5, 9.5, 'Parallel Processing:', fontsize=10, fontweight='bold', ha='left', color=colors['dark_green'])
    ax6.text(6.5, 9, '• File validation', fontsize=8, ha='left', color=colors['gray'])
    ax6.text(6.5, 8.7, '• Image preprocessing', fontsize=8, ha='left', color=colors['gray'])
    ax6.text(6.5, 8.4, '• Security checks', fontsize=8, ha='left', color=colors['gray'])
    
    # Add timing information
    timing_box = FancyBboxPatch((6.5, 6.5), 4.5, 2, boxstyle="round,pad=0.1", 
                               facecolor=colors['yellow'], alpha=0.1, 
                               edgecolor=colors['dark_green'], linewidth=1)
    ax6.add_patch(timing_box)
    ax6.text(8.75, 7.8, 'Processing Times', fontsize=10, fontweight='bold', ha='center', color=colors['dark_green'])
    ax6.text(6.7, 7.3, '• Upload: < 1s', fontsize=8, ha='left', color=colors['gray'])
    ax6.text(6.7, 7, '• AI Analysis: 2-5s', fontsize=8, ha='left', color=colors['gray'])
    ax6.text(6.7, 6.7, '• Results: < 1s', fontsize=8, ha='left', color=colors['gray'])
    
    # 7. File Structure
    ax7 = plt.subplot(4, 2, 7)
    ax7.set_xlim(0, 10)
    ax7.set_ylim(0, 10)
    ax7.axis('off')
    
    ax7.text(5, 9.5, 'Project Structure', fontsize=16, fontweight='bold', 
             ha='center', color=colors['dark_green'])
    
    # File structure
    structure = [
        ('app.py', 'Main Flask application', 0.5, 8.5),
        ('security.py', 'Security & CAPTCHA system', 0.5, 8),
        ('templates/', 'HTML templates', 0.5, 7.5),
        ('  ├── index.html', 'Home page', 1, 7.2),
        ('  ├── discovery.html', 'Upload page', 1, 6.9),
        ('  ├── results.html', 'Results display', 1, 6.6),
        ('  └── map.html', 'Habitat mapping', 1, 6.3),
        ('static/', 'Static assets', 0.5, 6),
        ('  ├── css/style.css', 'Main stylesheet', 1, 5.7),
        ('  └── js/app.js', 'Client-side logic', 1, 5.4),
        ('bridge/', 'Kubernetes configs', 0.5, 5),
        ('Dockerfile', 'Container definition', 0.5, 4.5),
        ('requirements.txt', 'Python dependencies', 0.5, 4)
    ]
    
    for item, desc, x, y in structure:
        ax7.text(x, y, item, fontsize=9, ha='left', va='center', 
                color=colors['dark_green'] if not item.startswith('  ') else colors['gray'])
        if desc:
            ax7.text(x+3, y, desc, fontsize=8, ha='left', va='center', 
                    color=colors['gray'], style='italic')
    
    # 8. Deployment & Infrastructure
    ax8 = plt.subplot(4, 2, 8)
    ax8.set_xlim(0, 10)
    ax8.set_ylim(0, 10)
    ax8.axis('off')
    
    ax8.text(5, 9.5, 'Deployment & Infrastructure', fontsize=16, fontweight='bold', 
             ha='center', color=colors['dark_green'])
    
    # Docker container
    container_box = FancyBboxPatch((1, 7.5), 8, 1.5, boxstyle="round,pad=0.1", 
                                  facecolor=colors['slate'], alpha=0.2, 
                                  edgecolor=colors['dark_green'], linewidth=2)
    ax8.add_patch(container_box)
    ax8.text(5, 8.2, 'Docker Container', fontsize=12, fontweight='bold', ha='center', 
             color=colors['dark_green'])
    ax8.text(2, 7.8, '• Multi-stage build', fontsize=10, ha='left')
    ax8.text(2, 7.5, '• Health checks', fontsize=10, ha='left')
    ax8.text(6, 7.8, '• Port 3000', fontsize=10, ha='left')
    ax8.text(6, 7.5, '• Gunicorn WSGI', fontsize=10, ha='left')
    
    # Kubernetes
    k8s_box = FancyBboxPatch((1, 5.5), 8, 1.5, boxstyle="round,pad=0.1", 
                            facecolor=colors['medium_green'], alpha=0.2, 
                            edgecolor=colors['dark_green'], linewidth=2)
    ax8.add_patch(k8s_box)
    ax8.text(5, 6.2, 'Kubernetes Deployment', fontsize=12, fontweight='bold', ha='center', 
             color=colors['dark_green'])
    ax8.text(2, 5.8, '• Namespace: proof-of-concept-demo', fontsize=10, ha='left')
    ax8.text(2, 5.5, '• Service & Ingress', fontsize=10, ha='left')
    ax8.text(6, 5.8, '• Persistent volumes', fontsize=10, ha='left')
    ax8.text(6, 5.5, '• Network policies', fontsize=10, ha='left')
    
    # Environment
    env_box = FancyBboxPatch((1, 3.5), 8, 1.5, boxstyle="round,pad=0.1", 
                            facecolor=colors['yellow'], alpha=0.2, 
                            edgecolor=colors['dark_green'], linewidth=2)
    ax8.add_patch(env_box)
    ax8.text(5, 4.2, 'Environment Configuration', fontsize=12, fontweight='bold', ha='center', 
             color=colors['dark_green'])
    ax8.text(2, 3.8, '• TOGETHER_API_KEY', fontsize=10, ha='left')
    ax8.text(2, 3.5, '• SECRET_KEY', fontsize=10, ha='left')
    ax8.text(6, 3.8, '• Rate limiting config', fontsize=10, ha='left')
    ax8.text(6, 3.5, '• Session settings', fontsize=10, ha='left')
    
    # Footer
    ax_footer = plt.subplot(4, 1, 4)
    ax_footer.set_xlim(0, 10)
    ax_footer.set_ylim(0, 2)
    ax_footer.axis('off')
    
    # Footer box
    footer_box = FancyBboxPatch((0.5, 0.5), 9, 1, boxstyle="round,pad=0.1", 
                               facecolor=colors['dark_green'], alpha=0.1, 
                               edgecolor=colors['dark_green'], linewidth=2)
    ax_footer.add_patch(footer_box)
    ax_footer.text(5, 1.2, 'WildID - Wildlife Identification App', fontsize=14, fontweight='bold', 
                  ha='center', color=colors['dark_green'])
    ax_footer.text(5, 0.8, 'AI-Powered Species Identification • Interactive Habitat Mapping • Advanced Security', 
                  fontsize=10, ha='center', color=colors['gray'])
    ax_footer.text(5, 0.6, 'Built with Flask, Together.ai, Docker, and Kubernetes', 
                  fontsize=9, ha='center', color=colors['gray'], style='italic')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.subplots_adjust(top=0.95, hspace=0.3, wspace=0.3)
    
    # Save as high-quality PNG
    plt.savefig('/workspace/wildid_design_document.png', 
                dpi=300, bbox_inches='tight', facecolor='white', 
                edgecolor='none', pad_inches=0.2)
    
    print("✅ Design document generated successfully!")
    print("📁 Saved as: wildid_design_document.png")
    print("📊 Document includes:")
    print("   • Application overview and features")
    print("   • Technology stack and architecture")
    print("   • Security features and implementation")
    print("   • UI components and design system")
    print("   • Data flow and processing pipeline")
    print("   • Project structure and file organization")
    print("   • Deployment and infrastructure setup")
    
    return fig

if __name__ == "__main__":
    create_design_document()