import re
from schemas.blood_schema import VALID_BLOOD_GROUPS, VALID_COMPONENTS

def validate_blood_group(bg):
    return bg in VALID_BLOOD_GROUPS

def validate_component(comp):
    return comp in VALID_COMPONENTS

def validate_priority(priority):
    return priority in ['NORMAL', 'URGENT', 'EMERGENCY']

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None

def sanitize_string(s):
    if not s:
        return s
    return str(s).strip()
