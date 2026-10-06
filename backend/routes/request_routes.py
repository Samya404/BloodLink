from flask import Blueprint, request
from extensions import db, socketio
from models.user import User
from models.request import BloodRequest
from models.match import DonorMatch
from models.notification import Notification
from services.matching_service import MatchingService
from utils.helpers import success_response, error_response
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('requests', __name__)

VALID_BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

@bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
def create_request():
    data = request.get_json()
    if not data:
        return error_response("INVALID_REQUEST", "No data provided", 400)

    blood_group = data.get('blood_group')
    if not blood_group or blood_group.upper() not in VALID_BLOOD_GROUPS:
        return error_response("INVALID_BLOOD_GROUP", f"Invalid blood group: {blood_group}", 400)

    units = data.get('units') if 'units' in data else data.get('units_required')
    if units is None:
        return error_response("INVALID_UNITS", "Units required", 400)
    
    try:
        units = int(units)
    except (ValueError, TypeError):
        return error_response("INVALID_UNITS", "Units must be an integer", 400)

    if units <= 0:
        return error_response("INVALID_UNITS", "Units must be greater than 0", 400)

    current_user_id = int(get_jwt_identity())
    
    priority = (data.get('urgency_level') or data.get('priority') or 'NORMAL').upper()
    if priority not in ['NORMAL', 'URGENT', 'CRITICAL', 'EMERGENCY', 'HIGH', 'ROUTINE']:
        priority = 'NORMAL'

    req = BloodRequest(
        requester_id=current_user_id,
        blood_group=blood_group.upper(),
        units_required=units,
        patient_name=data.get('patient_name'),
        hospital_name=data.get('hospital_name'),
        hospital_id=data.get('hospital_id'),
        city=data.get('city'),
        component=data.get('component') or 'Whole Blood',
        priority=priority,
        status='PENDING',
        notes=data.get('notes')
    )
    db.session.add(req)
    db.session.commit()

    # Trigger matching service
    try:
        MatchingService.find_matching_donors(req.id)
    except Exception as e:
        print(f"Matching error: {e}")

    # Emit socketio event
    socketio.emit('new_blood_request', {
        'id': req.id,
        'request_id': req.id,
        'blood_group': req.blood_group,
        'city': req.city,
        'priority': req.priority,
        'units': req.units_required
    })

    return success_response(req.to_dict(), 201)

@bp.route('/', methods=['GET'], strict_slashes=False)
def list_requests():
    query = BloodRequest.query.order_by(BloodRequest.created_at.desc())
    
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status.upper())
        
    blood_group = request.args.get('blood_group')
    if blood_group:
        query = query.filter_by(blood_group=blood_group.upper())

    city = request.args.get('city')
    if city:
        query = query.filter(BloodRequest.city.ilike(f"%{city}%"))

    requests_list = [r.to_dict() for r in query.all()]
    return success_response(requests_list, 200)

@bp.route('/my', methods=['GET'])
@jwt_required()
def get_my_requests():
    current_user_id = int(get_jwt_identity())
    requests = BloodRequest.query.filter_by(requester_id=current_user_id).order_by(BloodRequest.created_at.desc()).all()
    return success_response([r.to_dict() for r in requests], 200)

@bp.route('/<int:id>', methods=['GET'])
def get_request(id):
    req = BloodRequest.query.get(id)
    if not req:
        return error_response("NOT_FOUND", "Request not found", 404)
    return success_response(req.to_dict(), 200)

@bp.route('/<int:id>/matches', methods=['GET'])
@jwt_required()
def get_request_matches(id):
    req = BloodRequest.query.get(id)
    if not req:
        return error_response("NOT_FOUND", "Request not found", 404)
        
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if req.requester_id != current_user_id and user.role not in ['HOSPITAL', 'ADMIN']:
        return error_response("UNAUTHORIZED", "Access denied", 403)

    matches = DonorMatch.query.filter_by(request_id=id).order_by(DonorMatch.match_score.desc()).all()
    if not matches:
        # Generate matches if none exist yet
        matches = MatchingService.find_matching_donors(id)
        
    return success_response([m.to_dict(req) for m in matches], 200)

@bp.route('/<int:id>', methods=['PATCH', 'PUT'])
@bp.route('/<int:id>/status', methods=['PATCH', 'PUT', 'POST'])
@jwt_required()
def update_request(id):
    req = BloodRequest.query.get(id)
    if not req:
        return error_response("NOT_FOUND", "Request not found", 404)

    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    # Only creator, hospital or admin can update
    if req.requester_id != current_user_id and user.role not in ['HOSPITAL', 'ADMIN']:
        return error_response("UNAUTHORIZED", "You cannot modify this request", 403)

    data = request.get_json() or {}
    status = data.get('status')
    if status:
        req.status = status.upper()

    if 'units' in data or 'units_required' in data:
        units = data.get('units') or data.get('units_required')
        if int(units) > 0:
            req.units_required = int(units)

    if 'notes' in data:
        req.notes = data.get('notes')

    db.session.commit()

    # Emit socket event
    socketio.emit('request_status_changed', {
        'id': req.id,
        'request_id': req.id,
        'status': req.status
    })

    # Notification for requester if updated by hospital/admin
    if req.requester_id != current_user_id:
        notif = Notification(
            user_id=req.requester_id,
            type='REQUEST_STATUS_CHANGED',
            title='Request Status Updated',
            message=f"Your blood request #{req.id} status changed to {req.status}."
        )
        db.session.add(notif)
        db.session.commit()

    return success_response(req.to_dict(), 200)

@bp.route('/<int:id>/cancel', methods=['POST'])
@jwt_required()
def cancel_request(id):
    req = BloodRequest.query.get(id)
    if not req:
        return error_response("NOT_FOUND", "Request not found", 404)

    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    if req.requester_id != current_user_id and user.role not in ['ADMIN', 'HOSPITAL']:
        return error_response("UNAUTHORIZED", "You cannot cancel this request", 403)

    req.status = 'CANCELLED'
    db.session.commit()

    socketio.emit('request_status_changed', {
        'id': req.id,
        'request_id': req.id,
        'status': 'CANCELLED'
    })

    return success_response(req.to_dict(), 200)
