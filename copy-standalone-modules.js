const fs = require('fs');
const path = require('path');

const src = path.join(__dirname, 'node_modules');
const dest = path.join(__dirname, 'apps', 'web', '.next', 'standalone', 'node_modules');

if (fs.existsSync(dest)) {
  fs.rmSync(dest, { recursive: true, force: true });
}

fs.cpSync(src, dest, { recursive: true, dereference: true });
console.log('Standalone node_modules copied successfully.');