import random
from .external_blood_provider import ExternalBloodProvider

class MockBloodProvider(ExternalBloodProvider):
    """
    Mock blood provider with realistic demo data.
    """
    def __init__(self):
        self.cities = ['Kolkata', 'Delhi', 'Mumbai', 'Bengaluru']
        self.blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        self.components = ['WHOLE_BLOOD', 'PACKED_RED_CELLS', 'PLASMA', 'PLATELETS']
        
        self.demo_banks = []
        for city in self.cities:
            self.demo_banks.extend([
                {"id": f"bb_{city[:3].lower()}_1", "name": f"City Demo Blood Bank", "city": city, "state": "Demo State"},
                {"id": f"bb_{city[:3].lower()}_2", "name": f"Metro Demo Hospital", "city": city, "state": "Demo State"},
                {"id": f"bb_{city[:3].lower()}_3", "name": f"Care Demo Center", "city": city, "state": "Demo State"}
            ])

    def search_availability(self, blood_group, city=None, state=None, component=None):
        results = []
        target_cities = [city] if city else self.cities
        
        for c in target_cities:
            banks_in_city = [b for b in self.demo_banks if b['city'].lower() == c.lower()]
            for bank in banks_in_city:
                # Add random variations
                units = random.randint(0, 15)
                if units > 0:
                    results.append({
                        "blood_bank_id": bank["id"],
                        "blood_bank_name": bank["name"],
                        "city": bank["city"],
                        "blood_group": blood_group,
                        "component": component or "WHOLE_BLOOD",
                        "available_units": units,
                        "source_type": "DEMO",
                        "is_demo_data": True
                    })
        return results

    def get_blood_banks(self, city=None, state=None):
        if city:
            return [b for b in self.demo_banks if b['city'].lower() == city.lower()]
        return self.demo_banks

    def health_check(self):
        return True

    def get_provider_name(self):
        return "MockBloodProvider (Demo Data)"
