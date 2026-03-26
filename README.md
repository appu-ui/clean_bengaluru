# Clean Bengaluru

A full-stack web application designed to help citizens report uncollected garbage spots directly to the authorities (BBMP). The system tracks the status of reports and automatically escalates unresolved spots over email logic.

## Prerequisites
- Python 3.8+
- A Google Maps API key

## Setup Instructions

1. **Navigate to the project directory** (if not already there):
   ```bash
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
   Create a `.env` file in the root of the project with the following configuration:
   ```env
   GOOGLE_MAPS_API_KEY=your_actual_api_key_here
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   ```
   > **Note:** If using Gmail, you need to turn on 2-Factor Authentication and create an "App Password" to place in `MAIL_PASSWORD`.

## Running Locally

1. **Start the Flask Application**:
   ```bash
   python app.py
   ```
   *The SQLite database (`database.db`) will be automatically created on the first run.*

2. **Access the Web App**:
   Open a browser and navigate to: `http://127.0.0.1:5000/`

## Features Included
- **Interactive Google Map:** Click anywhere or drag the pin to set the exact coordinates of a garbage spot. Uses the latest AdvancedMarkerElement.
- **Photo Uploads:** Secure saving of "Before" and "After" photos, strictly validating for `.jpg` and `.png`.
- **Status Tracking:** Visual tracking with red (Pending) and green (Resolved) markers.
- **Email Escalation:** APScheduler runs daily to notify authorities via email after 2 days (reminder), 4 days (follow-up), and 7 days (escalation).
- **Responsive & Modern UI:** A premium, "glassmorphism" design built to wow users and look great on mobile devices.
