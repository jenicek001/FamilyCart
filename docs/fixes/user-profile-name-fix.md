# User Profile Name Fix

## Issue
The user profile page was showing an empty name even though the first and last name values were correctly stored in the database. The issue was caused by a mismatch between how the backend and frontend handle the user name:

1. Backend stores user names as `first_name` and `last_name` fields in the database
2. Backend provides a computed `full_name` property that combines these fields
3. Frontend expected a `full_name` field in the API response
4. When updating, the frontend was sending a `full_name` field, which the backend does not handle (it expects `first_name` and `last_name`)

## Solution

1. Updated the frontend User interface in `src/types/index.ts` to include `first_name` and `last_name` fields alongside `full_name`
2. Modified the profile page update handler in `src/app/(app)/profile/page.tsx` to:
   - Split the full name into first and last names
   - Send separate `first_name` and `last_name` fields to the backend API
   - Keep the existing UI where users enter their full name in a single field

## Benefits

- Maintains UI simplicity (single full name field) while correctly handling data storage (separate first/last name fields)
- Ensures proper saving and display of names throughout the application
- Accommodates users with only first names or names that don't fit the first/last pattern

## Notes

- The AuthContext already had logic to derive `full_name` from `first_name` and `last_name`, which was working correctly
- The backend User model and schema were already correctly set up to handle first and last names

This fix ensures that name changes persist correctly and display properly throughout the application.
