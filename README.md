# 🧹 Clean Bengaluru

A full-stack civic-tech web application that empowers citizens to report uncollected garbage spots directly to municipal authorities (BBMP). The platform enables real-time tracking of complaints and ensures accountability through automated escalation mechanisms.

## 🚀 Overview

Clean Bengaluru bridges the gap between citizens and city authorities by providing a simple, map-based reporting system. Users can mark garbage locations, upload images, and monitor resolution status—helping improve urban cleanliness and responsiveness.

## ✨ Key Features
- 🗺️ **Interactive Map Reporting**
  - Users can drop a pin on the map to mark exact garbage locations using Google Maps.
- 📍 **Geocoding & Reverse Geocoding**
  - Automatically converts coordinates into readable addresses and vice versa, making reports easier to understand for authorities.
- 📸 **Image Upload System**
  - Upload “before” and “after” images with validation for secure handling.
- 📊 **Real-Time Status Tracking**
  - Track complaints visually with status indicators (Pending → Resolved).
- 📧 **Automated Email Escalation**
  - Smart reminders and escalation emails sent if issues remain unresolved (2, 4, 7 days).
- 📱 **Modern Responsive UI**
  - Clean glassmorphism design optimized for both desktop and mobile devices.
- 🔒 **Data Validation & Security**
  - Ensures only valid inputs and file formats are accepted.

## 🧠 Tech Stack
- Frontend: HTML, CSS, JavaScript
- Backend: Python (Flask)
- Database: SQLite
- Maps Integration: Google Maps JavaScript API (Geocoding API)
- Task Scheduling: APScheduler
- Email Service: SMTP (Gmail)
- Other Tools: Jinja2, Flask Extensions

## 🎯 Impact
- Encourages citizen participation in maintaining city cleanliness.
- Improves transparency in municipal waste management.
- Reduces resolution delays through automated escalation.
- Scalable for other smart city initiatives.
