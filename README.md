# JobViewWebsite (Django + AI Interview Platform)

A full-stack Django project for job discovery, user dashboard analytics, and AI-powered interview practice.

This repository combines:
- Job browsing and applications
- User authentication and dashboard
- General AI interview mode (chat-style)
- Single-topic interview mode (SQL/Python with question-bank RAG)
- CV-based interview mode (resume upload + RAG + evaluation)

## Key Features

### 1. Authentication and User Dashboard
- Combined sign-in/sign-up flow
- Session-based authentication using Django auth
- Protected dashboard pages
- Interview analytics and graph visualizations

### 2. Job and Application Module
- Browse jobs
- Apply to jobs
- Track applied companies

### 3. AI Interview (General)
- Chat interview flow using Groq LLM
- Multi-stage interview state management
- Per-question scoring and feedback
- Interview history and detail pages

### 4. Single Topic Interview (SQL/Python)
- Two modes: Random Topics and Single Topic
- RAG-backed question retrieval from PDF question banks
- FAISS vector stores for fast retrieval
- Difficulty progression across interview questions

### 5. CV Interview (RAG)
- Resume upload and parsing
- Text chunking + embeddings + FAISS indexing
- Resume-aware question generation
- Context-aware answer evaluation
- Session history and final scoring

## Tech Stack

- Backend: Django 6.0.2
- Database: SQLite (development)
- AI/LLM: Groq API (LLaMA models)
- RAG: LangChain + FAISS + sentence-transformers
- PDF Processing: pypdf / pypdfium2
- Frontend: Django templates + JS + CSS + Chart.js

## Project Structure (Main)

```text
viewjobs/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── README.md
├── core/
├── users/
├── application/
├── interviews/
│   ├── api/
│   ├── services/
│   ├── management/commands/
│   ├── templates/
│   ├── static/
│   └── migrations/
├── media/
│   ├── resumes/
│   ├── question_banks/
│   └── vector_stores/
└── viewjobs/
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

## Important Routes

- Home: `/`
- Jobs: `/jobs/`
- Auth: `/users/auth/`
- Dashboard: `/users/dashboard/`
- Applied Companies: `/application/applied/`
- Interview Page: `/interviews/interview/`
- Interview History: `/interviews/history/`
- Chat Interview API: `/interview-api/chat/`

CV Interview routes:
- CV Interview Home: `/interviews/cv-interview/`
- Upload Resume: `/interviews/cv-interview/upload-resume/`
- Start CV Interview: `/interviews/cv-interview/start-interview/`
- CV Interview History: `/interviews/cv-interview/history/`

## Local Setup

### 1. Clone and enter project

```bash
git clone <your-repo-url>
cd JobViewWebsite/viewjobs
```

### 2. Create and activate virtual environment

Windows PowerShell:

```powershell
python -m venv jobenv
.\jobenv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv jobenv
source jobenv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the `viewjobs` folder:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. (Optional) Create superuser

```bash
python manage.py createsuperuser
```

### 7. Build question bank vector stores (for Single Topic RAG)

Place PDFs first:
- `media/question_banks/sql/sql_questions.pdf`
- `media/question_banks/python/python_questions.pdf`

Then run:

```bash
python manage.py build_question_banks
```

### 8. Run development server

```bash
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

## Data and Persistence

The app stores:
- Users and authentication data (Django auth tables)
- Job application records
- Interview sessions, questions, answers, scores, and feedback
- Resume metadata and extracted text for CV interviews
- FAISS vector stores under media folder for RAG retrieval

## Security Notes (Before GitHub Push)

1. Never commit secrets.
- Keep API keys in `.env`

2. Ensure these are ignored by Git:
- virtual environment folder (`jobenv/`)
- `.env`
- local database (`db.sqlite3`) if you do not want to version it
- generated media/vector stores if they are large

Example `.gitignore` essentials:

```gitignore
jobenv/
.env
__pycache__/
*.pyc
media/vector_stores/
```

## Core Management Commands

```bash
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py build_question_banks
python manage.py build_question_banks --verify
python manage.py verify_questions --limit 5
```

## Current Development Notes

- Interview architecture supports modular services and API views
- URL naming conflicts for CV interview were resolved with unique route names
- Single-topic mode supports path/mode tracking and history filtering
- Dashboard graphs can display CV interview and topic proficiency trends

## Author

Pranav Kakade

## License

Choose and add a license (MIT/Apache-2.0/etc.) before making repository public.
