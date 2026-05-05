# FRES Web - Updates & Changes Documentation

## Latest Updates (May 2026)

### 1. AI Answer Format Fix
**File:** `handlers/ai_handler.py`

**Problem:** 
- AI was generating letter answers (A, B, C, D) even for Identification questions
- Answer key format was inconsistent across question types

**Solution:**
- Updated AI prompt to include type-specific format instructions
- Added post-processing function `_fix_identification_answers()` that maps letter answers to actual keywords
- Different answer formats per question type:
  - **Multiple Choice:** A, B, C, or D
  - **True/False:** True or False
  - **Identification:** keywords/phrases (e.g., "mitochondria", "ATP")

**Code Changes:**
```python
# Added type-specific prompt instructions
if mode == "multipleChoice":
    answer_examples = "A\nB\nC\nD"
elif mode == "trueFalse":
    answer_examples = "True\nFalse\nTrue"
else:  # identification
    answer_examples = "photosynthesis\nmitochondria\ncell wall"

# Added post-processing for identification
def _fix_identification_answers(questions: str, answers: str) -> str:
    # Maps letter answers to actual keyword answers
    ...
```

---

### 2. Social Media Preview (Open Graph & Twitter Cards)
**Files:** `index.html`, `user/dashboard.html`, `frontend/user/dashboard.html`

**Added Meta Tags:**
```html
<!-- Open Graph / Facebook -->
<meta property="og:type" content="website">
<meta property="og:url" content="https://fres-web-fin.onrender.com/">
<meta property="og:title" content="FRES Web Portal — NwSSU CCIS">
<meta property="og:description" content="...">
<meta property="og:image" content="https://fres-web-fin.onrender.com/og-image.png">

<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:url" content="https://fres-web-fin.onrender.com/">
<meta name="twitter:title" content="...">
<meta name="twitter:description" content="...">
<meta name="twitter:image" content="https://fres-web-fin.onrender.com/og-image.png">
```

**Result:** Links shared on Facebook, Twitter, LinkedIn now show preview images and descriptions.

---

### 3. Deployment Migration (Vercel → Render.com)
**Files:** Multiple

**Changes:**
- Updated all URLs from `fres-web.vercel.app` to `fres-web-fin.onrender.com`
- Removed Vercel-related files: `pyproject.toml`, Vercel log export
- Updated `AGENTS.md` to reflect Render.com deployment instructions
- Updated `README.md` with migration notes

---

### 4. Bug Fixes & Refactoring
**Files:** `handlers/ai_handler.py`

**Fixed Issues:**
- Syntax errors with em dashes (—) in prompts
- Unclosed triple-quoted strings
- Missing variable initialization (`example_section`)
- Fixed indentation errors

**Refactored:**
- Simplified multi-line strings using parentheses
- Added proper error handling for all code paths

---

## Previous Updates

### January 2026 - System Migration
- Migrated from Google Gemini to OpenRouter AI (better free tier)
- Migrated from Vercel to Render.com (more reliable for Flask)
- Consolidated from separate API handlers to unified Flask app (`server.py`)

---

## File Structure Overview

```
FRES-WEB-FIN/
├── server.py              # Flask entry point
├── handlers/
│   ├── ai_handler.py      # AI quiz generation (UPDATED)
│   ├── users_handler.py   # User auth
│   └── admin_handler.py   # Admin functions
├── index.html             # Landing page (UPDATED with meta tags)
├── user/dashboard.html    # Student portal (UPDATED)
├── frontend/              # Mirror of frontend files (UPDATED)
├── render.yaml            # Render deployment config
└── README.md              # Updated with recent changes
```

---

## Testing the AI Answer Format

**Sample Lesson:**
```
Photosynthesis is the process by which plants convert sunlight, water, and carbon dioxide 
into glucose and oxygen. This process occurs in the chloroplasts. The mitochondria is 
the powerhouse of the cell and produces ATP through cellular respiration.
```

**Test Results by Type:**

| Type | Question Format | Answer Format |
|------|-----------------|---------------|
| Multiple Choice | A/B/C/D options | A, B, C, or D |
| True/False | True/False options | True or False |
| Identification | Fill-in-the-blank (_____) | Keywords (chloroplasts, mitochondria, ATP) |

---

## To Do / Future Enhancements

- [ ] Create OG image (1200x630px) for social media preview
- [ ] Add more quiz question types
- [ ] Improve password hashing (SHA-256 → bcrypt)
- [ ] Add user profile pictures
- [ ] Export quiz to PDF

---

*Last Updated: May 5, 2026*
*Project: FRES Web - Filipino Reviewer & Evaluation System*
*For: NwSSU College of Computer Studies*