# Shopping List and Items API Fix

## Issue Description
The dashboard wasn't displaying correctly after login because the backend API wasn't returning expected data structures for shopping lists and items. In particular:

1. The shopping list schema was missing the `members` field required by the frontend
2. Endpoints for shopping list items were not functioning correctly
3. Users could not access shared shopping lists

## Solution

### Shopping List Schema Updates
1. Updated `ShoppingListRead` schema to include a `members` field that returns a list of users who have access to the shopping list:
   ```python
   class ShoppingListRead(ShoppingListBase):
       id: int
       owner_id: uuid.UUID
       created_at: datetime
       updated_at: datetime
       items: list = []  # Default to empty list if no items
       members: List[UserRead] = []  # List of users who have access to this list
   ```

### Shopping List API Improvements
1. Enhanced `GET /api/v1/shopping-lists/` endpoint to:
   - Return both owned and shared lists
   - Populate the `members` field for each list

2. Enhanced `GET /api/v1/shopping-lists/{list_id}` endpoint to:
   - Allow access to lists shared with the user
   - Properly populate `members` field

3. Enhanced `GET /api/v1/shopping-lists/{list_id}/items` endpoint to:
   - Allow access to items in lists shared with the user

4. Added new `POST /api/v1/shopping-lists/{list_id}/share` endpoint to:
   - Allow list owners to share lists with other users
   - Return the updated list with new members

### Added Unit Tests
Created comprehensive unit tests for all shopping list and item API endpoints:
1. Test creating shopping lists
2. Test retrieving all shopping lists
3. Test retrieving a specific shopping list
4. Test updating shopping list details
5. Test deleting shopping lists
6. Test adding items to shopping lists
7. Test retrieving items from shopping lists

## Related Files
- `/backend/app/schemas/shopping_list.py`
- `/backend/app/api/v1/endpoints/shopping_lists.py`
- `/backend/app/schemas/share.py`
- `/backend/app/tests/test_shopping_lists.py`
- `/backend/app/tests/conftest.py`

## Impact
These changes ensure that the shopping lists and items display correctly in the dashboard after login, and that the sharing functionality works as expected. The frontend can now display the list of members for each shopping list and properly manage items.
