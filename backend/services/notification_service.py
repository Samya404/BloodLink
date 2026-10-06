from extensions import db, socketio
from models.notification import Notification
from models.request import BloodRequest
from models.donor import DonorMatch

class NotificationService:
    @staticmethod
    def create_notification(user_id, type, title, message):
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        
        socketio.emit('notification_created', {
            'id': notification.id,
            'user_id': user_id,
            'title': title,
            'message': message,
            'type': type
        }, room=str(user_id))
        
        return notification

    @staticmethod
    def get_notifications(user_id, unread_only=False):
        query = Notification.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(Notification.created_at.desc()).all()

    @staticmethod
    def mark_as_read(notification_id, user_id):
        notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def notify_matching_donors(request_id):
        matches = DonorMatch.query.filter_by(request_id=request_id).all()
        request = BloodRequest.query.get(request_id)
        
        if not request:
            return

        for match in matches:
            NotificationService.create_notification(
                user_id=match.donor.user_id,
                type='DONATION_REQUEST',
                title='Urgent Blood Request in your area',
                message=f"A patient needs {request.blood_group} blood. You are a compatible match!"
            )

    @staticmethod
    def notify_request_update(request_id, old_status, new_status):
        request = BloodRequest.query.get(request_id)
        if request and request.requester_id:
            NotificationService.create_notification(
                user_id=request.requester_id,
                type='REQUEST_UPDATE',
                title=f"Blood Request {new_status}",
                message=f"Your blood request status has changed from {old_status} to {new_status}."
            )

    @staticmethod
    def notify_low_stock(hospital_id, blood_group, units):
        # Simplified: notify hospital admins. Assuming a way to get admin user_ids for the hospital
        # In a real system, you'd query hospital users. We emit a general hospital room event.
        socketio.emit('low_stock_alert', {
            'hospital_id': hospital_id,
            'blood_group': blood_group,
            'units': units,
            'message': f"Low stock alert: Only {units} units of {blood_group} left."
        }, room=f"hospital_{hospital_id}")
