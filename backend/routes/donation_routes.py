from datetime import datetime, timezone
from flask import Blueprint, request
from extensions import db
from models.donation import Donation
from models.donor import DonorProfile
from utils.helpers import success_response, error_response
from utils.decorators import roles_required
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('donations', __name__)

@bp.route('/', methods=['POST'], strict_slashes=False)
@jwt_required()
@roles_required('DONOR', 'HOSPITAL', 'ADMIN')
def record_donation():
    data = request.get_json() or {}
    current_user_id = int(get_jwt_identity())
    
    donor = DonorProfile.query.filter_by(user_id=current_user_id).first()
    donor_id = donor.id if donor else data.get('donor_id')
    
    if not donor_id:
        return error_response("INVALID_REQUEST", "Donor ID is required", 400)

    bg = data.get('blood_group') or (donor.blood_group if donor else 'O+')
    comp = data.get('component', 'Whole Blood')
    loc = data.get('collection_location', 'Blood Donation Center')

    donation = Donation(
        donor_id=donor_id,
        blood_group=bg,
        component=comp,
        collection_location=loc,
        status='COMPLETED',
        donation_date=datetime.now(timezone.utc)
    )
    db.session.add(donation)
    
    if donor:
        donor.last_donation_date = datetime.now(timezone.utc)
        
    db.session.commit()
    return success_response(donation.to_dict(), 201)

@bp.route('/', methods=['GET'], strict_slashes=False)
@jwt_required()
def list_donations():
    current_user_id = int(get_jwt_identity())
    donor = DonorProfile.query.filter_by(user_id=current_user_id).first()
    
    if donor:
        donations = Donation.query.filter_by(donor_id=donor.id).order_by(Donation.donation_date.desc()).all()
    else:
        donations = Donation.query.order_by(Donation.donation_date.desc()).all()
        
    return success_response([d.to_dict() for d in donations], 200)
