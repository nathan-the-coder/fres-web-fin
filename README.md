# FRES Backend - Filipino Reviewer & Evaluation System

A backend system for quiz generation using AI (OpenRouter API) with user management, admin dashboard, and SQLite database.

## 🚀 Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=YOUR_REPO_URL)

### Deployment Steps

1. **Push to Git**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Connect to Vercel**
   - Go to https://vercel.com/new
   - Import your Git repository
   - Vercel will auto-detect the Python project

3. **Set Environment Variables in Vercel**
   In your Vercel project settings → Environment Variables, add:
   ```
   OPENROUTER_API_KEY=your-api-key-here
   OPENROUTER_MODEL=openrouter/auto
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   ```

4. **Initialize Database**
   After deployment, run the database initialization:
   ```bash
   # Via Vercel CLI
   vercel run api/init_db.py
   ```
   Or access it once via browser: `https://your-domain.vercel.app/api/init_db.py`

5. **Deploy!**
   Vercel will automatically deploy on every push to main branch.

## 📁 Project Structure

```
FRES-WEB-FIN/
├── api/                      # Vercel serverless functions (PRODUCTION)
│   ├── base.py              # Shared utilities
│   ├── ai.py                # AI quiz generation endpoint
│   ├── users.py             # User authentication endpoints
│   ├── admin.py             # Admin management endpoints
│   ├── ping.py              # Health check endpoint
│   └── init_db.py           # Database initialization script
├── frontend/                 # Static frontend files
│   ├── index.html
│   ├── register.html
│   ├── css/
│   ├── js/
│   ├── user/
│   └── admin/
├── handlers/                 # Legacy handlers (local dev only)
├── server.py                 # Local development server
├── db.py                     # Database utilities
├── instance/                 # SQLite database (auto-created)
│   └── fres.db
├── assets/                   # Static assets (logos, images)
├── vercel.json               # Vercel configuration
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
└── .vercelignore            # Vercel deploy ignore rules
```

## 🛠️ Local Development

### Setup

1. **Install dependencies**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**
   Create `.env` file:
   ```env
   OPENROUTER_API_KEY=your-api-key-here
   OPENROUTER_MODEL=openrouter/auto
   PORT=5000
   ```

3. **Initialize database**
   ```bash
   python db.py
   ```

4. **Run local server**
   ```bash
   python server.py
   ```

5. **Access the app**
   Open http://127.0.0.1:5000/

## 🤖 AI Configuration

### Get FREE OpenRouter API Key

1. Visit https://openrouter.ai
2. Sign up (free, 30 seconds)
3. Copy your API key from dashboard
4. Add to `.env` or Vercel environment variables

### Free Tier Limits

- **50 requests/day** - completely free
- **20 requests/minute** rate limit
- **No expiration** - permanent free tier
- **200,000 token context window**

Perfect for quiz generation: ~500 questions/day (10 questions per request)

### Available Free Models

Browse at: https://openrouter.ai/openrouter/free

- `openrouter/auto` - Auto-selects best available model (default)
- `qwen/qwen-2.5-72b-instruct:free` - High quality
- `nvidia/nemotron-3-super-120b-a12b:free` - NVIDIA's model

## 📡 API Endpoints

### User Endpoints
- `POST /api/users/login` - User login
- `POST /api/users/register` - User registration

### AI Endpoints
- `POST /api/ai/generate` - Generate quiz questions
- `GET /api/ai/logs` - Get AI generation logs

### Admin Endpoints
- `GET /api/admin/stats` - Dashboard statistics
- `GET /api/admin/users` - List all users
- `PUT /api/admin/users/:id/status` - Update user status
- `GET /api/admin/suggestions` - Get suggestions
- `POST /api/admin/suggestions/:id/reply` - Reply to suggestion
- `GET /api/admin/announcements` - Get announcements
- `POST /api/admin/announcements` - Create announcement

### Health Check
- `GET /api/ping` - System status check

## 🗄️ Database

Uses SQLite (zero-config, serverless). Database file auto-creates in `instance/fres.db`.

### Tables
- `users` - User accounts
- `chat_logs` - AI generation history
- `suggestions` - User feedback
- `announcements` - Admin announcements

## 🔒 Security Notes

- Passwords hashed with SHA-256 (consider upgrading to bcrypt for production)
- Default admin: `admin` / `admin123` (change immediately!)
- CORS enabled for all origins (restrict in production if needed)
- API keys stored in environment variables (never commit to Git)

## 📦 Dependencies

- `openai>=2.0.0` - OpenRouter API client (OpenAI-compatible)

## 🔄 Migration from Google Gemini

This project migrated from Google Gemini (quota issues) to OpenRouter (generous free tier).

**Changes:**
- Removed `google-cloud-aiplatform` dependency
- Added `openai` package
- Updated API handlers to use OpenRouter
- Better error messages for rate limits

## 📝 License

Private project - FRES System

## 👥 Support

For issues or questions about deployment:
1. Check Vercel deployment logs
2. Verify environment variables are set
3. Ensure database is initialized
4. Check OpenRouter API key is valid and has quota
