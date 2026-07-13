Learning Platform
# Learning Platform

A full-stack online learning platform where mentors can create courses, students can enroll and learn, and administrators can manage the platform.

---
Frontend URL: https://learning-app-eight-tan.vercel.app
Backend URL : https://learning-app-7mtx.onrender.com

## Features

### Authentication
- JWT Authentication
- Student Registration
- Mentor Registration
- Admin Login
- Role-Based Authorization
- Protected Routes

---

## Student Features

- Browse Courses
- Search Courses
- View Course Details
- Enroll in Courses
- Track Learning Progress
- Attempt Quizzes
- Download Certificates
- Review Courses
- View Announcements
- Real-time Q&A

---

## Mentor Features

- Create Courses
- Manage Modules
- Upload Lessons
- Upload Course Resources
- Create Quizzes
- View Student Progress
- Manage Announcements
- Respond to Questions

---

## Admin Features

- Approve Mentors
- Approve Courses
- View Analytics
- Manage Users
- Moderate Reviews
- Platform Dashboard

---

## Payments

- Stripe Integration
- PayPal Integration

---

## Storage

- AWS S3 File Upload
- Secure Presigned URLs

---

## Search

- Elasticsearch Integration

---

## Real-time Features

- Flask Socket.IO
- Live Course Q&A
- Notifications

---

## Tech Stack

### Frontend

- React
- Vite
- React Router
- Redux Toolkit
- Axios

### Backend

- Flask
- SQLAlchemy
- Flask-JWT-Extended
- Flask-Migrate
- Flask-Mail
- Flask-SocketIO

### Database

- PostgreSQL

### Cloud Services

- AWS S3
- Render
- Vercel

---

## Project Structure


frontend/
src/
components/
pages/
redux/
services/

backend/
app/
models/
routes/
services/
middleware/
migrations/


---

## Installation

### Backend

```bash
git clone <repo>

cd backend

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

flask db upgrade

python run.py
Frontend
cd frontend

npm install

npm run dev
Environment Variables
Backend

Create a .env file with:


SECRET_KEY=
JWT_SECRET_KEY=
DATABASE_URL=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_BUCKET_NAME=
AWS_REGION=
MAIL_SERVER=
MAIL_USERNAME=
MAIL_PASSWORD=
STRIPE_SECRET_KEY=
PAYPAL_CLIENT_ID=
PAYPAL_CLIENT_SECRET=
FRONTEND_URL=
REDIS_URL=

Frontend

VITE_API_BASE_URL=

Deployment

Frontend:Vercel

Backend:Render

Database:
PostgreSQL (Render)

Storage:
AWS S3

Author
Ajina Joseph