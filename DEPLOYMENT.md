# FRES Deployment Checklist

## Pre-Deployment

- [ ] Get OpenRouter API key from https://openrouter.ai
- [ ] Update .env with your actual API key (not the placeholder)
- [ ] Test locally: `python server.py`
- [ ] Verify AI generation works: quiz generation should respond

## Vercel Deployment

- [ ] Push code to GitHub
- [ ] Connect repository to Vercel (https://vercel.com/new)
- [ ] Set environment variables in Vercel:
  - [ ] OPENROUTER_API_KEY (your actual key)
  - [ ] OPENROUTER_MODEL (or use default: openrouter/auto)
  - [ ] OPENROUTER_BASE_URL (or use default: https://openrouter.ai/api/v1)
- [ ] Deploy and wait for build to complete
- [ ] Initialize database:
  - [ ] Run `vercel run api/init_db.py` via Vercel CLI
  - [ ] OR access https://your-domain.vercel.app/api/init_db.py once
- [ ] Test /api/ping endpoint
- [ ] Test quiz generation
- [ ] Change default admin password (admin/admin123)

## Post-Deployment

- [ ] Test all user endpoints (login, register)
- [ ] Test admin dashboard functionality
- [ ] Verify AI generation works in production
- [ ] Update frontend URLs if needed
- [ ] Set up Vercel custom domain (optional)
- [ ] Enable Vercel deployment protection rules
- [ ] Monitor OpenRouter usage in dashboard

## Troubleshooting

### "API connection failed"
- Check OPENROUTER_API_KEY is set correctly in Vercel
- Verify API key has available quota at https://openrouter.ai

### "Database error"
- Run api/init_db.py to create tables
- Check file permissions on instance/ folder

### "Module not found"
- Verify requirements.txt has all dependencies
- Check Vercel build logs for installation errors

### "CORS errors"
- CORS is enabled for all origins in api/base.py
- Frontend should be on same domain or CORS headers will allow it
