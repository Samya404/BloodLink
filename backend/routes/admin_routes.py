from flask import Blueprint, request
from extensions import db
from models.user import User
from models.donor import DonorProfile
from models.hospital import Hospital
from models.request import BloodRequest
from models.inventory import BloodInventory
from models.audit import AuditLog
from models.notification import Notification
from utils.helpers import success_response, error_response
from utils.decorators import roles_required
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('admin', __name__)

@bp.route('/statistics', methods=['GET'])
@jwt_required()
@roles_required('ADMIN')
def get_statistics():
    total_users = User.query.count()
    total_donors = DonorProfile.query.count()
    total_hospitals = Hospital.query.count()
    
    active_requests = BloodRequest.query.filter(BloodRequest.status.in_(['PENDING', 'MATCHING'])).count()
    emergency_requests = BloodRequest.query.filter(BloodRequest.priority.in_(['EMERGENCY', 'CRITICAL'])).count()
    fulfilled_requests = BloodRequest.query.filter_by(status='FULFILLED').count()
    
    inv_items = BloodInventory.query.all()
    total_units = sum(item.available_units for item in inv_items)
    
    # Blood group distribution
    bg_inventory = {}
    for item in inv_items:
        bg_inventory[item.blood_group] = bg_inventory.get(item.blood_group, 0) + item.available_units
        
    stats = {
        "total_users": total_users,
        "total_donors": total_donors,
        "total_hospitals": total_hospitals,
        "active_requests": active_requests,
        "emergency_requests": emergency_requests,
        "fulfilled_requests": fulfilled_requests,
        "total_inventory_units": total_units,
        "blood_inventory": bg_inventory
    }
    
    return success_response(stats, 200)

@bp.route('/users', methods=['GET'])
@jwt_required()
@roles_required('ADMIN')
def list_users():
    query = User.query.order_by(User.created_at.desc())
    
    role = request.args.get('role')
    if role:
        query = query.filter_by(role=role.upper())
        
    users = query.all()
    return success_response([u.to_dict() for u in users], 200)

@bp.route('/audit-logs', methods=['GET'])
@jwt_required()
@roles_required('ADMIN')
def list_audit_logs():
    query = AuditLog.query.order_by(AuditLog.created_at.desc())
    logs = query.limit(100).all()
    return success_response([l.to_dict() for l in logs], 200)

@bp.route('/hospitals/<int:id>/verify', methods=['PATCH', 'PUT'])
@jwt_required()
@roles_required('ADMIN')
def verify_hospital(id):
    hospital = Hospital.query.get(id)
    if not hospital:
        return error_response("NOT_FOUND", "Hospital not found", 404)
        
    data = request.get_json() or {}
    status = data.get('verification_status', 'VERIFIED').upper()
    hospital.verification_status = status
    
    current_user_id = int(get_jwt_identity())
    log = AuditLog(
        user_id=current_user_id,
        action="VERIFIED_HOSPITAL",
        entity_type="Hospital",
        entity_id=hospital.id,
        description=f"Hospital {hospital.name} verification status set to {status}"
    )
    db.session.add(log)
    
    if hospital.user_id:
        notif = Notification(
            user_id=hospital.user_id,
            type='SYSTEM_NOTIFICATION',
            title='Hospital Verification Status',
            message=f"Your hospital account verification status has been updated to: {status}"
        )
        db.session.add(notif)
        
    db.session.commit()
    return success_response(hospital.to_dict(), 200)
