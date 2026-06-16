# PulseFit - Fitness Tracker Web App

PulseFit is a full-stack fitness tracking web application built with React, Express, and MySQL. It started as a basic Python terminal fitness tracker and has been upgraded into a modern web-based fitness dashboard with authentication, daily intake tracking, workout planning, and persistent database storage.

## Overview

PulseFit helps users manage simple daily fitness habits from one clean dashboard:

- Create an account and login securely
- View a weekly workout split
- Track daily calorie intake
- Track daily water intake
- Get basic recommendation messages based on user profile
- View recent intake history saved in MySQL

The app uses a modern dark fitness UI theme with responsive layouts, progress cards, and a professional dashboard-style experience.

## Tech Stack

### Frontend

- React
- Vite
- CSS3
- Local storage for session persistence

### Backend

- Node.js
- Express.js
- MySQL2
- JWT authentication
- bcrypt password hashing
- dotenv environment configuration

### Database

- MySQL
- Database name: `fitness_trac`

## Features

## 1. User Authentication

Users can register and login with:

- Username
- Password
- Age
- Weight
- Sex
- Fitness goal

Passwords are hashed using `bcryptjs` before being stored in the database. The backend returns a JWT token after successful login or registration.

## 2. Fitness Dashboard

After login, users can access a dashboard showing:

- User profile details
- Daily calorie progress
- Daily water progress
- Recommended calorie and water targets
- Recent intake history
- Weekly workout plan

## 3. Calorie Tracker

Users can enter daily calorie intake. The app compares the value against recommended ranges:

- Female: 1800-2400 calories/day
- Male: 2400-3000 calories/day

## 4. Water Tracker

Users can enter daily water intake. The app compares the value against recommended goals:

- Female: 2.7 liters/day
- Male: 3.7 liters/day

## 5. Workout Plan

The application includes a weekly workout split:

- Monday: Back Strength
- Tuesday: Chest Power
- Wednesday: Shoulders
- Thursday: Biceps
- Friday: Triceps
- Saturday: Leg Day
- Sunday: Cardio

## Project Structure

```text
FITNESS_TRACKER/
├── database.sql
├── fitness_tracker_final.py
├── index.html
├── package.json
├── README.md
├── scripts/
│   └── setupDatabase.js
├── server/
│   └── server.js
└── src/
    ├── App.jsx
    ├── main.jsx
    └── styles.css
```

## Important Files

### `fitness_tracker_final.py`

The original Python terminal-based fitness tracker. It is kept in the project for reference.

### `src/App.jsx`

Main React application. It handles:

- Login/register UI
- Dashboard rendering
- API communication
- Daily intake update
- Recent history display
- Workout plan display

### `src/styles.css`

Complete frontend styling for the modern fitness dashboard UI.

### `server/server.js`

Express backend server. It handles:

- Authentication routes
- JWT verification
- MySQL queries
- Intake tracking APIs
- Workout plan API
- Health check API

### `database.sql`

MySQL schema for creating the `fitness_trac` database and required tables.

### `scripts/setupDatabase.js`

Node.js script that imports `database.sql` and prepares the MySQL database.

## Database Schema

The app uses two main tables.

### `users`

Stores registered user details:

- `id`
- `username`
- `password_hash`
- `age`
- `weight`
- `sex`
- `goal`
- `created_at`

### `intake_logs`

Stores daily calorie and water tracking:

- `id`
- `user_id`
- `log_date`
- `calories`
- `water`
- `created_at`
- `updated_at`

Each user can have one intake log per day.

## Setup Instructions

## 1. Install Dependencies

```bash
npm install
```

## 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
PORT=5000
JWT_SECRET=replace_this_with_a_long_random_secret
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=fitness_trac
```

Update `DB_USER` and `DB_PASSWORD` according to your MySQL setup.

## 3. Create the Database

Run:

```bash
npm run db:setup
```

This creates the `fitness_trac` database and required tables.

## 4. Start the Backend

```bash
npm run server
```

Backend runs at:

```text
http://127.0.0.1:5000
```

Health check:

```text
http://127.0.0.1:5000/api/health
```

## 5. Start the Frontend

In another terminal:

```bash
npm run client
```

Frontend runs at:

```text
http://127.0.0.1:5174
```

## 6. Build for Production

```bash
npm run build
```

The production build is generated in the `dist/` folder.

## API Endpoints

### Health

```http
GET /api/health
```

Checks whether the backend and database are working.

### Register

```http
POST /api/auth/register
```

Creates a new user account.

### Login

```http
POST /api/auth/login
```

Logs in an existing user and returns a JWT token.

### Current User

```http
GET /api/me
```

Returns the authenticated user profile.

### Workout Plan

```http
GET /api/workouts
```

Returns the weekly workout plan.

### Today’s Intake

```http
GET /api/intake/today
```

Returns today’s calorie and water intake.

```http
PUT /api/intake/today
```

Updates today’s calorie and water intake.

### Intake History

```http
GET /api/intake/history
```

Returns recent intake history for the logged-in user.

## Verification Status

The application has been tested locally with the following flow:

- Database `fitness_trac` created successfully
- Backend server started successfully
- Frontend server started successfully
- Health endpoint confirmed database connection
- User registration tested
- User login tested
- Daily calorie and water update tested
- Saved intake data loaded back from MySQL
- Intake history loaded from MySQL
- React production build completed successfully

## Current Status

PulseFit is a market-ready local MVP. It is suitable for portfolio, academic, and early product demonstration use.

For production deployment, recommended next steps include:

- Deploy frontend and backend to a cloud platform
- Use a hosted MySQL database
- Enable HTTPS
- Add password reset by email
- Add profile editing
- Add charts and long-term analytics
- Add admin dashboard
- Add stronger security rules and rate limiting

## Author

Created as a full-stack upgrade of a Python fitness tracker project.
