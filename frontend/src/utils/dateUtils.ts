/**
 * Utility functions for date formatting with proper timezone handling
 */

/**
 * Ensures a date string from the backend is properly interpreted as UTC
 * Backend sends naive datetime strings that should be treated as UTC
 * @param dateString - Date string from backend API
 * @returns Properly parsed Date object in UTC
 */
function parseUTCDate(dateString: string): Date {
  // If the string already has timezone info, use it as-is
  if (dateString.includes('Z') || dateString.includes('+') || dateString.includes('T') && dateString.lastIndexOf('-') > dateString.indexOf('T')) {
    return new Date(dateString);
  }
  
  // For naive datetime strings from backend, append 'Z' to indicate UTC
  const utcString = dateString.endsWith('Z') ? dateString : `${dateString}Z`;
  return new Date(utcString);
}

/**
 * Formats a date to show both date and time in user's local timezone
 * @param dateString - ISO date string from backend (treated as UTC)
 * @returns Formatted string like "Dec 26, 2025 at 14:30" in local time
 */
export function formatDateWithTime(dateString: string): string {
  const date = parseUTCDate(dateString);
  
  // Check if the date is valid
  if (isNaN(date.getTime())) {
    return 'Invalid date';
  }
  
  const dateOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
  };
  
  const timeOptions: Intl.DateTimeFormatOptions = {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false, // Use 24-hour format
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
  };
  
  const formattedDate = date.toLocaleDateString('en-US', dateOptions);
  const formattedTime = date.toLocaleTimeString('en-US', timeOptions);
  
  return `${formattedDate} at ${formattedTime}`;
}

/**
 * Formats a date to show relative time (e.g., "2 hours ago", "5 minutes ago")
 * @param dateString - ISO date string from backend (treated as UTC)
 * @returns Relative time string
 */
export function formatRelativeTime(dateString: string): string {
  const date = parseUTCDate(dateString);
  const now = new Date();
  
  // Check if the date is valid
  if (isNaN(date.getTime())) {
    return 'Invalid date';
  }
  
  const diffInMs = now.getTime() - date.getTime();
  const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
  const diffInHours = Math.floor(diffInMinutes / 60);
  const diffInDays = Math.floor(diffInHours / 24);
  
  if (diffInDays > 0) {
    return diffInDays === 1 ? '1 day ago' : `${diffInDays} days ago`;
  } else if (diffInHours > 0) {
    return diffInHours === 1 ? '1 hour ago' : `${diffInHours} hours ago`;
  } else if (diffInMinutes > 0) {
    return diffInMinutes === 1 ? '1 minute ago' : `${diffInMinutes} minutes ago`;
  } else {
    return 'Just now';
  }
}

/**
 * Formats a date to show smart relative or absolute time based on recency
 * Shows relative time for recent items (< 24 hours) and absolute time for older items
 * @param dateString - ISO date string from backend (treated as UTC)
 * @returns Smart formatted string
 */
export function formatSmartTime(dateString: string): string {
  const date = parseUTCDate(dateString);
  const now = new Date();
  
  // Check if the date is valid
  if (isNaN(date.getTime())) {
    return 'Invalid date';
  }
  
  const diffInMs = now.getTime() - date.getTime();
  const diffInHours = diffInMs / (1000 * 60 * 60);
  
  // If less than 24 hours ago, show relative time
  if (diffInHours < 24) {
    return formatRelativeTime(dateString);
  }
  
  // For older items, show date and time
  return formatDateWithTime(dateString);
}

/**
 * Formats a date to show just the time portion (hours and minutes) in local timezone
 * @param dateString - ISO date string from backend (treated as UTC)
 * @returns Time string like "14:30" in local time
 */
export function formatTimeOnly(dateString: string): string {
  const date = parseUTCDate(dateString);
  
  // Check if the date is valid
  if (isNaN(date.getTime())) {
    return 'Invalid time';
  }
  
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
  });
}

/**
 * Gets the current timezone name for debugging/display purposes
 * @returns Timezone string like "Europe/Prague"
 */
export function getCurrentTimeZone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}

/**
 * Debug function to compare UTC vs local interpretation of a date string
 * @param dateString - Date string from backend
 * @returns Object with both interpretations for debugging
 */
export function debugDateInterpretation(dateString: string) {
  const naiveDate = new Date(dateString); // How JS interprets it without timezone info
  const utcDate = parseUTCDate(dateString); // How it should be interpreted (as UTC)
  
  return {
    original: dateString,
    naiveInterpretation: {
      timestamp: naiveDate.getTime(),
      formatted: naiveDate.toISOString(),
      localString: naiveDate.toLocaleString()
    },
    correctInterpretation: {
      timestamp: utcDate.getTime(),
      formatted: utcDate.toISOString(),
      localString: utcDate.toLocaleString()
    },
    timezoneOffset: naiveDate.getTimezoneOffset(),
    currentTimeZone: getCurrentTimeZone()
  };
}
