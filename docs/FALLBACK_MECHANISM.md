# Fallback Mechanism for Offline Mode

## Overview
The application now includes a fallback mechanism to handle network disconnections gracefully. When external APIs are unavailable, the system automatically switches to local data sources to prevent UI breakdowns.

## Changes Made

### 1. Created `utils/fallback.py`
A utility module that provides the `get_data_with_fallback()` function:
- Attempts to fetch data from external URLs
- Automatically catches network errors (timeout, connection errors)
- Falls back to local database queries or static demo data
- Logs all fallback events for debugging

### 2. Updated `routes/users/routes.py`

#### Vessel Finder Route (`/vessel_finder`)
- **Online Mode**: Fetches real-time vessel data from SeaRoutes API
- **Offline Mode**: Displays demo data with a warning message
- Shows "Demo Vessel (Offline Mode)" when network is unavailable

#### Map Route (`/map`)
- Now uses local PostgreSQL database as primary source
- Ports data is stored locally, so no external dependency
- Limited to 200 ports for performance optimization

#### Ports API Route (`/api/ports`)
- Fetches data exclusively from local database
- Added try-except block for error handling
- Returns empty list instead of crashing on DB errors

## How It Works

### For Vessel Tracking:
```python
# When internet is connected:
✅ Real vessel position, speed, destination from API

# When internet is disconnected:
⚠️ Demo data shown with warning: "Network unavailable. Showing demo data."
   - Latitude/Longitude: Example coordinates
   - Name: "Demo Vessel (Offline Mode)"
   - Speed: 0.0
   - Destination: Unknown
```

### For Ports/Map:
```python
# Always works (online or offline):
✅ Data loaded from local PostgreSQL database
✅ No external API dependency
✅ Fast response time
```

## Benefits
1. **No UI Breakage**: Site remains functional even without internet
2. **Better UX**: Users see meaningful fallback data instead of errors
3. **Graceful Degradation**: Core features work in limited capacity
4. **Logging**: All fallback events are logged for monitoring

## Testing Offline Mode
To test the fallback mechanism:
1. Disconnect your internet
2. Navigate to `/vessel_finder`
3. Enter a valid IMO number (7 digits)
4. You should see demo data with a warning message instead of an error

## Future Enhancements
- Add caching layer for API responses
- Implement background sync when connection restores
- Store last-known vessel positions in database
- Add more sophisticated demo data for different scenarios
