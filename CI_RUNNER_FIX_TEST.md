# CI Runner Fix Test

## Fixed Issue
- Runners were crashing every ~15 minutes with HTTP 404 errors
- Root cause: Using registration token instead of removal token for runner cleanup
- Solution: Implemented proper removal token API calls

## Changes Made
1. Updated `deploy/github-runners/entrypoint.sh`:
   - Added `get_removal_token()` function to fetch proper removal tokens
   - Updated shutdown cleanup to use removal tokens
   - Updated startup cleanup to use removal tokens
   
## Test Status
- Runners restarted at: $(date)
- All 3 runners started successfully and are healthy
- No HTTP 404 errors in logs since restart
- Runners processing jobs normally

This test file can be removed after confirming the fix works.