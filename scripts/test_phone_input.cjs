const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('../apps/web/node_modules/typescript');
const scope = { exports: {} };
vm.runInNewContext(ts.transpileModule(fs.readFileSync('apps/web/src/lib/phone.ts', 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.CommonJS },
}).outputText, scope);
const { formatPhoneInput: format, phoneDigits, PHONE_PLACEHOLDER } = scope.exports;
test('Russian default placeholder and national input', () => {
  assert.equal(PHONE_PLACEHOLDER, '8 912 345 67 89');
  assert.equal(format('9123456789'), '8 912 345 67 89');
  assert.equal(format('89123456789'), '8 912 345 67 89');
  assert.equal(format(format('89123456789')), '8 912 345 67 89');
});
test('empty, invalid and partial input', () => {
  assert.equal(format(''), '');
  assert.equal(format('abc'), '');
  assert.equal(format('8'), '8');
  assert.equal(format('89'), '8 9');
  assert.equal(format('891234567890'), '891234567890');
});
test('existing international and US numbers retain all original digits', () => {
  for (const input of ['+15550100001', '15550100001', '+79123456789', '+442079460958']) {
    assert.equal(phoneDigits(format(input)), phoneDigits(input));
    assert.equal(format(format(input)), format(input));
  }
  assert.equal(format('+1'), '+1');
  assert.equal(format('+7'), '+7');
});
