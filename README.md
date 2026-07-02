<p align="center">
  <img src="app/static/logo.png" alt="ESSAYra logo" width="180" />
</p>

<h1 align="center">ESSAYra</h1>

<p align="center">
  AI-powered web application for checking Russian OGE essays and giving criterion-based feedback.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688" alt="FastAPI" />
  <img src="https://img.shields.io/badge/OpenAI-LLM-black" alt="OpenAI" />
  <img src="https://img.shields.io/badge/SQLite%20%2F%20PostgreSQL-Database-blue" alt="Database" />
  <img src="https://img.shields.io/badge/Jinja2-Templates-orange" alt="Jinja2" />
</p>

---

## Overview

**ESSAYra** is an educational AI product that helps students and teachers check Russian OGE essays faster.

Manual essay checking takes a lot of time, and students often cannot get instant feedback while preparing for exams. ESSAYra automates the first review layer: it analyzes the essay, estimates scores by OGE-style criteria, highlights weak points, and gives recommendations for improvement.

The project is built as a web application with authentication, task selection, timed writing mode, AI evaluation, result pages, and database persistence.

---

## Problem

Checking essays manually is slow and repetitive:

- teachers spend significant time reviewing similar mistakes;
- students need frequent practice before the exam;
- feedback is not always available immediately;
- scoring criteria are difficult for students to interpret on their own.

## Solution

ESSAYra gives students a structured AI-based review:

- checks the essay against OGE-style criteria;
- evaluates content, logic, composition, grammar, speech quality, and factual accuracy;
- explains each criterion in simple language;
- returns a total score and personalized feedback;
- stores attempts in a database for future analysis.

> ESSAYra is not an official exam grader. It is a training assistant designed to support preparation and reduce routine checking work.

---

## My Role

I developed the project as a backend-focused AI web application:

- designed the application architecture;
- implemented authentication and session handling;
- created database models for users, tasks, topics, and essay attempts;
- built the essay submission and result flow;
- implemented the AI evaluation pipeline;
- designed prompts for criterion-based essay checking;
- configured structured JSON output validation with Pydantic;
- built server-rendered pages with Jinja2 templates;
- prepared the project for local and production database usage.

---

## Tech Stack

| Area | Technologies |
| --- | --- |
| Backend | Python, FastAPI |
| Frontend | HTML, CSS, Jinja2 Templates |
| Database | SQLite for local development, PostgreSQL-ready configuration |
| ORM / Models | SQLModel, Pydantic |
| AI | OpenAI API, structured JSON output |
| Auth | Session middleware, password hashing |
| Runtime | Uvicorn |

---

## Key Features

- User registration and login
- Random OGE-style task selection
- Choice between essay topics `13.1`, `13.2`, `13.3`
- Built-in writing timer
- Essay word count calculation
- AI-based essay evaluation
- Criterion-by-criterion scoring
- Total score calculation
- Personalized feedback
- Attempt persistence in the database
- Local SQLite setup and PostgreSQL-ready deployment configuration

---

## AI Evaluation Pipeline

```text
Student essay
     │
     ▼
FastAPI form handler
     │
     ▼
Word count + task/topic context
     │
     ▼
Prompt builder
     │
     ▼
OpenAI Responses API
     │
     ▼
Structured JSON result
     │
     ▼
Pydantic validation
     │
     ▼
Database save
     │
     ▼
Result page with criteria and feedback
```

---

## Application Flow

```text
Register / Login
     │
     ▼
Get random task
     │
     ▼
Read source text and instructions
     │
     ▼
Choose essay topic
     │
     ▼
Start timer
     │
     ▼
Write essay
     │
     ▼
Submit for AI review
     │
     ▼
View score and feedback
```

---

## Project Structure

```text
ESSAYra/
├── run.py
├── requirements.txt
├── README.md
├── .env.example
└── app/
    ├── main.py                  # FastAPI routes and application flow
    ├── db.py                    # Database engine and sessions
    ├── models.py                # SQLModel database models
    ├── schemas.py               # Pydantic validation schemas
    ├── prompts.py               # AI prompt construction
    ├── seed.py                  # Initial task loading
    ├── settings.py              # Environment-based configuration
    ├── data/
    │   └── task_sets.py         # OGE-style source texts and topics
    ├── services/
    │   └── openai_service.py    # OpenAI integration
    ├── templates/
    │   ├── base.html
    │   ├── index.html
    │   ├── login.html
    │   ├── register.html
    │   └── result.html
    └── static/
        ├── logo.png
        └── styles.css
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/K1ng-Art4r/ESSAYra.git
cd ESSAYra
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

For Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Create `.env`

Create a local `.env` file from the example:

```bash
cp .env.example .env
```

Then fill in the required values:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5
APP_HOST=127.0.0.1
APP_PORT=8000
DATABASE_URL=sqlite:///./ai_oge.db
SESSION_SECRET_KEY=change_this_secret_key
```

For local development, SQLite is enough. The database file will be created automatically on startup.

### 5. Run the application

```bash
python run.py
```

Open in your browser:

```text
http://127.0.0.1:8000
```

---

## How to Use

1. Open the app in the browser.
2. Create an account or log in.
3. Read the source text and task instructions.
4. Choose one essay topic.
5. Click **НАЧАТЬ** to start the timer.
6. Write the essay in the text area.
7. Submit the essay for checking.
8. Review the final score, criteria breakdown, and AI feedback.

---

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | Yes | API key used for essay evaluation |
| `OPENAI_MODEL` | No | Model name used for evaluation. Default: `gpt-5` |
| `APP_HOST` | No | Local host. Default: `127.0.0.1` |
| `APP_PORT` | No | Local port. Default: `8000` |
| `DATABASE_URL` | No | Database connection URL. Default: `sqlite:///./ai_oge.db` |
| `SESSION_SECRET_KEY` | Recommended | Secret key for session cookies |

---

## Database

The app supports both SQLite and PostgreSQL-style URLs.

For local development:

```env
DATABASE_URL=sqlite:///./ai_oge.db
```

For PostgreSQL deployment:

```env
DATABASE_URL=postgresql://user:password@host:5432/database
```

The application normalizes PostgreSQL URLs internally for the `psycopg` driver.

---

## Screenshots

Screenshots can be added to the repository later:

```text
assets/screenshots/home.png
assets/screenshots/essay-form.png
assets/screenshots/result.png
```

Recommended screenshots for portfolio presentation:

1. Login / registration page
2. Main task page with source text
3. Essay writing form with timer
4. Result page with criteria and feedback

---

## Roadmap

- Teacher dashboard
- Attempt history page
- Student progress analytics
- Export attempts to CSV
- Admin interface for task management
- Support for multiple exam formats
- More detailed grammar and punctuation diagnostics
- Comparison between student versions before and after revision

---

## Security Notes

Do not commit the following files:

```text
.env
*.db
.venv/
__pycache__/
.DS_Store
```

The repository should contain `.env.example`, but not real API keys, database URLs, or production secrets.

---

## Project Status

MVP / portfolio version.

The project demonstrates how AI can be integrated into an educational workflow to automate repetitive assessment tasks and provide fast feedback to students.

---

## Author

Developed by **K1ng-Art4r**.
