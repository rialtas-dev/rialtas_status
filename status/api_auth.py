"""
API authentication using API keys
"""
from django.utils import timezone
from ninja.security import HttpBearer
from .models import APIKey


class APIKeyAuth(HttpBearer):
    """
    API Key authentication for Django Ninja
    Expects Authorization header: Bearer <api_key>
    """

    def authenticate(self, request, token):
        """
        Validate the API key and update last_used_at timestamp
        Returns the APIKey object if valid, None otherwise
        """
        try:
            api_key = APIKey.objects.get(key=token, is_active=True)
            # Update last used timestamp
            api_key.last_used_at = timezone.now()
            api_key.save(update_fields=['last_used_at'])
            return api_key
        except APIKey.DoesNotExist:
            return None
