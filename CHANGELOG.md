# FRES WEB FIN Change Log

## Summary
This update transitions FRES from official Google Gemini AI generation to a local `Puter.js`-based generator for the student dashboard.

## What changed
- Added `frontend/js/components/puter.js`
  - Implements local question generation from lesson text without relying on external Gemini API calls.
  - Supports multiple choice, true/false, and identification question formats.
- Updated `frontend/js/components/generator.js`
  - Switched generation logic to use `generateReviewerLocal()` from `puter.js`.
  - Removed the backend `/api/ai/generate` dependency for quiz generation.
- Updated frontend UI copy
  - Changed the dashboard connection status from "Gemini AI" to "Puter.js".
  - Updated the admin system info label to "Local Puter.js Generator".
  - Updated the homepage copy to advertise Puter.js instead of Google Gemini.

## Why this change was made
- The previous Gemini integration failed due to an expired or invalid API key.
- Puter.js allows local, offline question generation directly in the browser.
- This removes the dependence on an external AI service for quiz creation.

## Notes
- The backend AI endpoint remains in place as legacy support but is no longer required for normal quiz generation.
- If you'd like, I can also rename or remove the legacy Gemini handler and clean up unused server API routes.
