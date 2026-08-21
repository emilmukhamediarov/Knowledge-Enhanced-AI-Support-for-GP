# GP Support Backend

Backend prototype for the Bitwise GP pre-consultation support project.

The current backend uses:

- **FastAPI** for HTTP endpoints
- **PostgreSQL** for persistent storage
- **SQLAlchemy ORM** for database access
- **Alembic** for database migrations
- **Groq** for the pre-consultation chatbot
- **Pydantic** for request validation

The current persistent database flow supports users, consultations, and consultation messages.

## Current project status

Implemented:

- PostgreSQL connection through `DATABASE_URL`
- SQLAlchemy `User`, `Consultation`, and `Message` models
- One user -> many consultations relationship
- One consultation -> many messages relationship
- Timezone-aware message timestamps stored in UTC
- FastAPI request-scoped database sessions
- Consultation creation endpoint
- Message creation endpoint
- Conversation-history retrieval endpoint
- Database-backed Groq chat history
- Alembic migration setup

Not yet completed:

- Persistent consultation summaries
- Authentication integration with the real `users` table
- RAG integration
- Final frontend integration
- Production security/configuration

## Quick start

### 1. Clone the repository and enter the backend folder

```bash
git clone <repository-url>
cd team-17-project/gp-support
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows Git Bash:

```bash
source venv/Scripts/activate
```

On Windows Command Prompt:

```cmd
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Create a file called `.env` in the `gp-support` directory:

```env
DATABASE_URL=postgresql+psycopg2://USERNAME:PASSWORD@localhost:5432/DATABASE_NAME
GROQ_API_KEY=your_groq_api_key_here
```

Do **not** commit `.env` to Git.

### 5. Make sure PostgreSQL is running

Create the database named in `DATABASE_URL` if it does not already exist.

Alembic manages the application tables; teammates should not manually create `users`, `consultations`, or `messages`.

### 6. Apply database migrations

```bash
alembic upgrade head
```

This brings the local database schema up to the latest version committed to the repository.

### 7. Run the API

```bash
uvicorn main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Normal development workflow

When pulling changes from another teammate:

```bash
git pull
pip install -r requirements.txt
alembic upgrade head
```

Then start FastAPI:

```bash
uvicorn main:app --reload
```

## When changing the database schema

Do not use `drop_all()` and do not rely on `create_all()` for schema changes now that Alembic is configured.

1. Edit the SQLAlchemy models.
2. Generate a migration:

```bash
alembic revision --autogenerate -m "describe the schema change"
```

3. Inspect the generated file under `migrations/versions/`.
4. Apply it:

```bash
alembic upgrade head
```

5. Commit both the model change and migration file.

Check the currently applied migration with:

```bash
alembic current
```

View migration history with:

```bash
alembic history
```

## Environment variables

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection used by SQLAlchemy and Alembic |
| `GROQ_API_KEY` | API key used by the chatbot service |

Never hard-code secrets into Python files or commit the `.env` file.

## Useful commands

```bash
# activate virtual environment
source venv/Scripts/activate

# install dependencies
pip install -r requirements.txt

# update database schema
alembic upgrade head

# show current migration
alembic current

# run development server
uvicorn main:app --reload

# open API documentation
# http://127.0.0.1:8000/docs
```

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the current backend design and request flows.
