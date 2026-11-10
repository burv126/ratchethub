"""Local Windows setup only; never imports or changes application auth logic."""
from pathlib import Path
import argparse
import json
import secrets

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / '.local'


def prepare():
    LOCAL.mkdir(exist_ok=True)
    path = LOCAL / 'settings.json'
    if not path.exists():
        path.write_text(json.dumps({
            'bootstrap_password': secrets.token_hex(24),
            'database_password': secrets.token_hex(24),
            'jwt_secret': secrets.token_hex(40),
            'account_password': secrets.token_urlsafe(20),
        }, indent=2), encoding='utf8')
    settings = json.loads(path.read_text(encoding='utf8'))
    (LOCAL / 'initdb-password').write_text(settings['bootstrap_password'], encoding='utf8')
    url = f"postgresql+asyncpg://ratchethub_app:{settings['database_password']}@127.0.0.1:55432/ratchethub_dev"
    env = {
        'ENVIRONMENT': 'development', 'DATABASE_URL': url,
        'DATABASE_URL_SYNC': url.replace('+asyncpg', '+psycopg'),
        'JWT_SECRET': settings['jwt_secret'],
        'API_CORS_ORIGINS': 'http://127.0.0.1:3003,http://localhost:3003',
        'NEXT_PUBLIC_API_URL': 'http://127.0.0.1:8003',
        'WEB_APP_URL': 'http://127.0.0.1:3003',
        'BILLING_SUCCESS_URL': 'http://127.0.0.1:3003/dashboard/billing?checkout=success',
        'BILLING_CANCEL_URL': 'http://127.0.0.1:3003/dashboard/billing?checkout=cancel',
        'BILLING_PORTAL_RETURN_URL': 'http://127.0.0.1:3003/dashboard/billing',
        'AI_PROVIDER': 'heuristic', 'OPENAI_ENABLED': 'false', 'OPENAI_API_KEY': '',
        'TWILIO_PROVIDER': 'fake', 'VOICE_PROVIDER': 'fake', 'EMAIL_PROVIDER': 'fake',
        'TWILIO_ACCOUNT_SID': '', 'TWILIO_AUTH_TOKEN': '', 'TWILIO_FROM_NUMBER': '',
        'TWILIO_ALLOW_NUMBER_RELEASE': 'false', 'TWILIO_VALIDATE_SIGNATURE': 'true',
        'STRIPE_SECRET_KEY': '', 'STRIPE_WEBHOOK_SECRET': '',
        'SMTP_USERNAME': '', 'SMTP_PASSWORD': '', 'OIDC_CLIENT_SECRET': '',
        'SENTRY_DSN': '', 'PLATFORM_ADMIN_USERNAMES': '',
        'PLATFORM_ADMIN_BOOTSTRAP_PASSWORD': '',
        'SMS_QUEUE_BACKEND': 'memory', 'VOICE_QUEUE_BACKEND': 'memory',
        'SMS_STORE_BACKEND': 'db', 'VOICE_STORE_BACKEND': 'db',
        'IMPORT_STORE_BACKEND': 'db', 'OTP_STORE_BACKEND': 'db',
        'READY_REQUIRE_REDIS': 'false',
    }
    (LOCAL / 'environment.json').write_text(json.dumps(env, indent=2), encoding='utf8')
    return settings


def database():
    import psycopg
    from psycopg import sql
    settings = prepare()
    with psycopg.connect(host='127.0.0.1', port=55432, dbname='postgres',
                         user='ratchethub_bootstrap', password=settings['bootstrap_password'],
                         autocommit=True, connect_timeout=5) as conn:
        directory = conn.execute("SELECT current_setting('data_directory')").fetchone()[0]
        if Path(directory).resolve() != (LOCAL / 'postgres').resolve():
            raise SystemExit('Refusing a cluster outside this project')
        if not conn.execute('SELECT 1 FROM pg_roles WHERE rolname=%s', ('ratchethub_app',)).fetchone():
            conn.execute(sql.SQL('CREATE ROLE ratchethub_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS PASSWORD {}').format(sql.Literal(settings['database_password'])))
        if not conn.execute('SELECT 1 FROM pg_database WHERE datname=%s', ('ratchethub_dev',)).fetchone():
            conn.execute("CREATE DATABASE ratchethub_dev OWNER ratchethub_app TEMPLATE template0 LOCALE_PROVIDER icu ICU_LOCALE 'und'")
    print('Isolated project database ready on 127.0.0.1:55432')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'database'])
    args = parser.parse_args()
    if args.action == 'prepare':
        prepare()
        print('Local configuration prepared; secret values are not displayed')
    else:
        database()
