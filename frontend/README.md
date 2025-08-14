# Frontend

## Installation

Install dependencies in this directory:

```bash
npm install
```

## Environment

Copy `.env.local.example` to `.env.local` and set the backend API location:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Adjust the URL if your API runs elsewhere and restart `npm run dev` after changes.

## Development

Start the development server:

```bash
npm run dev
```

The app will be available at http://localhost:3000.

## Troubleshooting

- **CORS errors** – confirm the backend allows requests from the frontend origin.
- **Wrong API URL** – ensure `NEXT_PUBLIC_API_URL` matches the backend.
