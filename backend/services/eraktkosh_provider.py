import os
import requests
import logging
from .external_blood_provider import ExternalBloodProvider

logger = logging.getLogger(__name__)

class ERaktKoshProvider(ExternalBloodProvider):
    """
    Requires authorized API access. 
    Configure ERAKTKOSH_API_BASE_URL and ERAKTKOSH_API_KEY.
    """
    def __init__(self):
        self.base_url = os.environ.get('ERAKTKOSH_API_BASE_URL')
        self.api_key = os.environ.get('ERAKTKOSH_API_KEY')

    def _check_config(self):
        if not self.base_url or not self.api_key:
            raise ValueError("eRaktKosh API credentials not configured. Set ERAKTKOSH_API_BASE_URL and ERAKTKOSH_API_KEY.")

    def search_availability(self, blood_group, city=None, state=None, component=None):
        self._check_config()
        
        try:
            # Placeholder API endpoint
            url = f"{self.base_url}/api/v1/blood-availability"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            params = {
                "blood_group": blood_group,
                "city": city,
                "state": state,
                "component": component
            }
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Failed to fetch data from eRaktKosh: {e}")
            return []

    def get_blood_banks(self, city=None, state=None):
        self._check_config()
        try:
            url = f"{self.base_url}/api/v1/blood-banks"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            params = {"city": city, "state": state}
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get('data', [])
        except Exception as e:
            logger.error(f"Failed to fetch blood banks from eRaktKosh: {e}")
            return []

    def health_check(self):
        if not self.base_url or not self.api_key:
            return False
        # Could make a lightweight ping request here
        return True

    def get_provider_name(self):
        return "eRaktKosh (Official API)"
