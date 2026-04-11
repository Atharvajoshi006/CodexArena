# Deployment Setup

This repo is currently a single Django application with server-rendered pages and backend APIs in the same codebase.

Because of that, the safest deployment split is:

- Render hosts the Django app and PostgreSQL database.
- Vercel sits in front as the public frontend entry point and rewrites requests to the Render backend.

That gives you the Vercel + Render setup you asked for without forcing a risky full frontend rewrite first.

## Render backend

Files added for Render:

- `requirements.txt`
- `runtime.txt`
- `render.yaml`

Render service settings already prepared:

- `gunicorn codexarena.wsgi:application` as the start command
- `collectstatic` and `migrate` in the build command
- `/health/` as the health check path
- PostgreSQL wired through `DATABASE_URL`
- `autoDeploy: false` so it will not start auto-shipping code after you import it

## Vercel frontend

File added for Vercel:

- `vercel.json`

Right now `vercel.json` rewrites all traffic to:

- `https://codexarena-backend.onrender.com`

If you keep the Render service name as `codexarena-backend`, this should match the default Render hostname.
If you rename the Render service, update the destination in `vercel.json` before deploying Vercel.

## Required environment variables

Use `.env.example` as your reference.

Important production values:

- `SECRET_KEY`
- `DEBUG=false`
- `DATABASE_URL`
- `BACKEND_PUBLIC_URL=https://codexarena-backend.onrender.com`
- `FRONTEND_URL=https://your-project.vercel.app`
- `ALLOWED_HOSTS=127.0.0.1,localhost,codexarena-backend.onrender.com`
- `CSRF_TRUSTED_ORIGINS=https://codexarena-backend.onrender.com,https://your-project.vercel.app`

Notes:

- Render automatically provides `RENDER_EXTERNAL_HOSTNAME`, and the Django settings now honor that.
- `FRONTEND_URL` matters once traffic is coming through Vercel so CSRF and host checks stay valid.
- Cookies are configured for HTTPS production use.

## Local development

Local development still works with SQLite when `DATABASE_URL` is not set.

Recommended local commands:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Future improvement

If you later want a true standalone frontend on Vercel, the next step would be moving these Django templates into a separate frontend app such as Next.js, React, or plain static pages that consume JSON APIs from Render.
