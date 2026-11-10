# Local Russian UI inspection on Windows

The local stack is separate from the existing application database. Nothing is deployed.

- Frontend: http://127.0.0.1:3003
- API documentation: http://127.0.0.1:8003/docs
- API health: http://127.0.0.1:8003/health
- PostgreSQL: `127.0.0.1:55432`, database `ratchethub_dev`.

## Start after restarting Windows

From PowerShell:

```powershell
cd C:\Users\Administrator\Desktop\Ratchethub
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\start-local.ps1
```

The script checks/starts this project's cluster, applies existing migrations only to its database, starts hidden persistent API/frontend processes, verifies HTTP health, and creates the local owner once through normal registration. Repeat starts reuse owned processes and preserve the existing account/sessions. Occupied ports belonging to other processes cause an error instead of stopping or reusing them. No elevated shell should be necessary. The execution-policy option applies only to this invocation.

Stop this stack (data is retained):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\stop-local.ps1
```

Only wrappers recorded with matching PID, creation time and project command path, their child processes, and the cluster under `.local/postgres` are stopped. Other PostgreSQL installations, containers and application servers are not stopped.

## Local login

Open the frontend and choose **Войти → Телефон**. The shop is **Локальный автосервис**. Read the phone and generated password privately from `.local/account.json` in your editor. Do not paste that file into logs, reports or Git. The account is a real local `owner`, created using `/v1/auth/register`; authentication is not bypassed. Onboarding was completed through the normal UI. Existing registration/login forms can be used for further local test shops.

`.local/settings.json` and `.local/environment.json` contain generated database/JWT credentials and local provider settings. The entire `.local/` directory is Git-ignored. No production environment file is overwritten. Keep these files with the local data; do not replace the passwords while retaining the cluster. Startup deliberately does not reset passwords or modify existing accounts.

## Actual services and explicit offline behavior

The frontend is the existing Next.js development server, and the backend is the real FastAPI application connected to real local PostgreSQL. Existing global Node/pnpm/Python dependencies were reused without upgrades. PostgreSQL **18** was already installed; the repository Compose template specifies 16. The final database uses ICU `und` Unicode collation so Cyrillic case-insensitive name lookup works. Existing migrations reached `0046_enterprise_plan_price`. The application role is not a superuser and cannot create roles/databases or bypass RLS.

Docker's earlier unavailable daemon is not required. Redis is optional for the selected existing memory queues (`SMS_QUEUE_BACKEND=memory`, `VOICE_QUEUE_BACKEND=memory`, readiness does not require Redis), so no Redis service is started. Redis-backed queues are not being tested.

- **Real local:** login/logout/refresh, protected routes, shop setup, customer/vehicle/appointment forms, settings and PostgreSQL-backed records. Use only synthetic data.
- **Offline heuristic AI:** explicitly selected with `AI_PROVIDER=heuristic`; no OpenAI key is supplied. This is existing bounded offline processing, not live AI chat/STT/TTS acceptance.
- **Fake communications:** existing fake Twilio SMS/voice and fake email senders. They do not place real calls or deliver messages. Development OTP codes can be displayed by the application's existing development flow; no external provider is required for the configured phone/password account.
- **Unavailable/unverified:** real OpenAI or local model servers, Stripe checkout/payment/portal, external calls/SMS/email delivery, DMS/accounting sync, OAuth/SSO and Redis-backed background delivery. No external integration is connected by setup. Public VIN decoding may require network access if you invoke that feature.
- Workflow definitions/runs use the application's existing in-memory store; they are not made database-durable by this setup and can disappear on API restart. The seeded service catalog retains its canonical English names and technical select values; setup does not rewrite them or alter Russian translations.

## Diagnostics and limitations

Logs are `.local/api.stdout.log`, `api.stderr.log`, `web.stdout.log`, `web.stderr.log`, `postgres.log` and `migrations.stderr.log`. Scripts report failures without printing credentials. The dev server can emit existing Windows Watchpack EINVAL warnings when scanning system files and a Next.js smooth-scroll warning; these were not repaired through unrelated configuration changes. Browser evidence is under `.local/evidence/`.

The first experimental `C`-locale database `ratchethub_local` remains unused inside the same isolated cluster. The final app uses only `ratchethub_dev`; no shared/production database was reused or deleted. The script reuses the installed `pg_ctl.exe` on PATH; ensure the same PostgreSQL major version remains available for this cluster after restarting Windows.

This setup makes local manual inspection possible. It is not a production-readiness or external-integration sign-off. Do not point these scripts or credentials at production. Do not run the broad pytest suite against this manual-review database: its existing cleanup fixture deletes test-shaped tenants. Use a separate disposable test database for that suite.
