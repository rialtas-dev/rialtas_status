# Rialtas Status Page

A Django-based status page for monitoring the health of all Rialtas company services and infrastructure.

## Features

- **Public Status Dashboard**: View real-time status of all company services
- **Service Management**: Add and configure services (Database, Cloudflare, Thinfinity, Apps, etc.)
- **Status Updates**: Update service status with Comments and Plan sections
- **History Tracking**: View last 5 updates per service, with all history stored in database
- **Admin Interface**: Secure admin panel for managing services and updates
- **REST API**: Django Ninja-powered API for external apps to post status updates
- **API Key Authentication**: Secure token-based authentication for API access
- **Status Levels**: Stable, Degraded Performance, Partial Outage, Major Outage, Maintenance
- **Tailwind CSS 4**: Modern, responsive styling

## Setup Instructions

### 1. Install Tailwind CSS CLI

First, install the Tailwind CSS CLI tool:

```bash
npm install -g tailwindcss
```

### 2. Generate CSS

Run Tailwind to generate the output CSS file:

```bash
tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
```

Leave this running in a terminal during development (the `--watch` flag will auto-rebuild when you change templates).

For production, build minified CSS:

```bash
tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify
```

### 3. Create Admin User

Create a superuser to access the admin panel:

```bash
python manage.py createsuperuser
```

### 4. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at:
- **Status Page**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/

## Usage

### Adding Services

1. Log in to the admin panel at http://localhost:8000/admin/
2. Click on "Services" → "Add Service"
3. Enter:
   - **Name**: e.g., "Database", "Cloudflare", "Thinfinity", "App"
   - **Description**: Optional description of the service
   - **Order**: Display order (lower numbers appear first)
   - **Is active**: Whether to show on the status page

### Updating Service Status

1. Go to the admin panel
2. Click on "Status updates" → "Add status update"
3. Select the service and choose a status:
   - **Stable**: Everything is working normally
   - **Degraded Performance**: Service is slow but functional
   - **Partial Outage**: Some features unavailable
   - **Major Outage**: Service is completely down
   - **Maintenance**: Scheduled maintenance
4. Fill in the **Comments** field to describe the issue
5. Fill in the **Plan** field to describe how you'll fix it
6. Click Save (the system automatically records which user created the update)

The status page will immediately show the updated status.

### Viewing History

- Click on any service on the main status page to expand and see its last 5 updates
- The update history shows inline without navigating to a new page
- All historical updates remain in the database

## Project Structure

```
rialtas_status/
├── status/                 # Main app
│   ├── models.py          # Service and StatusUpdate models
│   ├── views.py           # Status page views
│   ├── admin.py           # Admin interface
│   ├── urls.py            # URL routing
│   └── templates/         # HTML templates
├── static/
│   └── css/
│       ├── input.css      # Tailwind input
│       └── output.css     # Generated CSS (created by Tailwind)
├── rialtas_status/        # Project settings
└── manage.py              # Django management
```

## Status Color Scheme

- **Green**: Stable - All systems operational
- **Blue**: Maintenance - Scheduled maintenance
- **Yellow**: Degraded - Performance issues
- **Orange**: Partial Outage - Some features down
- **Red**: Major Outage - Critical systems down

## API Usage

The Rialtas Status API allows external applications to programmatically create and retrieve status updates.

### Getting Started with the API

#### 1. Create an API Key

1. Log in to the admin panel at http://localhost:8000/admin/
2. Navigate to "API Keys" → "Add API Key"
3. Enter a descriptive name (e.g., "Mobile App", "Monitoring Service")
4. Click "Save" and copy the generated API key immediately

**Important:** Keep your API keys secure! Store them in environment variables or secure credential storage.

#### 2. Test the API

Health check (no authentication required):
```bash
curl http://localhost:8000/api/health
```

List all services:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     http://localhost:8000/api/services
```

#### 3. Create a Status Update

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": 1,
    "status": "stable",
    "comments": "All systems operational"
  }' \
  http://localhost:8000/api/status-updates
```

### Available Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/health` | Health check | No |
| POST | `/api/status-updates` | Create status update | Yes |
| GET | `/api/status-updates` | List all status updates | Yes |
| GET | `/api/status-updates/{id}` | Get specific status update | Yes |
| GET | `/api/services` | List all services | Yes |
| GET | `/api/services/{id}` | Get specific service | Yes |
| GET | `/api/services/{id}/history` | Get service status history | Yes |

### Status Values

- `stable` - All systems operational
- `degraded` - Reduced performance
- `partial` - Some features unavailable
- `down` - Complete outage
- `maintenance` - Scheduled maintenance

### Python Example

```python
import requests

API_KEY = "your_api_key_here"
API_URL = "http://localhost:8000/api"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Create a status update
data = {
    "service_id": 1,
    "status": "degraded",
    "comments": "Experiencing slow response times",
    "plan": "Investigating database performance"
}

response = requests.post(
    f"{API_URL}/status-updates",
    json=data,
    headers=headers
)

print(response.json())
```

### Interactive API Documentation

Visit http://localhost:8000/api/docs for interactive Swagger documentation where you can test all endpoints directly from your browser.

## Testing

The project includes comprehensive test coverage for the API functionality.

### Running Tests

Run all tests:
```bash
python manage.py test
```

Run only API tests:
```bash
python manage.py test status.test_api
```

Run tests with verbose output:
```bash
python manage.py test status.test_api -v 2
```

### Test Coverage

The test suite includes:
- **API Key Model Tests** (3 tests) - API key creation, validation, and uniqueness
- **API Authentication Tests** (6 tests) - Authentication, authorization, and key lifecycle
- **Status Update API Tests** (8 tests) - Creating, listing, and retrieving status updates
- **Service API Tests** (7 tests) - Service endpoints and status history
- **API Integration Tests** (2 tests) - Complete workflows and status progression

Total: **26 comprehensive tests** covering all API functionality.

## Tips

- The overall status banner shows the worst status across all services
- Only active services appear on the public status page
- The admin interface automatically tracks who created each update
- Use the "Order" field to control how services appear on the page
- Comments and Plan sections support line breaks for better formatting
- API updates are not associated with a user account (created_by will be null)
- API keys track their last usage time automatically