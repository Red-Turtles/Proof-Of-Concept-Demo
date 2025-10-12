#!/usr/bin/env python3
"""
WildID Visual Design Document Generator
Creates a visual mockup-style design document showing the actual webpage appearance
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Arrow, Polygon
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import seaborn as sns

# Set up the figure with high DPI for crisp output
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 9
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
    'slate': '#1e293b',
    'light_gray': '#f8fffe'
}

def create_visual_design_document():
    """Create a visual design document showing webpage appearance"""
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(24, 32))
    fig.patch.set_facecolor('white')
    
    # Main title
    fig.suptitle('WildID - Visual Design & UI Mockups\nWildlife Identification App Interface Design', 
                 fontsize=28, fontweight='bold', color=colors['dark_green'], y=0.98)
    
    # 1. Header Navigation Bar
    ax1 = plt.subplot(6, 3, 1)
    ax1.set_xlim(0, 12)
    ax1.set_ylim(0, 8)
    ax1.axis('off')
    
    # Header background
    header_bg = Rectangle((0, 0), 12, 8, facecolor=colors['dark_green'], alpha=0.9)
    ax1.add_patch(header_bg)
    
    # Logo
    logo_circle = Circle((1.5, 4), 0.8, facecolor=colors['yellow'], alpha=0.8)
    ax1.add_patch(logo_circle)
    ax1.text(1.5, 4, '🍃', fontsize=16, ha='center', va='center')
    ax1.text(2.8, 4, 'WildID', fontsize=18, fontweight='bold', ha='left', va='center', color=colors['white'])
    
    # Navigation links
    nav_links = ['Home', 'Discovery', 'Tell Us What You Saw', 'Contact']
    for i, link in enumerate(nav_links):
        x = 6 + i * 1.2
        nav_box = FancyBboxPatch((x, 3), 1, 2, boxstyle="round,pad=0.1", 
                                facecolor=colors['medium_green'] if i == 0 else 'none', 
                                edgecolor='none', linewidth=0)
        ax1.add_patch(nav_box)
        ax1.text(x+0.5, 4, link, fontsize=10, ha='center', va='center', 
                color=colors['white'], fontweight='bold' if i == 0 else 'normal')
    
    ax1.text(6, 7.5, 'Header Navigation', fontsize=14, fontweight='bold', ha='center', color=colors['white'])
    
    # 2. Hero Section
    ax2 = plt.subplot(6, 3, 2)
    ax2.set_xlim(0, 12)
    ax2.set_ylim(0, 8)
    ax2.axis('off')
    
    # Hero background with gradient effect
    hero_bg = Rectangle((0, 0), 12, 8, facecolor=colors['dark_green'], alpha=0.8)
    ax2.add_patch(hero_bg)
    
    # Decorative elements
    for i in range(5):
        x = np.random.uniform(1, 11)
        y = np.random.uniform(1, 7)
        size = np.random.uniform(0.3, 0.8)
        circle = Circle((x, y), size, facecolor=colors['light_green'], alpha=0.3)
        ax2.add_patch(circle)
    
    # Hero content
    ax2.text(6, 6.5, 'Discover the Wild', fontsize=20, fontweight='bold', ha='center', 
             color=colors['white'])
    ax2.text(6, 5.8, 'Identify animals instantly with AI-powered recognition.', 
             fontsize=12, ha='center', color=colors['white'], alpha=0.9)
    ax2.text(6, 5.4, 'Learn about wildlife, conservation, and share your discoveries.', 
             fontsize=12, ha='center', color=colors['white'], alpha=0.9)
    
    # Hero buttons
    btn1 = FancyBboxPatch((4, 3.5), 3, 1, boxstyle="round,pad=0.1", 
                         facecolor=colors['yellow'], alpha=0.9, 
                         edgecolor=colors['dark_green'], linewidth=1)
    ax2.add_patch(btn1)
    ax2.text(5.5, 4, 'Start Identifying', fontsize=11, fontweight='bold', ha='center', va='center')
    
    btn2 = FancyBboxPatch((7, 3.5), 3, 1, boxstyle="round,pad=0.1", 
                         facecolor='none', alpha=0.9, 
                         edgecolor=colors['white'], linewidth=2)
    ax2.add_patch(btn2)
    ax2.text(8.5, 4, 'Share a Sighting', fontsize=11, fontweight='bold', ha='center', va='center', 
             color=colors['white'])
    
    ax2.text(6, 7.5, 'Hero Section', fontsize=14, fontweight='bold', ha='center', color=colors['white'])
    
    # 3. Feature Cards Section
    ax3 = plt.subplot(6, 3, 3)
    ax3.set_xlim(0, 12)
    ax3.set_ylim(0, 8)
    ax3.axis('off')
    
    # Background
    ax3.set_facecolor(colors['light_gray'])
    
    # Section title
    ax3.text(6, 7.5, 'How WildID Works', fontsize=16, fontweight='bold', ha='center', color=colors['dark_green'])
    
    # Feature cards
    features = [
        ('AI Identification', '📷', 'Upload a photo and let our AI identify the animal instantly'),
        ('Location Mapping', '🗺️', 'See where animals naturally live on an interactive map'),
        ('Conservation Info', '❤️', 'Learn about conservation status and how to help'),
        ('Community', '👥', 'Share your wildlife sightings with fellow nature enthusiasts')
    ]
    
    for i, (title, icon, desc) in enumerate(features):
        x = 1 + (i % 2) * 5
        y = 5.5 - (i // 2) * 2.5
        
        # Card background
        card = FancyBboxPatch((x, y), 4, 2, boxstyle="round,pad=0.1", 
                             facecolor=colors['white'], alpha=0.9, 
                             edgecolor=colors['gray'], linewidth=1)
        ax3.add_patch(card)
        
        # Card icon
        ax3.text(x+2, y+1.5, icon, fontsize=20, ha='center', va='center')
        
        # Card title
        ax3.text(x+2, y+1.2, title, fontsize=11, fontweight='bold', ha='center', va='center', 
                color=colors['dark_green'])
        
        # Card description
        ax3.text(x+0.2, y+0.6, desc, fontsize=8, ha='left', va='top', 
                color=colors['gray'], wrap=True)
    
    # 4. Upload Interface
    ax4 = plt.subplot(6, 3, 4)
    ax4.set_xlim(0, 12)
    ax4.set_ylim(0, 8)
    ax4.axis('off')
    
    # Background
    ax4.set_facecolor(colors['light_gray'])
    
    # Title
    ax4.text(6, 7.5, 'Animal Discovery - Upload Interface', fontsize=14, fontweight='bold', ha='center', color=colors['dark_green'])
    
    # Upload card
    upload_card = FancyBboxPatch((1, 2), 10, 5, boxstyle="round,pad=0.2", 
                                facecolor=colors['white'], alpha=0.9, 
                                edgecolor=colors['gray'], linewidth=1)
    ax4.add_patch(upload_card)
    
    # Upload area
    upload_area = FancyBboxPatch((2, 4), 8, 2, boxstyle="round,pad=0.1", 
                                facecolor=colors['light_gray'], alpha=0.5, 
                                edgecolor=colors['gray'], linewidth=2, linestyle='--')
    ax4.add_patch(upload_area)
    
    # Upload icon and text
    ax4.text(6, 5.2, '⬆', fontsize=24, ha='center', va='center', color=colors['dark_gray'])
    ax4.text(6, 4.8, 'Click to upload or drag and drop', fontsize=11, fontweight='bold', ha='center', va='center', color=colors['dark_green'])
    ax4.text(6, 4.5, 'PNG, JPG, or WEBP (MAX. 16MB)', fontsize=9, ha='center', va='center', color=colors['gray'])
    
    # Submit button
    submit_btn = FancyBboxPatch((4, 2.5), 4, 0.8, boxstyle="round,pad=0.1", 
                               facecolor=colors['yellow'], alpha=0.9, 
                               edgecolor=colors['dark_green'], linewidth=1)
    ax4.add_patch(submit_btn)
    ax4.text(6, 2.9, 'Identify Animal', fontsize=11, fontweight='bold', ha='center', va='center')
    
    # 5. Results Page Layout
    ax5 = plt.subplot(6, 3, 5)
    ax5.set_xlim(0, 12)
    ax5.set_ylim(0, 8)
    ax5.axis('off')
    
    # Background
    ax5.set_facecolor(colors['light_gray'])
    
    # Title
    ax5.text(6, 7.5, 'Results Page Layout', fontsize=14, fontweight='bold', ha='center', color=colors['dark_green'])
    
    # Results hero
    results_hero = FancyBboxPatch((1, 5.5), 10, 1.5, boxstyle="round,pad=0.1", 
                                 facecolor=colors['medium_green'], alpha=0.8, 
                                 edgecolor=colors['dark_green'], linewidth=1)
    ax5.add_patch(results_hero)
    
    ax5.text(6, 6.5, 'African Lion', fontsize=16, fontweight='bold', ha='center', va='center', color=colors['white'])
    ax5.text(6, 6.1, 'Species identification complete', fontsize=10, ha='center', va='center', color=colors['white'])
    
    # Confidence badge
    conf_badge = FancyBboxPatch((8.5, 5.8), 2, 0.6, boxstyle="round,pad=0.05", 
                               facecolor=colors['light_green'], alpha=0.9, 
                               edgecolor=colors['dark_green'], linewidth=1)
    ax5.add_patch(conf_badge)
    ax5.text(9.5, 6.1, '🟢 High Confidence', fontsize=8, fontweight='bold', ha='center', va='center')
    
    # Results grid
    # Image card
    img_card = FancyBboxPatch((1, 2.5), 5, 2.5, boxstyle="round,pad=0.1", 
                             facecolor=colors['white'], alpha=0.9, 
                             edgecolor=colors['gray'], linewidth=1)
    ax5.add_patch(img_card)
    ax5.text(3.5, 4.2, '📷', fontsize=20, ha='center', va='center')
    ax5.text(3.5, 3.8, 'Uploaded Image', fontsize=10, fontweight='bold', ha='center', va='center', color=colors['dark_green'])
    ax5.text(3.5, 3.5, 'AI Analysis', fontsize=8, ha='center', va='center', color=colors['gray'])
    
    # Species card
    species_card = FancyBboxPatch((6.5, 2.5), 5, 2.5, boxstyle="round,pad=0.1", 
                                 facecolor=colors['white'], alpha=0.9, 
                                 edgecolor=colors['gray'], linewidth=1)
    ax5.add_patch(species_card)
    ax5.text(9, 4.2, '🔬', fontsize=20, ha='center', va='center')
    ax5.text(9, 3.8, 'Species Analysis', fontsize=10, fontweight='bold', ha='center', va='center', color=colors['dark_green'])
    ax5.text(7, 3.5, 'Species: Panthera leo', fontsize=8, ha='left', va='center')
    ax5.text(7, 3.2, 'Common: African Lion', fontsize=8, ha='left', va='center')
    ax5.text(7, 2.9, 'Type: Mammal', fontsize=8, ha='left', va='center')
    
    # 6. Interactive Map Interface
    ax6 = plt.subplot(6, 3, 6)
    ax6.set_xlim(0, 12)
    ax6.set_ylim(0, 8)
    ax6.axis('off')
    
    # Background
    ax6.set_facecolor(colors['slate'])
    
    # Title
    ax6.text(6, 7.5, 'Interactive Habitat Map', fontsize=14, fontweight='bold', ha='center', color=colors['white'])
    
    # Map container
    map_container = FancyBboxPatch((1, 2), 10, 5, boxstyle="round,pad=0.1", 
                                  facecolor=colors['dark_gray'], alpha=0.8, 
                                  edgecolor=colors['gray'], linewidth=1)
    ax6.add_patch(map_container)
    
    # Map controls
    controls = ['🎯 Show All', '👁️ Toggle', '🔄 Reset']
    for i, control in enumerate(controls):
        control_btn = FancyBboxPatch((9, 6-i*0.8), 1.5, 0.6, boxstyle="round,pad=0.05", 
                                    facecolor=colors['black'], alpha=0.8, 
                                    edgecolor=colors['gray'], linewidth=1)
        ax6.add_patch(control_btn)
        ax6.text(9.75, 6.3-i*0.8, control, fontsize=7, ha='center', va='center', color=colors['white'])
    
    # Map markers (simulated)
    for i in range(8):
        x = np.random.uniform(2, 10)
        y = np.random.uniform(3, 6)
        marker = Circle((x, y), 0.15, facecolor=colors['yellow'], alpha=0.8)
        ax6.add_patch(marker)
    
    # Habitat info panel
    habitat_panel = FancyBboxPatch((1.5, 2.2), 7, 0.6, boxstyle="round,pad=0.05", 
                                  facecolor=colors['black'], alpha=0.8, 
                                  edgecolor=colors['gray'], linewidth=1)
    ax6.add_patch(habitat_panel)
    ax6.text(5, 2.5, '📍 4 Habitat Locations Found', fontsize=9, ha='center', va='center', color=colors['white'])
    
    # 7. Mobile Responsive Design
    ax7 = plt.subplot(6, 3, 7)
    ax7.set_xlim(0, 12)
    ax7.set_ylim(0, 8)
    ax7.axis('off')
    
    # Background
    ax7.set_facecolor(colors['light_gray'])
    
    # Title
    ax7.text(6, 7.5, 'Mobile Responsive Design', fontsize=14, fontweight='bold', ha='center', color=colors['dark_green'])
    
    # Mobile phone frame
    phone_frame = FancyBboxPatch((2, 1), 3, 6, boxstyle="round,pad=0.1", 
                                facecolor=colors['black'], alpha=0.9, 
                                edgecolor=colors['dark_gray'], linewidth=3)
    ax7.add_patch(phone_frame)
    
    # Mobile screen
    mobile_screen = FancyBboxPatch((2.2, 1.5), 2.6, 5, boxstyle="round,pad=0.05", 
                                  facecolor=colors['white'], alpha=0.9, 
                                  edgecolor=colors['gray'], linewidth=1)
    ax7.add_patch(mobile_screen)
    
    # Mobile header
    mobile_header = Rectangle((2.2, 5.5), 2.6, 1, facecolor=colors['dark_green'], alpha=0.9)
    ax7.add_patch(mobile_header)
    ax7.text(3.5, 6, '🍃 WildID', fontsize=10, fontweight='bold', ha='center', va='center', color=colors['white'])
    
    # Mobile content
    ax7.text(3.5, 5, 'Discover the Wild', fontsize=8, fontweight='bold', ha='center', va='center', color=colors['dark_green'])
    ax7.text(3.5, 4.6, 'Upload animal photo', fontsize=6, ha='center', va='center', color=colors['gray'])
    
    # Mobile upload area
    mobile_upload = FancyBboxPatch((2.5, 3.5), 2, 1, boxstyle="round,pad=0.05", 
                                  facecolor=colors['light_gray'], alpha=0.5, 
                                  edgecolor=colors['gray'], linewidth=1, linestyle='--')
    ax7.add_patch(mobile_upload)
    ax7.text(3.5, 4, '⬆', fontsize=12, ha='center', va='center', color=colors['dark_gray'])
    
    # Mobile button
    mobile_btn = FancyBboxPatch((2.7, 2.5), 1.6, 0.6, boxstyle="round,pad=0.05", 
                               facecolor=colors['yellow'], alpha=0.9, 
                               edgecolor=colors['dark_green'], linewidth=1)
    ax7.add_patch(mobile_btn)
    ax7.text(3.5, 2.8, 'Identify', fontsize=7, fontweight='bold', ha='center', va='center')
    
    # Desktop comparison
    desktop_frame = FancyBboxPatch((6.5, 2), 4.5, 5, boxstyle="round,pad=0.1", 
                                  facecolor=colors['white'], alpha=0.9, 
                                  edgecolor=colors['gray'], linewidth=2)
    ax7.add_patch(desktop_frame)
    
    # Desktop header
    desktop_header = Rectangle((6.5, 6), 4.5, 1, facecolor=colors['dark_green'], alpha=0.9)
    ax7.add_patch(desktop_header)
    ax7.text(8.75, 6.5, '🍃 WildID - Full Desktop Experience', fontsize=8, fontweight='bold', ha='center', va='center', color=colors['white'])
    
    # Desktop content
    ax7.text(8.75, 5.5, 'Discover the Wild', fontsize=12, fontweight='bold', ha='center', va='center', color=colors['dark_green'])
    ax7.text(8.75, 5.1, 'Identify animals instantly with AI-powered recognition', fontsize=8, ha='center', va='center', color=colors['gray'])
    
    # Desktop buttons
    desktop_btn1 = FancyBboxPatch((7, 4), 1.8, 0.6, boxstyle="round,pad=0.05", 
                                 facecolor=colors['yellow'], alpha=0.9, 
                                 edgecolor=colors['dark_green'], linewidth=1)
    ax7.add_patch(desktop_btn1)
    ax7.text(7.9, 4.3, 'Start Identifying', fontsize=7, fontweight='bold', ha='center', va='center')
    
    desktop_btn2 = FancyBboxPatch((9.2, 4), 1.8, 0.6, boxstyle="round,pad=0.05", 
                                 facecolor='none', alpha=0.9, 
                                 edgecolor=colors['dark_green'], linewidth=1)
    ax7.add_patch(desktop_btn2)
    ax7.text(10.1, 4.3, 'Share Sighting', fontsize=7, fontweight='bold', ha='center', va='center', color=colors['dark_green'])
    
    # 8. Color Palette & Typography
    ax8 = plt.subplot(6, 3, 8)
    ax8.set_xlim(0, 12)
    ax8.set_ylim(0, 8)
    ax8.axis('off')
    
    # Background
    ax8.set_facecolor(colors['light_gray'])
    
    # Title
    ax8.text(6, 7.5, 'Design System - Colors & Typography', fontsize=14, fontweight='bold', ha='center', color=colors['dark_green'])
    
    # Color palette
    color_palette = [
        (colors['dark_green'], 'Dark Green', '#1a4d3a'),
        (colors['medium_green'], 'Medium Green', '#2d6a4f'),
        (colors['light_green'], 'Light Green', '#52c41a'),
        (colors['yellow'], 'Yellow Accent', '#ffd84d'),
        (colors['slate'], 'Slate', '#1e293b'),
        (colors['gray'], 'Gray', '#6b7280')
    ]
    
    for i, (color, name, hex_code) in enumerate(color_palette):
        x = 1 + (i % 3) * 3.5
        y = 6 - (i // 3) * 1.5
        
        # Color swatch
        color_rect = Rectangle((x, y), 1.5, 0.8, facecolor=color, edgecolor=colors['black'], linewidth=1)
        ax8.add_patch(color_rect)
        ax8.text(x+0.75, y+0.4, name, fontsize=9, fontweight='bold', ha='center', va='center', 
                color=colors['white'] if color in [colors['dark_green'], colors['slate']] else colors['black'])
        ax8.text(x+0.75, y+0.1, hex_code, fontsize=7, ha='center', va='center', color=colors['gray'])
    
    # Typography examples
    ax8.text(1, 3.5, 'Typography:', fontsize=12, fontweight='bold', ha='left', color=colors['dark_green'])
    ax8.text(1, 3, 'Main Heading (24px, Bold)', fontsize=12, fontweight='bold', ha='left', color=colors['dark_green'])
    ax8.text(1, 2.6, 'Section Heading (16px, Bold)', fontsize=10, fontweight='bold', ha='left', color=colors['dark_green'])
    ax8.text(1, 2.2, 'Body Text (10px, Regular)', fontsize=8, ha='left', color=colors['black'])
    ax8.text(1, 1.8, 'Small Text (8px, Regular)', fontsize=6, ha='left', color=colors['gray'])
    
    # 9. Security Features UI
    ax9 = plt.subplot(6, 3, 9)
    ax9.set_xlim(0, 12)
    ax9.set_ylim(0, 8)
    ax9.axis('off')
    
    # Background
    ax9.set_facecolor(colors['light_gray'])
    
    # Title
    ax9.text(6, 7.5, 'Security Features UI', fontsize=14, fontweight='bold', ha='center', color=colors['dark_green'])
    
    # Security status
    security_status = FancyBboxPatch((1, 5.5), 10, 1, boxstyle="round,pad=0.1", 
                                    facecolor=colors['yellow'], alpha=0.2, 
                                    edgecolor=colors['dark_green'], linewidth=2)
    ax9.add_patch(security_status)
    ax9.text(6, 6, '🔒 Security verification required', fontsize=11, fontweight='bold', ha='center', va='center', color=colors['dark_green'])
    
    # CAPTCHA section
    captcha_section = FancyBboxPatch((1, 3.5), 10, 1.5, boxstyle="round,pad=0.1", 
                                    facecolor=colors['white'], alpha=0.9, 
                                    edgecolor=colors['gray'], linewidth=1)
    ax9.add_patch(captcha_section)
    
    ax9.text(6, 4.7, 'Security Verification', fontsize=12, fontweight='bold', ha='center', va='center', color=colors['dark_green'])
    ax9.text(6, 4.3, 'Please solve the math problem to continue:', fontsize=9, ha='center', va='center', color=colors['gray'])
    
    # CAPTCHA challenge
    captcha_challenge = FancyBboxPatch((4, 3.8), 2, 0.6, boxstyle="round,pad=0.05", 
                                      facecolor=colors['light_gray'], alpha=0.5, 
                                      edgecolor=colors['gray'], linewidth=1)
    ax9.add_patch(captcha_challenge)
    ax9.text(5, 4.1, '7 + 3 = ?', fontsize=10, fontweight='bold', ha='center', va='center', color=colors['dark_green'])
    
    # CAPTCHA input
    captcha_input = FancyBboxPatch((6.5, 3.8), 1.5, 0.6, boxstyle="round,pad=0.05", 
                                  facecolor=colors['white'], alpha=0.9, 
                                  edgecolor=colors['gray'], linewidth=1)
    ax9.add_patch(captcha_input)
    ax9.text(7.25, 4.1, '10', fontsize=9, ha='center', va='center', color=colors['gray'])
    
    # Verify button
    verify_btn = FancyBboxPatch((8.5, 3.8), 1.5, 0.6, boxstyle="round,pad=0.05", 
                               facecolor=colors['yellow'], alpha=0.9, 
                               edgecolor=colors['dark_green'], linewidth=1)
    ax9.add_patch(verify_btn)
    ax9.text(9.25, 4.1, 'Verify', fontsize=9, fontweight='bold', ha='center', va='center')
    
    # Security note
    ax9.text(6, 3.2, 'After 2 image identifications, additional verification may be required.', 
             fontsize=8, ha='center', va='center', color=colors['gray'], style='italic')
    
    # 10. Call to Action Section
    ax10 = plt.subplot(6, 3, 10)
    ax10.set_xlim(0, 12)
    ax10.set_ylim(0, 8)
    ax10.axis('off')
    
    # Background
    ax10.set_facecolor(colors['yellow'])
    ax10.set_alpha(0.1)
    
    # CTA content
    ax10.text(6, 6, 'Ready to Explore Wildlife?', fontsize=18, fontweight='bold', ha='center', va='center', color=colors['dark_green'])
    ax10.text(6, 5.3, 'Join thousands of nature enthusiasts discovering and learning about animals worldwide.', 
              fontsize=11, ha='center', va='center', color=colors['gray'])
    
    # CTA button
    cta_btn = FancyBboxPatch((4.5, 4), 3, 1, boxstyle="round,pad=0.1", 
                            facecolor=colors['medium_green'], alpha=0.9, 
                            edgecolor=colors['dark_green'], linewidth=2)
    ax10.add_patch(cta_btn)
    ax10.text(6, 4.5, 'Get Started Now', fontsize=12, fontweight='bold', ha='center', va='center', color=colors['white'])
    
    ax10.text(6, 7.5, 'Call to Action Section', fontsize=14, fontweight='bold', ha='center', color=colors['dark_green'])
    
    # 11. Footer Design
    ax11 = plt.subplot(6, 3, 11)
    ax11.set_xlim(0, 12)
    ax11.set_ylim(0, 8)
    ax11.axis('off')
    
    # Footer background
    footer_bg = Rectangle((0, 0), 12, 8, facecolor=colors['dark_green'], alpha=0.9)
    ax11.add_patch(footer_bg)
    
    # Footer content
    ax11.text(6, 6, 'WildID • Wildlife Identification • Auto file cleanup • Interactive habitat mapping', 
              fontsize=10, ha='center', va='center', color=colors['white'])
    
    # Footer links (simulated)
    footer_links = ['Privacy Policy', 'Terms of Service', 'Contact', 'About']
    for i, link in enumerate(footer_links):
        x = 2 + i * 2
        ax11.text(x, 4.5, link, fontsize=9, ha='center', va='center', color=colors['white'], alpha=0.8)
    
    # Copyright
    ax11.text(6, 3, '© 2024 WildID. All rights reserved.', fontsize=8, ha='center', va='center', color=colors['white'], alpha=0.7)
    
    ax11.text(6, 7.5, 'Footer Design', fontsize=14, fontweight='bold', ha='center', color=colors['white'])
    
    # 12. Interactive Elements & States
    ax12 = plt.subplot(6, 3, 12)
    ax12.set_xlim(0, 12)
    ax12.set_ylim(0, 8)
    ax12.axis('off')
    
    # Background
    ax12.set_facecolor(colors['light_gray'])
    
    # Title
    ax12.text(6, 7.5, 'Interactive Elements & States', fontsize=14, fontweight='bold', ha='center', color=colors['dark_green'])
    
    # Button states
    ax12.text(1, 6.5, 'Button States:', fontsize=11, fontweight='bold', ha='left', color=colors['dark_green'])
    
    # Normal button
    normal_btn = FancyBboxPatch((1, 5.5), 2, 0.6, boxstyle="round,pad=0.05", 
                               facecolor=colors['yellow'], alpha=0.9, 
                               edgecolor=colors['dark_green'], linewidth=1)
    ax12.add_patch(normal_btn)
    ax12.text(2, 5.8, 'Normal', fontsize=8, fontweight='bold', ha='center', va='center')
    
    # Hover button
    hover_btn = FancyBboxPatch((3.5, 5.5), 2, 0.6, boxstyle="round,pad=0.05", 
                              facecolor=colors['yellow'], alpha=0.7, 
                              edgecolor=colors['dark_green'], linewidth=2)
    ax12.add_patch(hover_btn)
    ax12.text(4.5, 5.8, 'Hover', fontsize=8, fontweight='bold', ha='center', va='center')
    
    # Disabled button
    disabled_btn = FancyBboxPatch((6, 5.5), 2, 0.6, boxstyle="round,pad=0.05", 
                                 facecolor=colors['gray'], alpha=0.5, 
                                 edgecolor=colors['dark_gray'], linewidth=1)
    ax12.add_patch(disabled_btn)
    ax12.text(7, 5.8, 'Disabled', fontsize=8, fontweight='bold', ha='center', va='center', color=colors['white'])
    
    # Upload area states
    ax12.text(1, 4.5, 'Upload Area States:', fontsize=11, fontweight='bold', ha='left', color=colors['dark_green'])
    
    # Normal upload
    normal_upload = FancyBboxPatch((1, 3.5), 3, 0.8, boxstyle="round,pad=0.05", 
                                  facecolor=colors['light_gray'], alpha=0.5, 
                                  edgecolor=colors['gray'], linewidth=1, linestyle='--')
    ax12.add_patch(normal_upload)
    ax12.text(2.5, 3.9, 'Normal Upload', fontsize=8, ha='center', va='center', color=colors['gray'])
    
    # Hover upload
    hover_upload = FancyBboxPatch((4.5, 3.5), 3, 0.8, boxstyle="round,pad=0.05", 
                                 facecolor=colors['yellow'], alpha=0.2, 
                                 edgecolor=colors['yellow'], linewidth=2, linestyle='--')
    ax12.add_patch(hover_upload)
    ax12.text(6, 3.9, 'Hover Upload', fontsize=8, ha='center', va='center', color=colors['dark_green'])
    
    # Drag over upload
    dragover_upload = FancyBboxPatch((8, 3.5), 3, 0.8, boxstyle="round,pad=0.05", 
                                    facecolor=colors['yellow'], alpha=0.3, 
                                    edgecolor=colors['yellow'], linewidth=2, linestyle='-')
    ax12.add_patch(dragover_upload)
    ax12.text(9.5, 3.9, 'Drag Over', fontsize=8, ha='center', va='center', color=colors['dark_green'])
    
    # File info display
    ax12.text(1, 2.5, 'File Info Display:', fontsize=11, fontweight='bold', ha='left', color=colors['dark_green'])
    
    file_info = FancyBboxPatch((1, 1.5), 6, 0.8, boxstyle="round,pad=0.05", 
                              facecolor=colors['slate'], alpha=0.8, 
                              edgecolor=colors['dark_gray'], linewidth=1)
    ax12.add_patch(file_info)
    ax12.text(4, 1.9, 'animal-photo.jpg ✕', fontsize=9, ha='center', va='center', color=colors['white'])
    
    # Adjust layout and save
    plt.tight_layout()
    plt.subplots_adjust(top=0.95, hspace=0.4, wspace=0.3)
    
    # Save as high-quality PNG
    plt.savefig('/workspace/wildid_visual_design.png', 
                dpi=300, bbox_inches='tight', facecolor='white', 
                edgecolor='none', pad_inches=0.2)
    
    print("✅ Visual design document generated successfully!")
    print("📁 Saved as: wildid_visual_design.png")
    print("🎨 Document includes:")
    print("   • Header navigation bar design")
    print("   • Hero section with call-to-action")
    print("   • Feature cards layout")
    print("   • Upload interface mockup")
    print("   • Results page layout")
    print("   • Interactive habitat map interface")
    print("   • Mobile responsive design")
    print("   • Color palette and typography")
    print("   • Security features UI")
    print("   • Call-to-action section")
    print("   • Footer design")
    print("   • Interactive elements and states")
    
    return fig

if __name__ == "__main__":
    create_visual_design_document()