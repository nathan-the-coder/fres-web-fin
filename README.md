# FRES Web — Filipino Reviewer & Evaluation System

AI-powered quiz generator for students, built with Flask and OpenRouter AI. Features user management, admin dashboard, student suggestions, and announcements.

## 🚀 Deploy to Render.com

This project is configured for [Render.com](https://render.com) using Gunicorn + Flask.

### One-Click Deploy

1. Fork/clone this repo
2. Create a new **Web Service** on Render
3. Connect your Git repository
4. Render will auto-detect the config from `render.yaml`

### Environment Variables

Set these in your Render service settings → Environment:

```
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_MODEL=openrouter/auto
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### Start Command

```
gunicorn -b 0.0.0.0:$PORT server:app
```

## 📁 Project Structure

```
FRES-WEB-FIN/
├── server.py                 # Flask app (entry point for Gunicorn)
├── db.py                     # SQLite init + helper functions
├── handlers/                 # Request handlers (users, admin, AI)
│   ├── users_handler.py
│   ├── admin_handler.py
│   └── ai_handler.py
├── frontend/                 # Static frontend files
│   ├── index.html
│   ├── register.html
│   ├── css/
│   ├── js/
│   │   ├── core/api.js
│   │   └── components/generator.js
│   ├── user/
│   │   └── dashboard.html   # Student portal (AI generator, suggestions)
│   └── admin/
│       └── dashboard.html    # Admin portal (users, suggestions, announcements)
├── assets/                   # Static assets (logos, images)
├── instance/                 # SQLite database (auto-created, gitignored)
│   └── fres.db
├── render.yaml               # Render.com deployment config
├── requirements.txt          # Python dependencies
└── .env                     # Local environment vars (gitignored)
```

## 🛠️ Local Development

### Prerequisites

- Python 3.10+
- [OpenRouter API key](https://openrouter.ai) (free tier: 50 requests/day)

### Setup

```bash
# Clone the repo
git clone https://github.com/nathan-the-coder/fres-web-fin.git
cd fres-web-fin

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env   # then edit .env and add your API key
```

### Environment Variables (`.env`)

```
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=openrouter/auto
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### Run Locally

```bash
python server.py
```

The database auto-initializes on startup. Visit http://127.0.0.1:5000/

### Default Admin Credentials

```
Username: admin
Password: admin123
```

> ⚠️ Change the default password immediately after first login.

## 🤖 AI Configuration

### Get a FREE OpenRouter API Key

1. Visit https://openrouter.ai
2. Sign up (free, 30 seconds)
3. Copy your API key from the dashboard
4. Add it to `.env` or Render environment variables

### Free Tier Limits

- **50 requests/day** — completely free
- **20 requests/minute** rate limit
- **No expiration** — permanent free tier
- **200,000 token** context window

Perfect for quiz generation: ~500 questions/day (10 questions per request).

### Available Free Models

Browse at: https://openrouter.ai/openrouter/free

- `openrouter/auto` — Auto-selects best available model (default)
- `qwen/qwen-2.5-72b-instruct:free` — High quality
- `nvidia/nemotron-3-super-120b-a12b:free` — NVIDIA's model

## 📡 API Endpoints

### User Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/users/login` | User login |
| POST | `/api/users/register` | User registration |

### AI Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/generate` | Generate quiz questions |
| GET | `/api/ai/logs` | Get AI generation logs |

### Suggestions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/suggestions` | Submit a suggestion (students) |
| GET | `/api/admin/suggestions` | List all suggestions (admin) |
| POST | `/api/admin/suggestions/:id/reply` | Reply to suggestion (admin) |

### Admin Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/stats` | Dashboard statistics |
| GET | `/api/admin/users` | List all users |
| PUT | `/api/admin/users/:id/status` | Activate/disable user |
| GET/POST | `/api/admin/announcements` | Manage announcements |

### Health Check
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ping` | System status check |

## 🗄️ Database

Uses SQLite (zero-config). Database file auto-creates at `instance/fres.db` on server start.

### Tables
- `users` — User accounts (username, password hash, role, status)
- `chat_logs` — AI generation history
- `suggestions` — Student feedback and suggestions
- `announcements` — Admin announcements

## 🔒 Security Notes

- Passwords hashed with SHA-256 (consider upgrading to bcrypt for production)
- Default admin credentials should be changed immediately after deployment
- API keys stored in environment variables only (never committed to Git)
- `.env` and `instance/*.db` are excluded via `.gitignore`

## 📦 Dependencies

```
flask>=3.0.0       # Web framework
openai>=2.0.0      # OpenRouter API client (OpenAI-compatible)
gunicorn            # WSGI server for Render deployment
```

## 🔄 Migration Notes

This project previously used:
- **Google Gemini** → Migrated to OpenRouter (better free tier)
- **Vercel** → Migrated to Render.com (more reliable Flask deployment)
- **`api/` serverless functions** → Unified Flask app (`server.py`)

## 📝 License

Private project — FRES System (NwSSU CCIS)

## 🆘 Support

For deployment issues:
1. Check Render deployment logs
2. Verify environment variables are set correctly
3. Ensure the database initialized (check `/api/ping` response)
4. Check OpenRouter API key is valid and has remaining quota
