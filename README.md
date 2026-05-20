# 📶 wifi-attendance

<div align="center">

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
<img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
<img src="https://img.shields.io/badge/UI--Design-Material--3-1A237E?style=for-the-badge" />

</div>

## 📌 Overview

**wifi-attendance** is a modern, premium attendance tracking system designed for secure, local-network-only presence verification. By validating that participants are on the same WiFi network as the host, it prevents remote attendance fraud and ensures physical presence in meetings or classrooms.

## 🎯 Objectives

1.  **Secure Attendance**: Ensure participants are physically present on-site.
2.  **Real-Time Engagement**: Provide instant feedback through live attendee lists and interactive polls.
3.  **Automated Reporting**: Generate professional PDF reports with detailed join/leave timelines.

## 🛠 Features

- **🔒 Local Network Lockdown:**
  - Strict IP-based validation to ensure participants are on the same WiFi as the host.
- **⚡ Instant Joining:**
  - Join via **QR Code** or **Direct URL** in seconds.
- **📊 Advanced Reporting:**
  - Export **PDF Reports** including:
    - Multiple join/leave timestamps per user.
    - Full poll results and statistics.
- **🗳️ Interactive Polls:**
  - Create and vote in polls with real-time result visualization.
- **🎨 Premium UI:**
  - Stunning glassmorphism UI with smooth transitions and deep Light/Dark mode support.
- **🛡️ Host Controls:**
  - Hosts can instantly kick or ban users, preventing them from rejoining. Unverified users cannot view poll or attendance data.

## 📂 Project Structure

```bash
.
├── models.py           # SQLAlchemy Database Models
├── app.py              # Main Flask Application & API
├── templates/          # Jinja2 HTML Templates
│   ├── partials/       # Reusable components (e.g., header.html)
│   ├── login.html      
│   ├── signup.html
│   ├── dashboard.html
│   └── meeting_room.html
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

## 🚀 Working

1. **Host Setup**: The host creates a meeting session which captures their current network IP.
2. **Participant Access**: Participants join via a unique link or by scanning the generated QR code.
3. **WiFi Validation**: The system automatically compares the participant's network IP with the host's IP. Access is granted only if they match. Unverified users are blocked from viewing room data.
4. **Live Interaction**: Attendees can vote in polls, and the host can monitor the live attendance list. The UI updates in real-time.
5. **Session Export**: Once the meeting ends, the host can download a high-quality PDF report containing all logs and poll results.

## ⚙️ Installation & Usage

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/wifi-attendance.git
cd wifi-attendance
```

### 2. Setup Python Environment

Ensure you have Python 3.8+ installed.

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```env
PORT=3000
DATABASE_URL=sqlite:///attendance.db
JWT_SECRET=your_super_secret_jwt_key
```

### 4. Run the Application

```bash
python app.py
```

Open your browser and visit: `http://localhost:3000`

## ☁️ Deployment Guide

### For Immediate Free Deployment (Best for getting started)
**PythonAnywhere** is highly recommended for a free, zero-cost deployment using the default SQLite database. Because PythonAnywhere offers a persistent file system on their free tier, your SQLite database will not be erased when the server restarts.
1. Sign up for a free [PythonAnywhere](https://www.pythonanywhere.com/) account.
2. Upload your files and install your `requirements.txt` via their Bash console.
3. Configure the WSGI file to point to your `app.py` Flask instance.

### For Future Scalability (Production-ready)
To scale perfectly for hundreds of concurrent users without paying a dime initially, use a combination of **Render** (for hosting the app) and **Neon.tech** (for the database).
*Note: Render's free tier uses ephemeral storage, which means standard SQLite files will be wiped on every deploy. You MUST use a remote database like PostgreSQL.*

1. **Database:** Create a free serverless PostgreSQL database on [Neon.tech](https://neon.tech/) or [Supabase](https://supabase.com/). Copy the connection string.
2. **Hosting:** Create a new "Web Service" on [Render.com](https://render.com/) and connect your GitHub repository.
3. **Environment:** In Render's dashboard, add your `.env` variables. Set `DATABASE_URL` to your Neon PostgreSQL connection string.
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `gunicorn app:app`

---

## 👤 Author

[![Github](https://img.shields.io/badge/GitHub-181717?style=plastic&logo=github&logoColor=white)](https://github.com/yourusername)
[![Project](https://img.shields.io/badge/Project-Repository-blue?style=plastic&logo=github&logoColor=white)](https://github.com/yourusername/wifi-attendance)
