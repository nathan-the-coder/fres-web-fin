# FRES Backend - Quick Start Guide

## 🚀 Deploy to Vercel in 5 Minutes

### 1️⃣ Get Your FREE API Key
Visit: https://openrouter.ai
- Sign up (30 seconds, free)
- Copy your API key

### 2️⃣ Deploy to Vercel
```bash
# Install Vercel CLI (one time)
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel
```

### 3️⃣ Set Environment Variables
```bash
vercel env add OPENROUTER_API_KEY
# Paste your API key when prompted

vercel env add OPENROUTER_MODEL
# Type: openrouter/auto (or press enter for default)

vercel env add OPENROUTER_BASE_URL  
# Type: https://openrouter.ai/api/v1 (or press enter for default)
```

### 4️⃣ Initialize Database
```bash
vercel run api/init_db.py
```

### 5️⃣ Done! 🎉
Your app is now live and ready to use!

---

## 🧪 Test Locally (Optional)

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
OPENROUTER_API_KEY=your-key-here
OPENROUTER_MODEL=openrouter/auto
PORT=5000
EOF

# Run
python server.py
```

---

## 📡 API Endpoints

- `GET  /api/ping` - Health check
- `POST /api/users/register` - Register user
- `POST /api/users/login` - Login user
- `POST /api/ai/generate` - Generate quiz
- `GET  /api/ai/logs` - Get AI logs
- `GET  /api/admin/stats` - Admin stats
- `GET  /api/admin/users` - List users
- `PUT  /api/admin/users/:id/status` - Update user
- `GET  /api/admin/suggestions` - Get suggestions
- `POST /api/admin/suggestions/:id/reply` - Reply
- `GET  /api/admin/announcements` - Get announcements
- `POST /api/admin/announcements` - Create announcement

---

## 🔧 Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`
- ⚠️ Change this immediately after first login!

---

## 🆓 Free Tier Limits

- **50 requests/day** - completely free
- **20 requests/minute** rate limit
- **No expiration** - permanent free tier
- **~500 questions/day** (10 questions per request)

---

## 📚 Need Help?

- Full docs: README.md
- Deployment guide: DEPLOYMENT.md
- Get API key: https://openrouter.ai
