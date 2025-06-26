// Test the timezone fixes
import { formatSmartTime, formatDateWithTime, formatRelativeTime, debugDateInterpretation, getCurrentTimeZone } from './src/utils/dateUtils';

console.log('=== Timezone Fix Test ===');
console.log('Current timezone:', getCurrentTimeZone());
console.log('');

// Test with naive datetime string (what backend currently sends)
const naiveDateString = '2025-06-26T12:30:45.123456';
console.log('Testing naive datetime string:', naiveDateString);

const debugInfo = debugDateInterpretation(naiveDateString);
console.log('Debug info:', JSON.stringify(debugInfo, null, 2));
console.log('');

console.log('Smart time format:', formatSmartTime(naiveDateString));
console.log('Full date format:', formatDateWithTime(naiveDateString));
console.log('Relative time format:', formatRelativeTime(naiveDateString));
console.log('');

// Test with proper UTC string (what backend should send)
const utcDateString = '2025-06-26T12:30:45.123456Z';
console.log('Testing proper UTC string:', utcDateString);
console.log('Smart time format:', formatSmartTime(utcDateString));
console.log('Full date format:', formatDateWithTime(utcDateString));
console.log('');

// Test with very recent time
const recentTime = new Date(Date.now() - 5 * 60 * 1000).toISOString(); // 5 minutes ago
console.log('Testing recent time (5 min ago):', recentTime);
console.log('Relative format:', formatRelativeTime(recentTime));
