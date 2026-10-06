import os
from abc import ABC, abstractmethod

class ExternalBloodProvider(ABC):
    @abstractmethod
    def search_availability(self, blood_group, city=None, state=None, component=None):
        pass
    
    @abstractmethod
    def get_blood_banks(self, city=None, state=None):
        pass
    
    @abstractmethod
    def health_check(self):
        pass
    
    @abstractmethod
    def get_provider_name(self):
        pass

def get_blood_provider():
    provider_type = os.environ.get('BLOOD_PROVIDER', 'datagov')
    if provider_type == 'eraktkosh':
        from .eraktkosh_provider import ERaktKoshProvider
        return ERaktKoshProvider()
    elif provider_type == 'mock':
        from .mock_blood_provider import MockBloodProvider
        return MockBloodProvider()
    else:
        from .datagov_provider import DataGovInBloodProvider
        return DataGovInBloodProvider()
