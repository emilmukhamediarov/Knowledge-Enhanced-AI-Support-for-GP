# GP Support

GP Support is a full-stack pre-consultation application that helps patients collect and submit health information before a GP appointment. A multilingual conversational assistant gathers the current complaint and relevant background information. When the patient submits the consultation, the backend creates a structured patient summary and a separate clinical insight grounded in a controlled medical-guideline knowledge base.

The application is decision support for clinicians. It is not a diagnostic system and does not replace professional medical judgement.

## Current Features

### Patient workflow

- Account registration with email verification
- JWT login and password reset
- Patient profile with date of birth, preferred language, ethnicity, medical history, medications and allergies
- Selection of an assigned GP
- New and related follow-up consultations
- Multilingual pre-consultation chatbot
- Text and real-time voice input
- Three-dimensional speaking avatar with text-to-speech
- Persistent consultation history
- Reset or delete an in-progress consultation
- Submit a completed consultation to the assigned doctor

Supported conversation/transcription language codes currently include:

- English (`en-US`)
- Simplified Chinese (`zh-CN`)
- Thai (`th-TH`)
- Russian (`ru-RU`)
- Spanish (`es-US`)

### Doctor workflow

- View assigned patients
- Review ready and closed consultations
- View structured patient information
- View a knowledge-base-grounded clinical insight
- Open guideline source links
- Record subjective, objective, assessment and plan notes
- Update permitted patient profile fields
- Close a reviewed consultation

### Knowledge-base and RAG workflow

- 34 local medical-guideline documents as the knowledge base corpus
- NHS- and CDC-derived source material
- BAAI `bge-small-en-v1.5` embeddings
- PostgreSQL/pgvector storage through LlamaIndex
- 512-token chunks with 50-token overlap
- Semantic retrieval with a 0.67 similarity cut-off
- Deterministic abstention when no guideline chunk qualifies
- Amazon Bedrock synthesis constrained to retrieved passages
- Returned source passages and guideline links
- Knowledge-grounded live follow-up topics during problem exploration
- Incremental indexing for newly added files

## Important Terminology

The system creates two different outputs:

1. **Patient summary** — factual JSON extracted from information the patient stated or explicitly confirmed.
2. **RAG clinical insight** — a separate doctor-facing answer generated from guideline chunks retrieved for that patient summary.


## Technology Stack

### Frontend

- React 19
- TypeScript
- Vite
- React Router
- Three.js avatar rendering
- Tailwind CSS

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- JWT authentication

### AWS and AI services

- Amazon Bedrock — chatbot, patient-summary extraction and grounded answer synthesis
- Amazon Transcribe Streaming — live voice transcription
- Amazon Polly — speech and word-level speech marks
- Amazon SES — verification and password-reset email
- Hugging Face sentence-transformer embeddings
- LlamaIndex
- PostgreSQL pgvector

## Architecture

```text
Patient React UI
       |
       | HTTPS / WebSocket
       v
FastAPI consultations router
       |
       +---------------------> PostgreSQL
       |                       users, consultations,
       |                       messages, summaries, SOAP notes
       |
       +---------------------> Amazon Bedrock
       |                       chat + structured extraction
       |
       +---------------------> knowledge_rag.py
                               |
                               +--> BGE query embedding
                               +--> pgvector retrieval
                               +--> similarity filtering
                               +--> Bedrock grounded synthesis
                               +--> source passages and links

Assigned Doctor React UI
       |
       +--> patient summary + RAG insight + guideline links
```

### Final submission flow

```text
Conversation messages
    -> chat_service.summary_aws()
    -> validated ConsultationSummary dictionary
    -> build_query_from_consultation_summary()
    -> English retrieval query
    -> ask_structured()
    -> filtered guideline chunks
    -> grounded clinical insight
    -> patient_summary + rag_response stored as JSONB
    -> consultation status becomes ready
```

## Repository Structure

```text
.
├── frontend/                         React/TypeScript frontend
│   ├── public/                       Static assets and avatar models
│   └── src/
│       ├── api/                      Authenticated API client
│       ├── components/               Shared UI, routes and avatar
│       └── pages/
│           ├── doctor/               Doctor dashboards and review
│           └── patient/              Patient profile and chat
│
├── gp-support/                       FastAPI backend
│   ├── alembic.ini
│   ├── migrations/                   Database migrations
│   ├── requirements.txt
│   ├── tests/                        RAG tests and evaluation cases
│   └── app/
│       ├── db/                       SQLAlchemy models and sessions
│       ├── dependencies/             Authentication and DB dependencies
│       ├── knowledge_base/           Medical guideline text files
│       ├── repositories/             Persistence operations
│       ├── routers/                  Auth, users, consultations and TTS
│       ├── schemas/                  Pydantic request/response models
│       └── services/
│           ├── chat_service.py       Bedrock chat and summary extraction
│           ├── knowledge_rag.py      Indexing, retrieval and synthesis
│           ├── state_service.py      Consultation phase state machine
│           ├── transcribe_service.py Amazon Transcribe integration
│           └── tts_service.py        Amazon Polly integration
│
└── README.md                         Existing project documentation
```

## Prerequisites

Install or provision:

- Python 3.11 or later
- Node.js and npm
- PostgreSQL with pgvector available
- AWS credentials with access to the services used by the application
- Amazon Bedrock model access for the configured model

The first backend startup may download the Hugging Face embedding model.

## Environment Configuration

### Backend

Create `gp-support/.env`:

```env
# PostgreSQL
DATABASE_URL=postgresql+psycopg://USERNAME:PASSWORD@HOST:5432/DATABASE

# Frontend origin used by FastAPI CORS
FRONTEND_URL=http://localhost:5173

# JWT authentication
AUTH_SECRET_KEY=replace-with-a-long-random-secret
AUTH_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS
AWS_REGION=ap-southeast-2
AWS_PROFILE=your-local-profile
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0

# Email verification and reset
SES_FROM_EMAIL=verified-sender@example.com
EMAIL_VERIFICATION_SECRET=replace-with-a-long-random-secret
EMAIL_CODE_TTL_MINUTES=10
EMAIL_CODE_RESEND_SECONDS=60
EMAIL_CODE_MAX_ATTEMPTS=5

# Amazon Transcribe language identification
TRANSCRIBE_LANGUAGE_OPTIONS=en-US,zh-CN,th-TH,ru-RU,es-US

```


### Frontend

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

Do not commit `.env` files or credentials.

## Local Development

### 1. Clone and enter the project

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Set up the backend

```bash
cd gp-support
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```powershell
.venv\Scripts\activate
```

Create `gp-support/.env` using the configuration above.

### 3. Prepare PostgreSQL

Create the database named by `DATABASE_URL`. Ensure pgvector is available to the database/user. Then apply all migrations:

```bash
alembic upgrade head
```

Do not use `Base.metadata.drop_all()` for normal schema changes.

### 4. Prepare the RAG index

To index only newly added top-level knowledge-base files:

```bash
python -m app.services.knowledge_rag --update
```

Incremental updates identify documents by filename:

- new filenames are indexed;
- already indexed filenames are skipped;
- hidden files are ignored;
- edits to an existing filename are not re-indexed;
- renamed or deleted documents are not synchronised automatically.

For edits or removals, perform a controlled full rebuild with `build_index(db)` or the configured startup rebuild path. A full rebuild clears existing RAG chunks before inserting the current corpus.

### 5. Start the backend

From `gp-support`:

```bash
uvicorn app.main:app --reload
```

Available locally:

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- OpenAPI schema: <http://localhost:8000/openapi.json>

### 6. Start the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>.

## Frontend Commands

Run from `frontend`:

```bash
npm run dev       # development server
npm run build     # TypeScript and production build
npm run lint      # ESLint
npm run preview   # preview production build
```

## Database Migrations

After changing SQLAlchemy models:

```bash
cd gp-support
alembic revision --autogenerate -m "describe the schema change"
alembic upgrade head
```

Always inspect generated migrations before applying or committing them.

Useful commands:

```bash
alembic current
alembic history
alembic downgrade -1
```


## API Overview

The full interactive contract is available through Swagger. Main endpoint groups are:

### Authentication

- `POST /auth/send-code`
- `POST /auth/verify-code`
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`

### Users

- `GET /users/me`
- `PATCH /users/me`
- `GET /users/doctors`
- `PUT /users/me/doctor`
- `GET /users/me/doctor`
- `GET /users/me/patients`
- `GET /users/patients/{patient_id}`
- `PATCH /users/patients/{patient_id}`

### Consultations

- `POST /consultations`
- `POST /consultations/{id}/chat`
- `GET /consultations/{id}/messages`
- `DELETE /consultations/{id}/messages`
- `DELETE /consultations/{id}`
- `PATCH /consultations/{id}/ready`
- `PATCH /consultations/{id}/close`
- `GET /consultations/{id}/summary`
- `GET /consultations/{id}/rag`
- `GET /consultations/{id}/status`
- `GET /consultations/doctor`
- `PATCH /consultations/{id}/related-consultation`
- SOAP note GET/PATCH endpoints for `subjective`, `objective`, `assessment` and `plan`
- WebSocket `/consultations/{id}/audio-stream`

### Speech

- `POST /tts/tts`

Protected endpoints use:

```http
Authorization: Bearer <access_token>
```

## Consultation State

Consultations move through:

```text
in-progress -> ready -> closed
```

- **in-progress:** patient can chat, reset, delete and submit.
- **ready:** submitted to the assigned doctor; patient editing is disabled.
- **closed:** doctor has completed review.

The chatbot separately moves through intake phases:

```text
explore_problem
    -> confirm_medical_history
    -> confirm_medications
    -> confirm_allergies
    -> additional_concerns
    -> complete
```

## Knowledge Base

Medical documents live in:

```text
gp-support/app/knowledge_base/
```

Each document should:

- use readable headings and plain text;
- describe one primary topic;
- preserve medically important wording and negative findings;
- end with a `SOURCE` or `SOURCES` heading;
- place authoritative HTTP(S) source URLs after that heading; and
- be clinically and jurisdictionally reviewed before indexing.


## Security and Clinical-Safety Notes

- Review AWS data residency and health-information handling requirements.
- The RAG answer is generated decision support, not a diagnosis. Doctors should verify answers.
- Guideline grounding reduces but does not eliminate model error.
- Similarity confidence is not equivalent to clinical confidence.


