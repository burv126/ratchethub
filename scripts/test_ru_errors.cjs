/* Run with node --test scripts/test_ru_errors.cjs; uses existing TypeScript only. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('../apps/web/node_modules/typescript');

function load(file) {
  const code = ts.transpileModule(fs.readFileSync(file, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS },
  }).outputText;
  const scope = { exports: {} };
  vm.runInNewContext(code, scope);
  return scope.exports;
}
const { ruError, readApiError, ruNotification, ruNotificationTitle, ruDiagnostic, ruWorkflowLog, ruIntegrationLog } = load('apps/web/src/lib/ru-errors.ts');
const { ruLabel, ruClock } = load('apps/web/src/lib/ru.ts');

for (const message of [
  'VIN must be 17 characters and exclude I, O, and Q', 'VIN already exists for this shop',
  'VIN cannot be empty', 'A customer with this phone number already exists',
  'A customer with this email already exists', 'A service with this name already exists',
  'Walk-in already has a customer', 'Walk-in visit is closed', 'Walk-in visit is cancelled',
  'MFA is not enabled', 'Speech-to-text returned an empty transcript', 'Invalid credentials',
  'Invalid token', 'Email already registered', 'Shop name already taken', 'Shop not found',
  'Not authenticated', 'Not Found', 'Forbidden', 'Unauthorized', 'Too Many Requests',
  'Failed to fetch', 'NetworkError when attempting to fetch resource.',
  'auth_method must be phone or email', 'email or phone is required',
  'service_id is required to book an appointment', 'plan_id is required',
  'username is required', 'preferred_time_unavailable', 'appointment_not_found', 'permission_denied',
]) test(`Russian display and idempotence: ${message}`, () => {
  const display = ruError(message);
  assert.match(display, /[А-Яа-яЁё]/);
  assert.notEqual(display, message);
  assert.equal(ruError(display), display);
});

for (const value of [null, undefined, 23, true, {}, [], 'unrecognized failure',
  'Traceback: password=supersecret', 'Ошибка SQLAlchemy SELECT secret FROM users',
  'Ошибка: https://provider.example/?api_key=secret', 'Ошибка: Bearer private-token',
  'Ошибка: C:\\private\\credentials.txt', 'Ошибка: /etc/private/credentials',
  'Ошибка KeyError: private-secret', 'Ошибка: connection refused private-host', { detail: { secret: 'password' } }]) {
  test(`Invalid/unknown diagnostics are safe: ${JSON.stringify(value)}`, () => {
    const display = ruError(value);
    assert.match(display, /[А-Яа-яЁё]/);
    assert.doesNotMatch(display, /secret|private|Traceback|SQLAlchemy|provider|credentials/i);
  });
}

test('Pydantic validation localizes by type, preserves response and omits input/context', async () => {
  const payload = { detail: [
    { type: 'missing', loc: ['body', 'email'], msg: 'Field required', input: { password: 'secret' } },
    { type: 'string_too_short', loc: ['body', 'password'], msg: 'String should have at least 8 characters', ctx: { min_length: 8 } },
    { type: 'decimal_parsing', loc: ['body', 'price'], msg: 'Input should be a valid decimal', input: 'bad' },
  ] };
  const before = JSON.stringify(payload);
  const response = { status: 422, json: async () => payload };
  const display = await readApiError(response);
  assert.match(display, /Электронная почта: заполните/);
  assert.match(display, /Пароль: введённое значение слишком короткое/);
  assert.match(display, /Цена: введите корректное число/);
  assert.doesNotMatch(display, /secret|Field required|String should/);
  assert.equal(JSON.stringify(payload), before);
});

test('HTTP status/code/retry data and Russian/English input payloads remain untouched', async () => {
  const payload = { detail: { code: 'permission_denied', message: 'Forbidden', retry_after: 90 } };
  const before = JSON.stringify(payload);
  assert.equal(await readApiError({ status: 403, json: async () => payload }), 'Недостаточно прав для этого действия.');
  assert.equal(JSON.stringify(payload), before);
  assert.match(await readApiError({ status: 503, json: async () => { throw new Error('bad JSON'); } }), /Повторите/);
  assert.equal(await readApiError({ status: 409, json: async () => ({ detail: 'Данные уже существуют' }) }), 'Данные уже существуют');
});

test('Notification metadata and diagnostic codes are not translated or mutated', () => {
  const note = { title: 'New signup', event_type: 'saas.signup', message: 'shop=x joined_by=Owner', payload: { shop_name: 'Example / Автосервис' } };
  const before = JSON.stringify(note);
  assert.equal(ruNotificationTitle(note), 'Новый автосервис');
  assert.match(ruNotification(note), /Example \/ Автосервис/);
  assert.equal(JSON.stringify(note), before);
  assert.equal(ruNotification({ message: 'Проверка завершена' }), 'Проверка завершена');
  assert.match(ruNotification({ message: 'secret provider failure' }), /Новое уведомление/);
  const raw = { code: 'workflow.failed', status: 'failed', error: 'Traceback: private-secret', token: 'private', nested: [{ error: 'Forbidden' }] };
  const original = JSON.stringify(raw);
  const displayed = ruDiagnostic(raw);
  assert.equal(displayed.code, raw.code);
  assert.equal(displayed.status, raw.status);
  assert.equal(displayed.token, '[скрыто]');
  assert.doesNotMatch(JSON.stringify(displayed), /private|Traceback/);
  assert.equal(JSON.stringify(raw), original);
  assert.equal(ruWorkflowLog('Conditions matched'), 'Условия выполнены');
  assert.match(ruWorkflowLog('Step 2: secret failed'), /Не удалось/);
  assert.equal(ruWorkflowLog('Условия выполнены'), 'Условия выполнены');
});

test('Legacy workflow names and canonical statuses are mapped only for display', () => {
  for (const name of ['Walk-in created', 'CRM payment note', 'Appointment booked cascade', 'Automotive: Repair completed', 'revenue']) {
    assert.match(ruLabel(name), /[А-Яа-яЁё]/);
  }
  assert.equal(ruLabel('Customer-defined workflow'), 'Customer-defined workflow');
  assert.equal(ruLabel('Мой процесс'), 'Мой процесс');
  assert.equal(ruLabel(null), '—');
  assert.equal(ruLabel('booked'), 'Записано');
});

test('404 copy does not duplicate the framework punctuation', () => {
  assert.match(fs.readFileSync('apps/web/src/app/not-found.tsx', 'utf8'), /title="Страница не найдена"/);
});

test('Business hours use a Russian 24-hour display without changing API/form values', () => {
  for (const [raw, display] of [['08:00', '08:00'], ['17:30', '17:30'], ['9:05', '09:05'], ['00:00:00', '00:00']]) {
    const payload = { open_time: raw, closed: false };
    const before = JSON.stringify(payload);
    assert.equal(ruClock(payload.open_time), display);
    assert.equal(JSON.stringify(payload), before);
  }
  for (const invalid of ['', '25:00', '12:99', 'morning', 'утром']) assert.equal(ruClock(invalid), '—');
  for (const file of ['settings', 'setup']) {
    assert.match(fs.readFileSync(`apps/web/src/app/dashboard/${file}/page.tsx`, 'utf8'), /open \? "открыто" : "закрыто"/);
  }
});

test('Long Russian visit-type labels have full-width cards on small screens', () => {
  const source = fs.readFileSync('apps/web/src/app/dashboard/customer/page.tsx', 'utf8');
  assert.match(source, /grid grid-cols-1 gap-2 sm:grid-cols-2/);
  assert.match(source, /label="Известный клиент"/);
  assert.match(source, /label="Неизвестный посетитель"/);
});

test('Integration/background errors are localized without rewriting raw logs', () => {
  for (const log of [{ level: 'error', message: 'Forbidden' },
    { level: 'info', message: 'Connected successfully' },
    { level: 'warning', message: 'Ошибка KeyError: secret' },
    { level: 'info', message: 'Подключение установлено' }]) {
    const before = JSON.stringify(log);
    const display = ruIntegrationLog(log);
    assert.match(display, /[А-Яа-яЁё]/);
    assert.doesNotMatch(display, /Forbidden|Connected successfully|KeyError|secret/);
    assert.equal(JSON.stringify(log), before);
  }
});
