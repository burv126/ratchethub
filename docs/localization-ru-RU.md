# Russian localization (ru-RU)

## Russian brand wordmark — 2026-10-21

Owner-selected display name: **АвтоЦентр**. Updated the shared header/hero/authenticated wordmark and accessible label, browser metadata, homepage brand mention, and privacy/terms brand mentions. The orange hexagon remains as the stylized `о`, with the complete Cyrillic accessible name. Technical asset paths and backend identifiers are unchanged. TypeScript no-emit and diff-whitespace checks passed. Actual local homepage screenshots at 320/1280 px show the header and hero logos inside their viewport (`.local/evidence/brand-autocentr-{width}.png`); browser title is `АвтоЦентр`. No functionality, authentication or data change was made.

## Russian domestic phone input default — 2026-10-21

At the owner's request, the shared ordinary phone-input placeholder and typing formatter now default to `8 912 345 67 89`, covering login, registration, customer/team/settings/setup and other consumers of `lib/phone.ts`. Explicit international prefixes (including existing `+1` and `+7` numbers) and legacy eleven-digit US numbers preserve their digits. Backend normalization, authentication, existing stored records and Twilio's technical E.164 fields were not changed. Overlong input is retained for validation rather than silently truncated.

Changed `apps/web/src/lib/phone.ts` and added `scripts/test_phone_input.cjs`. `node --test scripts/test_phone_input.cjs scripts/test_ru_errors.cjs`: **58 passed / 0 failed**; TypeScript `--noEmit`: **passed**. The live local customer dialog visually showed the new placeholder and `8` input formatting; no form was submitted. Screenshot: `.local/evidence/phone-default-8.png`. Browser tooling masks phone DOM values, so visual evidence and unit tests are used rather than claiming a successful raw-DOM-value assertion. No production operation or database update was performed.

## Usable isolated Windows local environment — 2026-10-21

The earlier missing local-environment/account blocker has now been addressed for **local owner-account inspection**. See `LOCAL_SETUP.md`, `start-local.ps1` and `stop-local.ps1`. This is local setup, not deployment or production approval. External provider acceptance, other roles and durable workflow acceptance remain outside the verified scope.

- Real frontend: `http://127.0.0.1:3003`; real FastAPI: `http://127.0.0.1:8003` (`/docs`, `/health`). Frontend, API and the frontend's same-origin `/api-backend/health` proxy each returned **HTTP 200**. Persistent hidden launcher processes are tracked under ignored `.local/processes.json`; services are left running for manual inspection.
- Created a separate project-local PostgreSQL cluster at `.local/postgres`, listening on **127.0.0.1:55432**, without reusing the pre-existing application database or its credentials. Reused installed PostgreSQL **18** binaries; the repository Compose template specifies 16, so this does not certify version-16 compatibility. Final application database: **`ratchethub_dev`**, ICU `und` locale, with a generated non-superuser/non-BYPASSRLS application role. Existing Alembic migrations reached **`0046_enterprise_plan_price`**; no migration/schema source was added or changed.
- Initial setup with a `C`-locale database demonstrated failed Cyrillic lowercase matching. Rather than changing auth code, a fresh ICU database was created using existing migrations. `lower('Локальный автосервис') = 'локальный автосервис'` then returned true, and real Russian-name login succeeded. The initial isolated `ratchethub_local` database remains unused; no shared data was deleted.
- Created the local owner through normal `/v1/auth/register` phone/password registration. Real `/v1/auth/me` **200**, `/refresh` **200**, `/logout` **204**, and anonymous `/me` **401** were checked. Passwords/JWT/database secrets remain only in Git-ignored `.local/` files; tokens were kept in memory and not printed or saved in reports. Credentials for manual login are in `.local/account.json`.
- Browser execution used the normal frontend login form and the real backend/database, not mocked successful authentication. Completed the actual three-step shop setup UI, saved contact details, weekday hours and the existing catalog, and reached the authenticated Russian dashboard. Customer navigation and its add-customer dialog were inspected without creating customer data. Browser reload retained the real local session once an unrelated helper logout check was no longer rerun. The setup helper now creates/verifies the account once and preserves existing sessions on later starts; application logout behavior was not modified.
- After the final full local stop/restart, reloading the authenticated settings page recovered the real owner session without another login. Dashboard/header rendering was inspected at **320, 390, 768 and 1280 px**; the 390 px navigation drawer opened/closed with Russian labels. Screenshot evidence is `.local/evidence/dashboard-{width}.png` and `mobile-menu-390.png`. The existing dashboard title truncates heavily at narrow widths (especially 320 px); this setup does not certify every private layout or change existing UI. Console inspection found the smooth-scroll advisory but no JavaScript error entries in the captured checked flows (`browser-console.json`).
- Checked start/stop/restart plus repeat-start behavior. Only recorded project wrapper trees and the cluster under this checkout were stopped. The final successful start reports the URLs after HTTP checks; data/account were retained. Existing dependencies and lockfiles were reused, with no installations or upgrades.
- Explicit local modes: **heuristic/offline AI**, existing **fake SMS/voice/email** providers and memory queues. PostgreSQL-backed application records are real local records. No OpenAI, Stripe, Twilio, SMTP or OIDC secrets are configured; no provider call, real payment, real message or production/customer data operation was performed. Redis is optional for the selected memory queues and is not started. Workflow storage retains its existing in-memory lifetime; this setup does not add persistence.
- Existing dev-environment warnings were observed: Windows Watchpack EINVAL while scanning system files and Next.js's smooth-scroll advisory. These were not addressed through unrelated changes. Default editable catalog names and technical select values still include English canonical data; translations/data were not rewritten during setup.

Local evidence: `.local/auth-verification.json`, `.local/evidence/http-checks.json`, `.local/evidence/` screenshots and service/migration logs. These files are ignored to keep credentials, generated databases and local state out of Git. PowerShell parser checks for all three launch scripts, Python compile checks for the two setup helpers, Git ignore checks for every credential/data path and `git diff --check` passed. No backend test cleanup suite was run against the manual-review database.

Exact repository changes for setup: **`.gitignore`**, **`start-local.ps1`**, **`stop-local.ps1`**, **`scripts/local_process.ps1`**, **`scripts/local_environment.py`**, **`scripts/create_local_account.py`**, **`LOCAL_SETUP.md`**, and **this report**. Existing application/business/authentication/payment/integration/translation source files and production configuration were not changed. Generated `.local/` files are described in the setup guide. The real local owner flow now has evidence; live providers, all role combinations and production readiness do not receive a sign-off from this setup.

## Real functional verification attempt — 2026-10-21

**Readiness: NOT READY — real acceptance is pending access.** The user confirmed that a safe test environment exists and said access details would follow. At the time of this report update, no environment URL, existing test account/role credentials, isolated-database identification or approved provider sandbox connection details had been supplied. The real-flow checks below therefore remain **NOT VERIFIED**. This is an access blocker, not evidence that those flows failed. No mock successful authentication was substituted. No deployment, production operation, shared-database access or application-functionality change was performed.

### Real authentication and authenticated layouts

- Login/logout, refresh/session persistence, protected routes, real authentication failure messages and role-based permissions: **NOT VERIFIED**. Blocker: the authorized test endpoint/account and role access details are pending. Existing unit tests and earlier fixture login are not counted as real authentication.
- Russian labels in authenticated navigation and the authenticated header at **320, 390, 768 and 1280 px**: **NOT VERIFIED** for the same blocker. No authenticated screenshot is claimed. The public-header screenshots and real frontend button/keyboard interactions in the preceding task remain valid in their narrower, explicitly unauthenticated scope; they were not repeated or relabelled as private-page acceptance here.
- A configuration-only local probe found development mode, OpenAI selected without a key, fake SMS/voice/email providers and absent Stripe/Twilio/SMTP/OIDC secrets. It did not establish access to the user's separate safe environment. No credential values were printed or saved. See `environment-redacted.json` in the evidence directory below.

### Persisted workflow verification

Create → save → browser reload → retrieve → edit/save → safe execution → inspect persisted canonical identifiers: **NOT VERIFIED against an isolated database**. The isolated target and existing account remain pending; no production or shared workflow was created, edited, executed or deleted. All 19 existing workflow tests pass in the disconnected unit selection, but they are not database persistence or real authenticated browser evidence.

There is also a pre-existing architecture limitation requiring explicit acceptance: the checked-in workflow API's runtime dependency calls `get_workflow_runtime()`; `build_workflow_runtime()` defaults to `InMemoryWorkflowStore`. The store holds workflow/run/event/retry dictionaries/lists in process memory. A source search found no database-backed `WorkflowStorePort` implementation or application override. Browser reload within the same running process may retain an item, but that is not proof of database durability or retention after process replacement. `apps/api/app/workflows/store.py` and `factory.py` are text-identical to both Git baseline `1dda82556a22ffcaae5727acc22a5925c8a94e51` and the saved pre-fix snapshot (`source-comparison.json`). This limitation is **not introduced by localization** and was not repaired/refactored. Any isolated staging deployment with different storage wiring must be checked on its own evidence.

No completed runtime persistence probe is claimed. An optional sandboxed local async store probe stalled and was stopped without a result; it is excluded from pass counts. The storage conclusion above rests on the inspected source, not that interrupted attempt.

### External integration verification matrix

Configuration statements below refer only to the available local configuration/source. Tenant connections were not queried because no authorized isolated tenant has been identified. For **every entry**, a safe live end-to-end test is currently blocked by missing approved target/access details; real provider acceptance is **NOT VERIFIED**. Machine-readable rows with configuration, sandbox availability, evidence scope and status are saved in `integration-matrix.json`.

- **OpenAI chat/STT/TTS:** selected locally, API key absent; sandbox access unavailable locally. Heuristic/unit processing passes apart from the documented missing-key TTS test. Russian speech and provider-generated responses were not executed.
- **Ollama/local Whisper/Piper:** default endpoints exist; running services and isolated test availability were not established. No model request was made.
- **Stripe checkout/portal/webhooks:** local key and signing secret absent; no approved sandbox credentials. Mocked paid/unpaid checkout checks pass. No actual checkout, payment, portal session or signed provider delivery was initiated.
- **Twilio SMS/voice/number provisioning:** fake providers selected; local SID/token absent. Fake-provider/webhook tests pass in their unit scope. No real call, SMS or number operation was performed.
- **SMTP email:** fake provider selected and SMTP credentials absent. Template/fake checks provide no live delivery evidence. No email was sent.
- **Shopmonkey, Tekmetric, AutoLeap and Mitchell** (each): adapter/direct-import connector present; actual tenant configuration and sandbox credentials unknown. Demo/sample import checks pass; real export/import/sync remains untested. Missing credentials or `use_sample=true` produce existing sample data in the direct connector, so a successful sample import is not a provider handshake.
- **QuickBooks:** registered adapter present; tenant connection/sandbox unknown. Demo integration checks only; no accounting sync.
- **Google Calendar, Google Business and Facebook** (each): MCP adapter definitions present; tenant OAuth configuration/sandbox unknown. MCP demo checks only; no OAuth handshake, calendar write or publication.
- **Enterprise OIDC/SSO:** local client secret absent; tenant IdP configuration unknown. In-memory enterprise checks pass, but neither an actual IdP exchange nor real role mapping was exercised.
- **NHTSA vPIC VIN decoding:** public endpoint configured in source and requires no secret; no approved sandbox endpoint/test environment was supplied. No external VIN request or customer VIN transmission was made.
- **Redis/background execution:** default endpoint configured; running state and an isolated queue were not established. No live queued-job acceptance test was performed.

Localization evidence is bounded: freshly generated OpenAPI equals the completed implementation's document across **268 paths** (`openapi-comparison.json`); existing tests cover canonical codes, Russian/English parsing, localized templates and display-only error conversion. Earlier reviewed webhook/payment request construction remains unchanged. These facts do **not** establish identical live provider payloads/responses. Some human-readable content intentionally becomes Russian. The generic integration/MCP adapters can report connected/demo results without an actual provider exchange; those outputs are not counted as real integration verification.

### Fresh regression checks and baseline comparison

Evidence directory: `C:/Users/Administrator/.codex/visualizations/2026/10/20/01a15acc-44aa-7f82-b230-f78e9325f821/real-functional-verification/`.

- `pnpm --filter @asa/web build`: **PASS**, exit 0, **52/52 pages** (`build.txt`). Host execution permits Windows standalone symlinks; nothing was deployed.
- `node apps/web/node_modules/typescript/bin/tsc --noEmit -p apps/web/tsconfig.json`: **PASS**, exit 0 after build (`typecheck.txt`).
- `pnpm lint:web`: **PASS**, **0 errors / the same 8 baseline warnings** (`lint.txt`).
- `node --test scripts/test_ru_errors.cjs`: **55 passed / 0 failed / 0 skipped** (`frontend.txt`).
- `python scripts/verify_ru_localization.py`: **PASS**, Russian templates/interpolation/conversation cues/dates/TwiML. `python -m compileall -q apps/api/app`: **PASS**.
- From `apps/api`, using the documented disconnected database/fake-provider environment below and additionally `STRIPE_WEBHOOK_SECRET=''`: `python -m pytest -p pytest_localization_disconnected -q tests/agents tests/workflows tests/analytics tests/scheduling tests/voice tests/sms tests/localization tests/integrations tests/saas/test_billing_checkout.py tests/test_phase1_auth_isolation.py --tb=short`: **501 passed / 2 failed / 8 skipped**, 5.24 s (`api.txt`). All eight skipped cases are database-dependent auth tests and are **NOT VERIFIED**. No shared DB cleanup fixture was permitted to connect.
- With the same isolation environment: `python -m pytest -p pytest_localization_disconnected -q tests/core/test_permissions.py tests/enterprise tests/mcp_hub tests/import_engine --tb=short`: **29 passed / 0 failed**, 2.06 s (`permissions-connectors.txt`). These use inspected in-memory/demo/sample paths; role-policy passes are not proof of a real signed-in account's authorization.
- Combined API selections: **530 passed / 2 failed / 8 skipped**, 540 cases. The complete database-dependent suite was not executed against shared data. Frontend test counts are separate.
- OpenAPI generated without app startup/database access using the existing external `contract_probe.py`: **268 paths, equal to the completion document** (`openapi.json`, `openapi-comparison.json`).
- `git -c safe.directory=C:/Users/Administrator/Desktop/Ratchethub diff --check`: **PASS**.

The two failures are unchanged from the documented controlled baseline: `test_default_service_catalog_uses_session_outside_test` expects bare `SessionServiceCatalog` but receives its existing `CachingServiceCatalog` wrapper; `test_speech_pipeline_tts` selects OpenAI without a key and raises `AIProviderUnavailable`. The prior fresh completion-start run reproduced both (**407 passed / 2 failed**, `final-readiness-2026-10-21/completion-baseline.txt`), and the historical Git comparisons below remain applicable. No new automated regression appeared in the completed selections. Historical fixture contamination and clock-sensitive scheduling failures were not fixed or claimed resolved by their absence here.

### Remaining blockers and files changed

Production acceptance still requires: the safe test URL and secure access to the existing account(s)/roles; confirmation/identification of the isolated database; real authentication and authenticated layouts at the requested widths; a recorded workflow lifecycle with canonical data inspection and explicit acceptance of actual storage durability; approved sandbox integration checks including signed callbacks; and the full applicable database-backed suite on disposable data. The user's statement that a safe environment exists is recorded, but is not enough to execute or sign off those tests.

Only **`docs/localization-ru-RU.md`** was modified in the repository during this verification attempt. External logs, redacted configuration, source/OpenAPI comparisons and integration matrix contain the evidence for completed checks. No source/test/dependency/schema/authentication/payment/integration/deployment code was changed. The prior mobile-header patch remains intact. **Final classification for the evidence currently available: NOT READY.**

## Mobile public-header correction — 2026-10-21

**The mobile header clipping recorded in the audit below is resolved in the checked viewports.** This narrowly scoped correction does not change the overall production-readiness decision: real authentication and critical integration acceptance remain outstanding. No deployment was performed.

### Cause and minimal change

The public header is rendered in `apps/web/src/app/page.tsx` near line 181. Its inner `flex` row previously used the default `flex-wrap: nowrap`, with a logo, `gap-3`, horizontal padding and a `shrink-0` action group. The full Russian actions exceed the remaining width at 390/320 px. The existing `.landing-nav` fixed/inset positioning in `globals.css` constrains it to the viewport; the shared `.btn-primary` padding contributes to the action's intrinsic width. Root scroll-width checks missed the visibly clipped control.

The only application edit adds **`flex-wrap sm:flex-nowrap`** to that header's inner container. Below Tailwind's existing 640 px breakpoint, the intact action group can occupy a second row; from 640 px upward the original single row remains. No global CSS, button text, padding, colors, handler, link, authentication code or accessibility semantics changed. Neither action is hidden, removed or truncated. The mobile header grows to accommodate both rows.

### Browser verification and screenshots

Executed against the freshly built frontend on loopback port 3002. All three controls (brand link, `Войти`, `Начать бесплатно`) were enabled, had unobstructed center hit targets and stayed inside the viewport at **320, 375, 390, 768 and 1280 px**. Full labels remained visible; control `scrollWidth` equaled `clientWidth`. Document width equaled viewport width in all five checks. The action's right edge is **283.453125 px** at 320/375/390, **744 px** at 768 and **1192 px** at 1280, replacing the overflowing 396.984375 px narrow-screen bound. Tablet/desktop keep the original one-row arrangement; the changed CSS resolves to `nowrap` there.

Both action buttons were actually clicked at **each of the five widths**, and the appropriate Russian login/registration dialog appeared and closed: **10/10 action-opening checks passed**. No credentials were entered, account created or authentication form submitted. Keyboard checks at 320 and 1280 confirmed the unchanged order **brand link → Войти → Начать бесплатно**, `:focus-visible` on all three controls, Enter opening login and Space opening registration. Native link/button elements, accessible names and handlers are unchanged. These checks demonstrate frontend control behavior, not real login.

Screenshots saved and dimensions checked (the 320 px capture is 844 px high; the others are 900 px high):

- [320 px](C:/Users/Administrator/.codex/visualizations/2026/10/20/01a15acc-44aa-7f82-b230-f78e9325f821/mobile-header-fix/header-320.png)
- [375 px](C:/Users/Administrator/.codex/visualizations/2026/10/20/01a15acc-44aa-7f82-b230-f78e9325f821/mobile-header-fix/header-375.png)
- [390 px](C:/Users/Administrator/.codex/visualizations/2026/10/20/01a15acc-44aa-7f82-b230-f78e9325f821/mobile-header-fix/header-390.png)
- [768 px](C:/Users/Administrator/.codex/visualizations/2026/10/20/01a15acc-44aa-7f82-b230-f78e9325f821/mobile-header-fix/header-768.png)
- [1280 px](C:/Users/Administrator/.codex/visualizations/2026/10/20/01a15acc-44aa-7f82-b230-f78e9325f821/mobile-header-fix/header-1280.png)

The same external `mobile-header-fix` directory contains `header-measurements.json`, `button-clicks.json`, `keyboard.json`, the pre-patch page snapshot and check logs. Early captures affected by compositor resize timing were replaced; final PNG pixel widths match all five requested widths. Temporary browser tabs were closed, viewport overrides reset and the preview server stopped after verification.

### Checks and exact files changed

- `node --test scripts/test_ru_errors.cjs`: **55 passed / 0 failed / 0 skipped**.
- `node apps/web/node_modules/typescript/bin/tsc --noEmit -p apps/web/tsconfig.json`: **PASS**, exit 0 after build.
- `pnpm --filter @asa/web build`: **PASS**, exit 0, **52/52 pages**; run with host permissions for Windows standalone symlinks. No dependency/configuration change was required.
- `pnpm lint:web`: **PASS**, 0 errors, the same **8 baseline warnings**.
- `python scripts/verify_ru_localization.py`: **PASS**, Russian templates/interpolation/conversation cues/dates/TwiML.
- `git -c safe.directory=C:/Users/Administrator/Desktop/Ratchethub diff --check`: **PASS**.

Exact repository files changed by this patch: **`apps/web/src/app/page.tsx`** (one class-name line) and **`docs/localization-ru-RU.md`** (this evidence). No new automated test source was added for this responsive-only change; actual browser geometry, click, keyboard and screenshot checks provide the focused regression evidence. Backend/API/database/payment/integration sources were untouched, and no backend suite was rerun for this CSS-only correction. Prior baseline failures below remain unresolved and were not altered to make checks pass.

**Authenticated header: NOT VERIFIED.** No safe real test account/environment was available; this patch targets the public landing header only. Authentication/session behavior and other acceptance gaps retain their earlier NOT VERIFIED status. Overall production readiness remains **NOT READY**, despite this specific layout defect being fixed.

## Final pre-deployment verification — 2026-10-21

**Decision: NOT READY.** No deployment or production operation was performed. Automated compatibility evidence is strong in the covered paths, but real authentication, database-backed workflows and critical provider integrations remain unverified. This audit also discovered a clipped public-header action on narrow mobile screens. This section supersedes earlier readiness statements; earlier results below remain historical evidence.

### Fresh automated results

Commands ran from the repository root unless noted. Logs are under `C:/Users/Administrator/.codex/visualizations/2026/10/20/01a15acc-44aa-7f82-b230-f78e9325f821/final-readiness-2026-10-21/`.

- `pnpm --filter @asa/web build`: **PASS**, 52/52 static pages generated, host retry exit 0 (`build-host.txt`). The first sandbox attempt failed during standalone packaging with Windows `EPERM` creating symlinks (`build.txt`); compilation/page generation had completed. The identical command succeeded with host permissions, without code/configuration changes. Deployment-platform packaging is still a separate acceptance step.
- `node apps/web/node_modules/typescript/bin/tsc --noEmit -p apps/web/tsconfig.json`: **PASS**, exit 0, including a fresh check after the successful build.
- `pnpm lint:web`: **PASS**, **0 errors / 8 warnings** (`lint.txt`). The same eight findings listed in the historical audit remain: unsupported ARIA attributes in admin shops and Sidebar; unused appointments helper, walk-in directive and home Link; missing effect dependencies in settings, TeamPanel and VinInput. No new warning was found.
- `python -m compileall -q apps/api/app`: **PASS**, exit 0.
- `python scripts/verify_ru_localization.py`: **PASS**, including a second check after the successful build. This checks bounded templates/interpolation/conversation cues/date formatting/TwiML; it is not exhaustive UI or provider acceptance.
- `node --test scripts/test_ru_errors.cjs`: **55 passed / 0 failed / 0 skipped** (`frontend.txt`). Includes errors/privacy, unchanged payload objects, notification/workflow display, clock values and Russian labels.
- From `apps/api`, with the exact disconnected database/fake-provider environment documented under “Safe test isolation” below: `python -m pytest -p pytest_localization_disconnected -q tests/agents tests/workflows tests/analytics tests/scheduling tests/voice tests/sms tests/localization --tb=short`: **484 passed / 2 failed**, 486 total, 5.15 s (`api.txt`). All 77 added localization cases and all 19 workflow cases pass. This covers Russian/English/invalid input, scheduling, heuristic chatbot processing, reports and fake messaging; it does not verify persisted records or real AI delivery.
- With the same isolation settings and additionally `STRIPE_WEBHOOK_SECRET=''`: `python -m pytest -p pytest_localization_disconnected -q tests/integrations tests/saas/test_billing_checkout.py tests/test_phase1_auth_isolation.py --tb=short`: **17 passed / 0 failed / 8 skipped**, 1.99 s (`integrations-auth.txt`). The eight database-dependent auth tests skipped because the required PostgreSQL environment was unavailable. They are **NOT VERIFIED**, not passes. Integration tests use in-memory/demo adapters; billing tests use mocks and cover paid/unpaid checkout behavior without a payment.
- `git -c safe.directory=C:/Users/Administrator/Desktop/Ratchethub diff --check`: **PASS**, exit 0.

### Every fresh failure and baseline evidence

1. `tests/scheduling/test_catalog_booking_decision.py::test_default_service_catalog_uses_session_outside_test`: expects a bare `SessionServiceCatalog`, while the unchanged factory returns a `CachingServiceCatalog` wrapper. **Existing baseline assertion mismatch**, not a localization regression.
2. `tests/voice/test_voice_ai.py::test_speech_pipeline_tts`: selects OpenAI TTS without `OPENAI_API_KEY` and raises `AIProviderUnavailable`. **Missing credentials/environment**, not a localization regression. No provider call was made and no fake success substituted.

For a fresh controlled comparison, the same existing selection (excluding the new `tests/localization` directory) was run from the saved completion-start `before/apps/api` snapshot with `PYTHONPATH='.;C:/Users/Administrator/Desktop/Ratchethub/scripts'` and the same disconnected/fake-provider environment: `python -m pytest -p pytest_localization_disconnected -q tests/agents tests/workflows tests/analytics tests/scheduling tests/voice tests/sms --tb=short`. Result: **407 passed / the identical 2 failed**, 409 total, 4.53 s (`completion-baseline.txt`). This snapshot is a saved working-tree baseline, not a Git commit. The committed pre-localization reference remains `1dda82556a22ffcaae5727acc22a5925c8a94e51`; its original full-suite evidence and individual failure diagnoses are retained below.

The historical seven contaminated registration fixtures and time-dependent scheduling failures were not repaired or rerun against the shared database. Their absence from this isolated selection does not establish resolution. The complete database-backed suite still requires a disposable database. No newly introduced automated-test failure was identified in these fresh completed runs.

### Source, contract and data-safety review

- Reviewed the current Git diff, including authentication/dependency guards, JWT handling, billing and Twilio webhook changes. In those critical files, differences from the Git/pre-localization references are human-facing strings; authentication branches, role checks, exception types, HTTP statuses, payment transitions, signature verification and logging calls remain structurally unchanged. AST comparison with string contents removed supports that finding but is not proof by itself: the critical string diffs were also inspected for technical-value changes. The twelve checked critical files are text-identical to the saved completion-start versions (`critical-source-comparison.json`).
- Generated OpenAPI by importing the app and deferred routers, without startup/database access: `python <evidence-root>/localization-completion/contract_probe.py apps/api <this-audit-directory>/openapi.json`. Parsed JSON equals the prior completion's canonical document across **268 paths**, including schemas/defaults/enums. Earlier comparison with Git has the documented localized descriptive/message defaults; do not interpret this as byte-identical error prose to the English Git baseline. Original localization translated some backend human-readable exception details, while the later error-boundary fixes preserved their existing contracts.
- All checked API `models.py`, `enums.py` and migration Python sources match Git text except `app/domain/enums.py`, whose only diff is the `Invalid role` exception's Russian prose. Enum members/values, ORM schemas and migration definitions are unchanged. No database or customer data was accessed or modified during this audit.
- Reviewed Russian input aliases, error presentation/redaction and representative date/number/currency display boundaries. Russian aliases feed existing identifiers; canonical service names and API values remain unchanged. Currency formatting still uses USD/cents rather than currency conversion; locale formatting is for rendering. OpenAPI equality and existing Russian/English tests provide compatibility evidence, not universal proof for all possible natural-language input.
- The large working-tree diff also contains pre-existing dependency/deployment changes. This audit did not introduce, upgrade, deploy or certify those as localization work. No production secret or customer record was inspected. Stored tenant-specific integration configuration was deliberately not queried.

### Authentication, workflows and browser evidence

No safe local/staging account credentials were supplied or found in the available configuration. A redacted settings probe found development mode, OpenAI selected without a key, fake Twilio/voice/email providers and no Stripe, Twilio or SMTP credentials (`environment-redacted.json`). Docker's daemon remains unavailable (`dockerDesktopLinuxEngine` pipe missing); the earlier inability to provision a disposable database remains unresolved. No shared database, production credentials or authentication bypass was used.

**NOT VERIFIED with real authentication:** login/logout, refresh/session persistence, protected routes, profile/settings persistence, role-based access and actual server authentication error flows. Automated/mock error tests do verify Russian display behavior, but cannot substitute for these acceptance tests. Creating/editing persisted records, server-backed dashboard navigation, real scheduling/workflow execution, notifications and reports with a real tenant also remain **NOT VERIFIED** end to end. The selected unit/fake-provider tests above passed in their stated scope.

Fresh browser checks used the built frontend on loopback port 3002, with no credentials entered and no login/registration submitted. The public landing page and login dialog were observed at 1280 × 900 and 390 × 844. Visible copy was Russian apart from retained branding/technical abbreviations; `html.lang` was `ru-RU`. The login dialog's fields and buttons were readable at both widths. The earlier signed-in dashboard/settings/customer/workflow checks below remain **historical fixture-backed UI evidence**, not real backend authentication, and were not relabelled as fresh authenticated execution. Admin notification views, all role combinations and all private mobile pages remain unverified. Temporary frontend processes were stopped, tabs closed and viewport overrides reset. The server's existing standalone/`next start` warning was recorded; this read-only preview did not validate the deployed standalone server.

**Newly discovered unresolved layout defect:** the landing header's `Начать бесплатно` action extends past the viewport. At 390 px, its DOM bounds are left **218.625**, right **396.984375** (~7 px clipped); at 320 px the same right bound clips ~77 px. Screenshots confirmed clipping. The document reports widths 390/320 respectively, so a root-scroll-width-only check misses it. Location: `apps/web/src/app/page.tsx`, header action near line 224, and existing landing navigation styles. Git shows `Start free` changed to the longer Russian label with the same button structure. Russian text expansion is a likely contributor; the English baseline was not browser-executed at these widths, so this audit does **not** establish that all narrow-width clipping was absent before localization. This is a new audit finding, not a code change made during this audit. No fix was applied because this task explicitly requests verification without additional development. Narrow-mobile acceptance fails until it is addressed and rechecked.

Static English-text spot checks found branding/provider names, technical identifiers and sample proper names (for example `Sam Chen`, Honda and Accord). These do not establish an English error regression. Custom/user-authored names and historical free text intentionally remain untranslated. Neither those checks nor the earlier fixture views support claiming that every dynamic/private surface is free of unintended English.

### External integrations and remaining acceptance gates

The registered integration inventory is Shopmonkey, Tekmetric, AutoLeap, Mitchell, QuickBooks, Twilio, email and Stripe; the AI layer also exposes OpenAI and optional local Ollama/Whisper/Piper configuration. Registration/configuration availability is not proof of an active tenant connection. No tenant/customer connection data was read.

Additional source integration surfaces include NHTSA vPIC VIN decoding, enterprise OIDC/SSO, direct DMS import connectors and MCP-hub adapter definitions for Google Calendar, Google Business and Facebook (alongside the DMS/Stripe/Twilio/email adapters). None of those external services or OAuth/SSO handshakes was executed in this final audit. Their availability and tenant configuration remain **NOT VERIFIED**; adapter presence must not be read as a configured live connection. Redis-backed/background execution and the full import pipeline also require isolated environment acceptance.

- DMS/accounting adapters (Shopmonkey/Tekmetric/AutoLeap/Mitchell/QuickBooks): registry, demo mapping and tenant-isolation behavior have automated evidence; real sandbox credentials, import/sync and provider APIs remain **NOT VERIFIED**. Base adapters are demo-capable skeletons; a local “connected” result is not proof of a live handshake.
- Stripe: mocked checkout/paid-event behavior passes; actual sandbox checkout, portal and signed webhook delivery remain **NOT VERIFIED**. Signature/payment code is unchanged in the reviewed diff. No charge was initiated.
- Twilio SMS/voice: fake-provider and webhook tests are included in the selected suite; actual Russian recognition/speech, phone provisioning, provider signatures and delivery remain **NOT VERIFIED** end to end. No message or call was sent.
- Email: template/localization and fake paths have evidence; SMTP sandbox delivery/rendering remains **NOT VERIFIED**. OpenAI chat/STT/TTS and optional local model services likewise have no live acceptance evidence; the missing-key TTS test fails as documented.

Before production approval: resolve/retest the mobile header defect; provision an isolated migrated database and real test tenant; execute login/logout/session/protected-route/role tests and critical persisted workflows; run approved sandbox payment/webhook, communication, AI and required DMS/accounting acceptance; validate packaging in the intended deployment environment. No production-readiness sign-off is given while these gates remain open.

### Files modified by this final audit

Only **`docs/localization-ru-RU.md`** was intentionally modified in the repository. Build/test caches are generated artifacts; no application, test, dependency, deployment configuration or business-logic source was edited. Fresh logs, redacted environment evidence, source comparisons and source-start hashes are in the external audit evidence directory named above. All previous implementation/audit changes were preserved.

## Completion update — 2026-10-21

The documented localization code gaps have been addressed with presentation mappings and bounded Russian input aliases. **This is not an unconditional production-readiness sign-off.** The final build/type checks pass, Russian/English regression tests pass apart from two reproduced baseline/environment failures, and selected signed-in views were inspected using a synthetic fixture API. Real authentication/database integration and live provider acceptance still require a safe target test environment.

### Fixes applied

- Added `ru-errors.ts` as the frontend error-display boundary. Known legacy English domain errors (VIN, duplicate contacts/services, walk-in state, authentication/MFA, required fields), existing machine codes, HTTP failures and Pydantic validation types display professional Russian. API readers use this boundary, and error rendering covers direct page/component paths, admin login, scanner failures, imports and walk-in booking errors.
- Kept server exception types/messages, response status codes, validation `type`/`loc`/`input`/`ctx`, structured codes, retry metadata, raw logs and payload objects intact. English API error prose remains intentionally unchanged where clients may depend on it; the browser translates its presentation. Unknown diagnostics receive a safe Russian fallback. Validation inputs/context, raw JSON objects, tracebacks, SQL, provider URLs, filesystem paths and credential-like details are not rendered as user errors. Displayed workflow diagnostic copies redact sensitive fields without mutating the underlying objects.
- Localized notification display from existing event/payload fields, legacy workflow/template names, system-health labels, integration/background log messages, benchmark labels, forecast KPI/trend text, voice-note service labels and the extra 404 punctuation. Stored workflow identities, trigger/action/event codes, report metric IDs, status values, numeric metrics and raw logs are unchanged. Unknown user-defined names and customer-authored text retain their original values.
- Added explicit Russian date aliases: today/tomorrow/day-after-tomorrow, weekdays and common inflections, next week, morning/afternoon/evening/noon, and same-day/same-time preferences. Explicit Russian 24-hour clocks including `03:15` retain the intended hour; malformed clocks do not become valid times. Existing English parsing, shop timezone and ambiguity/confirmation rules remain in place.
- Extended only personal-name recognition to Cyrillic/Ё with existing Latin/hyphen/apostrophe compatibility. Russian confirmations and short declines are tested; commands/dates/yes/no are not accepted as customer names. Explicit Russian booking, cancellation, rescheduling, service-change, availability and price phrases map to the existing English intent identifiers. Negated Russian booking/cancellation/move requests are not turned into affirmative commands.
- Added Russian service-search aliases for the existing catalog and fallback service phrases. Matching returns the original catalog ID/name/price/duration; a real Russian custom service name beats an English alias when both exist. English input is retained. Mechanic-note extraction recognizes bounded Russian service/recommendation/mileage phrases while keeping canonical service names and numeric mileage.
- Browser inspection found two additional display issues: settings used AM/PM and `open/closed` accessibility text; the mobile customer visit-type cards cramped the longer Russian labels. Settings now display 24-hour time with Russian accessibility labels while preserving HH:MM form/API values. Only those two visit-type cards stack at small widths; desktop retains the two-column layout.

### Regression tests and results

Final verification used Windows, Python 3.11.0, Node v24.19.0 and the existing pnpm/Next/TypeScript dependencies. No dependencies were upgraded.

- `pnpm --filter @asa/web build`: **passed**, 52/52 pages. The normal API rewrite was restored and checked as `http://127.0.0.1:8000/:path*`; no fixture port remains in the production routes manifest.
- `node apps/web/node_modules/typescript/bin/tsc --noEmit -p apps/web/tsconfig.json`: **passed**.
- `pnpm lint:web`: **passed**, the same **8 pre-existing warnings**, no new warnings/errors. Locations shifted with imports and display edits; rules/findings are those documented in the historical audit below.
- `python -m compileall -q apps/api/app`: **passed**.
- `python scripts/verify_ru_localization.py`: **passed**.
- `node --test scripts/test_ru_errors.cjs`: **55 passed / 0 failed**. Covers Russian display of known English errors, Russian pass-through, invalid/unknown input, privacy fallbacks, Pydantic validation, unchanged status/code/retry payloads, legacy notifications, raw-log preservation, diagnostic redaction, custom workflow names, business-hour values, mobile visit cards and 404 copy.
- Final API selection (`tests/agents tests/workflows tests/analytics tests/scheduling tests/voice tests/sms tests/localization`): **484 passed / 2 failed**, 5.15 s, 486 tests total. All **77 new localization cases** pass, including Russian, English and invalid input; all **19 workflow tests** pass. This is a selected unit/validation/fake-provider run, not the entire database-backed API suite.
- The narrower final date/intent/workflow/report/API-validation selection passed **293 tests** before the last two additional Russian/English fallback-service cases; those two are included in the final 486-test run.
- Full generated OpenAPI documents before/after this task are **byte-identical after canonical JSON serialization**, including documentation/defaults/enums, with **268 paths**. No request/response schema contract was changed. The HTTP 422/domain exception tests separately verify unchanged internal detail/type/location structures; frontend tests verify display translation without payload mutation.
- Source comparisons confirm unchanged authentication implementation, JWT/security code, database engine/ORM models, subscription/payment business logic, agent factory and frontend authentication provider. Existing business rules were not changed to repair baseline failures. No schema migration, dependency, deployment configuration or stored-data update was introduced.

### Safe test isolation and baseline comparison

No suitable disposable PostgreSQL database was available: the local role cannot create databases, and Docker's local daemon was unavailable. The shared application database was **not** used for this completion run. The opt-in test helper `scripts/pytest_localization_disconnected.py` requires the explicit disconnected test URL and then refuses all asyncpg connections immediately. This also prevents the repository's existing session cleanup fixture from deleting shared records. It is not a database-integration substitute.

Reproduction command (PowerShell, from `apps/api`; keep the disconnected URL and fake providers):

```powershell
$env:PYTHONPATH='.;../../scripts'
$env:ENVIRONMENT='test'
$env:DATABASE_URL='postgresql+asyncpg://invalid:invalid@127.0.0.1:1/ru_localization_disconnected'
$env:DATABASE_URL_SYNC='postgresql+psycopg://invalid:invalid@127.0.0.1:1/ru_localization_disconnected'
$env:OPENAI_API_KEY=''
$env:STRIPE_SECRET_KEY=''
$env:TWILIO_PROVIDER='fake'
$env:VOICE_PROVIDER='fake'
$env:EMAIL_PROVIDER='fake'
python -m pytest -p pytest_localization_disconnected -q tests/agents tests/workflows tests/analytics tests/scheduling tests/voice tests/sms tests/localization --tb=short
```

The two remaining failures are:

1. `tests/scheduling/test_catalog_booking_decision.py::test_default_service_catalog_uses_session_outside_test` — unchanged stale strict type expectation: actual `CachingServiceCatalog(SessionServiceCatalog(...))`, expected bare `SessionServiceCatalog`. Same issue as historical audit item 9.
2. `tests/voice/test_voice_ai.py::test_speech_pipeline_tts` — OpenAI TTS selected with no API key; raises the unchanged `AIProviderUnavailable` credential error. This test ID differs from the earlier audit's plugin TTS failure, but reproduces on this task's saved pre-change source under the same cleared-key environment. No live synthesis was attempted or fake success added.

The saved pre-change application/test sources ran the same existing 409-test selection with the same disconnected/fake-provider settings: **404 passed / 5 failed**, 6.32 s. Both final failures appear there. The other three were `test_reschedule_can_change_service`, `test_unavailable_preferred_start_rejects_without_suggesting` and `test_walk_in_start_books_in_progress_during_hours`. Their slot-grid/current-time expectations vary as the real clock crosses the business-day boundaries; the latter two respectively observed date-vs-time unavailability and clamping a past 12:30 start. These are unchanged scheduling fixtures/behavior, not localization fixes. Their later passes do not establish a repair. The original audit already demonstrated the service-grid and past-time issues against Git HEAD.

The earlier 711/712-test shared-database runs and seven contaminated registration fixtures remain historical evidence below. They were not re-executed against shared data, repaired, or claimed to pass here. The full database-dependent API suite still needs an isolated database. Initial disconnected runs without the fail-fast helper stalled on Windows connection delays and were stopped; they are not counted as completed runs. Early new-test failures were corrected test-call/expectation errors (keyword-only persona helper and its pre-existing unconditional English farewell behavior); production behavior was not altered to satisfy them.

### Browser execution: fixture-backed signed-in UI

A temporary development server on localhost:3001 used a loopback-only synthetic API on 127.0.0.1:18001. It had no database access, returned dummy login/refresh identities and read-only fixture responses, and rejected business writes. No real account, payment, message, production record or integration was used. The normal frontend login form was exercised with dummy credentials; this demonstrates **signed-in frontend rendering against a mock**, not backend authentication/security verification.

Actually inspected:

- Desktop 1280 px: dashboard/empty states, account settings, shop-settings forms, customer page and customer dialog.
- Mobile 390 × 844: shop settings and long synthetic shop/service names, 24-hour business hours and Russian switch labels, navigation drawer, workflow builder with a legacy English template name displayed in Russian, customer empty state and customer dialog.
- Cyrillic customer-name/phone entry and a submitted fixture conflict: English HTTP 409 detail `A customer with this phone number already exists` displayed as `Клиент с таким номером телефона уже существует.` The fixture rejected the operation and stored nothing.
- Measured document width equaled 390/1280 in the checked views, with no visible button-text horizontal overflow. Visually rechecked the corrected mobile visit cards: both Russian labels are readable at full card width; the dialog scrolls and keeps its action buttons available. Existing intentional truncation of long customer/shop header values remains.

Viewport overrides were reset and temporary fixture servers stopped. Production build output was then regenerated with its normal API target. Some browser actions/observations required their permitted retry after automatic origin-review timeouts; successful states above were subsequently observed. Notification mapping/redaction has automated coverage, but the admin notification center, real role/permission combinations, every modal, 320 px layouts and authenticated server-backed flows were not browser-verified. The temporary development process also emitted Windows Watchpack EINVAL warnings for system files; rendered test pages and the final production build succeeded. No unrelated configuration change was made for that environment warning.

### Remaining acceptance requirements and readiness

The documented code gaps are fixed in the covered paths; **not yet fully production-verified**. Required acceptance remains:

- Run the complete API/auth/CRM/billing integration suite against a disposable PostgreSQL database. Revisit the known fixture contamination without deleting shared application data or weakening production rules.
- Use a real test tenant to verify authentication/authorization, all relevant roles, notification-center views, private pages and additional mobile breakpoints. Mock-backed rendering is not proof of those backend flows.
- Execute approved sandbox checks for OpenAI/Russian STT/TTS, Twilio calls/SMS, email rendering/delivery, Stripe checkout/webhooks/portal and configured DMS/accounting integrations. No real payment, production message or live provider call was performed here.
- Russian language support intentionally consists of tested aliases for existing functionality, not unrestricted natural-language understanding. Unsupported phrases retain the existing clarification/fallback behavior. Custom catalog/workflow names, customer content, raw logs and historical records are not rewritten. New report/template presentation is Russian; arbitrary previously stored free text is not machine-translated.

No critical failure was introduced by these fixes in the completed compatibility selection, and no additional unrelated baseline failures were repaired. This evidence supports further sandbox acceptance, not an unconditional production-ready declaration.

### Exact files changed in this completion task

The following list is relative to the saved task-start sources, not all pre-existing working-tree changes. Generated/ignored build caches are excluded. **81 files**: 75 existing source files, five new implementation/test-support files and this report.

- `apps/api/app/agents/intent/datetime_parse.py`
- `apps/api/app/agents/intent/reschedule_text.py`
- `apps/api/app/agents/intent/ru_input.py`
- `apps/api/app/agents/intent/service.py`
- `apps/api/app/agents/scheduling/catalog_match.py`
- `apps/api/app/analytics/forecast.py`
- `apps/api/app/analytics/reports.py`
- `apps/api/app/infrastructure/ai/heuristic.py`
- `apps/api/app/localization.py`
- `apps/api/tests/localization/test_ru_input.py`
- `apps/web/src/app/admin/ai-usage/page.tsx`
- `apps/web/src/app/admin/billing/page.tsx`
- `apps/web/src/app/admin/login/page.tsx`
- `apps/web/src/app/admin/notifications/page.tsx`
- `apps/web/src/app/admin/page.tsx`
- `apps/web/src/app/admin/settings/page.tsx`
- `apps/web/src/app/admin/shops/[shopId]/page.tsx`
- `apps/web/src/app/admin/shops/page.tsx`
- `apps/web/src/app/admin/system-health/page.tsx`
- `apps/web/src/app/admin/tokens/page.tsx`
- `apps/web/src/app/admin/twilio-numbers/page.tsx`
- `apps/web/src/app/admin/users/page.tsx`
- `apps/web/src/app/dashboard/agents/page.tsx`
- `apps/web/src/app/dashboard/analytics/page.tsx`
- `apps/web/src/app/dashboard/appointments/page.tsx`
- `apps/web/src/app/dashboard/billing/page.tsx`
- `apps/web/src/app/dashboard/customer/[id]/CustomerDetailContent.tsx`
- `apps/web/src/app/dashboard/customer/page.tsx`
- `apps/web/src/app/dashboard/enterprise/page.tsx`
- `apps/web/src/app/dashboard/external/page.tsx`
- `apps/web/src/app/dashboard/import/page.tsx`
- `apps/web/src/app/dashboard/integrations/page.tsx`
- `apps/web/src/app/dashboard/intelligence/page.tsx`
- `apps/web/src/app/dashboard/marketing/page.tsx`
- `apps/web/src/app/dashboard/ops/page.tsx`
- `apps/web/src/app/dashboard/page.tsx`
- `apps/web/src/app/dashboard/revenue/page.tsx`
- `apps/web/src/app/dashboard/settings/page.tsx`
- `apps/web/src/app/dashboard/setup/page.tsx`
- `apps/web/src/app/dashboard/vehicles/[id]/page.tsx`
- `apps/web/src/app/dashboard/walk-ins/[id]/page.tsx`
- `apps/web/src/app/dashboard/walk-ins/page.tsx`
- `apps/web/src/app/dashboard/workflows/page.tsx`
- `apps/web/src/app/forgot-password/page.tsx`
- `apps/web/src/app/not-found.tsx`
- `apps/web/src/app/reset-password/page.tsx`
- `apps/web/src/app/status/page.tsx`
- `apps/web/src/components/LoginForm.tsx`
- `apps/web/src/components/RegisterForm.tsx`
- `apps/web/src/components/VinInput.tsx`
- `apps/web/src/components/admin/AdminShell.tsx`
- `apps/web/src/components/conversations/SmsInboxPanel.tsx`
- `apps/web/src/components/conversations/VoiceCallsPanel.tsx`
- `apps/web/src/components/conversations/VoiceNotesPanel.tsx`
- `apps/web/src/components/services/ServicesPanel.tsx`
- `apps/web/src/components/team/TeamPanel.tsx`
- `apps/web/src/lib/admin.ts`
- `apps/web/src/lib/agents.ts`
- `apps/web/src/lib/api.ts`
- `apps/web/src/lib/appointments.ts`
- `apps/web/src/lib/calls.ts`
- `apps/web/src/lib/capabilities.ts`
- `apps/web/src/lib/crm.ts`
- `apps/web/src/lib/executive.ts`
- `apps/web/src/lib/imports.ts`
- `apps/web/src/lib/integrations.ts`
- `apps/web/src/lib/marketing.ts`
- `apps/web/src/lib/ops-dashboard.ts`
- `apps/web/src/lib/platform.ts`
- `apps/web/src/lib/revenue.ts`
- `apps/web/src/lib/ru-errors.ts`
- `apps/web/src/lib/ru.ts`
- `apps/web/src/lib/shopSetup.ts`
- `apps/web/src/lib/sms.ts`
- `apps/web/src/lib/tenant.ts`
- `apps/web/src/lib/voiceNotes.ts`
- `apps/web/src/lib/walkin.ts`
- `apps/web/src/lib/workflows.ts`
- `docs/localization-ru-RU.md`
- `scripts/pytest_localization_disconnected.py`
- `scripts/test_ru_errors.cjs`

### Evidence retained

`C:/Users/Administrator/.codex/visualizations/2026/10/20/01a15acc-44aa-7f82-b230-f78e9325f821/localization-completion/`

Contains task-start source snapshots, baseline/final API logs, focused test logs, frontend tests, build/lint/type-check/localization logs, OpenAPI snapshots, modified-file inventory, fixture request traces and an evidence hash manifest. Fixture artifacts contain only synthetic data; test traces do not log credential request bodies.

## Historical regression audit — 2026-10-20

The following audit is retained as historical evidence. Its unresolved-findings list describes the pre-completion state and is superseded by the completion update above.

## Deployment readiness — NOT fully verified

Audited on 2026-10-20. Do not approve this as a completely verified Russian release. The application builds and the original test failures reproduce on pre-localization code, but Russian text coverage and Russian conversational input remain incomplete. Authenticated browser flows, dense private/mobile layouts, and live payment/email/SMS/voice integrations were not executed in this audit. One genuine localization regression in the explicit workflow reseeding helper was reproduced and fixed. No production business logic was changed merely to satisfy the original failing tests.

## Baselines and evidence

The committed baseline is **`1dda82556a22ffcaae5727acc22a5925c8a94e51`** (`feat: icon fix`). It was exported with `git archive HEAD` into an independent directory, and its own application and test sources were executed. The working tree already contained uncommitted changes before localization; Git HEAD alone cannot attribute all working-tree differences to localization. Per-file snapshots saved before translation were also compared, and a second API copy overlaid those snapshots on the current source tree. Unchanged files in that reconstruction come from the current tree; it is supplementary evidence, not an independent historical Git commit.

All three API versions used the same configured local PostgreSQL/services environment. This is a comparison against today's shared test-data state, not proof of when leftover records were originally created. Credentials were neither added nor replaced. The existing tests create/update records and run their existing session cleanup; this audit did not add database deletions, migrations, customer-data translations, or cleanup of the seven conflicting fixtures.

Raw evidence is retained outside the repository at:

`C:/Users/Administrator/.codex/visualizations/2026/10/20/01a15acc-44aa-7f82-b230-f78e9325f821/localization-audit/regression/`

Key evidence files: `git-head-api-results.txt`, `prelocal-api-results.txt`, `current-api-results.txt`, `final-serialized-api-results.txt`, `git-head-frozen-scheduling.txt`, `current-frozen-scheduling.txt`, all three `*-lint.txt` logs, `fixture-counts.txt`, `snapshot.diff`, `snapshot-comparison.json`, `current-openapi.json`, `git-head-openapi.json`, `openapi-differences.json`, `russian-input-probes.txt`, `display-boundaries.txt`, `build.txt`, and `evidence-manifest.json` (SHA-256 hashes). The earlier implementation-stage run remains at `../final-api-results.txt`: 700 passed / 11 failed. It is not the final audit result.

Environment: Windows, Python 3.11.0, Node v24.19.0, pnpm 10.34.5, Next.js 15.5.23. Native asyncio/API tests and the production build ran with normal host access because the restricted Windows execution environment blocks required socket/filesystem behavior.

## Checks executed

- `pnpm --filter @asa/web build`: **passed**, 52/52 pages generated; framework compilation, lint and type checks passed with the eight warnings below.
- `node apps/web/node_modules/typescript/bin/tsc --noEmit -p apps/web/tsconfig.json`: **passed**.
- `pnpm lint:web` and `pnpm --filter @asa/web exec eslint src`: **passed**, zero errors / eight warnings. `next lint` also emits its existing deprecation notice; it still works with the installed version.
- Same ESLint configuration and installed toolchain against copied Git HEAD and saved pre-localization web sources: **zero errors / the same eight warnings**. Temporary source copies under `apps/web/.regression-audit` were removed afterward. This compares source warnings under the same current lint policy, not a separately installed historic dependency environment.
- `python -m compileall -q apps/api/app`: **passed**.
- `python scripts/verify_ru_localization.py`: **passed**. Covers all marketing campaign/channel combinations, Cyrillic/literal-brace interpolation, custom-template preservation, Windows-safe date rendering, selected conversation cues, status display labels, TwiML locale/voices/XML escaping/callback URLs. It is a focused check, not a complete untranslated-string detector or end-to-end conversation test.
- Additional display-boundary probe: **passed**. `1234.56 USD` displays as `1 234,56 $`; an ISO UTC timestamp retains its epoch/ISO value after Russian local-time display; status `booked` displays as `Записано` while the original JSON remains byte-identical. Unknown custom labels remain unchanged.
- Git HEAD full API suite: **698 passed / 13 failed**, 85.49 s (711 tests).
- Reconstructed pre-localization full API suite: **698 passed / 13 failed**, 83.09 s (711 tests).
- Localized full API suite before the audit fix: **698 passed / 13 failed**, 83.07 s (711 tests), the same failing test IDs as both baselines.
- Original service-change failure with a test-only fixed clock (2026-10-20 13:07 America/Los_Angeles): **failed identically on Git HEAD and localized code**, 2.05 s / 2.00 s. No application source or system clock was changed for this probe.
- New workflow upgrade regression test: **passed on Git HEAD**, **failed on localized code before the fix** (11 unnecessary seed writes), **passed after the fix**. All workflow tests after the fix: **19 passed**, 2.70 s.
- First full run after the fix: **698 passed / 14 failed**, 83.89 s (712 tests). Besides the 13 shared failures, `tests/shop_setup/test_shop_setup.py::test_setup_wizard_and_phone_catalog` returned a late HTTP 404 on reloading its shop after successful setup/settings requests. A baseline pytest probe overlapped this run and invoked the same session-wide shop cleanup. That overlap is a plausible deletion race, not a proven localization defect; this run is retained rather than discarded.
- Final full API run with no overlapping pytest processes: **699 passed / 13 failed**, 82.44 s (712 tests; includes the new passing upgrade test). The transient setup 404 did not recur.
- Browser execution: public landing page at desktop width 1101 px and mobile width 390 px; mobile login/registration dialogs, privacy, terms, password-reset missing-token state, and a deliberate 404. Measured document widths matched the viewport, and visible login/registration/reset buttons had no horizontal text overflow. Registration's inner form scrolls while its submit area remains available. Screenshots were visually inspected for the mobile dialogs. The 404 title has duplicate punctuation (`Страница не найдена..`), a minor unresolved copy issue. Viewport override was reset.

## Each of the original 11 failures

The following are individual diagnoses, not an assumption that all failures are caused by missing credentials.

1. **`tests/admin/test_admin_account_separation.py::test_shop_register_creates_shop_account_not_admin`** — registration stops before account-separation assertions: HTTP 409, shop name `Separation Garage` already exists. Read-only SQL counted one matching shop. Git HEAD returns the same 409 (`Shop name already taken`); localized code changes only its display message. **Shared fixture contamination, baseline reproducible.** The intended separation assertion is not covered by this failed test run.
2. **`tests/admin/test_admin_api.py::test_admin_rejects_non_allowlisted_user`** — registration stops before the admin-denial assertion: HTTP 409 for fixed email `not-admin@example.com`; SQL counted one matching user. Same failure on Git HEAD and saved sources. **Shared fixture contamination, baseline reproducible.**
3. **`tests/admin/test_admin_api.py::test_admin_organization_detail_actions`** — registration stops before organization actions: HTTP 409 for fixed email `org-actions@example.com`; SQL counted one matching user. Same baseline failure. **Shared fixture contamination, baseline reproducible.**
4. **`tests/admin/test_admin_notifications.py::test_register_creates_admin_signup_notification`** — registration of fixed name `Signup Garage` returns HTTP 409; SQL counted one shop. Random slug/email do not make the shop name unique. Same baseline failure. **Shared fixture contamination; notification behavior is not reached by this test.**
5. **`tests/admin/test_admin_notifications.py::test_invite_staff_creates_member_joined_notification`** — fixed `Invite Garage` registration returns HTTP 409; SQL counted one shop. No invite/notification assertion is reached. Same baseline failure. **Shared fixture contamination, baseline reproducible.**
6. **`tests/agents/test_scheduling_agent.py::test_reschedule_can_change_service`** — test chooses `available_slots[4]` from the default 60-minute grid, then requests `Brake Repair` (120 minutes), whose availability grid is recomputed in 120-minute increments. At the original run's 13:07 local time, the selected next-day 09:00 start is absent from the 08:00/10:00/etc. two-hour grid. The result is `preferred_time_unavailable`, not a confirmed reschedule. The fixed-clock probe reproduces this on original Git code. At the later audit time the selected slot aligns and this test passes in all three full suites. **Pre-existing clock/grid-dependent fixture expectation, not a credential or localization error.**
7. **`tests/plugins/test_voice_plugin.py::test_call_lifecycle_events_and_metrics`** — invoking the TTS capability selects OpenAI and raises `AIProviderUnavailable: OPENAI_API_KEY is required for OpenAI text-to-speech` at `infrastructure/ai/openai_provider.py`. This happens on Git HEAD, saved sources and localized code. **Missing integration credential; synthesis and the remaining lifecycle assertions are not verified.** No fake success or provider fallback was added.
8. **`tests/scheduling/test_appointment_intelligence.py::test_walk_in_start_books_in_progress_during_hours`** — test picks today's mid-business-window 12:30 even when it is already past, then expects the unchanged timestamp. `_book_walk_in_start` already clamps past starts to the current minute. Original log: actual 13:07 versus expected 12:30; Git audit log: actual 14:08 versus 12:30. Same clamp and failure in baseline sources. **Pre-existing time-dependent test expectation.**
9. **`tests/scheduling/test_catalog_booking_decision.py::test_default_service_catalog_uses_session_outside_test`** — strict `isinstance(catalog, SessionServiceCatalog)` fails because `_default_service_catalog()` already returns `CachingServiceCatalog(SessionServiceCatalog(SessionLocal), ttl_sec=60.0)` in development. `agents/factory.py` is byte-identical to Git HEAD. **Stale test expectation against an existing wrapper; not a credential failure or localization regression.**
10. **`tests/shop_setup/test_shop_setup.py::test_create_service_rejects_duplicate_name`** — initial registration of fixed `Dup Service Garage` returns HTTP 409; SQL counted one matching shop. The duplicate-service request/assertion is never reached. Same baseline failure. **Shared fixture contamination, baseline reproducible.** Its still-English duplicate-service error is separately listed as a localization gap below.
11. **`tests/shop_setup/test_shop_setup.py::test_phone_signup_setup_email_syncs_to_owner_profile`** — initial registration of fixed `Phone Only Garage` returns HTTP 409; SQL counted one matching shop. No email synchronization is exercised by this test. Same baseline failure. **Shared fixture contamination, baseline reproducible.**

`tests/conftest.py` cleans a finite list/prefix set of shop names. None of those five conflicting names is included, and fixed user emails can remain attached to non-cleaned shops. `auth_helpers.py` randomizes a default name but respects explicitly supplied fixed names/emails. No cleanup expansion was made against the shared database. Reproduction on old code establishes that localization is not required to cause these failures; it does not establish the historical creation time of the current database rows.

### Other failures seen during the audit

The three tests in `tests/voice/test_reschedule_both.py` — `test_change_service_and_time_one_shot`, `test_change_service_and_time_two_turns`, and `test_change_service_only_then_time` — fail on **all three source versions** at their `awaiting_reschedule_confirmation` assertions; actual result is `preferred_time_unavailable`. `_book_oil` selects a later slot from the original service's availability and reuses it for the longer brake service. That start is not guaranteed to fit/alignment-match the new duration. These are the same clock/availability-fixture class as item 6; none is a new Russian-message assertion failure. Together with items 1–5 and 7–11 they account for the 13 failures in the matched full audit runs. Item 6's clock-dependent pass explains why the original 11-failure list differs.

## All eight lint warnings

Each warning appears under the same rule in both Git HEAD and saved pre-localization sources. Line shifts are translation/import changes, not newly introduced warnings.

- `apps/web/src/app/admin/shops/page.tsx:229` — unsupported `aria-selected` on a link (`jsx-a11y/role-supports-aria-props`); baseline line 227.
- `apps/web/src/app/dashboard/appointments/page.tsx:113` — unused `dayKey` (`@typescript-eslint/no-unused-vars`); same baseline line.
- `apps/web/src/app/dashboard/settings/page.tsx:541` — effect missing `session` dependency (`react-hooks/exhaustive-deps`); same baseline line.
- `apps/web/src/app/dashboard/walk-ins/page.tsx:220` — unused exhaustive-deps disable directive; baseline line 218.
- `apps/web/src/app/page.tsx:5` — unused `Link` import; baseline line 3.
- `apps/web/src/components/Sidebar.tsx:135` — unsupported `aria-disabled` on navigation; same baseline line.
- `apps/web/src/components/VinInput.tsx:1840` — effect missing `ocrSuggestions.length`; Git line 1819, saved pre-localization line 1840 (earlier user changes explain the difference).
- `apps/web/src/components/team/TeamPanel.tsx:431` — effect missing `load`; baseline line 429.

No unrelated lint remediation was applied.

## Functional and data boundaries

- **Authentication/authorization:** reviewed security, auth services/routers/dependencies, roles/capabilities and frontend session handling. JWT algorithms/signature checks, password verification, permission branches and capability codes are unchanged by localization; `security.py` changes only the invalid-token message. API tests executed real local ASGI authentication/authorization scenarios, but the seven blocked registrations do not count as exercising their intended flows. No signed-in browser session was executed.
- **Subscriptions/payments:** billing changes are error/display messages; Stripe adapter changes its description. Checkout form keys, plan IDs, cents amounts, subscription-state transitions, webhook checks and currency remain unchanged in the reviewed diff. Automated billing tests ran as part of the suite; no live Stripe checkout, portal interaction or charge was performed.
- **Database:** database configuration engine code, ORM models and migration source files match Git HEAD; no schema migration or bulk data rewrite was added. This is code evidence, not a before/after dump of all database contents. Test runs do mutate test records through their existing fixtures. Newly generated Russian messages/notes/template text may be persisted through existing code; that is not equivalent to saying all stored text is unchanged.
- **API contracts:** generated OpenAPI from both source trees contains the same 268 paths. After excluding documentation title/summary/description metadata, the sole difference is the user-facing `SendOtpResponse.message` default (`Verification code sent` → `Код подтверждения отправлен`). URLs, methods, field keys/types, required fields, enums and non-copy defaults otherwise match. Error/message text intentionally changes; clients depending on English prose cannot be promised byte-identical payloads. Existing backend dictionary contract keys/decorators were compared with saved sources; report-label dictionaries were added, not substituted for API keys.
- **AI/chatbot:** a blanket claim of “no processing changes” would be inaccurate. Prompts, name/purpose/closing-question recognition, Russian affirmation alternatives, repair-extraction output language and spoken date labels were changed. Tool identifiers, structured JSON keys, numeric fields and decision/action codes were preserved in the inspected changes. The full suite primarily uses English input and fake/in-memory providers; it does not prove Russian language understanding or live-model behavior.
- **Jobs/integrations/workflows:** provider request structures, credentials, retry parameters, trigger/event/action types and schedules are unchanged in the reviewed localization diff. TwiML intentionally changes speech recognition language to `ru-RU` and maps default `Polly.Joanna` to `Polly.Tatyana` at rendering; custom voice names are left intact. XML tests pass, but no real call was placed. Translated workflow names exposed the seed identity issue fixed below. The normal runtime uses `_seed_if_empty`; no current application caller of `seed_default_workflows` was found. Thus this is a reproduced latent explicit-reseed regression, not evidence that normal startup duplicated production workflows.
- **Identifiers/statuses:** existing enum values, tool/capability/event keys, tenant IDs, workflow fixed UUIDs and form/API status values remain unchanged. Display labels use `ruLabel`/`status_label` and preserve unknown values. Workflow names historically also served as identities, so they were an exception requiring the compatibility fix; they must not be dismissed as harmless copy.
- **Locale formatting:** inspected changes to `toLocale*`, `Intl.NumberFormat`, Python reply/report dates and calendar labels are display-boundary changes. ISO serialization, calendar `en-US` format-to-parts construction, parsing, timezone rules, monetary arithmetic, USD denomination and unit values are preserved. The display probe validates representative values, not every date/currency path or every DST boundary.

## Genuine regression fixed during verification

`seed_default_workflows` checks global template names for idempotence. Eleven names changed during localization. An in-memory store populated with the original 12 template names caused 11 seed writes: five random-ID templates were duplicated and six fixed-ID automotive templates were overwritten. The normal runtime's separate `_seed_if_empty` path is not affected by this reproduction.

The smallest compatibility fix recognizes the eleven original English names alongside their Russian names before deciding to seed. It does not rename/delete stored templates, change trigger/action logic, alter fixed IDs, modify the schema, or repair any of the original failing tests. The regression test checks that IDs, objects, descriptions, timestamps and total count survive repeated reseeding. Existing duplicates, if any, are not deleted automatically; none was asserted to exist in a deployed environment.

## Russian coverage findings and unresolved issues

Static JSX/attribute extraction found that direct public/dashboard/settings/form labels are largely Russian; remaining direct Latin-only strings are mostly brands, acronyms, sample data and technical field names. This is not proof that every dynamic value is translated. The following are confirmed gaps:

- **Application-controlled errors still in English.** Examples: `application/crm_service.py` (`VIN must be 17 characters and exclude I, O, and Q`, duplicate phone/email/VIN, `VIN cannot be empty`); `shop_setup/service.py` (`A service with this name already exists`, dynamic `... is required`); `application/walkin_service.py` (`Walk-in already has a customer`, `Walk-in visit is closed/cancelled`); and selected auth/admin/password-reset validation messages. Routers pass domain exception strings into `detail`; frontend error parsers display them directly. These are not all external-provider diagnostics. Source scanning saved 71 backend candidates, including internal-only diagnostics; 71 is a candidate count, not a claimed count of user-visible defects.
- **Schema-generated validation:** frontend parsers join Pydantic `detail[].msg` without localization, so application-generated 422 messages can still be English. Browser-native required/date-input validation depends on browser language; it was not claimed to be controlled by app copy.
- **Dynamic dashboard/report/template text:** admin system-health `levelLabel` still displays `healthy/degraded/outage`; report bodies interpolate benchmark status and KPI codes in English; some seeded workflow/action names remain English (for example `Walk-in created`, `CRM payment note`). Persisted older application-owned templates/notifications are also not translated. Static labels alone therefore cannot establish complete dashboard, report, notification or email coverage.
- **Russian conversational input:** pure heuristic probes with the Russian name question returned `Alex` for `Alex`, but no extracted name for `Иван` or `Меня зовут Иван` because name patterns remain ASCII. At fixed 2026-10-20 09:00 LA, `tomorrow at 10:00` resolves to October 21 with an explicit day; `завтра в 10:00` loses “tomorrow” and becomes a provisional October 20 clock with `day_explicit=False`; `в пятницу утром` yields no datetime. These parser limitations predate localization but now conflict with Russian prompts/recognition. They are a release acceptance gap; a parser rewrite was deliberately not folded into this verification task.
- **Visual coverage limits:** no authenticated dashboard/settings/team/billing/report/table/mobile-menu screens were opened with a real signed-in browser session. Long customer/catalog names, all permission combinations, every breakpoint, mail-client rendering and nondefault voice compatibility remain unverified. Public/mobile checks cover only the views explicitly listed above. The duplicate 404 punctuation remains minor unresolved copy polish.
- **Live integrations:** no live AI generation/TTS, telephone call, SMS/email delivery, DMS/accounting integration or Stripe payment was executed. Missing OpenAI TTS credentials block that test. Passing template/XML/fake-adapter tests is not live integration verification.

Names entered by users, imported/catalog records, brands, technical IDs and customer-authored/custom template content should retain their original values. That exception does not excuse the application-owned English error/status copy above. No broad translation rewrite, credential change, fixture cleanup expansion or unrelated logic/lint fix was made.

## Files modified during this verification

- `apps/api/app/workflows/seeds.py` — original-name compatibility check for explicit reseeding.
- `apps/api/tests/workflows/test_seed_localization_upgrade.py` — new isolated in-memory upgrade regression test.
- `docs/localization-ru-RU.md` — this audit, replacing the earlier incomplete verification claims and preserving the original localization inventory below.

Build/type-check commands also regenerated ignored build/cache artifacts, including `apps/web/tsconfig.tsbuildinfo`; these are not source changes. Evidence and baseline copies are outside the repository. No deployment, commit, schema/data migration or production integration action was performed.

Deployment assessment: **not ready for a claim of complete ru-RU verification**. Compilation and baseline comparisons support preservation of the inspected business rules after the narrow seed fix. Remaining English application copy, Russian-input failures, unresolved baseline test/environment issues, missing private/mobile execution and untested live integrations prevent full acceptance. Use an isolated disposable database and valid test-provider credentials for the remaining acceptance run; do not treat the shared-database failures as permission to weaken production logic.

## Original implementation file inventory

The implementation-stage inventory listed 321 application, test and verification files (plus this report). The new audit regression test is listed separately above:

- `apps/api/app/admin/api.py`
- `apps/api/app/admin/deps.py`
- `apps/api/app/admin/event_bridge.py`
- `apps/api/app/admin/saas_notify.py`
- `apps/api/app/admin/service.py`
- `apps/api/app/agents/base/agent.py`
- `apps/api/app/agents/base/retry.py`
- `apps/api/app/agents/bus/in_memory.py`
- `apps/api/app/agents/communication/service.py`
- `apps/api/app/agents/counselor/persona.py`
- `apps/api/app/agents/crm/service.py`
- `apps/api/app/agents/customer/service.py`
- `apps/api/app/agents/intent/service.py`
- `apps/api/app/agents/marketing/service.py`
- `apps/api/app/agents/mcp/registry.py`
- `apps/api/app/agents/mcp/tools.py`
- `apps/api/app/agents/orchestrator.py`
- `apps/api/app/agents/revenue/service.py`
- `apps/api/app/agents/scheduling/service.py`
- `apps/api/app/agents/supervisor/service.py`
- `apps/api/app/agents/vehicle/service.py`
- `apps/api/app/analytics/engine.py`
- `apps/api/app/analytics/forecast.py`
- `apps/api/app/analytics/reports.py`
- `apps/api/app/analytics/service.py`
- `apps/api/app/api/deps.py`
- `apps/api/app/api/routers/agents.py`
- `apps/api/app/api/routers/analytics.py`
- `apps/api/app/api/routers/appointments.py`
- `apps/api/app/api/routers/auth.py`
- `apps/api/app/api/routers/enterprise.py`
- `apps/api/app/api/routers/imports.py`
- `apps/api/app/api/routers/marketing.py`
- `apps/api/app/api/routers/mcp_hub.py`
- `apps/api/app/api/routers/memory.py`
- `apps/api/app/api/routers/sms_inbox.py`
- `apps/api/app/api/routers/tenant.py`
- `apps/api/app/api/routers/twilio_voice_webhooks.py`
- `apps/api/app/api/routers/twilio_webhooks.py`
- `apps/api/app/api/routers/vehicles.py`
- `apps/api/app/api/routers/voice_calls.py`
- `apps/api/app/api/routers/voice_notes.py`
- `apps/api/app/api/routers/workflows.py`
- `apps/api/app/api/schemas.py`
- `apps/api/app/application/crm_service.py`
- `apps/api/app/application/services.py`
- `apps/api/app/application/voice_note_service.py`
- `apps/api/app/application/walkin_service.py`
- `apps/api/app/auth/otp.py`
- `apps/api/app/core/permissions/capabilities.py`
- `apps/api/app/core/permissions/permission_service.py`
- `apps/api/app/dashboard/plugin.py`
- `apps/api/app/dashboard/widgets.py`
- `apps/api/app/domain/enums.py`
- `apps/api/app/enterprise/dashboard.py`
- `apps/api/app/enterprise/gateway.py`
- `apps/api/app/enterprise/roles.py`
- `apps/api/app/enterprise/service.py`
- `apps/api/app/enterprise/sso.py`
- `apps/api/app/executive/aggregator.py`
- `apps/api/app/import_engine/connectors/api_common.py`
- `apps/api/app/import_engine/connectors/csv_connector.py`
- `apps/api/app/import_engine/connectors/excel_connector.py`
- `apps/api/app/import_engine/connectors/manual_connector.py`
- `apps/api/app/import_engine/connectors/ocr_connector.py`
- `apps/api/app/import_engine/connectors/pdf_connector.py`
- `apps/api/app/import_engine/normalize.py`
- `apps/api/app/import_engine/service.py`
- `apps/api/app/import_engine/sql_store.py`
- `apps/api/app/import_engine/store.py`
- `apps/api/app/import_engine/validation.py`
- `apps/api/app/import_engine/vin.py`
- `apps/api/app/infrastructure/agent_directories.py`
- `apps/api/app/infrastructure/ai/heuristic.py`
- `apps/api/app/infrastructure/ai/openai_provider.py`
- `apps/api/app/infrastructure/ai/provider.py`
- `apps/api/app/infrastructure/config.py`
- `apps/api/app/infrastructure/repositories.py`
- `apps/api/app/infrastructure/security.py`
- `apps/api/app/integrations/accounting/quickbooks.py`
- `apps/api/app/integrations/api.py`
- `apps/api/app/integrations/communication/email.py`
- `apps/api/app/integrations/core/adapter.py`
- `apps/api/app/integrations/core/registry.py`
- `apps/api/app/integrations/dms/autoleap.py`
- `apps/api/app/integrations/dms/mitchell.py`
- `apps/api/app/integrations/dms/shopmonkey.py`
- `apps/api/app/integrations/dms/tekmetric.py`
- `apps/api/app/integrations/payment/stripe.py`
- `apps/api/app/integrations/plugin.py`
- `apps/api/app/integrations/security.py`
- `apps/api/app/integrations/service.py`
- `apps/api/app/learning/collector.py`
- `apps/api/app/learning/engine.py`
- `apps/api/app/learning/feedback/staff.py`
- `apps/api/app/learning/optimizer.py`
- `apps/api/app/localization.py`
- `apps/api/app/marketing/ai_chooser.py`
- `apps/api/app/marketing/audience.py`
- `apps/api/app/marketing/channels.py`
- `apps/api/app/marketing/scheduler.py`
- `apps/api/app/marketing/service.py`
- `apps/api/app/marketing/templates.py`
- `apps/api/app/mcp_hub/adapters/__init__.py`
- `apps/api/app/mcp_hub/adapters/autoleap.py`
- `apps/api/app/mcp_hub/adapters/base.py`
- `apps/api/app/mcp_hub/adapters/email.py`
- `apps/api/app/mcp_hub/adapters/facebook.py`
- `apps/api/app/mcp_hub/adapters/future.py`
- `apps/api/app/mcp_hub/adapters/google_business.py`
- `apps/api/app/mcp_hub/adapters/google_calendar.py`
- `apps/api/app/mcp_hub/adapters/mitchell.py`
- `apps/api/app/mcp_hub/adapters/shopmonkey.py`
- `apps/api/app/mcp_hub/adapters/stripe.py`
- `apps/api/app/mcp_hub/adapters/tekmetric.py`
- `apps/api/app/mcp_hub/adapters/twilio.py`
- `apps/api/app/mcp_hub/connection_manager.py`
- `apps/api/app/mcp_hub/permissions.py`
- `apps/api/app/mcp_hub/service.py`
- `apps/api/app/mcp_hub/versioning.py`
- `apps/api/app/memory/auto.py`
- `apps/api/app/memory/core/store.py`
- `apps/api/app/memory/customer/preferences.py`
- `apps/api/app/memory/retriever.py`
- `apps/api/app/memory/service.py`
- `apps/api/app/memory/shop/preferences.py`
- `apps/api/app/memory/shop/profile.py`
- `apps/api/app/memory/vehicle/health.py`
- `apps/api/app/plugins/advisor/advisor.py`
- `apps/api/app/plugins/advisor/communication/service.py`
- `apps/api/app/plugins/advisor/customer/service.py`
- `apps/api/app/plugins/advisor/estimate/service.py`
- `apps/api/app/plugins/advisor/followup/service.py`
- `apps/api/app/plugins/advisor/repair/service.py`
- `apps/api/app/plugins/advisor/vehicle/service.py`
- `apps/api/app/plugins/conversation/channels/email.py`
- `apps/api/app/plugins/conversation/intelligence/service.py`
- `apps/api/app/plugins/conversation/plugin.py`
- `apps/api/app/plugins/conversation/session/service.py`
- `apps/api/app/plugins/conversation/store.py`
- `apps/api/app/plugins/crm/customer/service.py`
- `apps/api/app/plugins/crm/plugin.py`
- `apps/api/app/plugins/crm/repair/service.py`
- `apps/api/app/plugins/framework/capability.py`
- `apps/api/app/plugins/framework/factory.py`
- `apps/api/app/plugins/framework/lifecycle.py`
- `apps/api/app/plugins/framework/registry.py`
- `apps/api/app/plugins/inspection/approval/service.py`
- `apps/api/app/plugins/inspection/diagnosis/service.py`
- `apps/api/app/plugins/inspection/explanation/service.py`
- `apps/api/app/plugins/inspection/plugin.py`
- `apps/api/app/plugins/inspection/recommendation/service.py`
- `apps/api/app/plugins/inspection/templates.py`
- `apps/api/app/plugins/inventory/ordering/service.py`
- `apps/api/app/plugins/inventory/plugin.py`
- `apps/api/app/plugins/inventory/prediction/service.py`
- `apps/api/app/plugins/inventory/stock/service.py`
- `apps/api/app/plugins/learning/plugin.py`
- `apps/api/app/plugins/memory/plugin.py`
- `apps/api/app/plugins/revenue/plugin.py`
- `apps/api/app/plugins/revenue/prediction/service.py`
- `apps/api/app/plugins/scheduling/availability/service.py`
- `apps/api/app/plugins/scheduling/plugin.py`
- `apps/api/app/plugins/voice/plugin.py`
- `apps/api/app/plugins/voice/providers/base.py`
- `apps/api/app/plugins/voice/session/service.py`
- `apps/api/app/revenue/decisions/campaign.py`
- `apps/api/app/revenue/decisions/retention.py`
- `apps/api/app/revenue/engine.py`
- `apps/api/app/revenue/recommendations/timing.py`
- `apps/api/app/revenue_intel/agent_adapter.py`
- `apps/api/app/revenue_intel/engine.py`
- `apps/api/app/revenue_intel/messaging.py`
- `apps/api/app/revenue_intel/scoring.py`
- `apps/api/app/revenue_intel/service.py`
- `apps/api/app/revenue_intel/store.py`
- `apps/api/app/saas/access_review.py`
- `apps/api/app/saas/billing.py`
- `apps/api/app/saas/compliance.py`
- `apps/api/app/saas/compliance_api.py`
- `apps/api/app/saas/password_reset.py`
- `apps/api/app/saas/quotas.py`
- `apps/api/app/saas/rate_limit.py`
- `apps/api/app/scheduling/agent_adapter.py`
- `apps/api/app/scheduling/catalog.py`
- `apps/api/app/scheduling/engines/conflict.py`
- `apps/api/app/scheduling/engines/optimization.py`
- `apps/api/app/scheduling/service.py`
- `apps/api/app/shop_setup/schemas.py`
- `apps/api/app/shop_setup/service.py`
- `apps/api/app/simulation/cli.py`
- `apps/api/app/simulation/engine.py`
- `apps/api/app/simulation/scenarios/inspection_completed.py`
- `apps/api/app/simulation/scenarios/new_customer_phone.py`
- `apps/api/app/sms/reply.py`
- `apps/api/app/sms/service.py`
- `apps/api/app/sms/sql_store.py`
- `apps/api/app/telephony/numbers.py`
- `apps/api/app/voice/reply.py`
- `apps/api/app/voice/service.py`
- `apps/api/app/voice/sql_store.py`
- `apps/api/app/voice/twilio/provider.py`
- `apps/api/app/workflows/actions.py`
- `apps/api/app/workflows/automotive/declined_estimate_recovery.py`
- `apps/api/app/workflows/automotive/inspection_completed.py`
- `apps/api/app/workflows/automotive/maintenance_reminder.py`
- `apps/api/app/workflows/automotive/new_customer_phone_request.py`
- `apps/api/app/workflows/automotive/repair_completed.py`
- `apps/api/app/workflows/automotive/walk_in_customer.py`
- `apps/api/app/workflows/decision_executor.py`
- `apps/api/app/workflows/runner.py`
- `apps/api/app/workflows/seeds.py`
- `apps/api/app/workflows/service.py`
- `apps/api/tests/admin/test_admin_account_separation.py`
- `apps/api/tests/admin/test_admin_api.py`
- `apps/api/tests/admin/test_admin_me.py`
- `apps/api/tests/agents/test_counselor_persona.py`
- `apps/api/tests/agents/test_crm_agent.py`
- `apps/api/tests/agents/test_revenue_agent.py`
- `apps/api/tests/agents/test_supervisor_agent.py`
- `apps/api/tests/executive/test_executive_dashboard.py`
- `apps/api/tests/marketing/test_marketing.py`
- `apps/api/tests/saas/test_billing_checkout.py`
- `apps/api/tests/saas/test_seat_quota.py`
- `apps/api/tests/scheduling/test_appointment_intelligence.py`
- `apps/api/tests/scheduling/test_resource_sync.py`
- `apps/api/tests/sms/test_sms_ai.py`
- `apps/api/tests/test_phase1_auth_isolation.py`
- `apps/api/tests/voice/test_reschedule_both.py`
- `apps/api/tests/voice/test_voice_ai.py`
- `apps/api/tests/workflows/test_automotive_workflows.py`
- `apps/api/tests/workflows/test_workflow_engine.py`
- `apps/web/src/app/admin/ai-usage/page.tsx`
- `apps/web/src/app/admin/billing/page.tsx`
- `apps/web/src/app/admin/login/page.tsx`
- `apps/web/src/app/admin/notifications/page.tsx`
- `apps/web/src/app/admin/page.tsx`
- `apps/web/src/app/admin/settings/page.tsx`
- `apps/web/src/app/admin/shops/[shopId]/page.tsx`
- `apps/web/src/app/admin/shops/page.tsx`
- `apps/web/src/app/admin/system-health/page.tsx`
- `apps/web/src/app/admin/tokens/page.tsx`
- `apps/web/src/app/admin/twilio-numbers/page.tsx`
- `apps/web/src/app/admin/users/page.tsx`
- `apps/web/src/app/dashboard/agents/page.tsx`
- `apps/web/src/app/dashboard/analytics/page.tsx`
- `apps/web/src/app/dashboard/appointments/page.tsx`
- `apps/web/src/app/dashboard/billing/page.tsx`
- `apps/web/src/app/dashboard/calls/page.tsx`
- `apps/web/src/app/dashboard/customer/[id]/CustomerDetailContent.tsx`
- `apps/web/src/app/dashboard/customer/[id]/page.tsx`
- `apps/web/src/app/dashboard/customer/page.tsx`
- `apps/web/src/app/dashboard/enterprise/page.tsx`
- `apps/web/src/app/dashboard/external/page.tsx`
- `apps/web/src/app/dashboard/import/page.tsx`
- `apps/web/src/app/dashboard/integrations/page.tsx`
- `apps/web/src/app/dashboard/intelligence/page.tsx`
- `apps/web/src/app/dashboard/marketing/page.tsx`
- `apps/web/src/app/dashboard/ops/page.tsx`
- `apps/web/src/app/dashboard/page.tsx`
- `apps/web/src/app/dashboard/revenue/page.tsx`
- `apps/web/src/app/dashboard/settings/page.tsx`
- `apps/web/src/app/dashboard/setup/page.tsx`
- `apps/web/src/app/dashboard/vehicles/[id]/page.tsx`
- `apps/web/src/app/dashboard/walk-ins/[id]/page.tsx`
- `apps/web/src/app/dashboard/walk-ins/page.tsx`
- `apps/web/src/app/dashboard/workflows/page.tsx`
- `apps/web/src/app/enterprise/sso/callback/page.tsx`
- `apps/web/src/app/forgot-password/page.tsx`
- `apps/web/src/app/layout.tsx`
- `apps/web/src/app/login/page.tsx`
- `apps/web/src/app/not-found.tsx`
- `apps/web/src/app/page.tsx`
- `apps/web/src/app/pricing/page.tsx`
- `apps/web/src/app/privacy/page.tsx`
- `apps/web/src/app/register/page.tsx`
- `apps/web/src/app/reset-password/page.tsx`
- `apps/web/src/app/status/page.tsx`
- `apps/web/src/app/terms/page.tsx`
- `apps/web/src/components/ApiHealthCard.tsx`
- `apps/web/src/components/DashboardShell.tsx`
- `apps/web/src/components/LoginForm.tsx`
- `apps/web/src/components/MobileBottomNav.tsx`
- `apps/web/src/components/PasswordField.tsx`
- `apps/web/src/components/RegisterForm.tsx`
- `apps/web/src/components/SetupGate.tsx`
- `apps/web/src/components/Sidebar.tsx`
- `apps/web/src/components/VinInput.tsx`
- `apps/web/src/components/admin/AdminShell.tsx`
- `apps/web/src/components/admin/AdminSidebar.tsx`
- `apps/web/src/components/conversations/SmsInboxPanel.tsx`
- `apps/web/src/components/conversations/VoiceCallsPanel.tsx`
- `apps/web/src/components/conversations/VoiceNotesPanel.tsx`
- `apps/web/src/components/services/ServicesPanel.tsx`
- `apps/web/src/components/team/TeamPanel.tsx`
- `apps/web/src/lib/admin.ts`
- `apps/web/src/lib/agents.ts`
- `apps/web/src/lib/analytics.ts`
- `apps/web/src/lib/api.ts`
- `apps/web/src/lib/appointments.ts`
- `apps/web/src/lib/calls.ts`
- `apps/web/src/lib/capabilities.ts`
- `apps/web/src/lib/crm.ts`
- `apps/web/src/lib/enterprise.ts`
- `apps/web/src/lib/executive.ts`
- `apps/web/src/lib/imports.ts`
- `apps/web/src/lib/integrations.ts`
- `apps/web/src/lib/marketing.ts`
- `apps/web/src/lib/mcp-hub.ts`
- `apps/web/src/lib/memory.ts`
- `apps/web/src/lib/ops-dashboard.ts`
- `apps/web/src/lib/revenue.ts`
- `apps/web/src/lib/ru.ts`
- `apps/web/src/lib/shopSetup.ts`
- `apps/web/src/lib/sms.ts`
- `apps/web/src/lib/system-health.ts`
- `apps/web/src/lib/tenant.ts`
- `apps/web/src/lib/voiceNotes.ts`
- `apps/web/src/lib/walkin.ts`
- `apps/web/src/lib/workflows.ts`
- `scripts/verify_ru_localization.py`
