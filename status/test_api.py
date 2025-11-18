"""
Comprehensive tests for the Rialtas Status API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from status.models import Service, StatusUpdate, APIKey

User = get_user_model()


class APIKeyModelTests(TestCase):
    """Test the APIKey model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_create_api_key(self):
        """Test creating an API key"""
        api_key = APIKey.objects.create(
            name="Test App",
            created_by=self.user
        )
        self.assertIsNotNone(api_key.key)
        self.assertEqual(len(api_key.key), 64)
        self.assertTrue(api_key.is_active)
        self.assertEqual(api_key.name, "Test App")

    def test_api_key_string_representation(self):
        """Test the API key string representation"""
        api_key = APIKey.objects.create(
            name="Test App",
            is_active=True
        )
        self.assertEqual(str(api_key), "Test App (Active)")

        api_key.is_active = False
        api_key.save()
        self.assertEqual(str(api_key), "Test App (Inactive)")

    def test_api_key_unique(self):
        """Test that API keys are unique"""
        key1 = APIKey.objects.create(name="App 1")
        key2 = APIKey.objects.create(name="App 2")
        self.assertNotEqual(key1.key, key2.key)


class APIAuthenticationTests(TestCase):
    """Test API authentication"""

    def setUp(self):
        self.api_key = APIKey.objects.create(
            name="Test App",
            is_active=True
        )
        self.service = Service.objects.create(
            name="Test Service",
            description="A test service"
        )

    def test_health_check_no_auth_required(self):
        """Test that health check endpoint doesn't require authentication"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "API is running"})

    def test_api_requires_authentication(self):
        """Test that API endpoints require authentication"""
        response = self.client.get('/api/services')
        self.assertEqual(response.status_code, 401)

    def test_api_with_valid_key(self):
        """Test API access with valid API key"""
        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.api_key.key}'}
        response = self.client.get('/api/services', **headers)
        self.assertEqual(response.status_code, 200)

    def test_api_with_invalid_key(self):
        """Test API access with invalid API key"""
        headers = {'HTTP_AUTHORIZATION': 'Bearer invalid_key_12345'}
        response = self.client.get('/api/services', **headers)
        self.assertEqual(response.status_code, 401)

    def test_api_with_inactive_key(self):
        """Test API access with inactive API key"""
        self.api_key.is_active = False
        self.api_key.save()

        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.api_key.key}'}
        response = self.client.get('/api/services', **headers)
        self.assertEqual(response.status_code, 401)

    def test_api_key_last_used_updated(self):
        """Test that last_used_at is updated when API key is used"""
        self.assertIsNone(self.api_key.last_used_at)

        headers = {'HTTP_AUTHORIZATION': f'Bearer {self.api_key.key}'}
        self.client.get('/api/services', **headers)

        self.api_key.refresh_from_db()
        self.assertIsNotNone(self.api_key.last_used_at)


class StatusUpdateAPITests(TestCase):
    """Test status update API endpoints"""

    def setUp(self):
        self.api_key = APIKey.objects.create(name="Test App")
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.api_key.key}'}
        self.service = Service.objects.create(
            name="Test Service",
            description="A test service"
        )

    def test_create_status_update(self):
        """Test creating a status update via API"""
        data = {
            "service_id": self.service.id,
            "status": "stable",
            "comments": "All systems operational",
            "plan": ""
        }

        response = self.client.post(
            '/api/status-updates',
            data=data,
            content_type='application/json',
            **self.headers
        )

        self.assertEqual(response.status_code, 201)
        json_data = response.json()
        self.assertEqual(json_data['service_id'], self.service.id)
        self.assertEqual(json_data['status'], 'stable')
        self.assertEqual(json_data['comments'], 'All systems operational')
        self.assertIsNone(json_data['created_by_username'])

        # Verify in database
        status_update = StatusUpdate.objects.get(id=json_data['id'])
        self.assertEqual(status_update.status, 'stable')
        self.assertEqual(status_update.comments, 'All systems operational')

    def test_create_status_update_with_all_fields(self):
        """Test creating a status update with all fields"""
        data = {
            "service_id": self.service.id,
            "status": "degraded",
            "comments": "Slow response times",
            "plan": "Investigating database performance"
        }

        response = self.client.post(
            '/api/status-updates',
            data=data,
            content_type='application/json',
            **self.headers
        )

        self.assertEqual(response.status_code, 201)
        json_data = response.json()
        self.assertEqual(json_data['status'], 'degraded')
        self.assertEqual(json_data['comments'], 'Slow response times')
        self.assertEqual(json_data['plan'], 'Investigating database performance')

    def test_create_status_update_invalid_status(self):
        """Test creating a status update with invalid status"""
        data = {
            "service_id": self.service.id,
            "status": "invalid_status",
            "comments": "Test"
        }

        response = self.client.post(
            '/api/status-updates',
            data=data,
            content_type='application/json',
            **self.headers
        )

        self.assertEqual(response.status_code, 400)

    def test_create_status_update_invalid_service(self):
        """Test creating a status update for non-existent service"""
        data = {
            "service_id": 99999,
            "status": "stable",
            "comments": "Test"
        }

        response = self.client.post(
            '/api/status-updates',
            data=data,
            content_type='application/json',
            **self.headers
        )

        self.assertEqual(response.status_code, 404)

    def test_list_status_updates(self):
        """Test listing status updates"""
        # Create some status updates
        StatusUpdate.objects.create(
            service=self.service,
            status='stable',
            comments='First update'
        )
        StatusUpdate.objects.create(
            service=self.service,
            status='degraded',
            comments='Second update'
        )

        response = self.client.get('/api/status-updates', **self.headers)

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 2)
        # Most recent first
        self.assertEqual(json_data[0]['comments'], 'Second update')
        self.assertEqual(json_data[1]['comments'], 'First update')

    def test_list_status_updates_with_limit(self):
        """Test listing status updates with limit parameter"""
        # Create 10 status updates
        for i in range(10):
            StatusUpdate.objects.create(
                service=self.service,
                status='stable',
                comments=f'Update {i}'
            )

        response = self.client.get('/api/status-updates?limit=5', **self.headers)

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 5)

    def test_get_specific_status_update(self):
        """Test getting a specific status update"""
        update = StatusUpdate.objects.create(
            service=self.service,
            status='stable',
            comments='Test update'
        )

        response = self.client.get(f'/api/status-updates/{update.id}', **self.headers)

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['id'], update.id)
        self.assertEqual(json_data['comments'], 'Test update')

    def test_get_nonexistent_status_update(self):
        """Test getting a non-existent status update"""
        response = self.client.get('/api/status-updates/99999', **self.headers)
        self.assertEqual(response.status_code, 404)


class ServiceAPITests(TestCase):
    """Test service API endpoints"""

    def setUp(self):
        self.api_key = APIKey.objects.create(name="Test App")
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.api_key.key}'}
        self.service1 = Service.objects.create(
            name="Service 1",
            description="First service",
            order=1,
            is_active=True
        )
        self.service2 = Service.objects.create(
            name="Service 2",
            description="Second service",
            order=2,
            is_active=False
        )

    def test_list_services_active_only(self):
        """Test listing only active services"""
        response = self.client.get('/api/services', **self.headers)

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 1)
        self.assertEqual(json_data[0]['name'], 'Service 1')

    def test_list_services_all(self):
        """Test listing all services including inactive"""
        response = self.client.get('/api/services?active_only=false', **self.headers)

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

    def test_get_service_with_current_status(self):
        """Test getting a service with its current status"""
        # Create a status update
        StatusUpdate.objects.create(
            service=self.service1,
            status='degraded',
            comments='Performance issues'
        )

        response = self.client.get(f'/api/services/{self.service1.id}', **self.headers)

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['id'], self.service1.id)
        self.assertEqual(json_data['name'], 'Service 1')
        self.assertIsNotNone(json_data['current_status'])
        self.assertEqual(json_data['current_status']['status'], 'degraded')

    def test_get_service_without_status(self):
        """Test getting a service that has no status updates"""
        response = self.client.get(f'/api/services/{self.service1.id}', **self.headers)

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertIsNone(json_data['current_status'])

    def test_get_service_history(self):
        """Test getting service status history"""
        # Create multiple status updates
        for i in range(5):
            StatusUpdate.objects.create(
                service=self.service1,
                status='stable',
                comments=f'Update {i}'
            )

        response = self.client.get(
            f'/api/services/{self.service1.id}/history',
            **self.headers
        )

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 5)
        # Most recent first
        self.assertEqual(json_data[0]['comments'], 'Update 4')

    def test_get_service_history_with_limit(self):
        """Test getting service status history with limit"""
        # Create 10 status updates
        for i in range(10):
            StatusUpdate.objects.create(
                service=self.service1,
                status='stable',
                comments=f'Update {i}'
            )

        response = self.client.get(
            f'/api/services/{self.service1.id}/history?limit=3',
            **self.headers
        )

        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(len(json_data), 3)

    def test_get_nonexistent_service(self):
        """Test getting a non-existent service"""
        response = self.client.get('/api/services/99999', **self.headers)
        self.assertEqual(response.status_code, 404)


class APIIntegrationTests(TestCase):
    """Integration tests for complete API workflows"""

    def setUp(self):
        self.api_key = APIKey.objects.create(name="Integration Test App")
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.api_key.key}'}
        self.service = Service.objects.create(
            name="Production API",
            description="Main production API"
        )

    def test_complete_status_update_workflow(self):
        """Test complete workflow: create update, verify it appears in lists"""
        # Create a status update
        create_data = {
            "service_id": self.service.id,
            "status": "down",
            "comments": "Database connection lost",
            "plan": "Restarting database server"
        }

        create_response = self.client.post(
            '/api/status-updates',
            data=create_data,
            content_type='application/json',
            **self.headers
        )

        self.assertEqual(create_response.status_code, 201)
        update_id = create_response.json()['id']

        # Verify it appears in the list
        list_response = self.client.get('/api/status-updates', **self.headers)
        self.assertEqual(list_response.status_code, 200)
        updates = list_response.json()
        self.assertTrue(any(u['id'] == update_id for u in updates))

        # Verify it appears in service current status
        service_response = self.client.get(
            f'/api/services/{self.service.id}',
            **self.headers
        )
        self.assertEqual(service_response.status_code, 200)
        service_data = service_response.json()
        self.assertEqual(service_data['current_status']['id'], update_id)
        self.assertEqual(service_data['current_status']['status'], 'down')

        # Verify it appears in service history
        history_response = self.client.get(
            f'/api/services/{self.service.id}/history',
            **self.headers
        )
        self.assertEqual(history_response.status_code, 200)
        history = history_response.json()
        self.assertEqual(history[0]['id'], update_id)

    def test_status_progression(self):
        """Test updating service status through different states"""
        statuses = ['down', 'degraded', 'stable']

        for status in statuses:
            data = {
                "service_id": self.service.id,
                "status": status,
                "comments": f"Service is now {status}"
            }

            response = self.client.post(
                '/api/status-updates',
                data=data,
                content_type='application/json',
                **self.headers
            )

            self.assertEqual(response.status_code, 201)

        # Verify service shows most recent status
        service_response = self.client.get(
            f'/api/services/{self.service.id}',
            **self.headers
        )
        self.assertEqual(
            service_response.json()['current_status']['status'],
            'stable'
        )

        # Verify all statuses in history
        history_response = self.client.get(
            f'/api/services/{self.service.id}/history',
            **self.headers
        )
        history = history_response.json()
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['status'], 'stable')
        self.assertEqual(history[1]['status'], 'degraded')
        self.assertEqual(history[2]['status'], 'down')
