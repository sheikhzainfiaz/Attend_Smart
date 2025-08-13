
# Attend Smart <img src="https://github.com/sheikhzainfiaz/Attend_Smart/blob/3d5e993469f5d7125432527a997372cd642babe5/assets/logo.png" alt="Attend Smart Logo" width="60"/>


**Attend Smart** is a **face recognition–based attendance system** designed with advanced security and user-friendly features.  
It automates attendance tracking for classes, ensuring accuracy and real-time record-keeping.  
The system was developed with integration for **National Textile University (NTU)** validations, but it can be adapted for other institutions.

---

## 📌 Features

- 🎯 **Face Recognition Attendance**
  - Built using the [`face_recognition`](https://github.com/ageitgey/face_recognition) library.
  - Detects and verifies student faces in real time.

- 🛡 **University System Validation**
  - Attendance and logins are validated against official university records.

- 📧 **Secure Email Notifications**
  - Integrated with **SendGrid API** to send:
    - Teacher credentials upon account creation.
    - Login notifications for security.
  
- 📊 **Attendance Export**
  - Teachers can export attendance data for **any selected day** in **Excel format**.

- ⚡ **Fast UI**
  - Built using the [Flet](https://flet.dev) Python framework for a responsive and modern interface.

---

## 🛠 Tech Stack

| Component            | Technology |
|----------------------|------------|
| **Language**         | Python     |
| **Database**         | MySQL      |
| **UI Framework**     | Flet       |
| **Face Recognition** | face_recognition library |
| **Email Service**    | SendGrid API |

---


## 📸 Screenshots

### 1. Login Page

![Login Page Screenshot](path/to/login_screenshot.png)

### 2. Dashboard

![Dashboard Screenshot](path/to/dashboard_screenshot.png)

### 3. Face Recognition Attendance

![Face Recognition Screenshot](path/to/face_recognition_screenshot.png)

### 4. Export Attendance Excel

![Export Screenshot](path/to/export_screenshot.png)

---

## ⚙️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/attend_smart.git
   cd attend_smart
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure MySQL Database**

   * Create a database in MySQL for Attend Smart.
   * Import the provided `.sql` file from the `database` folder.

4. **Configure SendGrid**

   * Get an API key from [SendGrid](https://sendgrid.com).
   * Set it in your environment variables:

     ```bash
     export SENDGRID_API_KEY="your_api_key_here"
     ```

5. **Run the application**

   ```bash
   python main.py
   ```

---

## 📧 Email Notification Flow

* **On Teacher Account Creation** → Credentials sent via SendGrid email.
* **On Teacher Login** → Security email sent to the registered email address.

---

## ✨ Authors

* **Sheikh Zain Fiaz** – 
* **Team Members** – \Muhammad Talha, Taha Manshoor

---

## 📜 License

This project is open source — you may modify and adapt it as per your needs.

```
Don't misuse the project
```
