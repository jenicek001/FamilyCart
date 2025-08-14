// Test script for date formatting
import { formatDateWithTime, formatRelativeTime, formatTimeOnly } from './src/utils/dateUtils';

// Test with current time
const now = new Date().toISOString();
console.log('Current time formatted:', formatDateWithTime(now));

// Test with a specific time
const testTime = '2025-06-26T14:30:45.123Z';
console.log('Test time formatted:', formatDateWithTime(testTime));

// Test relative time
const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString();
console.log('One hour ago:', formatRelativeTime(oneHourAgo));

// Test time only
console.log('Time only:', formatTimeOnly(testTime));
