"""
API Documentation Module for International Trade Platform
Generates Swagger/OpenAPI documentation using flask-smorest

This module provides comprehensive API documentation for all endpoints
in the international trade platform, including authentication, user management,
admin operations, and magazine features.
"""

import os
from flask import Blueprint
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from marshmallow import Schema, fields, validate


# Create API specification
spec = APISpec(
    title="International Trade Platform API",
    version="1.0.0",
    openapi_version="3.0.2",
    info=dict(
        description="Comprehensive API for international trade platform with user management, "
                   "order processing, admin controls, and magazine features",
        contact=dict(name="API Support", email="support@tradeplatform.com"),
    ),
    servers=[
        {"url": "http://localhost:5000", "description": "Development server"},
        {"url": "https://api.tradeplatform.com", "description": "Production server"},
    ],
    plugins=[MarshmallowPlugin()],
)

# Create blueprint for API documentation
api_bp = Blueprint('api_docs', __name__, url_prefix='/api')


# ==================== SCHEMAS ====================

class UserSchema(Schema):
    """User model schema"""
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    role = fields.Str(validate=validate.OneOf(['user', 'admin', 'provider']))
    company = fields.Str()
    country = fields.Str()
    phone = fields.Str()
    is_premium = fields.Bool()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)


class OrderSchema(Schema):
    """Order model schema"""
    id = fields.Int(dump_only=True)
    buyer_id = fields.Int(required=True)
    seller_id = fields.Int()
    product_name = fields.Str(required=True)
    quantity = fields.Float(required=True)
    unit = fields.Str()
    price = fields.Float()
    currency = fields.Str(load_default='USD')
    status = fields.Str(validate=validate.OneOf([
        'pending', 'confirmed', 'rejected', 'completed', 'cancelled'
    ]))
    created_at = fields.DateTime(dump_only=True)


class PortSchema(Schema):
    """Port model schema"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    country = fields.Str(required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)


class MessageSchema(Schema):
    """Message model schema"""
    id = fields.Int(dump_only=True)
    sender_id = fields.Int(required=True)
    receiver_id = fields.Int(required=True)
    content = fields.Str(required=True)
    is_read = fields.Bool(load_default=False)
    created_at = fields.DateTime(dump_only=True)


class NotificationSchema(Schema):
    """Notification model schema"""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    title = fields.Str(required=True)
    message = fields.Str(required=True)
    is_read = fields.Bool(load_default=False)
    created_at = fields.DateTime(dump_only=True)


class PremiumRequestSchema(Schema):
    """Premium membership request schema"""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    status = fields.Str(validate=validate.OneOf(['pending', 'approved', 'rejected']))
    documents = fields.List(fields.Str())
    created_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class MagazineIssueSchema(Schema):
    """Magazine issue schema"""
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    issue_number = fields.Int()
    publication_date = fields.Date()
    file_url = fields.Url()
    sponsor = fields.Str()


class LoginSchema(Schema):
    """Login request schema"""
    username = fields.Str(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))


class RegisterSchema(Schema):
    """Registration request schema"""
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    role = fields.Str(required=True, validate=validate.OneOf(['buyer', 'seller', 'provider']))
    company = fields.Str()
    country = fields.Str()
    phone = fields.Str()


class ErrorResponseSchema(Schema):
    """Error response schema"""
    error = fields.Str()
    message = fields.Str()
    status_code = fields.Int()


# ==================== TAGS ====================

tags = {
    "Authentication": "User authentication and registration endpoints",
    "Users": "User profile and account management",
    "Orders": "Order creation and management",
    "Ports": "Port information and management",
    "Messages": "Messaging system between users",
    "Notifications": "User notifications",
    "Admin": "Administrative operations",
    "Magazine": "Magazine and publication management",
    "Premium": "Premium membership requests and management",
    "Health": "System health and monitoring"
}


# ==================== API ROUTES ====================

@api_bp.route('/docs')
def api_docs():
    """
    Get API documentation in Swagger UI format
    
    Returns interactive Swagger UI for API exploration
    """
    from flask import render_template_string
    
    swagger_ui_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation - International Trade Platform</title>
        <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css">
        <style>
            body { margin: 0; padding: 0; }
            #swagger-ui { max-width: 1460px; margin: 0 auto; }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
        <script>
            window.onload = function() {
                const ui = SwaggerUIBundle({
                    url: "/api/openapi.json",
                    dom_id: '#swagger-ui',
                    presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
                    layout: "BaseLayout",
                    deepLinking: true,
                    showExtensions: true,
                    showCommonExtensions: true
                });
                window.ui = ui;
            };
        </script>
    </body>
    </html>
    """
    return render_template_string(swagger_ui_html)


@api_bp.route('/openapi.json')
def openapi_spec():
    """
    Get OpenAPI specification in JSON format
    
    Returns complete OpenAPI 3.0 specification for all API endpoints
    """
    from flask import jsonify
    
    # Build complete spec
    from apispec import yaml_utils
    
    full_spec = {
        "openapi": "3.0.2",
        "info": {
            "title": "International Trade Platform API",
            "version": "1.0.0",
            "description": """
            ## Comprehensive API for International Trade
            
            This API provides complete functionality for:
            - User authentication and authorization
            - Order management and processing
            - Port and logistics information
            - Messaging and notifications
            - Admin panel operations
            - Magazine publications
            - Premium membership management
            
            ### Authentication
            All authenticated endpoints require a valid session cookie or JWT token.
            
            ### Rate Limiting
            API calls are rate-limited to prevent abuse. Limits vary by endpoint.
            
            ### Response Format
            All responses are in JSON format with consistent error handling.
            """
        },
        "servers": [
            {"url": "http://localhost:5000", "description": "Development"},
            {"url": "https://api.tradeplatform.com", "description": "Production"}
        ],
        "tags": [{"name": tag, "description": desc} for tag, desc in tags.items()],
        "paths": {},
        "components": {
            "schemas": {
                "User": spec.components.schemas['User'] if 'User' in spec.components.schemas else {},
                "Order": spec.components.schemas['Order'] if 'Order' in spec.components.schemas else {},
                "Port": spec.components.schemas['Port'] if 'Port' in spec.components.schemas else {},
                "Message": spec.components.schemas['Message'] if 'Message' in spec.components.schemas else {},
                "Notification": spec.components.schemas['Notification'] if 'Notification' in spec.components.schemas else {},
                "PremiumRequest": spec.components.schemas['PremiumRequest'] if 'PremiumRequest' in spec.components.schemas else {},
                "MagazineIssue": spec.components.schemas['MagazineIssue'] if 'MagazineIssue' in spec.components.schemas else {},
                "Login": spec.components.schemas['Login'] if 'Login' in spec.components.schemas else {},
                "Register": spec.components.schemas['Register'] if 'Register' in spec.components.schemas else {},
                "Error": spec.components.schemas['Error'] if 'Error' in spec.components.schemas else {}
            },
            "securitySchemes": {
                "sessionAuth": {
                    "type": "apiKey",
                    "in": "cookie",
                    "name": "session"
                },
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "security": [{"sessionAuth": []}]
    }
    
    # Register all schemas with apispec
    spec.components.schema('User', schema=UserSchema)
    spec.components.schema('Order', schema=OrderSchema)
    spec.components.schema('Port', schema=PortSchema)
    spec.components.schema('Message', schema=MessageSchema)
    spec.components.schema('Notification', schema=NotificationSchema)
    spec.components.schema('PremiumRequest', schema=PremiumRequestSchema)
    spec.components.schema('MagazineIssue', schema=MagazineIssueSchema)
    spec.components.schema('Login', schema=LoginSchema)
    spec.components.schema('Register', schema=RegisterSchema)
    spec.components.schema('Error', schema=ErrorResponseSchema)
    
    # Update components with registered schemas
    full_spec["components"]["schemas"] = spec.to_dict()["components"]["schemas"]
    
    # Add all paths
    full_spec["paths"] = get_all_paths()
    
    return jsonify(full_spec)


def get_all_paths():
    """
    Generate OpenAPI paths for all application routes
    
    Returns dict of all API paths with their specifications
    """
    paths = {}
    
    # Health endpoints
    paths.update({
        "/health": {
            "get": {
                "tags": ["Health"],
                "summary": "Health check endpoint",
                "description": "Returns system health status including database, Redis, and Celery status",
                "responses": {
                    "200": {
                        "description": "System is healthy",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "healthy"},
                                        "timestamp": {"type": "string", "format": "date-time"},
                                        "version": {"type": "string", "example": "1.0.0"},
                                        "checks": {
                                            "type": "object",
                                            "properties": {
                                                "database": {"type": "string"},
                                                "redis": {"type": "string"},
                                                "celery": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "503": {
                        "description": "System is unhealthy"
                    }
                }
            }
        },
        "/metrics": {
            "get": {
                "tags": ["Health"],
                "summary": "System metrics endpoint",
                "description": "Returns Prometheus-style metrics for monitoring",
                "responses": {
                    "200": {
                        "description": "Metrics data",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "uptime_seconds": {"type": "number"},
                                        "active_users": {"type": "integer"},
                                        "total_orders": {"type": "integer"},
                                        "timestamp": {"type": "string", "format": "date-time"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    })
    
    # Authentication endpoints
    paths.update({
        "/users/register": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Get registration page",
                "responses": {"200": {"description": "Registration form HTML"}}
            },
            "post": {
                "tags": ["Authentication"],
                "summary": "Register new user",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {"$ref": "#/components/schemas/Register"}
                        }
                    }
                },
                "responses": {
                    "302": {"description": "Redirect to login page"},
                    "400": {
                        "description": "Invalid input",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
                    }
                }
            }
        },
        "/users/login": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Get login page",
                "responses": {"200": {"description": "Login form HTML"}}
            },
            "post": {
                "tags": ["Authentication"],
                "summary": "Authenticate user",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "302": {"description": "Redirect to dashboard"},
                    "401": {"description": "Invalid credentials"}
                }
            }
        },
        "/users/logout": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Logout user",
                "responses": {"302": {"description": "Redirect to login page"}}
            }
        },
        "/users/verify_phone": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Verify phone number",
                "responses": {"200": {"description": "Phone verification form"}}
            },
            "post": {
                "tags": ["Authentication"],
                "summary": "Submit phone verification code",
                "responses": {
                    "200": {"description": "Verification successful"},
                    "400": {"description": "Invalid code"}
                }
            }
        },
        "/users/verify_email": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Request email verification",
                "responses": {"200": {"description": "Email sent"}}
            }
        },
        "/users/confirm_email/<token>": {
            "get": {
                "tags": ["Authentication"],
                "summary": "Confirm email with token",
                "parameters": [
                    {
                        "name": "token",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {"description": "Email confirmed"},
                    "400": {"description": "Invalid or expired token"}
                }
            }
        }
    })
    
    # User management endpoints
    paths.update({
        "/users/profile": {
            "get": {
                "tags": ["Users"],
                "summary": "Get user profile",
                "security": [{"sessionAuth": []}],
                "responses": {
                    "200": {"description": "User profile data"},
                    "401": {"description": "Unauthorized"}
                }
            }
        },
        "/users/edit": {
            "get": {
                "tags": ["Users"],
                "summary": "Get edit profile page",
                "security": [{"sessionAuth": []}],
                "responses": {"200": {"description": "Edit form HTML"}}
            },
            "post": {
                "tags": ["Users"],
                "summary": "Update user profile",
                "security": [{"sessionAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "email": {"type": "string", "format": "email"},
                                    "company": {"type": "string"},
                                    "country": {"type": "string"},
                                    "phone": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "302": {"description": "Redirect to profile"},
                    "400": {"description": "Invalid data"}
                }
            }
        },
        "/users/delete": {
            "post": {
                "tags": ["Users"],
                "summary": "Delete user account",
                "security": [{"sessionAuth": []}],
                "responses": {
                    "302": {"description": "Redirect to login"},
                    "401": {"description": "Unauthorized"}
                }
            }
        }
    })
    
    # Order endpoints
    paths.update({
        "/users/place_order": {
            "get": {
                "tags": ["Orders"],
                "summary": "Get order creation form",
                "security": [{"sessionAuth": []}],
                "responses": {"200": {"description": "Order form HTML"}}
            },
            "post": {
                "tags": ["Orders"],
                "summary": "Create new order",
                "security": [{"sessionAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "product_name": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "unit": {"type": "string"},
                                    "price": {"type": "number"},
                                    "currency": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "302": {"description": "Redirect to orders list"},
                    "400": {"description": "Invalid order data"}
                }
            }
        },
        "/users/orders": {
            "get": {
                "tags": ["Orders"],
                "summary": "Get user's orders (as buyer)",
                "security": [{"sessionAuth": []}],
                "responses": {
                    "200": {"description": "List of orders"}
                }
            }
        },
        "/users/seller/orders": {
            "get": {
                "tags": ["Orders"],
                "summary": "Get user's orders (as seller)",
                "security": [{"sessionAuth": []}],
                "responses": {
                    "200": {"description": "List of orders"}
                }
            }
        },
        "/users/order/{order_id}/confirm": {
            "post": {
                "tags": ["Orders"],
                "summary": "Confirm an order",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {
                        "name": "order_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "302": {"description": "Redirect to orders"},
                    "404": {"description": "Order not found"}
                }
            }
        },
        "/users/order/{order_id}/reject": {
            "post": {
                "tags": ["Orders"],
                "summary": "Reject an order",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {
                        "name": "order_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "302": {"description": "Redirect to orders"},
                    "404": {"description": "Order not found"}
                }
            }
        }
    })
    
    # Port endpoints
    paths.update({
        "/users/api/ports": {
            "get": {
                "tags": ["Ports"],
                "summary": "Get all ports",
                "responses": {
                    "200": {
                        "description": "List of ports",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Port"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "/users/add_port": {
            "post": {
                "tags": ["Ports"],
                "summary": "Add new port",
                "security": [{"sessionAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Port"}
                        }
                    }
                },
                "responses": {
                    "201": {"description": "Port created"},
                    "400": {"description": "Invalid data"}
                }
            }
        },
        "/users/update_port/{port_id}": {
            "put": {
                "tags": ["Ports"],
                "summary": "Update port",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {
                        "name": "port_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Port"}
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Port updated"},
                    "404": {"description": "Port not found"}
                }
            }
        },
        "/users/delete_port/{port_id}": {
            "delete": {
                "tags": ["Ports"],
                "summary": "Delete port",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {
                        "name": "port_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {"description": "Port deleted"},
                    "404": {"description": "Port not found"}
                }
            }
        }
    })
    
    # Messaging endpoints
    paths.update({
        "/users/chat": {
            "get": {
                "tags": ["Messages"],
                "summary": "Get chat interface",
                "security": [{"sessionAuth": []}],
                "responses": {"200": {"description": "Chat interface HTML"}}
            },
            "post": {
                "tags": ["Messages"],
                "summary": "Send message",
                "security": [{"sessionAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "receiver_id": {"type": "integer"},
                                    "content": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Message sent"},
                    "400": {"description": "Invalid data"}
                }
            }
        },
        "/users/notifications": {
            "get": {
                "tags": ["Notifications"],
                "summary": "Get user notifications",
                "security": [{"sessionAuth": []}],
                "responses": {
                    "200": {
                        "description": "List of notifications",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/Notification"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "/users/support": {
            "get": {
                "tags": ["Messages"],
                "summary": "Get support interface",
                "security": [{"sessionAuth": []}],
                "responses": {"200": {"description": "Support interface HTML"}}
            },
            "post": {
                "tags": ["Messages"],
                "summary": "Send support request",
                "security": [{"sessionAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "subject": {"type": "string"},
                                    "message": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Support request sent"}
                }
            }
        }
    })
    
    # Premium membership endpoints
    paths.update({
        "/users/upgrade_to_premium": {
            "get": {
                "tags": ["Premium"],
                "summary": "Get premium upgrade page",
                "security": [{"sessionAuth": []}],
                "responses": {"200": {"description": "Premium upgrade page"}}
            }
        },
        "/users/start_upgrade": {
            "post": {
                "tags": ["Premium"],
                "summary": "Start premium upgrade process",
                "security": [{"sessionAuth": []}],
                "responses": {
                    "302": {"description": "Redirect to document upload"}
                }
            }
        },
        "/users/upload_documents": {
            "get": {
                "tags": ["Premium"],
                "summary": "Get document upload page",
                "security": [{"sessionAuth": []}],
                "responses": {"200": {"description": "Upload form"}}
            },
            "post": {
                "tags": ["Premium"],
                "summary": "Upload premium verification documents",
                "security": [{"sessionAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "documents": {
                                        "type": "array",
                                        "items": {"type": "string", "format": "binary"}
                                    }
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "302": {"description": "Redirect to payment"}
                }
            }
        },
        "/users/make_payment": {
            "get": {
                "tags": ["Premium"],
                "summary": "Get payment page",
                "security": [{"sessionAuth": []}],
                "responses": {"200": {"description": "Payment page"}}
            },
            "post": {
                "tags": ["Premium"],
                "summary": "Process premium payment",
                "security": [{"sessionAuth": []}],
                "responses": {
                    "302": {"description": "Redirect to confirmation"}
                }
            }
        },
        "/users/payment_confirmation": {
            "get": {
                "tags": ["Premium"],
                "summary": "Get payment confirmation page",
                "responses": {"200": {"description": "Confirmation page"}}
            }
        }
    })
    
    # Admin endpoints
    paths.update({
        "/admin": {
            "get": {
                "tags": ["Admin"],
                "summary": "Get admin dashboard",
                "security": [{"sessionAuth": []}],
                "responses": {
                    "200": {"description": "Admin dashboard"},
                    "403": {"description": "Forbidden - not admin"}
                }
            }
        },
        "/admin/dashboard": {
            "get": {
                "tags": ["Admin"],
                "summary": "Get detailed admin dashboard",
                "security": [{"sessionAuth": []}],
                "responses": {
                    "200": {"description": "Dashboard with statistics"}
                }
            }
        },
        "/admin/users": {
            "get": {
                "tags": ["Admin"],
                "summary": "List all users",
                "security": [{"sessionAuth": []}],
                "responses": {
                    "200": {
                        "description": "List of users",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "/admin/user/{user_id}/role": {
            "post": {
                "tags": ["Admin"],
                "summary": "Update user role",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "role": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "302": {"description": "Redirect to users list"}
                }
            }
        },
        "/admin/premium_requests": {
            "get": {
                "tags": ["Admin"],
                "summary": "List premium requests",
                "security": [{"sessionAuth": []}],
                "responses": {
                    "200": {
                        "description": "List of premium requests",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {"$ref": "#/components/schemas/PremiumRequest"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "/admin/approve_premium/{req_id}": {
            "post": {
                "tags": ["Admin"],
                "summary": "Approve premium request",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {
                        "name": "req_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "302": {"description": "Redirect to requests list"}
                }
            }
        },
        "/admin/reject_premium/{req_id}": {
            "post": {
                "tags": ["Admin"],
                "summary": "Reject premium request",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {
                        "name": "req_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "302": {"description": "Redirect to requests list"}
                }
            }
        },
        "/admin/user/{user_id}/delete": {
            "post": {
                "tags": ["Admin"],
                "summary": "Delete user",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "302": {"description": "Redirect to users list"}
                }
            }
        },
        "/admin/user/{user_id}/deactivate": {
            "post": {
                "tags": ["Admin"],
                "summary": "Deactivate user",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "302": {"description": "Redirect to users list"}
                }
            }
        },
        "/admin/user/{user_id}/activate": {
            "post": {
                "tags": ["Admin"],
                "summary": "Activate user",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "302": {"description": "Redirect to users list"}
                }
            }
        },
        "/admin/user/{user_id}/toggle_premium": {
            "post": {
                "tags": ["Admin"],
                "summary": "Toggle user premium status",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "302": {"description": "Redirect to users list"}
                }
            }
        },
        "/admin/chat": {
            "get": {
                "tags": ["Admin"],
                "summary": "Get admin chat interface",
                "security": [{"sessionAuth": []}],
                "responses": {"200": {"description": "Chat interface"}}
            }
        },
        "/admin/chat/{user_id}": {
            "get": {
                "tags": ["Admin"],
                "summary": "Chat with specific user",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {"200": {"description": "Chat interface"}}
            },
            "post": {
                "tags": ["Admin"],
                "summary": "Send message to user",
                "security": [{"sessionAuth": []}],
                "parameters": [
                    {
                        "name": "user_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "content": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Message sent"}
                }
            }
        },
        "/admin/login": {
            "get": {
                "tags": ["Admin"],
                "summary": "Get admin login page",
                "responses": {"200": {"description": "Login form"}}
            },
            "post": {
                "tags": ["Admin"],
                "summary": "Admin login",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "302": {"description": "Redirect to admin dashboard"},
                    "401": {"description": "Invalid credentials"},
                    "403": {"description": "Not an admin"}
                }
            }
        }
    })
    
    # Magazine endpoints
    paths.update({
        "/magazine": {
            "get": {
                "tags": ["Magazine"],
                "summary": "Get magazine homepage",
                "responses": {"200": {"description": "Magazine homepage"}}
            }
        },
        "/magazine/download/{issue_id}": {
            "get": {
                "tags": ["Magazine"],
                "summary": "Download magazine issue",
                "parameters": [
                    {
                        "name": "issue_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {"description": "File download"},
                    "404": {"description": "Issue not found"}
                }
            }
        },
        "/magazine/sponsorship": {
            "get": {
                "tags": ["Magazine"],
                "summary": "Get sponsorship information",
                "responses": {"200": {"description": "Sponsorship page"}}
            },
            "post": {
                "tags": ["Magazine"],
                "summary": "Submit sponsorship request",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/x-www-form-urlencoded": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "company_name": {"type": "string"},
                                    "contact_email": {"type": "string"},
                                    "message": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Request submitted"}
                }
            }
        }
    })
    
    # Additional utility endpoints
    paths.update({
        "/users/vessel_finder": {
            "get": {
                "tags": ["Users"],
                "summary": "Get vessel finder tool",
                "security": [{"sessionAuth": []}],
                "responses": {"200": {"description": "Vessel finder interface"}}
            },
            "post": {
                "tags": ["Users"],
                "summary": "Search for vessels",
                "security": [{"sessionAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "port": {"type": "string"},
                                    "vessel_type": {"type": "string"},
                                    "date_range": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Search results"}
                }
            }
        },
        "/users/map": {
            "get": {
                "tags": ["Ports"],
                "summary": "Get interactive map",
                "responses": {"200": {"description": "Map interface"}}
            }
        }
    })
    
    return paths


def init_api_docs(app):
    """
    Initialize API documentation for the Flask application
    
    Args:
        app: Flask application instance
    
    Returns:
        None
    """
    # Register the API blueprint
    app.register_blueprint(api_bp)
    
    # Log registration
    app.logger.info("API documentation registered at /api/docs and /api/openapi.json")


if __name__ == "__main__":
    # Test the API documentation generation
    import json
    
    # Generate and print the spec
    spec_data = {
        "openapi": "3.0.2",
        "info": {
            "title": "International Trade Platform API",
            "version": "1.0.0"
        },
        "paths": get_all_paths()
    }
    
    print(json.dumps(spec_data, indent=2))
