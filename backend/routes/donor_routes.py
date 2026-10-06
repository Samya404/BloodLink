from flask import Blueprint, request
from extensions import db
from models.user import User
from models.donor import DonorProfile
from models.match import DonorMatch
from models.audit import AuditLog
from services.matching_service import MatchingService
from utils.helpers import success_response, error_response
from utils.decorators import roles_required
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('donors', __name__)

@bp.route('/', methods=['GET'], strict_slashes=False)
def list_donors():
    query = DonorProfile.query
    
    blood_group = request.args.get('blood_group')
    if blood_group:
        query = query.filter_by(blood_group=blood_group.upper())

    city = request.args.get('city')
    if city:
        query = query.filter(DonorProfile.city.ilike(f"%{city}%"))

    availability = request.args.get('availability_status')
    if availability:
        query = query.filter_by(availability_status=availability.upper())

    donors = query.all()
    return success_response([d.to_dict() for d in donors], 200)

@bp.route('/<int:id>', methods=['GET'])
def get_donor(id):
    donor = DonorProfile.query.get(id)
    if not donor:
        return error_response("NOT_FOUND", "Donor not found", 404)
    return success_response(donor.to_dict(), 200)

@bp.route('/matches/<int:request_id>', methods=['GET'])
@jwt_required()
def get_matches(request_id):
    matches = MatchingService.find_matching_donors(request_id)
    return success_response([m.to_dict() for m in matches], 200)

@bp.route('/profile', methods=['PATCH', 'PUT', 'GET'])
@jwt_required()
@roles_required('DONOR')
def handle_profile():
    current_user_id = int(get_jwt_identity())
    donor = DonorProfile.query.filter_by(user_id=current_user_id).first()
    
    if not donor:
        return error_response("NOT_FOUND", "Donor profile not found", 404)

    if request.method == 'GET':
        return success_response(donor.to_dict(), 200)

    data = request.get_json() or {}
    
    if 'city' in data:
        donor.city = data['city']
    if 'area' in data:
        donor.area = data['area']
    if 'blood_group' in data:
        donor.blood_group = data['blood_group'].upper()
    if 'latitude' in data:
        donor.latitude = float(data['latitude']) if data['latitude'] is not None else None
    if 'longitude' in data:
        donor.longitude = float(data['longitude']) if data['longitude'] is not None else None
    if 'lat' in data:
        donor.latitude = float(data['lat']) if data['lat'] is not None else None
    if 'lng' in data:
        donor.longitude = float(data['lng']) if data['lng'] is not None else None
    if 'availability_status' in data:
        donor.availability_status = data['availability_status'].upper()
    if 'is_available' in data:
        donor.is_available = bool(data['is_available'])

    db.session.flush()

    audit = AuditLog(
        user_id=current_user_id,
        action="UPDATE_DONOR_PROFILE",
        entity_type="DonorProfile",
        entity_id=donor.id,
        description=f"Updated profile details for donor {donor.id}"
    )
    db.session.add(audit)
    db.session.commit()

    return success_response(donor.to_dict(), 200)

@bp.route('/availability', methods=['PATCH', 'PUT'])
@jwt_required()
@roles_required('DONOR')
def update_availability():
    current_user_id = int(get_jwt_identity())
    donor = DonorProfile.query.filter_by(user_id=current_user_id).first()
    
    if not donor:
        return error_response("NOT_FOUND", "Donor profile not found", 404)

    data = request.get_json() or {}
    
    if 'is_available' in data:
        donor.is_available = bool(data['is_available'])
    elif 'availability_status' in data:
        donor.availability_status = data['availability_status'].upper()

    db.session.flush()

    audit = AuditLog(
        user_id=current_user_id,
        action="UPDATE_AVAILABILITY",
        entity_type="DonorProfile",
        entity_id=donor.id,
        description=f"Donor availability changed to {donor.availability_status}"
    )
    db.session.add(audit)
    db.session.commit()

    return success_response(donor.to_dict(), 200)
