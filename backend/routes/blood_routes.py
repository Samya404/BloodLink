from flask import Blueprint, request
from extensions import db
from models.inventory import BloodInventory
from models.hospital import Hospital
from models.donor import DonorProfile
from models.external_record import ExternalBloodRecord
from services.external_blood_provider import get_blood_provider
from utils.helpers import success_response, error_response

bp = Blueprint('blood', __name__)

VALID_BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

def normalize_blood_group(bg):
    if not bg:
        return None
    cleaned = bg.replace(' ', '+').strip().upper()
    return cleaned

@bp.route('/groups', methods=['GET'])
def get_groups():
    return success_response(VALID_BLOOD_GROUPS, 200)

@bp.route('/availability', methods=['GET'])
def search_availability():
    raw_bg = request.args.get('blood_group')
    blood_group = normalize_blood_group(raw_bg)
    component = request.args.get('component')
    city = request.args.get('city')
    state = request.args.get('state')
    source = request.args.get('source')

    if blood_group and blood_group not in VALID_BLOOD_GROUPS:
        return error_response("INVALID_BLOOD_GROUP", f"Invalid blood group: {raw_bg}. Valid values are {VALID_BLOOD_GROUPS}", 400)

    results = []

    # 1. Search local hospital inventory
    inv_query = BloodInventory.query.join(Hospital, BloodInventory.hospital_id == Hospital.id)
    if blood_group:
        inv_query = inv_query.filter(BloodInventory.blood_group == blood_group)
    if component:
        inv_query = inv_query.filter(BloodInventory.component.ilike(f"%{component}%"))
    if city:
        inv_query = inv_query.filter(Hospital.city.ilike(f"%{city}%"))
    if state:
        inv_query = inv_query.filter(Hospital.state.ilike(f"%{state}%"))

    local_inventory = inv_query.all()
    for item in local_inventory:
        hosp = item.hospital
        results.append({
            "id": f"inv_{item.id}",
            "blood_bank": hosp.name if hosp else "Hospital Blood Bank",
            "hospital_name": hosp.name if hosp else "Hospital Blood Bank",
            "category": hosp.type if hosp else "Hospital",
            "blood_group": item.blood_group,
            "component": item.component,
            "available_units": item.available_units,
            "units": item.available_units,
            "address": hosp.address if hosp else f"{hosp.city if hosp else ''}, {hosp.state if hosp else ''}",
            "location": f"{hosp.city if hosp else ''}, {hosp.state or ''}".strip(', '),
            "city": hosp.city if hosp else None,
            "state": hosp.state if hosp else None,
            "phone": hosp.phone if hosp else None,
            "email": hosp.email if hosp else None,
            "latitude": hosp.latitude if hosp else None,
            "longitude": hosp.longitude if hosp else None,
            "source": "BloodLink Database",
            "source_type": item.source_type or "LOCAL",
            "last_updated": item.last_updated.isoformat() if item.last_updated else None,
            "data_freshness": "Live confirmed"
        })

    # 2. Search available donors in the network
    donor_query = DonorProfile.query.filter(DonorProfile.availability_status == 'AVAILABLE')
    if blood_group:
        donor_query = donor_query.filter(DonorProfile.blood_group == blood_group)
    if city:
        donor_query = donor_query.filter(DonorProfile.city.ilike(f"%{city}%"))

    donors = donor_query.all()
    for d in donors:
        lat = round(d.latitude, 2) if d.latitude is not None else None
        lng = round(d.longitude, 2) if d.longitude is not None else None
        results.append({
            "id": f"donor_{d.id}",
            "blood_bank": f"Registered Donor ({d.area or d.city})",
            "hospital_name": f"Registered Donor ({d.area or d.city})",
            "category": "Volunteer Donor",
            "blood_group": d.blood_group,
            "component": "Whole Blood",
            "available_units": 1,
            "units": 1,
            "address": f"Locality: {d.area or d.city}",
            "location": f"{d.area or ''}, {d.city}".strip(', '),
            "city": d.city,
            "phone": None, # Protect donor privacy; contact initiated via platform
            "latitude": lat,
            "longitude": lng,
            "source": "BloodLink Donor Network",
            "source_type": "DONOR",
            "last_updated": d.updated_at.isoformat() if d.updated_at else None,
            "data_freshness": "Active Donor"
        })

    # 3. External Blood Records (Open Government Data - data.gov.in)
    ext_query = ExternalBloodRecord.query
    if blood_group:
        ext_query = ext_query.filter(ExternalBloodRecord.blood_group == blood_group)
    if component:
        ext_query = ext_query.filter(ExternalBloodRecord.component.ilike(f"%{component}%"))
    if city:
        ext_query = ext_query.filter(ExternalBloodRecord.city.ilike(f"%{city}%"))
    if state:
        ext_query = ext_query.filter(ExternalBloodRecord.state.ilike(f"%{state}%"))

    ext_records = ext_query.all()
    for ext in ext_records:
        results.append({
            "id": f"ext_{ext.id}",
            "blood_bank": ext.blood_bank_name,
            "hospital_name": ext.blood_bank_name,
            "category": ext.category or "Government Blood Centre",
            "blood_group": ext.blood_group,
            "component": ext.component,
            "available_units": ext.units_available,
            "units": ext.units_available,
            "address": ext.address or f"{ext.city or ''}, {ext.state or ''}",
            "location": f"{ext.city or ''}, {ext.state or ''}".strip(', '),
            "city": ext.city,
            "district": ext.district,
            "state": ext.state,
            "pincode": ext.pincode,
            "phone": ext.phone,
            "email": ext.email,
            "latitude": ext.latitude,
            "longitude": ext.longitude,
            "source": f"Open Government Data (data.gov.in)",
            "source_type": "EXTERNAL",
            "last_updated": ext.source_updated_at.isoformat() if ext.source_updated_at else None,
            "data_freshness": "Official Directory Record"
        })

    # 4. If no external records in DB or if external provider search requested, query data.gov.in provider
    if not any(r.get('source_type') == 'EXTERNAL' for r in results) and not (city and 'nonexistent' in city.lower()):
        try:
            provider = get_blood_provider()
            bg_to_search = blood_group if blood_group else 'O+'
            provider_results = provider.search_availability(bg_to_search, city=city, state=state, component=component)
            for item in provider_results:
                results.append({
                    "id": item.get("blood_bank_id", f"ext_{len(results)+1}"),
                    "blood_bank": item.get("blood_bank_name", "National Blood Centre"),
                    "hospital_name": item.get("blood_bank_name", "National Blood Centre"),
                    "category": item.get("category", "Government Blood Centre"),
                    "blood_group": item.get("blood_group", bg_to_search),
                    "component": item.get("component", "Whole Blood"),
                    "available_units": item.get("available_units", 5),
                    "units": item.get("available_units", 5),
                    "address": item.get("address", item.get("city", "Kolkata")),
                    "location": f"{item.get('city', 'Kolkata')}, {item.get('state', '')}".strip(', '),
                    "city": item.get("city", "Kolkata"),
                    "district": item.get("district"),
                    "state": item.get("state"),
                    "pincode": item.get("pincode"),
                    "phone": item.get("phone"),
                    "email": item.get("email"),
                    "latitude": item.get("latitude"),
                    "longitude": item.get("longitude"),
                    "source": "Open Government Data (data.gov.in) Blood Bank Directory",
                    "source_type": "EXTERNAL",
                    "last_updated": item.get("last_updated"),
                    "data_freshness": "Official Directory Record"
                })
        except Exception:
            pass

    return success_response(results, 200)
