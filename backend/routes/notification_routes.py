from flask import Blueprint, request
from extensions import db
from models.notification import Notification
from utils.helpers import success_response, error_response
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('notifications', __name__)

@bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def get_notifications():
    current_user_id = int(get_jwt_identity())
    query = Notification.query.filter_by(user_id=current_user_id).order_by(Notification.created_at.desc())
    
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    if unread_only:
        query = query.filter_by(is_read=False)
        
    notifications = query.all()
    return success_response([n.to_dict() for n in notifications], 200)

@bp.route('/<int:id>/read', methods=['PATCH', 'PUT'])
@jwt_required()
def mark_read(id):
    current_user_id = int(get_jwt_identity())
    notif = Notification.query.get(id)
    
    if not notif:
        return error_response("NOT_FOUND", "Notification not found", 404)
        
    if notif.user_id != current_user_id:
        return error_response("UNAUTHORIZED", "Access denied", 403)
        
    notif.is_read = True
    db.session.commit()
    
    return success_response(notif.to_dict(), 200)

@bp.route('/read-all', methods=['POST'])
@jwt_required()
def mark_all_read():
    current_user_id = int(get_jwt_identity())
    Notification.query.filter_by(user_id=current_user_id, is_read=False).update({'is_read': True})
    db.session.commit()
    return success_response({"message": "All notifications marked as read"}, 200)
