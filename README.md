# Rialtas Status Page

A Django-based status page for monitoring the health of all Rialtas company services and infrastructure.

## Features

- **Public Status Dashboard**: View real-time status of all company services
- **Service Management**: Add and configure services (Database, Cloudflare, Thinfinity, Apps, etc.)
- **Status Updates**: Update service status with Problem and Plan sections
- **History Tracking**: View last 5 updates per service, with all history stored in database
- **Admin Interface**: Secure admin panel for managing services and updates
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
4. Fill in the **Problem** field to describe the issue
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

## Tips

- The overall status banner shows the worst status across all services
- Only active services appear on the public status page
- The admin interface automatically tracks who created each update
- Use the "Order" field to control how services appear on the page
- Problem and Plan sections support line breaks for better formatting