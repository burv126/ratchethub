"""Create/verify the local owner through the normal HTTP auth endpoints."""
import json
import httpx
from local_environment import LOCAL, database, prepare


def main():
    # Verify that the dedicated local cluster belongs to this checkout first.
    database()
    settings = prepare()
    account_path = LOCAL / 'account.json'
    if account_path.exists() and json.loads(account_path.read_text(encoding='utf8')).get('local_database') == 'ratchethub_dev':
        print('Local owner already configured; existing sessions preserved.')
        return
    account = {
        'shop_name': 'Локальный автосервис',
        'phone': '+15550100001',
        'email': 'local-owner@example.com',
        'password': settings['account_password'],
        'local_database': 'ratchethub_dev',
    }
    with httpx.Client(base_url='http://127.0.0.1:8003', timeout=30, trust_env=False) as client:
        login = client.post('/v1/auth/login', json={k: account[k] for k in ('shop_name', 'phone', 'password')})
        created = False
        needs_account = not account_path.exists() or json.loads(account_path.read_text(encoding='utf8')).get('local_database') != 'ratchethub_dev'
        if needs_account and login.status_code in (401, 404):
            login = client.post('/v1/auth/register', json={
                'shop_name': account['shop_name'],
                'auth_method': 'phone', 'owner_full_name': 'Локальный владелец',
                'owner_phone': account['phone'], 'owner_email': account['email'],
                'password': account['password'], 'timezone': 'America/Los_Angeles',
            })
            created = True
        if login.status_code not in (200, 201):
            raise SystemExit(f'Local account auth failed (HTTP {login.status_code}); no credentials printed.')
        tokens = login.json()
        protected = client.get('/v1/auth/me', headers={'Authorization': 'Bearer ' + tokens['access_token']})
        if protected.status_code != 200:
            raise SystemExit(f'Local protected identity failed (HTTP {protected.status_code}).')
        refreshed = client.post('/v1/auth/refresh', json={'refresh_token': tokens['refresh_token']})
        if refreshed.status_code != 200:
            raise SystemExit(f'Local refresh failed (HTTP {refreshed.status_code}).')
        logout = client.post('/v1/auth/logout', json={'refresh_token': refreshed.json()['refresh_token']})
        if logout.status_code not in (200, 204):
            raise SystemExit(f'Local logout failed (HTTP {logout.status_code}).')
        unauth = client.get('/v1/auth/me')
        if unauth.status_code != 401:
            raise SystemExit('Unauthenticated identity was not rejected.')
    (LOCAL / 'account.json').write_text(json.dumps(account, ensure_ascii=False, indent=2), encoding='utf8')
    (LOCAL / 'auth-verification.json').write_text(json.dumps({
        'real_local_backend': True, 'database': 'ratchethub_dev@127.0.0.1:55432',
        'account_created': created, 'authenticated_me': protected.status_code,
        'refresh': refreshed.status_code, 'logout': logout.status_code,
        'unauthenticated_me': unauth.status_code,
    }, indent=2), encoding='utf8')
    print('Local owner ready; real protected identity, refresh, logout and anonymous rejection verified.')
    print('Credentials are in ignored .local/account.json; no password or token is printed.')


if __name__ == '__main__':
    main()
