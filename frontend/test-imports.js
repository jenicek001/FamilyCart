// Quick test to verify import paths work at runtime
const path = require('path');
const fs = require('fs');

// Test if the files exist
const loginDialogPath = path.resolve(__dirname, 'src/components/auth/LoginDialog.tsx');
const registerDialogPath = path.resolve(__dirname, 'src/components/auth/RegisterDialog.tsx');
const authContextPath = path.resolve(__dirname, 'src/contexts/AuthContext.tsx');

console.log('File existence check:');
console.log('LoginDialog.tsx exists:', fs.existsSync(loginDialogPath));
console.log('RegisterDialog.tsx exists:', fs.existsSync(registerDialogPath));
console.log('AuthContext.tsx exists:', fs.existsSync(authContextPath));

// Check if they export the expected components
console.log('\nContent checks:');
const loginContent = fs.readFileSync(loginDialogPath, 'utf8');
const registerContent = fs.readFileSync(registerDialogPath, 'utf8');

console.log('LoginDialog has export:', loginContent.includes('export function LoginDialog'));
console.log('RegisterDialog has export:', registerContent.includes('export function RegisterDialog'));
