import re
from flask import Blueprint, request
from extensions import db
from models.user import User
from models.donor import DonorProfile
from models.hospital import Hospital
from utils.helpers import success_response, error_response
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity
)

bp = Blueprint('auth', __name__)

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return error_response("INVALID_REQUEST", "No data provided", 400)

    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    full_name = data.get('full_name') or data.get('name')

    if not all([email, password, role, full_name]):
        return error_response("MISSING_FIELDS", "Missing required fields (full_name, email, password, role)", 400)

    # Validate email
    if not re.match(EMAIL_REGEX, email):
        return error_response("INVALID_EMAIL", "Invalid email format", 400)

    # Validate password length
    if len(password) < 8:
        return error_response("INVALID_PASSWORD", "Password must be at least 8 characters long", 400)

    role_upper = role.upper()
    if role_upper not in ['PATIENT', 'DONOR', 'HOSPITAL', 'ADMIN']:
        return error_response("INVALID_ROLE", "Invalid role specified", 400)

    if User.query.filter_by(email=email).first():
        return error_response("EMAIL_EXISTS", "Email is already registered", 400)

    user = User(
        email=email,
        full_name=full_name,
        role=role_upper,
        phone=data.get('phone')
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    if role_upper == 'DONOR':
        donor_data = data.get('donor_data') or {}
        bg = donor_data.get('blood_group') or data.get('blood_group') or 'O+'
        city = donor_data.get('city') or data.get('city') or 'Unknown'
        area = donor_data.get('area') or data.get('area')
        
        donor_profile = DonorProfile(
            user_id=user.id,
            blood_group=bg,
            city=city,
            area=area
        )
        db.session.add(donor_profile)
    
    elif role_upper == 'HOSPITAL':
        hospital_data = data.get('hospital_data') or {}
        hosp_name = hospital_data.get('name') or data.get('hospital_name') or full_name
        city = hospital_data.get('city') or data.get('city') or 'Unknown'
        hosp_type = hospital_data.get('type') or data.get('type') or data.get('hospital_type') or 'HOSPITAL'
        address = hospital_data.get('address') or data.get('address')
        state = hospital_data.get('state') or data.get('state')
            
        hospital = Hospital(
            name=hosp_name,
            city=city,
            state=state,
            address=address,
            user_id=user.id,
            type=hosp_type,
            phone=data.get('phone'),
            email=email
        )
        db.session.add(hospital)

    db.session.commit()

    return success_response({
        "message": "Registration successful",
        "user": user.to_dict()
    }, 201)

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return error_response("INVALID_REQUEST", "Email and password are required", 400)

    user = User.query.filter_by(email=data['email']).first()
    if not user or not user.check_password(data['password']):
        return error_response("INVALID_CREDENTIALS", "Invalid email or password", 401)

    if not user.is_active:
        return error_response("INACTIVE_ACCOUNT", "Account is deactivated", 403)

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return success_response({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token": access_token,
        "user": user.to_dict()
    }, 200)

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=str(current_user_id))
    return success_response({
        "access_token": new_access_token,
        "token": new_access_token
    }, 200)

@bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return error_response("USER_NOT_FOUND", "User not found", 404)
        
    return success_response(user.to_dict(), 200)

@bp.route('/logout', methods=['POST'])
def logout():
    return success_response({"message": "Successfully logged out"}, 200)
