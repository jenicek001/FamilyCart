/**
 * Utility functions for managing localStorage in a Next.js environment
 * with proper handling for server-side rendering
 */

const STORAGE_KEYS = {
  LAST_ACTIVE_LIST_ID: 'familycart_last_active_list_id',
  USER_PREFERENCES: 'familycart_user_preferences',
} as const;

/**
 * Safely check if we're running in a browser environment
 */
const isBrowser = () => typeof window !== 'undefined';

/**
 * Store the last active shopping list ID
 */
export const setLastActiveListId = (listId: number | null): void => {
  if (!isBrowser()) return;
  
  try {
    if (listId === null) {
      localStorage.removeItem(STORAGE_KEYS.LAST_ACTIVE_LIST_ID);
    } else {
      localStorage.setItem(STORAGE_KEYS.LAST_ACTIVE_LIST_ID, listId.toString());
    }
  } catch (error) {
    console.warn('Failed to save last active list ID to localStorage:', error);
  }
};

/**
 * Retrieve the last active shopping list ID
 */
export const getLastActiveListId = (): number | null => {
  if (!isBrowser()) return null;
  
  try {
    const storedId = localStorage.getItem(STORAGE_KEYS.LAST_ACTIVE_LIST_ID);
    return storedId ? parseInt(storedId, 10) : null;
  } catch (error) {
    console.warn('Failed to retrieve last active list ID from localStorage:', error);
    return null;
  }
};

/**
 * Store user preferences
 */
export const setUserPreferences = (preferences: Record<string, any>): void => {
  if (!isBrowser()) return;
  
  try {
    localStorage.setItem(STORAGE_KEYS.USER_PREFERENCES, JSON.stringify(preferences));
  } catch (error) {
    console.warn('Failed to save user preferences to localStorage:', error);
  }
};

/**
 * Retrieve user preferences
 */
export const getUserPreferences = (): Record<string, any> => {
  if (!isBrowser()) return {};
  
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.USER_PREFERENCES);
    return stored ? JSON.parse(stored) : {};
  } catch (error) {
    console.warn('Failed to retrieve user preferences from localStorage:', error);
    return {};
  }
};

/**
 * Clear all FamilyCart data from localStorage
 */
export const clearAllStoredData = (): void => {
  if (!isBrowser()) return;
  
  try {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
  } catch (error) {
    console.warn('Failed to clear localStorage data:', error);
  }
};
