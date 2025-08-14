# AI Study Buddy with Memory

An AI-powered study assistant that:
- Generates flashcards from any notes, PDFs, or lecture transcripts.
- Uses spaced repetition to maximize retention.
- Tracks your knowledge health over time.
- Acts like a personal coach, telling you exactly what to study each day.

## Tech Stack
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **Queue:** Redis + RQ (for background processing)
- **Frontend:** Next.js (later in the build)
- **AI Processing:** LangFlow + PyTorch (custom models later)

## Goals for MVP
1. Upload notes → auto-generate flashcards.
2. Daily study plan from the coach system.
3. Memory tracking + spaced repetition.
4. Launch closed beta within 8 weeks.

## Development Notes

If you encounter `npm WARN Unknown env config "http-proxy"`, it comes from legacy
environment variables (`npm_config_http_proxy` or `npm_config_https_proxy`).
Modern npm expects the `proxy` and `https-proxy` settings instead. The
`frontend/.npmrc` file maps these to the standard `HTTP_PROXY` and `HTTPS_PROXY`
variables. Clearing the old `npm_config_http_proxy` variables fixes the warning.
