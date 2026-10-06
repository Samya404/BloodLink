from flask import Blueprint, request
from extensions import db
from models.hospital import Hospital
from models.inventory import BloodInventory
from utils.helpers import success_response, error_response

bp = Blueprint('hospitals', __name__)

@bp.route('/', methods=['GET'], strict_slashes=False)
def list_hospitals():
    query = Hospital.query
    
    city = request.args.get('city')
    if city:
        query = query.filter(Hospital.city.ilike(f"%{city}%"))

    state = request.args.get('state')
    if state:
        query = query.filter(Hospital.state.ilike(f"%{state}%"))

    verification = request.args.get('verification_status')
    if verification:
        query = query.filter_by(verification_status=verification.upper())

    hospitals = query.all()
    return success_response([h.to_dict() for h in hospitals], 200)

@bp.route('/<int:id>', methods=['GET'])
def get_hospital(id):
    hosp = Hospital.query.get(id)
    if not hosp:
        return error_response("NOT_FOUND", "Hospital not found", 404)
    return success_response(hosp.to_dict(), 200)

@bp.route('/<int:id>/inventory', methods=['GET'])
def get_hospital_inventory(id):
    hosp = Hospital.query.get(id)
    if not hosp:
        return error_response("NOT_FOUND", "Hospital not found", 404)
        
    items = BloodInventory.query.filter_by(hospital_id=id).all()
    return success_response([item.to_dict() for item in items], 200)
