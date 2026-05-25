# 📶 wifi-attendance

<div align="center">

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" />
<img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
<img src="https://img.shields.io/badge/UI--Design-Glassmorphism-a855f7?style=for-the-badge" />

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


## 👤 Author

[![Github](https://img.shields.io/badge/GitHub-181717?style=plastic&logo=github&logoColor=white)](https://github.com/ajit3xh)
[![Project](https://img.shields.io/badge/Project-Repository-blue?style=plastic&logo=github&logoColor=white)](https://github.com/ajit3xh/wifi_attendance.git)
