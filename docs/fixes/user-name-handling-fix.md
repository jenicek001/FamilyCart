# User Name Handling Fix

## Issue
- User full name was not being stored in the database even though it was submitted in the registration form
- Database showed NULL values for first_name and last_name columns
- Frontend was sending a `full_name` field but backend expected separate `first_name` and `last_name` fields

## Analysis
1. The database schema stores names in two separate fields: `first_name` and `last_name`
2. The `User` model in the backend correctly defines these fields
3. The `UserCreate` Pydantic schema expects `first_name` and `last_name` as separate fields
4. However, the frontend signup form was sending a single `full_name` field

## Solution
Updated the frontend signup page to:
1. Split the fullName value into first and last name components
2. Send separate first_name and last_name fields in the API request
```typescript
// Split fullName into first_name and last_name
const nameParts = fullName.trim().split(' ');
const firstName = nameParts[0];
const lastName = nameParts.length > 1 ? nameParts.slice(1).join(' ') : '';

await axios.post('/api/v1/auth/register', {
  email,
  password,
  first_name: firstName,
  last_name: lastName,
});
```

## Testing
- Created a test user with both first and last name
- Verified in the database that both fields are populated correctly:
```
id,email,first_name,last_name,is_active,is_superuser,is_verified
e9dfdb3f-0a11-4717-865a-28c37214d0f0,test2@example.com,John,Doe,True,False,False
```
