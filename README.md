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

## 🛠️ Local Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/appu-ui/clean_bengaluru.git
   cd clean_bengaluru
   ```

2. **Set up a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   # source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root of the project with your configurations. E.g.:
   ```env
   GOOGLE_MAPS_API_KEY=your_actual_api_key_here
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   ```

---

## 🏁 Running the Application

1. **Start the Flask Application**:
   ```bash
   python app.py
   ```
   *The SQLite database (`database.db`) will be automatically created on the first run.*

2. **Access the Web App**:
   Open a browser and navigate to: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

- Email Service: SMTP (Gmail)
- Other Tools: Jinja2, Flask Extensions

## 🎯 Impact
- Encourages citizen participation in maintaining city cleanliness.
- Improves transparency in municipal waste management.
- Reduces resolution delays through automated escalation.
- Scalable for other smart city initiatives.
  **live link:clean-bengaluru-beta.vercel.app**
