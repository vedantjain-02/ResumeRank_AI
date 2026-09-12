# ResumeRank AI

AI-powered Resume Screening and Candidate Ranking System built with **FastAPI, PostgreSQL, pgvector, sentence-transformers, Grok Cloud API, and Next.js**.

ResumeRank AI helps HR recruiters create a Job Description, screen candidates from a PostgreSQL database, and generate an explainable ranked list of the best matching candidates.

---

## Features

### AI-Powered Resume Extraction

- Upload PDF or DOCX resumes.
- Extract resume text using PyMuPDF and python-docx.
- Parse structured candidate information using the Grok Cloud API.
- Rule-based fallback extraction when the Grok API is unavailable.
- Store structured candidate information in PostgreSQL.
- Generate resume embeddings for semantic search.

### Hybrid Candidate Ranking

The ranking pipeline combines:

- Hard filtering
- Mandatory skill matching
- BM25 keyword search
- pgvector semantic similarity
- Structured skill matching
- Experience matching
- Seniority alignment
- Education matching
- Final explainable scoring

### Mandatory Skill Handling

- Detect mandatory and preferred skills from a Job Description.
- Apply strict hard filtering first.
- Automatically relax filters if the strict candidate pool is empty.
- Apply penalties to candidates missing mandatory skills.
- Prioritize candidates satisfying all mandatory skills.

### Explainable Results

Each ranked candidate includes:

- Match score
- Matched skills
- Missing skills
- Experience match
- Seniority alignment
- BM25 score
- Vector similarity score
- Hybrid score
- Final score breakdown
- Human-readable explanation

### Recruiter Dashboard

The project includes:

- Modern Next.js frontend named **ResumeRank AI**
- Job Description creation
- Candidate ranking
- Ranking results
- Candidate database
- Candidate search and details
- Legacy FastAPI dashboard for testing

### Database

- PostgreSQL
- pgvector extension
- SQLAlchemy 2.0
- Alembic migrations
- JSONB structured fields
- GIN indexes
- 100+ seeded candidates in the current development database

---

## Technology Stack

### Backend

- Python 3.10+
- FastAPI
- Uvicorn
- SQLAlchemy 2.0
- PostgreSQL
- pgvector
- Alembic
- Pydantic Settings
- PyMuPDF
- python-docx
- sentence-transformers
- BM25
- Grok Cloud API
- Pytest

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- ESLint
- Modern dashboard components

---

## Project Structure

```text
resume_project/
│
├── .venv/
│
├── backend/
│   ├── main.py
│   │
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   │
│   │   ├── models/
│   │   │   ├── candidate.py
│   │   │   ├── job.py
│   │   │   └── ranking.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── candidate.py
│   │   │   ├── job.py
│   │   │   └── ranking.py
│   │   │
│   │   ├── routes/
│   │   │   ├── candidates.py
│   │   │   ├── jobs.py
│   │   │   └── ranking.py
│   │   │
│   │   ├── services/
│   │   │   ├── resume_parser.py
│   │   │   ├── candidate_extractor.py
│   │   │   ├── jd_parser.py
│   │   │   ├── embedding_service.py
│   │   │   └── ranking_service.py
│   │   │
│   │   ├── utils/
│   │   └── seed_data.py
│   │
│   ├── migrations/
│   │   ├── env.py
│   │   └── versions/
│   │       ├── 0001_create_initial_tables.py
│   │       ├── 0002_restructure_candidate_schema.py
│   │       ├── 0003_add_indexes.py
│   │       ├── 0004_add_ranking_fields.py
│   │       └── 0005_add_final_scoring_columns.py
│   │
│   ├── tests/
│   ├── scripts/
│   ├── uploads/
│   ├── .env
│   ├── .env.example
│   ├── alembic.ini
│   └── requirements.txt
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── package.json
│   └── next.config.mjs
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## Candidate Database Schema

The `candidates` table contains the following main columns:

| Column | Data Type | Description |
|---|---|---|
| `id` | Integer | Primary key |
| `name` | String | Candidate full name |
| `phone_number` | String | Candidate contact number |
| `career_summary` | Text | Professional summary |
| `total_experience_years` | Float | Total professional experience |
| `seniority_level` | String | Junior, Mid-Level, Senior, Lead, or Manager |
| `job_title` | String | Current or relevant job title |
| `functional_expertise` | JSONB | Domain expertise and functional areas |
| `leadership` | JSONB | Leadership experience and responsibilities |
| `education` | JSONB | Degree, field, institution, and graduation year |
| `capability_tags` | JSONB | Skills, tools, frameworks, and technologies |

### Supplementary Columns

| Column | Description |
|---|---|
| `resume_embedding` | 384-dimensional vector |
| `resume_text` | Extracted resume text |
| `resume_file_path` | Stored resume file path |
| `is_seed` | Indicates seeded candidate |
| `created_at` | Candidate creation timestamp |

---

## Ranking Pipeline

```text
Job Description
      |
      v
JD Parsing
      |
      v
Mandatory and Preferred Skill Detection
      |
      v
Hard Filtering
      |
      v
BM25 Keyword Search
      |
      v
pgvector Semantic Search
      |
      v
Hybrid Candidate Fusion
      |
      v
Detailed Scoring
      |
      v
Mandatory Skill Priority
      |
      v
Final Top-N Candidates
```

### Example Pipeline

```text
101 candidates
      ↓
Hard filter
      ↓
BM25 + vector search
      ↓
Hybrid ranking
      ↓
Detailed scoring
      ↓
Top 5 or Top 6 candidates
```

The exact number of candidates at each stage depends on the Job Description and configured limits.

---

## Scoring Algorithm

Each candidate receives scores across multiple dimensions.

### Skills and Capability Matching

The system compares Job Description skills against:

- `capability_tags`
- `functional_expertise`
- Job title
- Resume text

Mandatory skills receive higher priority than preferred skills.

### Experience Matching

The system considers:

- Minimum required experience
- Maximum required experience, when available
- Candidate's total experience
- Seniority level
- Role seniority alignment

### Semantic Similarity

Resume and Job Description embeddings are generated using:

```text
all-MiniLM-L6-v2
```

The embeddings are stored and searched using PostgreSQL with pgvector.

### BM25 Keyword Matching

BM25 identifies candidates whose resume content contains relevant keywords and phrases from the Job Description.

### Education Matching

The system compares candidate education with the educational requirements of the Job Description.

### Final Ranking

The final score combines:

- Detailed structured score
- BM25 score
- Vector similarity score
- Hybrid score
- Mandatory skill status
- Experience alignment
- Education alignment

Candidates who satisfy all mandatory skills are prioritized over candidates with higher semantic similarity but missing mandatory requirements.

---

## Fairness

The ranking system does not use the following information for candidate scoring:

- Name
- Gender
- Phone number
- Personal contact information
- Other unrelated personal attributes

The ranking is based on job-relevant information such as skills, experience, education, seniority, and resume content.

---

## Prerequisites

Install the following before running the project:

- Python 3.10 or newer
- PostgreSQL 13 or newer
- pgvector PostgreSQL extension
- Node.js and npm
- Optional Grok Cloud API key

The current development environment uses:

- Windows
- Python 3.13
- PostgreSQL 18
- Native PostgreSQL installation
- pgvector
- Next.js frontend

Docker is not required for the current setup.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/resume-rank-ai.git
cd resume_project
```

### 2. Create the Python Virtual Environment

Run this command from the project root:

```bash
python -m venv .venv
```

#### Windows

```powershell
.venv\Scripts\Activate.ps1
```

#### macOS/Linux

```bash
source .venv/bin/activate
```

### 3. Install Backend Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

---

## PostgreSQL Setup

### 1. Create the Database

```sql
CREATE DATABASE resume_screening;
```

### 2. Enable pgvector

Connect to the `resume_screening` database and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Configure Environment Variables

Create the environment file:

#### Windows

```powershell
Copy-Item .env.example .env
```

#### macOS/Linux

```bash
cp .env.example .env
```

Update `backend/.env`:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/resume_screening

GROK_API_KEY=your_grok_api_key
GROK_MODEL=grok-4.6

EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

DEFAULT_RANKING_LIMIT=5
```

Never commit `.env` or API keys to GitHub.

---

## Run Database Migrations

Run this command from the `backend` directory:

```bash
alembic upgrade head
```

This applies all database migrations, including:

- Initial database tables
- Candidate JSONB fields
- Database indexes
- Ranking fields
- Final scoring columns

---

## Start the Backend

Run the backend from the `backend` directory:

```powershell
uvicorn main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

### API Documentation

```text
http://127.0.0.1:8000/docs
```

### Legacy Dashboard

```text
http://127.0.0.1:8000/static/index.html
```

### Health Check

```text
http://127.0.0.1:8000/api/health
```

---

## Start the Frontend

Open a second terminal:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start the Next.js development server:

```powershell
npm run dev
```

The frontend will be available at:

```text
http://localhost:3000
```

If port 3000 is already occupied:

```powershell
npm run dev -- -p 3001
```

Then open:

```text
http://localhost:3001
```

---

## Frontend Environment Configuration

Create `frontend/.env.local` if required:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

The frontend uses this variable to communicate with the FastAPI backend.

---

## API Endpoints

### Candidate APIs

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/candidates/upload` | Upload and process a resume |
| `GET` | `/api/candidates` | List and search candidates |
| `GET` | `/api/candidates/{id}` | Get candidate details |

### Job APIs

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/jobs` | Create a Job Description |
| `GET` | `/api/jobs` | List all jobs |
| `GET` | `/api/jobs/{id}` | Get job details |

### Ranking APIs

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/jobs/{job_id}/rank` | Rank candidates for a job |
| `GET` | `/api/jobs/{job_id}/results` | Get stored ranking results |

### Utility APIs

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Backend health check |
| `GET` | `/api/weights` | View current scoring weights |

---

## Example Ranking Request

```bash
curl -X POST http://127.0.0.1:8000/api/jobs/1/rank \
  -H "Content-Type: application/json" \
  -d "{\"top_n\": 5}"
```

---

## Example Ranking Response

```json
{
  "job_id": 1,
  "job_title": "Python Backend Developer",
  "total_candidates_evaluated": 100,
  "top_candidates": [
    {
      "rank": 1,
      "candidate_id": 20,
      "candidate_name": "Candidate Name",
      "match_score": 91.3,
      "matched_skills": [
        "Python",
        "FastAPI",
        "PostgreSQL",
        "Docker",
        "AWS"
      ],
      "missing_skills": [],
      "experience_match": "Strong",
      "explanation": "Strong match for the Python Backend Developer role because the candidate has relevant backend experience, matching technical skills, and suitable professional experience."
    }
  ]
}
```

---

## Running Tests

Run tests from the `backend` directory:

```bash
pytest tests/ -v
```

Or:

```bash
python -m pytest -q
```

The test suite covers:

- Resume text extraction
- PDF and DOCX processing
- Candidate extraction
- Job Description parsing
- Mandatory and preferred skill detection
- Seniority matching
- Experience matching
- BM25 ranking
- Vector ranking
- Hybrid ranking
- Final score calculation
- Fallback ranking
- API behavior
- Configuration and scoring weights

---

## Seed Candidates

The current development database contains more than 100 candidates.

Seed candidates are useful for:

- Testing ranking behavior
- Testing different Job Descriptions
- Validating mandatory skill filtering
- Testing the recruiter dashboard
- Demonstrating candidate ranking

Seed utilities are available inside:

```text
backend/scripts/
```

---

## Troubleshooting

### Port 8000 Already in Use

```powershell
netstat -ano | findstr :8000
```

Stop the process using its PID:

```powershell
taskkill /PID YOUR_PID /F
```

### Port 3000 Already in Use

```powershell
netstat -ano | findstr :3000
```

Or use another port:

```powershell
npm run dev -- -p 3001
```

### pgvector Extension Error

If PostgreSQL reports:

```text
could not open extension control file "vector"
```

Install pgvector for your PostgreSQL version and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Grok API Error

- Check that `GROK_API_KEY` is valid.
- Confirm the model name in `.env`.
- Restart the backend after changing `.env`.
- Check the backend terminal for the exact API error.

The system includes rule-based fallback extraction when the Grok API is unavailable.

### Sentence-Transformer Model Download

The first embedding operation may download:

```text
all-MiniLM-L6-v2
```

The first run may take longer than subsequent runs.

### Empty Ranking Results

Check that:

- Candidates exist in the database.
- Candidate embeddings have been generated.
- The Job Description contains meaningful skills.
- The database connection is correct.
- The backend is running.
- Database migrations have been applied.

The ranking pipeline includes filter relaxation when the strict candidate pool is empty.

---

## Configuration

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL database connection string |
| `GROK_API_KEY` | Grok Cloud API key |
| `GROK_MODEL` | Grok model used for extraction and JD parsing |
| `EMBEDDING_MODEL_NAME` | Sentence-transformer model |
| `DEFAULT_RANKING_LIMIT` | Default number of ranked candidates |
| `SCORING_WEIGHTS_SKILLS` | Skills scoring weight |
| `SCORING_WEIGHTS_EXPERIENCE` | Experience scoring weight |
| `SCORING_WEIGHTS_SEMANTIC` | Semantic similarity weight |
| `SCORING_WEIGHTS_EDUCATION` | Education scoring weight |
| `MANDATORY_SKILL_PENALTY` | Penalty for missing mandatory skills |
| `FINAL_SCORE_HYBRID_WEIGHT` | Hybrid score contribution |
| `FINAL_SCORE_DETAILED_WEIGHT` | Detailed score contribution |
| `FINAL_SCORE_ENABLE_MANDATORY_PRIORITY` | Enables mandatory skill priority |

---

## Security Notes

- Never commit `.env` files.
- Never expose the Grok API key in frontend code.
- Keep API keys in backend environment variables.
- Uploaded resumes may contain personal information.
- Do not expose uploaded resume files publicly.
- Add authentication and authorization before production deployment.
- Use HTTPS before production deployment.
- Restrict database access to trusted services.

---

## Current Status

ResumeRank AI currently supports:

- PDF and DOCX resume upload
- Grok-powered structured extraction
- Rule-based fallback extraction
- PostgreSQL candidate storage
- pgvector embeddings
- BM25 keyword ranking
- Hybrid candidate ranking
- Mandatory skill filtering
- Automatic filter relaxation
- Explainable ranking results
- FastAPI backend
- Next.js recruiter dashboard
- 100+ seeded candidates
- Automated backend tests

---

## Future Improvements

- Recruiter authentication
- Role-based access control
- Resume duplicate detection
- Bulk resume upload
- Advanced analytics dashboard
- Candidate comparison view
- Export ranking results to CSV or Excel
- Email notifications
- Audit logs
- Background task processing
- Production deployment
- Model evaluation and ranking quality metrics

---

## License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for details.

---

## Author

**Vedant Jain**

Python Backend Developer | FastAPI | AI Enthusiast

- GitHub: https://github.com/vedantjain-02
- Portfolio: https://vedant-portfolio-1802.lovable.app/