# API Documentation (Swagger/OpenAPI)

## Overview

This project now includes comprehensive **Swagger/OpenAPI 3.0** documentation for all API endpoints. The documentation is automatically generated and provides interactive exploration of all available API routes.

## Features

- **OpenAPI 3.0.2 Specification**: Complete API specification following the OpenAPI standard
- **Interactive Swagger UI**: Web-based interface for exploring and testing APIs
- **47 Documented Endpoints**: All major endpoints across 10 categories
- **Schema Definitions**: Reusable component schemas for all data models
- **Authentication Documentation**: Session-based and JWT authentication schemes

## Access Points

### Swagger UI Interface
Visit `/api/docs` in your browser to access the interactive Swagger UI:
```
http://localhost:5000/api/docs
```

### OpenAPI JSON Specification
Access the raw OpenAPI specification in JSON format:
```
http://localhost:5000/api/openapi.json
```

## API Categories

The documentation covers the following endpoint categories:

1. **Health** - System health checks and metrics
   - `/health` - Health check endpoint
   - `/metrics` - Prometheus-style metrics

2. **Authentication** - User registration and login
   - `/users/register` - User registration
   - `/users/login` - User authentication
   - `/users/logout` - User logout
   - `/users/verify_phone` - Phone verification
   - `/users/verify_email` - Email verification
   - `/users/confirm_email/<token>` - Email confirmation

3. **Users** - User profile management
   - `/users/profile` - Get user profile
   - `/users/edit` - Update profile
   - `/users/delete` - Delete account

4. **Orders** - Order management
   - `/users/place_order` - Create order
   - `/users/orders` - Get buyer orders
   - `/users/seller/orders` - Get seller orders
   - `/users/order/{id}/confirm` - Confirm order
   - `/users/order/{id}/reject` - Reject order

5. **Ports** - Port information
   - `/users/api/ports` - List all ports
   - `/users/add_port` - Add new port
   - `/users/update_port/{id}` - Update port
   - `/users/delete_port/{id}` - Delete port

6. **Messages** - Messaging system
   - `/users/chat` - Chat interface
   - `/users/support` - Support requests

7. **Notifications** - User notifications
   - `/users/notifications` - Get notifications

8. **Premium** - Premium membership
   - `/users/upgrade_to_premium` - Upgrade page
   - `/users/start_upgrade` - Start upgrade process
   - `/users/upload_documents` - Upload documents
   - `/users/make_payment` - Process payment
   - `/users/payment_confirmation` - Payment confirmation

9. **Admin** - Administrative operations
   - `/admin` - Admin dashboard
   - `/admin/users` - User management
   - `/admin/premium_requests` - Premium requests
   - `/admin/user/{id}/role` - Update user role
   - `/admin/user/{id}/delete` - Delete user
   - `/admin/chat/{user_id}` - Admin-user chat

10. **Magazine** - Magazine publications
    - `/magazine` - Magazine homepage
    - `/magazine/download/{id}` - Download issue
    - `/magazine/sponsorship` - Sponsorship requests

## Data Schemas

The following schemas are defined in the OpenAPI specification:

- **User** - User account information
- **Order** - Order details
- **Port** - Port location data
- **Message** - Message content
- **Notification** - Notification details
- **PremiumRequest** - Premium membership request
- **MagazineIssue** - Magazine publication info
- **Login** - Login credentials
- **Register** - Registration data
- **Error** - Error response format

## Authentication

The API supports two authentication methods:

1. **Session Authentication** (Primary)
   - Type: API Key
   - Location: Cookie
   - Name: `session`

2. **Bearer Token Authentication** (JWT)
   - Type: HTTP Bearer
   - Scheme: Bearer

## Usage Examples

### Using Swagger UI

1. Navigate to `http://localhost:5000/api/docs`
2. Browse endpoints by category
3. Click on an endpoint to expand details
4. Use "Try it out" button to test endpoints
5. View request/response schemas

### Using the OpenAPI JSON

```bash
# Download the specification
curl http://localhost:5000/api/openapi.json -o openapi.json

# Use with code generators
openapi-generator generate -i openapi.json -g python -o ./client

# Use with Postman
# Import the JSON file into Postman
```

### Programmatic Access

```python
import requests

# Get OpenAPI spec
response = requests.get('http://localhost:5000/api/openapi.json')
spec = response.json()

# List all paths
for path in spec['paths']:
    print(f"Endpoint: {path}")
```

## Integration

The API documentation is automatically integrated into the Flask application:

```python
# In app.py
from api_docs import init_api_docs

def create_app():
    app = Flask(__name__)
    # ... other setup ...
    
    # Initialize API documentation
    init_api_docs(app)
    
    return app
```

## Customization

To add documentation for new endpoints:

1. Add the endpoint to `get_all_paths()` function in `api_docs.py`
2. Define any new schemas using Marshmallow Schema classes
3. Register schemas with the spec object
4. Include appropriate tags, parameters, and responses

## Tools Compatibility

The OpenAPI specification is compatible with:

- **Swagger UI** - Interactive documentation
- **Swagger Editor** - Online editor
- **Postman** - API testing
- **OpenAPI Generator** - Code generation
- **Redoc** - Alternative documentation UI
- **Insomnia** - API client

## Files

- `/api_docs.py` - Main API documentation module
- `/api/docs` - Swagger UI endpoint
- `/api/openapi.json` - OpenAPI specification

## Maintenance

The API documentation should be updated whenever:
- New endpoints are added
- Existing endpoints are modified
- Data models change
- Authentication methods are updated

Run tests to verify documentation accuracy:
```bash
python -c "from app import create_app; app = create_app()"
```

## Support

For issues or questions about the API documentation, contact the development team.
