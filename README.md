# Agentic Backend 🤖

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com)
[![SQLModel](https://img.shields.io/badge/SQLModel-latest-red.svg)](https://sqlmodel.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Hacktoberfest](https://img.shields.io/badge/Hacktoberfest-friendly-orange.svg)](https://hacktoberfest.com)
[![Tests](https://img.shields.io/badge/tests-11%2F11%20passing-success.svg)](test_api_comprehensive.py)
[![Status](https://img.shields.io/badge/status-fully%20working-success.svg)](APPLICATION_STATUS.md)

A modern, **fully-functional** FastAPI backend for AI chatbot agents with complete authentication system, PostgreSQL database, and JWT token management.

## ✨ Features

-   ✅ **Complete Authentication System** (WORKING!)

    -   User registration with email/password
    -   Login with JWT access & refresh tokens
    -   Token refresh with automatic revocation
    -   Logout with token blacklisting
    -   Secure password hashing (bcrypt)
    -   Token verification endpoint

-   🗄️ **Modern Database Architecture**

    -   PostgreSQL with async SQLAlchemy
    -   SQLModel for type-safe models
    -   Alembic migrations ready
    -   UUID primary keys
    -   Automatic timestamps
    -   Ready for AI chat conversations

-   � **Security Best Practices**

    -   JWT tokens with configurable expiration
    -   Refresh token rotation
    -   Password hashing with bcrypt
    -   CORS configuration
    -   SQL injection protection
    -   Environment-based secrets

-   🚀 **Developer Experience**
    -   UV package manager (fast!)
    -   Automatic API documentation (Swagger/ReDoc)
    -   Type hints everywhere
    -   Async/await throughout
    -   Clean architecture
    -   Comprehensive documentation

## 🚀 Quick Start

### Prerequisites

-   Python 3.13+
-   PostgreSQL database (or use [Neon](https://neon.tech) / [Supabase](https://supabase.com))
-   UV package manager: `pip install uv`

### 1. Clone and setup

```powershell
git clone https://github.com/heyibad/agentic-backend.git
cd agentic-backend
```

### 2. Install dependencies

```powershell
uv sync
```

### 3. Configure environment

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your database URL and generate a secure JWT secret:

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
JWT_SECRET=your-super-secret-key-at-least-32-chars
```

**Generate JWT secret (PowerShell):**

```powershell
[System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
```

### 4. Run database migrations

```powershell
uv run alembic upgrade head
```

### 5. Start the server

```powershell
uv run uvicorn app.main:app --reload --port 8080
```

Visit http://localhost:8080/docs for interactive API documentation! 🎉

### 6. Test Authentication

```powershell
# Register a user
curl -X POST http://localhost:8080/api/v1/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"user@example.com\", \"password\": \"SecurePass123\", \"name\": \"John Doe\"}"

# Login and get tokens
curl -X POST http://localhost:8080/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"user@example.com\", \"password\": \"SecurePass123\"}"
```

📖 **Full guide:** [docs/quickstart.md](docs/quickstart.md)

## 🛣️ API Endpoints

### Authentication (✅ WORKING)

| Method | Endpoint                    | Description             | Auth Required |
| ------ | --------------------------- | ----------------------- | ------------- |
| POST   | `/api/v1/auth/register`     | Register new user       | ❌            |
| POST   | `/api/v1/auth/login`        | Login and get tokens    | ❌            |
| POST   | `/api/v1/auth/refresh`      | Refresh access token    | ❌            |
| POST   | `/api/v1/auth/logout`       | Logout and revoke token | ✅            |
| GET    | `/api/v1/auth/me`           | Get current user info   | ✅            |
| GET    | `/api/v1/auth/verify-token` | Verify token validity   | ✅            |

### Coming Soon

-   💬 Chat endpoints for conversations
-   📧 Email verification flow
-   🔑 Password reset flow
-   🔐 Google OAuth2 integration

## 🗄️ Database Schema

| Table            | Description                                            |
| ---------------- | ------------------------------------------------------ |
| `users`          | User accounts with email, password hash, OAuth support |
| `refresh_tokens` | JWT refresh tokens with revocation capability          |
| `conversations`  | AI chat sessions with model and system prompt config   |
| `messages`       | Chat messages with role, content, tokens, and metadata |

**Alembic migration:** `alembic/versions/001_initial_schema.py`

## 📚 Documentation

-   **[Quick Start Guide](docs/quickstart.md)** - Complete setup instructions
-   **[Authentication API](docs/authentication-api.md)** - All auth endpoints with examples
-   **[Database Setup](docs/database.md)** - PostgreSQL configuration
-   **[Architecture Guide](docs/modern-architecture.md)** - SQLModel patterns

## 🏗️ Project Structure

```
agentic-backend/
├── app/
│   ├── api/v1/          # API endpoints
│   │   ├── auth.py      # Authentication routes ✅
│   │   └── chat.py      # Chat routes (TODO)
│   ├── core/            # Core configuration
│   │   ├── config.py    # Settings
│   │   └── security.py  # Auth dependencies
│   ├── models/          # SQLModel database models
│   │   ├── user.py
│   │   ├── refresh_token.py
│   │   ├── conversation.py
│   │   └── message.py
│   ├── schema/          # Pydantic schemas
│   │   ├── auth.py
│   │   └── user.py
│   ├── services/        # Business logic
│   │   └── auth_service.py
│   ├── utils/           # Utilities
│   │   ├── db.py        # Database session
│   │   └── jwt.py       # JWT utilities
│   └── main.py          # FastAPI app
├── alembic/             # Database migrations
├── docs/                # Documentation
└── tests/               # Tests (TODO)
```

## 🔐 Security Features

-   ✅ Bcrypt password hashing (industry standard)
-   ✅ JWT tokens with configurable expiration
-   ✅ Refresh token rotation on use
-   ✅ Token revocation on logout
-   ✅ SQL injection protection (parameterized queries)
-   ✅ CORS configured for allowed origins
-   ✅ No sensitive data in JWT payload
-   ✅ Environment-based secrets (never committed)

## 🧪 Testing (Coming Soon)

```powershell
# Run tests
uv run pytest

# With coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_auth.py
```

## 🛠️ Development

### Database Migrations

```powershell
# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback
uv run alembic downgrade -1
```

### Code Quality

```powershell
# Format
uv run black app/

# Lint
uv run ruff check app/

# Type check
uv run mypy app/
```

## 🤝 Contributing

This is a **Hacktoberfest-friendly** project! We welcome contributions of all kinds.

-   📋 [Contributing Guide](CONTRIBUTING.md)
-   🐛 [Good First Issues](GOOD_FIRST_ISSUES.md)
-   📜 [Code of Conduct](CODE_OF_CONDUCT.md)
-   🏷️ Issues labeled: `good first issue`, `hacktoberfest`, `help wanted`

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with:

-   [FastAPI](https://fastapi.tiangolo.com) - Modern web framework
-   [SQLModel](https://sqlmodel.tiangolo.com) - SQL databases in Python
-   [UV](https://github.com/astral-sh/uv) - Fast Python package manager
-   [Alembic](https://alembic.sqlalchemy.org) - Database migrations

## 📞 Support

-   📖 Documentation: Check `docs/` folder
-   🐛 Bug reports: Create an issue
-   💡 Feature requests: Create an issue with `enhancement` label
-   💬 Questions: GitHub Discussions (if enabled)

---

**Made with ❤️ for Hacktoberfest 2024** 🎃

-   `POST /predict` - Simple prediction endpoint (placeholder)
-   `POST /chat` - AI chat endpoint (coming soon)
-   `POST /auth/register` - Register new user (coming soon)
-   `POST /auth/login` - Login and get tokens (coming soon)
-   `POST /auth/refresh` - Refresh access token (coming soon)

## Contributing

We welcome contributions! This repo is Hacktoberfest-friendly.

See `CONTRIBUTING.md` for ways to get started. If you're participating in Hacktoberfest, check the `good first issue` label and the issue templates when opening an issue.

See [GOOD_FIRST_ISSUES.md](GOOD_FIRST_ISSUES.md) for some small starter tasks you can pick up.

## License

MIT License - see LICENSE file for details.
